"""
Quick diagnostic — print full structure of first 3 LP cache files
to find where coordinates are stored.
"""
import os, json

LP_CACHE = "lp_cache"
files = [f for f in os.listdir(LP_CACHE) if f.endswith(".json")][:3]

for fname in files:
    path = os.path.join(LP_CACHE, fname)
    with open(path) as f:
        data = json.load(f)
    print(f"\n{'='*60}")
    print(f"FILE: {fname}")
    print(json.dumps(data, indent=2))
