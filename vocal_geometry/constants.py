"""
vocal_geometry/constants.py
============================
All constants used in the Vocal Geometry low-dimensional body-cover model.

Sources:
  - Titze, I. R., & Story, B. H. (2002). Rules for controlling low-dimensional
    vocal fold models with muscle activation. JASA, 112(3), 1064–1076.
  - Story, B. H., & Titze, I. R. (1995). Voice simulation with a body-cover
    model of the vocal folds. JASA, 97(2), 1249–1260.
  - Verified against MATLAB App Designer source (Calcular function).

Units:
  - Lengths: mm
  - Stresses / elastic moduli: Pa
  - Density: kg/mm³
  - Springs (output): Pa·mm  (not N/m)
  - Masses (output): kg
"""

from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────────────────────
# Geometric rule constants (dimensionless)
# ──────────────────────────────────────────────────────────────────────────────

G: float = 0.2  # Elongation gain constant  []
R: float = 3.0  # CT-to-TA ratio constant   []
H: float = 0.2  # LCA elongation influence  []

# ──────────────────────────────────────────────────────────────────────────────
# Mechanical / tissue constants
# ──────────────────────────────────────────────────────────────────────────────

TISSUE_DENSITY: float = 1040e-9   # kg/mm³  (≈ 1040 kg/m³)

# Shear moduli
MU_BODY: float  = 1000.0   # Pa  —  body layer shear modulus  (Miub)
MU_COVER: float = 500.0    # Pa  —  cover layer shear modulus (Miuc)

# Passive stress function parameters (piecewise)
E1: float  = -0.5     # First transition elongation (compression limit) []
E2: float  = -0.05    # Second transition elongation                    []
SIGMA0: float = 1000.0   # Pa  —  passive stress scale (O0)
SIGMA2: float = 1500.0   # Pa  —  passive stress scale (O2)
C_EXP: float  = 6.5      # Exponential shaping constant (C)             []

# Active (muscle) stress parameters
SIGMA_AM: float = 105000.0  # Pa  —  maximum muscle active stress (Oam)
EPSILON_M: float = 0.4      # Optimal elongation for muscle stress (em)  []
B_FACTOR: float  = 1.07     # Muscle stress Gaussian width factor (b)    []

# Layer-specific elastic stresses (rest state)
SIGMA_LIG: float = 400.0   # Pa  —  ligament stress (Olig)
SIGMA_MUC: float = 500.0   # Pa  —  mucosa stress (Omuc)

# ──────────────────────────────────────────────────────────────────────────────
# Sex-specific anatomical parameters (rest-state geometry)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SexParams:
    """Rest-state geometric parameters for a given sex."""
    sex:   str
    L0:    float   # mm  —  rest length
    T0:    float   # mm  —  rest thickness (width)
    Dmuc:  float   # mm  —  mucosa depth
    Dlig:  float   # mm  —  ligament depth
    Dmus:  float   # mm  —  muscle depth


MALE = SexParams(
    sex  = "Male",
    L0   = 16.0,   # mm
    T0   = 3.0,    # mm
    Dmuc = 2.0,    # mm
    Dlig = 2.0,    # mm
    Dmus = 4.0,    # mm
)

FEMALE = SexParams(
    sex  = "Female",
    L0   = 10.0,   # mm
    T0   = 2.0,    # mm
    Dmuc = 1.5,    # mm
    Dlig = 1.5,    # mm
    Dmus = 3.0,    # mm
)

SEX_PARAMS: dict[str, SexParams] = {
    "Male":   MALE,
    "Female": FEMALE,
}

# ──────────────────────────────────────────────────────────────────────────────
# Convenience: muscle activation labels
# ──────────────────────────────────────────────────────────────────────────────

MUSCLE_LABELS = {
    "aCT":  "Cricothyroid (CT)",
    "aTA":  "Thyroarytenoid (TA)",
    "aLCA": "Lateral Cricoarytenoid (LCA)",
}

# Activation range
ACTIVATION_MIN: float = 0.0
ACTIVATION_MAX: float = 1.0
