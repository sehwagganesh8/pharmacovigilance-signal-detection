# src/llm_agent.py
"""
LLM Agent Stub (offline)
Summarizes detected signals using simple rule-based logic.
Usage:
python src/llm_agent.py --signals outputs/signals_detected.csv --clustered data/faers_clustered.csv --out outputs/signals_with_summaries.json
"""

import argparse
import json
import pandas as pd


def summarize_signal(drug, reaction, count):
    """
    Offline simple summarizer.
    You can later replace with real LLM (OpenAI, Gemini, Groq etc.)
    """
    summary = (
        f"Potential safety signal detected for **{drug}** associated with "
        f"the adverse reaction **{reaction}**.\n\n"
        f"- Report count: {count}\n"
        f"- Interpretation: Higher-than-expected reports may indicate a real drug–event relationship. "
        f"Further clinical validation is recommended."
    )
    return summary


def main(signals_csv, clustered_csv, out_json):
    print("Loading detected signals:", signals_csv)
    sigs = pd.read_csv(signals_csv)

    print("Loading clustered dataset (for future enrichment):", clustered_csv)
    df = pd.read_csv(clustered_csv)

    results = []

    for _, row in sigs.iterrows():
        drug = row.iloc[0]
        reaction = row.iloc[1]
        count = row["count"]

        summary = summarize_signal(drug, reaction, count)

        results.append({
            "drug": drug,
            "reaction": reaction,
            "count": int(count),
            "summary": summary
        })

    output = {
        "total_signals": len(results),
        "signals": results
    }

    print(f"Saving summarized signals to {out_json}")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--signals", required=True)
    parser.add_argument("--clustered", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    main(args.signals, args.clustered, args.out)
