"""
RAW PEEK — just show us what is in the files, nothing else.
Run: python raw_peek.py
Files expected in same directory: 1496.txt and 1497.txt
"""

import gzip
from pathlib import Path

FILES = ["1496.txt", "1497.txt"]

for filename in FILES:
    print(f"\n{'='*60}")
    print(f"FILE: {filename}")
    print(f"{'='*60}")

    p = Path(filename)
    if not p.exists():
        p = Path(filename + ".gz")
    if not p.exists():
        print(f"  NOT FOUND: {filename}")
        continue

    print(f"Size: {p.stat().st_size / 1_048_576:.1f} MB")

    # Open file
    if str(p).endswith(".gz"):
        fh = gzip.open(p, "rt")
    else:
        fh = open(p, "r")

    print(f"\n--- First 10 raw lines ---")
    with fh:
        for i, line in enumerate(fh):
            if i >= 10:
                break
            print(f"[{i}] {repr(line[:200])}")

    print(f"\n--- Line count (counting...) ---")
    if str(p).endswith(".gz"):
        fh2 = gzip.open(p, "rt")
    else:
        fh2 = open(p, "r")
    count = 0
    with fh2:
        for _ in fh2:
            count += 1
    print(f"Total lines: {count:,}")
