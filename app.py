"""
app.py
======
VocalFold Explorer — Phase 14.
Complete visual and structural redesign. Consistent dark med-tech aesthetic,
semantically correct metrics, and LaTeX-rich documentation.
"""

import streamlit as st
import pandas as pd
import numpy as np

from vocal_geometry.model import calculate_all
from vocal_geometry.plotting import (
    plot_3d_fold,
    plot_3d_fold_animated,
    plot_3d_fold_at_phase,
    plot_comparison_overlay,
    plot_activation_heatmap,
    compute_dynamic_gap,
    plot_glottal_area,
    plot_glottal_area_with_marker,
    plot_contact_area_proxy,
    plot_contact_area_with_marker,
    plot_cycle_comparison_ab,
    C,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config & CSS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VocalFold Explorer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root {
  --bg-main: #05070A;
  --bg-panel: #0B0F14;
  --bg-card: #0F151C;
  --bg-card-alt: #111821;
  --border: rgba(255,255,255,0.08);
  --text-main: #E5EEF7;
  --text-sec: #8FA3B5;
  --text-muted: #5F7180;
  
  --accent-ag: #00C8E0;
  --accent-ac: #F0A030;
  --accent-coq: #61D345;
  --accent-phase: #FF9F1C;
}

[data-testid="stHeader"]    { display: none !important; }
[data-testid="stToolbar"]   { display: none !important; }
[data-testid="stDecoration"]{ display: none !important; }
#MainMenu                   { display: none !important; }
footer                      { display: none !important; }

.block-container { padding-top: 1.2rem !important; padding-bottom: 0.5rem !important; max-width: 100% !important; }
.stApp { background-color: var(--bg-main) !important; }
body, .stMarkdown, .stText, p, li, label, span { color: var(--text-main) !important; }
[data-testid="stSidebar"] { background-color: var(--bg-panel) !important; border-right: 1px solid var(--border); }

/* Tabs styling */
.stTabs [role="tablist"] { background-color: var(--bg-panel); border-bottom: 1px solid var(--border); gap: 2px; }
.stTabs [role="tab"] { color: var(--text-sec) !important; background: transparent !important; border-radius: 4px 4px 0 0; padding: 6px 18px; font-size: 0.88rem; border: none !important; }
.stTabs [role="tab"][aria-selected="true"] { color: var(--accent-ag) !important; background: var(--bg-card) !important; border-bottom: 2px solid var(--accent-ag) !important; }

/* Widgets controls styling */
div[data-baseweb="select"] > div { background-color: var(--bg-card) !important; color: var(--text-main) !important; border-color: var(--border) !important; }
div[data-baseweb="select"] svg { fill: var(--text-sec) !important; }
div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"] { background-color: var(--bg-panel) !important; border: 1px solid var(--border) !important; color: var(--text-main) !important; }
li[role="option"], div[role="option"] { color: var(--text-main) !important; background-color: var(--bg-panel) !important; }
li[role="option"]:hover, div[role="option"]:hover, li[aria-selected="true"], div[aria-selected="true"] { background-color: var(--bg-card-alt) !important; color: var(--accent-ag) !important; }

.stSlider label, .stRadio label, .stCheckbox label { color: var(--text-sec) !important; font-size: 0.84rem !important; }

/* Dataframe styling */
.stDataFrame { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; }
.stDataFrame th { background-color: var(--bg-panel) !important; color: var(--text-sec) !important; }
.stDataFrame td { color: var(--text-main) !important; }
.stDataFrame [data-testid="StyledDataFrameDataCell"] { background-color: var(--bg-card) !important; }

/* Multiselect pills */
span[data-baseweb="tag"] { background-color: var(--bg-card-alt) !important; color: var(--accent-ag) !important; border: 1px solid var(--border); }
span[data-baseweb="tag"] svg { fill: var(--accent-ag) !important; }

.stButton > button { background-color: var(--bg-card-alt); color: var(--accent-ag); border: 1px solid var(--accent-ag); border-radius: 4px; font-size: 0.82rem; }
.stButton > button:hover { background-color: var(--bg-panel); color: var(--accent-ag); border-color: var(--accent-ag); }

hr { border-color: var(--border) !important; margin: 10px 0 !important; }

/* Metric Cards */
.metric-container {
  display: flex;
  gap: 16px;
  width: 100%;
}
.metric-card {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 3px solid var(--accent-ag);
  padding: 12px 16px;
  border-radius: 6px;
  text-align: center;
  position: relative;
}
.metric-card.ag  { border-top-color: var(--accent-ag); }
.metric-card.ac  { border-top-color: var(--accent-ac); }
.metric-card.coq { border-top-color: var(--accent-coq); }
.metric-card.min { border-top-color: var(--text-muted); }

.metric-title { font-size: 0.74rem; color: var(--text-sec); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; font-weight: 500; }
.metric-val   { font-size: 1.5rem; font-weight: 600; color: var(--text-main); }

.ibox { background: var(--bg-card); border-left: 3px solid var(--accent-ag); padding: 12px 16px; border-radius: 6px; margin-top: 8px; font-size: 0.86em; color: var(--text-sec); border: 1px solid var(--border); border-left-width: 3px; }
.footer-bar { text-align: center; color: var(--text-muted); font-size: 0.76rem; padding: 16px 0 6px 0; border-top: 1px solid var(--border); margin-top: 24px; }
.phase-badge { display: inline-block; background: var(--bg-card); border: 1px solid var(--accent-phase); color: var(--accent-phase); border-radius: 4px; padding: 3px 10px; font-size: 0.82rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


def _section(title: str, subtitle: str = ""):
    st.markdown(f"<h3 style='margin:0;padding:0;color:#E5EEF7;font-size:1.05rem;'>{title}</h3>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='margin:0 0 4px 0;color:#8FA3B5;font-size:0.80rem;'>{subtitle}</p>", unsafe_allow_html=True)


def _render_metrics(m: dict):
    """Render metric cards: Peak Ag, Min Ag, Peak Ac, CoQ."""
    ag_max = f"{m['Ag_max']:.3f} mm²"
    ag_min = f"{m['Ag_min']:.3f} mm²"
    ac_max = f"{m['Ac_max']:.3f} mm²"
    coq    = f"{m['CoQ']:.1f} %"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"<div class='metric-card ag'>"
            f"<div class='metric-title'>Peak Glottal Area</div>"
            f"<div class='metric-val'>{ag_max}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card min'>"
            f"<div class='metric-title'>Min Glottal Area</div>"
            f"<div class='metric-val'>{ag_min}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='metric-card ac'>"
            f"<div class='metric-title'>Peak Contact Area</div>"
            f"<div class='metric-val'>{ac_max}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"<div class='metric-card coq'>"
            f"<div class='metric-title'>Contact Quotient (CoQ)</div>"
            f"<div class='metric-val'>{coq}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )



def _render_compare_metrics_html(ma: dict, mb: dict) -> str:
    """Render a premium dark med-tech HTML table comparing dynamic metrics."""
    interp_map = {
        "Ag_max": ("Larger peak area (B)",   "Smaller peak area (B)"),
        "Ag_min": ("Larger minimum area (B)", "Smaller minimum area (B)"),
        "Ac_max": ("Greater peak contact proxy (B)", "Less peak contact proxy (B)"),
        "CoQ":    ("Greater Contact Quotient (B)", "Less Contact Quotient (B)"),
        "Lc_max": ("More contact length (B)", "Less contact length (B)"),
        "Lc_pct": ("More contact % (B)",      "Less contact % (B)"),
    }
    metric_keys = [
        ("Ag_max", "Peak Glottal Area [mm²]", ".3f"),
        ("Ag_min", "Minimum Glottal Area [mm²]",  ".3f"),
        ("Ac_max", "Peak Contact Area Proxy [mm²]", ".3f"),
        ("CoQ",    "Approximate Contact Quotient [%]", ".1f"),
        ("Lc_max", "Max Contact Length [mm]", ".2f"),
        ("Lc_pct", "Max Contact Length [%]", ".1f"),
    ]
    
    # We define the HTML without any leading indentation on lines to prevent Markdown block parsers from treating it as a code block.
    lines = [
        '<table style="width:100%; border-collapse:collapse; background-color:#0F151C; border:1px solid rgba(255,255,255,0.08); font-family:Inter, sans-serif; font-size:0.88rem; color:#E5EEF7; border-radius:6px; overflow:hidden;">',
        '<thead>',
        '<tr style="background-color:#0B0F14; border-bottom:1px solid rgba(255,255,255,0.08); text-align:left;">',
        '<th style="padding:10px 14px; color:#8FA3B5; font-weight:600;">Metric</th>',
        '<th style="padding:10px 14px; color:#00C8E0; font-weight:600;">State A</th>',
        '<th style="padding:10px 14px; color:#F04D5E; font-weight:600;">State B</th>',
        '<th style="padding:10px 14px; color:#8FA3B5; font-weight:600;">Δ (B−A)</th>',
        '<th style="padding:10px 14px; color:#8FA3B5; font-weight:600;">Interpretation</th>',
        '</tr>',
        '</thead>',
        '<tbody>'
    ]
    
    for k, label, fmt in metric_keys:
        va = ma[k]
        vb = mb[k]
        delta = vb - va
        pos_i, neg_i = interp_map.get(k, ("Higher (B)", "Lower (B)"))
        semantic = pos_i if delta > 0.0001 else (neg_i if delta < -0.0001 else "No change")
        
        # delta color
        d_color = "#61D345" if delta > 0.0001 else ("#F04D5E" if delta < -0.0001 else "#5F7180")
        d_str = f"{delta:+{fmt}}" if abs(delta) > 0.0001 else "0.000"
        
        lines.append('<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">')
        lines.append(f'<td style="padding:10px 14px; font-weight:500;">{label}</td>')
        lines.append(f'<td style="padding:10px 14px;">{va:{fmt}}</td>')
        lines.append(f'<td style="padding:10px 14px;">{vb:{fmt}}</td>')
        lines.append(f'<td style="padding:10px 14px; color:{d_color}; font-weight:600;">{d_str}</td>')
        lines.append(f'<td style="padding:10px 14px; color:#8FA3B5;">{semantic}</td>')
        lines.append('</tr>')
        
    lines.append('</tbody>')
    lines.append('</table>')
    return "".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Presets
# ─────────────────────────────────────────────────────────────────────────────
PRESETS = {
    "Custom":                      (0.30, 0.30, 0.30, ""),
    "Neutral / balanced":          (0.30, 0.30, 0.30, "Balanced activation across intrinsic muscles."),
    "Chest-like / TA-weighted":    (0.25, 0.75, 0.55, "TA-dominated. Shorter, thicker folds with greater body depth."),
    "Falsetto-like / CT-weighted": (0.80, 0.10, 0.20, "CT-dominated. Longer, thinner folds. Reduced TA contribution."),
    "Adducted / LCA-weighted":     (0.35, 0.35, 0.80, "LCA-dominated. High adductory contribution."),
    "Light mechanism":             (0.55, 0.25, 0.30, "Moderate CT bias, lighter mechanism, reduced TA engagement."),
    "Heavy mechanism":             (0.35, 0.60, 0.55, "Moderate TA bias, heavier mechanism, thicker body."),
}

# ─────────────────────────────────────────────────────────────────────────────
# App Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='margin-bottom: 12px;'>"
    "<h1 style='color:#00C8E0; font-size:2.4rem; font-weight:700; margin:0 0 4px 0; letter-spacing:0.02em; line-height:1.2;'>"
    "VocalFold Explorer</h1>"
    "<p style='color:#8FA3B5; font-size:0.9rem; margin:0; font-weight:400;'>"
    "Interactive body-cover model for vocal fold geometry, mechanics, and glottal-cycle visualization · Developed by Calvache, 2026"
    "</p>"
    "</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs([
    "  Interactive Model  ", "  Compare Geometries  ", "  Activation Heatmaps  ", "  Equations & References  "
])


