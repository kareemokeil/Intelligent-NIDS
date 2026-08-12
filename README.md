# Intelligent NIDS & SOC Analysis Platform

> An AI-powered Network Intrusion Detection System that combines Machine Learning, Explainable AI, RAG, and LLM-based security analysis to detect, explain, and report network attacks.

## Live Demo

🚀 **Try the deployed application:**

[**Intelligent NIDS — Streamlit App**](https://intelligent-nids-appnag3fzwwmyopt89ejfaj.streamlit.app/)

---

## Overview

**Intelligent NIDS** is an end-to-end Network Intrusion Detection and Security Analysis project developed to detect malicious network traffic and transform machine learning predictions into meaningful security insights.

The system uses the **CICIDS2017** dataset to classify network traffic into multiple attack categories and combines traditional Machine Learning with modern AI techniques to provide more than just a prediction.

The pipeline integrates:

**Machine Learning → SHAP Explainability → RAG → LLM → SOC Incident Reporting**

The goal is to make network attack detection more interpretable and useful for security analysts.

---

## What Problem Does It Solve?

Modern networks generate massive amounts of traffic, making manual analysis difficult and time-consuming.

A traditional ML model may simply return:

```text
Prediction: DoS
Confidence: 98%
```

But a SOC analyst needs more information:

* Why was this traffic classified as an attack?
* Which features influenced the prediction?
* What are the characteristics of this attack?
* What indicators should be investigated?
* What mitigation steps should be considered?
* How should the incident be documented?

This project addresses these questions by combining **ML detection, Explainable AI, Retrieval-Augmented Generation, and LLM-based reporting**.

---

## System Architecture

```text
                    Network Traffic
                          │
                          ▼
                Data Preprocessing
                          │
                          ▼
                 Feature Engineering
                          │
                          ▼
                Random Forest Model
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
          Prediction             SHAP
          + Confidence        Explainability
                │                   │
                └─────────┬─────────┘
                          ▼
                  Detected Attack
                          │
                          ▼
                  RAG Knowledge Base
                          │
                       FAISS
                          │
                          ▼
                    Relevant Context
                          │
                          ▼
                         LLM
                          │
                          ▼
              AI Security Incident Report
                          │
                          ▼
                  SOC Dashboard / App
```

---

## Dataset

The project uses the **CICIDS2017** dataset for network intrusion detection.

The classification task contains eight traffic categories:

| Label | Attack Type |
| ----: | ----------- |
|     0 | BENIGN      |
|     1 | Bot         |
|     2 | Brute Force |
|     3 | DDoS        |
|     4 | DoS         |
|     5 | PortScan    |
|     6 | Rare Attack |
|     7 | Web Attack  |

---

## Machine Learning Pipeline

### 1. Data Preprocessing

The raw CICIDS2017 CSV files are processed through several steps:

* Merge multiple network traffic files.
* Clean column names.
* Optimize numerical data types.
* Handle `Inf` and `-Inf` values.
* Remove duplicate records.
* Handle missing values.
* Analyze outliers using the IQR method.
* Apply feature transformations.
* Select relevant features.

Memory optimization was also applied by downcasting numerical columns where appropriate.

---

### 2. Feature Engineering

The final model uses a selected subset of network traffic features.

Important features identified during the analysis include:

* Bwd Packet Length Std
* Idle Mean
* Idle Max
* Bwd Packet Length Mean
* Total Length of Fwd Packets
* Flow Bytes/s

Selected skewed features were transformed using logarithmic transformations to improve their distributions.

---

## 3. Random Forest Classifier

The main detection model is a **Random Forest Classifier**.

The final configuration includes:

```text
n_estimators = 300
max_depth = 30
min_samples_leaf = 2
min_samples_split = 5
random_state = 42
n_jobs = -1
```

Class weighting was also applied to reduce the impact of class imbalance and improve the detection of minority attack categories.

---

## 4. Model Inference

For each network traffic sample, the model produces:

```text
Attack Type
Confidence Score
```

Example:

```text
Attack: DoS
Confidence: 100.00%
```

The prediction pipeline uses the saved preprocessing artifacts to ensure that incoming data is processed consistently with the data used during training.

---

# Explainable AI with SHAP

A prediction alone does not explain **why** the model made that decision.

For this reason, the project integrates **SHAP (SHapley Additive exPlanations)**.

SHAP identifies the features that contributed most strongly to a specific prediction.

For example:

```text
Prediction:
DoS

Important Features:
1. Bwd Packet Length Std
2. Idle Mean
3. Flow Bytes/s
4. Total Length of Fwd Packets
```

This provides security analysts with more transparency into the model's decision-making process.

---

# RAG-Based Security Knowledge

The project also includes a security knowledge base covering different attack types.

The knowledge base contains information such as:

* Attack description
* Attack behavior
* Indicators of Compromise
* Mitigation
* Response procedures
* SOC investigation guidance

The documents are divided into searchable chunks and indexed using **FAISS**.

---

## RAG Pipeline

```text
Detected Attack
       ↓
Security Query
       ↓
Embedding Model
       ↓
FAISS Similarity Search
       ↓
Relevant Security Knowledge
       ↓
LLM
       ↓
Structured Incident Report
```

This allows the LLM to use retrieved project-specific security knowledge when generating its analysis.

---

# AI-Generated SOC Incident Report

The final stage combines information from multiple components:

* ML prediction
* Confidence score
* SHAP feature contributions
* Retrieved security knowledge
* LLM reasoning

The resulting report can provide:

### Incident Classification

What type of attack was detected.

### Detection Confidence

How confident the ML model is.

### Key Contributing Features

Which network features influenced the prediction.

### Attack Analysis

What the detected attack means.

### Indicators of Compromise

Potential indicators that should be investigated.

### Recommended Actions

Suggested investigation and mitigation steps.

### SOC Guidance

Security operations guidance for handling the incident.

---

# Web Application

The project is deployed using **Streamlit**.

The application provides an interface for interacting with the detection and analysis pipeline.

### Application Workflow

```text
User Input
    ↓
Preprocessing
    ↓
ML Prediction
    ↓
Confidence Score
    ↓
SHAP Analysis
    ↓
RAG Retrieval
    ↓
LLM Analysis
    ↓
Security Report
```

---

# Project Structure

```text
NIDS/
│
├── notebooks/
│   ├── 01_data_preprocessing.ipynb
│   ├── model_training_evaluation.ipynb
│   ├── 03_Inference_and_LLM.ipynb
│   ├── 4_RAG.ipynb
│   └── 5_LLM_Integration.ipynb
│
├── models/
│   ├── final_random_forest_model.pkl
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   └── feature_names.pkl
│
├── datasets/
│
├── knowledge_base/
│   ├── BENIGN.md
│   ├── DoS.md
│   ├── DDoS.md
│   ├── PortScan.md
│   └── ...
│
├── faiss_index/
│
├── reports/
│
├── app/
│
├── requirements.txt
└── README.md
```

---

# Technologies & Tools

### Machine Learning

* Python
* Scikit-learn
* Random Forest
* SMOTE
* Joblib

### Data Processing

* Pandas
* NumPy

### Explainable AI

* SHAP

### RAG

* FAISS
* LangChain
* Hugging Face Embeddings

### Generative AI

* LLM
* Structured Prompting
* AI Incident Reporting

### Visualization

* Matplotlib
* Seaborn

### Deployment

* Streamlit

---

# Evaluation

The model was evaluated using:

* Accuracy
* Precision
* Recall
* F1-Score
* Classification Report
* Confusion Matrix

Evaluation was performed on unseen test data to measure the model's ability to generalize to previously unseen network traffic.

---

# Key Highlights

* Multi-class network intrusion detection
* CICIDS2017-based security classification
* Random Forest with class imbalance handling
* Feature engineering and preprocessing
* SHAP-based Explainable AI
* FAISS vector search
* RAG-based security knowledge retrieval
* LLM-powered incident analysis
* Automated SOC-oriented reporting
* Streamlit deployment

---

# Future Work

The project can be extended toward a more complete SOC platform through:

### Real-Time Network Monitoring

Integrate the system with live network traffic sources.

### Advanced SOC Dashboard

Add:

* Real-time alerts
* Attack timelines
* Severity levels
* Attack statistics
* Feature importance
* Incident history

### Threat Intelligence Integration

Connect the system with external threat intelligence sources.

### MITRE ATT&CK Integration

Map detected attacks to relevant MITRE ATT&CK techniques and tactics.

### Automated Response

Integrate predefined response actions for high-confidence security incidents.

### Advanced Machine Learning

Compare the current Random Forest model with:

* XGBoost
* LightGBM
* Neural Networks
* Ensemble approaches

---

# What I Learned

This project provided hands-on experience in building an end-to-end AI cybersecurity system, including:

* Network Intrusion Detection
* Machine Learning
* Imbalanced Classification
* Feature Engineering
* Explainable AI
* SHAP
* Vector Databases
* RAG
* LLM Integration
* Prompt Engineering
* Automated Security Reporting
* Streamlit Deployment

---

# Author

**Kareem Ashraf Hussin Okeil**

Computer & Communications Engineering Student

Interested in:

* Machine Learning
* Artificial Intelligence

---

## Disclaimer

This project is developed for educational and research purposes using the CICIDS2017 dataset.

The generated predictions and security recommendations should be reviewed and validated by qualified security professionals before being used in real-world security operations.

---

## Project

**Intelligent NIDS — From Network Traffic Detection to AI-Powered SOC Analysis**

**Machine Learning → SHAP → RAG → LLM → Security Incident Report**
