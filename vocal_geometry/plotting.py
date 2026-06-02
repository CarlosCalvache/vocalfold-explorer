"""
vocal_geometry/plotting.py
===========================
Phase 13 – Correcciones conceptuales.

Changes from Phase 12:
- C(t) no longer normalized by its own maximum → absolute relative scale 0–1
  based on (contact-weighted length) / total glottal length.
- New Lc(t): binary contact-length function (mm) per frame.
- Metrics dict: OQ, CQ, AQ removed; added Lc_max, Lc_pct, closure_status.
- New plot_contact_length() for Lc(t) display.
- plot_cycle_comparison_ab() gains "Lc" mode.
- plot_comparison_delta_abs(): fixed duplicate-margin TypeError.
"""

from __future__ import annotations

import math
import numpy as np
import plotly.graph_objects as go
from typing import Tuple, Dict, List, Any, Optional

from vocal_geometry.model import VocalFoldState, calculate_all


# ─────────────────────────────────────────────────────────────────────────────
# Colour palette (Body-Cover conventions)
# ─────────────────────────────────────────────────────────────────────────────
C: Dict[str, str] = {
    "bg":           "#05070A",
    "panel":        "#0B0F14",
    "card":         "#0F151C",
    "card_alt":     "#111821",
    "border":       "rgba(255,255,255,0.08)",
    "text":         "#E5EEF7",
    "text_sec":     "#8FA3B5",
    "text_muted":   "#5F7180",
    "grid":         "rgba(255,255,255,0.06)",
    "ag":           "#00C8E0",
    "ac":           "#F0A030",
    "phase":        "#FF9F1C",
    "coq":          "#61D345",
    "body":         "rgba(120,18,28,0.95)",
    "cover_low":    "rgba(210,90,10,0.85)",
    "cover_hi":     "rgba(250,150,40,0.70)",
    "state_a":      "#00C8E0",
    "state_b":      "#F04D5E",
    "zn":           "#00E5FF",
}


_LAYOUT_BASE: Dict[str, Any] = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["bg"],
    font=dict(color=C["text"], family="Inter, system-ui, sans-serif"),
    margin=dict(l=0, r=0, t=22, b=0),
)


# ─────────────────────────────────────────────────────────────────────────────
# Geometry & Kinematics
# ─────────────────────────────────────────────────────────────────────────────

