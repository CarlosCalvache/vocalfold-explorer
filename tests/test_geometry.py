"""
tests/test_geometry.py
=======================
Pytest tests verifying computed vocal fold geometry against Table 5
of the original manuscript.

Reference values (from Table 5):
    Activation 1: aLCA=0.5, aTA=0.6, aCT=0.3
    Activation 2: aLCA=0.4, aTA=0.4, aCT=0.6

Tolerance: ±0.02 mm for all geometry outputs.

Run with:
    pytest tests/test_geometry.py -v
"""

import pytest
from vocal_geometry.model import calculate_all


# ─────────────────────────────────────────────────────────────────────────────
# Tolerance
# ─────────────────────────────────────────────────────────────────────────────

ABS_TOL_MM = 0.02   # mm — maximum allowed absolute deviation


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def act1_male():
    """Activation 1, Male."""
    return calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Male")


@pytest.fixture(scope="module")
def act1_female():
    """Activation 1, Female."""
    return calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Female")


@pytest.fixture(scope="module")
def act2_male():
    """Activation 2, Male."""
    return calculate_all(aCT=0.6, aTA=0.4, aLCA=0.4, sex="Male")


@pytest.fixture(scope="module")
def act2_female():
    """Activation 2, Female."""
    return calculate_all(aCT=0.6, aTA=0.4, aLCA=0.4, sex="Female")


# ─────────────────────────────────────────────────────────────────────────────
# Activation 1 — Male
# ─────────────────────────────────────────────────────────────────────────────

