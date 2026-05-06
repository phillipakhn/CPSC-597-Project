# CPSC 597

# Machine Learning for Network Anomaly Detection

## Overview
This project implements a Machine Learning–based Intrusion Detection System (IDS) using the CICIDS2017 dataset. Beyond model training and evaluation, the system includes an interactive pipeline that enables users to upload their own network traffic data (CSV files generated from PCAPs) for real-time analysis.

Uploaded data is automatically cleaned, aligned with the training feature schema, and passed through multiple models to perform binary classification, multiclass attack classification, and anomaly detection. The results are presented through a dashboard that simulates a real-world security monitoring environment.

The system supports:
- Binary classification (Normal vs Attack)
- Multiclass classification (Attack categories)
- Anomaly detection using unsupervised learning
- Interactive visualization through a web interface

Dataset Source:  
https://www.unb.ca/cic/datasets/ids-2017.html  

---

## Recommended: Run on WSL or Linux Environment

## Dataset Setup

The raw dataset can be downloaded from:

https://github.com/phillipakhn/CPSC-597-Project/releases/tag/v1.0-data

### Instructions

1. Download and extract the dataset  
2. The download will contain a folder named `raw_data`  
3. Place this folder directly inside the project directory:

CPSC-597-Project/raw_data/

## How to Run

### Step 1. Clone the Repository
```bash
git clone https://github.com/phillipakhn/CPSC-597-Project.git
cd CPSC-597-Project
```

### Step 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4. Run the Application (Streamlit)
```bash
cd Frontend/
streamlit run app.py
```

---

## Project Structure
```
CPSC-597-Project/
│
├── Frontend/
├── cicflowmeter/
├── notebooks/
├── models/
├── artifacts/
├── results/
├── raw_data/
├── requirements.txt
└── README.md
```

---

## Machine Learning Models

### 1. Binary Classification
- Logistic Regression 
- Random Forest  
- Deep Learning (Neural Network)  

### 2. Multiclass Classification
- Random Forest (Multiclass)  

### 3. Anomaly Detection
- Isolation Forest  

> Note: SMOTE was also applied to improve performance on minority attack classes.
---

## Features & Functionality

- Upload CSV network traffic data for prediction  
- Real-time attack detection  
- Alert system with severity levels  
- Feature importance visualization  
- SHAP-based explainability  
- Concept drift analysis  

---

## Evaluation Metrics

- Accuracy  
- Precision  
- Recall  
- F1 Score  
- ROC-AUC  
- PR-AUC  

---

## Notes

- Large datasets and trained models are not included in the repository  
- Ensure input CSV files match the expected feature schema  
- The `raw_data/` folder must be manually downloaded and placed in the project directory  

---

## Run the App

```bash
streamlit run app.py
```

Then open:
http://localhost:8501
