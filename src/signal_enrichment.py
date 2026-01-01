# src/signal_enrichment.py
import argparse, os, json
import pandas as pd

def load_signals(path):
    return pd.read_csv(path)

def enrich(signals_csv, clustered_csv, out_json, sample_n=5):
    df = pd.read_csv(clustered_csv, dtype=str)
    signals = load_signals(signals_csv)

    # tolerant column names
    drug_col = next((c for c in df.columns if c.lower() in ("drugname","drug_name","drug")), None)
    react_col = next((c for c in df.columns if c.lower() in ("pt","reaction","preferred_term")), None)
    case_col = next((c for c in df.columns if c.lower() in ("primaryid","caseid","report_id","id")), None)
    serious_col = next((c for c in df.columns if c.lower() in ("serious","seriousness","seriousnessdeath")), None)
    week_col = next((c for c in df.columns if c.lower() in ("week","event_week","event_dt_week")), None)

    out = {"total_signals": len(signals), "signals": []}
    for _, row in signals.iterrows():
        drug = row.iloc[0]
        reaction = row.iloc[1]
        count = int(row["count"])

        mask = df[drug_col].str.upper().fillna("") == str(drug).upper()
        mask &= df[react_col].str.upper().fillna("") == str(reaction).upper()
        sub = df[mask].copy()

        # serious pct
        if serious_col and serious_col in sub.columns:
            serious_pct = (sub[serious_col].fillna("").str.upper().isin(["Y","YES","1","SERIOUS","S"]).sum() / max(1, len(sub)))
        else:
            serious_pct = None

        # sample case ids
        case_ids = []
        if case_col and case_col in sub.columns:
            case_ids = sub[case_col].dropna().unique().tolist()[:sample_n]

        # weekly trend (simple counts per week if week_col exists)
        trend = None
        if week_col and week_col in sub.columns:
            trend = sub.groupby(week_col).size().reset_index(name="count").sort_values(week_col).to_dict(orient="records")

        out["signals"].append({
            "drug": drug,
            "reaction": reaction,
            "count": count,
            "serious_pct": (round(float(serious_pct)*100,2) if serious_pct is not None else None),
            "sample_case_ids": case_ids,
            "weekly_trend": trend
        })

    if out_json and os.path.dirname(out_json):
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("Saved enrichment to", out_json)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--signals", required=True)
    p.add_argument("--clustered", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sample_n", type=int, default=5)
    args = p.parse_args()
    enrich(args.signals, args.clustered, args.out, args.sample_n)

