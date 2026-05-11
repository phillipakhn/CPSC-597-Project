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

### Step 2. Create Virtual Environment (Optional, but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 4. Run the Application (Streamlit)
```bash
cd Frontend/
streamlit run app.py
```
Then open:
http://localhost:8501

## Run the Notebook
```
jupyter notebook
```
notebooks/IDS_Project_Notebook.ipynb


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

- Network traffic can be captured using tools such as Wireshark and saved in PCAP format.
- PCAP files are automatically processed and converted into feature-based CSV format within the pipeline via CICFlowMeter.

## Acknowledgments

- The `cicflowmeter/` module is third-party code obtained from:
  https://pypi.org/project/cicflowmeter/

- This tool is used in this project for extracting network flow features from PCAP files.

- All rights and licensing for CICFlowMeter belong to the original authors.
---
