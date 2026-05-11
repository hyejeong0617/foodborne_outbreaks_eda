# ─────────────────────────────────────────────────────────────────────────────
# Foodborne Disease Outbreak Dashboard
# CDC FDOSS 1998–2015  ·  3-page Streamlit application
# Run: streamlit run rasff_app.py   (or: streamlit run dashboard.py)
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Foodborne Disease Outbreak Analysis",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS injection ──────────────────────────────────────────────────────
st.markdown("""
<style>
/* KPI cards */
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #e8e8e8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
    height: 100%;
}
.kpi-card .kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 6px 0 4px;
}
.kpi-card .kpi-label {
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #888;
}
.kpi-card .kpi-sub {
    font-size: 0.75rem;
    color: #aaa;
    margin-top: 4px;
}
/* Insight cards */
.insight-card {
    border-radius: 10px;
    padding: 16px 18px;
    height: 100%;
    border-left: 5px solid;
}
.insight-card.red   { background:#fff5f5; border-color:#e53e3e; }
.insight-card.amber { background:#fffaf0; border-color:#dd6b20; }
.insight-card.blue  { background:#ebf8ff; border-color:#3182ce; }
.insight-card.green { background:#f0fff4; border-color:#38a169; }
.insight-card .ic-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 6px;
}
.insight-card.red   .ic-title { color: #c53030; }
.insight-card.amber .ic-title { color: #c05621; }
.insight-card.blue  .ic-title { color: #2b6cb0; }
.insight-card.green .ic-title { color: #276749; }
.insight-card .ic-num {
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}
.insight-card.red   .ic-num { color: #e53e3e; }
.insight-card.amber .ic-num { color: #dd6b20; }
.insight-card.blue  .ic-num { color: #3182ce; }
.insight-card.green .ic-num { color: #38a169; }
.insight-card .ic-body {
    font-size: 0.82rem;
    color: #444;
    line-height: 1.5;
}
/* Section divider label */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #aaa;
    margin: 24px 0 8px;
}
/* Dataset info box */
.dataset-box {
    background: #f7f9fc;
    border: 1px solid #dce3ed;
    border-radius: 10px;
    padding: 18px 22px;
    font-size: 0.85rem;
    color: #444;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Colour palette (consistent across all pages) ──────────────────────────────
C_PRIMARY   = "#2E6FA3"
C_DANGER    = "#C0392B"
C_WARM      = "#E07B39"
C_TEAL      = "#1D9E75"
C_PURPLE    = "#7F77DD"
C_GRAY      = "#888780"
SEQ_ROCKET  = "reds"
SEQ_TEAL    = "teal"

MONTH_ORDER = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
]

# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_data_grouped.csv")
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)
    # primary_location: first venue in compound strings
    df["primary_location"] = df["Location"].str.split(";").str[0].str.strip()
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🦠 Foodborne Outbreaks")
    st.markdown("**CDC FDOSS · 1998–2015**")
    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Overview", "🦠 Pathogen risk", "📍 Location analysis"],
        label_visibility="collapsed",
    )
    st.divider()

    # Global filters (apply to all pages)
    st.markdown("**Filters**")
    year_range = st.slider(
        "Year range", 1998, 2015, (1998, 2015), step=1
    )
    top_n = st.selectbox("Top N categories", [5, 10, 15, 20], index=1)

    st.divider()
    st.caption(
        "Analysis: Hyejeong (Hayley) Lee  \n"
        "Ph.D. Biotechnology · NTNU, 2023  \n"
        "Data Science & ML · Ironhack, 2025"
    )

# ── Apply year filter ─────────────────────────────────────────────────────────
df_f = df[df["Year"].between(year_range[0], year_range[1])].copy()

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def excl(data, col):
    """Exclude 'Unknown' rows."""
    return data[data[col].str.lower() != "unknown"].copy()

def kpi(col, label, value, color="#2E6FA3", sub=None):
    """Render a styled KPI card with HTML."""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value" style="color:{color}">{value}</div>
    {sub_html}
</div>""", unsafe_allow_html=True)


