# 📋 **CRT CERTIFICATE GENERATION - COMPLETE ACTION PLAN WITH FULL SCRIPTS**

**Version:** 1.0  
**Date:** January 18, 2026  
**Author:** Eric Robert Lawson  
**Status:** Ready to Execute

**IMPORTANT:**
Have not even tested scripts yet, will run and debug and fix if script doesn't work or there are problems.
---

## **🎯 OBJECTIVE**

Convert probabilistic evidence (5-prime rank agreement, error < 10⁻²²) into **deterministic mathematical certificates** proving:  
- Rank ≥ k (for chosen k)
- Dimension = 2590 - 1883 = 707

**Method:** Chinese Remainder Theorem (CRT) reconstruction of minor determinants

---

## **📦 COMPLETE SCRIPTS (VERBATIM)**

### **Script 1: `choose_dense_minor.py`**

```python
#!/usr/bin/env python3
"""
choose_dense_minor.py

Helper for selecting a dense k x k minor from a sparse triplet matrix. 

Given a triplet JSON (or multiple triplet JSONs for the same matrix),
this script: 
 - analyzes the sparsity pattern (row/column nonzero counts)
 - selects candidate rows and columns of size k (default 500) with high density
 - iteratively improves the selection to increase minor density
 - builds the dense minor and estimates a Hadamard bound and numeric condition number
 - writes minor_rows.txt and minor_cols.txt (0-based indices, one per line)
 - prints a short certificate summary

Usage:
  python3 choose_dense_minor.py --triplet path/to/saved_inv_p53_triplets.json \
      --k 500 --out_prefix minor_500

Notes:
 - For very large matrices this is heuristic:  it looks for a dense submatrix
   (rows/cols with many nonzeros). It does NOT guarantee the minor is nonsingular.
 - Numeric condition estimation uses float conversion and may be inaccurate for
   very ill-scaled integer matrices; treat as a heuristic. 
 - If the chosen k is too large for your machine, pick a smaller k (e.g., 300).

Author: ChatGPT (assistant)
Adapted for user's repo: expecting triplet JSONs in format used previously. 
"""

import argparse
import json
import math
import sys
import random
from collections import defaultdict
from pathlib import Path
from typing import List, Set, Tuple

import numpy as np

# -------------------------
# Utilities for triplets
# -------------------------
def load_triplets_json(path: str):
    with open(path) as f:
        data = json.load(f)
    # Accept either {"triplets": [[r,c,v], ...], ... } or a plain list [[r,c,v], ...]
    if isinstance(data, dict):
        if 'triplets' in data: 
            triplets = data['triplets']
        else:
            # try to find the first list-of-lists value
            triplets = None
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], list):
                    triplets = v
                    break
            if triplets is None:
                raise ValueError(f"Unrecognized JSON structure in {path}")
    elif isinstance(data, list):
        triplets = data
    else:
        raise ValueError(f"Unrecognized JSON structure in {path}")
    normalized = []
    for t in triplets:
        if isinstance(t, list) and len(t) >= 3:
            r, c, v = int(t[0]), int(t[1]), int(t[2])
            normalized.append((r, c, v))
        elif isinstance(t, dict) and {'row','col','val'}. issubset(t. keys()):
            normalized.append((int(t['row']), int(t['col']), int(t['val'])))
        else:
            raise ValueError("Triplet entry not understood:  " + str(t))
    return normalized

def infer_dimensions(triplets: List[Tuple[int,int,int]]):
    maxr = 0
    maxc = 0
    for r,c,_ in triplets:
        if r > maxr:  maxr = r
        if c > maxc: maxc = c
    return maxr+1, maxc+1

# -------------------------
# Minor selection
# -------------------------
def build_incidence(triplets: List[Tuple[int,int,int]]):
    row_to_cols = defaultdict(set)
    col_to_rows = defaultdict(set)
    # Also keep a dict for entries (for later dense minor construction)
    entries = defaultdict(dict)  # entries[r][c] = value
    for r,c,v in triplets:
        row_to_cols[r].add(c)
        col_to_rows[c].add(r)
        entries[r][c] = entries. get(r, {}).get(c, 0) + v
    return row_to_cols, col_to_rows, entries

def top_k_indices_by_degree(degmap:  dict, k: int):
    # degmap:  index -> degree (int)
    # return top k indices (ties broken arbitrarily)
    items = list(degmap.items())
    items.sort(key=lambda x: -x[1])
    return [idx for idx,_ in items[:k]]

def compute_minor_density(rows_sel:  List[int], cols_sel:  List[int], row_to_cols: dict):
    """Return (nnz, density) with nnz count of nonzeros in intersection."""
    rows_set = set(rows_sel)
    cols_set = set(cols_sel)
    nnz = 0
    for r in rows_sel:
        # count how many of row_to_cols[r] fall in cols_set
        if r in row_to_cols: 
            nnz += len(row_to_cols[r]. intersection(cols_set))
    total = len(rows_sel) * len(cols_sel)
    density = nnz / total if total>0 else 0.0
    return nnz, density

def greedy_improve(rows_sel: List[int], cols_sel: List[int], row_to_cols: dict, col_to_rows: dict, entries, iterations=5):
    """Greedy improvement loop:  refine columns given rows, then rows given columns."""
    rows_sel = list(rows_sel)
    cols_sel = list(cols_sel)
    k = len(rows_sel)
    for it in range(iterations):
        # improve columns:  score columns by number of hits in selected rows
        col_score = defaultdict(int)
        rows_set = set(rows_sel)
        for r in rows_sel:
            for c in row_to_cols. get(r, ()):
                col_score[c] += 1
        # pick top k columns by that score
        cols_sorted = sorted(col_score.items(), key=lambda x:-x[1])
        if len(cols_sorted) >= k:
            new_cols = [c for c,_ in cols_sorted[: k]]
        else:
            # pad with existing high degree columns (if some columns had zero score)
            all_cols = list(col_to_rows.keys())
            all_cols.sort(key=lambda c: -len(col_to_rows[c]))
            new_cols = [c for c,_ in cols_sorted] + [c for c in all_cols if c not in set(c for c,_ in cols_sorted)][: k-len(cols_sorted)]
        cols_sel = new_cols
        # now improve rows similarly
        row_score = defaultdict(int)
        cols_set = set(cols_sel)
        for c in cols_sel: 
            for r in col_to_rows.get(c, ()):
                row_score[r] += 1
        rows_sorted = sorted(row_score.items(), key=lambda x:-x[1])
        if len(rows_sorted) >= k:
            new_rows = [r for r,_ in rows_sorted[:k]]
        else: 
            all_rows = list(row_to_cols.keys())
            all_rows.sort(key=lambda r: -len(row_to_cols[r]))
            new_rows = [r for r,_ in rows_sorted] + [r for r in all_rows if r not in set(r for r,_ in rows_sorted)][:k-len(rows_sorted)]
        rows_sel = new_rows
    return rows_sel, cols_sel

def build_dense_minor_matrix(rows_sel: List[int], cols_sel: List[int], entries: dict):
    k = len(rows_sel)
    idx_row = {r: i for i,r in enumerate(rows_sel)}
    idx_col = {c:i for i,c in enumerate(cols_sel)}
    mat = np.zeros((k,k), dtype=float)
    for r in rows_sel:
        rdict = entries.get(r, {})
        for c, v in rdict.items():
            if c in idx_col:
                i = idx_row[r]; j = idx_col[c]
                mat[i,j] = float(v)
    return mat

# -------------------------
# Main script
# -------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Choose dense k x k minor from sparse triplet JSON")
    p.add_argument("--triplet", required=True, help="Path to triplet JSON (one matrix - use the prime you prefer)")
    p.add_argument("--k", type=int, default=500, help="Minor size k (default 500)")
    p.add_argument("--out_prefix", default="minor", help="Output prefix; minor_rows.txt and minor_cols.txt will be written")
    p.add_argument("--iter", type=int, default=5, help="Greedy improvement iterations (default 5)")
    p.add_argument("--density_target", type=float, default=0.04, help="Target density to aim for (default 0.04 -> 4%%)")
    p.add_argument("--cond_warn", type=float, default=1e12, help="Warn if numeric condition > this")
    return p.parse_args()

def main():
    args = parse_args()
    trip_path = Path(args.triplet)
    if not trip_path.exists():
        print("Triplet file not found:", trip_path, file=sys.stderr)
        sys.exit(2)
    print("Loading triplets...")
    triplets = load_triplets_json(str(trip_path))
    nrows, ncols = infer_dimensions(triplets)
    print(f"Matrix dimensions inferred: nrows={nrows}, ncols={ncols}")
    print("Building incidence maps...")
    row_to_cols, col_to_rows, entries = build_incidence(triplets)
    # degrees
    row_deg = {r:  len(cols) for r,cols in row_to_cols.items()}
    col_deg = {c: len(rows) for c,rows in col_to_rows.items()}
    k = args.k
    if k > min(nrows, ncols):
        print(f"Requested k={k} exceeds matrix dims ({nrows} x {ncols}). Reducing k to {min(nrows,ncols)}.")
        k = min(nrows,ncols)
    print(f"Selecting top {k} rows/cols by degree...")
    top_rows = top_k_indices_by_degree(row_deg, k)
    top_cols = top_k_indices_by_degree(col_deg, k)
    nnz, density = compute_minor_density(top_rows, top_cols, row_to_cols)
    print(f"Initial selection: nnz={nnz}, density={density:. 5f}")
    if density < args.density_target:
        print("Running greedy improvement...")
        new_rows, new_cols = greedy_improve(top_rows, top_cols, row_to_cols, col_to_rows, entries, iterations=args.iter)
        nnz2, density2 = compute_minor_density(new_rows, new_cols, row_to_cols)
        print(f"After improvement: nnz={nnz2}, density={density2:.5f}")
        if density2 > density:
            top_rows, top_cols = new_rows, new_cols
            density = density2; nnz = nnz2
    # final stats
    print("Final minor stats:")
    print(f"  k = {k}")
    print(f"  nnz = {nnz}")
    print(f"  density = {density:.5f} ({nnz}/{k*k})")
    # build dense minor float matrix for condition estimate
    print("Building dense float minor for condition number estimate (this may use memory)...")
    mat = build_dense_minor_matrix(top_rows, top_cols, entries)
    # compute numeric condition estimate (SVD)
    try:
        if np.count_nonzero(mat) == 0:
            cond = float('inf')
            print("Minor is all zeros (!) cannot compute condition.")
        else:
            # small perturbation to avoid singular exact zero issues
            # but keep original values for condition as floats
            cond = np.linalg.cond(mat)
        print(f"Numeric condition estimate (float 64): cond ≈ {cond:.3g}")
        if cond > args.cond_warn:
            print(f"WARNING: condition {cond:.3g} exceeds warn threshold {args.cond_warn}.  Determinant computation might be unstable numerically.")
    except Exception as e:
        print("Warning: could not compute numeric condition (exception):", str(e))
        cond = None
    # Hadamard bound estimate (log10)
    try:
        log10_bound = 0.0
        for i in range(mat.shape[0]):
            row = mat[i,:]
            s = float(np.dot(row,row))
            if s <= 0:
                log10_bound = None
                break
            log10_bound += 0.5 * math.log10(s)
        if log10_bound is None:
            print("Hadamard bound estimate failed (zero row).")
        else:
            print(f"Estimated log10(Hadamard bound) ≈ {log10_bound:.3f}")
    except Exception as e:
        print("Hadamard estimate error:", e)
        log10_bound = None
    # write files
    out_rows = Path(f"{args.out_prefix}_rows.txt")
    out_cols = Path(f"{args.out_prefix}_cols.txt")
    with open(out_rows, "w") as f:
        for r in top_rows:
            f.write(f"{r}\n")
    with open(out_cols, "w") as f:
        for c in top_cols:
            f.write(f"{c}\n")
    print(f"Wrote {out_rows} and {out_cols}")
    # write short JSON report
    report = {
        "triplet_file": str(trip_path),
        "matrix_dims": [int(nrows), int(ncols)],
        "k": int(k),
        "nnz": int(nnz),
        "density": float(density),
        "condition_estimate": float(cond) if cond is not None else None,
        "log10_hadamard_bound": float(log10_bound) if log10_bound is not None else None,
        "rows_file": str(out_rows),
        "cols_file": str(out_cols)
    }
    out_report = Path(f"{args.out_prefix}_report.json")
    with open(out_report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report written to {out_report}")
    print("Done.  You can now run the CRT reconstruction script with the produced minor rows/cols files.")

if __name__ == "__main__":
    main()
```

