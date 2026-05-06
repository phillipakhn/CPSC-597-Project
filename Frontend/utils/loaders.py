import os
import warnings
from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
import streamlit as st
from sklearn.exceptions import InconsistentVersionWarning

from config import EXPECTED_FILES


def _frontend_dir() -> Path:
    """Return the folder that contains app.py/Frontend code."""
    return Path(__file__).resolve().parents[1]


def _score_project_root(path: Path) -> int:
    """Score a possible project root by checking for expected folders/files."""
    score = 0
    for folder in ("models", "results", "artifacts"):
        if (path / folder).exists():
            score += 10
    # Extra points for actual expected files.
    for files in EXPECTED_FILES.values():
        for rel_path in files.values():
            if (path / rel_path).exists():
                score += 1
    return score


def discover_project_root() -> str:
    """Find the project root without hardcoded user-specific paths.

    Default expected layout:
        IDS_Project/Frontend/app.py
        IDS_Project/models/
        IDS_Project/results/
        IDS_Project/artifacts/

    You can override this with the IDS_PROJECT_ROOT environment variable
    or by typing a folder in the Streamlit sidebar.
    """
    frontend_dir = _frontend_dir()
    candidates = []

    env_root = os.environ.get("IDS_PROJECT_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    candidates.extend([
        frontend_dir.parent,      # normal layout: project_root/Frontend
        Path.cwd(),               # running from project root
        Path.cwd().parent,        # running from Frontend
        frontend_dir,             # fallback if folders are inside Frontend
    ])

    best = max(candidates, key=_score_project_root)
    return str(best.resolve())


def normalize_base_path(base_path: str) -> str:
    """Expand and normalize a user-provided project root path."""
    if not base_path:
        return discover_project_root()
    return str(Path(base_path).expanduser().resolve())


def build_paths(base_path: str) -> Dict[str, Dict[str, str]]:
    base = Path(normalize_base_path(base_path))
    return {
        section: {key: str(base / rel_path) for key, rel_path in files.items()}
        for section, files in EXPECTED_FILES.items()
    }


@st.cache_data(show_spinner=False)
def load_csv(path: str):
    if path and os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_resource(show_spinner=False)
def load_pickle(path: str):
    if not path or not os.path.exists(path):
        return None, None
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", InconsistentVersionWarning)
            obj = joblib.load(path)
        version_warning = None
        for warning_msg in caught:
            if issubclass(warning_msg.category, InconsistentVersionWarning):
                version_warning = str(warning_msg.message)
                break
        return obj, version_warning
    except Exception as exc:
        return None, f"Could not load {os.path.basename(path)}: {exc}"


@st.cache_resource(show_spinner=False)
def load_keras_model(path: str):
    if not path or not os.path.exists(path):
        return None, None
    try:
        import tensorflow as tf
        return tf.keras.models.load_model(path), None
    except Exception as exc:
        return None, f"Could not load {os.path.basename(path)}: {exc}"


def file_status_table(paths: dict) -> pd.DataFrame:
    rows = []
    for section, files in paths.items():
        for name, path in files.items():
            rows.append({
                "Section": section,
                "Artifact": name,
                "Path": path,
                "Found": os.path.exists(path),
            })
    return pd.DataFrame(rows)


def load_app_data(paths: dict) -> dict:
    data = {
        "binary_results_df": load_csv(paths["results"]["binary_comparison"]),
        "multiclass_results_df": load_csv(paths["results"]["multiclass_comparison"]),
        "feature_importance_df": load_csv(paths["results"]["feature_importance"]),
        "multiclass_feature_importance_df": load_csv(paths["results"]["multiclass_feature_importance"]),
        "shap_importance_df": load_csv(paths["results"]["shap_feature_importance"]),
        "alerts_df": load_csv(paths["results"]["alerts"]),
        "drift_df": load_csv(paths["results"]["concept_drift"]),
        "project_summary_df": load_csv(paths["results"]["project_summary"]),
        "sample_end_to_end_df": load_csv(paths["results"]["sample_end_to_end_predictions"]),
        "sample_explanations_df": load_csv(paths["results"]["sample_prediction_explanations"]),
        "X_test_df": load_csv(paths["artifacts"]["x_test"]),
        "y_test_df": load_csv(paths["artifacts"]["y_test"]),
    }

    model_specs = {
        "rf_model": paths["models"]["random_forest"],
        "log_model": paths["models"]["logistic_regression"],
        "standard_scaler": paths["models"]["standard_scaler"],
        "rf_multi_model": paths["models"]["random_forest_multiclass"],
        "dl_scaler": paths["models"]["deep_learning_scaler"],
        "iso_model": paths["models"]["isolation_forest"],
        "iso_scaler": paths["models"]["isolation_forest_scaler"],
        "multi_label_encoder": paths["artifacts"]["multi_label_encoder"],
        "training_features": paths["artifacts"]["training_features"],
        "what_if_features": paths["artifacts"]["what_if_features"],
    }

    warnings_list = []
    for key, path in model_specs.items():
        data[key], warning = load_pickle(path)
        if warning:
            warnings_list.append(warning)

    data["dl_model"], warning = load_keras_model(paths["models"]["deep_learning_model"])
    if warning:
        warnings_list.append(warning)

    data["load_warnings"] = warnings_list
    return data
