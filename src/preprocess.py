# src/preprocess.py
import pandas as pd
import os
from pathlib import Path

BASE = Path("data/ASCII")
OUT_CSV = Path("data/faers_master.csv")

def read_table(path: Path):
    # FAERS ASCII uses $ as separator and latin1 encoding
    return pd.read_csv(path, sep="$", encoding="latin1", dtype=str)

def find_file_by_prefix(prefix: str):
    files = [f for f in os.listdir(BASE) if f.upper().startswith(prefix)]
    if not files:
        return None
    return BASE / files[0]

def load_faers_ascii():
    demo_path = find_file_by_prefix("DEMO")
    drug_path = find_file_by_prefix("DRUG")
    reac_path = find_file_by_prefix("REAC")
    outc_path = find_file_by_prefix("OUTC")  # optional

    if not (demo_path and drug_path and reac_path):
        raise FileNotFoundError("Missing one of DEMO/DRUG/REAC files in data/ASCII. Found: " + ", ".join(os.listdir(BASE)))

    demo = read_table(demo_path)
    drug = read_table(drug_path)
    reac = read_table(reac_path)
    outc = read_table(outc_path) if outc_path is not None else pd.DataFrame()

    return demo, drug, reac, outc

def safe_lower_cols(df: pd.DataFrame):
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    return df

def build_master_df(demo, drug, reac, outc):
    # normalize column names to lowercase
    demo = safe_lower_cols(demo)
    drug = safe_lower_cols(drug)
    reac = safe_lower_cols(reac)
    outc = safe_lower_cols(outc) if not outc.empty else pd.DataFrame()

    # Inspect which key column exists: primaryid or caseid etc.
    # FAERS uses PRIMARYID as the main join key; try to use 'primaryid' first
    key = None
    for candidate in ["primaryid", "caseid", "case_id"]:
        if candidate in demo.columns:
            key = candidate
            break
    if key is None:
        raise KeyError("No join key found in DEMO file (expected 'primaryid' or 'caseid'). Columns: " + ", ".join(demo.columns))

    # Ensure necessary columns exist (create if missing)
    for df in (demo, drug, reac, outc):
        if df is None:
            continue
        for col in df.columns:
            if isinstance(col, bytes):
                # avoid weird bytes columns
                df.rename(columns={col: col.decode("latin1")}, inplace=True)

    # Select needed columns (if present) with safe defaults
    demo_cols = [key]
    for c in ["age", "sex", "event_dt", "fda_dt", "serious"]:
        if c in demo.columns:
            demo_cols.append(c)
    demo_sel = demo[demo_cols].copy()

    drug_cols = [key]
    if "drugname" in drug.columns:
        drug_cols.append("drugname")
    elif "drug" in drug.columns:
        drug_cols.append("drug")
    drug_sel = drug[drug_cols].copy()

    reac_cols = [key]
    if "pt" in reac.columns:
        reac_cols.append("pt")
    elif "reaction" in reac.columns:
        reac_cols.append("reaction")
    reac_sel = reac[reac_cols].copy()

    outc_sel = pd.DataFrame()
    if not outc.empty:
        outc_cols = [key]
        if "outc_cod" in outc.columns:
            outc_cols.append("outc_cod")
        elif "outcome" in outc.columns:
            outc_cols.append("outcome")
        outc_sel = outc[outc_cols].copy()

    # Merge on key
    df = demo_sel.merge(drug_sel, on=key, how="left")\
                 .merge(reac_sel, on=key, how="left")
    if not outc_sel.empty:
        df = df.merge(outc_sel, on=key, how="left")

    # Normalize text fields and fill NaN
    for col in ["drugname", "pt", "outc_cod", "outcome"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.lower().str.strip()

    # Create unified columns with fallbacks
    df["drugname_final"] = df.get("drugname", df.get("drug", "")).fillna("").astype(str)
    df["pt_final"] = df.get("pt", df.get("reaction", "")).fillna("").astype(str)
    df["outcome_final"] = df.get("outc_cod", df.get("outcome", "")).fillna("").astype(str)

    # Create ae_text
    df["ae_text"] = (df["drugname_final"] + " | " + df["pt_final"] + " | " + df["outcome_final"]).str.replace(r'\s+', ' ', regex=True).str.strip()

    # Parse event date safely
    if "event_dt" in df.columns:
        df["event_dt_parsed"] = pd.to_datetime(df["event_dt"], errors="coerce")
    elif "mfr_dt" in df.columns:
        df["event_dt_parsed"] = pd.to_datetime(df["mfr_dt"], errors="coerce")
    else:
        df["event_dt_parsed"] = pd.NaT

    df["week"] = df["event_dt_parsed"].dt.to_period("W").astype(str)

    # Keep useful columns and the join key
    keep_cols = [key, "drugname_final", "pt_final", "outcome_final", "ae_text", "event_dt_parsed", "week"]
    for c in keep_cols:
        if c not in df.columns:
            df[c] = None

    df = df[keep_cols]

    # rename key column to PRIMARYID for consistency (if original key was caseid, keep it)
    if key != "primaryid":
        df = df.rename(columns={key: "primaryid"})

    df = df.rename(columns={"event_dt_parsed": "event_dt", "drugname_final": "drugname", "pt_final": "pt", "outcome_final": "outcome"})

    return df

def main():
    if not BASE.exists():
        raise SystemExit(f"Folder {BASE} does not exist. Put FAERS ASCII files under data/ASCII/")
    print("Loading FAERS files from", BASE)
    demo, drug, reac, outc = load_faers_ascii()
    print("Files loaded. Building master dataframe...")
    df = build_master_df(demo, drug, reac, outc)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print("Saved:", OUT_CSV)
    print("Rows:", len(df))
    print("Columns:", list(df.columns)[:20])

if __name__ == "__main__":
    main()
