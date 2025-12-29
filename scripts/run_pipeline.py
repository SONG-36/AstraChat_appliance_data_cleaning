"""
Run full OCR → cleaning → extraction → classification → analysis pipeline.
"""

import subprocess
import sys

def run(cmd: list):
    print(f"\n>>> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("❌ Step failed")
        sys.exit(1)

def main():
    print("=== OCR Data Pipeline Started ===")

    # Step 1: Clean & extract structured fields
    run(["python", "src/clean_text.py"])

    # Step 2: Classify power type
    run(["python", "scripts/classify_power_type.py"])

    # Step 3: Analyze field coverage
    run(["python", "scripts/analyze_field_coverage_by_power_type.py"])

    print("\n✅ Pipeline completed successfully.")

if __name__ == "__main__":
    main()