# =============================================================================
# TAB 1 – Interactive Model
# =============================================================================
with tab1:
    ctrl_cols = st.columns([2, 1, 1, 3.5])
    with ctrl_cols[0]:
        view_mode = st.radio(
            "Display mode", ["Static", "Animated"],
            horizontal=True, label_visibility="collapsed"
        )
    with ctrl_cols[1]: show_zn     = st.checkbox("Show Nodal Point",     value=False)
    with ctrl_cols[2]: show_labels = st.checkbox("Show labels",  value=True)

    # Output selectors only relevant for Animated
    graph_choices = ["Glottal Area Ag(t)", "Contact Area Proxy Ac(t)", "Metrics"]
    with ctrl_cols[3]:
        if view_mode == "Animated":
            out_sel = st.multiselect(
                "Graph outputs to display:",
                graph_choices,
                default=["Glottal Area Ag(t)", "Contact Area Proxy Ac(t)", "Metrics"]
            )
        else:
            out_sel = []

    animated       = view_mode == "Animated"
    phase_explorer = False
    st.markdown("<hr>", unsafe_allow_html=True)

    col_ctrl, col_3d = st.columns([1.15, 2.85])

    with col_ctrl:
        _section("Model Inputs")
        sex_choice  = st.radio("Sex", ["Male", "Female"], horizontal=True)
        preset_name = st.selectbox("Pedagogical configuration", list(PRESETS.keys()))
        def_ct, def_ta, def_lca, preset_info = PRESETS[preset_name]

        st.button("↺ Reset to preset")  # triggers re-run with preset defaults

        st.markdown("<p style='color:#8FA3B5;font-size:0.78rem;margin:6px 0 2px 0;'>MUSCLE ACTIVATION</p>", unsafe_allow_html=True)
        aCT  = st.slider("Cricothyroid (aCT)",          0.0, 1.0, def_ct,  step=0.01)
        aTA  = st.slider("Thyroarytenoid (aTA)",        0.0, 1.0, def_ta,  step=0.01)
        aLCA = st.slider("Lat. Cricoarytenoid (aLCA)",  0.0, 1.0, def_lca, step=0.01)

        st.markdown("<p style='color:#8FA3B5;font-size:0.78rem;margin:10px 0 2px 0;'>AERODYNAMIC DRIVER</p>", unsafe_allow_html=True)
        Ps = st.slider(
            "Subglottal Pressure [cmH₂O]", 0.0, 20.0, 8.0, step=0.5,
            help="Modulates oscillation amplitude. Low Ps (≤4) → incomplete glottal closure."
        )

        if preset_info:
            st.markdown(f"<div class='ibox'>{preset_info}</div>", unsafe_allow_html=True)

        st.session_state["cur"] = dict(aCT=aCT, aTA=aTA, aLCA=aLCA, sex=sex_choice)

    state = calculate_all(aCT=aCT, aTA=aTA, aLCA=aLCA, sex=sex_choice)

    with col_3d:
        _section("3D Vocal Fold Schematic", "Anterior–posterior view | Rotate freely with mouse")

        if animated:
            st.plotly_chart(plot_3d_fold_animated(state, Ps, show_zn, show_labels), use_container_width=True)
        else:
            st.plotly_chart(plot_3d_fold(state, show_zn, show_labels), use_container_width=True)

    # ── Glottal Cycle Explorer (Animated mode) ──
    if animated and len(out_sel) > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        _section("Glottal Cycle Explorer", "Model-derived pedagogical curves from the animated medial gap")

        dyn = compute_dynamic_gap(state, Ps)
        m   = dyn["metrics"]

        for sel in out_sel:
            if sel == "Glottal Area Ag(t)":
                st.plotly_chart(plot_glottal_area(dyn), use_container_width=True)
            elif sel == "Contact Area Proxy Ac(t)":
                st.plotly_chart(plot_contact_area_proxy(dyn), use_container_width=True)
                st.caption("⚠ **Contact Area Proxy** is a geometric proxy ($A_c = L_c \\cdot h_{\\text{contact}}$) derived from the simulated medial gap. It is not tissue contact pressure or a clinical measurement.")

        if "Metrics" in out_sel:
            st.markdown("<br>", unsafe_allow_html=True)
            _render_metrics(m)
            st.caption("⚠ **Note:** These curves and metrics are pedagogical proxies. They are not clinical high-speed imaging or FEM measurements.")


