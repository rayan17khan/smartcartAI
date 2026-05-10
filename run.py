"""
SmartCart AI - Application Startup Script
=========================================
Run this file to start the full application:
    python run.py

This script:
  1. Verifies all dependencies are installed
  2. Checks that datasets exist (generates them if not)
  3. Runs data preprocessing
  4. Starts the Flask server on http://localhost:5000
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ANSI colours
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def ok(msg):
    print(f"  {GREEN}[OK]{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}[!]{RESET}  {msg}")


def err(msg):
    print(f"  {RED}[X]{RESET}  {msg}")


def info(msg):
    print(f"  {BLUE}[>]{RESET}  {msg}")


def banner():
    print(
        f"""
{BOLD}{BLUE}+----------------------------------------------------------+
| SmartCart AI - E-Commerce Recommendation System         |
| Powered by Machine Learning and Flask                   |
+----------------------------------------------------------+{RESET}
"""
    )


def check_python():
    print(f"{BOLD}[1/5] Checking Python version...{RESET}")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        err(f"Python 3.9+ required (found {v.major}.{v.minor})")
        sys.exit(1)
    ok(f"Python {v.major}.{v.minor}.{v.micro}")


def check_dependencies():
    print(f"\n{BOLD}[2/5] Checking dependencies...{RESET}")
    required = [
        "flask",
        "flask_login",
        "flask_sqlalchemy",
        "flask_cors",
        "pandas",
        "numpy",
        "sklearn",
        "scipy",
        "matplotlib",
        "faker",
    ]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            ok(pkg)
        except ImportError:
            err(f"{pkg} (MISSING)")
            missing.append(pkg)

    if missing:
        warn(f"{len(missing)} packages missing - installing now...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", os.path.join(BASE_DIR, "requirements.txt"), "-q"]
        )
        ok("All dependencies installed")


def check_datasets():
    print(f"\n{BOLD}[3/5] Checking datasets...{RESET}")
    files = {
        "products.csv": 10000,
        "users.csv": 5000,
        "interactions.csv": 100000,
    }
    all_ok = True
    for fname, min_rows in files.items():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            err(f"{fname} not found")
            all_ok = False
        else:
            with open(path, encoding="utf-8", errors="ignore") as handle:
                rows = sum(1 for _ in handle) - 1
            if rows < min_rows:
                warn(f"{fname}: only {rows:,} rows (expected {min_rows:,}+)")
            else:
                ok(f"{fname}: {rows:,} rows")

    if not all_ok:
        warn("Generating missing datasets...")
        subprocess.check_call([sys.executable, os.path.join(BASE_DIR, "utils", "generate_dataset.py")])
        ok("Datasets generated")


def run_preprocessing():
    print(f"\n{BOLD}[4/5] Running data preprocessing...{RESET}")
    preprocessed = os.path.join(DATA_DIR, "products_preprocessed.csv")
    if os.path.exists(preprocessed):
        ok("Preprocessed data already exists - skipping")
    else:
        info("Running preprocessing pipeline...")
        subprocess.check_call([sys.executable, os.path.join(BASE_DIR, "utils", "preprocess.py")])
        ok("Preprocessing complete")


def start_server():
    print(f"\n{BOLD}[5/5] Starting Flask server...{RESET}")
    print()
    print(f"  {BOLD}{'-' * 52}{RESET}")
    print(f"  {BOLD}  SmartCart AI is running!{RESET}")
    print(f"  {BOLD}{'-' * 52}{RESET}")
    print(f"  {GREEN}  Local:   http://localhost:5000{RESET}")
    print(f"  {GREEN}  Network: http://0.0.0.0:5000{RESET}")
    print(f"  {BOLD}{'-' * 52}{RESET}")
    print(
        f"""
  {BOLD}Test Accounts:{RESET}
    admin   / Admin@123   (Admin Dashboard access)
    alice   / Alice@123
    bob     / Bob@123
    charlie / Charlie@123
    demo    / Demo@123

  Press Ctrl+C to stop the server.
"""
    )
    os.chdir(BASE_DIR)
    sys.path.insert(0, BASE_DIR)
    from app import app

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    banner()
    check_python()
    check_dependencies()
    check_datasets()
    run_preprocessing()
    start_server()
