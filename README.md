Pharmacovigilance Signal Detection Agent
Introduction:

This project aims to build an AI-based system that can automatically detect early drug safety signals from adverse event (AE) data. Today, pharmacovigilance teams manually review huge datasets like FAERS reports, medical literature, and safety bulletins. This process is slow and makes it easy to miss early warning signs.

Our goal is to use LLMs and machine learning to make this process faster, smarter, and more reliable.

Problem We Are Solving

Millions of adverse events are reported every year, but identifying real safety issues hidden inside this data is difficult. Manual analysis is time-consuming, and weak signals often go unnoticed.

We want to build a system that can:

Read and analyze structured and unstructured AE reports

Group similar cases together using clustering

Detect patterns like unexpected reactions or rising trends

Summarize potential risks using an LLM

Produce a simple weekly dashboard with key signals

This helps pharmacovigilance teams act early and make better safety decisions.

Our Solution

We designed a pipeline that combines data processing, clustering, and LLM-based analysis.

1. Data Collection

We use publicly available adverse event datasets such as:

FAERS (FDA)

WHO-UMC sample data

https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html

From each report, we extract important fields like drug name, reaction, seriousness, patient details, etc.

2. Preprocessing

Before analysis, we:

Clean up drug names

Normalize reaction terms

Create embeddings for text fields

Prepare the data for clustering

3. Clustering

Using scikit-learn algorithms (KMeans, HDBSCAN), we group similar AE reports.
These clusters help us notice:

Rare but severe adverse events

Sharp increases in specific reactions

Unusual drug–event combinations

4. LLM Analysis

We use LangChain agents and an LLM to:

Summarize what each cluster represents

Identify the top safety signals

Assign a simple risk level (Low, Medium, High)

Provide short explanations useful for reviewers

5. Weekly Dashboard

The final output includes:

A JSON file with detected signals and cluster summaries

A text/Markdown report that highlights the most important findings

Clear explanations that non-technical reviewers can understand...
