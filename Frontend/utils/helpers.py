import numpy as np
import pandas as pd
import streamlit as st


def make_download(df: pd.DataFrame, label: str, filename: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name=filename, mime="text/csv")


def label_name_from_binary(value: int) -> str:
    return "ATTACK" if int(value) == 1 else "BENIGN"


def severity_from_probability(prob: float) -> str:
    if pd.isna(prob):
        return "Unknown"
    if prob >= 0.97:
        return "Critical"
    if prob >= 0.93:
        return "High"
    return "Medium"


def recommended_action(severity):
    if severity == "Critical":
        return "Immediate review"
    if severity == "High":
        return "Investigate soon"
    return "Monitor"


def generate_alert_message(row: pd.Series, top_features) -> str:
    details = []
    for feature in top_features:
        if feature in row.index:
            value = row[feature]
            if pd.api.types.is_numeric_dtype(pd.Series([value])):
                details.append(f"{feature}={float(value):.2f}")
            else:
                details.append(f"{feature}={value}")
    return (
        f"ALERT | Confidence={row.get('Attack_Probability', np.nan):.3f} | "
        f"Class={row.get('Predicted_Label_Name', 'UNKNOWN')} | "
        f"Top signals: {', '.join(details)}"
    )


def short_reason(row, top_feature_names):
    reasons = []
    for feature in top_feature_names[:3]:
        if feature in row.index:
            value = row[feature]
            if pd.api.types.is_numeric_dtype(pd.Series([value])):
                reasons.append(f"{feature}={float(value):.2f}")
            else:
                reasons.append(f"{feature}={value}")
    return " | ".join(reasons) if reasons else "High model confidence"


def build_workflow_guide():
    return pd.DataFrame({
        "Step": [1, 2, 3, 4],
        "What to do": [
            "Open Binary Models to show overall performance.",
            "Open Alert Center to show how suspicious flows become analyst-friendly alerts.",
            "Use What-If Simulation to change important features and show the prediction move.",
            "Use Upload & Predict with a CSV to run end-to-end inference.",
        ],
        "Why it matters": [
            "Shows the baseline comparison between models.",
            "Shows how the model helps identify which alerts should be reviewed first.",
            "Shows the system is interactive instead of static.",
            "Shows the system works on new data, not only notebook samples.",
        ],
    })
