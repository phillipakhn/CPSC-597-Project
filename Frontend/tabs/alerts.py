import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from config import FEATURE_EXPLANATIONS
from utils.helpers import generate_alert_message, make_download, recommended_action, short_reason
from utils.ui import hero, metric_card, section_panel


def render(ctx):
    data = ctx["data"]
    alerts_df = data.get("alerts_df")
    feature_importance_df = data.get("feature_importance_df")
    hero("Alert Center", "Prioritize suspicious traffic, tune severity thresholds, and inspect the highest-risk flows.")

    section_panel("Severity Controls", "Adjust these thresholds to control how aggressive the alert queue should be.")
    c1, c2, c3 = st.columns(3)
    with c1:
        medium_threshold = st.slider("Medium threshold", 0.50, 1.00, 0.90, 0.01)
    with c2:
        high_threshold = st.slider("High threshold", 0.50, 1.00, 0.93, 0.01)
    with c3:
        critical_threshold = st.slider("Critical threshold", 0.50, 1.00, 0.97, 0.01)

    if not (medium_threshold < high_threshold < critical_threshold):
        st.warning("Use ascending thresholds: Medium < High < Critical.")

    def custom_severity(prob):
        if pd.isna(prob):
            return "Unknown"
        if prob >= critical_threshold:
            return "Critical"
        if prob >= high_threshold:
            return "High"
        if prob >= medium_threshold:
            return "Medium"
        return "Low"

    if alerts_df is None or alerts_df.empty:
        st.warning("No saved alert records found.")
        return

    filtered_alerts = alerts_df.copy()
    if "Predicted_Label" in filtered_alerts.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["Predicted_Label"] == 1]
    if "Attack_Probability" in filtered_alerts.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["Attack_Probability"] >= medium_threshold]

    if filtered_alerts.empty:
        st.warning("No alerts meet the current threshold.")
        return

    top_feature_names = (
        feature_importance_df["Feature"].head(5).tolist()
        if feature_importance_df is not None and not feature_importance_df.empty
        else list(filtered_alerts.columns[:5])
    )

    if "Alert_Message" not in filtered_alerts.columns:
        filtered_alerts["Alert_Message"] = filtered_alerts.apply(lambda row: generate_alert_message(row, top_feature_names), axis=1)

    filtered_alerts["Severity"] = filtered_alerts["Attack_Probability"].apply(custom_severity)
    if "Predicted_Attack_Category" not in filtered_alerts.columns:
        filtered_alerts["Predicted_Attack_Category"] = "Unknown"
    if "Anomaly_Score" not in filtered_alerts.columns:
        filtered_alerts["Anomaly_Score"] = np.nan

    filtered_alerts["Recommended_Action"] = filtered_alerts["Severity"].apply(recommended_action)
    filtered_alerts["Why_Flagged"] = filtered_alerts.apply(lambda row: short_reason(row, top_feature_names), axis=1)
    filtered_alerts = filtered_alerts.sort_values(by="Attack_Probability", ascending=False).reset_index(drop=True)

    critical_count = int((filtered_alerts["Severity"] == "Critical").sum())
    high_count = int((filtered_alerts["Severity"] == "High").sum())
    medium_count = int((filtered_alerts["Severity"] == "Medium").sum())
    max_prob = filtered_alerts["Attack_Probability"].max()

    # summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Alerts", len(filtered_alerts), "Current threshold filter", "blue")
    with c2:
        metric_card("Critical", critical_count, "Immediate review", "red")
    with c3:
        metric_card("High", high_count, "Investigate soon", "orange")
    with c4:
        metric_card("Max Confidence", f"{max_prob:.3f}", f"Medium count: {medium_count}", "yellow")
        
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.05, 1])
    with left:
        severity_counts = filtered_alerts["Severity"].value_counts().reindex(["Critical", "High", "Medium", "Low"], fill_value=0)
        fig, ax = plt.subplots(figsize=(5.2, 3.0))
        ax.bar(severity_counts.index, severity_counts.values)
        ax.set_title("Alert Severity Breakdown", fontsize=11)
        ax.set_ylabel("Count", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig, width="content")
    with right:
        category_counts = filtered_alerts["Predicted_Attack_Category"].value_counts().head(8)
        fig, ax = plt.subplots(figsize=(5.2, 3.0))
        ax.barh(category_counts.index[::-1], category_counts.values[::-1])
        ax.set_title("Top Predicted Attack Categories", fontsize=11)
        ax.set_xlabel("Alerts", fontsize=9)
        fig.tight_layout()
        st.pyplot(fig, width="content")

    queue_cols = [c for c in [
        "Severity", "Attack_Probability", "Predicted_Label_Name", "Predicted_Attack_Category",
        "Anomaly_Score", "Recommended_Action", "Why_Flagged",
    ] if c in filtered_alerts.columns]

    st.markdown("### Priority Queue")
    queue_df = filtered_alerts[queue_cols].head(25).copy()
    selection = st.dataframe(
        queue_df,
        width="stretch",
        hide_index=False,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = selection["selection"]["rows"]
    selected_alert = filtered_alerts.iloc[selected_rows[0]] if selected_rows else filtered_alerts.iloc[0]

    # info cards
    st.markdown("### Alert Investigation")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        metric_card("Severity", selected_alert.get("Severity", "Unknown"), selected_alert.get("Recommended_Action", "Monitor"), "red" if selected_alert.get("Severity") == "Critical" else "orange")
    with d2:
        metric_card("Attack Prob.", f"{selected_alert.get('Attack_Probability', np.nan):.3f}", "Model confidence", "yellow")
    with d3:
        metric_card("Attack Category", str(selected_alert.get("Predicted_Attack_Category", "Unknown")), "Multi-class estimate", "purple")
    with d4:
        anomaly_val = selected_alert.get("Anomaly_Score", np.nan)
        metric_card("Anomaly Score", "N/A" if pd.isna(anomaly_val) else f"{anomaly_val:.3f}", "Higher is more suspicious", "blue")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### Analyst Notes")
        st.write("**Recommended action:**", selected_alert.get("Recommended_Action", "Monitor"))
        st.write("**Why flagged:**", selected_alert.get("Why_Flagged", "High model confidence"))
        st.markdown("**Alert summary**")
        st.code(selected_alert.get("Alert_Message", "No alert summary available."))
    with c2:
        feature_view = []
        for feature in top_feature_names:
            if feature in selected_alert.index:
                feature_view.append({
                    "Feature": str(feature),
                    "Value": str(selected_alert[feature]),
                    "Meaning": FEATURE_EXPLANATIONS.get(feature, "This feature contributed to the alert decision."),
                })
        st.markdown("#### Top Signals")
        if feature_view:
            st.dataframe(pd.DataFrame(feature_view), width="stretch", hide_index=True)
        else:
            st.info("No feature details available for this alert.")

    with st.expander("Full selected alert record"):
        st.dataframe(pd.DataFrame({"Field": selected_alert.index.astype(str), "Value": selected_alert.astype(str).values}), width="stretch", hide_index=True)

    make_download(filtered_alerts, "Download alert review CSV", "alert_review.csv")
