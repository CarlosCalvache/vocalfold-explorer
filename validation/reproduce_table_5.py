"""
validation/reproduce_table_5.py
================================
Reproduces Table 5 from the manuscript: vocal fold geometry values for
the two reference muscle activations and both sexes.

Run with:
    python validation/reproduce_table_5.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vocal_geometry.model import calculate_all
from vocal_geometry.validation import TABLE_5_REFERENCE, REFERENCE_ACTIVATIONS
import pandas as pd


def reproduce_table_5():
    """Print computed vs reference values for Table 5."""
    print("\n" + "=" * 80)
    print("TABLE 5 REPRODUCTION — Vocal Fold Geometry")
    print("=" * 80)
    print(f"{'Variable':<22} {'Reference':>12} {'Computed':>12} {'Error(mm)':>12} {'Status':>8}")
    print("-" * 70)

    all_passed = True
    rows = []

    for act_label, act_vals in REFERENCE_ACTIVATIONS.items():
        print(f"\n  ── {act_label}: aCT={act_vals['aCT']}, aTA={act_vals['aTA']}, aLCA={act_vals['aLCA']}")
        for sex in ("Male", "Female"):
            s = calculate_all(sex=sex, **act_vals)
            ref = TABLE_5_REFERENCE[(act_label, sex)]
            print(f"\n    [{sex}]")

            for attr, label, ref_val in [
                ("length_mm",       "Length [mm]",       ref["length_mm"]),
                ("thickness_mm",    "Thickness [mm]",    ref["thickness_mm"]),
                ("nodal_point_mm",  "Nodal Point [mm]",  ref["nodal_point_mm"]),
                ("body_depth_mm",   "Body Depth [mm]",   ref["body_depth_mm"]),
                ("cover_depth_mm",  "Cover Depth [mm]",  ref["cover_depth_mm"]),
            ]:
                comp  = getattr(s, attr)
                err   = abs(comp - ref_val)
                ok    = err <= 0.02
                sym   = "✓" if ok else "✗"
                if not ok:
                    all_passed = False
                print(f"      {label:<20} {ref_val:>10.3f}  {comp:>10.4f}  {err:>10.4f}   {sym}")
                rows.append({
                    "Activation": act_label,
                    "Sex":        sex,
                    "Variable":   label,
                    "Reference":  ref_val,
                    "Computed":   round(comp, 4),
                    "Abs Error":  round(err, 4),
                    "Pass":       ok,
                })

    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL Table 5 values reproduced within ±0.02 mm tolerance.")
    else:
        print("✗ Some values FAILED. See above for details.")
    print("=" * 80 + "\n")

    # Save to CSV
    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(__file__), "table5_results.csv")
    df.to_csv(out_path, index=False)
    print(f"Results saved to: {out_path}")

    return all_passed


if __name__ == "__main__":
    passed = reproduce_table_5()
    sys.exit(0 if passed else 1)
