from pathlib import Path
import sys

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from config import MODEL_EXPLANATIONS
from tabs import alerts, binary_models, drift, multiclass, overview, shap_explainability, upload_predict, what_if
from utils.loaders import build_paths, discover_project_root, file_status_table, load_app_data, normalize_base_path
from utils.ui import hero, inject_security_css


st.set_page_config(
    page_title="IDS Security Dashboard",
    page_icon="🛡️",
    layout="wide",
)

inject_security_css()

hero(
    "Intrusion Detection Security Dashboard",
    "",
)

with st.sidebar:
    st.header("Control Panel")
    default_project_root = discover_project_root()
    base_path = st.text_input(
        "Project root folder",
        value=default_project_root,
        help="Folder that contains models/, results/, and artifacts/.",
    )
    base_path = normalize_base_path(base_path)

    selected_binary_model = st.radio(
        "Primary detection model",
        ["Random Forest", "Logistic Regression", "Deep Learning"],
        index=0,
        help="Controls the main binary model shown in evaluation, what-if, and upload tabs.",
    )
    st.markdown("---")
    st.caption(MODEL_EXPLANATIONS[selected_binary_model])

paths = build_paths(base_path)
status_df = file_status_table(paths)

data = load_app_data(paths)

ctx = {
    "base_path": base_path,
    "paths": paths,
    "status_df": status_df,
    "data": data,
    "selected_binary_model": selected_binary_model,
}

tab_objects = st.tabs([
    "Command Center",
    "Alerts",
    "Performance",
    "Attack Categories",
    "Explainability",
    "What-If",
    "Drift",
    "Upload & Predict",
])

renderers = [
    overview.render,
    alerts.render,
    binary_models.render,
    multiclass.render,
    shap_explainability.render,
    what_if.render,
    drift.render,
    upload_predict.render,
]

for tab, render in zip(tab_objects, renderers):
    with tab:
        render(ctx)
