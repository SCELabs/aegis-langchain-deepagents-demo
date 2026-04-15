from supervisor.run_supervised import run_supervised

if __name__ == "__main__":
    path = run_supervised(mode="aegis_supervisor")
    print(f"aegis supervisor results written to: {path}")
