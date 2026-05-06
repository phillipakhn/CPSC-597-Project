import matplotlib.pyplot as plt
import streamlit as st

from utils.plotting import plot_horizontal_importance
from utils.ui import hero


def render(ctx):
    data = ctx["data"]

    multiclass_results_df = data.get("multiclass_results_df")
    multiclass_feature_importance_df = data.get("multiclass_feature_importance_df")
    sample_end_to_end_df = data.get("sample_end_to_end_df")

    hero(
        "Attack Categories",
        "After traffic is flagged as suspicious, this stage estimates the likely attack family."
    )
    st.markdown("### Multi-Class Model Performance")

    if multiclass_results_df is not None and not multiclass_results_df.empty:
        st.dataframe(multiclass_results_df.round(4), width="stretch", hide_index=True)

        metric_cols = [
            c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "Training Time"]
            if c in multiclass_results_df.columns
        ]

        if metric_cols and "Model" in multiclass_results_df.columns:
            selected_metric = st.selectbox(
                "Metric to visualize",
                metric_cols,
                index=min(3, len(metric_cols) - 1),
                key="multiclass_metric_select",
            )

            fig, ax = plt.subplots(figsize=(5.8, 2.8))
            ax.bar(multiclass_results_df["Model"], multiclass_results_df[selected_metric])
            ax.set_title(f"{selected_metric} by Multi-Class Model", fontsize=11)
            ax.set_ylabel(selected_metric, fontsize=9)

            if selected_metric != "Training Time":
                ax.set_ylim(0, 1)

            ax.tick_params(axis="x", rotation=15, labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            st.pyplot(fig, width="content")
    else:
        st.warning("No multi-class comparison CSV found yet.")

    st.markdown("### Attack Category Predictions")

    if sample_end_to_end_df is None or sample_end_to_end_df.empty:
        st.warning("No sample end-to-end prediction file found yet.")
    elif "Predicted_Attack_Category" not in sample_end_to_end_df.columns:
        st.warning("The sample prediction file does not contain Predicted_Attack_Category.")
    else:
        prediction_df = sample_end_to_end_df.copy()
        prediction_df = prediction_df[
            prediction_df["Predicted_Attack_Category"].notna()
        ].copy()

        total_rows = len(prediction_df)
        category_counts = prediction_df["Predicted_Attack_Category"].value_counts()

        most_common_category = category_counts.index[0] if not category_counts.empty else "Unknown"
        most_common_count = int(category_counts.iloc[0]) if not category_counts.empty else 0

        avg_confidence = None
        if "MultiClass_Confidence" in prediction_df.columns:
            avg_confidence = prediction_df["MultiClass_Confidence"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows Classified", total_rows)
        c2.metric("Most Common Attack Type", most_common_category)
        c3.metric(
            "Average Confidence",
            "N/A" if avg_confidence is None else f"{avg_confidence:.3f}",
        )

        left, right = st.columns([1.1, 1])

        with left:
            st.markdown("#### Category Breakdown")
            category_df = category_counts.reset_index()
            category_df.columns = ["Attack Category", "Count"]
            st.dataframe(category_df, width="stretch", hide_index=True)

        with right:
            fig, ax = plt.subplots(figsize=(5.4, 3.2))
            ax.barh(category_counts.index[::-1], category_counts.values[::-1])
            ax.set_title("Predicted Attack Categories", fontsize=11)
            ax.set_xlabel("Count", fontsize=9)
            fig.tight_layout()
            st.pyplot(fig, width="content")

        st.markdown("### High-Confidence Attack Type Predictions")
        st.caption("These rows show which attack family the model believes each suspicious flow belongs to.")

        preview_cols = [
            c for c in [
                "RF_Prediction",
                "RF_Attack_Probability",
                "Predicted_Attack_Category",
                "MultiClass_Confidence",
                "Anomaly_Prediction",
                "Anomaly_Score",
            ]
            if c in prediction_df.columns
        ]

        display_df = prediction_df[preview_cols].copy()

        if "MultiClass_Confidence" in display_df.columns:
            display_df = display_df.sort_values(
                by="MultiClass_Confidence",
                ascending=False,
            )

        st.dataframe(display_df.head(25), width="stretch", hide_index=True)

        st.markdown("### Attack Category Drilldown")

        categories = sorted(prediction_df["Predicted_Attack_Category"].dropna().unique().tolist())

        if categories:
            selected_category = st.selectbox(
                "Select an attack category to inspect",
                categories,
                key="selected_multiclass_category",
            )

            selected_df = prediction_df[
                prediction_df["Predicted_Attack_Category"] == selected_category
            ].copy()

            c1, c2, c3 = st.columns(3)
            c1.metric("Matching Rows", len(selected_df))

            if "MultiClass_Confidence" in selected_df.columns:
                c2.metric("Avg Category Confidence", f"{selected_df['MultiClass_Confidence'].mean():.3f}")
                c3.metric("Max Category Confidence", f"{selected_df['MultiClass_Confidence'].max():.3f}")
            else:
                c2.metric("Avg Category Confidence", "N/A")
                c3.metric("Max Category Confidence", "N/A")

            st.dataframe(selected_df[preview_cols].head(20), width="stretch", hide_index=True)

    st.markdown("### Features Used for Attack-Type Separation")
    st.caption(
        "These are the features the multi-class model used most when separating one attack family from another."
    )

    if multiclass_feature_importance_df is not None and not multiclass_feature_importance_df.empty:
        top_multi = multiclass_feature_importance_df.head(12)

        c1, c2 = st.columns([1.15, 1])

        with c1:
            st.dataframe(top_multi, width="stretch", hide_index=True)

        with c2:
            plot_horizontal_importance(
                top_multi,
                "Feature",
                "Importance",
                "Top multi-class features",
                "Importance",
            )
    else:
        st.warning("No multi-class feature importance CSV found yet.")

    with st.expander("How to explain this tab"):
        st.write(
            "This tab shows the second stage of the IDS pipeline. "
            "The binary model flags suspicious traffic, then the multi-class model estimates the likely attack type. "
            "This gives the analyst more context than a simple attack/not-attack result."
        )