def insight_card(col, color, title, number, body):
    """Render a bordered insight card with a prominent number."""
    col.markdown(f"""
<div class="insight-card {color}">
    <div class="ic-title">{title}</div>
    <div class="ic-num">{number}</div>
    <div class="ic-body">{body}</div>
</div>""", unsafe_allow_html=True)

def fmt_k(n):
    return f"{int(n):,}"

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 · OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Overview":

    st.title("Foodborne Disease Outbreak Overview")
    st.caption(
        f"CDC Foodborne Disease Outbreak Surveillance System · "
        f"{year_range[0]}–{year_range[1]}"
    )

    # ── About this dataset ────────────────────────────────────────────────────
    with st.expander("ℹ️ About this dataset", expanded=False):
        st.markdown("""
<div class="dataset-box">
<strong>Source:</strong>
<a href="https://www.kaggle.com/datasets/cdc/foodborne-diseases" target="_blank">
CDC Foodborne Disease Outbreak Surveillance System (FDOSS)</a> via Kaggle<br><br>
The CDC has tracked foodborne disease outbreaks in the United States since 1973.
This dataset covers <strong>1998–2015</strong> — 18 years of surveillance across all 50 states.
Each record represents a single confirmed outbreak event reported by state and local health departments.
<br><br>
<table style="width:100%;font-size:0.82rem;border-collapse:collapse">
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">Year / Month</td>
  <td style="padding:5px 10px;color:#666">When the outbreak was reported</td>
</tr>
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">State / Location</td>
  <td style="padding:5px 10px;color:#666">Where it occurred (state + venue type)</td>
</tr>
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">Food</td>
  <td style="padding:5px 10px;color:#666">Implicated food vehicle</td>
</tr>
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">Species</td>
  <td style="padding:5px 10px;color:#666">Causative pathogen (bacteria, virus, toxin)</td>
</tr>
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">Illnesses</td>
  <td style="padding:5px 10px;color:#666">Number of people ill</td>
</tr>
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:5px 10px;font-weight:600;color:#555">Hospitalizations</td>
  <td style="padding:5px 10px;color:#666">Number hospitalised</td>
</tr>
<tr>
  <td style="padding:5px 10px;font-weight:600;color:#555">Fatalities</td>
  <td style="padding:5px 10px;color:#666">Number of deaths</td>
</tr>
</table>
<br>
<strong>Scope:</strong> Only <em>confirmed</em> outbreaks with ≥2 cases linked to the same source.
Missingness in <code>Food</code> (46%) and <code>Species</code> (34%) reflects
real-world surveillance limitations, not analysis errors.
</div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Key insights (always visible, top of page) ────────────────────────────
    st.markdown('<div class="section-label">Key findings</div>',
                unsafe_allow_html=True)
    ins1, ins2, ins3, ins4 = st.columns(4)
    insight_card(ins1, "blue",  "Outbreak trend",
                 "−31%",
                 "Outbreaks declined from 1998 to 2015. Improved food safety "
                 "regulation — not a true reduction in exposure risk.")
    insight_card(ins2, "green", "Seasonal pattern",
                 "Bimodal",
                 "Summer peak (May–Jun) from bacterial growth + winter peak "
                 "(Dec) from Norovirus. Autumn is consistently lowest-risk.")
    insight_card(ins3, "amber", "Top food vehicle",
                 "Salad #1",
                 "Complex multi-ingredient, no kill step. Raw produce is a "
                 "known contamination vector — 677 outbreaks.")
    insight_card(ins4, "red",   "Frequency ≠ severity",
                 "37% vs 51%",
                 "Norovirus: 37% of all illnesses. Salmonella: 51% of all "
                 "hospitalisations. Completely different metrics, different priorities.")

    st.divider()

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi(k1, "Total outbreaks",   fmt_k(len(df_f)),                      "#2E6FA3")
    kpi(k2, "Total illnesses",   fmt_k(df_f["Illnesses"].sum()),         "#E07B39")
    kpi(k3, "Hospitalisations",  fmt_k(df_f["Hospitalizations"].sum()),  "#C0392B")
    kpi(k4, "Fatalities",        fmt_k(df_f["Fatalities"].sum()),        "#7F77DD",
        sub="deaths confirmed")
    kpi(k5, "States covered",    str(df_f["State"].nunique()),           "#1D9E75")

    st.divider()

    # ── Row 1: Annual trend (dual axis) ───────────────────────────────────────
    yr = df_f.groupby("Year").agg(
        Outbreaks=("Illnesses", "count"),
        Illnesses=("Illnesses", "sum"),
    ).reset_index()

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Bar(x=yr["Year"], y=yr["Outbreaks"],
               name="Outbreaks", marker_color=C_PRIMARY, opacity=0.75),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Scatter(x=yr["Year"], y=yr["Illnesses"],
                   name="Illnesses", mode="lines+markers",
                   line=dict(color=C_DANGER, width=2),
                   marker=dict(size=5)),
        secondary_y=True,
    )
    fig_trend.update_layout(
        title="Annual outbreak count vs. illness burden",
        legend=dict(orientation="h", y=1.08),
        height=340, margin=dict(t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_trend.update_yaxes(title_text="Outbreaks", secondary_y=False,
                            gridcolor="#eee")
    fig_trend.update_yaxes(title_text="Illnesses", secondary_y=True,
                            gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── Row 2: Monthly + Food/Pathogen ────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        mo = (df_f["Month"].value_counts()
              .reset_index()
              .rename(columns={"Month": "Month", "count": "Outbreaks"})
              .sort_values("Month"))
        fig_mo = px.bar(
            mo, x="Month", y="Outbreaks",
            color="Outbreaks", color_continuous_scale=SEQ_TEAL,
            title="Seasonal distribution of outbreaks",
        )
        fig_mo.update_layout(
            height=340, showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=50, b=80),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_mo.update_xaxes(tickangle=40)
        st.plotly_chart(fig_mo, use_container_width=True)

    with col_right:
        state_df = df_f["State"].value_counts().head(top_n).reset_index()
        state_df.columns = ["State", "Outbreaks"]
        fig_state = px.bar(
            state_df.sort_values("Outbreaks"),
            x="Outbreaks", y="State", orientation="h",
            color="Outbreaks", color_continuous_scale=SEQ_ROCKET,
            title=f"Top {top_n} states by outbreak count",
        )
        fig_state.update_layout(
            height=340, showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=50, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_state, use_container_width=True)

    # ── Row 3: Food + Pathogen frequency ─────────────────────────────────────
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        food_df = (excl(df_f, "Food_grouped")["Food_grouped"]
                   .value_counts().head(top_n).reset_index())
        food_df.columns = ["Food", "Outbreaks"]
        fig_food = px.bar(
            food_df.sort_values("Outbreaks"),
            x="Outbreaks", y="Food", orientation="h",
            color="Outbreaks", color_continuous_scale=SEQ_ROCKET,
            title=f"Top {top_n} food vehicles (outbreak frequency)",
        )
        fig_food.update_layout(
            height=360, showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=50, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_food, use_container_width=True)

    with col_r2:
        path_df = (excl(df_f, "Species_grouped")["Species_grouped"]
                   .value_counts().head(top_n).reset_index())
        path_df.columns = ["Pathogen", "Outbreaks"]
        fig_path = px.bar(
            path_df.sort_values("Outbreaks"),
            x="Outbreaks", y="Pathogen", orientation="h",
            color="Outbreaks", color_continuous_scale=SEQ_TEAL,
            title=f"Top {top_n} pathogens (outbreak frequency)",
        )
        fig_path.update_layout(
            height=360, showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=50, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_path, use_container_width=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 · PATHOGEN RISK
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🦠 Pathogen risk":

    st.title("Pathogen Risk Profile")
    st.caption(
        "CDC FDOSS 1998–2015 · "
        f"{year_range[0]}–{year_range[1]} filter applied"
    )

    # ── Key insights (always visible) ─────────────────────────────────────────
    st.markdown('<div class="section-label">Key findings</div>',
                unsafe_allow_html=True)
    p2i1, p2i2, p2i3 = st.columns(3)
    insight_card(p2i1, "red",   "The inversion",
                 "37% → 51%",
                 "Norovirus: <strong>37%</strong> of all illnesses, only 10% of hospitalisations. "
                 "Salmonella: <strong>51%</strong> of all hospitalisations. "
                 "Frequency rankings and severity rankings are completely different.")
    insight_card(p2i2, "amber", "Most clinically dangerous",
                 "76% hosp. rate",
                 "<em>Listeria monocytogenes</em>: <strong>76%</strong> hospitalisation rate, "
                 "<strong>16%</strong> fatality rate. "
                 "<em>C. botulinum</em>: 75% hospitalisation rate. Low frequency, extreme severity.")
    insight_card(p2i3, "blue",  "Seasonal ecology",
                 "Winter vs Summer",
                 "Norovirus dominates <strong>winter</strong> (Dec–Feb) — environmental persistence. "
                 "Salmonella peaks in <strong>summer</strong> — bacterial growth at warm temperatures. "
                 "Same season, different pathogen, different source.")

    st.divider()

    # ── What this page shows ──────────────────────────────────────────────────
    with st.expander("ℹ️ How to read this page", expanded=False):
        st.markdown("""
This page analyses **which pathogens cause the most harm** — and separates
*frequency* (how often an outbreak occurs) from *severity* (how serious it is
when it does occur).

**Three severity metrics:**
- **Total illnesses** — volume of disease burden
- **Total hospitalisations** — burden on healthcare system
- **Hospitalisation rate** = hospitalisations ÷ illnesses — clinical severity *per case*
- **Fatality rate** = deaths ÷ illnesses — lethality *per case*

A pathogen can rank #1 on frequency and #10 on severity (Norovirus),
or #8 on frequency and #1 on severity (Listeria). Both matter —
but they require completely different intervention strategies.
        """)

    # ── KPI row ───────────────────────────────────────────────────────────────
    noro_ill  = int(df_f[df_f["Species_grouped"]=="Norovirus"]["Illnesses"].sum())
    salm_hosp = int(df_f[df_f["Species_grouped"]=="Salmonella enterica"]["Hospitalizations"].sum())
    total_ill = int(df_f["Illnesses"].sum())
    total_hop = int(df_f["Hospitalizations"].sum())

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Norovirus illness share",
        f"{noro_ill/total_ill*100:.1f}%", "#E07B39",
        sub=f"{fmt_k(noro_ill)} cases total")
    kpi(k2, "Norovirus hosp. rate",
        f"{int(df_f[df_f['Species_grouped']=='Norovirus']['Hospitalizations'].sum())/noro_ill*100:.1f}%",
        "#1D9E75", sub="hospitalisations per illness")
    kpi(k3, "Salmonella hosp. share",
        f"{salm_hosp/total_hop*100:.1f}%", "#C0392B",
        sub=f"{fmt_k(salm_hosp)} hospitalisations")
    kpi(k4, "Listeria fatality rate",
        "16.0%", "#7F77DD",
        sub="highest among major pathogens")

    st.divider()

    # ── Row 1: Illnesses vs Hospitalisations ──────────────────────────────────
    sp_data = (
        excl(df_f, "Species_grouped")
        .groupby("Species_grouped")
        .agg(Illnesses=("Illnesses","sum"),
             Hospitalisations=("Hospitalizations","sum"))
        .reset_index()
    )
    top_ill  = sp_data.nlargest(top_n, "Illnesses")
    top_hosp = sp_data.nlargest(top_n, "Hospitalisations")

    col_l, col_r = st.columns(2)

    with col_l:
        fig_ill = px.bar(
            top_ill.sort_values("Illnesses"),
            x="Illnesses", y="Species_grouped", orientation="h",
            color="Illnesses", color_continuous_scale=SEQ_TEAL,
            title=f"Top {top_n} pathogens — total illnesses",
        )
        fig_ill.update_layout(
            height=380, showlegend=False, coloraxis_showscale=False,
            margin=dict(t=50, b=40), yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_ill, use_container_width=True)

    with col_r:
        fig_hosp = px.bar(
            top_hosp.sort_values("Hospitalisations"),
            x="Hospitalisations", y="Species_grouped", orientation="h",
            color="Hospitalisations", color_continuous_scale=SEQ_ROCKET,
            title=f"Top {top_n} pathogens — total hospitalisations",
        )
        fig_hosp.update_layout(
            height=380, showlegend=False, coloraxis_showscale=False,
            margin=dict(t=50, b=40), yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_hosp, use_container_width=True)

    # ── Row 2: Rate analysis ──────────────────────────────────────────────────
    sev = (
        df_f[df_f["Illnesses"] > 0]
        .groupby("Species_grouped")
        .agg(hosp=("Hospitalizations","sum"),
             ill=("Illnesses","sum"),
             fatal=("Fatalities","sum"))
        .reset_index()
    )
    sev["Hosp rate"]  = sev["hosp"]  / sev["ill"]
    sev["Fatal rate"] = sev["fatal"] / sev["ill"]
    sev_stable = excl(sev, "Species_grouped")[sev["ill"] >= 30]

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        # Show all pathogens meeting stability threshold (ill >= 30),
        # sorted ascending so highest rate appears at top of horizontal bar.
        top_hr = sev_stable.nlargest(10, "Hosp rate").sort_values("Hosp rate")
        colors_hr = [C_DANGER if v == top_hr["Hosp rate"].max()
                     else C_PRIMARY for v in top_hr["Hosp rate"]]
        fig_hr = go.Figure(go.Bar(
            x=top_hr["Hosp rate"],
            y=top_hr["Species_grouped"],
            orientation="h",
            marker_color=colors_hr,
            text=[f"{v:.0%}" for v in top_hr["Hosp rate"]],
            textposition="outside",
        ))
        fig_hr.update_layout(
            title="Hospitalisation rate — top 10 (min 30 cases)",
            height=400, margin=dict(t=50, b=40, r=60), yaxis_title="",
            xaxis=dict(tickformat=".0%"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    with col_r2:
        top_fr = sev_stable.nlargest(10, "Fatal rate").sort_values("Fatal rate")
        colors_fr = [C_DANGER if v == top_fr["Fatal rate"].max()
                     else C_GRAY for v in top_fr["Fatal rate"]]
        fig_fr = go.Figure(go.Bar(
            x=top_fr["Fatal rate"],
            y=top_fr["Species_grouped"],
            orientation="h",
            marker_color=colors_fr,
            text=[f"{v:.1%}" for v in top_fr["Fatal rate"]],
            textposition="outside",
        ))
        fig_fr.update_layout(
            title="Fatality rate — top 10 (min 30 cases)",
            height=400, margin=dict(t=50, b=40, r=60), yaxis_title="",
            xaxis=dict(tickformat=".1%"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_fr, use_container_width=True)

    # ── Row 3: Seasonal × Pathogen ────────────────────────────────────────────
    st.subheader("Seasonal pathogen composition")
    top_path_list = (excl(df_f, "Species_grouped")["Species_grouped"]
                     .value_counts().head(8).index.tolist())
    df_top = df_f[df_f["Species_grouped"].isin(top_path_list)].copy()
    df_top["Month"] = pd.Categorical(df_top["Month"],
                                      categories=MONTH_ORDER, ordered=True)
    ct_mo = (pd.crosstab(df_top["Month"], df_top["Species_grouped"])
             .div(pd.crosstab(df_top["Month"], df_top["Species_grouped"])
                  .sum(axis=1), axis=0))
    ct_mo_long = ct_mo.reset_index().melt(id_vars="Month",
                                           var_name="Pathogen",
                                           value_name="Proportion")
    fig_seasonal = px.bar(
        ct_mo_long, x="Month", y="Proportion",
        color="Pathogen",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Monthly pathogen composition (top 8, proportion-normalised)",
        barmode="stack",
    )
    fig_seasonal.update_layout(
        height=360, margin=dict(t=50, b=80),
        xaxis_tickangle=40, yaxis_tickformat=".0%",
        legend=dict(orientation="h", y=-0.35, x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)

    # ── Food × Pathogen heatmap ───────────────────────────────────────────────
    st.subheader("Food–pathogen risk matrix")
    metric_opt = st.radio(
        "Metric",
        ["Outbreak count", "Total illnesses"],
        horizontal=True,
        label_visibility="collapsed",
    )
    top_food_list = (excl(df_f, "Food_grouped")["Food_grouped"]
                     .value_counts().head(top_n).index.tolist())
    df_matrix = df_f[
        df_f["Species_grouped"].isin(top_path_list) &
        df_f["Food_grouped"].isin(top_food_list)
    ]
    if metric_opt == "Outbreak count":
        hm_data = pd.crosstab(df_matrix["Species_grouped"],
                               df_matrix["Food_grouped"])
        cbar_title = "Outbreaks"
    else:
        hm_data = df_matrix.pivot_table(
            values="Illnesses", index="Species_grouped",
            columns="Food_grouped", aggfunc="sum", fill_value=0)
        cbar_title = "Illnesses"

    fig_hm = px.imshow(
        hm_data,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        title=f"Food × Pathogen — {metric_opt.lower()}",
        aspect="auto",
    )
    fig_hm.update_layout(
        height=420, margin=dict(t=60, b=80),
        coloraxis_colorbar_title=cbar_title,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_hm.update_xaxes(tickangle=40)
    st.plotly_chart(fig_hm, use_container_width=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 · LOCATION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📍 Location analysis":

    st.title("Location Risk Analysis")
    st.caption(
        "CDC FDOSS 1998–2015 · "
        f"{year_range[0]}–{year_range[1]} filter applied"
    )

    # ── Key insights (always visible) ─────────────────────────────────────────
    st.markdown('<div class="section-label">Key findings</div>',
                unsafe_allow_html=True)
    p3i1, p3i2, p3i3, p3i4 = st.columns(4)
    insight_card(p3i1, "red",   "Scale anomaly — Prison/Jail",
                 "107 cases/event",
                 "Prison/Jail is only <strong>1%</strong> of outbreaks but averages "
                 "<strong>107 cases per event</strong> — 8× larger than Restaurant (14). "
                 "Why this pattern exists cannot be determined from FDOSS alone.")
    insight_card(p3i2, "amber", "Severity anomaly — Private Home",
                 "9.3% hosp. rate",
                 "Private Home has the highest hospitalisation rate: <strong>9.3%</strong> — "
                 "nearly <strong>3×</strong> Restaurant (3.6%). "
                 "The dataset records where food was consumed, not who consumed it.")
    insight_card(p3i3, "red",   "Fatality concentration — Nursing Home",
                 "44 deaths",
                 "<strong>44 fatalities</strong> from only 186 outbreaks — "
                 "the highest fatality count per outbreak of all settings. "
                 "This is an observed association in the data.")
    insight_card(p3i4, "blue",  "Pathogen composition varies",
                 "2 exceptions",
                 "Norovirus dominates most settings. Two exceptions observed: "
                 "Prison/Jail (<em>Clostridium</em> highest illness burden) and "
                 "Private Home (only setting where <em>Salmonella</em> leads on both metrics).")

    st.divider()

    # ── What this page shows ──────────────────────────────────────────────────
    with st.expander("ℹ️ How to read this page", expanded=False):
        st.markdown("""
This page asks: **does where an outbreak occurs determine how severe it is?**

The answer is yes — and this has direct implications for where regulatory
resources should be focused.

**Three severity dimensions:**
- **Average outbreak size** — how many people are affected when an event occurs
- **Hospitalisation rate** — what fraction of ill people need hospital care
- **Fatality rate** — what fraction die

**Colour coding:** Settings with hospitalisation rate above the median
are highlighted in red — this is determined by the data, not by
pre-assigned categories.

The bubble chart is the key visualisation:
x-axis = average outbreak scale, y-axis = hospitalisation rate,
bubble size = total outbreak count. Settings in the upper-right
are both large *and* severe. Settings in the lower-right are large
but clinically mild (e.g. School/College).
        """)

    # ── Setting profile aggregation ───────────────────────────────────────────
    loc_p = (
        df_f[df_f["primary_location"] != "Unknown"]
        .groupby("primary_location")
        .agg(
            Outbreaks    = ("Illnesses", "count"),
            Illnesses    = ("Illnesses", "sum"),
            Hospitalisations = ("Hospitalizations", "sum"),
            Fatalities   = ("Fatalities", "sum"),
            Avg_size     = ("Illnesses", "mean"),
        )
        .reset_index()
    )
    loc_p["Hosp rate"]  = loc_p["Hospitalisations"] / loc_p["Illnesses"]
    loc_p["Fatal rate"] = loc_p["Fatalities"] / loc_p["Illnesses"]

    # No pre-assigned vulnerability categories.
    # Colour in charts is determined by observed data: settings with
    # hospitalisation rate above median are highlighted in red.

    # ── KPI row ───────────────────────────────────────────────────────────────
    prison  = loc_p[loc_p["primary_location"] == "Prison/Jail"].iloc[0]
    nursing = loc_p[loc_p["primary_location"] == "Nursing Home/Assisted Living Facility"].iloc[0]
    home    = loc_p[loc_p["primary_location"] == "Private Home/Residence"].iloc[0]
    rest    = loc_p[loc_p["primary_location"] == "Restaurant"].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Prison avg outbreak size",
        f"{prison['Avg_size']:.0f} cases", "#C0392B",
        sub="8× larger than Restaurant avg")
    kpi(k2, "Private Home hosp. rate",
        f"{home['Hosp rate']:.1%}", "#E07B39",
        sub="3× higher than Restaurant (3.6%)")
    kpi(k3, "Nursing Home fatalities",
        fmt_k(nursing["Fatalities"]), "#7F77DD",
        sub="from 186 outbreaks (0.8% fatality rate)")
    kpi(k4, "Restaurant share",
        f"{rest['Outbreaks']/loc_p['Outbreaks'].sum()*100:.1f}%", "#2E6FA3",
        sub="of all outbreaks — frequency leader")

    st.divider()

    # ── Row 1: Bubble chart ───────────────────────────────────────────────────
    loc_stable = loc_p[loc_p["Outbreaks"] >= 8].copy()
    loc_stable["label"] = loc_stable["primary_location"].str.replace(
        "/", "/<br>", regex=False
    )

    # Colour by hospitalisation rate (data-driven, no pre-assigned categories)
    median_hosp = loc_stable["Hosp rate"].median()
    loc_stable["highlight"] = loc_stable["Hosp rate"].apply(
        lambda x: "Above median hosp. rate" if x >= median_hosp else "Below median"
    )

    fig_bubble = px.scatter(
        loc_stable,
        x="Avg_size",
        y="Hosp rate",
        size="Outbreaks",
        color="highlight",
        color_discrete_map={
            "Above median hosp. rate": C_DANGER,
            "Below median": C_PRIMARY,
        },
        hover_name="primary_location",
        hover_data={
            "Outbreaks": True,
            "Illnesses": True,
            "Avg_size": ":.1f",
            "Hosp rate": ":.1%",
            "Fatal rate": ":.2%",
            "highlight": False,
        },
        text="primary_location",
        title="Setting severity profile — outbreak scale vs. hospitalisation rate",
        labels={
            "Avg_size": "Average outbreak size (cases / event)",
            "Hosp rate": "Hospitalisation rate",
        },
    )
    fig_bubble.update_traces(
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(opacity=0.7, line=dict(width=1, color="white")),
    )
    fig_bubble.update_yaxes(tickformat=".0%")
    fig_bubble.update_layout(
        height=460, margin=dict(t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.08),
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    # ── Row 2: Three severity bars ────────────────────────────────────────────
    SHOW_LOCS = [
        "Restaurant", "Fast Food Restaurant", "Catering Service",
        "Banquet Facility", "Private Home/Residence", "Grocery Store",
        "School/College/University", "Prison/Jail",
        "Nursing Home/Assisted Living Facility", "Hospital",
    ]
    loc_sub = loc_p[loc_p["primary_location"].isin(SHOW_LOCS)].copy()

    col_a, col_b, col_c = st.columns(3)

    def loc_bar(col, metric, title, fmt):
        sub = loc_sub.sort_values(metric, ascending=True)
        # Highlight the top value on each metric (data-driven)
        max_val = sub[metric].max()
        colors = [C_DANGER if v == max_val else C_PRIMARY for v in sub[metric]]
        fig = go.Figure(go.Bar(
            y=sub["primary_location"],
            x=sub[metric],
            orientation="h",
            marker_color=colors,
            text=[fmt(v) for v in sub[metric]],
            textposition="outside",
        ))
        fig.update_layout(
            title=title, height=400,
            margin=dict(t=50, b=30, r=80), xaxis_title="",
            yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        col.plotly_chart(fig, use_container_width=True)

    loc_bar(col_a, "Avg_size",   "Avg outbreak size (cases/event)",
            lambda v: f"{v:.0f}")
    loc_bar(col_b, "Hosp rate",  "Hospitalisation rate",
            lambda v: f"{v:.1%}")
    loc_bar(col_c, "Fatal rate", "Fatality rate",
            lambda v: f"{v:.2%}")

    # ── Row 3: Setting × Pathogen heatmap ─────────────────────────────────────
    st.subheader("Setting × pathogen risk matrix")

    # Explicitly defined to match EDA Section 3.5 — includes Nursing Home
    # despite lower outbreak count, because fatality profile warrants inclusion
    ANALYSIS_LOCS = [
        "Restaurant", "Fast Food Restaurant", "Catering Service",
        "Private Home/Residence", "School/College/University",
        "Prison/Jail", "Nursing Home/Assisted Living Facility", "Banquet Facility",
    ]
    top8_path = (excl(df_f, "Species_grouped")["Species_grouped"]
                 .value_counts().head(8).index.tolist())

    df_lp = df_f[
        df_f["primary_location"].isin(ANALYSIS_LOCS) &
        df_f["Species_grouped"].isin(top8_path)
    ]

    loc_metric = st.radio(
        "Matrix metric",
        ["Outbreak count", "Total illnesses"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if loc_metric == "Outbreak count":
        lp_data = pd.crosstab(df_lp["primary_location"],
                               df_lp["Species_grouped"])
        cbar = "Outbreaks"
    else:
        lp_data = df_lp.pivot_table(
            values="Illnesses",
            index="primary_location",
            columns="Species_grouped",
            aggfunc="sum", fill_value=0,
        )
        cbar = "Illnesses"

    fig_lp = px.imshow(
        lp_data,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        title=f"Setting × pathogen — {loc_metric.lower()}",
        aspect="auto",
    )
    fig_lp.update_layout(
        height=420, margin=dict(t=60, b=80),
        coloraxis_colorbar_title=cbar,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_lp.update_xaxes(tickangle=40)
    st.plotly_chart(fig_lp, use_container_width=True)


