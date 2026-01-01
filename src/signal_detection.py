# src/signal_detection.py
"""
Simple signal detection script.
Usage:
  python src/signal_detection.py --input data/faers_clustered.csv --out outputs/signals_detected.csv
"""

import argparse
import os
import pandas as pd

def choose_columns(df):
    # Accept several common name variants
    drug_col = None
    react_col = None

    for c in df.columns:
        if c.lower() in ("drugname", "drug_name", "drug"):
            drug_col = c
            break
    for c in df.columns:
        if c.lower() in ("pt", "reaction", "preferred_term"):
            react_col = c
            break

    return drug_col, react_col

def detect_signals(df, drug_col, react_col, min_count=5):
    # compute counts for drug - reaction pairs and per-cluster counts
    pair_counts = df.groupby([drug_col, react_col]).size().reset_index(name="count")
    # basic threshold (changeable)
    signals = pair_counts[pair_counts["count"] >= min_count].sort_values("count", ascending=False)
    return signals

def main(input_csv, out_csv, min_count):
    print("Loading clustered data:", input_csv)
    df = pd.read_csv(input_csv)

    drug_col, react_col = choose_columns(df)
    if drug_col is None or react_col is None:
        print("ERROR: Could not find drug or reaction column in the input CSV.")
        print("Columns present:", list(df.columns)[:60])
        raise SystemExit(1)

    print("Using columns:", drug_col, "for drug, and", react_col, "for reaction/PT")

    signals = detect_signals(df, drug_col, react_col, min_count=min_count)

    # add a simple enrichment: top drug share in cluster for each signal (helpful heuristic)
    # We attempt to join with cluster counts if cluster exists
    if "cluster" in df.columns:
        cluster_counts = df.groupby(["cluster"]).size().reset_index(name="cluster_total")
        # we will not compute cluster-level concentration here to keep lightweight

    # ensure outputs folder exists
    out_dir = os.path.dirname(out_csv)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print(f"Found {len(signals)} signals (min_count={min_count}). Saving to {out_csv}")
    signals.to_csv(out_csv, index=False)
    print("Top signals:")
    if not signals.empty:
        print(signals.head(20).to_string(index=False))
    else:
        print("No signals found with the current threshold.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to clustered CSV")
    parser.add_argument("--out", required=True, help="Output CSV for detected signals")
    parser.add_argument("--min_count", type=int, default=5, help="Minimum count threshold for a signal")
    args = parser.parse_args()
    main(args.input, args.out, args.min_count)
