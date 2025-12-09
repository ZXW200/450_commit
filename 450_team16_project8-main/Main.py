"""
Main pipeline controller for NTD clinical trials analysis.
Runs all analysis scripts in the correct order and reports execution status.
"""

import subprocess
import sys
import time
import os

# define execution order - each script depends on outputs from previous ones
SCRIPTS = [
    "CleanData.py",      # clean and preprocess raw data
    "DataFit.py",        # build logistic regression model
    "ExtractDrug.py",    # analyze Chagas drug trends
    "Network.py",        # create collaboration network
    "visualization.py",  # generate geographic and funding visualizations
    "pregnant.py",       # analyze pregnancy inclusion patterns
]


def run_script(script_name):
    """
    Execute a Python script and capture its return status.
    Returns True if successful, False if error occurred.
    """
    print(f"\n{'=' * 50}")
    print(f"Running: {script_name}")
    print('=' * 50)

    start = time.time()
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"{script_name} done ({time.time() - start:.2f}s)")
        return True
    except subprocess.CalledProcessError:
        print(f"{script_name} failed")
        return False
    except FileNotFoundError:
        print(f"{script_name} not found")
        return False


def main():
    """
    Main execution function - runs all analysis scripts sequentially.
    Stops if any script fails to ensure data integrity.
    """
    print("\n" + "=" * 50)
    print("  NTD Clinical Trials Analysis Pipeline")
    print("  Group 16 - Lancaster University")
    print("=" * 50)

    total_start = time.time()
    success, failed = 0, 0

    for script in SCRIPTS:
        if not os.path.exists(script):
            print(f"{script} not found, skipping")
            continue
        if run_script(script):
            success += 1
        else:
            failed += 1
            print("Stopping due to error")
            break

    print(f"\n{'=' * 50}")
    print(f"  Done! Success: {success}, Failed: {failed}")
    print(f"  Total time: {time.time() - total_start:.2f}s")
    print("=" * 50)


if __name__ == "__main__":
    main()
