---
title: Intelligent NIDS SOC Console
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.35.0
app_file: Dashboard/app.py
pinned: false
---

# NIDS Project

This project provides an Intelligent Network Intrusion Detection Workflow & SOC Dashboard.


## Structure
- notebooks/: Jupyter notebooks for preprocessing, visualization, training, evaluation, and AI reporting.
- models/: Serialized model artifacts such as the classifier and preprocessing objects.
- app/: A lightweight application for serving results and generating reports.
- reports/: Generated figures and incident reports.

## Getting Started
1. Create a Python environment and install the dependencies from requirements.txt.
2. Work through the notebooks in order.
3. Use the app package to expose the trained model or generate reports.
