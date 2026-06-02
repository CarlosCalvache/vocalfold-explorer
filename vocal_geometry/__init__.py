"""
vocal_geometry/__init__.py
===========================
Public API of the vocal_geometry package.

Usage
-----
    from vocal_geometry import calculate_all, VocalFoldState

    state = calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Male")
    print(state.length_mm)   # → 15.36
"""

from vocal_geometry.model import (
    calculate_all,
    calculate_elongation,
    calculate_length,
    calculate_thickness,
    calculate_nodal_point,
    calculate_body_depth,
    calculate_cover_depth,
    calculate_masses,
    calculate_passive_stress,
    calculate_muscle_stress,
    calculate_body_cover_stress,
    calculate_springs,
    VocalFoldState,
)

from vocal_geometry.constants import (
    SEX_PARAMS,
    MALE,
    FEMALE,
    G, R, H,
    TISSUE_DENSITY,
)

__all__ = [
    "calculate_all",
    "calculate_elongation",
    "calculate_length",
    "calculate_thickness",
    "calculate_nodal_point",
    "calculate_body_depth",
    "calculate_cover_depth",
    "calculate_masses",
    "calculate_passive_stress",
    "calculate_muscle_stress",
    "calculate_body_cover_stress",
    "calculate_springs",
    "VocalFoldState",
    "SEX_PARAMS",
    "MALE",
    "FEMALE",
    "G", "R", "H",
    "TISSUE_DENSITY",
]