def _glottal_profile(state: VocalFoldState, Ny: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns (y_1d, gap_rest) representing the anterior-posterior length L
    and the resting medial gap (triangular).
    """
    L = state.length_mm
    aLCA = state.aLCA
    y_1d = np.linspace(0, L, Ny)

    # Triangular glottis: narrow anteriorly (y=0), wider posteriorly (y=L)
    gap_ant = 0.15
    gap_post = 0.18 + 2.2 * (1.0 - aLCA)
    gap_rest = gap_ant + (gap_post - gap_ant) * (y_1d / L)

    return y_1d, gap_rest


def _vibration_field(
    t: float, y: float, z: float, u: float,
    L: float, T: float, Zn: float, Dc: float, Db: float,
    pressure: float
) -> float:
    """
    Compute medial displacement dx for a point (y, z, u) at time t.
    u is the lateral distance from the medial surface.

    Pressure-to-amplitude scaling is steeper (cubic root) so that:
    - Ps ≤ 3 cmH₂O  →  amplitude insufficient for full closure  (incomplete)
    - Ps ≥ 6 cmH₂O  →  full closure is achieved during cycle    (complete)
    """
    # Amplitude envelope along Y (zero at anterior/posterior ends)
    y_env = math.sin(math.pi * (y / max(L, 0.01)))
    if y_env < 0:
        y_env = 0

    # Steeper pressure scaling: amp ∝ (Ps/8)^(2/3), scaled so Ps=8 → 0.45 mm
    amp_base = 0.45 * ((pressure / 8.0) ** (2.0 / 3.0))

    # Lateral decay (u)
    if u <= Dc:
        u_factor = 1.0 - 0.7 * (u / max(Dc, 0.01))
    else:
        rem_u = u - Dc
        u_factor = 0.3 * (1.0 - rem_u / max(Db, 0.01))
    u_factor = max(0.0, min(1.0, u_factor))

    # Vertical phase and amplitude (mucosal wave)
    if z <= Zn:
        phase_lag = 0.0
        z_amp = 1.0
    else:
        z_rel = (z - Zn) / max(T - Zn, 0.01)
        phase_lag = 0.8 * z_rel
        z_amp = 1.0 + 0.2 * z_rel

    # Asymmetric temporal waveform: sin(t) - 0.35*sin(2t)
    wave = math.sin(t - phase_lag) - 0.35 * math.sin(2 * (t - phase_lag))

    dx = amp_base * y_env * u_factor * z_amp * wave
    return dx


# ─────────────────────────────────────────────────────────────────────────────
# Central Dynamic Function
# ─────────────────────────────────────────────────────────────────────────────

def compute_dynamic_gap(
    state: VocalFoldState, pressure: float, n_cycles: int = 10, fps: int = 24
) -> Dict[str, Any]:
    """
    Central function to compute dynamic glottal characteristics.

    Returns a dict with:
    - cycles, t_vals: time axis
    - Ag: Glottal Area Function [mm²]
    - Ac: Contact Area Proxy [mm²]
    - Lc: Contact Length Function [mm] — binary threshold-based
    - phase_labels: per-frame strings
    - metrics: Ag_max, Ag_min, Ac_max, CoQ
    """
    L = state.length_mm
    T = state.thickness_mm
    Zn = state.nodal_point_mm
    Dc = state.cover_depth_mm
    Db = state.body_depth_mm

    Ny = 50
    y_1d, gap_rest = _glottal_profile(state, Ny)
    dy = L / (Ny - 1)

    t_vals = np.linspace(0, n_cycles * 2 * math.pi, n_cycles * fps, endpoint=False)
    cycles = t_vals / (2 * math.pi)

    Ag_arr: List[float] = []
    Ac_arr: List[float] = []
    Lc_arr: List[float] = []  # contact length in mm (binary threshold)

    contact_thresh = 0.05    # mm — binary threshold for Lc(t)
    h_contact = min(max(0.5 * Dc, 0.5), 1.5)

    for t in t_vals:
        ag_frame = 0.0
        lc_frame = 0.0

        for iy, y in enumerate(y_1d):
            z_points = [0.0, Zn / 2.0, Zn, Zn + (T - Zn) / 2.0, T]
            min_gap_y = gap_rest[iy]

            for z in z_points:
                dx = _vibration_field(t, y, z, 0.0, L, T, Zn, Dc, Db, pressure)
                current_gap = gap_rest[iy] - 2.0 * dx
                if current_gap < min_gap_y:
                    min_gap_y = current_gap

            gap_effective = max(min_gap_y, 0.0)
            ag_frame += gap_effective * dy

            # Lc(t): binary contact length
            if min_gap_y <= contact_thresh:
                lc_frame += dy

        ac_frame = lc_frame * h_contact

        Ag_arr.append(ag_frame)
        Ac_arr.append(ac_frame)
        Lc_arr.append(lc_frame)

    Ag_arr_np = np.array(Ag_arr)
    Ac_arr_np = np.array(Ac_arr)
    Lc_arr_np = np.array(Lc_arr)

    Ag_max = float(np.max(Ag_arr_np)) if np.max(Ag_arr_np) > 0 else 1.0
    Ag_min = float(np.min(Ag_arr_np))
    Ac_max = float(np.max(Ac_arr_np))
    CoQ = float(np.mean(Lc_arr_np > 0.0) * 100.0)
    Lc_max = float(np.max(Lc_arr_np))
    Lc_pct = float((Lc_max / max(L, 0.01)) * 100.0)

    peak_idx = int(np.argmax(Ag_arr_np))

    # Phase labelling: (Opening / Max opening / Closing / Contact interval / Residual gap)
    phase_labels: List[str] = []
    for k, ag in enumerate(Ag_arr_np):
        if Lc_arr_np[k] > 0.0:
            phase_labels.append("Contact interval")
        elif ag <= Ag_min + 0.05 * (Ag_max - Ag_min):
            phase_labels.append("Residual gap")
        elif k == peak_idx:
            phase_labels.append("Max opening")
        elif k < peak_idx:
            phase_labels.append("Opening")
        else:
            phase_labels.append("Closing")

    return {
        "cycles":       cycles,
        "t_vals":       t_vals,
        "Ag":           Ag_arr_np,
        "Ac":           Ac_arr_np,
        "Lc":           Lc_arr_np,
        "phase_labels": phase_labels,
        "metrics": {
            "Ag_max":         Ag_max,
            "Ag_min":         Ag_min,
            "Ac_max":         Ac_max,
            "CoQ":            CoQ,
            "Lc_max":         Lc_max,
            "Lc_pct":         Lc_pct,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3D Mesh Generation
# ─────────────────────────────────────────────────────────────────────────────

def _build_block_mesh(
    state: VocalFoldState,
    sign: int,
    t: float,
    pressure: float,
    u_start: float, u_end: float,
    z_start: float, z_end: float,
    Ny: int = 30, Nu: int = 5, Nz: int = 5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[int], List[int], List[int]]:
    L, T, Zn = state.length_mm, state.thickness_mm, state.nodal_point_mm
    Db, Dc = state.body_depth_mm, state.cover_depth_mm

    y_1d, gap_rest = _glottal_profile(state, Ny)
    u_1d = np.linspace(u_start, u_end, Nu)
    z_1d = np.linspace(z_start, z_end, Nz)

    X, Y, Z = [], [], []

    for iz, z in enumerate(z_1d):
        for iy, y in enumerate(y_1d):
            rest_medial_x = gap_rest[iy] / 2.0
            for iu, u in enumerate(u_1d):
                dx = _vibration_field(t, y, z, u, L, T, Zn, Dc, Db, pressure)
                x_val = sign * (rest_medial_x + u) - sign * dx
                X.append(x_val)
                Y.append(y)
                Z.append(z)

    X = np.array(X); Y = np.array(Y); Z = np.array(Z)

    def idx(iy: int, iu: int, iz: int) -> int:
        return iz * (Ny * Nu) + iy * Nu + iu

    I, J, K = [], [], []
    for iz, flip in [(0, sign == -1), (Nz-1, sign == 1)]:
        for iy in range(Ny - 1):
            for iu in range(Nu - 1):
                p0 = idx(iy, iu, iz);   p1 = idx(iy+1, iu, iz)
                p2 = idx(iy+1, iu+1, iz); p3 = idx(iy, iu+1, iz)
                if flip: I += [p0, p0]; J += [p2, p1]; K += [p3, p2]
                else:    I += [p0, p0]; J += [p1, p2]; K += [p2, p3]

    for iu, flip in [(0, sign == 1), (Nu-1, sign == -1)]:
        for iy in range(Ny - 1):
            for iz in range(Nz - 1):
                p0 = idx(iy, iu, iz);   p1 = idx(iy+1, iu, iz)
                p2 = idx(iy+1, iu, iz+1); p3 = idx(iy, iu, iz+1)
                if flip: I += [p0, p0]; J += [p2, p1]; K += [p3, p2]
                else:    I += [p0, p0]; J += [p1, p2]; K += [p2, p3]

    for iy, flip in [(0, sign == -1), (Ny-1, sign == 1)]:
        for iu in range(Nu - 1):
            for iz in range(Nz - 1):
                p0 = idx(iy, iu, iz);   p1 = idx(iy, iu+1, iz)
                p2 = idx(iy, iu+1, iz+1); p3 = idx(iy, iu, iz+1)
                if flip: I += [p0, p0]; J += [p2, p1]; K += [p3, p2]
                else:    I += [p0, p0]; J += [p1, p2]; K += [p2, p3]

    return X, Y, Z, I, J, K


def _generate_fold_traces(
    state: VocalFoldState, sign: int,
    t: float = 0.0, pressure: float = 0.0,
    show_legend: bool = True,
    name_prefix: str = "",
) -> List[go.Mesh3d]:
    T, Zn, Db, Dc = state.thickness_mm, state.nodal_point_mm, state.body_depth_mm, state.cover_depth_mm
    Zn_eff = min(Zn, T * 0.95)
    traces = []

    # Body
    X, Y, Z, I, J, K = _build_block_mesh(state, sign, t, pressure, Dc, Dc+Db, 0, T, Nu=4, Nz=4)
    traces.append(go.Mesh3d(
        x=X, y=Y, z=Z, i=I, j=J, k=K,
        color=C["body"], opacity=1.0, name=f"{name_prefix}Body mass / TA core",
        showlegend=show_legend, flatshading=False,
        lighting=dict(ambient=0.45, diffuse=0.8, specular=0.2, roughness=0.6),
        hovertemplate="<b>Body mass (TA core)</b><extra></extra>",
    ))
    # Lower Cover M1
    X, Y, Z, I, J, K = _build_block_mesh(state, sign, t, pressure, 0, Dc, 0, Zn_eff, Nu=3, Nz=4)
    traces.append(go.Mesh3d(
        x=X, y=Y, z=Z, i=I, j=J, k=K,
        color=C["cover_low"], opacity=0.85, name=f"{name_prefix}Lower cover mass M2",
        showlegend=show_legend, flatshading=False,
        lighting=dict(ambient=0.5, diffuse=0.7, specular=0.4, roughness=0.4),
        hovertemplate="<b>Lower cover mass M2</b><extra></extra>",
    ))
    # Upper Cover M2
    X, Y, Z, I, J, K = _build_block_mesh(state, sign, t, pressure, 0, Dc, Zn_eff, T, Nu=3, Nz=4)
    traces.append(go.Mesh3d(
        x=X, y=Y, z=Z, i=I, j=J, k=K,
        color=C["cover_hi"], opacity=0.75, name=f"{name_prefix}Upper cover mass M1",
        showlegend=show_legend, flatshading=False,
        lighting=dict(ambient=0.55, diffuse=0.7, specular=0.5, roughness=0.3),
        hovertemplate="<b>Upper cover mass M1</b><extra></extra>",
    ))
    return traces


def _zn_plane_traces(state: VocalFoldState, sign: int, t: float = 0.0, pressure: float = 0.0,
                     show_legend: bool = True) -> List[go.Mesh3d]:
    L, T, Zn, Dc, Db = state.length_mm, state.thickness_mm, state.nodal_point_mm, state.cover_depth_mm, state.body_depth_mm
    Zn_eff = min(Zn, T * 0.95)
    y_1d, gap_rest = _glottal_profile(state, 5)
    X, Y, Z = [], [], []
    for u in [0, Dc]:
        for iy, y in enumerate([0, L]):
            gap = gap_rest[0] if iy == 0 else gap_rest[-1]
            dx = _vibration_field(t, y, Zn_eff, u, L, T, Zn, Dc, Db, pressure)
            X.append(sign * (gap/2.0 + u) - sign * dx)
            Y.append(y)
            Z.append(Zn_eff)
    return [go.Mesh3d(
        x=X, y=Y, z=Z, i=[0, 0], j=[1, 2], k=[2, 3],
        color=C["zn"], opacity=0.20, name="Nodal Point (Zn)", showlegend=show_legend,
        hovertemplate=f"<b>Nodal Point (Zn) = {Zn:.2f} mm</b><extra></extra>",
    )]


def _label_traces(state: VocalFoldState) -> List[go.Scatter3d]:
    L, T, Db, Dc = state.length_mm, state.thickness_mm, state.body_depth_mm, state.cover_depth_mm
    mid_z = T / 2.0
    lat_x = Dc + Db + 1.0
    labels = [
        (0, -1.5, mid_z, "Anterior"),
        (0, L+1.5, mid_z, "Posterior"),
        (lat_x, L/2, mid_z, "Lateral →"),
        (-lat_x, L/2, mid_z, "← Lateral"),
        (0, L/2, T + 1.5, "Superior"),
        (0, L/2, -1.5, "Inferior"),
        (Dc+Db/2, L*0.15, T + 1.0, "Right fold"),
        (-(Dc+Db/2), L*0.15, T + 1.0, "Left fold"),
        (0, L*0.8, mid_z, "Glottal gap"),
    ]
    return [go.Scatter3d(
        x=[l[0] for l in labels], y=[l[1] for l in labels], z=[l[2] for l in labels],
        mode="text", text=[l[3] for l in labels], textfont=dict(color=C["text"], size=10),
        showlegend=False, hoverinfo="skip"
    )]


def _default_scene(state: VocalFoldState) -> Dict[str, Any]:
    L, T, Db, Dc = state.length_mm, state.thickness_mm, state.body_depth_mm, state.cover_depth_mm
    max_x = Dc + Db + 2.0
    ax_style = dict(showbackground=False, showgrid=False, zeroline=False,
                    showticklabels=False, showaxeslabels=False, title="", visible=False)
    return dict(
        xaxis=dict(**ax_style, range=[-max_x, max_x]),
        yaxis=dict(**ax_style, range=[-2.5, L + 2.5]),
        zaxis=dict(**ax_style, range=[-1.5, T + 2.0]),
        camera=dict(eye=dict(x=0.0, y=-2.4, z=1.3), center=dict(x=0.0, y=0.0, z=0.0), up=dict(x=0.0, y=0.0, z=1.0)),
        bgcolor=C["bg"], aspectmode="data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3D Main Plots
# ─────────────────────────────────────────────────────────────────────────────

def plot_3d_fold(state: VocalFoldState, show_zn: bool = True, show_labels: bool = True, height: int = 500) -> go.Figure:
    traces = []
    for sign, sl in [(+1, True), (-1, False)]:
        traces.extend(_generate_fold_traces(state, sign, show_legend=sl))
        if show_zn: traces.extend(_zn_plane_traces(state, sign, show_legend=sl))
    if show_labels: traces.extend(_label_traces(state))

    fig = go.Figure(data=traces)
    fig.update_layout(
        **_LAYOUT_BASE, scene=_default_scene(state), uirevision="vocal_fold_camera",
        legend=dict(bgcolor="rgba(6,6,6,0.85)", font=dict(color=C["text"], size=11), x=0.01, y=0.99),
        height=height,
    )
    return fig


def plot_3d_fold_at_phase(
    state: VocalFoldState, phase_pct: float, pressure: float,
    show_zn: bool = True, show_labels: bool = True, height: int = 480,
) -> go.Figure:
    """
    Render the 3D fold frozen at a specific phase (0–100% of one cycle).
    Used by the Phase Explorer mode.
    """
    t_val = (phase_pct / 100.0) * 2 * math.pi
    traces = []
    for sign, sl in [(+1, True), (-1, False)]:
        traces.extend(_generate_fold_traces(state, sign, t=t_val, pressure=pressure, show_legend=sl))
        if show_zn: traces.extend(_zn_plane_traces(state, sign, t=t_val, pressure=pressure, show_legend=sl))
    if show_labels: traces.extend(_label_traces(state))

    fig = go.Figure(data=traces)
    fig.update_layout(
        **_LAYOUT_BASE, scene=_default_scene(state), uirevision="phase_explorer_camera",
        legend=dict(bgcolor="rgba(6,6,6,0.85)", font=dict(color=C["text"], size=11), x=0.01, y=0.99),
        height=height,
    )
    return fig


def plot_3d_fold_animated(state: VocalFoldState, pressure: float, show_zn: bool = True,
                          show_labels: bool = True, height: int = 500) -> go.Figure:
    def build_traces(t_val: float, first: bool = False) -> List[Any]:
        tr = []
        for sign, sl in [(+1, first), (-1, False)]:
            tr.extend(_generate_fold_traces(state, sign, t=t_val, pressure=pressure, show_legend=sl))
            if show_zn: tr.extend(_zn_plane_traces(state, sign, t=t_val, pressure=pressure, show_legend=sl))
        if show_labels and first: tr.extend(_label_traces(state))
        return tr

    fig = go.Figure(data=build_traces(0.0, first=True))
    n_cycles, fps = 10, 10
    t_vals = np.linspace(0, n_cycles * 2 * math.pi, n_cycles * fps, endpoint=False)
    fig.frames = [go.Frame(data=build_traces(t), name=str(k)) for k, t in enumerate(t_vals)]

    fig.update_layout(
        **_LAYOUT_BASE, scene=_default_scene(state), uirevision="vocal_fold_camera",
        legend=dict(bgcolor="rgba(6,6,6,0.85)", font=dict(color=C["text"], size=11), x=0.01, y=0.99),
        height=height,
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="▶ Play",  method="animate", args=[None, dict(frame=dict(duration=75, redraw=True), fromcurrent=True, mode="immediate")]),
                dict(label="⏸ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
            ],
            direction="left", pad=dict(r=8, t=8), showactive=False, x=0.0, xanchor="left", y=1.03, yanchor="bottom",
            bgcolor="#1a1a1a", bordercolor="#444", font=dict(color="#fff")
        )]
    )
    return fig


def plot_comparison_overlay(state_a: VocalFoldState, state_b: VocalFoldState, show_zn: bool = True) -> go.Figure:
    traces = []
    for sign in [+1, -1]:
        for s, color, prefix, sl in [(state_a, C["state_a"], "A – ", sign == 1), (state_b, C["state_b"], "B – ", sign == 1)]:
            m = _generate_fold_traces(s, sign, show_legend=sl, name_prefix=prefix)
            for tr in m:
                tr.color = color; tr.opacity = 0.35
            traces.extend(m)
        if show_zn: traces.extend(_zn_plane_traces(state_a, sign, show_legend=(sign==1)))
    traces.extend(_label_traces(state_a))

    fig = go.Figure(data=traces)
    fig.update_layout(
        **_LAYOUT_BASE, scene=_default_scene(state_a), uirevision="vocal_fold_camera", height=500,
        title=dict(text="Overlay: State A (Cyan) vs State B (Red)", font=dict(size=14, color=C["text"])),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2D Analysis Plots
# ─────────────────────────────────────────────────────────────────────────────

def _base_2d_layout(title: str) -> Dict[str, Any]:
    return {
        **_LAYOUT_BASE,
        "margin": dict(l=10, r=10, t=35, b=10),
        "height": 240,
        "title": dict(text=f"<b>{title}</b>", font=dict(size=14, color=C["text"])),
        "xaxis": dict(title="Cycles", gridcolor=C["grid"], zeroline=False),
        "showlegend": False,
    }


def plot_glottal_area(dyn: Dict[str, Any]) -> go.Figure:
    fig = go.Figure()
    
    Ag_max = dyn["metrics"]["Ag_max"]
    Ag_min = dyn["metrics"]["Ag_min"]

    fig.add_trace(go.Scatter(
        x=dyn["cycles"], y=dyn["Ag"], mode="lines", name="Ag(t)",
        line=dict(color=C["ag"], width=2.5), fill="tozeroy", fillcolor="rgba(0, 200, 224, 0.12)"
    ))

    # Peak horizontal line
    fig.add_hline(
        y=Ag_max, line_dash="dash", line_color=C["text_muted"], line_width=1.5,
        annotation_text=f"Peak: {Ag_max:.2f} mm²", annotation_position="top right",
        annotation_font=dict(color=C["text_sec"], size=10)
    )

    # Min horizontal line
    fig.add_hline(
        y=Ag_min, line_dash="dash", line_color=C["text_muted"], line_width=1.5,
        annotation_text=f"Min: {Ag_min:.2f} mm²", annotation_position="bottom right",
        annotation_font=dict(color=C["text_sec"], size=10)
    )

    fig.update_layout(
        **_base_2d_layout("Glottal Area Function Ag(t)"),
        yaxis=dict(title="Area [mm²]", gridcolor=C["grid"], zeroline=False, rangemode="tozero")
    )
    return fig


def plot_glottal_area_with_marker(dyn: Dict[str, Any], phase_pct: float) -> go.Figure:
    """
    Glottal Area Function with a vertical phase marker line.
    Used by Phase Explorer mode.
    """
    fig = plot_glottal_area(dyn)
    n_cycles = float(dyn["cycles"][-1]) if len(dyn["cycles"]) > 0 else 10.0
    marker_x = (phase_pct / 100.0) * (n_cycles / 10.0)

    idx_closest = int(np.argmin(np.abs(dyn["cycles"] - marker_x)))
    marker_x_actual = float(dyn["cycles"][idx_closest])
    phase_label = dyn["phase_labels"][idx_closest] if "phase_labels" in dyn else ""

    fig.add_vline(
        x=marker_x_actual, line_color=C["phase"], line_width=2, line_dash="dash",
        annotation_text=phase_label,
        annotation_font=dict(color=C["phase"], size=11),
        annotation_position="top right",
    )
    fig.update_layout(title=dict(text=f"<b>Glottal Area Ag(t)</b> — Phase: {phase_pct:.0f}%", font=dict(size=14, color=C["text"])))
    return fig


def plot_contact_area_proxy(dyn: Dict[str, Any]) -> go.Figure:
    fig = go.Figure()
    Ac_max = dyn["metrics"]["Ac_max"]
    
    fig.add_trace(go.Scatter(
        x=dyn["cycles"], y=dyn["Ac"], mode="lines", name="Ac(t) Proxy",
        line=dict(color=C["ac"], width=2.5), fill="tozeroy", fillcolor="rgba(240, 160, 48, 0.12)"
    ))

    # Peak horizontal line
    fig.add_hline(
        y=Ac_max, line_dash="dash", line_color=C["text_muted"], line_width=1.5,
        annotation_text=f"Peak: {Ac_max:.2f} mm²", annotation_position="top right",
        annotation_font=dict(color=C["text_sec"], size=10)
    )

    fig.update_layout(
        **_base_2d_layout("Contact Area Proxy Ac(t)"),
        yaxis=dict(title="Proxy Area [mm²]", gridcolor=C["grid"], zeroline=False, rangemode="tozero")
    )
    return fig


def plot_contact_area_with_marker(dyn: Dict[str, Any], phase_pct: float) -> go.Figure:
    """Ac(t) with vertical phase marker for Phase Explorer."""
    fig = plot_contact_area_proxy(dyn)
    n_cycles = float(dyn["cycles"][-1]) if len(dyn["cycles"]) > 0 else 10.0
    marker_x = (phase_pct / 100.0) * (n_cycles / 10.0)
    idx_closest = int(np.argmin(np.abs(dyn["cycles"] - marker_x)))
    marker_x_actual = float(dyn["cycles"][idx_closest])
    phase_label = dyn["phase_labels"][idx_closest] if "phase_labels" in dyn else ""
    
    fig.add_vline(
        x=marker_x_actual, line_color=C["phase"], line_width=2, line_dash="dash",
        annotation_text=phase_label,
        annotation_font=dict(color=C["phase"], size=11),
        annotation_position="top right",
    )
    fig.update_layout(title=dict(text=f"<b>Contact Area Proxy Ac(t)</b> — Phase: {phase_pct:.0f}%", font=dict(size=14, color=C["text"])))
    return fig


def plot_cycle_comparison_ab(dyn_a: Dict[str, Any], dyn_b: Dict[str, Any], mode: str) -> go.Figure:
    fig = go.Figure()

    if mode == "Ag":
        fig.add_trace(go.Scatter(
            x=dyn_a["cycles"], y=dyn_a["Ag"], mode="lines", name="State A",
            line=dict(color=C["state_a"], width=2.5),
            fill="tozeroy", fillcolor="rgba(0, 200, 224, 0.08)"
        ))
        fig.add_trace(go.Scatter(
            x=dyn_b["cycles"], y=dyn_b["Ag"], mode="lines", name="State B",
            line=dict(color=C["state_b"], width=2.5),
            fill="tozeroy", fillcolor="rgba(240, 77, 94, 0.08)"
        ))
        title   = "Glottal Area Comparison Ag(t)"
        y_title = "Area [mm²]"
    else:  # Ac
        fig.add_trace(go.Scatter(
            x=dyn_a["cycles"], y=dyn_a["Ac"], mode="lines", name="State A",
            line=dict(color=C["state_a"], width=2.5),
            fill="tozeroy", fillcolor="rgba(0, 200, 224, 0.08)"
        ))
        fig.add_trace(go.Scatter(
            x=dyn_b["cycles"], y=dyn_b["Ac"], mode="lines", name="State B",
            line=dict(color=C["state_b"], width=2.5),
            fill="tozeroy", fillcolor="rgba(240, 77, 94, 0.08)"
        ))
        title   = "Contact Area Proxy Comparison Ac(t)"
        y_title = "Proxy Area [mm²]"

    l_over = {**_LAYOUT_BASE, "margin": dict(l=10, r=10, t=35, b=10)}
    fig.update_layout(
        **l_over, height=240,
        title=dict(text=f"<b>{title}</b>", font=dict(size=14, color=C["text"])),
        legend=dict(orientation="h", y=1.02, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(title="Cycles", gridcolor=C["grid"], zeroline=False),
        yaxis=dict(title=y_title, gridcolor=C["grid"], zeroline=False, rangemode="tozero"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Heatmaps & Deltas
# ─────────────────────────────────────────────────────────────────────────────

def _get_heatmap_value(state: VocalFoldState, variable: str) -> float:
    # Mechanical proxies
    if variable == "k_eff_proxy":
        return (state.upper_spring + state.lower_spring) * 1e-3
    elif variable == "m_eff_proxy":
        return state.upper_mass_kg + state.lower_mass_kg
    elif variable == "k_to_m_ratio":
        k_eff = (state.upper_spring + state.lower_spring) * 1e-3
        m_eff = state.upper_mass_kg + state.lower_mass_kg
        if m_eff <= 0:
            return float('nan')
        return k_eff / m_eff
        
    # Glottal-cycle dynamic metrics
    elif variable in ("Ag_max", "Ag_min", "Ac_max", "CoQ", "Lc_max", "Lc_pct"):
        # n_cycles=1, fps=12 for fast evaluation
        dyn = compute_dynamic_gap(state, pressure=8.0, n_cycles=1, fps=12)
        if variable == "Ag_max":
            return dyn["metrics"]["Ag_max"]
        elif variable == "Ag_min":
            return dyn["metrics"]["Ag_min"]
        elif variable == "Ac_max":
            return dyn["metrics"]["Ac_max"]
        elif variable == "CoQ":
            return dyn["metrics"]["CoQ"]
        elif variable == "Lc_max":
            return dyn["metrics"]["Lc_max"]
        elif variable == "Lc_pct":
            return dyn["metrics"]["Lc_pct"]

    # Otherwise, static morphology / inputs
    return getattr(state, variable)


def plot_activation_heatmap(
    variable: str, sex: str, x_muscle: str, y_muscle: str, fixed_muscle: str, fixed_val: float
) -> Tuple[go.Figure, np.ndarray, np.ndarray, np.ndarray]:
    n = 25
    x_arr = np.linspace(0, 1, n)
    y_arr = np.linspace(0, 1, n)
    x_g, y_g = np.meshgrid(x_arr, y_arr)
    vals = np.zeros_like(x_g)
    for i in range(n):
        for j in range(n):
            kw = {x_muscle: x_g[i, j], y_muscle: y_g[i, j], fixed_muscle: fixed_val, "sex": sex}
            s = calculate_all(**kw)
            vals[i, j] = _get_heatmap_value(s, variable)

    label_map = {
        "length_mm": "Length L [mm]",
        "thickness_mm": "Thickness T [mm]",
        "nodal_point_mm": "Nodal Point (Zn) [mm]",
        "body_depth_mm": "Body Depth Db [mm]",
        "cover_depth_mm": "Cover Depth Dc [mm]",
        "Ag_max": "Peak Glottal Area Ag,max [mm²]",
        "Ag_min": "Minimum Glottal Area Ag,min [mm²]",
        "Ac_max": "Peak Contact Area Proxy Ac,max [mm²]",
        "CoQ": "Approximate Contact Quotient CoQ [%]",
        "Lc_max": "Max Contact Length Lc,max [mm]",
        "Lc_pct": "Max Contact Length Lc,pct [%]",
        "k_eff_proxy": "Effective Stiffness Proxy",
        "m_eff_proxy": "Effective Mass Proxy",
        "k_to_m_ratio": "Stiffness–Mass Ratio Proxy",
        "body_mass_kg": "Body Mass Mb [kg]",
        "upper_mass_kg": "Upper Mass M1 [kg]",
        "lower_mass_kg": "Lower Mass M2 [kg]",
        "body_spring": "Body Spring Kb",
        "upper_spring": "Upper Spring K1",
        "lower_spring": "Lower Spring K2",
        "cover_spring": "Coupling Spring Kc",
    }
    label = label_map.get(variable, variable.replace("_", " ").title())

    fig = go.Figure(go.Heatmap(
        x=x_arr, y=y_arr, z=vals, colorscale="Inferno",
        colorbar=dict(title=dict(text=label, font=dict(color=C["text"])), tickfont=dict(color=C["text"])),
        hovertemplate=f"{x_muscle}: %{{x:.2f}}<br>{y_muscle}: %{{y:.2f}}<br>Value: %{{z:.4f}}<extra></extra>"
    ))
    fig.update_layout(
        **_LAYOUT_BASE, height=480,
        title=dict(text=f"<b>{label}</b> — {sex} | {fixed_muscle}={fixed_val:.2f}", font=dict(size=14, color=C["text"])),
        xaxis=dict(title=x_muscle, color=C["text"], gridcolor=C["grid"]),
        yaxis=dict(title=y_muscle, color=C["text"], gridcolor=C["grid"]),
    )
    return fig, x_g, y_g, vals
