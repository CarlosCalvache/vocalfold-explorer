"""
validation/reproduce_table_6.py
================================
Reproduces Table 6 from the manuscript: vocal fold masses and springs
for the two reference muscle activations and both sexes.

Run with:
    python validation/reproduce_table_6.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vocal_geometry.model import calculate_all
from vocal_geometry.validation import TABLE_6_REFERENCE, REFERENCE_ACTIVATIONS, _relative_error
import pandas as pd


def reproduce_table_6():
    """Print computed vs reference values for Table 6."""
    print("\n" + "=" * 80)
    print("TABLE 6 REPRODUCTION — Vocal Fold Mechanics")
    print("=" * 80)
    print(f"{'Variable':<22} {'Reference':>12} {'Computed':>12} {'Rel Error(%)':>12} {'Status':>8}")
    print("-" * 70)

    all_passed = True
    rows = []

    for act_label, act_vals in REFERENCE_ACTIVATIONS.items():
        print(f"\n  ── {act_label}: aCT={act_vals['aCT']}, aTA={act_vals['aTA']}, aLCA={act_vals['aLCA']}")
        for sex in ("Male", "Female"):
            s = calculate_all(sex=sex, **act_vals)
            ref = TABLE_6_REFERENCE[(act_label, sex)]
            print(f"\n    [{sex}]")

            mass_vars = [
                ("body_mass_kg",   "Body Mass [kg]"),
                ("upper_mass_kg",  "Mass 1 [kg]"),
                ("lower_mass_kg",  "Mass 2 [kg]"),
            ]
            spring_vars = [
                ("body_spring",    "Body Spring [Pa*mm]"),
                ("cover_spring",   "Spring C [Pa*mm]"),
                ("upper_spring",   "Spring 1 [Pa*mm]"),
                ("lower_spring",   "Spring 2 [Pa*mm]"),
            ]

            for attr, label in mass_vars + spring_vars:
                comp    = getattr(s, attr)
                ref_val = ref[attr]
                rel_err = _relative_error(comp, ref_val)
                
                tol = 6.0 if attr in dict(mass_vars) else 7.0 # 6% for masses, 7% for springs
                ok  = rel_err <= tol
                
                sym = "✓" if ok else "✗"
                if not ok:
                    all_passed = False
                
                print(f"      {label:<20} {ref_val:>10.2e}  {comp:>10.2e}  {rel_err:>11.2f}%  {sym}")
                rows.append({
                    "Activation": act_label,
                    "Sex":        sex,
                    "Variable":   label,
                    "Reference":  f"{ref_val:.2e}",
                    "Computed":   f"{comp:.2e}",
                    "Rel Error(%)": round(rel_err, 2),
                    "Pass":       ok,
                })

    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL Table 6 values reproduced within tolerances.")
    else:
        print("✗ Some values FAILED. See above for details.")
    print("=" * 80 + "\n")

    # Save to CSV
    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(__file__), "table6_results.csv")
    df.to_csv(out_path, index=False)
    print(f"Results saved to: {out_path}")

    return all_passed


if __name__ == "__main__":
    passed = reproduce_table_6()
    sys.exit(0 if passed else 1)
