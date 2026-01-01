# src/dashboard.py
import json, os
import pandas as pd
import matplotlib.pyplot as plt

def make_dashboard(enriched_json, out_json="outputs/dashboard.json", plots_dir="outputs/plots", top_n=10):
    with open(enriched_json) as f:
        data = json.load(f)

    # sort signals by count and take top_n
    signals = sorted(data["signals"], key=lambda s: s["count"], reverse=True)[:top_n]
    # basic summary metrics
    summary = {
        "total_signals": data["total_signals"],
        "top_signals": signals
    }
    os.makedirs(plots_dir, exist_ok=True)

    # create simple bar chart for top_n counts
    names = [f"{s['drug']} | {s['reaction']}" for s in signals]
    counts = [s["count"] for s in signals]
    plt.figure(figsize=(10,6))
    plt.barh(range(len(names))[::-1], counts[::-1])
    plt.yticks(range(len(names))[::-1], names[::-1])
    plt.xlabel("Report count")
    plt.title("Top signals")
    plt.tight_layout()
    png = os.path.join(plots_dir, "top_signals.png")
    plt.savefig(png)
    plt.close()
    summary["plots"] = {"top_signals": png}

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Wrote dashboard:", out_json)
    print("Plot saved to:", png)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--enriched", required=True)
    p.add_argument("--out", default="outputs/dashboard.json")
    p.add_argument("--plots", default="outputs/plots")
    p.add_argument("--top", type=int, default=10)
    args = p.parse_args()
    make_dashboard(args.enriched, args.out, args.plots, args.top)
