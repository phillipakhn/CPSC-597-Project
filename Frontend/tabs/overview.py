import streamlit as st

from utils.ui import metric_card


def _best_metric(df, metric):
    if df is None or df.empty or metric not in df.columns:
        return "N/A", "No data"

    row = df.loc[df[metric].idxmax()]
    return f"{row[metric]:.4f}", str(row.get("Model", "Model"))


def render(ctx):
    data = ctx["data"]

    binary_df = data.get("binary_results_df")
    alerts_df = data.get("alerts_df")
    sample_df = data.get("sample_end_to_end_df")

    best_f1, best_model = _best_metric(binary_df, "F1-Score")
    best_auc, best_auc_model = _best_metric(binary_df, "ROC-AUC")

    st.markdown("### System Pipeline")

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        metric_card("Step 1", "Input Traffic", "CSV or PCAP network flow data", "blue")

    with r1c2:
        metric_card("Step 2", "Detect Attacks", "Binary attack / benign prediction", "red")

    with r1c3:
        metric_card("Step 3", "Classify Type", "Predicted attack category", "purple")
        
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        metric_card("Step 4", "Score Anomalies", "Isolation Forest behavior score", "yellow")

    with r2c2:
        metric_card("Step 5", "Explain Results", "SHAP and feature signals", "green")

    with r2c3:
        metric_card("Step 6", "Review Alerts", "Prioritized suspicious flows", "orange")
    

    st.markdown("### Best Model Performance")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Best F1", best_f1, best_model, "green")

    with c2:
        metric_card("Best ROC-AUC", best_auc, best_auc_model, "blue")

    with c3:
        metric_card(
            "Alert Records",
            0 if alerts_df is None else len(alerts_df),
            "Available for review",
            "red",
        )