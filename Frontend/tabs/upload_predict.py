import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils.ui import hero
from utils.pcap_converter import convert_uploaded_pcap_to_csv, is_pcap_filename
from utils.helpers import make_download
from utils.predictions import (
    get_anomaly_predictions,
    get_binary_probabilities,
    get_dl_probabilities,
    get_multiclass_predictions,
)
from utils.preprocessing import (
    align_features_to_training,
    clean_uploaded_data,
    looks_like_old_cicids_schema,
)


def add_primary_prediction(results_df, selected_binary_model, rf_pred, rf_prob, log_pred, log_prob, dl_pred, dl_prob):
    if selected_binary_model == "Random Forest" and rf_pred is not None:
        results_df["Primary_Prediction"] = rf_pred
        results_df["Primary_Attack_Probability"] = rf_prob
    elif selected_binary_model == "Logistic Regression" and log_pred is not None:
        results_df["Primary_Prediction"] = log_pred
        results_df["Primary_Attack_Probability"] = log_prob
    elif selected_binary_model == "Deep Learning" and dl_pred is not None:
        results_df["Primary_Prediction"] = dl_pred
        results_df["Primary_Attack_Probability"] = dl_prob

    if "Primary_Prediction" in results_df.columns:
        results_df["Primary_Label"] = results_df["Primary_Prediction"].map({0: "BENIGN", 1: "ATTACK"})

    return results_df


def _plot_prediction_breakdown(results_df):
    cols = st.columns(2)

    with cols[0]:
        if "Primary_Label" in results_df.columns:
            counts = results_df["Primary_Label"].value_counts()
            fig, ax = plt.subplots(figsize=(5.4, 3.0))
            ax.bar(counts.index, counts.values)
            ax.set_title("Detection Results", fontsize=11)
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            st.pyplot(fig, width="content")

    with cols[1]:
        if "Primary_Attack_Probability" in results_df.columns:
            fig, ax = plt.subplots(figsize=(5.4, 3.0))
            ax.hist(results_df["Primary_Attack_Probability"].dropna(), bins=30)
            ax.set_title("Attack Probability Distribution", fontsize=11)
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            st.pyplot(fig, width="content")


def render(ctx):
    data = ctx["data"]
    selected_binary_model = ctx["selected_binary_model"]
    training_features = data.get("training_features")

    # header
    hero(
        "Upload & Predict",
        "Run intrusion detection on new network traffic (CSV or PCAP)."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or PCAP file",
        type=["csv", "pcap", "pcapng", "pcap_ISCX"],
    )

    if uploaded_file is None:
        st.info("Upload a file to begin.")
        return

    
    # Load file
    
    original_name = uploaded_file.name

    if is_pcap_filename(original_name):
        with st.spinner("Converting PCAP..."):
            csv_path, saved_csv_path = convert_uploaded_pcap_to_csv(
                uploaded_file,
                original_filename=original_name,
                project_root=ctx["base_path"],
                keep_csv=True,
            )
        st.success("PCAP converted.")
        user_df = pd.read_csv(csv_path)
    else:
        user_df = pd.read_csv(uploaded_file)

    # Preview (minimal)
    with st.expander("Preview data"):
        st.dataframe(user_df.head(), width="stretch")

    try:
        if training_features is None:
            st.error("Missing training features.")
            return

        if looks_like_old_cicids_schema(training_features):
            st.warning("Old feature schema detected. Retrain recommended.")


        # Preprocess

        user_df_clean = clean_uploaded_data(user_df)
        aligned_df, missing_cols, extra_cols = align_features_to_training(
            user_df_clean,
            training_features
        )

        # Metrics

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", len(aligned_df))
        c2.metric("Missing Features", len(missing_cols))
        c3.metric("Removed Columns", len(extra_cols))

        if missing_cols and len(missing_cols) / max(len(training_features), 1) > 0.10:
            st.warning("Too many missing features. Predictions may be unreliable.")

        # Predictions

        rf_pred, rf_prob = get_binary_probabilities(data.get("rf_model"), aligned_df)
        log_pred, log_prob = get_binary_probabilities(
            data.get("log_model"),
            aligned_df,
            scaler=data.get("standard_scaler"),
        )
        dl_pred, dl_prob = get_dl_probabilities(
            data.get("dl_model"),
            aligned_df,
            data.get("dl_scaler"),
        )

        results_df = aligned_df.copy()

        # Add predictions
        if rf_pred is not None:
            results_df["RF_Label"] = pd.Series(rf_pred).map({0: "BENIGN", 1: "ATTACK"})

        if log_pred is not None:
            results_df["LogReg_Label"] = pd.Series(log_pred).map({0: "BENIGN", 1: "ATTACK"})

        if dl_pred is not None:
            results_df["DL_Label"] = pd.Series(dl_pred).map({0: "BENIGN", 1: "ATTACK"})

        # Primary model
        results_df = add_primary_prediction(
            results_df,
            selected_binary_model,
            rf_pred, rf_prob,
            log_pred, log_prob,
            dl_pred, dl_prob,
        )

        # Multi-class
        if data.get("rf_multi_model") and data.get("multi_label_encoder"):
            multi_df = get_multiclass_predictions(
                data["rf_multi_model"],
                aligned_df,
                data["multi_label_encoder"]
            )
            results_df = pd.concat([results_df, multi_df], axis=1)

        # Anomaly
        if data.get("iso_model") and data.get("iso_scaler"):
            anomaly_df = get_anomaly_predictions(
                data["iso_model"],
                aligned_df,
                data["iso_scaler"]
            )
            results_df = pd.concat([results_df, anomaly_df], axis=1)

        st.subheader("Summary")

        attacks = int((results_df["Primary_Prediction"] == 1).sum())
        anomalies = int((results_df.get("Anomaly_Prediction", 0) == 1).sum())

        s1, s2, s3 = st.columns(3)
        s1.metric("Attacks", attacks)
        s2.metric("Anomalies", anomalies)
        s3.metric("Max Confidence", f"{results_df['Primary_Attack_Probability'].max():.3f}")

        # Charts
        _plot_prediction_breakdown(results_df)

        # Results table
        st.subheader("Predictions")

        display_cols = [c for c in [
            "Primary_Label",
            "Primary_Attack_Probability",
            "Predicted_Attack_Category",
            "MultiClass_Confidence",
            "Anomaly_Prediction",
            "Anomaly_Score",
        ] if c in results_df.columns]

        st.dataframe(results_df[display_cols].head(50), width="stretch", hide_index=True)

        # Download
        make_download(results_df, "Download results", "predictions.csv")

    except Exception as e:
        st.error("Error processing file.")
        st.write(str(e))