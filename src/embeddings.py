# src/embeddings.py
import argparse
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def main(input_csv, out_path="data/embeddings.npy"):
    print("Loading dataset:", input_csv)
    df = pd.read_csv(input_csv)

    if "ae_text" not in df.columns:
        raise ValueError("Column 'ae_text' not found in input CSV.")

    texts = df["ae_text"].fillna("").astype(str).tolist()

    print("Loading embedding model (this may take 5–10 seconds)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Encoding", len(texts), "rows...")
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True)

    np.save(out_path, embeddings)
    print("Saved embeddings to", out_path)
    print("Embedding shape:", embeddings.shape)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to CSV containing ae_text column")
    parser.add_argument("--out", default="data/embeddings.npy", help="output .npy file")
    args = parser.parse_args()
    main(args.input, args.out)
