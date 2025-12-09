# main.py
# NTD Clinical Trials Analysis - Main Entry Point
# Group 16 - Lancaster University

import subprocess
import sys
import time
import os

# 脚本执行顺序 Script execution order
SCRIPTS = [
    "CleanData.py",  # 必须第一个运行 Must run first
    "DataFit.py",
    "ExtractDrug.py",
    "Network.py",
    "visualization.py",
    "pregnant.py",
]


def run_script(script_name):
    """运行单个脚本 Run a single script"""
    print(f"\n{'=' * 50}")
    print(f"▶ Running: {script_name}")
    print('=' * 50)

    start = time.time()
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✓ {script_name} done ({time.time() - start:.2f}s)")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {script_name} failed")
        return False
    except FileNotFoundError:
        print(f"✗ {script_name} not found")
        return False


def main():
    print("\n" + "=" * 50)
    print("  NTD Clinical Trials Analysis Pipeline")
    print("  Group 16 - Lancaster University")
    print("=" * 50)

    total_start = time.time()
    success, failed = 0, 0

    for script in SCRIPTS:
        if not os.path.exists(script):
            print(f"⚠ {script} not found, skipping")
            continue
        if run_script(script):
            success += 1
        else:
            failed += 1
            print("停止执行 Stopping due to error")
            break

    # 总结 Summary
    print(f"\n{'=' * 50}")
    print(f"  Done! Success: {success}, Failed: {failed}")
    print(f"  Total time: {time.time() - total_start:.2f}s")
    print("=" * 50)


if __name__ == "__main__":
    main()