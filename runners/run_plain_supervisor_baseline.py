from supervisor.run_plain import run_plain

if __name__ == "__main__":
    path = run_plain(mode="plain_supervisor_baseline")
    print(f"plain baseline results written to: {path}")
