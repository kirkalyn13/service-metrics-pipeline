import pandas as pd
import streamlit as st
import plotly.express as px
from db import get_engine, PG_SCHEMA

TABLE = "mart_high_utilization_nl"

st.set_page_config(
    page_title="High Utilization — NL",
    page_icon="📡",
    layout="wide",
)

@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = get_engine()
    query = f"""
        SELECT
            "week", "date", tech, vendor,
            site_name, cell_name, municipality, province, band,
            prb_utilization, rrc_user, payload,
            dl_user_throughput_kbps, ul_user_throughput_kbps,
            site_status, is_high_util
        FROM {PG_SCHEMA}.{TABLE}
        ORDER BY "date" DESC, site_name, cell_name
    """
    return pd.read_sql(query, engine)


st.title("📡 High Utilization — NL Area")
st.caption("Sites with at least one cell exceeding 90% PRB utilization · All cells shown per site")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not connect to database: {e}")
    st.stop()

if df.empty:
    st.warning("No high utilization sites found for NL.")
    st.stop()

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    weeks = sorted(df["week"].dropna().unique(), reverse=True)
    selected_week = st.selectbox("Week", weeks)

with col2:
    provinces = sorted(df["province"].dropna().unique())
    selected_provinces = st.multiselect("Province", provinces, default=provinces)

with col3:
    municipalities = sorted(
        df[df["province"].isin(selected_provinces)]["municipality"].dropna().unique()
    )
    selected_municipalities = st.multiselect("Municipality", municipalities, default=municipalities)

df = df[
    (df["week"] == selected_week) &
    (df["province"].isin(selected_provinces)) &
    (df["municipality"].isin(selected_municipalities))
]

st.divider()

# Summary cards
high_util_sites = df[df["is_high_util"]]["site_name"].nunique()
total_sites     = df["site_name"].nunique()
max_prb         = df["prb_utilization"].max()

m1, m2, m3 = st.columns(3)
m1.metric("Sites with >90% PRB", high_util_sites)
m2.metric("Total Sites in View", total_sites)
m3.metric("Peak PRB Utilization", f"{max_prb:.1f}%")

st.divider()

# High util cells table
st.subheader("🔴 Cells Exceeding 90% PRB Utilization")

breach_df = (
    df[df["is_high_util"]][[
        "site_name", "cell_name", "municipality", "province",
        "band", "prb_utilization", "site_status"
    ]]
    .sort_values("prb_utilization", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(
    breach_df.style.background_gradient(
        subset=["prb_utilization"], cmap="Reds", vmin=90, vmax=100
    ),
    use_container_width=True,
)

st.divider()

# Per-site cell breakdown
st.subheader("📊 Cell-Level Detail per Site")

selected_site = st.selectbox(
    "Select Site",
    options=sorted(df["site_name"].unique())
)

site_df = df[df["site_name"] == selected_site].sort_values("cell_name")

fig = px.bar(
    site_df,
    x="cell_name",
    y="prb_utilization",
    color="is_high_util",
    color_discrete_map={True: "#e53935", False: "#43a047"},
    labels={
        "cell_name":       "Cell",
        "prb_utilization": "PRB Utilization (%)",
        "is_high_util":    ">90%",
    },
    title=f"PRB Utilization — {selected_site}",
)
fig.add_hline(y=90, line_dash="dash", line_color="orange", annotation_text="90% threshold")
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="top", y=1.08, xanchor="right", x=1),
)
fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)", range=[0, 105])
st.plotly_chart(fig, use_container_width=True)

# Payload + RRC sub-metrics
c1, c2 = st.columns(2)

with c1:
    fig2 = px.bar(
        site_df, x="cell_name", y="payload", color="is_high_util",
        color_discrete_map={True: "#e53935", False: "#43a047"},
        labels={"cell_name": "Cell", "payload": "Payload", "is_high_util": ">90%"},
        title="Payload by Cell",
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig2.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    fig3 = px.bar(
        site_df, x="cell_name", y="rrc_user", color="is_high_util",
        color_discrete_map={True: "#e53935", False: "#43a047"},
        labels={"cell_name": "Cell", "rrc_user": "RRC Users", "is_high_util": ">90%"},
        title="RRC Users by Cell",
    )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig3.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Raw data
st.subheader("📋 Raw Data")
with st.expander("View full dataset"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True)