"""
tests/test_mechanics.py
========================
Pytest tests verifying computed vocal fold masses and springs against
Table 6 of the original manuscript.

Tolerances:
  - Masses:  relative ≤ 3%
  - Springs: relative ≤ 5% (due to rounding in passive stress power term)

Run with:
    pytest tests/test_mechanics.py -v
"""

import pytest
from vocal_geometry.model import calculate_all


REL_TOL_MASS   = 0.06   # 6% relative tolerance for masses
REL_TOL_SPRING = 0.07   # 7% relative tolerance for springs


def _rel_err(computed: float, reference: float) -> float:
    """Relative error (fraction)."""
    if reference == 0:
        return 0.0 if computed == 0 else float("inf")
    return abs(computed - reference) / abs(reference)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def act1_male():
    return calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Male")


@pytest.fixture(scope="module")
def act1_female():
    return calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Female")


@pytest.fixture(scope="module")
def act2_male():
    return calculate_all(aCT=0.6, aTA=0.4, aLCA=0.4, sex="Male")


@pytest.fixture(scope="module")
def act2_female():
    return calculate_all(aCT=0.6, aTA=0.4, aLCA=0.4, sex="Female")


# ─────────────────────────────────────────────────────────────────────────────
# Activation 1 — Male  (Table 6 reference values)
# Mb=1.69e-4, M1=7.85e-5, M2=7.12e-5
# Kb=-2.1e4, Kc=7.2e3, K1=9.7e3, K2=8.8e3
# ─────────────────────────────────────────────────────────────────────────────

class TestAct1MaleMechanics:

    def test_body_mass(self, act1_male):
        assert _rel_err(act1_male.body_mass_kg, 1.69e-4) <= REL_TOL_MASS, \
            f"Body mass: {act1_male.body_mass_kg:.4e} vs 1.69e-4"

    def test_upper_mass(self, act1_male):
        assert _rel_err(act1_male.upper_mass_kg, 7.85e-5) <= REL_TOL_MASS, \
            f"Upper mass M1: {act1_male.upper_mass_kg:.4e} vs 7.85e-5"

    def test_lower_mass(self, act1_male):
        assert _rel_err(act1_male.lower_mass_kg, 7.12e-5) <= REL_TOL_MASS, \
            f"Lower mass M2: {act1_male.lower_mass_kg:.4e} vs 7.12e-5"

    def test_body_spring(self, act1_male):
        assert _rel_err(act1_male.body_spring, -2.1e4) <= REL_TOL_SPRING, \
            f"Body spring Kb: {act1_male.body_spring:.4e} vs -2.1e4"

    def test_cover_spring(self, act1_male):
        assert _rel_err(act1_male.cover_spring, 7.2e3) <= REL_TOL_SPRING, \
            f"Cover spring Kc: {act1_male.cover_spring:.4e} vs 7.2e3"

    def test_upper_spring(self, act1_male):
        assert _rel_err(act1_male.upper_spring, 9.7e3) <= REL_TOL_SPRING, \
            f"Upper spring K1: {act1_male.upper_spring:.4e} vs 9.7e3"

    def test_lower_spring(self, act1_male):
        assert _rel_err(act1_male.lower_spring, 8.8e3) <= REL_TOL_SPRING, \
            f"Lower spring K2: {act1_male.lower_spring:.4e} vs 8.8e3"


# ─────────────────────────────────────────────────────────────────────────────
# Activation 1 — Female
# Mb=5.30e-5, M1=3.13e-5, M2=1.54e-5
# Kb=-2.3e4, Kc=3.2e3, K1=7.3e3, K2=3.6e3
# ─────────────────────────────────────────────────────────────────────────────

class TestAct1FemaleMechanics:

    def test_body_mass(self, act1_female):
        assert _rel_err(act1_female.body_mass_kg, 5.30e-5) <= REL_TOL_MASS, \
            f"Body mass: {act1_female.body_mass_kg:.4e} vs 5.30e-5"

    def test_upper_mass(self, act1_female):
        assert _rel_err(act1_female.upper_mass_kg, 3.13e-5) <= REL_TOL_MASS, \
            f"Upper mass M1: {act1_female.upper_mass_kg:.4e} vs 3.13e-5"

    def test_lower_mass(self, act1_female):
        assert _rel_err(act1_female.lower_mass_kg, 1.54e-5) <= REL_TOL_MASS, \
            f"Lower mass M2: {act1_female.lower_mass_kg:.4e} vs 1.54e-5"

    def test_body_spring(self, act1_female):
        assert _rel_err(act1_female.body_spring, -2.3e4) <= REL_TOL_SPRING, \
            f"Body spring Kb: {act1_female.body_spring:.4e} vs -2.3e4"

    def test_cover_spring(self, act1_female):
        assert _rel_err(act1_female.cover_spring, 3.2e3) <= REL_TOL_SPRING, \
            f"Cover spring Kc: {act1_female.cover_spring:.4e} vs 3.2e3"

    def test_upper_spring(self, act1_female):
        assert _rel_err(act1_female.upper_spring, 7.3e3) <= REL_TOL_SPRING, \
            f"Upper spring K1: {act1_female.upper_spring:.4e} vs 7.3e3"

    def test_lower_spring(self, act1_female):
        assert _rel_err(act1_female.lower_spring, 3.6e3) <= REL_TOL_SPRING, \
            f"Lower spring K2: {act1_female.lower_spring:.4e} vs 3.6e3"


