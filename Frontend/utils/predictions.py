import numpy as np
import pandas as pd


def get_binary_probabilities(model, X: pd.DataFrame, scaler=None):
    if model is None or X is None or X.empty:
        return None, None
    X_used = X.copy()
    if scaler is not None:
        X_used = scaler.transform(X_used)
    preds = model.predict(X_used)
    probs = model.predict_proba(X_used)[:, 1] if hasattr(model, "predict_proba") else None
    return preds, probs


def get_dl_probabilities(model, X: pd.DataFrame, scaler):
    if model is None or X is None or X.empty or scaler is None:
        return None, None
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled, verbose=0).flatten()
    preds = (probs >= 0.5).astype(int)
    return preds, probs


def get_multiclass_predictions(model, X: pd.DataFrame, label_encoder):
    if model is None or X is None or X.empty or label_encoder is None:
        return None
    pred_enc = model.predict(X)
    result_df = pd.DataFrame({"Predicted_Attack_Category": label_encoder.inverse_transform(pred_enc)})
    if hasattr(model, "predict_proba"):
        result_df["MultiClass_Confidence"] = model.predict_proba(X).max(axis=1)
    return result_df


def get_anomaly_predictions(model, X: pd.DataFrame, scaler):
    if model is None or X is None or X.empty or scaler is None:
        return None
    X_scaled = scaler.transform(X)
    raw_pred = model.predict(X_scaled)
    raw_scores = model.decision_function(X_scaled)
    return pd.DataFrame({
        "Anomaly_Prediction": np.where(raw_pred == -1, 1, 0),
        "Anomaly_Score": -raw_scores,
    })


def predict_with_selected_model(selected_model, data, X):
    if selected_model == "Random Forest":
        return get_binary_probabilities(data.get("rf_model"), X)
    if selected_model == "Logistic Regression":
        return get_binary_probabilities(data.get("log_model"), X, scaler=data.get("standard_scaler"))
    if selected_model == "Deep Learning":
        return get_dl_probabilities(data.get("dl_model"), X, data.get("dl_scaler"))
    return None, None