# =============================================================================
# TAB 2 – Compare Geometries
# =============================================================================
with tab2:
    st.markdown("<h3 style='color:#E5EEF7;margin:0 0 4px 0;'>Compare Geometries</h3>", unsafe_allow_html=True)
    if "sa" not in st.session_state: st.session_state["sa"] = dict(aCT=0.30, aTA=0.60, aLCA=0.50, sex="Male")
    if "sb" not in st.session_state: st.session_state["sb"] = dict(aCT=0.60, aTA=0.40, aLCA=0.40, sex="Male")

    btn1, btn2, btn3 = st.columns(3)
    if btn1.button("⬆ Use current model as State A"):
        cur = st.session_state.get("cur", {"aCT": 0.30, "aTA": 0.60, "aLCA": 0.50, "sex": "Male"})
        st.session_state["sa"] = cur.copy()
        st.session_state["ct_a"] = cur["aCT"]
        st.session_state["ta_a"] = cur["aTA"]
        st.session_state["lca_a"] = cur["aLCA"]
        st.session_state["sex_a"] = cur["sex"]
    if btn2.button("⬆ Use current model as State B"):
        cur = st.session_state.get("cur", {"aCT": 0.30, "aTA": 0.60, "aLCA": 0.50, "sex": "Male"})
        st.session_state["sb"] = cur.copy()
        st.session_state["ct_b"] = cur["aCT"]
        st.session_state["ta_b"] = cur["aTA"]
        st.session_state["lca_b"] = cur["aLCA"]
        st.session_state["sex_b"] = cur["sex"]
    if btn3.button("↺ Reset both states"):
        st.session_state["sa"] = dict(aCT=0.30, aTA=0.60, aLCA=0.50, sex="Male")
        st.session_state["sb"] = dict(aCT=0.60, aTA=0.40, aLCA=0.40, sex="Male")
        st.session_state["ct_a"] = 0.30
        st.session_state["ta_a"] = 0.60
        st.session_state["lca_a"] = 0.50
        st.session_state["sex_a"] = "Male"
        st.session_state["ct_b"] = 0.60
        st.session_state["ta_b"] = 0.40
        st.session_state["lca_b"] = 0.40
        st.session_state["sex_b"] = "Male"

    ca, cb = st.columns(2)
    with ca:
        st.markdown("<p style='color:#00c8e0;font-weight:600;margin:4px 0;'>State A (Cyan)</p>", unsafe_allow_html=True)
        aCT_A  = st.slider("aCT (A)",  0.0, 1.0, st.session_state["sa"]["aCT"],  key="ct_a")
        aTA_A  = st.slider("aTA (A)",  0.0, 1.0, st.session_state["sa"]["aTA"],  key="ta_a")
        aLCA_A = st.slider("aLCA (A)", 0.0, 1.0, st.session_state["sa"]["aLCA"], key="lca_a")
        sex_A  = st.radio("Sex A", ["Male", "Female"], key="sex_a", horizontal=True)
    with cb:
        st.markdown("<p style='color:#e05050;font-weight:600;margin:4px 0;'>State B (Red)</p>", unsafe_allow_html=True)
        aCT_B  = st.slider("aCT (B)",  0.0, 1.0, st.session_state["sb"]["aCT"],  key="ct_b")
        aTA_B  = st.slider("aTA (B)",  0.0, 1.0, st.session_state["sb"]["aTA"],  key="ta_b")
        aLCA_B = st.slider("aLCA (B)", 0.0, 1.0, st.session_state["sb"]["aLCA"], key="lca_b")
        sex_B  = st.radio("Sex B", ["Male", "Female"], key="sex_b", horizontal=True)

    state_A = calculate_all(aCT_A, aTA_A, aLCA_A, sex_A)
    state_B = calculate_all(aCT_B, aTA_B, aLCA_B, sex_B)

    st.markdown("<hr>", unsafe_allow_html=True)
    ctrl_cmp = st.columns([1.5, 1, 3.5])
    with ctrl_cmp[0]: comp_mode = st.radio("Comparison mode", ["Separate Mode", "Overlay Mode"], horizontal=True, label_visibility="collapsed")
    with ctrl_cmp[1]: show_zn_c = st.checkbox("Show Nodal Point", value=False, key="zn_compare")

    if comp_mode == "Separate Mode":
        with ctrl_cmp[2]:
            out_sel_c = st.multiselect(
                "Graph outputs (Requires vibration):",
                ["Glottal Area Ag(t)", "Contact Area Proxy Ac(t)", "Metrics"],
                default=["Glottal Area Ag(t)", "Contact Area Proxy Ac(t)", "Metrics"]
            )

        c_anim, c_pres = st.columns([1, 4])
        with c_anim: enable_anim = st.checkbox("Enable vibration", value=False)
        with c_pres: Ps_c = st.slider("Subglottal Pressure (compare) [cmH₂O]", 0.0, 20.0, 8.0, step=0.5, key="ps_c", disabled=not enable_anim)

        v1, v2 = st.columns(2)
        with v1:
            st.markdown("<p style='color:#00c8e0;margin:0;font-size:0.85rem;'>State A</p>", unsafe_allow_html=True)
            if enable_anim: st.plotly_chart(plot_3d_fold_animated(state_A, Ps_c, show_zn_c), use_container_width=True, key="ca_anim")
            else:           st.plotly_chart(plot_3d_fold(state_A, show_zn_c), use_container_width=True, key="ca_stat")
        with v2:
            st.markdown("<p style='color:#e05050;margin:0;font-size:0.85rem;'>State B</p>", unsafe_allow_html=True)
            if enable_anim: st.plotly_chart(plot_3d_fold_animated(state_B, Ps_c, show_zn_c), use_container_width=True, key="cb_anim")
            else:           st.plotly_chart(plot_3d_fold(state_B, show_zn_c), use_container_width=True, key="cb_stat")

        if enable_anim and len(out_sel_c) > 0:
            st.markdown("<hr>", unsafe_allow_html=True)
            dyn_a = compute_dynamic_gap(state_A, Ps_c)
            dyn_b = compute_dynamic_gap(state_B, Ps_c)

            for sel in out_sel_c:
                if sel == "Glottal Area Ag(t)":
                    st.plotly_chart(plot_cycle_comparison_ab(dyn_a, dyn_b, "Ag"), use_container_width=True)
                elif sel == "Contact Area Proxy Ac(t)":
                    st.plotly_chart(plot_cycle_comparison_ab(dyn_a, dyn_b, "Ac"), use_container_width=True)
                    st.caption("⚠ **Contact Area Proxy** is a geometric proxy derived from the simulated medial gap. It is not tissue contact pressure or a clinical measurement.")
                elif sel == "Metrics":
                    st.markdown(_render_compare_metrics_html(dyn_a["metrics"], dyn_b["metrics"]), unsafe_allow_html=True)
        elif not enable_anim:
            st.info("Dynamic glottal cycle outputs require vibration to be enabled.")

    else:
        st.plotly_chart(plot_comparison_overlay(state_A, state_B, show_zn_c), use_container_width=True)