class TestActivation1Male:
    """Table 5 reference: Act1 Male — Length=15.36, Width=3.09, Zn=1.62, Db=3.42, Dc=3.02"""

    def test_elongation(self, act1_male):
        """Epsilon should be -0.04 for Act1."""
        assert abs(act1_male.epsilon - (-0.04)) < 1e-10

    def test_length(self, act1_male):
        assert abs(act1_male.length_mm - 15.36) < ABS_TOL_MM, (
            f"Length: expected 15.36, got {act1_male.length_mm:.4f}"
        )

    def test_thickness(self, act1_male):
        assert abs(act1_male.thickness_mm - 3.09) < ABS_TOL_MM, (
            f"Thickness: expected 3.09, got {act1_male.thickness_mm:.4f}"
        )

    def test_nodal_point(self, act1_male):
        assert abs(act1_male.nodal_point_mm - 1.62) < ABS_TOL_MM, (
            f"Nodal Point: expected 1.62, got {act1_male.nodal_point_mm:.4f}"
        )

    def test_body_depth(self, act1_male):
        assert abs(act1_male.body_depth_mm - 3.42) < ABS_TOL_MM, (
            f"Body Depth: expected 3.42, got {act1_male.body_depth_mm:.4f}"
        )

    def test_cover_depth(self, act1_male):
        assert abs(act1_male.cover_depth_mm - 3.02) < ABS_TOL_MM, (
            f"Cover Depth: expected 3.02, got {act1_male.cover_depth_mm:.4f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Activation 1 — Female
# ─────────────────────────────────────────────────────────────────────────────

class TestActivation1Female:
    """Table 5 reference: Act1 Female — Length=9.6, Width=2.06, Zn=1.38, Db=2.57, Dc=2.26"""

    def test_length(self, act1_female):
        assert abs(act1_female.length_mm - 9.60) < ABS_TOL_MM, (
            f"Length: expected 9.60, got {act1_female.length_mm:.4f}"
        )

    def test_thickness(self, act1_female):
        assert abs(act1_female.thickness_mm - 2.06) < ABS_TOL_MM, (
            f"Thickness: expected 2.06, got {act1_female.thickness_mm:.4f}"
        )

    def test_nodal_point(self, act1_female):
        assert abs(act1_female.nodal_point_mm - 1.38) < ABS_TOL_MM, (
            f"Nodal Point: expected 1.38, got {act1_female.nodal_point_mm:.4f}"
        )

    def test_body_depth(self, act1_female):
        assert abs(act1_female.body_depth_mm - 2.57) < ABS_TOL_MM, (
            f"Body Depth: expected 2.57, got {act1_female.body_depth_mm:.4f}"
        )

    def test_cover_depth(self, act1_female):
        assert abs(act1_female.cover_depth_mm - 2.26) < ABS_TOL_MM, (
            f"Cover Depth: expected 2.26, got {act1_female.cover_depth_mm:.4f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Activation 2 — Male
# ─────────────────────────────────────────────────────────────────────────────

class TestActivation2Male:
    """Table 5 reference: Act2 Male — Length=19.2, Width=2.58, Zn=1.33, Db=2.50, Dc=2.88"""

    def test_elongation(self, act2_male):
        """Epsilon should be 0.20 for Act2."""
        assert abs(act2_male.epsilon - 0.20) < 1e-10

    def test_length(self, act2_male):
        assert abs(act2_male.length_mm - 19.20) < ABS_TOL_MM, (
            f"Length: expected 19.20, got {act2_male.length_mm:.4f}"
        )

    def test_thickness(self, act2_male):
        assert abs(act2_male.thickness_mm - 2.58) < ABS_TOL_MM, (
            f"Thickness: expected 2.58, got {act2_male.thickness_mm:.4f}"
        )

    def test_nodal_point(self, act2_male):
        assert abs(act2_male.nodal_point_mm - 1.33) < ABS_TOL_MM, (
            f"Nodal Point: expected 1.33, got {act2_male.nodal_point_mm:.4f}"
        )

    def test_body_depth(self, act2_male):
        assert abs(act2_male.body_depth_mm - 2.50) < ABS_TOL_MM, (
            f"Body Depth: expected 2.50, got {act2_male.body_depth_mm:.4f}"
        )

    def test_cover_depth(self, act2_male):
        assert abs(act2_male.cover_depth_mm - 2.88) < ABS_TOL_MM, (
            f"Cover Depth: expected 2.88, got {act2_male.cover_depth_mm:.4f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Activation 2 — Female
# ─────────────────────────────────────────────────────────────────────────────

class TestActivation2Female:
    """Table 5 reference: Act2 Female — Length=12.0, Width=1.72, Zn=1.21, Db=1.87, Dc=2.16"""

    def test_length(self, act2_female):
        assert abs(act2_female.length_mm - 12.00) < ABS_TOL_MM, (
            f"Length: expected 12.00, got {act2_female.length_mm:.4f}"
        )

    def test_thickness(self, act2_female):
        assert abs(act2_female.thickness_mm - 1.72) < ABS_TOL_MM, (
            f"Thickness: expected 1.72, got {act2_female.thickness_mm:.4f}"
        )

    def test_nodal_point(self, act2_female):
        assert abs(act2_female.nodal_point_mm - 1.21) < ABS_TOL_MM, (
            f"Nodal Point: expected 1.21, got {act2_female.nodal_point_mm:.4f}"
        )

    def test_body_depth(self, act2_female):
        assert abs(act2_female.body_depth_mm - 1.87) < ABS_TOL_MM, (
            f"Body Depth: expected 1.87, got {act2_female.body_depth_mm:.4f}"
        )

    def test_cover_depth(self, act2_female):
        assert abs(act2_female.cover_depth_mm - 2.16) < ABS_TOL_MM, (
            f"Cover Depth: expected 2.16, got {act2_female.cover_depth_mm:.4f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Edge cases & physical constraints
# ─────────────────────────────────────────────────────────────────────────────

class TestPhysicalConstraints:
    """Verify physical plausibility over a range of activations."""

    @pytest.mark.parametrize("aCT,aTA,aLCA,sex", [
        (0.0, 0.0, 0.0, "Male"),
        (1.0, 0.0, 0.0, "Male"),
        (0.0, 1.0, 0.0, "Male"),
        (0.5, 0.5, 0.5, "Male"),
        (0.0, 0.0, 0.0, "Female"),
        (1.0, 1.0, 1.0, "Female"),
    ])
    def test_positive_geometry(self, aCT, aTA, aLCA, sex):
        """All geometry outputs must be positive."""
        s = calculate_all(aCT=aCT, aTA=aTA, aLCA=aLCA, sex=sex)
        assert s.length_mm > 0,       f"length_mm ≤ 0 for {aCT},{aTA},{aLCA},{sex}"
        assert s.thickness_mm > 0,    f"thickness_mm ≤ 0"
        assert s.nodal_point_mm > 0,  f"nodal_point_mm ≤ 0"
        assert s.body_depth_mm > 0,   f"body_depth_mm ≤ 0"
        assert s.cover_depth_mm > 0,  f"cover_depth_mm ≤ 0"

    @pytest.mark.parametrize("aCT,aTA,aLCA,sex", [
        (0.5, 0.5, 0.5, "Male"),
        (0.5, 0.5, 0.5, "Female"),
    ])
    def test_positive_masses(self, aCT, aTA, aLCA, sex):
        """All masses must be positive."""
        s = calculate_all(aCT=aCT, aTA=aTA, aLCA=aLCA, sex=sex)
        assert s.body_mass_kg > 0
        assert s.upper_mass_kg > 0
        assert s.lower_mass_kg > 0

    def test_ct_increases_length(self):
        """Higher aCT → longer fold (all else equal)."""
        s_low  = calculate_all(aCT=0.2, aTA=0.5, aLCA=0.3, sex="Male")
        s_high = calculate_all(aCT=0.8, aTA=0.5, aLCA=0.3, sex="Male")
        assert s_high.length_mm > s_low.length_mm

    def test_ta_increases_thickness(self):
        """Higher aTA → thicker fold (all else equal)."""
        s_low  = calculate_all(aCT=0.5, aTA=0.1, aLCA=0.3, sex="Male")
        s_high = calculate_all(aCT=0.5, aTA=0.9, aLCA=0.3, sex="Male")
        assert s_high.thickness_mm > s_low.thickness_mm

    def test_male_longer_than_female(self):
        """Male folds are longer than female folds at same activation."""
        s_m = calculate_all(aCT=0.5, aTA=0.5, aLCA=0.5, sex="Male")
        s_f = calculate_all(aCT=0.5, aTA=0.5, aLCA=0.5, sex="Female")
        assert s_m.length_mm > s_f.length_mm
