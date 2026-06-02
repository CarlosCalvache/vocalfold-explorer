"""
validation/run_all_validation.py
=================================
Runs both table reproductions and unit tests.
"""

import sys
import os
import subprocess

def run():
    print("=" * 80)
    print("RUNNING VOCAL GEOMETRY VALIDATION SUITE")
    print("=" * 80)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n[1] Running pytest on test suite...")
    res_pytest = subprocess.run(["venv/bin/pytest", "tests/", "-v"], cwd=project_root)
    
    print("\n[2] Running Table 5 Reproduction...")
    res_t5 = subprocess.run(["venv/bin/python", "validation/reproduce_table_5.py"], cwd=project_root)
    
    print("\n[3] Running Table 6 Reproduction...")
    res_t6 = subprocess.run(["venv/bin/python", "validation/reproduce_table_6.py"], cwd=project_root)
    
    print("\n" + "=" * 80)
    if res_pytest.returncode == 0 and res_t5.returncode == 0 and res_t6.returncode == 0:
        print("ALL VALIDATIONS PASSED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("SOME VALIDATIONS FAILED. CHECK OUTPUTS ABOVE.")
        sys.exit(1)

if __name__ == "__main__":
    run()