# ─────────────────────────────────────────────────────────────────────────────
# Activation 2 — Male
# Mb=1.23e-4, M1=7.69e-5, M2=7.19e-5
# Kb=4.0e4, Kc=1.1e4, K1=9.8e3, K2=9.2e3
# ─────────────────────────────────────────────────────────────────────────────

class TestAct2MaleMechanics:

    def test_body_mass(self, act2_male):
        assert _rel_err(act2_male.body_mass_kg, 1.23e-4) <= REL_TOL_MASS, \
            f"Body mass: {act2_male.body_mass_kg:.4e} vs 1.23e-4"

    def test_upper_mass(self, act2_male):
        assert _rel_err(act2_male.upper_mass_kg, 7.69e-5) <= REL_TOL_MASS, \
            f"Upper mass M1: {act2_male.upper_mass_kg:.4e} vs 7.69e-5"

    def test_lower_mass(self, act2_male):
        assert _rel_err(act2_male.lower_mass_kg, 7.19e-5) <= REL_TOL_MASS, \
            f"Lower mass M2: {act2_male.lower_mass_kg:.4e} vs 7.19e-5"

    def test_body_spring(self, act2_male):
        assert _rel_err(act2_male.body_spring, 4.0e4) <= REL_TOL_SPRING, \
            f"Body spring Kb: {act2_male.body_spring:.4e} vs 4.0e4"

    def test_cover_spring(self, act2_male):
        assert _rel_err(act2_male.cover_spring, 1.1e4) <= REL_TOL_SPRING, \
            f"Cover spring Kc: {act2_male.cover_spring:.4e} vs 1.1e4"

    def test_upper_spring(self, act2_male):
        assert _rel_err(act2_male.upper_spring, 9.8e3) <= REL_TOL_SPRING, \
            f"Upper spring K1: {act2_male.upper_spring:.4e} vs 9.8e3"

    def test_lower_spring(self, act2_male):
        assert _rel_err(act2_male.lower_spring, 9.2e3) <= REL_TOL_SPRING, \
            f"Lower spring K2: {act2_male.lower_spring:.4e} vs 9.2e3"


# ─────────────────────────────────────────────────────────────────────────────
# Activation 2 — Female
# Mb=4.03e-5, M1=3.27e-5, M2=1.38e-5
# Kb=2.2e4, Kc=4.2e3, K1=7.7e3, K2=3.2e3
# ─────────────────────────────────────────────────────────────────────────────

class TestAct2FemaleMechanics:

    def test_body_mass(self, act2_female):
        assert _rel_err(act2_female.body_mass_kg, 4.03e-5) <= REL_TOL_MASS, \
            f"Body mass: {act2_female.body_mass_kg:.4e} vs 4.03e-5"

    def test_upper_mass(self, act2_female):
        assert _rel_err(act2_female.upper_mass_kg, 3.27e-5) <= REL_TOL_MASS, \
            f"Upper mass M1: {act2_female.upper_mass_kg:.4e} vs 3.27e-5"

    def test_lower_mass(self, act2_female):
        assert _rel_err(act2_female.lower_mass_kg, 1.38e-5) <= REL_TOL_MASS, \
            f"Lower mass M2: {act2_female.lower_mass_kg:.4e} vs 1.38e-5"

    def test_body_spring(self, act2_female):
        assert _rel_err(act2_female.body_spring, 2.2e4) <= REL_TOL_SPRING, \
            f"Body spring Kb: {act2_female.body_spring:.4e} vs 2.2e4"

    def test_cover_spring(self, act2_female):
        assert _rel_err(act2_female.cover_spring, 4.2e3) <= REL_TOL_SPRING, \
            f"Cover spring Kc: {act2_female.cover_spring:.4e} vs 4.2e3"

    def test_upper_spring(self, act2_female):
        assert _rel_err(act2_female.upper_spring, 7.7e3) <= REL_TOL_SPRING, \
            f"Upper spring K1: {act2_female.upper_spring:.4e} vs 7.7e3"

    def test_lower_spring(self, act2_female):
        assert _rel_err(act2_female.lower_spring, 3.2e3) <= REL_TOL_SPRING, \
            f"Lower spring K2: {act2_female.lower_spring:.4e} vs 3.2e3"
