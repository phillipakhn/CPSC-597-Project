import os
import warnings

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve, average_precision_score
from sklearn.exceptions import InconsistentVersionWarning

st.set_page_config(
    page_title="Network Intrusion Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
)

# -----------------------------
# Paths
# -----------------------------
DEFAULT_BASE_PATHS = [
    "/home/phillip/IDS_Project",
    "/content/drive/MyDrive/Spring 2026/IDS_Project",
    "C:/Users/phill/Desktop/IDS_Project",
]

EXPECTED_FILES = {
    "results": {
        "model_comparison": "results/model_comparison.csv",
        "feature_importance": "results/feature_importance.csv",
        "alerts": "results/high_confidence_alerts.csv",
        "concept_drift": "results/concept_drift_results.csv",
    },
    "models": {
        "random_forest": "models/random_forest_model.pkl",
        "logistic_regression": "models/logistic_regression_model.pkl",
        "scaler": "models/standard_scaler.pkl",
    },
    "data": {
        "x_test": "artifacts/X_test_sample.csv",
        "y_test": "artifacts/y_test_sample.csv",
    },
}

FEATURE_EXPLANATIONS = {
    "Avg Bwd Segment Size": "Average size of backward packets in the flow.",
    "Packet Length Std": "How much packet sizes vary within the flow.",
    "Packet Length Variance": "Variance of packet lengths. Higher values mean more spread.",
    "Max Packet Length": "Largest packet observed in the flow.",
    "Bwd Packet Length Std": "Variation in backward packet lengths.",
    "Bwd Packet Length Max": "Largest backward packet seen in the flow.",
    "Average Packet Size": "Average packet size over the flow.",
    "Bwd Packet Length Mean": "Average backward packet length.",
}

# -----------------------------
# Helpers
# -----------------------------
def discover_base_path() -> str:
    for path in DEFAULT_BASE_PATHS:
        if os.path.exists(path):
            return path
    return DEFAULT_BASE_PATHS[0]


def build_paths(base_path: str):
    resolved = {}
    for section, files in EXPECTED_FILES.items():
        resolved[section] = {key: os.path.join(base_path, rel) for key, rel in files.items()}
    return resolved


@st.cache_data
def load_csv(path: str):
    if path and os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_resource
def load_pickle(path: str):
    if not path or not os.path.exists(path):
        return None, None

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", InconsistentVersionWarning)
            obj = joblib.load(path)

        version_warning = None
        for warning in caught:
            if issubclass(warning.category, InconsistentVersionWarning):
                version_warning = str(warning.message)
                break

        return obj, version_warning
    except Exception as exc:
        return None, f"Could not load {os.path.basename(path)}: {exc}"


def file_status_table(paths: dict) -> pd.DataFrame:
    rows = []
    for section, files in paths.items():
        for name, path in files.items():
            rows.append(
                {
                    "Section": section,
                    "Artifact": name,
                    "Path": path,
                    "Found": os.path.exists(path),
                }
            )
    return pd.DataFrame(rows)


def get_probabilities(model, X: pd.DataFrame, scaler=None):
    if model is None or X is None or X.empty:
        return None, None

    X_used = X.copy()

    model_name = model.__class__.__name__.lower()
    needs_scaling = "logistic" in model_name and scaler is not None
    if needs_scaling:
        X_used = scaler.transform(X_used)

    preds = model.predict(X_used)
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_used)[:, 1]
    else:
        probs = None
    return preds, probs


def plot_metric_bar(df: pd.DataFrame, metric: str):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["Model"], df[metric])
    ax.set_title(f"{metric} by Model")
    ax.set_ylabel(metric)
    ax.set_ylim(0, 1 if metric != "Training Time" else max(df[metric].max() * 1.15, 1))
    ax.tick_params(axis="x", rotation=15)
    st.pyplot(fig)


def plot_confusion_from_labels(y_true, y_pred, title: str):
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["BENIGN", "ATTACK"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title)
    st.pyplot(fig)


def plot_roc_curve(y_true, y_score, title: str):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)


