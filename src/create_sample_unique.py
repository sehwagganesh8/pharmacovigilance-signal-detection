# src/create_sample_unique.py
"""
Create a small sample with ONE row per primaryid.
Usage:
    python src/create_sample_unique.py --n 10000
"""
import argparse, os, csv, random
import pandas as pd
from collections import Counter

BASE = "data/ASCII"
OUT = "data/faers_sample_master.csv"  # overwrite safe sample

def reservoir_sample_primaryids(demo_path, n):
    reservoir = []
    with open(demo_path, encoding="latin1", errors="ignore") as fh:
        reader = csv.reader(fh, delimiter="$")
        header = next(reader)
        idx = None
        for i, col in enumerate(header):
            if col.strip().lower() == "primaryid":
                idx = i
                break
        if idx is None:
            raise SystemExit("primaryid column not found in DEMO header")
        for t, row in enumerate(reader, start=1):
            if len(row) <= idx:
                continue
            pid = row[idx]
            if t <= n:
                reservoir.append(pid)
            else:
                r = random.randint(0, t-1)
                if r < n:
                    reservoir[r] = pid
    return set(reservoir)

def filter_file_by_ids(path, ids_set, out_path):
    reader = pd.read_csv(path, sep="$", encoding="latin1", dtype=str, chunksize=200000)
    first = True
    for chunk in reader:
        chunk.columns = [c.lower() for c in chunk.columns]
        key = "primaryid" if "primaryid" in chunk.columns else next((c for c in chunk.columns if "primary" in c), None)
        if key is None:
            raise SystemExit(f"Cannot find primary id column in {path}")
        filtered = chunk[chunk[key].isin(ids_set)]
        if filtered.empty:
            continue
        if first:
            filtered.to_csv(out_path, mode="w", index=False, sep="$")
            first = False
        else:
            filtered.to_csv(out_path, mode="a", index=False, header=False, sep="$")

def choose_most_common(series):
    # series may be NaN or empty strings - pick most common non-empty
    vals = [str(v).strip() for v in series if pd.notna(v) and str(v).strip() != ""]
    if not vals:
        return ""
    c = Counter(vals)
    return c.most_common(1)[0][0]

def build_unique_master(tmp_demo, tmp_drug, tmp_reac, tmp_outc):
    # read filtered (they use $ separator)
    demo = pd.read_csv(tmp_demo, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    drug = pd.read_csv(tmp_drug, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    reac = pd.read_csv(tmp_reac, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    outc = pd.read_csv(tmp_outc, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower) if tmp_outc else None

    # ensure primaryid present
    if "primaryid" not in demo.columns:
        if "caseid" in demo.columns:
            demo = demo.rename(columns={"caseid":"primaryid"})
        else:
            raise SystemExit("primaryid missing in demo")

    # merge to have everything available per primaryid (this can still expand rows)
    merged = demo.merge(drug, on="primaryid", how="left")\
                 .merge(reac, on="primaryid", how="left")

    # Clean up outc to avoid duplicate-column merge errors:
    if outc is not None:
        # lowercased already; keep only primaryid and outcome column(s)
        keep = ["primaryid"]
        if "outc_cod" in outc.columns:
            keep.append("outc_cod")
        elif "outcome" in outc.columns:
            keep.append("outcome")
        # if none of the expected outcome columns present, skip merging outc
        if len(keep) > 1:
            outc_clean = outc[keep].copy()
            merged = merged.merge(outc_clean, on="primaryid", how="left")
        else:
            # no useful outcome column found; skip merging
            pass

    # group by primaryid -> pick representative fields
    reps = []
    grouped = merged.groupby("primaryid")
    for pid, g in grouped:
        row = {}
        row["primaryid"] = pid
        # pick some demo fields if present
        for c in ["caseid","age","sex","event_dt","fda_dt","serious"]:
            row[c] = g[c].dropna().astype(str).iloc[0] if c in g.columns and not g[c].dropna().empty else ""
        # most common drug name
        row["drugname"] = choose_most_common(g.get("drugname", g.get("drug", pd.Series(dtype=str))))
        # most common reaction PT
        row["pt"] = choose_most_common(g.get("pt", g.get("reaction", pd.Series(dtype=str))))
        # outcome (already in merged if present)
        row["outc_cod"] = choose_most_common(g.get("outc_cod", g.get("outcome", pd.Series(dtype=str))))
        # create ae_text
        row["ae_text"] = " | ".join([row["drugname"], row["pt"], row["outc_cod"]]).strip(" | ")
        reps.append(row)

    out_df = pd.DataFrame(reps)
    # safe date parsing and week
    out_df["event_dt"] = pd.to_datetime(out_df.get("event_dt", pd.Series([""]*len(out_df))), errors="coerce")
    out_df["week"] = out_df["event_dt"].dt.to_period("W").astype(str)
    out_df.to_csv(OUT, index=False)
    print("Saved sample (unique per primaryid) to", OUT, "rows:", len(out_df))


def main(n):
    files = os.listdir(BASE)
    demo = [f for f in files if f.upper().startswith("DEMO")][0]
    drug = [f for f in files if f.upper().startswith("DRUG")][0]
    reac = [f for f in files if f.upper().startswith("REAC")][0]
    outc_list = [f for f in files if f.upper().startswith("OUTC")]
    outc = outc_list[0] if outc_list else None

    demo_path = os.path.join(BASE, demo)
    drug_path = os.path.join(BASE, drug)
    reac_path = os.path.join(BASE, reac)
    outc_path = os.path.join(BASE, outc) if outc else None

    print("Reservoir sampling", n, "primaryids from", demo_path)
    ids = reservoir_sample_primaryids(demo_path, n)
    print("Sampled ids:", len(ids))

    tmp_demo = "data/_demo_sample.txt"
    tmp_drug = "data/_drug_sample.txt"
    tmp_reac = "data/_reac_sample.txt"
    tmp_outc = "data/_outc_sample.txt" if outc_path else None

    print("Filtering DEMO (streaming)...")
    filter_file_by_ids(demo_path, ids, tmp_demo)
    print("Filtering DRUG (streaming)...")
    filter_file_by_ids(drug_path, ids, tmp_drug)
    print("Filtering REAC (streaming)...")
    filter_file_by_ids(reac_path, ids, tmp_reac)
    if outc_path:
        print("Filtering OUTC (streaming)...")
        filter_file_by_ids(outc_path, ids, tmp_outc)

    print("Building unique merged sample...")
    build_unique_master(tmp_demo, tmp_drug, tmp_reac, tmp_outc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10000, help="number of unique primaryids")
    args = parser.parse_args()
    main(args.n)
