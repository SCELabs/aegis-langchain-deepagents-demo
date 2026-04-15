from demo.run_shared import run_demo


if __name__ == "__main__":
    path = run_demo(mode="aegis", use_aegis=True)
    print(f"aegis results written to: {path}")
