import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from db import get_engine, PG_SCHEMA

# Config
TABLE       = "open_signal_4g"
WEEKS       = 13

METRICS = {
    "Download Speed (Mbps)":  "download_mean",
    "Latency (ms)":           "latency_mean",
}

COLOR_MAP = {"S":"#4CAF50", "G":"#2196F3"}

# Data
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = get_engine()
    cutoff = date.today() - timedelta(weeks=WEEKS)
    query  = f"""
        SELECT report_end_date, network_name, province, download_mean, latency_mean
        FROM {PG_SCHEMA}.{TABLE}
        ORDER BY report_end_date
    """
    return pd.read_sql(query, engine)


# Layout
st.title("📶 Open Signal — Network Performance")
st.caption("4G · All networks compared")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not connect to database: {e}")
    st.stop()

if df.empty:
    st.warning("No data found for the last 13 weeks.")
    st.stop()

# Metric selector
selected_label = st.selectbox("Metric", list(METRICS.keys()))
selected_col   = METRICS[selected_label]

st.divider()

# Time series chart
fig = px.line(
    df,
    x="report_end_date",
    y=selected_col,
    color="network_name",
    facet_row="province",
    facet_row_spacing=0.02,
    color_discrete_map=COLOR_MAP,
    markers=True,
    labels={
        "report_end_date": "Week",
        selected_col:      selected_label,
        "network_name":    "Network",
    },
    title=f"{selected_label} — Operator Comparison by Province (Last 13 Weeks)",
    color_discrete_sequence=px.colors.qualitative.Set2,
)

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    height=500 * ((len(df["province"].unique()) // 3) + 1),  # dynamic based on rows
    legend_title_text="Network",
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
)

fig.for_each_annotation(lambda a: a.update(
    text=a.text.split("=")[-1],
    textangle=0,
))

fig.for_each_xaxis(lambda x: x.update(showgrid=False))
fig.for_each_yaxis(lambda y: y.update(gridcolor="rgba(200,200,200,0.2)"))

st.plotly_chart(fig, use_container_width=True)

# Raw data toggle
with st.expander("View raw data"):
    st.dataframe(
        df.sort_values(["report_end_date", "network_name"], ascending=[False, True]),
        use_container_width=True,
    )