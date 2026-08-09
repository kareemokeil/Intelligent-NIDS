# Dataset README — CIC-IDS2017

## Data Source

This dataset was downloaded from the **official website** of the Canadian Institute for Cybersecurity (CIC):

🔗 **https://www.unb.ca/cic/datasets/ids-2017.html**

The data was collected by the University of New Brunswick (Canada), and includes labeled network flows, along with full packet payloads in pcap format, and CSV files intended for machine learning and deep learning purposes.

---

## How the Data Was Collected

Data capturing started at 9 a.m. on Monday, July 3, 2017, and ended at 5 p.m. on Friday, July 7, 2017 — a total of 5 full days. The data was captured in a lab environment consisting of 50 attacker machines, 420 victim servers, and several emulated departmental networks.

The abstract behavior of 25 users was built based on HTTP, HTTPS, FTP, SSH, and email protocols, to generate realistic, human-like benign (normal) background traffic.

---

## Dataset Size and Classes

The dataset consists of 2,830,743 flow records, spread across 13–15 different classes, including benign (normal) traffic in addition to multiple attack types such as:
- Brute Force (FTP-Patator, SSH-Patator)
- DoS (Hulk, GoldenEye, Slowloris, Slowhttptest)
- DDoS
- Web Attack
- Botnet
- Infiltration
- Heartbleed
- PortScan

> ⚠️ **Important note:** The dataset suffers from a clear class imbalance, since benign traffic represents the vast majority of records. This must be handled during preprocessing (SMOTE / Class Weights) before training any model.

---

## Features

The dataset contains 79 columns: 78 numerical features plus one categorical 'Label' column. The features describe network flow characteristics such as flow duration, packet lengths, ports, and flags.

These features were extracted from the flow data using the CICFlowMeter tool, covering information such as timestamps, source/destination IP addresses, source/destination ports, protocol types, and attack categories.

---

## Dataset Files

The dataset is available in two forms: pcap files containing full packet payloads along with the corresponding profiles and labeled flows (GeneratedLabelledFlows.zip), and CSV files intended for machine learning and deep learning purposes (MachineLearningCSV.zip).

In this project, only the **CSV files** (MachineLearningCSV.zip) were used, since they are the most suitable format for classification tasks with Machine/Deep Learning models, and to avoid dealing directly with raw pcap files.

---

## Known Limitations

Several academic studies have noted technical issues in how some features were originally extracted in this dataset (e.g., duplicated columns or miscalculated values for some features). This point is mentioned in the academic report as a "known limitation" of the dataset itself — not an error introduced by this project — and it is commonly discussed in published research on CIC-IDS2017.

---

## Citation

When using this dataset in any research or academic report, the official citation required is:

> Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", 4th International Conference on Information Systems Security and Privacy (ICISSP), Portugal, January 2018.

---

## Usage in This Project

1. CSV files were downloaded directly from the official website.
2. Raw files are stored in `data/raw/`.
3. After cleaning and preprocessing (Steps 1–4 of the project plan), the cleaned version is saved in `data/processed/`.
