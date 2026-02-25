import subprocess
import sys
import os

VENV_DIR = ".venv"

def main():
    if os.path.exists(VENV_DIR):
        print(f"Virtual environment '{VENV_DIR}' already exists.")
        return

    print(f"Creating virtual environment in '{VENV_DIR}'...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print("Done.")
    print()
    print("Activate with:")
    print(f"  Windows:  {VENV_DIR}\\Scripts\\activate")
    print(f"  Unix/Mac: source {VENV_DIR}/bin/activate")

if __name__ == "__main__":
    main()
