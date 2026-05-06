from typing import List, Tuple

import numpy as np
import pandas as pd

from config import CICFLOWMETER_COLUMN_ALIASES, CICFLOWMETER_METADATA_COLUMNS


def clean_uploaded_data(df_input: pd.DataFrame) -> pd.DataFrame:
    df_clean = df_input.copy()
    df_clean.columns = df_clean.columns.astype(str).str.strip()
    df_clean = df_clean.rename(columns=CICFLOWMETER_COLUMN_ALIASES)
    df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]

    label_like_cols = [col for col in df_clean.columns if col.strip().lower() == "label"]
    df_clean = df_clean.drop(columns=label_like_cols, errors="ignore")
    df_clean = df_clean.drop(columns=CICFLOWMETER_METADATA_COLUMNS, errors="ignore")

    for col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    df_clean.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_clean.fillna(0, inplace=True)
    return df_clean


def align_features_to_training(df_input: pd.DataFrame, training_features: List[str]) -> Tuple[pd.DataFrame, List[str], List[str]]:
    df_aligned = df_input.copy()
    training_features = [str(col).strip() for col in training_features]
    missing_cols = [col for col in training_features if col not in df_aligned.columns]
    extra_cols = [col for col in df_aligned.columns if col not in training_features]

    for col in missing_cols:
        df_aligned[col] = 0

    return df_aligned[training_features], missing_cols, extra_cols


def looks_like_old_cicids_schema(training_features: List[str]) -> bool:
    if not training_features:
        return False
    old_names = {"Destination Port", "Flow Duration", "Total Fwd Packets", "Packet Length Mean"}
    return any(name in set(training_features) for name in old_names)
