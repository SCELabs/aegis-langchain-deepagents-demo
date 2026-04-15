from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI

from demo.env import load_demo_env
from demo.metrics import RunMetrics
from demo.scoring import evaluate_output
from demo.task import SYSTEM_PROMPT, USER_TASK
from demo.workspace import build_workspace


def _ensure_local_deepagents_import() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    local_pkg = repo_root / "deepagents" / "libs" / "deepagents"
    if str(local_pkg) not in os.sys.path:
        os.sys.path.insert(0, str(local_pkg))


def _extract_text(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    for message in reversed(messages):
        msg_type = getattr(message, "type", None)
        if msg_type != "ai":
            continue
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(str(x) for x in content)
    return ""


def _count_signals(result: Any) -> tuple[int, int, int]:
    text = str(result)

    model_calls = text.count("AIMessage")
    tool_calls = text.count("ToolMessage")
    repeated_read_signals = 0

    repeated_read_signals += max(0, text.count("read_file") - 2)
    repeated_read_signals += max(0, text.count("items.json") - 2)
    repeated_read_signals += max(0, text.count("brief.md") - 2)

    return model_calls, tool_calls, repeated_read_signals


def run_demo(*, mode: str, use_aegis: bool) -> Path:
    env = load_demo_env()
    _ensure_local_deepagents_import()

    from deepagents.backends import FilesystemBackend
    from deepagents.graph import create_deep_agent

    run_root = Path("results") / mode
    if run_root.exists():
        for p in sorted(run_root.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
        for p in sorted(run_root.rglob("*"), reverse=True):
            if p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass

    build_workspace(run_root)
    backend = FilesystemBackend(root_dir=str(run_root), virtual_mode=True)

    system_prompt = SYSTEM_PROMPT
    extra_model_kwargs: dict[str, Any] = {}
    metrics = RunMetrics(mode=mode)

    if use_aegis:
        from adapters.aegis_middleware import AegisDeepAgentsAdapter

        adapter = AegisDeepAgentsAdapter(
            base_prompt=SYSTEM_PROMPT,
            api_key=env.aegis_api_key,
            base_url=env.aegis_base_url,
        )
        system_prompt = adapter.apply_system_prompt(SYSTEM_PROMPT)
        extra_model_kwargs = adapter.generation_kwargs()
        (run_root / "aegis_plan.json").write_text(
            json.dumps(adapter.raw_plan(), indent=2) + "\n",
            encoding="utf-8",
        )

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=extra_model_kwargs.get("temperature", 0.7),
        top_p=extra_model_kwargs.get("top_p", 1.0),
    )

    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        backend=backend,
    )

    result: Any = None
    output_text = ""
    error_text = None

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": USER_TASK}]},
            config={"recursion_limit": 40},
        )
        output_text = _extract_text(result)
        metrics.completed = True
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"
        result = {"error": error_text}
        output_text = ""
        metrics.completed = False
        metrics.notes.append("run_failed")

    output_path = run_root / "final_output.txt"
    output_path.write_text(output_text, encoding="utf-8")

    result_path = run_root / "raw_result.json"
    result_path.write_text(json.dumps(str(result), indent=2) + "\n", encoding="utf-8")

    if error_text is not None:
        (run_root / "error.txt").write_text(error_text + "\n", encoding="utf-8")

    model_calls, tool_calls, repeated_tool_signals = _count_signals(result)
    scoring = evaluate_output(run_root, output_text)

    metrics.model_calls = model_calls
    metrics.tool_calls = tool_calls
    metrics.repeated_tool_signals = repeated_tool_signals
    metrics.final_output_present = bool(output_text.strip())
    metrics.output_path = str(output_path)

    metrics.parsed_json = scoring["parsed_json"]
    metrics.selected_ids = scoring["selected_ids"]
    metrics.average_score = scoring["average_score"]
    metrics.correct_top3 = scoring["correct_top3"]
    metrics.correct_average = scoring["correct_average"]
    metrics.exact_match = scoring["exact_match"]
    metrics.score = scoring["score"]

    if metrics.parsed_json:
        metrics.notes.append("structured_output_detected")
    if metrics.correct_top3:
        metrics.notes.append("top3_correct")
    if metrics.correct_average:
        metrics.notes.append("average_correct")
    if metrics.exact_match:
        metrics.notes.append("exact_match")
    if error_text and "GraphRecursionError" in error_text:
        metrics.notes.append("graph_recursion_error")

    (run_root / "scorecard.json").write_text(
        json.dumps(scoring, indent=2) + "\n",
        encoding="utf-8",
    )

    metrics.save(run_root / "metrics.json")
    return run_root
