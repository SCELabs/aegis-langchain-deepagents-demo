from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI


@dataclass
class LoopState:
    messages: list[dict[str, str]] = field(default_factory=list)
    model_calls: int = 0
    tool_calls: int = 0
    repeated_reads: int = 0
    completed: bool = False
    final_output: str = ""
    notes: list[str] = field(default_factory=list)


def _read_virtual_file(run_root: Path, rel_path: str) -> str:
    path = run_root / rel_path.lstrip("/")
    return path.read_text(encoding="utf-8")


def _detect_file_requests(text: str) -> list[str]:
    lowered = text.lower()
    requested: list[str] = []
    if "brief.md" in lowered:
        requested.append("/workspace/brief.md")
    if "items.json" in lowered:
        requested.append("/workspace/items.json")
    return requested


def _looks_final(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("{") or stripped.startswith("```json") or stripped.startswith("```")


def run_agent_loop(
    *,
    model: ChatOpenAI,
    system_prompt: str,
    user_task: str,
    run_root: Path,
    max_iterations: int = 6,
) -> LoopState:
    state = LoopState(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_task},
        ]
    )

    file_read_counts: dict[str, int] = {}

    for iteration in range(max_iterations):
        response = model.invoke(state.messages)
        state.model_calls += 1

        text = response.content if isinstance(response.content, str) else str(response.content)
        state.messages.append({"role": "assistant", "content": text})

        if _looks_final(text):
            state.completed = True
            state.final_output = text
            state.notes.append(f"completed_at_iteration_{iteration + 1}")
            break

        requested_files = _detect_file_requests(text)
        if not requested_files:
            state.notes.append(f"no_file_request_iteration_{iteration + 1}")
            state.messages.append(
                {
                    "role": "user",
                    "content": "You have enough information to continue. Read the required files if needed, then return the final JSON.",
                }
            )
            continue

        for rel_path in requested_files:
            file_read_counts[rel_path] = file_read_counts.get(rel_path, 0) + 1
            if file_read_counts[rel_path] > 1:
                state.repeated_reads += 1

            content = _read_virtual_file(run_root, rel_path)
            state.tool_calls += 1
            state.messages.append(
                {
                    "role": "user",
                    "content": f"FILE CONTENT {rel_path}:\n\n{content}",
                }
            )

    if not state.completed and not state.final_output:
        state.notes.append("max_iterations_reached")

    return state


def save_loop_artifacts(run_root: Path, state: LoopState) -> None:
    (run_root / "loop_messages.json").write_text(
        json.dumps(state.messages, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_root / "final_output.txt").write_text(state.final_output, encoding="utf-8")
    (run_root / "loop_state.json").write_text(
        json.dumps(
            {
                "model_calls": state.model_calls,
                "tool_calls": state.tool_calls,
                "repeated_reads": state.repeated_reads,
                "completed": state.completed,
                "notes": state.notes,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
