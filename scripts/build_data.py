#!/usr/bin/env python3
"""
Master build script - runs all data collection scripts in sequence
and validates the output JSON files.
"""

import json
import os
import subprocess
import sys


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPTS_DIR, "..", "data")

SCRIPTS = [
    "collect_os_requirements.py",
    "scrape_intel_cpus.py",
    "scrape_amd_cpus.py",
    "scrape_windows_cpu_whitelist.py",
]

EXPECTED_FILES = [
    "os-requirements.json",
    "cpu-intel.json",
    "cpu-amd.json",
    "windows-cpu-whitelist-win10-1809.json",
    "windows-cpu-whitelist-win10-21h2.json",
    "windows-cpu-whitelist-win10-22h2.json",
    "windows-cpu-whitelist-win11-22h2.json",
    "windows-cpu-whitelist-win11-24h2.json",
    "windows-cpu-whitelist-win11-25h2.json",
]


def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=SCRIPTS_DIR,
            capture_output=False,
            timeout=120
        )
        if result.returncode != 0:
            print(f"ERROR: {script_name} exited with code {result.returncode}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"ERROR: {script_name} timed out after 120s")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run {script_name}: {e}")
        return False


def validate_json(filename: str) -> bool:
    """Validate that a JSON file exists and is valid."""
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"FAIL: {filename} does not exist")
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: {filename} is not valid JSON: {e}")
        return False

    # Check metadata
    if "metadata" not in data:
        print(f"WARN: {filename} missing metadata")

    # Check counts
    if filename == "os-requirements.json":
        count = len(data.get("operatingSystems", []))
        print(f"  OK: {filename} - {count} OS entries")
        if count < 10:
            print(f"  WARN: Expected at least 10 OS entries, got {count}")
    elif filename.startswith("cpu-"):
        count = len(data.get("cpus", []))
        print(f"  OK: {filename} - {count} CPU entries")
        if count < 5:
            print(f"  WARN: Expected at least 5 CPU entries, got {count}")
    elif filename.startswith("windows-cpu-whitelist-"):
        intel_count = len(data.get("intel", []))
        amd_count = len(data.get("amd", []))
        qualcomm_count = len(data.get("qualcomm", []))
        print(f"  OK: {filename} - {intel_count} Intel + {amd_count} AMD + {qualcomm_count} Qualcomm entries")

    return True


def main():
    print("CPU/OS Compatibility Search - Data Build")
    print("=" * 60)

    # Run all scripts
    all_ok = True
    for script in SCRIPTS:
        if not run_script(script):
            all_ok = False
            print(f"WARNING: {script} failed, continuing with remaining scripts...")

    # Validate output files
    print(f"\n{'='*60}")
    print("Validating output files...")
    print(f"{'='*60}")

    for filename in EXPECTED_FILES:
        if not validate_json(filename):
            all_ok = False

    print(f"\n{'='*60}")
    if all_ok:
        print("BUILD COMPLETE - All files generated and validated successfully")
    else:
        print("BUILD COMPLETE WITH WARNINGS - Some steps had issues")
    print(f"{'='*60}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