def plot_pr_curve(y_true, y_score, title: str):
    precision, recall, _ = precision_recall_curve(y_true, y_score)
    ap = average_precision_score(y_true, y_score)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(recall, precision, label=f"AP = {ap:.4f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)


def generate_alert_message(row: pd.Series, top_features: list[str]) -> str:
    details = []
    for feature in top_features:
        if feature in row.index:
            value = row[feature]
            if pd.api.types.is_numeric_dtype(pd.Series([value])):
                details.append(f"{feature}={float(value):.2f}")
            else:
                details.append(f"{feature}={value}")
    return (
        f"ALERT: Possible network attack detected | "
        f"Confidence={row.get('Attack_Probability', np.nan):.3f} | "
        f"Predicted={row.get('Predicted_Label_Name', 'UNKNOWN')} | "
        f"Observed values: {', '.join(details)}"
    )


def make_download(df: pd.DataFrame, label: str, filename: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name=filename, mime="text/csv")


# -----------------------------
# Sidebar
# -----------------------------
st.title("Network Intrusion Detection Dashboard")
st.caption("Streamlit interface for your anomaly detection project using the CIC-IDS2017 workflow.")

with st.sidebar:
    st.header("Configuration")
    base_path = st.text_input("Project base path", value=discover_base_path())
    paths = build_paths(base_path)
    selected_model_name = st.selectbox(
        "Interactive model",
        ["Random Forest", "Logistic Regression"],
        index=0,
    )
    alert_threshold = st.slider("Alert threshold", 0.50, 0.99, 0.90, 0.01)
    st.markdown("---")
    st.subheader("Artifact status")
    status_df = file_status_table(paths)
    st.dataframe(status_df[["Artifact", "Found"]], width="stretch", hide_index=True)

# Load artifacts
results_df = load_csv(paths["results"]["model_comparison"])
feature_importance_df = load_csv(paths["results"]["feature_importance"])
alerts_df = load_csv(paths["results"]["alerts"])
drift_df = load_csv(paths["results"]["concept_drift"])
X_test_df = load_csv(paths["data"]["x_test"])
y_test_df = load_csv(paths["data"]["y_test"])
rf_model, rf_model_warning = load_pickle(paths["models"]["random_forest"])
log_model, log_model_warning = load_pickle(paths["models"]["logistic_regression"])
scaler, scaler_warning = load_pickle(paths["models"]["scaler"])

load_warnings = [w for w in [rf_model_warning, log_model_warning, scaler_warning] if w]

model_lookup = {
    "Random Forest": rf_model,
    "Logistic Regression": log_model,
}
active_model = model_lookup[selected_model_name]

# -----------------------------
# Top summary
# -----------------------------
if results_df is not None and not results_df.empty:
    c1, c2, c3, c4 = st.columns(4)
    best_f1_row = results_df.loc[results_df["F1-Score"].idxmax()]
    best_auc_row = results_df.loc[results_df["ROC-AUC"].idxmax()]
    c1.metric("Models compared", len(results_df))
    c2.metric("Best F1 model", best_f1_row["Model"])
    c3.metric("Best F1", f"{best_f1_row['F1-Score']:.4f}")
    c4.metric("Best ROC-AUC", f"{best_auc_row['ROC-AUC']:.4f}")
else:
    st.info("The app is ready, but it needs saved artifacts from the notebook to show real project outputs.")

if load_warnings:
    with st.expander("Model loading notes", expanded=True):
        for warning_text in load_warnings:
            st.warning(warning_text)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Model Comparison",
    "Feature Importance",
    "Alert Simulation",
    "What-If Attack Test",
    "Concept Drift",
    "Upload & Predict"
])

with tab1:
    st.subheader("Project Overview")
    st.write(
        "This dashboard presents the main parts of your network intrusion detection project: "
        "model comparison, feature importance, alert generation, interactive what-if testing, and concept drift analysis."
    )

    st.markdown("**Current workflow represented in the app**")
    st.markdown(
        "1. Load CIC-IDS2017 processed data  \n"
        "2. Clean NaN and infinite values  \n"
        "3. Convert labels into binary classes  \n"
        "4. Train baseline machine learning and deep learning models  \n"
        "5. Compare metrics and inspect behavior through alerts and drift"
    )

    st.subheader("Files the app expects")
    st.dataframe(status_df, width="stretch", hide_index=True)

    st.subheader("Notebook-to-app export checklist")
    st.code(
        """
results/model_comparison.csv
results/feature_importance.csv
results/high_confidence_alerts.csv
results/concept_drift_results.csv
models/random_forest_model.pkl
models/logistic_regression_model.pkl
models/standard_scaler.pkl
artifacts/X_test_sample.csv
artifacts/y_test_sample.csv
        """.strip(),
        language="text",
    )

