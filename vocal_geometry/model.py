"""
vocal_geometry/model.py
========================
Pure mathematical functions implementing the body-cover vocal fold model.

All equations verified against:
  1. MATLAB App Designer source code (Calcular function).
  2. Reference values in Tables 5 and 6 of the original manuscript.

Key implementation notes
------------------------
* Elongation formula: ``ε = G·(R·aCT − aTA) − H·aLCA``
  (NOT G·R·(aCT − aTA) − H·aLCA — the G and R do not factor through aTA).

* Nodal point formula: ``Zn = (1 + aTA)^(T/3)``
  (exponentiation, not multiplication; verified against Table 5).

* Passive stress for ε > e2 involves ``ε^(C·(ε−e2))``.
  When ε is slightly negative (−0.05 < ε < 0), MATLAB computes a complex
  result. We take the **real part**, which reproduces Table 6 exactly.
  Helper: ``_real_power(base, exp)``.

* The muscle stress factor ``0.1 − b·(ε − em)²`` is NOT clamped to zero.
  In MATLAB, ``max(scalar)`` returns the scalar unchanged. Allowing negative
  values is physically meaningful (compression) and reproduces Table 6.

Units: lengths in mm, stresses in Pa, masses in kg, springs in Pa·mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from vocal_geometry.constants import (
    G, R, H,
    TISSUE_DENSITY,
    MU_BODY, MU_COVER,
    E1, E2, SIGMA0, SIGMA2, C_EXP,
    SIGMA_AM, EPSILON_M, B_FACTOR,
    SIGMA_LIG, SIGMA_MUC,
    SEX_PARAMS, SexParams,
)

Sex = Literal["Male", "Female"]


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _real_power(base: float, exp: float) -> float:
    """
    Compute base**exp, returning only the **real part** of the result.

    When base < 0 and exp is non-integer, the result is mathematically
    complex: base**exp = |base|**exp · exp(i·π·exp).
    MATLAB's arithmetic propagates this complex value, but the downstream
    display (num2str) and text conversion effectively use the real component.
    Taking the real part here reproduces the MATLAB numerical results
    faithfully (verified against Table 6 of the manuscript).

    For base ≥ 0, this returns the standard real-valued power.
    """
    if base >= 0:
        return base ** exp
    # base < 0: real part of the complex power
    return (abs(base) ** exp) * math.cos(math.pi * exp)


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VocalFoldState:
    """
    Complete output of the body-cover vocal fold model for a given
    muscle activation and sex.

    Geometry outputs (Table 5)
    --------------------------
    epsilon        : Longitudinal strain (elongation, dimensionless)
    length_mm      : Fold length  L  [mm]
    thickness_mm   : Fold thickness (width) T  [mm]
    nodal_point_mm : Nodal point position Zn  [mm]
    body_depth_mm  : Body layer depth Db  [mm]
    cover_depth_mm : Cover layer depth Dc  [mm]

    Mechanical outputs (Table 6)
    ----------------------------
    body_mass_kg   : Body mass Mb  [kg]
    upper_mass_kg  : Upper cover mass M1  [kg]
    lower_mass_kg  : Lower cover mass M2  [kg]
    body_spring    : Body spring Kb  [Pa·mm]
    cover_spring   : Cover spring Kc  [Pa·mm]
    upper_spring   : Upper cover spring K1  [Pa·mm]
    lower_spring   : Lower cover spring K2  [Pa·mm]

    Inputs (stored for reference)
    -----------------------------
    aCT, aTA, aLCA : muscle activations [0, 1]
    sex            : "Male" or "Female"
    """
    # Inputs
    aCT: float
    aTA: float
    aLCA: float
    sex: str

    # Geometry
    epsilon: float
    length_mm: float
    thickness_mm: float
    nodal_point_mm: float
    body_depth_mm: float
    cover_depth_mm: float

    # Mechanics
    body_mass_kg: float
    upper_mass_kg: float
    lower_mass_kg: float
    body_spring: float
    cover_spring: float
    upper_spring: float
    lower_spring: float

    # Intermediate stresses (for transparency)
    passive_stress_pa: float
    muscle_stress_pa: float
    body_stress_pa: float
    cover_stress_pa: float


# ─────────────────────────────────────────────────────────────────────────────
# Individual calculation functions
# ─────────────────────────────────────────────────────────────────────────────

def calculate_elongation(aCT: float, aTA: float, aLCA: float) -> float:
    """
    Longitudinal strain (elongation) ε.

    Rule (Table 3, Titze 2002):
        ε = G·(R·aCT − aTA) − H·aLCA

    Parameters
    ----------
    aCT  : Cricothyroid muscle activation  [0, 1]
    aTA  : Thyroarytenoid activation       [0, 1]
    aLCA : Lat. cricoarytenoid activation  [0, 1]

    Returns
    -------
    epsilon : float  (dimensionless)

    Notes
    -----
    G·R·aCT lengthens the fold; G·aTA and H·aLCA shorten it.
    Negative ε means the fold is shorter / compressed relative to rest.
    """
    return G * (R * aCT - aTA) - H * aLCA


def calculate_length(epsilon: float, params: SexParams) -> float:
    """
    Vocal fold length L [mm].

    Rule:  L = L₀·(1 + ε)

    Parameters
    ----------
    epsilon : longitudinal strain (from calculate_elongation)
    params  : sex-specific anatomical parameters

    Returns
    -------
    length : float  [mm]
    """
    return params.L0 * (1.0 + epsilon)


def calculate_thickness(epsilon: float, params: SexParams) -> float:
    """
    Vocal fold thickness (width) T [mm].

    Rule:  T = T₀ / (1 + 0.8·ε)

    Elongation reduces thickness (conservation of tissue volume approximation).

    Parameters
    ----------
    epsilon : longitudinal strain
    params  : sex-specific anatomical parameters

    Returns
    -------
    thickness : float  [mm]
    """
    return params.T0 / (1.0 + 0.8 * epsilon)


def calculate_nodal_point(T: float, aTA: float) -> float:
    """
    Nodal point position Zn [mm].

    Rule:  Zn = (1 + aTA)^(T / 3)

    The nodal point divides the cover layer into upper (M1) and lower (M2)
    masses. It rises with increasing TA activation and increases with
    fold thickness.

    Parameters
    ----------
    T   : vocal fold thickness [mm]  (from calculate_thickness)
    aTA : thyroarytenoid activation [0, 1]

    Returns
    -------
    Zn : float  [mm]

    Notes
    -----
    This is an **exponentiation**, not multiplication. The exponent T/3
    depends on the current (strained) thickness, not the rest thickness.
    Validated against Table 5 (e.g., Act1 Male: Zn ≈ 1.62 mm).
    """
    return (1.0 + aTA) ** (T / 3.0)


def calculate_body_depth(epsilon: float, aTA: float, params: SexParams) -> float:
    """
    Body layer depth Db [mm].

    Rule:  Db = (aTA·Dmus + 0.5·Dlig) / (1 + 0.2·ε)

    Increasing TA activation swells the thyroarytenoid, deepening the body.
    Elongation compresses the depth slightly.

    Parameters
    ----------
    epsilon : longitudinal strain
    aTA     : thyroarytenoid activation [0, 1]
    params  : sex-specific anatomical parameters

    Returns
    -------
    Db : float  [mm]
    """
    return (aTA * params.Dmus + 0.5 * params.Dlig) / (1.0 + 0.2 * epsilon)


def calculate_cover_depth(epsilon: float, params: SexParams) -> float:
    """
    Cover layer depth Dc [mm].

    Rule:  Dc = (Dmuc + 0.5·Dlig) / (1 + 0.2·ε)

    The cover depth is independent of TA activation — it depends only on
    the mucosa and half the ligament depth, modulated by elongation.

    Parameters
    ----------
    epsilon : longitudinal strain
    params  : sex-specific anatomical parameters

    Returns
    -------
    Dc : float  [mm]
    """
    return (params.Dmuc + 0.5 * params.Dlig) / (1.0 + 0.2 * epsilon)


def calculate_masses(
    L: float, T: float, Db: float, Dc: float, Zn: float
) -> tuple[float, float, float]:
    """
    Vocal fold masses [kg].

    Rules (Table 4, Titze 2002):
        Mb = ρ·L·T·Db                    (body mass)
        M1 = ρ·L·T·Dc·(Zn/T) = ρ·L·Dc·Zn  (upper cover mass)
        M2 = ρ·L·T·Dc·(1 − Zn/T)           (lower cover mass)

    Parameters
    ----------
    L  : fold length [mm]
    T  : fold thickness [mm]
    Db : body depth [mm]
    Dc : cover depth [mm]
    Zn : nodal point position [mm]

    Returns
    -------
    (Mb, M1, M2) : tuple of floats  [kg]

    Notes
    -----
    TISSUE_DENSITY is 1040e-9 kg/mm³.
    The T cancels in M1 and M2 (ρ·L·T·Dc·Zn/T = ρ·L·Dc·Zn), but the
    formula is kept in its original MATLAB form for traceability.
    """
    rho = TISSUE_DENSITY
    Mb = rho * L * T * Db
    M1 = rho * L * T * Dc * (Zn / T)   # = rho*L*Dc*Zn
    M2 = rho * L * T * Dc * (1.0 - Zn / T)
    return Mb, M1, M2


def calculate_passive_stress(epsilon: float) -> float:
    """
    Passive tissue stress σ_p [Pa] as a piecewise function of elongation.

    Piecewise rules (Story & Titze 1995):
      ε < e1:               σ_p = 0
      e1 ≤ ε ≤ e2:         σ_p = −(σ0/e1)·(ε − e1)           [linear]
      ε > e2:               σ_p = −(σ0/e1)·(ε − e1)
                                 + σ2·(ε^(C·(ε−e2)) − C·(ε−e2) − 1)  [nonlinear]

    Parameters
    ----------
    epsilon : longitudinal strain (dimensionless)

    Returns
    -------
    sigma_p : float  [Pa]

    Notes
    -----
    The nonlinear branch uses ``ε^(C·(ε−e2))``. When ε is slightly negative
    (e2 < ε < 0), MATLAB produces a complex result. We take the real part
    using ``_real_power()``, which reproduces the MATLAB output and matches
    Table 6 spring values. See module docstring for details.
    """
    if epsilon < E1:
        return 0.0

    linear_term = -(SIGMA0 / E1) * (epsilon - E1)

    if epsilon <= E2:
        return linear_term

    # Nonlinear branch (epsilon > E2)
    u = C_EXP * (epsilon - E2)                       # exponent
    power_term = _real_power(epsilon, u)              # ε^u  (real part)
    nonlinear = SIGMA2 * (power_term - u - 1.0)
    return linear_term + nonlinear


def calculate_muscle_stress(aTA: float, epsilon: float) -> float:
    """
    Thyroarytenoid active muscle stress σ_mus [Pa].

    Rule:  σ_mus = aTA · σ_am · (0.1 − b·(ε − em)²)  +  σ_p(ε)

    The factor ``0.1 − b·(ε − em)²`` is a Gaussian-like curve peaked at
    ε = em (optimal elongation). It can be negative for large deviations
    from em (no clamping — matches MATLAB ``max(scalar) = scalar`` behavior).

    Parameters
    ----------
    aTA     : thyroarytenoid activation [0, 1]
    epsilon : longitudinal strain

    Returns
    -------
    sigma_mus : float  [Pa]
    """
    Op = calculate_passive_stress(epsilon)
    active_factor = 0.1 - B_FACTOR * (epsilon - EPSILON_M) ** 2
    return aTA * SIGMA_AM * active_factor + Op


def calculate_body_cover_stress(
    aTA: float, epsilon: float, params: SexParams, Db: float, Dc: float
) -> tuple[float, float]:
    """
    Effective body (σ_b) and cover (σ_c) stresses [Pa].

    Rules (Table 4, Titze 2002):
        σ_b = (0.5·σ_lig·Dlig + σ_mus·Dmus) / Db
        σ_c = (0.5·σ_lig·Dlig + σ_muc·Dmuc) / Dc

    Parameters
    ----------
    aTA     : thyroarytenoid activation [0, 1]
    epsilon : longitudinal strain
    params  : sex-specific anatomical parameters
    Db      : body depth [mm]
    Dc      : cover depth [mm]

    Returns
    -------
    (sigma_b, sigma_c) : tuple of floats  [Pa]
    """
    Omus = calculate_muscle_stress(aTA, epsilon)
    sigma_b = (0.5 * SIGMA_LIG * params.Dlig + Omus * params.Dmus) / Db
    sigma_c = (0.5 * SIGMA_LIG * params.Dlig + SIGMA_MUC * params.Dmuc) / Dc
    return sigma_b, sigma_c


def calculate_springs(
    L: float,
    T: float,
    Db: float,
    Dc: float,
    Zn: float,
    sigma_b: float,
    sigma_c: float,
) -> tuple[float, float, float, float]:
    """
    Body and cover spring constants [Pa·mm].

    Rules (Table 4, Titze 2002 / Story & Titze 1995):

        Kb = 2·μb·L·T/Db  +  π²·σb·(Db/L)·T
        Kc = [(0.5·μc·L·Dc/T)·(1/3 − ζ·(1−ζ))⁻¹ − 2·μc·L·T/Dc] · ζ·(1−ζ)
        K1 = 2·μc·(L·T/Dc)·ζ         +  π²·σc·(Dc/L)·Zn
        K2 = 2·μc·(L·T/Dc)·(1−ζ)    +  π²·σc·(Dc/L)·T·(1−ζ)

    where ζ = Zn/T.

    Parameters
    ----------
    L       : fold length [mm]
    T       : fold thickness [mm]
    Db      : body depth [mm]
    Dc      : cover depth [mm]
    Zn      : nodal point position [mm]
    sigma_b : body effective stress [Pa]
    sigma_c : cover effective stress [Pa]

    Returns
    -------
    (Kb, Kc, K1, K2) : tuple of floats  [Pa·mm]
    """
    zeta = Zn / T   # normalized nodal point position (dimensionless)

    # Body spring (Kb)
    Kb = (2.0 * MU_BODY * L * T / Db) + (math.pi ** 2 * sigma_b * (Db / L) * T)

    # Cover coupling spring (Kc)
    coupling_denom = (1.0 / 3.0) - zeta * (1.0 - zeta)
    Kc = (
        (0.5 * MU_COVER * L * Dc / T) * (1.0 / coupling_denom)
        - 2.0 * MU_COVER * L * T / Dc
    ) * zeta * (1.0 - zeta)

    # Upper cover spring (K1)
    K1 = (
        2.0 * MU_COVER * (L * T / Dc) * zeta
        + math.pi ** 2 * sigma_c * (Dc / L) * Zn
    )

    # Lower cover spring (K2)
    K2 = (
        2.0 * MU_COVER * (L * T / Dc) * (1.0 - zeta)
        + math.pi ** 2 * sigma_c * (Dc / L) * T * (1.0 - zeta)
    )

    return Kb, Kc, K1, K2


# ─────────────────────────────────────────────────────────────────────────────
# Master function
# ─────────────────────────────────────────────────────────────────────────────

def calculate_all(
    aCT: float,
    aTA: float,
    aLCA: float,
    sex: Sex = "Male",
) -> VocalFoldState:
    """
    Compute the complete vocal fold state for given muscle activations.

    This is the primary entry point. Calls all sub-functions in order and
    returns a ``VocalFoldState`` dataclass containing all geometry and
    mechanical parameters.

    Parameters
    ----------
    aCT  : Cricothyroid activation  [0, 1]
    aTA  : Thyroarytenoid activation [0, 1]
    aLCA : Lat. cricoarytenoid activation [0, 1]
    sex  : "Male" or "Female"

    Returns
    -------
    VocalFoldState

    Example
    -------
    >>> from vocal_geometry.model import calculate_all
    >>> s = calculate_all(aCT=0.3, aTA=0.6, aLCA=0.5, sex="Male")
    >>> round(s.length_mm, 2)
    15.36
    >>> round(s.thickness_mm, 2)
    3.09
    """
    params = SEX_PARAMS[sex]

    # ── Geometry ──────────────────────────────────────────────────────────────
    eps = calculate_elongation(aCT, aTA, aLCA)
    L   = calculate_length(eps, params)
    T   = calculate_thickness(eps, params)
    Zn  = calculate_nodal_point(T, aTA)
    Db  = calculate_body_depth(eps, aTA, params)
    Dc  = calculate_cover_depth(eps, params)

    # ── Masses ────────────────────────────────────────────────────────────────
    Mb, M1, M2 = calculate_masses(L, T, Db, Dc, Zn)

    # ── Stresses ──────────────────────────────────────────────────────────────
    Op   = calculate_passive_stress(eps)
    Omus = calculate_muscle_stress(aTA, eps)
    Ob, Oc = calculate_body_cover_stress(aTA, eps, params, Db, Dc)

    # ── Springs ───────────────────────────────────────────────────────────────
    Kb, Kc, K1, K2 = calculate_springs(L, T, Db, Dc, Zn, Ob, Oc)

    return VocalFoldState(
        # Inputs
        aCT=aCT, aTA=aTA, aLCA=aLCA, sex=sex,
        # Geometry
        epsilon=eps,
        length_mm=L,
        thickness_mm=T,
        nodal_point_mm=Zn,
        body_depth_mm=Db,
        cover_depth_mm=Dc,
        # Mechanics
        body_mass_kg=Mb,
        upper_mass_kg=M1,
        lower_mass_kg=M2,
        body_spring=Kb,
        cover_spring=Kc,
        upper_spring=K1,
        lower_spring=K2,
        # Intermediate stresses (transparency)
        passive_stress_pa=Op,
        muscle_stress_pa=Omus,
        body_stress_pa=Ob,
        cover_stress_pa=Oc,
    )
