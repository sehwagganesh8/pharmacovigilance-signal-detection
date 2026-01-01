# Pharmacovigilance Signal Detection Agent 🚨

An AI-driven system for early detection of drug safety signals using adverse event data, clustering, and Large Language Model (LLM) agents.

---

## Introduction

Pharmacovigilance teams receive millions of adverse event (AE) reports every year from sources such as regulatory databases, medical literature, and safety bulletins.  
Today, much of this data is reviewed manually, making the process slow and increasing the risk of missing early warning signs related to drug safety.

This project aims to build an **AI-based pharmacovigilance signal detection agent** that combines machine learning, clustering, and LLM-based analysis to identify emerging safety risks earlier and more efficiently.

---

## Problem Statement

Detecting early drug safety signals is challenging due to:

- The massive volume of adverse event reports
- Unstructured and noisy textual data
- Weak or emerging signals hidden within large datasets

Manual review is time-consuming and often detects risks too late, after patients may already be harmed.

---

## Objective

Build an intelligent system that can:

- Analyze structured and unstructured adverse event data
- Identify emerging and unexpected safety patterns
- Summarize key safety signals in a reviewer-friendly format
- Generate a simple weekly signal-detection dashboard

---

## Data Sources

Publicly available pharmacovigilance datasets are used for demonstration:

- **FAERS (FDA Adverse Event Reporting System)**
- **WHO-UMC sample adverse event datasets**

🔗 FAERS dataset:  
https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html

> Note: Raw datasets are not included in this repository due to size constraints.

---

## Solution Overview

The system follows a multi-stage AI pipeline:

### 1. Data Collection

- Ingest adverse event reports from public datasets
- Extract key fields such as drug name, reaction, seriousness, and patient details

### 2. Preprocessing

- Clean and normalize drug and reaction names
- Handle missing and inconsistent values
- Generate text embeddings for narrative fields

### 3. Clustering

- Group similar adverse event reports using clustering algorithms
- Identify:
  - Rare but severe adverse reactions
  - Rapidly increasing trends
  - Unusual drug–event combinations

### 4. LLM-Based Analysis

- Use LangChain-powered LLM agents to:
  - Summarize each cluster
  - Identify top safety signals
  - Assign risk levels (Low / Medium / High)
  - Provide concise explanations for reviewers

### 5. Weekly Signal Dashboard

- Generate:
  - A structured JSON output with detected signals
  - A human-readable text/Markdown report
- Highlight the most critical emerging safety concerns

---

## Expected Outcome

- Early identification of emerging adverse event clusters
- Clear summaries of potential safety risks
- A lightweight, interpretable dashboard for pharmacovigilance teams

This enables **faster, data-driven safety decisions** and supports early regulatory action.

---

## Tech Stack

- **Python**
- **Pandas, NumPy**
- **Scikit-learn (Clustering)**
- **Embeddings**
- **FAISS / Chroma**
- **LangChain Agents**
- **Prompt-based risk classification**

---

## Project Structure

```text
pharmacovigilance-signal-detection/
├── src/            # Core signal detection pipeline
├── ui/             # Dashboard and visualization
├── data/           # Sample data structure (no raw datasets)
├── requirements.txt
├── README.md
└── .gitignore

---

##Disclaimer

This project is developed for educational and hackathon purposes only and is not intended for direct clinical or regulatory decision-making.
```