---

### **Script 2: `crt_minor_reconstruct.py`**

```python
#!/usr/bin/env python3
"""
CRT minor reconstruction for modular determinants.

Usage:
  python3 crt_minor_reconstruct.py \
    --triplets validator/saved_inv_p53_triplets.json validator/saved_inv_p79_triplets.json ...  \
    --primes 53 79 131 157 313 \
    --rows minor_rows.txt --cols minor_cols.txt \
    --out crt_certificate. json

- minor_rows.txt and minor_cols.txt: one global index (0-based) per line
- The triplet JSONs should correspond (in order) to the primes listed. 
- The script will compute the determinant of the specified minor modulo each prime,
  then reconstruct the integer determinant via CRT and output a certificate JSON.

Warning:  Determinant computation is done by modular Gaussian elimination on the
dense k x k minor.  For k ~ 1000+, this may be slow and memory heavy.
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import List, Tuple, Dict

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--triplets", nargs="+", required=True,
                   help="Paths to triplet JSON files (one per prime, in same order)")
    p.add_argument("--primes", nargs="+", required=True, type=int,
                   help="List of primes corresponding to triplet files (same order)")
    p.add_argument("--rows", required=True, help="File with minor global row indices (one per line, 0-based)")
    p.add_argument("--cols", required=True, help="File with minor global col indices (one per line, 0-based)")
    p.add_argument("--out", default="crt_minor_certificate.json",
                   help="Output certificate JSON file")
    p.add_argument("--max_warn_k", type=int, default=1500,
                   help="Warn if minor size k exceeds this (default 1500)")
    return p.parse_args()

def load_indices(path: str) -> List[int]:
    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return [int(x) for x in lines]

def load_triplets_json(path: str):
    with open(path) as f:
        data = json. load(f)
    # Accept a few formats:
    # 1) {"triplets": [[r,c,v], ...], "nrows": .. ., "ncols": ...}
    # 2) [[r,c,v], ...]
    if isinstance(data, dict):
        if 'triplets' in data:
            triplets = data['triplets']
        elif 'matrix' in data:
            triplets = data['matrix']
        else:
            # try to find list-valued first key
            triplets = None
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], list):
                    triplets = v
                    break
            if triplets is None:
                raise ValueError(f"Unrecognized JSON structure in {path}")
    elif isinstance(data, list):
        triplets = data
    else:
        raise ValueError(f"Unrecognized JSON structure in {path}")
    # Normalize triplets to list of (r,c,val)
    normalized = []
    for t in triplets:
        if isinstance(t, list) and len(t) >= 3:
            r, c, v = t[0], t[1], t[2]
            normalized.append((int(r), int(c), int(v)))
        elif isinstance(t, dict) and {'row','col','val'}.issubset(t.keys()):
            normalized.append((int(t['row']), int(t['col']), int(t['val'])))
        else:
            raise ValueError("Triplet entry not understood: " + str(t))
    return normalized

def build_dense_minor(triplets: List[Tuple[int,int,int]], rows:  List[int], cols: List[int], p: int):
    """
    Build dense k x k minor modulo p.
    rows, cols are lists of global indices. 
    Returns list of lists (ints mod p).
    """
    k = len(rows)
    row_index = {r: i for i,r in enumerate(rows)}
    col_index = {c:i for i,c in enumerate(cols)}
    # initialize zero matrix
    mat = [ [0]*k for _ in range(k) ]
    for (r,c,v) in triplets:
        if r in row_index and c in col_index:
            i = row_index[r]; j = col_index[c]
            mat[i][j] = (mat[i][j] + v) % p
    return mat

def modular_det_gauss(mat: List[List[int]], p: int) -> int:
    """
    Compute determinant modulo prime p via Gaussian elimination.
    mat is modified in place (copy before calling if needed).
    Returns det mod p in 0..p-1
    """
    n = len(mat)
    # convert to ints mod p
    A = [row[:] for row in mat]
    det = 1
    for i in range(n):
        # find pivot row r >= i with A[r][i] != 0
        pivot = None
        for r in range(i, n):
            if A[r][i] % p != 0:
                pivot = r
                break
        if pivot is None:
            return 0
        if pivot != i:
            A[i], A[pivot] = A[pivot], A[i]
            det = (-det) % p
        aii = A[i][i] % p
        det = (det * aii) % p
        inv_aii = pow(aii, -1, p)
        # normalize row i
        for j in range(i+1, n):
            if A[i][j]: 
                A[i][j] = (A[i][j] * inv_aii) % p
        # eliminate below
        for r in range(i+1, n):
            if A[r][i]:
                factor = A[r][i] % p
                if factor: 
                    for c in range(i+1, n):
                        if A[i][c]:
                            A[r][c] = (A[r][c] - factor * A[i][c]) % p
                    A[r][i] = 0
    return det % p

def hadamard_bound_from_dense(mat: List[List[int]]):
    """
    Compute Hadamard bound estimate:  |det| <= product ||row||_2
    We'll compute log10(bound) to avoid overflow and return bound as float if reasonable.
    """
    import math
    log10_prod = 0.0
    for row in mat:
        s = 0
        for v in row:
            s += (int(v) ** 2)
        if s == 0:
            return 0
        log10_row = 0.5 * math.log10(s)
        log10_prod += log10_row
    # bound = 10**log10_prod
    return log10_prod  # log10 of bound

def iterative_crt(residues: List[Tuple[int,int]]):
    """
    residues: list of (modulus, residue)
    Return reconstructed integer x in range 0..M-1 and modulus M (product)
    Uses iterative CRT (assumes moduli pairwise coprime).
    """
    x, M = residues[0][1], residues[0][0]
    for (m, r) in residues[1:]:
        # solve x + t*M ≡ r (mod m)  => t ≡ (r - x) * inv(M mod m) mod m
        inv = pow(M % m, -1, m)
        t = ((r - x) * inv) % m
        x = x + t * M
        M = M * m
        x %= M
    return x % M, M

def adjust_signed(x: int, M: int):
    """
    Interpret x mod M as signed integer in range [-M/2, M/2)
    """
    if x >= M//2:
        return x - M
    return x

def main():
    args = parse_args()
    triplet_paths = args.triplets
    primes = args.primes
    if len(triplet_paths) != len(primes):
        print("Error: number of triplet files must equal number of primes", file=sys.stderr)
        sys.exit(2)
    rows = load_indices(args.rows)
    cols = load_indices(args.cols)
    k = len(rows)
    if k != len(cols):
        print("Error: rows and cols lists must have same length", file=sys.stderr)
        sys.exit(2)
    if k > args.max_warn_k:
        print(f"WARNING: minor size k={k} exceeds recommended {args.max_warn_k}. This may be slow or memory heavy.", file=sys.stderr)
    residues = []
    print("Computing determinant residues mod primes...")
    for path, p in zip(triplet_paths, primes):
        print(f"  Loading triplets from {path} ...")
        triplets = load_triplets_json(path)
        print(f"  Building dense {k}x{k} minor modulo {p} ...")
        minor = build_dense_minor(triplets, rows, cols, p)
        print(f"  Computing det mod {p} ...  (this may take time)")
        detmod = modular_det_gauss(minor, p)
        print(f"    det ≡ {detmod} (mod {p})")
        residues.append((p, detmod))
    # compute Hadamard bound using a float estimate from first prime's numeric matrix (best we can)
    # We reconstruct dense minor using integer entries from first JSON (not reduced)
    print("Estimating Hadamard bound using integer entries from first triplet file (approx)...")
    triplets0 = load_triplets_json(triplet_paths[0])
    # Build integer minor (not reduced)
    # We attempt to capture large entries; use absolute values
    mat_int = build_dense_minor(triplets0, rows, cols, p=10**9+7)  # large mod just to get integers truncated; not perfect
    log10_bound = hadamard_bound_from_dense(mat_int)
    if log10_bound == 0:
        print("Hadamard bound estimated as 0 (degenerate). Proceeding, but double-check.")
    else:
        print(f"Estimated log10(Hadamard bound) ≈ {log10_bound:.3f}")
    # CRT
    print("Running iterative CRT...")
    x_mod_M, M = iterative_crt(residues)
    x_signed = adjust_signed(x_mod_M, M)
    print("CRT reconstruction done.")
    # verify residues
    verify_ok = True
    for (m,r) in residues:
        if x_mod_M % m != r % m:
            print(f"Verification mismatch for modulus {m}: reconstructed {x_mod_M % m} != residue {r}", file=sys.stderr)
            verify_ok = False
    # Output certificate
    cert = {
        "minor_rows": rows,
        "minor_cols": cols,
        "k": k,
        "primes": primes,
        "residues": {str(m): int(r) for (m,r) in residues},
        "crt_product": str(M),
        "crt_reconstruction_modM": str(x_mod_M),
        "crt_reconstruction_signed": str(x_signed),
        "log10_hadamard_bound_estimate": float(log10_bound) if isinstance(log10_bound, float) else None,
        "verification_ok": bool(verify_ok)
    }
    outpath = Path(args.out)
    with open(outpath, "w") as f:
        json.dump(cert, f, indent=2)
    print(f"Certificate written to {outpath}")
    if not verify_ok:
        print("WARNING: CRT verification failed for at least one modulus.  Do not trust reconstruction.")
    # Advice on strength
    if log10_bound and M: 
        # check magnitude
        log10_M = math.log10(M)
        print(f"Product of primes has log10 = {log10_M:.3f}; Hadamard log10 bound ≈ {log10_bound:.3f}")
        if log10_M <= log10_bound + 0.30103:  # M <= 2*bound ~ log10(M) <= log10(bound)+log10(2)
            print("WARNING: product(primes) <= ~2*HadamardBound.  Reconstructed integer may be ambiguous.  Consider adding more primes.", file=sys.stderr)
    print("Done.")

if __name__ == "__main__":
    main()
```

