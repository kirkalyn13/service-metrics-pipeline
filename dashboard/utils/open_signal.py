import pandas as pd

def generate_notes(df: pd.DataFrame, col: str) -> dict:
    """Generate S vs G metric behavior notes"""
    notes = {}
    for province, pdf in df.groupby("province"):
        province_notes = []
        pdf = pdf.sort_values("report_end_date")

        # Check if S has decreasing values over last 3 weeks
        s_data = pdf[pdf["network_name"] == "S"][col].tail(3).values
        if len(s_data) == 3 and s_data[0] > s_data[1] > s_data[2]:
            province_notes.append(f"⚠️ **S** {get_metric_name(col)} has been decreasing over the last 3 weeks.")

        # Check if G is higher than S in the latest week
        latest = pdf[pdf["report_end_date"] == pdf["report_end_date"].max()]
        s_latest = latest[latest["network_name"] == "S"][col].values
        g_latest = latest[latest["network_name"] == "G"][col].values
        if len(s_latest) and len(g_latest):
            if g_latest[0] > s_latest[0]:
                province_notes.append(f"📊 **G** {get_metric_name(col)} is outperforming **S** in the latest week.")

        if province_notes:
            notes[province] = province_notes

    return notes

def get_metric_name(col: str):
    if col == "download_mean":
        return "download speed"
    if col == "latency_mean":
        return "latency"
    return col