with tab2:
    st.subheader("Model Comparison")
    if results_df is None or results_df.empty:
        st.warning("No model_comparison.csv found yet.")
    else:
        st.dataframe(results_df.round(4), width="stretch", hide_index=True)

        metric_options = [c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "Training Time"] if c in results_df.columns]
        metric = st.selectbox("Metric to visualize", metric_options, index=min(3, len(metric_options)-1))
        plot_metric_bar(results_df, metric)

        make_download(results_df, "Download comparison CSV", "model_comparison.csv")

        if X_test_df is not None and y_test_df is not None and active_model is not None:
            y_true = y_test_df.iloc[:, 0]
            preds, probs = get_probabilities(active_model, X_test_df, scaler=scaler)
            if preds is not None:
                plot_confusion_from_labels(y_true, preds, f"{selected_model_name} - Confusion Matrix")
            if probs is not None:
                c1, c2 = st.columns(2)
                with c1:
                    plot_roc_curve(y_true, probs, f"{selected_model_name} - ROC Curve")
                with c2:
                    plot_pr_curve(y_true, probs, f"{selected_model_name} - Precision-Recall Curve")
        else:
            st.caption("To show confusion matrix, ROC, and PR curves here, save a test sample plus trained model files.")

with tab3:
    st.subheader("Random Forest Feature Importance")
    if feature_importance_df is None or feature_importance_df.empty:
        st.warning("No feature_importance.csv found yet.")
    else:
        top_n = st.slider("Top features to show", 5, 30, 15)
        top_features = feature_importance_df.head(top_n)
        st.dataframe(top_features, width="stretch", hide_index=True)

        fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
        ax.barh(top_features["Feature"][::-1], top_features["Importance"][::-1])
        ax.set_title("Top Feature Importance")
        ax.set_xlabel("Importance")
        st.pyplot(fig)

        st.subheader("Plain-English explanations")
        explanations = []
        for feature in top_features["Feature"].head(8):
            explanations.append(
                {
                    "Feature": feature,
                    "Meaning": FEATURE_EXPLANATIONS.get(feature, "This feature captures flow or packet behavior that helps separate benign traffic from attacks."),
                }
            )
        st.dataframe(pd.DataFrame(explanations), width="stretch", hide_index=True)

with tab4:
    st.subheader("Alert Simulation")
    if alerts_df is not None and not alerts_df.empty:
        filtered_alerts = alerts_df.copy()
        if "Predicted_Label" in filtered_alerts.columns:
            filtered_alerts = filtered_alerts[filtered_alerts["Predicted_Label"] == 1]
        if "Attack_Probability" in filtered_alerts.columns:
            filtered_alerts = filtered_alerts[filtered_alerts["Attack_Probability"] >= alert_threshold]

        st.write(f"Showing {len(filtered_alerts)} alerts at threshold ≥ {alert_threshold:.2f}")

        if feature_importance_df is not None and not feature_importance_df.empty:
            top_feature_names = feature_importance_df["Feature"].head(5).tolist()
        else:
            top_feature_names = [c for c in filtered_alerts.columns[:5]]

        if not filtered_alerts.empty:
            preview_df = filtered_alerts.head(50).copy()
            preview_df["Alert_Message"] = preview_df.apply(lambda row: generate_alert_message(row, top_feature_names), axis=1)
            st.dataframe(preview_df, width="stretch")
            make_download(filtered_alerts, "Download filtered alerts", "high_confidence_alerts_filtered.csv")
        else:
            st.warning("No alerts meet the current threshold.")
    else:
        st.warning("No high_confidence_alerts.csv found yet.")

