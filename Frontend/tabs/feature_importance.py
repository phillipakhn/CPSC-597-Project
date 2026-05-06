import pandas as pd
import streamlit as st

from config import FEATURE_EXPLANATIONS
from utils.plotting import plot_horizontal_importance


def render(ctx):
    feature_importance_df = ctx["data"].get("feature_importance_df")
    st.subheader("Feature Importance")
    st.caption("This shows which traffic features matter most in the Random Forest decisions.")

    if feature_importance_df is None or feature_importance_df.empty:
        st.warning("No feature_importance.csv found yet.")
        return

    top_features = feature_importance_df.head(12)
    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.dataframe(top_features, width="stretch", hide_index=True)
        explanations = [{
            "Feature": feature,
            "Meaning": FEATURE_EXPLANATIONS.get(feature, "This feature captures flow or packet behavior that helps separate benign traffic from attacks."),
        } for feature in top_features["Feature"].head(8)]
        st.dataframe(pd.DataFrame(explanations), width="stretch", hide_index=True)
    with c2:
        plot_horizontal_importance(top_features, "Feature", "Importance", "Top binary features", "Importance")
