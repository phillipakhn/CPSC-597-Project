"""Shared configuration for the Streamlit IDS dashboard.

This file intentionally does not contain user-specific absolute paths.
The app discovers the project root at runtime and expects these folders
beside the Frontend folder by default:

    IDS_Project/
    ├── Frontend/
    ├── models/
    ├── results/
    └── artifacts/
"""

EXPECTED_FILES = {
    "results": {
        "binary_comparison": "results/model_comparison.csv",
        "full_comparison": "results/full_model_comparison.csv",
        "multiclass_comparison": "results/multiclass_model_comparison.csv",
        "feature_importance": "results/feature_importance.csv",
        "multiclass_feature_importance": "results/multiclass_feature_importance.csv",
        "shap_feature_importance": "results/shap_feature_importance.csv",
        "alerts": "results/high_confidence_alerts.csv",
        "concept_drift": "results/concept_drift_results.csv",
        "project_summary": "results/project_summary.csv",
        "sample_end_to_end_predictions": "results/sample_end_to_end_predictions.csv",
        "sample_prediction_explanations": "results/sample_prediction_explanations.csv",
        "artifact_manifest": "results/artifact_manifest.csv",
    },
    "models": {
        "random_forest": "models/random_forest_model.pkl",
        "logistic_regression": "models/logistic_regression_model.pkl",
        "standard_scaler": "models/standard_scaler.pkl",
        "random_forest_multiclass": "models/random_forest_multiclass_model.pkl",
        "deep_learning_model": "models/deep_learning_model.keras",
        "deep_learning_scaler": "models/deep_learning_scaler.pkl",
        "isolation_forest": "models/isolation_forest_model.pkl",
        "isolation_forest_scaler": "models/isolation_forest_scaler.pkl",
    },
    "artifacts": {
        "x_test": "artifacts/X_test_sample.csv",
        "y_test": "artifacts/y_test_sample.csv",
        "binary_feature_names": "artifacts/binary_feature_names.pkl",
        "multi_feature_names": "artifacts/multi_feature_names.pkl",
        "multi_label_encoder": "artifacts/multi_label_encoder.pkl",
        "training_feature_schema": "artifacts/training_feature_schema.csv",
        "training_features": "artifacts/training_features.pkl",
        "training_features_multiclass": "artifacts/training_features_multiclass.pkl",
        "what_if_features": "artifacts/what_if_features.pkl",
    },
}

FEATURE_EXPLANATIONS = {
    "bwd_seg_size_avg": "Average size of backward packets in the flow.",
    "pkt_len_std": "How much packet sizes vary within the flow.",
    "pkt_len_var": "Variance of packet lengths. Higher values mean more spread.",
    "pkt_len_max": "Largest packet observed in the flow.",
    "bwd_pkt_len_std": "Variation in backward packet lengths.",
    "bwd_pkt_len_max": "Largest backward packet seen in the flow.",
    "pkt_size_avg": "Average packet size over the flow.",
    "bwd_pkt_len_mean": "Average backward packet length.",
    "flow_duration": "How long the network flow lasted.",
    "flow_byts_s": "Average bytes per second in the flow.",
    "flow_pkts_s": "Average packets per second in the flow.",
    "tot_fwd_pkts": "Number of packets sent in the forward direction.",
    "tot_bwd_pkts": "Number of packets sent in the backward direction.",
    "dst_port": "Destination service port for the flow.",
    "Avg Bwd Segment Size": "Average size of backward packets in the flow.",
    "Packet Length Std": "How much packet sizes vary within the flow.",
    "Packet Length Variance": "Variance of packet lengths. Higher values mean more spread.",
    "Max Packet Length": "Largest packet observed in the flow.",
    "Bwd Packet Length Std": "Variation in backward packet lengths.",
    "Bwd Packet Length Max": "Largest backward packet seen in the flow.",
    "Average Packet Size": "Average packet size over the flow.",
    "Bwd Packet Length Mean": "Average backward packet length.",
}

CICFLOWMETER_METADATA_COLUMNS = ["src_ip", "dst_ip", "src_port", "protocol", "timestamp"]

CICFLOWMETER_COLUMN_ALIASES = {
    "flow_bytes_s": "flow_byts_s",
    "flow_packets_s": "flow_pkts_s",
    "fwd_packet_length_max": "fwd_pkt_len_max",
    "fwd_packet_length_min": "fwd_pkt_len_min",
    "fwd_packet_length_mean": "fwd_pkt_len_mean",
    "fwd_packet_length_std": "fwd_pkt_len_std",
    "bwd_packet_length_max": "bwd_pkt_len_max",
    "bwd_packet_length_min": "bwd_pkt_len_min",
    "bwd_packet_length_mean": "bwd_pkt_len_mean",
    "bwd_packet_length_std": "bwd_pkt_len_std",
}

MODEL_EXPLANATIONS = {
    "Random Forest": "Tree-based supervised model. Strong default model because it is accurate and easy to interpret.",
    "Logistic Regression": "Linear supervised baseline. Good for showing a simpler model and comparing trade-offs.",
    "Deep Learning": "Neural network baseline. Useful for comparing performance and training cost against classical ML.",
}

ALERT_THRESHOLDS = {
    "Conservative (0.97)": 0.97,
    "Balanced (0.93)": 0.93,
    "Investigative (0.90)": 0.90,
}
