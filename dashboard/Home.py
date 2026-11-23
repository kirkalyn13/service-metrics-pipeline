import streamlit as st

st.set_page_config(
    page_title="Service Metrics",
    page_icon="📈",
    layout="wide",
)

def home():
    st.title("📈 Service Metrics Dashboard")
    st.markdown("""
    Welcome to the **Service Metrics Dashboard**, an analytics tool for monitoring
    and comparing network performance.

    **About the data:** This project uses **real-world network data** pulled from several
    years ago. **Sensitive details**, including actual locations and site names, have been
    **redacted** and replaced with anonymized values.

    Use the sidebar to navigate between dashboards.
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Networks Tracked", value="3")
    with col2:
        st.metric(label="Technology", value="4G, Fiber")

    st.divider()

    st.subheader("🔍 About the Pipeline")
    st.markdown("""
    A **locally hosted, end-to-end data pipeline** built for team use in analysing
    network service metrics. It ingests **raw network performance data**, transforms it
    through a series of stages, and presents it through an **interactive dashboard**
    accessible to the whole team over the local network.

    It is intentionally designed for **on-premises or internal-network deployment**, so
    network metrics stay within the organization's environment rather than being exposed
    through a public-facing application.

    📂 **See the pipeline details:** [service-metrics-pipeline on GitHub](https://github.com/kirkalyn13/service-metrics-pipeline)
    """)

    st.subheader("📋 Available Dashboards")
    st.markdown("""
    **📡 High Utilization**  
    Weekly summary report for sites with high PRB utilization.
    """)
    st.markdown("""
    **📶 Open Signal**  
    Time series analysis of download speed and latency per province,
    comparing network operators S and G over the last quarter.
    """)
    st.markdown("""
    **🏍️ Speed Test**  
    Time series analysis of Ookla download speed and latency per reported location.
    """)

pg = st.navigation([
    st.Page(home, title="Home", icon="🏠", default=True),
    st.Page("pages/high_utilization.py", title="High Utilization", icon="📡"),
    st.Page("pages/open_signal.py", title="Open Signal", icon="📶"),
    st.Page("pages/speed_test.py", title="Speed Test", icon="🏍️")
])

pg.run()