import streamlit as st

st.set_page_config(
    page_title="Service Metrics",
    page_icon="📈",
    layout="wide",

)

st.title("📈 Service Metrics Dashboard")
st.markdown("""
Welcome to the **Service Metrics Dashboard** — a local analytics tool for monitoring 
and comparing network performance.

Use the sidebar to navigate between dashboards.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Networks Tracked", value="3")
with col2:
    st.metric(label="Technology", value="4G, Fiber")

st.divider()

st.subheader("📋 Available Dashboards")
st.markdown("""
**📶 Open Signal**  
Time series analysis of download speed and latency per province, 
comparing network operators S and G over the last quarter.
""")
st.markdown("""
**🏍️ Speed Test**  
Time series analysis of Ookla download speed and latency per reported location.
""")