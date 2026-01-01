# src/create_sample.py
"""
Create a small sample dataset from FAERS ASCII files by sampling PRIMARYID values
and filtering the main tables to those IDs. Output: data/faers_sample_master.csv
Usage:
    python src/create_sample.py --n 10000
"""
import argparse
import os
import random
import pandas as pd

BASE = "data/ASCII"
OUT = "data/faers_sample_master.csv"

def reservoir_sample_primaryids(demo_path, n):
    import csv
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
            raise SystemExit("primaryid column not found in DEMO header: " + str(header[:20]))
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

def filter_file_by_ids(path, ids_set, out_path, keycolname_guess="primaryid"):
    # read in chunks with FAERS delimiter and write using same delimiter $
    reader = pd.read_csv(path, sep="$", encoding="latin1", dtype=str, chunksize=200000)
    first = True
    for chunk in reader:
        chunk.columns = [c.lower() for c in chunk.columns]
        # find correct key column (primaryid or similar)
        key = keycolname_guess if keycolname_guess in chunk.columns else next((c for c in chunk.columns if "primary" in c), None)
        if key is None:
            raise SystemExit(f"Cannot find primary id column in {path}. cols: {chunk.columns[:20]}")
        filtered = chunk[chunk[key].isin(ids_set)]
        if filtered.empty:
            continue
        # write with $ separator to keep FAERS format consistent
        if first:
            filtered.to_csv(out_path, mode="w", index=False, sep="$")
            first = False
        else:
            filtered.to_csv(out_path, mode="a", index=False, header=False, sep="$")

def build_sample_master(demo_file, drug_file, reac_file, outc_file):
    # read the filtered temp files (they are written with sep="$")
    demo = pd.read_csv(demo_file, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    drug = pd.read_csv(drug_file, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    reac = pd.read_csv(reac_file, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower)
    outc = pd.read_csv(outc_file, sep="$", encoding="latin1", dtype=str).rename(columns=str.lower) if outc_file else None

    # choose columns if present
    demo_cols = [c for c in ["primaryid","caseid","age","sex","event_dt","serious"] if c in demo.columns]
    drug_cols = [c for c in ["primaryid","drugname","role_cod","drug"] if c in drug.columns]
    reac_cols = [c for c in ["primaryid","pt","reaction"] if c in reac.columns]
    outc_cols = [c for c in ["primaryid","outc_cod","outcome"] if outc is not None and c in outc.columns]

    demo_sel = demo[demo_cols].copy()
    drug_sel = drug[drug_cols].copy()
    reac_sel = reac[reac_cols].copy()
    outc_sel = outc[outc_cols].copy() if outc is not None and outc_cols else pd.DataFrame()

    # Merge (safe: primaryid must be present)
    if "primaryid" not in demo_sel.columns:
        # try caseid fallback
        if "caseid" in demo_sel.columns:
            demo_sel = demo_sel.rename(columns={"caseid":"primaryid"})
        else:
            raise SystemExit("No primaryid or caseid in DEMO sample")

    df = demo_sel.merge(drug_sel, on="primaryid", how="left")\
                 .merge(reac_sel, on="primaryid", how="left")
    if not outc_sel.empty:
        df = df.merge(outc_sel, on="primaryid", how="left")

    # normalize text cols and create ae_text and week
    df["drugname"] = df.get("drugname", pd.Series([""]*len(df))).fillna("").astype(str).str.lower()
    df["pt"] = df.get("pt", pd.Series([""]*len(df))).fillna("").astype(str).str.lower()
    df["outc_cod"] = df.get("outc_cod", pd.Series([""]*len(df))).fillna("").astype(str).str.lower()
    df["ae_text"] = (df["drugname"] + " | " + df["pt"] + " | " + df["outc_cod"]).str.replace(r"\s+"," ", regex=True).str.strip()
    df["event_dt"] = pd.to_datetime(df.get("event_dt", pd.Series([None]*len(df))), errors="coerce")
    df["week"] = df["event_dt"].dt.to_period("W").astype(str)

    df.to_csv(OUT, index=False)
    print("Saved sample master to", OUT, "rows:", len(df))

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

    print("Reservoir sampling", n, "primaryids from", demo_path, "...")
    ids = reservoir_sample_primaryids(demo_path, n)
    print("Sampled ids:", len(ids))

    tmp_demo = "data/_demo_sample.txt"
    tmp_drug = "data/_drug_sample.txt"
    tmp_reac = "data/_reac_sample.txt"
    tmp_outc = "data/_outc_sample.txt"

    print("Filtering DEMO (streaming) ...")
    filter_file_by_ids(demo_path, ids, tmp_demo)
    print("Filtering DRUG (streaming) ...")
    filter_file_by_ids(drug_path, ids, tmp_drug)
    print("Filtering REAC (streaming) ...")
    filter_file_by_ids(reac_path, ids, tmp_reac)
    if outc_path:
        print("Filtering OUTC (streaming) ...")
        filter_file_by_ids(outc_path, ids, tmp_outc)

    print("Building merged sample master ...")
    build_sample_master(tmp_demo, tmp_drug, tmp_reac, tmp_outc if outc_path else None)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10000, help="sample size")
    args = parser.parse_args()
    main(args.n)
