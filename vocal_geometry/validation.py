"""
vocal_geometry/validation.py
=============================
Reference data and comparison utilities for validating the model
against the manuscript tables.

Reference values come from:
  - Table 5: Vocal fold geometry
  - Table 6: Vocal fold masses and springs
of the original Vocal Geometry App manuscript.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import math

from vocal_geometry.model import VocalFoldState, calculate_all


# ─────────────────────────────────────────────────────────────────────────────
# Reference activations
# ─────────────────────────────────────────────────────────────────────────────

REFERENCE_ACTIVATIONS = {
    "Activation 1": dict(aCT=0.3, aTA=0.6, aLCA=0.5),
    "Activation 2": dict(aCT=0.6, aTA=0.4, aLCA=0.4),
}

# ─────────────────────────────────────────────────────────────────────────────
# Table 5 reference values
# ─────────────────────────────────────────────────────────────────────────────

TABLE_5_REFERENCE = {
    ("Activation 1", "Male"): {
        "length_mm":       15.36,
        "thickness_mm":     3.09,
        "nodal_point_mm":   1.62,
        "body_depth_mm":    3.42,
        "cover_depth_mm":   3.02,
    },
    ("Activation 1", "Female"): {
        "length_mm":        9.60,
        "thickness_mm":     2.06,
        "nodal_point_mm":   1.38,
        "body_depth_mm":    2.57,
        "cover_depth_mm":   2.26,
    },
    ("Activation 2", "Male"): {
        "length_mm":       19.20,
        "thickness_mm":     2.58,
        "nodal_point_mm":   1.33,
        "body_depth_mm":    2.50,
        "cover_depth_mm":   2.88,
    },
    ("Activation 2", "Female"): {
        "length_mm":       12.00,
        "thickness_mm":     1.72,
        "nodal_point_mm":   1.21,
        "body_depth_mm":    1.87,
        "cover_depth_mm":   2.16,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Table 6 reference values
# ─────────────────────────────────────────────────────────────────────────────

TABLE_6_REFERENCE = {
    ("Activation 1", "Male"): {
        "body_mass_kg":   1.69e-4,
        "upper_mass_kg":  7.85e-5,
        "lower_mass_kg":  7.12e-5,
        "body_spring":   -2.10e+4,
        "cover_spring":   7.20e+3,
        "upper_spring":   9.70e+3,
        "lower_spring":   8.80e+3,
    },
    ("Activation 1", "Female"): {
        "body_mass_kg":   5.30e-5,
        "upper_mass_kg":  3.13e-5,
        "lower_mass_kg":  1.54e-5,
        "body_spring":   -2.30e+4,
        "cover_spring":   3.20e+3,
        "upper_spring":   7.30e+3,
        "lower_spring":   3.60e+3,
    },
    ("Activation 2", "Male"): {
        "body_mass_kg":   1.23e-4,
        "upper_mass_kg":  7.69e-5,
        "lower_mass_kg":  7.19e-5,
        "body_spring":    4.00e+4,
        "cover_spring":   1.10e+4,
        "upper_spring":   9.80e+3,
        "lower_spring":   9.20e+3,
    },
    ("Activation 2", "Female"): {
        "body_mass_kg":   4.03e-5,
        "upper_mass_kg":  3.27e-5,
        "lower_mass_kg":  1.38e-5,
        "body_spring":    2.20e+4,
        "cover_spring":   4.20e+3,
        "upper_spring":   7.70e+3,
        "lower_spring":   3.20e+3,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Comparison result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ComparisonResult:
    """Result of one numerical comparison between computed and reference."""
    variable: str
    computed: float
    reference: float
    absolute_error: float
    relative_error_pct: float
    tolerance: float         # absolute (mm, kg) or relative (fraction)
    tolerance_type: str      # "absolute" or "relative"
    passed: bool

    def __str__(self) -> str:
        status = "PASS ✓" if self.passed else "FAIL ✗"
        return (
            f"  [{status}] {self.variable}: "
            f"computed={self.computed:.4g}, ref={self.reference:.4g}, "
            f"abs_err={self.absolute_error:.4g}, "
            f"rel_err={self.relative_error_pct:.2f}%"
        )


def _relative_error(computed: float, reference: float) -> float:
    """Relative error in percent. Returns 0 if reference is 0."""
    if reference == 0:
        return 0.0 if computed == 0 else float("inf")
    return abs(computed - reference) / abs(reference) * 100.0


def compare_geometry(
    state: VocalFoldState,
    activation_label: str,
    abs_tol_mm: float = 0.02,
) -> list[ComparisonResult]:
    """
    Compare computed geometry against Table 5 reference values.

    Parameters
    ----------
    state           : computed VocalFoldState
    activation_label: "Activation 1" or "Activation 2"
    abs_tol_mm      : absolute tolerance in mm (default 0.02 mm)

    Returns
    -------
    list of ComparisonResult
    """
    key = (activation_label, state.sex)
    ref = TABLE_5_REFERENCE.get(key, {})
    results = []

    fields = [
        ("length_mm",       "Length [mm]"),
        ("thickness_mm",    "Thickness [mm]"),
        ("nodal_point_mm",  "Nodal Point [mm]"),
        ("body_depth_mm",   "Body Depth [mm]"),
        ("cover_depth_mm",  "Cover Depth [mm]"),
    ]

    for attr, label in fields:
        computed = getattr(state, attr)
        reference = ref.get(attr, float("nan"))
        abs_err = abs(computed - reference)
        rel_err = _relative_error(computed, reference)
        passed = abs_err <= abs_tol_mm

        results.append(ComparisonResult(
            variable=label,
            computed=computed,
            reference=reference,
            absolute_error=abs_err,
            relative_error_pct=rel_err,
            tolerance=abs_tol_mm,
            tolerance_type="absolute",
            passed=passed,
        ))

    return results


def compare_mechanics(
    state: VocalFoldState,
    activation_label: str,
    mass_rel_tol: float = 0.03,   # 3%
    spring_rel_tol: float = 0.05,  # 5%
) -> list[ComparisonResult]:
    """
    Compare computed masses and springs against Table 6 reference values.

    Parameters
    ----------
    state            : computed VocalFoldState
    activation_label : "Activation 1" or "Activation 2"
    mass_rel_tol     : relative tolerance for masses (default 3%)
    spring_rel_tol   : relative tolerance for springs (default 5%)

    Returns
    -------
    list of ComparisonResult
    """
    key = (activation_label, state.sex)
    ref = TABLE_6_REFERENCE.get(key, {})
    results = []

    mass_fields = [
        ("body_mass_kg",   "Body Mass [kg]",      mass_rel_tol),
        ("upper_mass_kg",  "Upper Mass M1 [kg]",  mass_rel_tol),
        ("lower_mass_kg",  "Lower Mass M2 [kg]",  mass_rel_tol),
    ]
    spring_fields = [
        ("body_spring",    "Body Spring [Pa·mm]",  spring_rel_tol),
        ("cover_spring",   "Cover Spring [Pa·mm]", spring_rel_tol),
        ("upper_spring",   "Upper Spring K1 [Pa·mm]", spring_rel_tol),
        ("lower_spring",   "Lower Spring K2 [Pa·mm]", spring_rel_tol),
    ]

    for attr, label, tol in mass_fields + spring_fields:
        computed = getattr(state, attr)
        reference = ref.get(attr, float("nan"))
        abs_err = abs(computed - reference)
        rel_err = _relative_error(computed, reference)
        passed = rel_err <= (tol * 100)

        results.append(ComparisonResult(
            variable=label,
            computed=computed,
            reference=reference,
            absolute_error=abs_err,
            relative_error_pct=rel_err,
            tolerance=tol * 100,
            tolerance_type="relative",
            passed=passed,
        ))

    return results


def run_full_validation() -> dict[str, Any]:
    """
    Run the complete validation against Tables 5 and 6 for all 4 cases.

    Returns
    -------
    dict with keys:
        "all_passed"   : bool
        "cases"        : list of case result dicts
        "n_passed"     : int
        "n_failed"     : int
        "failures"     : list of ComparisonResult that failed
    """
    cases = []
    all_results = []

    for act_label, act_vals in REFERENCE_ACTIVATIONS.items():
        for sex in ("Male", "Female"):
            state = calculate_all(sex=sex, **act_vals)
            geo_results  = compare_geometry(state, act_label)
            mech_results = compare_mechanics(state, act_label)
            combined = geo_results + mech_results

            cases.append({
                "label": f"{act_label} / {sex}",
                "state": state,
                "results": combined,
                "passed": all(r.passed for r in combined),
            })
            all_results.extend(combined)

    failures = [r for r in all_results if not r.passed]
    return {
        "all_passed": len(failures) == 0,
        "cases": cases,
        "n_passed": sum(1 for r in all_results if r.passed),
        "n_failed": len(failures),
        "failures": failures,
    }
