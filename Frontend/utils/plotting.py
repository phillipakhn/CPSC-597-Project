import matplotlib.pyplot as plt
import streamlit as st
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    auc,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)


def plot_metric_bar(df, metric: str):
    fig, ax = plt.subplots(figsize=(5.8, 2.8))
    ax.bar(df["Model"], df[metric])
    ax.set_title(f"{metric} by Model", fontsize=11)
    ax.set_ylabel(metric, fontsize=9)
    if metric != "Training Time":
        ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=15, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, width="content")


def plot_confusion_from_labels(y_true, y_pred, title: str):
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["BENIGN", "ATTACK"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    st.pyplot(fig, width="content")


def plot_roc_curve(y_true, y_score, title: str):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_xlabel("False Positive Rate", fontsize=9)
    ax.set_ylabel("True Positive Rate", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, width="content")


def plot_pr_curve(y_true, y_score, title: str):
    precision, recall, _ = precision_recall_curve(y_true, y_score)
    ap = average_precision_score(y_true, y_score)
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.plot(recall, precision, label=f"AP = {ap:.4f}")
    ax.set_xlabel("Recall", fontsize=9)
    ax.set_ylabel("Precision", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, width="content")


def plot_horizontal_importance(df, feature_col, value_col, title, xlabel):
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.barh(df[feature_col][::-1], df[value_col][::-1])
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel, fontsize=9)
    fig.tight_layout()
    st.pyplot(fig, width="content")
