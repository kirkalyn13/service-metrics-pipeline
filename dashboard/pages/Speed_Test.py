import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from db import get_engine, PG_SCHEMA
from utils.open_signal import generate_notes

# Config
TABLE       = "speed_test"
HOURS       = 72

METRICS = {
    "Download Speed (Mbps)":  "download_speed_mbps",
    "Latency (ms)":           "idle_latency_ms",
}

# Data
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    engine = get_engine()
    query  = f"""
        SELECT timestamp, location, isp, ip, download_speed_mbps, idle_latency_ms
        FROM {PG_SCHEMA}.{TABLE}
        ORDER BY timestamp
    """
    return pd.read_sql(query, engine)


# Layout
st.title("🏍️ Speed Test — Network Performance")
st.caption("Ookla Speed Test Recording")
st.set_page_config(
    page_title="Speed Test",
    page_icon="🏍️",
    layout="wide",
)

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

# Province filter
all_locations = sorted(df["location"].unique())
st.markdown("""
    <style>
    [data-baseweb="tag"] {
        background-color: #4CAF50 !important;
    }
    </style>
""", unsafe_allow_html=True)
selected_locations = st.multiselect(
    "Province",
    options=all_locations,
    default=all_locations,
)

df = df[df["location"].isin(selected_locations)]

st.divider()

# Time series chart
fig = px.line(
    df,
    x="timestamp",
    y=selected_col,
    color="isp",
    facet_row="location",
    facet_row_spacing=0.02,
    markers=True,
    labels={
        "timestamp": "Timestamp",
        selected_col:      selected_label,
        "isp":    "Network",
    },
    title=f"{selected_label} — Operator Comparison by Province (Last 13 Weeks)",
    color_discrete_sequence=px.colors.qualitative.Set2,
)

fig.update_layout(
    title=dict(
        text=f"<b>{selected_label}</b> — Operator Comparison by Province (Last 13 Weeks)",
        pad=dict(b=30),  # margin below title
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    height=500 * ((len(df["location"].unique()) // 3) + 1),  # dynamic based on rows
    legend_title_text="Network",
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
)

fig.for_each_annotation(lambda a: a.update(
    text=f"<b>{a.text.split('=')[-1]}</b>"
))

fig.for_each_xaxis(lambda x: x.update(showgrid=False))
fig.for_each_yaxis(lambda y: y.update(gridcolor="rgba(200,200,200,0.2)"))

st.plotly_chart(fig, use_container_width=True)

# Raw data toggle
st.subheader("📋 Raw Data")
with st.expander("View raw data"):
    st.dataframe(
        df.sort_values(["timestamp", "isp"], ascending=[False, True]),
        use_container_width=True,
    )