# =============================================================================
# TAB 3 – Activation Heatmaps
# =============================================================================
with tab3:
    st.markdown("<h3 style='color:#E5EEF7;margin:0 0 4px 0;'>Activation Heatmaps</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8FA3B5;font-size:0.82rem;margin:0 0 10px 0;'>Explore how muscle activation patterns affect geometry, mechanical proxies, and glottal-cycle outputs.</p>", unsafe_allow_html=True)

    CATEGORIES = {
        "Glottal-cycle outputs": {
            "Peak Glottal Area Ag,max [mm²]": "Ag_max",
            "Minimum Glottal Area Ag,min [mm²]": "Ag_min",
            "Peak Contact Area Proxy Ac,max [mm²]": "Ac_max",
            "Approximate Contact Quotient CoQ [%]": "CoQ",
            "Max Contact Length Lc,max [mm]": "Lc_max",
            "Max Contact Length Lc,pct [%]": "Lc_pct",
        },
        "Geometry outputs": {
            "Length L [mm]": "length_mm",
            "Thickness T [mm]": "thickness_mm",
            "Nodal Point Zn [mm]": "nodal_point_mm",
            "Body Depth Db [mm]": "body_depth_mm",
            "Cover Depth Dc [mm]": "cover_depth_mm",
        },
        "Mechanical proxies": {
            "Effective Mass Proxy": "m_eff_proxy",
            "Effective Stiffness Proxy": "k_eff_proxy",
            "Stiffness–Mass Ratio Proxy": "k_to_m_ratio",
        },
        "Advanced model parameters": {
            "Body Mass Mb [kg]": "body_mass_kg",
            "Upper Mass M1 [kg]": "upper_mass_kg",
            "Lower Mass M2 [kg]": "lower_mass_kg",
            "Body Spring Kb": "body_spring",
            "Upper Spring K1": "upper_spring",
            "Lower Spring K2": "lower_spring",
            "Coupling Spring Kc": "cover_spring",
        }
    }

    hc1, hc2 = st.columns(2)
    with hc1:
        output_category = st.selectbox(
            "Output category",
            list(CATEGORIES.keys()),
            index=0  # Default: Glottal-cycle outputs
        )
        
        output_var_label = st.selectbox(
            "Output variable",
            list(CATEGORIES[output_category].keys()),
            index=0  # Default: Peak Glottal Area Ag,max [mm²]
        )
        if output_category == "Mechanical proxies":
            st.caption("Mechanical proxies summarize stiffness–mass tendencies of the implemented low-dimensional model. They are not F0, pitch, acoustic output, or clinical predictions.")
        
        map_var = CATEGORIES[output_category][output_var_label]
        map_sex = st.radio("Sex", ["Male", "Female"], horizontal=True, key="hm_sex")

    with hc2:
        plane = st.selectbox("Muscle plane", ["aCT vs aTA", "aCT vs aLCA", "aTA vs aLCA"], index=0)
        x_m, y_m, fixed_m = {
            "aCT vs aTA":  ("aCT", "aTA",  "aLCA"),
            "aCT vs aLCA": ("aCT", "aLCA", "aTA"),
            "aTA vs aLCA": ("aTA", "aLCA", "aCT"),
        }[plane]
        fixed_val = st.slider(f"Fixed {fixed_m}", 0.0, 1.0, 0.50, step=0.05)

    hfig, Xg, Yg, Zg = plot_activation_heatmap(map_var, map_sex, x_m, y_m, fixed_m, fixed_val)
    st.plotly_chart(hfig, use_container_width=True)

    # Interpretation Panel
    st.markdown("<h4 style='color:#E5EEF7;font-size:1.05rem;margin-top:16px;'>Heatmap Interpretation</h4>", unsafe_allow_html=True)
    
    # Compute statistics
    min_val = float(np.nanmin(Zg))
    max_val = float(np.nanmax(Zg))
    v_range = max_val - min_val
    
    idx_max = np.unravel_index(np.nanargmax(Zg), Zg.shape)
    max_x_val = float(Xg[idx_max])
    max_y_val = float(Yg[idx_max])
    
    if output_category == "Geometry outputs":
        interpretation = "Shows how activation settings modify the static geometric configuration of the body-cover model."
    elif output_category == "Glottal-cycle outputs":
        interpretation = "Shows how activation settings affect simulated glottal opening and contact-related pedagogical outputs."
    elif output_category == "Mechanical proxies":
        interpretation = "Shows mechanical tendencies derived from stiffness–mass relationships. This is not F0, pitch, or a clinical estimate."
    else:
        interpretation = "Internal model parameters for technical inspection."

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(
            f"<div class='metric-card min'>"
            f"<div class='metric-title'>Minimum Value</div>"
            f"<div class='metric-val'>{min_val:.4f}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_stat2:
        st.markdown(
            f"<div class='metric-card ag'>"
            f"<div class='metric-title'>Maximum Value</div>"
            f"<div class='metric-val'>{max_val:.4f}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_stat3:
        st.markdown(
            f"<div class='metric-card ac'>"
            f"<div class='metric-title'>Range (Max - Min)</div>"
            f"<div class='metric-val'>{v_range:.4f}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_stat4:
        st.markdown(
            f"<div class='metric-card coq'>"
            f"<div class='metric-title'>Highest Region</div>"
            f"<div class='metric-val' style='font-size:0.95rem;padding-top:4px;'>{x_m}: {max_x_val:.2f}<br>{y_m}: {max_y_val:.2f}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        
    st.markdown(f"<div class='ibox'><b>Interpretation:</b> {interpretation}</div>", unsafe_allow_html=True)


# =============================================================================
# TAB 4 – Equations & References
# =============================================================================
with tab4:
    st.markdown("<h3 style='color:#E5EEF7;'>Equations &amp; References</h3>", unsafe_allow_html=True)

    with st.expander("A. Purpose & Physiological Context", expanded=False):
        st.markdown("""
This application is an educational, interactive simulation based on a **low-dimensional triangular body-cover model** of the vocal folds. 
The tool demonstrates how intrinsic laryngeal muscle activations change vocal fold length, thickness, depths, and spring stiffnesses, 
and how these morphological changes shape the glottal cycle dynamics and contact patterns during phonation.
        """)

    with st.expander("B. Body-Cover Framework & Anatomy Mapping", expanded=False):
        st.markdown("""
The 3-mass model geometry is mapped to 3D space as follows:
- **$L$ (Length)**: Anterior-Posterior dimension (Y-axis).
- **$T$ (Thickness)**: Inferior-Superior vertical dimension (Z-axis).
- **$D_b, D_c$ (Depths)**: Medial-Lateral lateral depth (X-axis).
- **$Z_n$ (Nodal Point)**: Separates the upper/lower cover along the vertical Z-axis.

| Component | Visual | Mathematical Mapping |
|-----------|--------|----------------------|
| **Body / TA core** | 🔴 Wine red | Occupies full vertical thickness $T$, located laterally spanning from $D_c$ to $D_c+D_b$. |
| **Lower Cover Mass ($M_1$)** | 🟠 Amber | Occupies vertical space from $z=0$ to $z=Z_n$. Located medially spanning width $D_c$. |
| **Upper Cover Mass ($M_2$)** | 🟡 Light amber | Occupies vertical space from $z=Z_n$ to $z=T$. Located medially spanning width $D_c$. |
| **Nodal point $Z_n$** | 🔵 Cyan | Horizontal plane at $z=Z_n$ separating $M_1$ and $M_2$. |
        """)

    with st.expander("C. Intrinsic Muscle Control & Morphological Equations", expanded=False):
        st.markdown("Muscle activations cricothyroid ($a_{CT}$), thyroarytenoid ($a_{TA}$), and lateral cricoarytenoid ($a_{LCA}$) control vocal fold strain $\\varepsilon$ and morphology:")
        st.latex(r"\varepsilon = G\,(R\,a_{CT} - a_{TA}) - H\,a_{LCA}")
        st.latex(r"L = L_0\,(1+\varepsilon)")
        st.latex(r"T = T_0\,/\,(1+0.8\,\varepsilon)")
        st.latex(r"D_b = (a_{TA}\,D_{mus} + 0.5\,D_{lig})\,/\,(1+0.2\,\varepsilon)")
        st.latex(r"D_c = (D_{muc}  + 0.5\,D_{lig})\,/\,(1+0.2\,\varepsilon)")
        st.latex(r"Z_n = (1+a_{TA})^{T/3}")

    with st.expander("D. Mechanics & Spring Stiffnesses", expanded=False):
        st.markdown("Stiffness parameter scaling laws based on vocal fold strain $\\varepsilon$:")
        st.latex(r"K_b = K_{b0} \, (1 + 2\,\varepsilon^2 + 8\,\varepsilon^4) \cdot (1 + 3\,a_{TA})")
        st.latex(r"K_c = K_{c0} \, (1 + 2\,\varepsilon^2 + 8\,\varepsilon^4) \cdot (1 + a_{CT})")

    with st.expander("E. Glottal Cycle Explorer & Dynamic Gap Metrics", expanded=True):
        st.markdown("""
These curves and metrics are pedagogical derivations from the time-varying simulated medial gap $\\text{gap}(y,z,t)$:
        """)
        st.markdown("#### Glottal Area $A_g(t)$")
        st.latex(r"A_g(t) = \int_0^L \max\left(\min_z(\text{gap}(y,z,t)),\,0\right)\; dy")

        st.markdown("#### Contact Length $L_c(t)$")
        st.markdown("The length along the anterior-posterior axis that is in close contact (below a threshold $\\delta_c = 0.05$ mm):")
        st.latex(r"L_c(t) = \int_0^L \mathbf{1}\!\left[\min_z(\text{gap}(y,z,t)) \leq \delta_c\right]\; dy")

        st.markdown("#### Contact Area Proxy $A_c(t)$")
        st.markdown("The product of contact length and the effective vertical depth of contact $h_{\\text{contact}}$:")
        st.latex(r"A_c(t) = L_c(t) \cdot h_{\\text{contact}}")
        st.latex(r"h_{\\text{contact}} = \text{clamp}(0.5 \cdot D_c, \, 0.5, \, 1.5)")

        st.markdown("#### Contact Quotient (CoQ)")
        st.markdown("The ratio of the contact interval duration to the total period of the vibration cycle:")
        st.latex(r"\text{CoQ} = \frac{T_{\text{contact}}}{T_{\text{cycle}}} \times 100\% = \text{mean}\left(L_c(t) > 0\right) \times 100\%")

        st.markdown("#### Pedagogical Cycles & Mechanical Proxies")
        st.markdown("""
The glottal-cycle curves are displayed over normalized pedagogical cycles rather than calibrated physical time. Therefore, the application does not estimate F0, pitch, or acoustic frequency. Mechanical proxies only describe internal mass/stiffness tendencies.
        """)

        st.markdown("""
**Subglottal pressure and amplitude scaling:**
The vibration amplitude scales as $P_s^{2/3}$. 
- If $P_s \\leq 3$ cmH₂O, the oscillation amplitude is insufficient for the folds to meet medially, resulting in incomplete closure without contact.
- If $P_s \\geq 6$ cmH₂O, full closure and contact are achieved.
        """)

    with st.expander("F. Activation Heatmaps Categories", expanded=False):
        st.markdown("""
The heatmaps allow exploring how muscle activation patterns affect four distinct categories:
- **Geometry outputs**: Shows how activation settings modify the static geometric configuration of the body-cover model (Length, Thickness, Nodal Point, and layer depths).
- **Glottal-cycle outputs**: Shows how activation settings affect simulated glottal opening and contact-related pedagogical outputs ($A_{g,\\text{max}}$, $A_{g,\\text{min}}$, $A_{c,\\text{max}}$, $\\text{CoQ}$, $L_{c,\\text{max}}$, and $L_{c,\\text{pct}}$).
- **Mechanical proxies**: Shows mechanical tendencies derived from stiffness–mass relationships, including effective mass/stiffness proxies and the stiffness-to-mass ratio.
- **Advanced model parameters**: Technical model parameters for detailed inspection (layer masses $M_b, M_1, M_2$ and spring stiffnesses $K_b, K_1, K_2, K_c$).
        """)

    with st.expander("G. Limitations", expanded=False):
        st.markdown("""
- **Low-Dimensional Proxy**: This model simplifies the complex 3D continuum mechanics of vocal fold tissue into a few discrete masses.
- **Phonation Simulation**: It is not a clinical high-speed video processing system, finite element model (FEM) contact pressure simulation, or patient-specific surgical planner.
- **Fluid-Structure Interaction**: The aerodynamic driver is approximated using empirical scaling laws rather than solving the full Navier-Stokes flow equations.
        """)

    with st.expander("H. References", expanded=False):
        st.markdown("""
- Story BH, Titze IR. Voice simulation with a body-cover model of the vocal folds. *JASA*. 1995;97:1249–1260.
- Titze IR, Story BH. Rules for controlling low-dimensional vocal fold models with muscle activation. *JASA*. 2002;112:1064–1076.
- Zhang Z. Mechanics of human voice production and control. *JASA*. 2016;140:2614–2635.
- Zhang Z. Effect of vocal fold stiffness on voice production in a three-dimensional body-cover phonation model. *JASA*. 2017;142:2311–2321.
- Zhang Z. Vocal fold contact pressure in a three-dimensional body-cover phonation model. *JASA*. 2019;146:256–265.
- Smith SL, Titze IR. Vocal fold contact patterns based on normal modes of vibration. *Journal of Biomechanics*. 2018;73:177–184.
- Alzamendi GA et al. Triangular body-cover model of the vocal folds with coordinated activation of the five intrinsic laryngeal muscles. *JASA*. 2022;151:17–30.
        """)

# ─────────────────────────────────────────────────────────────────────────────
# Global Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='footer-bar'>"
    "VocalFold Explorer &nbsp;·&nbsp; "
    "Educational low-dimensional model"
    "</div>",
    unsafe_allow_html=True,
)
