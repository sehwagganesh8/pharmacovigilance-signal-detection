# src/inspect_ascii.py
import os
p = "data/ASCII"

print("Listing files in", p)
files = sorted(os.listdir(p))
for f in files:
    print(" -", f)
print()

# find the first DEMO file
demo_files = [f for f in files if f.upper().startswith("DEMO")]
if not demo_files:
    raise SystemExit("No DEMO file found in data/ASCII")

demo = os.path.join(p, demo_files[0])
print("Inspecting file:", demo)
print("-" * 60)

# show first 20 lines raw
with open(demo, "r", encoding="latin1", errors="ignore") as fh:
    for i in range(20):
        line = fh.readline()
        if not line:
            break
        print(f"{i+1:02d}> {line.rstrip()}")

print("\nNow showing how the first header line splits by common separators:")
with open(demo, "r", encoding="latin1", errors="ignore") as fh:
    header = fh.readline().rstrip()
    seps = ["$", "|", "^", "\t", ",", ";", "~"]
    for s in seps:
        parts = header.split(s)
        print(f"sep='{s}' -> {len(parts)} fields (first 8 fields): {parts[:8]}")
