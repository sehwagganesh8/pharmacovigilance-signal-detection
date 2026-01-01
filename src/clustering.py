# src/clustering.py
import argparse
import numpy as np
import pandas as pd

def run_hdbscan(emb):
    import hdbscan
    clusterer = hdbscan.HDBSCAN(min_cluster_size=20, prediction_data=True)
    labels = clusterer.fit_predict(emb)
    return labels

def run_dbscan(emb):
    from sklearn.cluster import DBSCAN
    db = DBSCAN(metric="cosine", eps=0.35, min_samples=5, n_jobs=-1)
    labels = db.fit_predict(emb)
    return labels

def main(emb_path, input_csv, out_csv):
    print("Loading embeddings:", emb_path)
    emb = np.load(emb_path).astype(np.float32)
    print("Embedding shape:", emb.shape)

    print("Loading dataset:", input_csv)
    df = pd.read_csv(input_csv)

    if len(df) != len(emb):
        raise ValueError(f"Row mismatch: df has {len(df)}, embeddings have {len(emb)}")

    labels = None
    try:
        print("Attempting HDBSCAN clustering...")
        labels = run_hdbscan(emb)
        print("HDBSCAN succeeded.")
    except Exception as e:
        print("HDBSCAN failed or incompatible. Falling back to DBSCAN.")
        print("HDBSCAN error:", repr(e))
        labels = run_dbscan(emb)

    df["cluster"] = labels
    print("Cluster counts (top 20):")
    print(df["cluster"].value_counts().head(20))

    print(f"Saving clustered data to {out_csv}")
    df.to_csv(out_csv, index=False)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emb", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    main(args.emb, args.input, args.out)
#this is clustering file