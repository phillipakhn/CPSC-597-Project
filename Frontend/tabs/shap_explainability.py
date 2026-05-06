import streamlit as st

from utils.plotting import plot_horizontal_importance
from utils.ui import hero


def render(ctx):
    data = ctx["data"]
    shap_importance_df = data.get("shap_importance_df")
    sample_explanations_df = data.get("sample_explanations_df")

    hero(
        "Explainability",
        "Use SHAP results to show which network-flow features had the strongest influence on suspicious predictions."
    )

    if shap_importance_df is None or shap_importance_df.empty:
        st.warning("No SHAP feature importance file found yet.")
    else:
        top_shap = shap_importance_df.head(12)
        c1, c2 = st.columns([1.15, 1])
        with c1:
            st.dataframe(top_shap, width="stretch", hide_index=True)
        with c2:
            plot_horizontal_importance(top_shap, "Feature", "MeanAbsSHAP", "Top SHAP features", "Mean |SHAP|")

    if sample_explanations_df is not None and not sample_explanations_df.empty:
        with st.expander("Sample prediction explanations"):
            preview_cols = [c for c in ["Predicted_Label", "Attack_Probability", "Predicted_Label_Name"] if c in sample_explanations_df.columns]
            st.dataframe(sample_explanations_df[preview_cols].head(15), width="stretch")
