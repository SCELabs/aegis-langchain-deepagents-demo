from demo.run_shared import run_demo


if __name__ == "__main__":
    path = run_demo(mode="baseline", use_aegis=False)
    print(f"baseline results written to: {path}")
