import matplotlib.pyplot as plt
import streamlit as st

from utils.ui import hero, section_panel


def render(ctx):
    drift_df = ctx["data"].get("drift_df")
    hero(
        "Concept Drift",
        "Check whether model performance stays stable across sequential chunks of test traffic."
    )

    if drift_df is None or drift_df.empty:
        st.warning("No concept_drift_results.csv found yet.")
        return

    metric_options = [c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC"] if c in drift_df.columns]
    drift_metric = st.selectbox("Metric", metric_options, index=3 if len(metric_options) > 3 else 0)

    c1, c2 = st.columns([1.05, 1])
    with c1:
        st.dataframe(drift_df.round(4), width="stretch", hide_index=True)
    with c2:
        fig, ax = plt.subplots(figsize=(5.4, 3.1))
        ax.plot(drift_df["Test_Chunk"], drift_df[drift_metric], marker="o")
        ax.set_title(f"{drift_metric} across chunks", fontsize=11)
        ax.set_xlabel("Test Chunk", fontsize=9)
        ax.set_ylabel(drift_metric, fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig, width="content")

    section_panel("How to read this", "If later chunks drop, the model may be struggling with changing traffic behavior.")
