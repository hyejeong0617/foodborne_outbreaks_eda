"""Portfolio-focused CDC foodborne outbreak dashboard (1998–2015).

Descriptive surveillance analysis. Missing clinical outcomes are never
implicitly converted to zero when constructing rate denominators.
"""
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Foodborne Disease Outbreak Analysis | Portfolio",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#20334A"
TEAL = "#157C8A"
CORAL = "#C86755"
MUTED = "#586B80"
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
VENUES = {
    "Restaurant": "Restaurant",
    "Prison/Jail": "Prison / jail",
    "Private Home/Residence": "Private home",
    "Nursing Home/Assisted Living Facility": "Nursing home",
    "School/College/University": "School / college",
    "Fast Food Restaurant": "Fast food",
    "Catering Service": "Catering",
}

st.markdown("""
<style>
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], .stApp {
    background-color: #F8FAFC !important; color: #20334A !important;
}
[data-testid="stHeader"] {background: #F8FAFC !important;}
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background: #EDF3F7 !important; color: #20334A !important;
}
[data-testid="stSidebar"] * {color: #20334A;}
[data-testid="stApp"] p, [data-testid="stApp"] label, [data-testid="stApp"] h1,
[data-testid="stApp"] h2, [data-testid="stApp"] h3 {color: #20334A;}
.block-container {max-width: 1160px; padding-top: 2rem; padding-bottom: 3.5rem;}
.stPlotlyChart {background: #FFFFFF; border: 1px solid #E3EAF0;
    border-radius: 12px; padding: 8px 12px;}
[data-testid="stExpander"] {background: #FFFFFF; border: 1px solid #E3EAF0; border-radius: 10px;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(130,145,160,.20);}
.portfolio-project-name {
    color: #20334A !important; font-size: 1.28rem; font-weight: 800;
    letter-spacing: -.025em; line-height: 1.4; margin-bottom: .55rem;
    opacity: 1 !important;
}
.hero-eyebrow {color: #087F8C; font-size: .78rem; font-weight: 750; letter-spacing: .12em;}
.hero-sub {color: #586B80; font-size: .99rem; max-width: 760px; line-height: 1.7;}
.story-note {border-left: 3px solid #087F8C; padding: .65rem 1rem; margin: .7rem 0 1.2rem;
    background: rgba(8,127,140,.07); border-radius: 0 .45rem .45rem 0;}
.section-caption {color:#64778A; font-size: .85rem; margin-bottom: .4rem;}
[data-testid="stMetric"] {background: #FFFFFF; padding: .75rem 1rem; border: 1px solid #E0E7EE;
    border-radius: .75rem; min-height: 105px;}
[data-testid="stMetricLabel"] {font-size: .82rem;}
[data-testid="stMetricValue"] {font-size: 1.65rem;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    data = pd.read_csv("data/cleaned_data_grouped.csv")
    numeric = ["Year", "Illnesses", "Hospitalizations", "Fatalities"]
    for name in numeric:
        data[name] = pd.to_numeric(data[name], errors="coerce")
    data["primary_location"] = (
        data["primary_location"].fillna("Unknown").astype(str).str.strip()
    )
    for name in ["Species_grouped", "Food_grouped"]:
        data[name] = data[name].fillna("Unknown").astype(str).str.strip()
    return data


def known(data, name):
    series = data[name]
    return data[series.notna() & series.ne("") & series.str.lower().ne("unknown")]


def severity(data, key):
    """Count observed outcomes; divide only by illnesses on reported rows.

    NOTE: these are reported-outcome case ratios, not unbiased population risks.
    """
    groups = []
    for label, sub in data.groupby(key):
        hosp = sub[sub["Hospitalizations"].notna() & sub["Illnesses"].gt(0)]
        deaths = sub[sub["Fatalities"].notna() & sub["Illnesses"].gt(0)]
        groups.append({
            key: label,
            "Outbreaks": len(sub),
            "Illnesses": sub["Illnesses"].sum(),
            "Hospitalizations": sub["Hospitalizations"].sum(min_count=1),
            "Fatalities": sub["Fatalities"].sum(min_count=1),
            "Hospitalization_rate": (
                hosp["Hospitalizations"].sum() / hosp["Illnesses"].sum()
                if hosp["Illnesses"].sum() > 0 else float("nan")
            ),
            "Fatality_rate": (
                deaths["Fatalities"].sum() / deaths["Illnesses"].sum()
                if deaths["Illnesses"].sum() > 0 else float("nan")
            ),
            "Reported_hospitalization_events": len(hosp),
            "Reported_fatality_events": len(deaths),
        })
    return pd.DataFrame(groups)


def chart_layout(fig, height=390, left=25):
    fig.update_layout(
        height=height,
        margin=dict(l=left, r=25, t=35, b=35),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(size=12, color=NAVY),
        showlegend=False,
        hoverlabel=dict(bgcolor="#172C45", font_color="#FFFFFF"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(125,145,165,.15)", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def callout(lead, detail):
    st.markdown(
        '<div class="story-note"><strong>' + html.escape(lead) +
        '</strong> ' + html.escape(detail) + '</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### 🔬 Outbreak explorer")
    st.caption("CDC FDOSS · 1998–2015")
    page = st.radio(
        "Explore",
        ["01 · The big picture", "02 · Pathogen burden", "03 · Food & pathogen links", "04 · Where outbreaks happen"],
    )
    st.divider()
    year_range = st.slider(
        "Reporting years", 1998, 2015, value=(1998, 2015)
    )
    st.caption("The year filter updates every metric and chart.")
    st.divider()
    st.markdown("[View code and methodology](https://github.com/hyejeong0617/foodborne_outbreaks_eda)")
    st.caption("Descriptive analysis, not a prediction or causal risk model.")

data = load_data()
filtered = data[data["Year"].between(*year_range)].copy()
if filtered.empty:
    st.info("No records in the selected period.")
    st.stop()

PAGE_HEADINGS = {
    "01": (
        "What do 18 years of foodborne outbreaks reveal?",
        "Explore outbreak counts, illness burden, and seasonality across reporting years.",
    ),
    "02": (
        "Which pathogens cause the greatest disease burden?",
        "Compare reported illness counts and hospitalizations, then examine outcome-specific severity.",
    ),
    "03": (
        "Which foods and pathogens are reported together?",
        "Explore identified food vehicles and food–pathogen combinations in surveillance records.",
    ),
    "04": (
        "How does outbreak burden vary by setting?",
        "Compare average outbreak sizes and reported hospitalization outcomes across venues.",
    ),
}
section_key = page[:2]
page_title, page_description = PAGE_HEADINGS[section_key]
st.markdown(
    '<div class="portfolio-project-name">Foodborne Disease Outbreak Analysis</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-eyebrow">CDC FDOSS 1998–2015 · EXPLORATORY DATA ANALYSIS</div>',
    unsafe_allow_html=True,
)
st.title(page_title)
st.markdown(
    '<p class="hero-sub">' + html.escape(page_description) + '</p>',
    unsafe_allow_html=True,
)
st.caption("Selected reporting period: " + str(year_range[0]) + "–" + str(year_range[1]))
st.divider()

if page.startswith("01"):
    st.markdown(
        '<div class="section-caption">Outbreaks and illness burden over time</div>',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    a.metric("Reported outbreaks", f"{len(filtered):,}")
    b.metric("Reported illnesses", f"{filtered['Illnesses'].sum():,.0f}")
    c.metric("Jurisdictions represented", f"{filtered['State'].nunique():,}")

    annual = filtered.groupby("Year", as_index=False).agg(
        Outbreaks=("Illnesses", "size"), Illnesses=("Illnesses", "sum")
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=annual["Year"], y=annual["Outbreaks"], mode="lines+markers",
        line=dict(color=TEAL, width=3), marker=dict(size=7),
        hovertemplate="%{x}: %{y:,} outbreaks<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Year", yaxis_title="Outbreaks")
    st.plotly_chart(chart_layout(fig), use_container_width=True)
    if len(annual) >= 2:
        first, last = annual.iloc[0], annual.iloc[-1]
        pct = (last["Outbreaks"] / first["Outbreaks"] - 1) * 100 if first["Outbreaks"] else 0
        callout(
            f"{pct:+.1f}% change from {int(first['Year'])} to {int(last['Year'])}.",
            "This is a change in reported outbreaks, not evidence that individual exposure risk changed.",
        )

    with st.expander("Explore seasonal distribution"):
        monthly = filtered["Month"].value_counts().reindex(MONTHS, fill_value=0)
        fig_m = go.Figure(go.Bar(
            x=[m[:3] for m in MONTHS], y=monthly.values,
            marker_color=TEAL,
            hovertemplate="%{x}: %{y:,} outbreaks<extra></extra>",
        ))
        fig_m.update_layout(yaxis_title="Outbreaks")
        st.plotly_chart(chart_layout(fig_m, 270), use_container_width=True)

elif page.startswith("02"):
    st.caption("Compare the pathogens accounting for the most reported illnesses and hospitalizations.")
    path = severity(known(filtered, "Species_grouped"), "Species_grouped")
    if path.empty:
        st.info("No known pathogens in this period.")
    else:
        top = path.nlargest(6, "Illnesses")
        # Common categories; same pathogens are compared on two differently scaled metrics.
        choice = st.radio(
            "Rank pathogens by",
            ["Illnesses", "Hospitalizations"],
            horizontal=True,
        )
        ranked = path.nlargest(7, choice).sort_values(choice)
        fig = go.Figure(go.Bar(
            y=ranked["Species_grouped"], x=ranked[choice],
            orientation="h", marker_color=TEAL if choice == "Illnesses" else CORAL,
            hovertemplate="%{y}<br>%{x:,.0f} reported " + choice.lower() + "<extra></extra>",
        ))
        fig.update_layout(xaxis_title="Reported " + choice.lower(), yaxis_title="")
        st.plotly_chart(chart_layout(fig, 410, 35), use_container_width=True)
        leading = path.nlargest(1, choice).iloc[0]
        callout(
            f"Top pathogen by {choice.lower()}: {leading['Species_grouped']}.",
            "Rankings depend on the outcome chosen; missing hospitalizations are not treated as zero.",
        )

        st.markdown("#### Clinical severity among commonly reported pathogens")
        st.caption(
            "Hospitalizations ÷ illnesses, restricted to events with a recorded hospitalization "
            "outcome and positive illness count. Minimum 30 illnesses in reported-outcome events."
        )
        reported = (
            filtered[filtered["Hospitalizations"].notna() & filtered["Illnesses"].gt(0)]
            .groupby("Species_grouped")["Illnesses"].sum()
        )
        stable = path.copy()
        stable["Reported_illnesses"] = stable["Species_grouped"].map(reported).fillna(0)
        stable = stable[
            stable["Reported_illnesses"].ge(30) &
            stable["Hospitalization_rate"].notna() &
            stable["Species_grouped"].str.lower().ne("unknown")
        ].nlargest(5, "Hospitalization_rate").sort_values("Hospitalization_rate")
        if not stable.empty:
            fig_r = go.Figure(go.Bar(
                y=stable["Species_grouped"], x=stable["Hospitalization_rate"],
                orientation="h", marker_color=CORAL,
                text=[f"{x:.1%}" for x in stable["Hospitalization_rate"]],
                textposition="outside",
                hovertemplate="%{y}: %{x:.1%}<extra></extra>",
            ))
            fig_r.update_layout(xaxis_tickformat=".0%", xaxis_title="Hospitalization / reported illnesses", yaxis_title="")
            st.plotly_chart(chart_layout(fig_r, 330, 35), use_container_width=True)
        else:
            st.info("No pathogen meets the display threshold.")

elif page.startswith("03"):
    st.caption(
        "Reported food vehicles and food–pathogen combinations. "
        "These are surveillance associations, not causal attribution or individual risk estimates."
    )
    food = known(filtered, "Food_grouped")
    pathogen = known(filtered, "Species_grouped")
    both = known(food, "Species_grouped")
    a, b, c = st.columns(3)
    a.metric("Events with known food", f"{len(food):,}")
    b.metric("Events with known pathogen", f"{len(pathogen):,}")
    c.metric("Events with both known", f"{len(both):,}")
    st.caption(
        f"Food unknown or missing: {len(filtered) - len(food):,} events. "
        "Unknowns are excluded only from the corresponding category rankings."
    )

    st.markdown("#### Frequently reported food vehicles")
    top_food = food["Food_grouped"].value_counts().head(7).sort_values()
    if top_food.empty:
        st.info("No identified food vehicles in the selected years.")
    else:
        fig_food = go.Figure(go.Bar(
            y=top_food.index, x=top_food.values,
            orientation="h", marker_color=TEAL,
            hovertemplate="%{y}: %{x:,} outbreaks<extra></extra>",
        ))
        fig_food.update_layout(xaxis_title="Reported outbreaks", yaxis_title="")
        st.plotly_chart(chart_layout(fig_food, 350, 35), use_container_width=True)

    st.markdown("#### Food–pathogen combinations")
    metric = st.radio(
        "Compare combinations by", ["Outbreak count", "Reported illnesses"],
        horizontal=True, key="food_pair_metric",
    )
    if both.empty:
        st.info("No records have both an identified food vehicle and pathogen.")
    else:
        pairs = both.groupby(["Food_grouped", "Species_grouped"]).agg(
            Outbreaks=("Illnesses", "size"),
            Illnesses=("Illnesses", "sum"),
        ).reset_index()
        field = "Outbreaks" if metric == "Outbreak count" else "Illnesses"
        pair_top = pairs.nlargest(7, field).copy()
        pair_top["Pair"] = (
            pair_top["Food_grouped"].str.slice(0, 35) + " · " +
            pair_top["Species_grouped"].str.slice(0, 35)
        )
        pair_top = pair_top.sort_values(field)
        fig_pair = go.Figure(go.Bar(
            y=pair_top["Pair"], x=pair_top[field], orientation="h",
            marker_color=CORAL,
            customdata=pair_top[["Food_grouped", "Species_grouped"]].to_numpy(),
            hovertemplate=(
                "%{customdata[0]} + %{customdata[1]}<br>"
                "%{x:,} " + ("outbreaks" if field == "Outbreaks" else "illnesses") +
                "<extra></extra>"
            ),
        ))
        fig_pair.update_layout(xaxis_title=metric, yaxis_title="")
        st.plotly_chart(chart_layout(fig_pair, 390, 35), use_container_width=True)
        leader = pairs.nlargest(1, field).iloc[0]
        callout(
            f"Leading observed pair: {leader['Food_grouped']} + {leader['Species_grouped']}.",
            "The food field describes implicated food vehicles in reports; this does not "
            "identify the contaminated ingredient or prove a transmission mechanism.",
        )

elif page.startswith("04"):
    st.caption("Compare outbreak scale and hospitalization reporting across settings.")
    loc = known(filtered, "primary_location")
    profile = severity(loc, "primary_location")
    if profile.empty:
        st.info("No known outbreak settings in this period.")
    else:
        profile["Cases_per_event"] = profile["Illnesses"] / profile["Outbreaks"]
        profile["Venue"] = profile["primary_location"].map(VENUES).fillna(profile["primary_location"])
        selected = profile[
            profile["primary_location"].isin(VENUES) & profile["Outbreaks"].ge(8)
        ].copy()

        r1, r2, r3 = st.columns(3)
        if not selected.empty:
            largest = selected.nlargest(1, "Cases_per_event").iloc[0]
            r1.metric("Largest avg. event", f"{largest['Cases_per_event']:.0f} cases/event", help=largest["Venue"])
            r2.metric("Known-setting events", f"{len(loc):,}")
            r3.metric("Settings compared", str(len(selected)))

            selected = selected.sort_values("Cases_per_event")
            fig = go.Figure(go.Bar(
                y=selected["Venue"], x=selected["Cases_per_event"],
                orientation="h", marker_color=TEAL,
                text=[f"{x:.0f}" for x in selected["Cases_per_event"]],
                textposition="outside",
                hovertemplate="%{y}: %{x:.1f} cases/event<extra></extra>",
            ))
            fig.update_layout(xaxis_title="Mean reported illnesses per outbreak", yaxis_title="")
            st.plotly_chart(chart_layout(fig, 375), use_container_width=True)
            callout(
                "Outbreak size and clinical severity are distinct.",
                "A setting with larger events is not automatically associated with a higher hospitalization ratio.",
            )

            with st.expander("Compare reported hospitalization ratios by setting"):
                reported = (
                    loc[loc["Hospitalizations"].notna() & loc["Illnesses"].gt(0)]
                    .groupby("primary_location")["Illnesses"].sum()
                )
                rate = selected.copy()
                rate["Reported_illnesses"] = rate["primary_location"].map(reported).fillna(0)
                rate = rate[rate["Reported_illnesses"].ge(30) & rate["Hospitalization_rate"].notna()]
                rate = rate.sort_values("Hospitalization_rate")
                if not rate.empty:
                    fig_r = go.Figure(go.Bar(
                        y=rate["Venue"], x=rate["Hospitalization_rate"],
                        orientation="h", marker_color=CORAL,
                        text=[f"{x:.1%}" for x in rate["Hospitalization_rate"]],
                        textposition="outside",
                    ))
                    fig_r.update_layout(xaxis_tickformat=".0%", xaxis_title="Hospitalizations / reported illnesses", yaxis_title="")
                    st.plotly_chart(chart_layout(fig_r, 330), use_container_width=True)
                else:
                    st.info("Insufficient recorded outcomes for comparison.")
        else:
            st.info("No settings meet the minimum of eight outbreaks.")

st.divider()
with st.expander("Methods, data quality & limitations"):
    missing_h = filtered["Hospitalizations"].isna().sum()
    missing_f = filtered["Fatalities"].isna().sum()
    st.markdown(
        f"**Data source:** [CDC Foodborne Diseases dataset (Kaggle)]"
        "(https://www.kaggle.com/datasets/cdc/foodborne-diseases), 1998–2015. "
        "Rows represent distinct source records after the repository's documented audit. "
        f"Selected period: **{len(filtered):,} records**; "
        f"hospitalization outcome missing in **{missing_h:,}** records; "
        f"fatality outcome missing in **{missing_f:,}** records.\n\n"
        "**Cleaning:** Unknown food, species, and venue values are not invented. "
        "Missing outcome values remain NaN, not zero. "
        "**Clinical ratios:** only positive-illness events with the relevant outcome reported "
        "contribute to the numerator and denominator. Outcomes missing from surveillance "
        "can bias these descriptive ratios, and no clinical risk interpretation is warranted. "
        "**Other caveats:** reporting varies by jurisdiction and time; associations are "
        "not causal; outbreak counts are not incidence rates."
    )
st.caption("Portfolio project · Python · pandas · Plotly · Streamlit · Source: CDC FDOSS via Kaggle")
