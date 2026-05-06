import numpy as np
import pandas as pd
import streamlit as st

from utils.helpers import label_name_from_binary
from utils.predictions import predict_with_selected_model
from utils.ui import hero


def render(ctx):
    data = ctx["data"]
    selected_binary_model = ctx["selected_binary_model"]
    X_test_df = data.get("X_test_df")
    what_if_features = data.get("what_if_features")

    hero(
        "What-If Simulation",
        "Change important traffic features and watch how the selected detection model responds."
    )

    if X_test_df is None or X_test_df.empty:
        st.warning("This section needs X_test_sample.csv.")
        return

    sample_index = st.number_input("Choose a sample row", min_value=0, max_value=max(len(X_test_df) - 1, 0), value=0, step=1)
    original_row = X_test_df.iloc[int(sample_index)].copy()
    editable_features = original_row.index.tolist()

    default_features = editable_features[:3]
    if what_if_features is not None:
        preferred = [f for f in what_if_features if f in editable_features]
        if preferred:
            default_features = preferred[:3]

    selected_features = st.multiselect(
        "Features to change",
        editable_features,
        default=default_features,
        help="Start with the top important features. Large changes should push the probability more noticeably.",
    )

    modified_row = original_row.copy()
    for feature in selected_features:
        modified_row[feature] = st.number_input(feature, value=float(original_row[feature]), format="%.6f", key=f"change_{feature}")

    original_df = pd.DataFrame([original_row])
    modified_df = pd.DataFrame([modified_row])
    orig_pred, orig_prob = predict_with_selected_model(selected_binary_model, data, original_df)
    mod_pred, mod_prob = predict_with_selected_model(selected_binary_model, data, modified_df)

    if orig_pred is not None and mod_pred is not None:
        delta = float(mod_prob[0] - orig_prob[0]) if orig_prob is not None and mod_prob is not None else np.nan
        c1, c2, c3 = st.columns(3)
        c1.metric("Original attack prob.", f"{float(orig_prob[0]):.3f}")
        c2.metric("Modified attack prob.", f"{float(mod_prob[0]):.3f}")
        c3.metric("Change", f"{delta:+.3f}")
        st.dataframe(pd.DataFrame({
            "Version": ["Original", "Modified"],
            "Predicted_Label": [int(orig_pred[0]), int(mod_pred[0])],
            "Predicted_Label_Name": [label_name_from_binary(orig_pred[0]), label_name_from_binary(mod_pred[0])],
            "Attack_Probability": [float(orig_prob[0]) if orig_prob is not None else np.nan, float(mod_prob[0]) if mod_prob is not None else np.nan],
        }), width="stretch", hide_index=True)

    compare_df = pd.DataFrame({
        "Feature": selected_features,
        "Original": [original_row[f] for f in selected_features],
        "Modified": [modified_row[f] for f in selected_features],
    })
    st.dataframe(compare_df, width="stretch", hide_index=True)