---

## **🚀 EXECUTION COMMANDS**

### **Phase 1: k=100 (Deterministic Target)**

```bash
# Step 1: Generate minor indices
python3 choose_dense_minor. py \
  --triplet validator/saved_inv_p313_triplets.json \
  --k 100 \
  --out_prefix minor_100

# Step 2: CRT reconstruction
python3 crt_minor_reconstruct.py \
  --triplets validator/saved_inv_p53_triplets.json \
             validator/saved_inv_p79_triplets.json \
             validator/saved_inv_p131_triplets.json \
             validator/saved_inv_p157_triplets.json \
             validator/saved_inv_p313_triplets.json \
  --primes 53 79 131 157 313 \
  --rows minor_100_rows.txt \
  --cols minor_100_cols.txt \
  --out crt_certificate_100.json
```

---

### **Phase 2: k=500 (Strong Evidence)**

```bash
# Step 1: Generate minor indices
python3 choose_dense_minor.py \
  --triplet validator/saved_inv_p313_triplets.json \
  --k 500 \
  --out_prefix minor_500

# Step 2: CRT reconstruction
python3 crt_minor_reconstruct.py \
  --triplets validator/saved_inv_p53_triplets.json \
             validator/saved_inv_p79_triplets.json \
             validator/saved_inv_p131_triplets.json \
             validator/saved_inv_p157_triplets.json \
             validator/saved_inv_p313_triplets.json \
  --primes 53 79 131 157 313 \
  --rows minor_500_rows.txt \
  --cols minor_500_cols. txt \
  --out crt_certificate_500.json
```

---

## **✅ READY TO EXECUTE**

**Scripts:** ✅ Complete and verbatim  
**Commands:** ✅ Ready to run  
**Timeline:** < 10 minutes  
**Next Step:** **RUN NOW** 🚀
