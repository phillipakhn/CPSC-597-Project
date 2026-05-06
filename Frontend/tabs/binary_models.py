import streamlit as st

from utils.ui import hero, metric_card

from utils.helpers import make_download
from utils.plotting import plot_confusion_from_labels, plot_metric_bar, plot_pr_curve, plot_roc_curve
from utils.predictions import predict_with_selected_model


def render(ctx):
    data = ctx["data"]
    selected_binary_model = ctx["selected_binary_model"]
    binary_results_df = data.get("binary_results_df")
    X_test_df = data.get("X_test_df")
    y_test_df = data.get("y_test_df")

    hero("Model Performance", "Compare binary detection models and inspect the selected model with confusion, ROC, and PR curves.")

    if binary_results_df is None or binary_results_df.empty:
        st.warning("No binary model comparison file found yet.")
        return

    metric_cols = [c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC"] if c in binary_results_df.columns]
    if metric_cols and "Model" in binary_results_df.columns:
        c1, c2, c3 = st.columns(3)
        best_f1 = binary_results_df.loc[binary_results_df["F1-Score"].idxmax()] if "F1-Score" in binary_results_df.columns else None
        best_auc = binary_results_df.loc[binary_results_df["ROC-AUC"].idxmax()] if "ROC-AUC" in binary_results_df.columns else None
        with c1:
            metric_card("Selected Model", selected_binary_model, "Used by interactive tabs", "blue")
        with c2:
            metric_card("Best F1", "N/A" if best_f1 is None else f"{best_f1['F1-Score']:.4f}", "N/A" if best_f1 is None else best_f1["Model"], "green")
        with c3:
            metric_card("Best ROC-AUC", "N/A" if best_auc is None else f"{best_auc['ROC-AUC']:.4f}", "N/A" if best_auc is None else best_auc["Model"], "purple")

    st.markdown("### Comparison Table")
    st.dataframe(binary_results_df.round(4), width="stretch", hide_index=True)
    metric_options = [c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "Training Time"] if c in binary_results_df.columns]
    metric = st.selectbox("Metric to visualize", metric_options, index=min(3, len(metric_options) - 1))
    plot_metric_bar(binary_results_df, metric)

    if X_test_df is not None and y_test_df is not None:
        preds, probs = predict_with_selected_model(selected_binary_model, data, X_test_df)
        y_true = y_test_df.iloc[:, 0]
        c1, c2, c3 = st.columns([1.1, 1, 1])
        with c1:
            if preds is not None:
                plot_confusion_from_labels(y_true, preds, selected_binary_model)
        with c2:
            if probs is not None:
                plot_roc_curve(y_true, probs, "ROC")
        with c3:
            if probs is not None:
                plot_pr_curve(y_true, probs, "PR")

    make_download(binary_results_df, "Download binary comparison CSV", "model_comparison.csv")