with tab5:
    st.subheader("What-If Attack Test")
    st.write(
        "Modify a sample flow and see whether the selected model becomes more or less confident that it is an attack."
    )

    if X_test_df is None or X_test_df.empty or active_model is None:
        st.warning("This section needs X_test_sample.csv and a saved model file.")
    else:
        sample_index = st.number_input("Sample index", min_value=0, max_value=max(len(X_test_df) - 1, 0), value=0, step=1)
        original_row = X_test_df.iloc[int(sample_index)].copy()
        editable_features = original_row.index.tolist()

        default_features = editable_features[:3]
        if feature_importance_df is not None and not feature_importance_df.empty:
            preferred = [f for f in feature_importance_df["Feature"].head(8).tolist() if f in editable_features]
            if preferred:
                default_features = preferred[:3]

        selected_features = st.multiselect("Features to modify", editable_features, default=default_features)
        modified_row = original_row.copy()

        cols = st.columns(2)
        for idx, feature in enumerate(selected_features):
            current_value = float(original_row[feature])
            new_value = cols[idx % 2].number_input(
                f"{feature}",
                value=current_value,
                format="%.6f",
                key=f"change_{feature}",
            )
            modified_row[feature] = new_value

        original_df = pd.DataFrame([original_row])
        modified_df = pd.DataFrame([modified_row])

        original_pred, original_prob = get_probabilities(active_model, original_df, scaler=scaler)
        modified_pred, modified_prob = get_probabilities(active_model, modified_df, scaler=scaler)

        result_df = pd.DataFrame(
            {
                "Version": ["Original", "Modified"],
                "Predicted_Label": [int(original_pred[0]), int(modified_pred[0])],
                "Predicted_Label_Name": [
                    "ATTACK" if int(original_pred[0]) == 1 else "BENIGN",
                    "ATTACK" if int(modified_pred[0]) == 1 else "BENIGN",
                ],
                "Attack_Probability": [
                    float(original_prob[0]) if original_prob is not None else np.nan,
                    float(modified_prob[0]) if modified_prob is not None else np.nan,
                ],
            }
        )
        st.dataframe(result_df, width="stretch", hide_index=True)

        compare_df = pd.DataFrame({
            "Feature": selected_features,
            "Original": [original_row[f] for f in selected_features],
            "Modified": [modified_row[f] for f in selected_features],
        })
        st.dataframe(compare_df, width="stretch", hide_index=True)

with tab6:
    st.subheader("Concept Drift")
    if drift_df is None or drift_df.empty:
        st.warning("No concept_drift_results.csv found yet.")
    else:
        st.dataframe(drift_df.round(4), width="stretch", hide_index=True)
        metric_options = [c for c in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC"] if c in drift_df.columns]
        drift_metric = st.selectbox("Drift metric", metric_options, index=3 if len(metric_options) > 3 else 0)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(drift_df["Test_Chunk"], drift_df[drift_metric], marker="o")
        ax.set_title(f"{drift_metric} Across Sequential Chunks")
        ax.set_xlabel("Test Chunk")
        ax.set_ylabel(drift_metric)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        st.write(
            "If the metric drops as the test chunk gets farther from the training chunk, that suggests the model is struggling with changing traffic patterns over time."
        )
        
with tab7:

    st.subheader("Upload Network Traffic CSV")

    uploaded_file = st.file_uploader(
        "Upload CSV with same features as training data",
        type=["csv"]
    )

    if uploaded_file is not None:

        user_df = pd.read_csv(uploaded_file)

        st.write("Uploaded data preview")
        st.dataframe(user_df.head())

        try:

            preds, probs = get_probabilities(
                active_model,
                user_df,
                scaler=scaler
            )

            results_df = user_df.copy()

            results_df["Prediction"] = preds

            if probs is not None:
                results_df["Attack Probability"] = probs

            results_df["Label"] = results_df["Prediction"].map({
                0: "BENIGN",
                1: "ATTACK"
            })

            st.subheader("Prediction Results")

            st.dataframe(results_df.head(50))

            attack_count = (results_df["Prediction"] == 1).sum()

            st.metric(
                "Detected Attacks",
                attack_count
            )

            make_download(
                results_df,
                "Download predictions",
                "predictions.csv"
            )

        except Exception as e:

            st.error(
                "Error processing file. Make sure the CSV has the same features used in training."
            )

            st.write(str(e))
