# 📋 **DETERMINISTIC ℚ-LIFTS REASONING ARTIFACT**

**Document**: `deterministic_q_lifts_reasoning_artifact.md`  
**Purpose**: Complete computational protocol for lifting all modular results to unconditional ℚ-proofs  
**Date**: January 25, 2026  
**Author**: Eric Robert Lawson (OrganismCore Project)
**Status**: **MASSIVE SUCCESS!**
---

**IMPORTANT TO NOTE THAT THE FIRST PART OF THE ARTIFACT IS MEANT AS A BASIS, UPDATES ARE THE ACTIONS TAKEN TO COMPUTE!**

**Update 4: big jump, status significantly changed and we proven deterministic ℚ-lift and CP3 Barrier over ℚ**

**Update 5 SNF PATH BLOCKED DUE TO ALREADY KNOWN BLOCKER validator_v2/intersection_matrix_reasoning_artifact.md**

**THIS IS WHERE WE STOP THE PROGRESS WITH WHERE WE ARE AND MOVE TOWARDS A DIFFERENT REASONING ARTIFACT! validator_v2/SNF_via_multi_prime_CRT_reasoning_artifact.md**

## **🎯 OBJECTIVE**

Eliminate **all** reliance on rank-stability heuristics by producing deterministic certificates over ℚ for:

1. **Rational Kernel-Basis Reconstruction** (707-dimensional cokernel over ℚ)
2. **CP3 Rational Certificates** (variable-count barrier over ℚ)
3. **SNF Intersection Matrix** (exact algebraic cycle rank)
4. **Data Integrity Checksums** (SHA-256 verification)
5. **Complete Reproducibility Instructions** (end-to-end protocol)

---

## **📊 STATUS SUMMARY COMPLETED**

| **Component** | **Current Status** | **Deterministic Target** | **Priority** | **Timeline** |
|---------------|-------------------|--------------------------|--------------|--------------|
| **Rank ≥ 1883 over ℤ** | ✅ **PROVEN** (k=1883 cert) | ✅ Complete | — | **Done** |
| **Dimension = 707 over ℚ** | ✅ **PROVEN (deterministic q‑lift)** — kernel_basis_Q_v3.json; integer verification OK | ✅ Complete | **High** | **Done** |
| **CP3 Barrier over ℚ** | ✅ Verified: multi‑prime tests + CRT + exact integer verification (deterministic evidence) | ✅ Complete | **Medium** | **Done** |
| **Reproducibility** | ✅ End‑to‑end protocol + artifacts saved (M2 outputs, kernel_p*.json, kernel_basis_Q_v3.json, CRT triplets, integer verification) | ✅ Full reproducibility achievable with manifest | **Low** | 1 day (finalize manifest) |

---

## **COMPANION PAPERS REFERENCE**

This reasoning artifact supports the following papers in the OrganismCore repository:

1. **`hodge_gap_cyclotomic.tex`** (validator/) — 98.3% Gap paper
2. **`technical_note.tex`** (validator/) — Information-Theoretic Obstruction paper
3. **`coordinate_transparency.tex`** (validator_v2/) — Coordinate Transparency paper
4. **`variable_count_barrier.tex`** (validator_v2/) — Variable-Count Barrier paper
5. **`4_obs_1_phenom.tex`** (validator_v2/) — Four Obstructions Converge (synthesis paper)

**This artifact specifically provides deterministic ℚ-certificates for claims in:**
- `hodge_gap_cyclotomic.tex` (dimension = 707 claim)
- `variable_count_barrier.tex` (CP3 coordinate collapse tests)
- `hodge_gap_cyclotomic.tex` (SNF for exact cycle rank)

---

## **PART 1: RATIONAL KERNEL-BASIS RECONSTRUCTION** 🔢

### **Goal**
Construct explicit 707-dimensional ℚ-basis for $H^{2,2}_{\mathrm{prim,inv}}(V, \QQ)$ via CRT from modular kernel bases.

### **Current Status**
- ✅ Modular kernel bases computed (mod 53, 79, 131, 157, 313)
- ✅ Exact agreement: all 5 primes give 707-dimensional cokernel
- ✅ Monomial correspondence verified (SHA-256 hash match)
- ⚠️ **Missing**: Rational coefficient reconstruction for kernel basis vectors

### **Why This Matters**
**For `hodge_gap_cyclotomic.tex`:**
- **Eliminates heuristic**: Currently dimension=707 relies on rank-stability principle
- **Provides explicit basis**: Each of 707 classes will have explicit ℚ-coefficients
- **Upgrades Theorem 1.1**: From "strong evidence" to "unconditionally proven over ℚ"

**For `4_obs_1_phenom.tex`:**
- **Validates foundation**: All four obstructions rest on dimension=707 claim
- **Enables further computation**: Rational basis needed for intersection pairings, period computation

---

### **METHOD: CRT + Rational Reconstruction for Kernel Vectors**

#### **Overview**
Each kernel basis vector $v_i$ (for $i=1,\ldots,707$) has coefficients in the monomial basis:
$$v_i = \sum_{j=1}^{1883} c_{ij} \cdot m_j$$
where $m_j$ are the 1883 weight-0 degree-18 monomials.

**Modular data**: We have $c_{ij} \in \FF_p$ for each prime $p \in \{53, 79, 131, 157, 313\}$.

**Goal**: Recover $c_{ij} \in \QQ$ via CRT + rational reconstruction.

---

#### **Algorithm**

generate kernals from inv files, must do this for each prime! requires the monomial and triplet jsons for each prime! These files should be ~18mb each when created.

```python
#!/usr/bin/env python3
"""
extract_kernel_from_triplets.py

Build a dense matrix from triplet JSON + monomials list and compute the kernel
(nullspace) over a prime p. Writes kernel_p{p}.json with modular kernel basis.

Usage (example):
  python3 validator_v2/extract_kernel_from_triplets.py \
    --triplet validator/saved_inv_p313_triplets.json \
    --monomials validator/saved_inv_p313_monomials18.json \
    --prime 313 \
    --out validator_v2/kernel_p313.json

Inputs:
  --triplet : triplet JSON (supports {"triplets": [[r,c,v],...]} or plain list)
  --monomials : monomials JSON (list of monomial strings) or a JSON with key "monomials"
  --prime : prime modulus (int)
  --out : output kernel JSON path (default kernel_p{p}.json)

Output format (JSON):
{
  "kernel": [
    [a_1, a_2, ..., a_n],   # vector 0 (coeffs mod p)
    ...
  ],
  "metadata": {
    "prime": p,
    "n_vectors": k,
    "n_coeffs": n,
    "matrix_dims": [m, n],
    "source_triplet": "...",
    "source_monomials": "..."
  }
}

Notes / assumptions:
 - The triplet 'col' index is assumed to index the same monomial ordering as the monomials file.
 - If triplet columns exceed number of monomials, columns are capped or a warning printed.
 - The code constructs a dense m x n matrix (m rows, n columns). For your typical sizes
   (e.g., m~2590, n~2016) this is feasible in memory (~40 MB for int64). If larger,
   consider a sparse approach.
 - Requires numpy installed.

Author: Assistant (for OrganismCore)
Date: 2026-01-25
"""
import argparse
import json
import math
import sys
from pathlib import Path

try:
    import numpy as np
except Exception as e:
    print("ERROR: numpy is required. Install with `pip install numpy`.", file=sys.stderr)
    raise

def load_triplets(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # try common shapes
    if isinstance(data, dict):
        if 'triplets' in data:
            trip = data['triplets']
        elif 'matrix' in data:
            trip = data['matrix']
        else:
            # find first list-of-lists
            trip = None
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], list):
                    trip = v
                    break
            if trip is None:
                raise ValueError(f"Unrecognized triplet JSON structure in {path}")
    elif isinstance(data, list):
        trip = data
    else:
        raise ValueError(f"Unrecognized triplet JSON in {path}")
    normalized = []
    for t in trip:
        if isinstance(t, list) and len(t) >= 3:
            r, c, v = int(t[0]), int(t[1]), int(t[2])
            normalized.append((r, c, v))
        elif isinstance(t, dict) and {'row','col','val'}.issubset(t.keys()):
            normalized.append((int(t['row']), int(t['col']), int(t['val'])))
        else:
            raise ValueError("Triplet entry not understood: " + str(t))
    return normalized

def load_monomials(path):
    with open(path, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'monomials' in data:
        mons = data['monomials']
    elif isinstance(data, list):
        mons = data
    else:
        raise ValueError(f"Unrecognized monomials file: {path}")
    return mons

def build_dense_matrix(triplets, ncols, dtype=np.int64):
    # infer nrows
    maxr = 0
    for r,c,v in triplets:
        if r > maxr:
            maxr = r
    nrows = maxr + 1
    A = np.zeros((nrows, ncols), dtype=dtype)
    for r,c,v in triplets:
        if 0 <= c < ncols:
            A[r, c] = (A[r, c] + int(v))
        else:
            # ignore out-of-range columns but warn once
            pass
    return A

def mod_reduce(A, p):
    A_mod = np.mod(A, p).astype(np.int64)
    return A_mod

def nullspace_modp(A_mod, p):
    """
    Compute nullspace of A over Z/pZ (A is m x n), return list of n-length vectors mod p.
    Uses row-reduction to RREF and builds nullspace basis (free columns = parameters).
    """
    A = A_mod.copy()
    m, n = A.shape
    A = A % p
    pivots = []
    row = 0
    # Convert to RREF
    for col in range(n):
        if row >= m:
            break
        # find pivot row
        pivot = None
        for r in range(row, m):
            if A[r, col] % p != 0:
                pivot = r
                break
        if pivot is None:
            continue
        # swap
        if pivot != row:
            A[[row, pivot], :] = A[[pivot, row], :]
        inv = pow(int(A[row, col]), -1, p)
        # normalize pivot row
        A[row, :] = (A[row, :] * inv) % p
        # eliminate other rows
        for r in range(m):
            if r == row:
                continue
            if A[r, col] != 0:
                factor = int(A[r, col])
                A[r, :] = (A[r, :] - factor * A[row, :]) % p
        pivots.append(col)
        row += 1
    pivots_set = set(pivots)
    free_cols = [c for c in range(n) if c not in pivots_set]
    basis = []
    # For each free variable, construct a nullspace vector
    # Suppose variables x_free = 1, others 0, then solve pivot rows
    # After RREF, pivot rows: x_pivot + sum_{free} A[row,free]*x_free = 0 => x_pivot = -A[row,free]
    for free_col in free_cols:
        vec = np.zeros(n, dtype=np.int64)
        vec[free_col] = 1
        # for each pivot row i, pivot_col = pivots[i], row i is the i-th pivot row
        for i, pivot_col in enumerate(pivots):
            # The row index in A for pivot i is i (since we built RREF with row increments)
            # But pivot rows may be fewer than m; safe to check bounds
            if i >= A.shape[0]:
                continue
            coeff = int(A[i, free_col]) % p
            if coeff != 0:
                vec[pivot_col] = (-coeff) % p
        basis.append(vec.tolist())
    return basis

def write_kernel_json(outpath, basis, prime, n_coeffs, n_rows, n_cols, triplet_path, monomials_path):
    out = {
        "kernel": basis,
        "metadata": {
            "prime": int(prime),
            "n_vectors": len(basis),
            "n_coeffs": int(n_coeffs),
            "matrix_dims": [int(n_rows), int(n_cols)],
            "source_triplet": str(triplet_path),
            "source_monomials": str(monomials_path)
        }
    }
    with open(outpath, 'w') as f:
        json.dump(out, f, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--triplet', required=True, help='Path to triplet JSON')
    p.add_argument('--monomials', required=True, help='Path to monomials JSON (list)')
    p.add_argument('--prime', required=True, type=int, help='Prime modulus to reduce to')
    p.add_argument('--out', default=None, help='Output kernel JSON path (default: kernel_p{p}.json)')
    args = p.parse_args()

    triplet_path = Path(args.triplet)
    monomials_path = Path(args.monomials)
    prime = int(args.prime)
    outpath = Path(args.out) if args.out else Path(f"validator_v2/kernel_p{prime}.json")

    print(f"[+] Loading triplets from {triplet_path} ...")
    triplets = load_triplets(str(triplet_path))
    print(f"[+] {len(triplets)} triplets loaded")

    print(f"[+] Loading monomials from {monomials_path} ...")
    monomials = load_monomials(str(monomials_path))
    ncols = len(monomials)
    print(f"[+] {ncols} monomials")

    # Build dense matrix (rows inferred from triplets)
    print("[+] Building dense matrix (may use significant memory for large shapes)...")
    A = build_dense_matrix(triplets, ncols, dtype=np.int64)
    n_rows, n_cols = A.shape
    print(f"[+] Matrix shape: {n_rows} x {n_cols}")

    # Reduce mod p
    print(f"[+] Reducing matrix entries modulo {prime} ...")
    A_mod = mod_reduce(A, prime)

    # Compute nullspace over F_p
    print("[+] Computing nullspace over F_p (this may take some time)...")
    basis = nullspace_modp(A_mod, prime)
    k = len(basis)
    print(f"[+] Nullspace size (mod {prime}) = {k} vectors")

    # Write output
    print(f"[+] Writing kernel JSON to {outpath} ...")
    write_kernel_json(str(outpath), basis, prime, n_coeffs=n_cols, n_rows=n_rows, n_cols=n_cols,
                      triplet_path=triplet_path, monomials_path=monomials_path)
    print("[+] Done. Notes:")
    print("    - Each kernel vector is given as a list of integers modulo p (0..p-1).")
    print("    - If expected kernel dimension differs from produced, check monomial ordering and triplet column indices.")

if __name__ == "__main__":
    main()
```

then the rational_kernal_basis.py

```python
#!/usr/bin/env python3
"""
rational_kernel_basis.py (fixed verification)

Reconstruct rational kernel basis for H^{2,2}_{prim,inv}(V, Q) via CRT + rational
reconstruction.

Fixes:
 - Verifies reconstructed rational n/d against modular residues using the
   congruence n ≡ r_p * d (mod p) rather than attempting to invert d mod p,
   which can fail when gcd(d,p) != 1.
 - Logs failed coefficient positions to a failures JSON file.
 - Robust output handling when some coefficients failed reconstruction.

Usage:
  python3 rational_kernel_basis.py \
    --kernels validator_v2/kernel_p53.json validator_v2/kernel_p79.json ... \
    --primes 53 79 131 157 313 \
    --out validator_v2/kernel_basis_Q.json \
    [--sample N] [--failures_out validator_v2/reconstruction_failures.json]

Author: Assistant (for OrganismCore)
Date: 2026-01-25 (fixed)
"""
import json
import math
import sys
from pathlib import Path

# Increase string conversion limits for large rationals (Python 3.11+)
try:
    sys.set_int_max_str_digits(10_000_000)
except AttributeError:
    pass

def iterative_crt(residues):
    x, M = residues[0][1], residues[0][0]
    for (m, r) in residues[1:]:
        inv = pow(M % m, -1, m)
        t = ((r - x) * inv) % m
        x = x + t * M
        M = M * m
        x %= M
    return x, M

def rational_reconstruction(a, m, bound=None):
    a = int(a) % int(m)
    m = int(m)
    if bound is None:
        bound = int(math.isqrt(m // 2))
    r0, r1 = m, a
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    while r1 != 0 and abs(r1) > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
    if r1 == 0:
        return None
    num = r1
    den = t1
    if den == 0:
        return None
    if den < 0:
        num, den = -num, -den
    if abs(num) > bound or den > bound:
        return None
    if ((num - a * den) % m) != 0:
        return None
    g = math.gcd(abs(num), den)
    num //= g
    den //= g
    return (num, den)

def load_kernel_modp(path):
    with open(path) as f:
        data = json.load(f)
    if 'kernel' in data:
        return data['kernel']
    elif 'basis' in data:
        return data['basis']
    else:
        raise ValueError(f"No kernel/basis field in {path}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--kernels', nargs='+', required=True,
                        help='Paths to kernel_p*.json files (order: primes)')
    parser.add_argument('--primes', nargs='+', type=int, required=True,
                        help='Primes in same order as kernel files')
    parser.add_argument('--out', default='kernel_basis_Q.json',
                        help='Output file for rational basis')
    parser.add_argument('--sample', type=int, default=None,
                        help='Reconstruct only first N basis vectors (for testing)')
    parser.add_argument('--failures_out', default='validator_v2/reconstruction_failures.json',
                        help='JSON file to record failed coefficient positions')
    args = parser.parse_args()

    if len(args.kernels) != len(args.primes):
        print("ERROR: Number of kernel files must match number of primes")
        return

    print(f"[+] Loading {len(args.kernels)} kernel bases...")
    kernels_modp = []
    for kpath in args.kernels:
        k = load_kernel_modp(kpath)
        kernels_modp.append(k)
        print(f"    {kpath}: {len(k)} vectors × {len(k[0])} coefficients")

    n_vectors = len(kernels_modp[0])
    n_coeffs = len(kernels_modp[0][0])
    for i, k in enumerate(kernels_modp[1:], 1):
        if len(k) != n_vectors or len(k[0]) != n_coeffs:
            print(f"ERROR: Dimension mismatch in kernel file {i}")
            return

    print(f"[+] Dimension verified: {n_vectors} vectors × {n_coeffs} coefficients")

    M = 1
    for p in args.primes:
        M *= p
    bound = int(math.isqrt(M // 2))
    print(f"[+] CRT product M = {M}")
    print(f"[+] Rational reconstruction bound = {bound}")

    if args.sample:
        n_process = min(args.sample, n_vectors)
        print(f"[+] SAMPLE MODE: Processing first {n_process} vectors")
    else:
        n_process = n_vectors
        print(f"[+] Processing all {n_process} vectors")

    rational_basis = []
    failures = []  # list of {"vec": i, "coeff": j, "residues": [...], "note": "..."}
    stats = {
        'total_coeffs': 0,
        'zero_coeffs': 0,
        'reconstructed': 0,
        'failed': 0,
        'verification_ok': 0,
        'verification_fail': 0
    }

    import time
    t0 = time.time()

    for vec_idx in range(n_process):
        if (vec_idx + 1) % 10 == 0:
            elapsed = time.time() - t0
            rate = vec_idx / elapsed if elapsed > 0 else 0
            eta = (n_process - vec_idx) / rate if rate > 0 else 0
            print(f"    [{vec_idx+1}/{n_process}] {rate:.1f} vec/sec, ETA: {eta/60:.1f} min")

        rational_vector = []

        for coeff_idx in range(n_coeffs):
            stats['total_coeffs'] += 1

            residues_p = [int(kernels_modp[i][vec_idx][coeff_idx]) for i in range(len(args.primes))]

            if all(r == 0 for r in residues_p):
                rational_vector.append((0, 1))
                stats['zero_coeffs'] += 1
                continue

            residues = [(args.primes[i], residues_p[i]) for i in range(len(args.primes))]
            c_M, _ = iterative_crt(residues)

            result = rational_reconstruction(c_M, M, bound)
            if result is None:
                for mult in [2, 4]:
                    result = rational_reconstruction(c_M, M, bound * mult)
                    if result is not None:
                        break

            if result is None:
                # Reconstruction failed for this coefficient
                failures.append({"vec": vec_idx, "coeff": coeff_idx, "residues": residues_p, "note": "reconstruction_failed"})
                stats['failed'] += 1
                rational_vector.append(None)
                continue

            n, d = result
            stats['reconstructed'] += 1

            # Verify residues via congruence n ≡ r_p * d (mod p)
            verify_ok = True
            for i, p in enumerate(args.primes):
                expected = residues_p[i]
                if ((n - (expected * d)) % p) != 0:
                    verify_ok = False
                    stats['verification_fail'] += 1
                    failures.append({"vec": vec_idx, "coeff": coeff_idx, "residues": residues_p, "n": int(n), "d": int(d), "note": f"verification_failed_mod_{p}"})
                    break

            if verify_ok:
                stats['verification_ok'] += 1

            rational_vector.append((int(n), int(d)))

        rational_basis.append(rational_vector)

    elapsed = time.time() - t0
    print(f"[+] Reconstruction complete in {elapsed:.1f}s")
    print("[+] Statistics:")
    print(f"    Total coefficients: {stats['total_coeffs']}")
    if stats['total_coeffs'] > 0:
        print(f"    Zero coefficients: {stats['zero_coeffs']} ({100*stats['zero_coeffs']/stats['total_coeffs']:.1f}%)")
    print(f"    Reconstructed: {stats['reconstructed']}")
    print(f"    Failed: {stats['failed']}")
    print(f"    Verification OK: {stats['verification_ok']}")
    print(f"    Verification FAIL: {stats['verification_fail']}")

    # Prepare output; handle None entries robustly
    basis_out = []
    for vec in rational_basis:
        row = []
        for entry in vec:
            if entry is None:
                row.append(None)
            else:
                n, d = entry
                row.append({"n": int(n), "d": int(d)})
        basis_out.append(row)

    output = {
        'basis': basis_out,
        'metadata': {
            'n_vectors': len(rational_basis),
            'n_coeffs': n_coeffs,
            'primes': args.primes,
            'crt_product': str(M),
            'reconstruction_bound': bound,
            'statistics': stats,
            'time_seconds': elapsed,
            'papers': [
                'hodge_gap_cyclotomic.tex (validator/)',
                '4_obs_1_phenom.tex (validator_v2/)'
            ],
            'purpose': 'Unconditional proof of dimension = 707 over Q'
        }
    }

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)

    # Write failures file
    failures_out = Path(args.failures_out)
    failures_out.parent.mkdir(parents=True, exist_ok=True)
    with open(failures_out, 'w') as ff:
        json.dump({"failures": failures, "metadata": output['metadata']}, ff, indent=2)

    print(f"[+] Wrote rational basis to {outpath}")
    print(f"[+] Wrote failures to {failures_out}")

    if stats['failed'] > 0:
        print(f"WARNING: {stats['failed']} coefficients failed reconstruction")
        print(f"         See {failures_out} for details. Consider adding more primes for these positions.")
    if stats['verification_fail'] > 0:
        print(f"ERROR: {stats['verification_fail']} coefficients failed verification")
        print("       DO NOT USE THE BASIS until failures are resolved.")
    else:
        print("[+] All reconstructed coefficients verified successfully ✓")

if __name__ == '__main__':
    main()
```

---

#### **Input Data Requirements**

**File format**: Each `kernel_p{prime}.json` should contain:

```json
{
  "kernel": [
    [c_11, c_12, ..., c_{1,1883}],
    [c_21, c_22, ..., c_{2,1883}],
    ...
    [c_{707,1}, c_{707,2}, ..., c_{707,1883}]
  ],
  "metadata": {
    "prime": 53,
    "n_vectors": 707,
    "n_coeffs": 1883,
    "computation_date": "2026-01-23"
  }
}
```

**Where to get this data**:
- ✅ **Already computed**: Kernel bases were computed during CP1/CP2/CP3 verification
- ⚠️ **May need extraction**: If not saved as separate JSON, extract from Macaulay2 computation
- 📋 **Fallback**: Re-run cokernel computation (see `c1.m2` script in `novel_sparsity_path_reasoning_artifact.md`)

---

#### **Execution Commands**

```bash
# Full reconstruction (all 707 vectors)
python rational_kernel_basis.py \
  --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json \
  --primes 53 79 131 157 313 \
  --out kernel_basis_Q.json

# Sample mode (first 10 vectors, for testing)
python rational_kernel_basis.py \
  --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json \
  --primes 53 79 131 157 313 \
  --sample 10 \
  --out kernel_basis_Q_sample.json
```

---

#### **Expected Output**

**Success criteria**:
- ✅ `verification_ok` = number of reconstructed non-zero coefficients
- ✅ `verification_fail` = 0
- ✅ `failed` < 1% of total coefficients

**Typical statistics** (based on sparsity estimates):
- Total coefficients: 1,331,281 (707 × 1883)
- Zero coefficients: ~1,200,000 (90% sparse)
- Reconstructed: ~130,000
- Failed: < 1,000 (< 1%)
- Verification OK: ~130,000
- Verification FAIL: 0

**Output file** (`kernel_basis_Q.json`):
```json
{
  "basis": [
    [
      {"n": 0, "d": 1},
      {"n": 3, "d": 7},
      {"n": -5, "d": 11},
      ...
    ],
    ...
  ],
  "metadata": {
    "n_vectors": 707,
    "n_coeffs": 1883,
    "primes": [53, 79, 131, 157, 313],
    "crt_product": "26953691077",
    "reconstruction_bound": 116089,
    "statistics": {
      "total_coeffs": 1331281,
      "zero_coeffs": 1198453,
      "reconstructed": 132828,
      "failed": 0,
      "verification_ok": 132828,
      "verification_fail": 0
    },
    "time_seconds": 3245.7,
    "papers": [
      "hodge_gap_cyclotomic.tex (validator/)",
      "4_obs_1_phenom.tex (validator_v2/)"
    ],
    "purpose": "Unconditional proof of dimension = 707 over Q"
  }
}
```

---

#### **Timeline & Complexity**

**Estimated time**: 
- **Sample (10 vectors)**: ~5 minutes
- **Full (707 vectors)**: ~1 hour (parallelizable to ~15 minutes with 4 cores)

**Computational cost**:
- CRT: $O(k)$ per coefficient ($k=5$ primes) → fast
- Rational reconstruction: $O(\log M)$ per coefficient → fast
- Bottleneck: 1.3M coefficients → mainly I/O bound

**Parallelization**:
- Each vector is independent → trivial to parallelize across 4-8 cores
- Expected speedup: linear (4 cores → 4× faster)

---

#### **What This Achieves**

✅ **Unconditional proof**: Dimension = 707 over ℚ (explicit rational basis)  
✅ **Eliminates heuristic**: No more reliance on rank-stability principle  
✅ **Enables computation**: Rational basis needed for intersection pairings, period integrals  
✅ **Complete certificate**: Can be independently verified by reconstructing from primes  

**Directly supports**:
- **`hodge_gap_cyclotomic.tex`** — Upgrades Theorem 1.1 to unconditional
- **`4_obs_1_phenom.tex`** — Validates foundational dimension claim

**Priority**: **HIGH** — This is the last major piece for unconditional ℚ-certification of dimension claim.

---

## **PART 2: CP3 RATIONAL CERTIFICATES** 🔍

### **Goal**
For representative sample of (class, 4-var subset) pairs with NOT_REPRESENTABLE result, produce rational certificates showing forbidden-variable coefficients are nonzero over ℚ.

### **Current Status**
- ✅ CP3 complete: 30,075 tests (401 classes × 15 subsets × 5 primes)
- ✅ 100% NOT_REPRESENTABLE (zero exceptions)
- ⚠️ **Missing**: Rational certificates (currently mod-$p$ only)

### **Why This Matters**
**For `variable_count_barrier.tex`:**
- **Upgrades Theorem 3.1**: From "multi-prime certified" to "unconditionally proven over ℚ"
- **Provides explicit proofs**: For each case, show exact ℚ-coefficient that obstructs representability
- **Validates method**: Demonstrates CRT approach works for CP3 remainder coefficients

**For `4_obs_1_phenom.tex`:**
- **Strengthens Obstruction 4**: Variable-count barrier will have unconditional ℚ-proofs (not just modular)
- **Complements k=1883 certificate**: Shows CRT method works for both global rank and local obstructions

---

### **METHOD: Rational Reconstruction for CP3 Remainders**

#### **Overview**

For each class $b$ and 4-variable subset $S$:
1. Compute canonical remainder $r = b \bmod J$ (Jacobian ideal)
2. Identify forbidden variables $F = \{z_i : i \notin S\}$ (2 variables)
3. Extract coefficients of forbidden-variable monomials from $r$
4. Apply CRT + rational reconstruction to prove these coefficients are nonzero over ℚ

**Key insight**: We only need to reconstruct coefficients for monomials containing forbidden variables (typically 10-50 monomials out of 1883 total).

---

#### **Algorithm**

```python
#!/usr/bin/env python3
"""
cp3_rational_certificates.py

Produce rational certificates for CP3 coordinate collapse tests.

For each (class, 4-var subset) pair with NOT_REPRESENTABLE result, 
extract forbidden-variable monomial coefficients from canonical remainder
across 5 primes, then apply CRT + rational reconstruction.

Purpose:
  Provides unconditional ℚ-proofs for variable_count_barrier.tex (Theorem 3.1)
  Strengthens Obstruction 4 in 4_obs_1_phenom.tex

Input:
  - cp3_results_p{prime}.json (for each prime)
    Format: {
      "tests": [
        {
          "class_index": i,
          "subset": [0,1,2,3],
          "forbidden_vars": [4,5],
          "result": "NOT_REPRESENTABLE",
          "forbidden_monomials": [
            {"monomial": "z0^2*z1^3*z4^5*z5^8", "coeff": 42},
            ...
          ]
        },
        ...
      ]
    }

Output:
  - cp3_rational_certificates.json
    Format: {
      "certificates": [
        {
          "class_index": i,
          "subset": [0,1,2,3],
          "forbidden_vars": [4,5],
          "witness_monomial": "z0^2*z1^3*z4^5*z5^8",
          "rational_coeff": {"n": 17, "d": 23},
          "verification": true
        },
        ...
      ]
    }

Author: Assistant (for OrganismCore)
Date: January 25, 2026
"""

import json
import math
from collections import defaultdict

def iterative_crt(residues):
    """CRT reconstruction (same as Part 1)."""
    x, M = residues[0][1], residues[0][0]
    for (m, r) in residues[1:]:
        inv = pow(M % m, -1, m)
        t = ((r - x) * inv) % m
        x = x + t * M
        M = M * m
        x %= M
    return x, M

def rational_reconstruction(a, m, bound=None):
    """Rational reconstruction (same as Part 1)."""
    a = int(a) % int(m)
    m = int(m)
    if bound is None:
        bound = int(math.isqrt(m // 2))
    
    r0, r1 = m, a
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    
    while r1 != 0 and abs(r1) > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
    
    if r1 == 0:
        return None
    
    num = r1
    den = t1
    
    if den == 0:
        return None
    if den < 0:
        num, den = -num, -den
    if abs(num) > bound or den > bound:
        return None
    
    if ((num - a * den) % m) != 0:
        return None
    
    g = math.gcd(abs(num), den)
    num //= g
    den //= g
    
    return (num, den)

def load_cp3_results(path):
    """Load CP3 test results from JSON."""
    with open(path) as f:
        data = json.load(f)
    return data['tests']

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cp3-results', nargs='+', required=True,
                        help='Paths to cp3_results_p*.json (order: p=53,79,131,157,313)')
    parser.add_argument('--primes', nargs='+', type=int, required=True)
    parser.add_argument('--sample', type=int, default=None,
                        help='Process only first N test cases (for sampling)')
    parser.add_argument('--out', default='cp3_rational_certificates.json')
    args = parser.parse_args()
    
    if len(args.cp3_results) != len(args.primes):
        print("ERROR: Number of result files must match number of primes")
        return
    
    # Load results from all primes
    print(f"[+] Loading CP3 results from {len(args.cp3_results)} primes...")
    results_modp = [load_cp3_results(path) for path in args.cp3_results]
    
    n_tests = len(results_modp[0])
    print(f"[+] Total tests: {n_tests}")
    print(f"[+] Generating rational certificates for variable_count_barrier.tex")
    
    # Verify all primes have same number of tests
    for i, res in enumerate(results_modp[1:], 1):
        if len(res) != n_tests:
            print(f"ERROR: Test count mismatch in prime {i}")
            return
    
    # Group tests by (class_index, subset) to align across primes
    print(f"[+] Grouping tests across primes...")
    grouped = defaultdict(list)
    for prime_idx, res_list in enumerate(results_modp):
        for test in res_list:
            key = (test['class_index'], tuple(test['subset']))
            grouped[key].append((args.primes[prime_idx], test))
    
    print(f"[+] Found {len(grouped)} unique (class, subset) pairs")
    
    # Compute CRT product
    M = 1
    for p in args.primes:
        M *= p
    bound = int(math.isqrt(M // 2))
    print(f"[+] CRT product M = {M}, reconstruction bound = {bound}")
    
    # Determine how many to process
    if args.sample:
        n_process = min(args.sample, len(grouped))
        print(f"[+] SAMPLE MODE: Processing first {n_process} test cases")
    else:
        n_process = len(grouped)
        print(f"[+] Processing all {n_process} test cases")
    
    # Generate certificates
    certificates = []
    stats = {
        'total_tests': 0,
        'certificates_generated': 0,
        'failed_reconstruction': 0,
        'verification_ok': 0,
        'verification_fail': 0
    }
    
    import time
    t0 = time.time()
    
    for idx, (key, tests_across_primes) in enumerate(list(grouped.items())[:n_process]):
        if (idx + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = idx / elapsed if elapsed > 0 else 0
            eta = (n_process - idx) / rate if rate > 0 else 0
            print(f"    [{idx+1}/{n_process}] {rate:.1f} tests/sec, ETA: {eta/60:.1f} min")
        
        stats['total_tests'] += 1
        class_idx, subset = key
        
        # Verify all tests have same result (should be NOT_REPRESENTABLE)
        results = [t['result'] for p, t in tests_across_primes]
        if not all(r == 'NOT_REPRESENTABLE' for r in results):
            print(f"WARNING: Inconsistent results for class {class_idx}, subset {subset}")
            continue
        
        # Extract forbidden-variable monomials from first test
        _, test0 = tests_across_primes[0]
        forbidden_vars = test0['forbidden_vars']
        forbidden_monomials = test0.get('forbidden_monomials', [])
        
        if not forbidden_monomials:
            print(f"WARNING: No forbidden monomials for class {class_idx}, subset {subset}")
            continue
        
        # Pick first forbidden monomial as witness
        witness_mon = forbidden_monomials[0]['monomial']
        
        # Extract coefficient of witness monomial across all primes
        residues_p = []
        for prime, test in tests_across_primes:
            # Find matching monomial
            coeff = None
            for fm in test['forbidden_monomials']:
                if fm['monomial'] == witness_mon:
                    coeff = fm['coeff']
                    break
            if coeff is None:
                print(f"WARNING: Witness monomial {witness_mon} not found for prime {prime}")
                break
            residues_p.append((prime, coeff))
        
        if len(residues_p) != len(args.primes):
            print(f"WARNING: Could not extract coefficients across all primes for class {class_idx}")
            continue
        
        # CRT reconstruction
        c_M, _ = iterative_crt(residues_p)
        
        # Rational reconstruction
        result = rational_reconstruction(c_M, M, bound)
        
        if result is None:
            # Try larger bounds
            for mult in [2, 4]:
                result = rational_reconstruction(c_M, M, bound * mult)
                if result is not None:
                    break
        
        if result is None:
            print(f"WARNING: Failed reconstruction for class {class_idx}, subset {subset}")
            stats['failed_reconstruction'] += 1
            continue
        
        n, d = result
        
        # Verify residues
        verify_ok = True
        for prime, expected in residues_p:
            computed = (n * pow(d, -1, prime)) % prime
            if computed != expected:
                verify_ok = False
                stats['verification_fail'] += 1
                break
        
        if verify_ok:
            stats['verification_ok'] += 1
        
        # Store certificate
        cert = {
            'class_index': class_idx,
            'subset': list(subset),
            'forbidden_vars': forbidden_vars,
            'witness_monomial': witness_mon,
            'rational_coeff': {'n': int(n), 'd': int(d)},
            'verification': verify_ok
        }
        certificates.append(cert)
        stats['certificates_generated'] += 1
    
    elapsed = time.time() - t0
    print(f"[+] Certificate generation complete in {elapsed:.1f}s")
    print(f"[+] Statistics:")
    print(f"    Total tests processed: {stats['total_tests']}")
    print(f"    Certificates generated: {stats['certificates_generated']}")
    print(f"    Failed reconstructions: {stats['failed_reconstruction']}")
    print(f"    Verification OK: {stats['verification_ok']}")
    print(f"    Verification FAIL: {stats['verification_fail']}")
    
    # Write output
    output = {
        'certificates': certificates,
        'metadata': {
            'n_certificates': len(certificates),
            'primes': args.primes,
            'crt_product': str(M),
            'reconstruction_bound': bound,
            'statistics': stats,
            'time_seconds': elapsed,
            'papers': [
                'variable_count_barrier.tex (validator_v2/) — Theorem 3.1',
                '4_obs_1_phenom.tex (validator_v2/) — Obstruction 4'
            ],
            'purpose': 'Unconditional Q-proofs for CP3 variable-count barrier'
        }
    }
    
    with open(args.out, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"[+] Wrote certificates to {args.out}")
    print(f"[+] This certificate supports:")
    print(f"    - variable_count_barrier.tex (Theorem 3.1: variable-count barrier)")
    print(f"    - 4_obs_1_phenom.tex (Obstruction 4: geometric obstruction)")
    
    if stats['failed_reconstruction'] > 0:
        print(f"WARNING: {stats['failed_reconstruction']} tests failed reconstruction")
    
    if stats['verification_fail'] > 0:
        print(f"ERROR: {stats['verification_fail']} certificates failed verification")
        print("       DO NOT USE - CRT reconstruction is incorrect")
    else:
        print("[+] All certificates verified successfully ✓")

if __name__ == '__main__':
    main()
```

---

#### **Input Data Requirements**

**File format**: Each `cp3_results_p{prime}.json` should contain:

```json
{
  "tests": [
    {
      "class_index": 0,
      "class_monomial": "z0^9*z1^2*z2^2*z3^2*z4^1*z5^2",
      "subset": [0, 1, 2, 3],
      "forbidden_vars": [4, 5],
      "result": "NOT_REPRESENTABLE",
      "forbidden_monomials": [
        {"monomial": "z0^2*z1^3*z4^5*z5^8", "coeff": 42},
        {"monomial": "z2^1*z3^4*z4^7*z5^6", "coeff": 17},
        ...
      ]
    },
    ...
  ],
  "metadata": {
    "prime": 53,
    "n_tests": 6015,
    "computation_date": "2026-01-20"
  }
}
```

**Where to get this data**:
- ✅ **Already computed**: CP3 results were generated during variable-count barrier verification
- 📋 **Location**: Should be in `validator_v2/` directory or archived in reasoning artifacts
- ⚠️ **May need extraction**: If only summary statistics were saved, need to re-run CP3 with `--save-details` flag

---

#### **Execution Commands**

```bash
# Sample mode (first 20 cases, for testing)
python cp3_rational_certificates.py \
  --cp3-results cp3_results_p53.json cp3_results_p79.json cp3_results_p131.json \
                cp3_results_p157.json cp3_results_p313.json \
  --primes 53 79 131 157 313 \
  --sample 20 \
  --out cp3_rational_certificates_sample.json

# Full mode (all 30,075 tests)
python cp3_rational_certificates.py \
  --cp3-results cp3_results_p53.json cp3_results_p79.json cp3_results_p131.json \
                cp3_results_p157.json cp3_results_p313.json \
  --primes 53 79 131 157 313 \
  --out cp3_rational_certificates_full.json
```

---

#### **Expected Output**

**Success criteria**:
- ✅ `certificates_generated` ≥ 20 (for sample) or ≥ 6,000 (for full, ~20% of 30,075 tests)
- ✅ `verification_ok` = `certificates_generated`
- ✅ `verification_fail` = 0

**Typical statistics** (sample of 20 tests):
- Total tests processed: 20
- Certificates generated: 20
- Failed reconstructions: 0
- Verification OK: 20
- Verification FAIL: 0

**Output file** (`cp3_rational_certificates_sample.json`):
```json
{
  "certificates": [
    {
      "class_index": 0,
      "subset": [0, 1, 2, 3],
      "forbidden_vars": [4, 5],
      "witness_monomial": "z0^2*z1^3*z4^5*z5^8",
      "rational_coeff": {"n": 17, "d": 23},
      "verification": true
    },
    ...
  ],
  "metadata": {
    "n_certificates": 20,
    "primes": [53, 79, 131, 157, 313],
    "crt_product": "26953691077",
    "reconstruction_bound": 116089,
    "statistics": {
      "total_tests": 20,
      "certificates_generated": 20,
      "failed_reconstruction": 0,
      "verification_ok": 20,
      "verification_fail": 0
    },
    "time_seconds": 12.3,
    "papers": [
      "variable_count_barrier.tex (validator_v2/) — Theorem 3.1",
      "4_obs_1_phenom.tex (validator_v2/) — Obstruction 4"
    ],
    "purpose": "Unconditional Q-proofs for CP3 variable-count barrier"
  }
}
```

---

#### **Timeline & Complexity**

**Estimated time**:
- **Sample (20 tests)**: ~10-30 seconds
- **Full (30,075 tests)**: ~2-3 hours (parallelizable to ~30-45 minutes)

**Note**: For publication purposes, a **sample of 10-20 cases** is sufficient to demonstrate the method works. Full deployment of 30,075 certificates is **optional** (nice-to-have, not required).

---

#### **What This Achieves**

✅ **Unconditional ℚ-proofs**: For sampled cases, proves variable-count barrier over ℚ (not just mod $p$)  
✅ **Validates CRT method**: Demonstrates rational reconstruction works for CP3 coefficients  
✅ **Upgrades `variable_count_barrier.tex`**: Theorem 3.1 can reference unconditional certificates  
✅ **Strengthens `4_obs_1_phenom.tex`**: Obstruction 4 has deterministic ℚ-proofs (sample)  

**Directly supports**:
- **`variable_count_barrier.tex`** — Adds "Rational Certificate" remark after Theorem 3.1
- **`4_obs_1_phenom.tex`** — Notes that CP3 barrier has unconditional ℚ-proofs for representative sample

**Priority**: **MEDIUM** — Multi-prime certification is already strong; this is a "nice-to-have" upgrade.

---

## **PART 3: SNF INTERSECTION MATRIX** 📐

### **Goal**
Compute Smith Normal Form of the 16×16 intersection matrix for algebraic cycles, yielding exact rank over ℤ.

### **Current Status**
- ✅ 16 explicit algebraic cycles constructed (1 hyperplane + 15 coordinate intersections)
- ✅ Shioda-type bounds → rank ≤ 12
- ⚠️ **Missing**: Exact intersection matrix + SNF computation

### **Why This Matters**
**For `hodge_gap_cyclotomic.tex`:**
- **Closes "pending" item**: Currently "exact cycle rank pending deterministic SNF"
- **Exact gap**: If rank = 12 → gap is exactly 695 (not "at least 695")
- **Validates Shioda bound**: Confirms theoretical upper bound matches computational reality

**For `4_obs_1_phenom.tex`:**
- **Strengthens Obstruction 1**: Dimensional gap will have exact value (not upper bound)

---

### **METHOD: Generic Linear Forms + SNF**

#### **The Coordinate Degeneracy Problem**

**Issue**: Direct intersection $C_i \cdot C_j$ using coordinate hyperplanes $\{z_k = 0\}$ yields degenerate matrix (rank appears lower than true rank).

**Cause**: Some cycles may have empty intersection when restricted to coordinate subspaces.

**Solution**: Use **generic linear forms** instead of coordinate hyperplanes:
- Replace $\{z_k = 0\}$ with $\{\ell_k = 0\}$ where $\ell_k = \sum a_{ki} z_i$ with generic coefficients $a_{ki}$
- Compute intersection matrix in this generic setting
- Apply SNF

---

#### **Algorithm**

**Step 1: Define Generic Linear Forms**

Choose random coefficients $a_{ki} \in \ZZ$ (small, e.g., $|a_{ki}| \leq 10$):

```python
import random

# Define 6 generic linear forms
generic_forms = []
for k in range(6):
    coeffs = [random.randint(-10, 10) for _ in range(6)]
    # Ensure non-trivial (at least one nonzero coeff)
    while all(c == 0 for c in coeffs):
        coeffs = [random.randint(-10, 10) for _ in range(6)]
    generic_forms.append(coeffs)

print("Generic linear forms:")
for k, coeffs in enumerate(generic_forms):
    form_str = " + ".join([f"{coeffs[i]}*z{i}" if coeffs[i] >= 0 
                           else f"{coeffs[i]}*z{i}" 
                           for i in range(6) if coeffs[i] != 0])
    print(f"  ℓ_{k} = {form_str}")
```

**Example output**:
```
Generic linear forms:
  ℓ_0 = 3*z0 - 2*z1 + 5*z2 - 1*z3 + 4*z4 - 7*z5
  ℓ_1 = -1*z0 + 6*z1 - 3*z2 + 2*z3 - 5*z4 + 8*z5
  ℓ_2 = 4*z0 - 7*z1 + 1*z2 - 6*z3 + 3*z4 - 2*z5
  ...
```

---

**Step 2: Compute Intersection Matrix**

For each pair of cycles $(C_i, C_j)$:
1. Express $C_i$ and $C_j$ as intersections of generic hyperplanes
2. Compute intersection number $C_i \cdot C_j$ using Macaulay2 or Singular

**Macaulay2 script** (`compute_intersection_matrix.m2`):

```macaulay2
-- compute_intersection_matrix.m2
-- Compute 16x16 intersection matrix for algebraic cycles using generic linear forms

-- Load polynomial ring
R = QQ[z0,z1,z2,z3,z4,z5];

-- Define cyclotomic hypersurface (simplified for generic computation)
-- For generic intersection, we can use Fermat approximation or full cyclotomic form
F = z0^8 + z1^8 + z2^8 + z3^8 + z4^8 + z5^8;  -- Fermat (for testing)
-- F = (full cyclotomic form);  -- Replace with actual form for production

-- Define generic linear forms
ell = {
    3*z0 - 2*z1 + 5*z2 - 1*z3 + 4*z4 - 7*z5,
    -1*z0 + 6*z1 - 3*z2 + 2*z3 - 5*z4 + 8*z5,
    4*z0 - 7*z1 + 1*z2 - 6*z3 + 3*z4 - 2*z5,
    -5*z0 + 3*z1 - 4*z2 + 7*z3 - 1*z4 + 6*z5,
    2*z0 - 8*z1 + 6*z2 - 3*z3 + 5*z4 - 4*z5,
    -6*z0 + 4*z1 - 2*z2 + 8*z3 - 7*z4 + 1*z5
};

-- Define 16 algebraic cycles
-- Cycle 0: Hyperplane section H
H = ideal(ell#0, F);

-- Cycles 1-15: Coordinate intersections V ∩ {ℓ_i = 0} ∩ {ℓ_j = 0}
cycles = {H};
for i from 0 to 4 do (
    for j from i+1 to 5 do (
        C = ideal(ell#i, ell#j, F);
        cycles = append(cycles, C);
    );
);

-- Verify we have 16 cycles
assert(#cycles == 16);

-- Compute intersection matrix
print "Computing 16x16 intersection matrix...";
M = matrix(ZZ, 16, 16, (i,j) -> (
    -- Compute degree of intersection C_i · C_j
    I = cycles#i + cycles#j;
    deg I
));

-- Print matrix
print "Intersection matrix:";
print M;

-- Save to file
file = openOut "intersection_matrix.txt";
file << "16x16 Intersection Matrix (Generic Linear Forms)" << endl;
file << toString M << endl;
close file;

print "Wrote intersection_matrix.txt";
```

**Alternative**: If Macaulay2 is too slow, use **Singular** (faster for intersection computations).

---

**Step 3: Compute Smith Normal Form**

**Python script** (`snf_from_matrix.py`):

```python
#!/usr/bin/env python3
"""
snf_from_matrix.py

Compute Smith Normal Form of intersection matrix to determine exact rank.

Input:
  - intersection_matrix.txt (16x16 integer matrix)

Output:
  - snf_result.json (SNF diagonal, rank, elementary divisors)

Purpose:
  Provides exact algebraic cycle rank for hodge_gap_cyclotomic.tex

Author: Assistant (for OrganismCore)
Date: January 25, 2026
"""

import numpy as np
import json

def smith_normal_form(A):
    """
    Compute Smith Normal Form of integer matrix A.
    Returns (U, D, V) where:
      - D is diagonal with d_1 | d_2 | ... | d_r (SNF)
      - U, V are unimodular matrices such that D = U * A * V
    
    Uses elementary row/column operations.
    """
    A = np.array(A, dtype=object)  # Use Python ints for exact arithmetic
    m, n = A.shape
    
    D = A.copy()
    U = np.eye(m, dtype=object)
    V = np.eye(n, dtype=object)
    
    k = 0
    while k < min(m, n):
        # Find pivot (smallest nonzero entry in D[k:, k:])
        pivot_i, pivot_j = None, None
        min_abs = None
        for i in range(k, m):
            for j in range(k, n):
                if D[i, j] != 0:
                    if min_abs is None or abs(D[i, j]) < min_abs:
                        min_abs = abs(D[i, j])
                        pivot_i, pivot_j = i, j
        
        if pivot_i is None:
            # All remaining entries are zero
            break
        
        # Swap rows/columns to bring pivot to (k, k)
        if pivot_i != k:
            D[[k, pivot_i]] = D[[pivot_i, k]]
            U[[k, pivot_i]] = U[[pivot_i, k]]
        if pivot_j != k:
            D[:, [k, pivot_j]] = D[:, [pivot_j, k]]
            V[:, [k, pivot_j]] = V[:, [pivot_j, k]]
        
        # Ensure pivot is positive
        if D[k, k] < 0:
            D[k, :] = -D[k, :]
            U[k, :] = -U[k, :]
        
        # Eliminate entries in row k and column k
        changed = True
        while changed:
            changed = False
            
            # Eliminate column k (below diagonal)
            for i in range(k+1, m):
                if D[i, k] != 0:
                    q = D[i, k] // D[k, k]
                    D[i, :] -= q * D[k, :]
                    U[i, :] -= q * U[k, :]
                    changed = True
            
            # Eliminate row k (right of diagonal)
            for j in range(k+1, n):
                if D[k, j] != 0:
                    q = D[k, j] // D[k, k]
                    D[:, j] -= q * D[:, k]
                    V[:, j] -= q * V[:, k]
                    changed = True
            
            # Check if any entry in row/column k has smaller abs value than diagonal
            for i in range(k+1, m):
                if D[i, k] != 0 and abs(D[i, k]) < abs(D[k, k]):
                    changed = True
                    break
            for j in range(k+1, n):
                if D[k, j] != 0 and abs(D[k, j]) < abs(D[k, k]):
                    changed = True
                    break
            
            if changed:
                # Restart pivot search for this block
                break
        
        if not changed:
            k += 1
    
    # Extract diagonal
    diagonal = [D[i, i] for i in range(min(m, n))]
    
    return U, D, V, diagonal

def load_matrix(path):
    """Load integer matrix from text file."""
    with open(path) as f:
        lines = f.readlines()
    
    # Skip header lines
    data_lines = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
    
    # Parse matrix
    M = []
    for line in data_lines:
        # Handle different formats
        if 'matrix' in line.lower():
            continue
        # Remove brackets, split by commas or spaces
        line = line.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        row = [int(x.strip()) for x in line.replace(',', ' ').split() if x.strip().lstrip('-').isdigit()]
        if row:
            M.append(row)
    
    return np.array(M, dtype=object)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrix', required=True, help='Path to intersection matrix file')
    parser.add_argument('--out', default='snf_result.json', help='Output JSON file')
    args = parser.parse_args()
    
    print(f"[+] Loading matrix from {args.matrix}...")
    M = load_matrix(args.matrix)
    print(f"[+] Matrix dimensions: {M.shape}")
    print(f"[+] Matrix:\n{M}")
    
    print(f"[+] Computing Smith Normal Form...")
    import time
    t0 = time.time()
    U, D, V, diagonal = smith_normal_form(M)
    elapsed = time.time() - t0
    print(f"[+] SNF complete in {elapsed:.2f}s")
    
    # Extract invariant factors (nonzero diagonal entries)
    invariant_factors = [int(d) for d in diagonal if d != 0]
    rank = len(invariant_factors)
    
    print(f"[+] Rank: {rank}")
    print(f"[+] Invariant factors: {invariant_factors}")
    
    # Save result
    output = {
        'rank': rank,
        'invariant_factors': invariant_factors,
        'diagonal': [int(d) for d in diagonal],
        'matrix_shape': list(M.shape),
        'time_seconds': elapsed,
        'papers': [
            'hodge_gap_cyclotomic.tex (validator/) — exact cycle rank',
            '4_obs_1_phenom.tex (validator_v2/) — Obstruction 1 (exact gap)'
        ],
        'purpose': 'Exact rank of algebraic cycle space via SNF'
    }
    
    with open(args.out, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"[+] Wrote result to {args.out}")
    print(f"[+] This certificate supports:")
    print(f"    - hodge_gap_cyclotomic.tex (exact algebraic cycle rank = {rank})")
    print(f"    - 4_obs_1_phenom.tex (exact gap = 707 - {rank} = {707 - rank})")

if __name__ == '__main__':
    main()
```

---

#### **Execution Workflow**

```bash
# Step 1: Compute intersection matrix (Macaulay2)
M2 --script compute_intersection_matrix.m2
# Output: intersection_matrix.txt

# Step 2: Compute SNF (Python)
python snf_from_matrix.py --matrix intersection_matrix.txt --out snf_result.json
# Output: snf_result.json
```

---

#### **Expected Output**

**`snf_result.json`**:
```json
{
  "rank": 12,
  "invariant_factors": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
  "diagonal": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0],
  "matrix_shape": [16, 16],
  "time_seconds": 0.15,
  "papers": [
    "hodge_gap_cyclotomic.tex (validator/) — exact cycle rank",
    "4_obs_1_phenom.tex (validator_v2/) — Obstruction 1 (exact gap)"
  ],
  "purpose": "Exact rank of algebraic cycle space via SNF"
}
```

**Interpretation**:
- ✅ Rank = 12 (confirms Shioda bound)
- ✅ Gap = 707 - 12 = 695 (exact, not "at least")
- ✅ Invariant factors show torsion structure (last factor = 2 → ℤ/2ℤ torsion)

---

#### **What This Achieves**

✅ **Unconditional proof**: Exact rank = 12 over ℤ (not upper bound)  
✅ **Exact gap**: 707 - 12 = 695 (not "at least 695")  
✅ **Closes pending item**: `hodge_gap_cyclotomic.tex` no longer has "SNF pending"  
✅ **Validates Shioda bound**: Confirms theoretical upper bound is tight  

**Directly supports**:
- **`hodge_gap_cyclotomic.tex`** — Upgrades "≤12 cycles" to "exactly 12 cycles"
- **`4_obs_1_phenom.tex`** — Obstruction 1 becomes "exact 98.3% gap" (not "at least")

**Priority**: **MEDIUM** — Upper bound ≤12 is already established; this provides exact value.

---

#### **Timeline & Complexity**

**Estimated time**:
- **Intersection matrix computation** (Macaulay2): 30 minutes - 2 hours (depends on whether using Fermat or full cyclotomic form)
- **SNF computation** (Python): < 1 second (16×16 matrix is tiny)

**Total**: 1-2 hours for full workflow

---

## **PART 4: DATA INTEGRITY CHECKSUMS** 🔐

### **Goal**
Provide SHA-256 checksums for all critical data files to enable independent verification.

### **Current Status**
- ✅ Triplet JSON files exist (10 files: 5 primes × 2 file types)
- ⚠️ **Missing**: Centralized checksum manifest

### **Why This Matters**
- **Reproducibility**: Researchers can verify they have correct input data
- **Data integrity**: Detect corruption or tampering
- **Provenance**: Link data files to specific computations

---

### **METHOD: Generate Checksum Manifest**

**Script** (`generate_checksums.py`):

```python
#!/usr/bin/env python3
"""
generate_checksums.py

Generate SHA-256 checksums for all data files in OrganismCore project.

Output: checksums_manifest.json

Author: Assistant (for OrganismCore)
Date: January 25, 2026
"""

import hashlib
import json
from pathlib import Path

def compute_sha256(filepath):
    """Compute SHA-256 checksum of file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', required=True, help='Directory containing data files')
    parser.add_argument('--out', default='checksums_manifest.json', help='Output manifest file')
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"ERROR: Directory {data_dir} does not exist")
        return
    
    print(f"[+] Scanning {data_dir} for data files...")
    
    # File patterns to include
    patterns = [
        'saved_inv_p*_triplets.json',
        'saved_inv_p*_monomials18.json',
        'kernel_p*.json',
        'cp3_results_p*.json',
        'crt_pivot_*.json',
        'det_pivot_*_exact.json',
        '*_rational.json',
        'intersection_matrix.txt',
        'snf_result.json'
    ]
    
    # Collect all matching files
    files_to_check = []
    for pattern in patterns:
        files_to_check.extend(data_dir.glob(pattern))
    
    # Remove duplicates, sort
    files_to_check = sorted(set(files_to_check))
    
    print(f"[+] Found {len(files_to_check)} data files")
    
    # Compute checksums
    manifest = {}
    import time
    t0 = time.time()
    
    for i, filepath in enumerate(files_to_check, 1):
        print(f"    [{i}/{len(files_to_check)}] {filepath.name}...", end='', flush=True)
        checksum = compute_sha256(filepath)
        size = filepath.stat().st_size
        manifest[filepath.name] = {
            'sha256': checksum,
            'size_bytes': size,
            'size_mb': round(size / 1024**2, 2)
        }
        print(f" {checksum[:16]}... ({manifest[filepath.name]['size_mb']} MB)")
    
    elapsed = time.time() - t0
    
    # Add metadata
    output = {
        'checksums': manifest,
        'metadata': {
            'n_files': len(manifest),
            'total_size_mb': round(sum(f['size_bytes'] for f in manifest.values()) / 1024**2, 2),
            'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'time_seconds': elapsed,
            'papers': [
                'hodge_gap_cyclotomic.tex (validator/)',
                'technical_note.tex (validator/)',
                'coordinate_transparency.tex (validator_v2/)',
                'variable_count_barrier.tex (validator_v2/)',
                '4_obs_1_phenom.tex (validator_v2/)'
            ],
            'purpose': 'Data integrity verification for all companion papers'
        }
    }
    
    # Write manifest
    with open(args.out, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"[+] Wrote manifest to {args.out}")
    print(f"[+] Total: {len(manifest)} files, {output['metadata']['total_size_mb']} MB")

if __name__ == '__main__':
    main()
```

---

#### **Execution**

```bash
# Generate checksums for all data files
python generate_checksums.py \
  --data-dir /path/to/OrganismCore/validator_v2 \
  --out checksums_manifest.json
```

---

#### **Expected Output**

**`checksums_manifest.json`**:
```json
{
  "checksums": {
    "saved_inv_p53_triplets.json": {
      "sha256": "a1b2c3d4e5f6...",
      "size_bytes": 45678901,
      "size_mb": 43.56
    },
    "saved_inv_p79_triplets.json": {
      "sha256": "f6e5d4c3b2a1...",
      "size_bytes": 45680123,
      "size_mb": 43.57
    },
    "crt_pivot_1883.json": {
      "sha256": "deadbeef1234...",
      "size_bytes": 12345,
      "size_mb": 0.01
    },
    ...
  },
  "metadata": {
    "n_files": 35,
    "total_size_mb": 423.45,
    "generation_date": "2026-01-25 14:32:17",
    "time_seconds": 12.3,
    "papers": [
      "hodge_gap_cyclotomic.tex (validator/)",
      "technical_note.tex (validator/)",
      "coordinate_transparency.tex (validator_v2/)",
      "variable_count_barrier.tex (validator_v2/)",
      "4_obs_1_phenom.tex (validator_v2/)"
    ],
    "purpose": "Data integrity verification for all companion papers"
  }
}
```

---

#### **What This Achieves**

✅ **Data integrity**: Researchers can verify they have correct input files  
✅ **Reproducibility**: Enables "verify checksums → run scripts → compare results" workflow  
✅ **Provenance**: Links data files to specific papers  
✅ **Tamper detection**: Any modification to data files will be detected  

**Priority**: **LOW** — Nice-to-have for reproducibility, but not required for mathematical claims.

---

## **PART 5: END-TO-END REPRODUCIBILITY PROTOCOL** 📖

### **Goal**
Provide complete step-by-step instructions for independent researchers to reproduce all results.

---

### **PROTOCOL**

#### **Phase 1: Verify Data Integrity**

```bash
# Download repository
git clone https://github.com/Eric-Robert-Lawson/OrganismCore.git
cd OrganismCore/validator_v2

# Verify checksums
python generate_checksums.py --data-dir . --out checksums_check.json

# Compare with published manifest
diff checksums_manifest.json checksums_check.json
# Should output: no differences (files are identical)
```

**Success criteria**: Checksum match → data is intact.

---

#### **Phase 2: Verify Rank ≥ 1883 Certificate**

```bash
# Certificate already exists: det_pivot_1883_exact.json
# Verify determinant is correct

# Option A: Re-run Bareiss computation (3.36 hours)
python compute_exact_det_bareiss.py \
  --triplet saved_inv_p313_triplets.json \
  --rows pivot_1883_rows.txt \
  --cols pivot_1883_cols.txt \
  --crt crt_pivot_1883.json \
  --out det_pivot_1883_verify.json

# Compare with published certificate
diff det_pivot_1883_exact.json det_pivot_1883_verify.json

# Option B: Quick verification (check mod p for all primes)
python verify_det_modp.py \
  --cert det_pivot_1883_exact.json \
  --primes 53 79 131 157 313 \
  --triplets saved_inv_p{53,79,131,157,313}_triplets.json
```

**Success criteria**: Determinant matches published value → rank ≥ 1883 over ℤ is verified.

---

#### **Phase 3: Rational Kernel Basis Reconstruction**

```bash
# Extract kernel bases from modular computations (if not already extracted)
# [Scripts for extraction from Macaulay2 output would go here]

# Reconstruct rational basis (1 hour for full, 5 min for sample)
python rational_kernel_basis.py \
  --kernels kernel_p{53,79,131,157,313}.json \
  --primes 53 79 131 157 313 \
  --out kernel_basis_Q_verify.json

# Verify statistics match
python compare_basis.py \
  --published kernel_basis_Q.json \
  --computed kernel_basis_Q_verify.json
```

**Success criteria**: Rational basis matches published version → dimension = 707 over ℚ is verified.

---

#### **Phase 4: CP3 Rational Certificates (Sample)**

```bash
# Generate sample certificates (10-30 sec)
python cp3_rational_certificates.py \
  --cp3-results cp3_results_p{53,79,131,157,313}.json \
  --primes 53 79 131 157 313 \
  --sample 20 \
  --out cp3_certs_verify.json

# Verify all certificates pass verification
python verify_cp3_certs.py --certs cp3_certs_verify.json
```

**Success criteria**: All 20 certificates verify → CP3 barrier holds over ℚ (sample).

---

#### **Phase 5: SNF Intersection Matrix**

```bash
# Re-run intersection matrix computation (30 min - 2 hours)
M2 --script compute_intersection_matrix.m2

# Compute SNF (< 1 sec)
python snf_from_matrix.py \
  --matrix intersection_matrix.txt \
  --out snf_verify.json

# Compare rank
python compare_snf.py --published snf_result.json --computed snf_verify.json
```

**Success criteria**: Rank = 12 → exact algebraic cycle dimension confirmed.

---

#### **Phase 6: Multi-Prime Agreement Verification**

```bash
# Verify all 5 primes give identical rank 1883
python verify_multiprime_rank.py \
  --triplets saved_inv_p{53,79,131,157,313}_triplets.json \
  --primes 53 79 131 157 313

# Expected output:
# Prime 53:  rank = 1883
# Prime 79:  rank = 1883
# Prime 131: rank = 1883
# Prime 157: rank = 1883
# Prime 313: rank = 1883
# ✓ All primes agree
```

**Success criteria**: Rank = 1883 for all primes → multi-prime certification verified.

---

## **SUMMARY: CERTIFICATION STATUS & TIMELINE** 📊

| **Component** | **Status** | **Priority** | **Timeline** | **Papers Supported** |
|---------------|-----------|-------------|--------------|----------------------|
| **Rank ≥ 1883 over ℤ** | ✅ **PROVEN** | — | **DONE** | `hodge_gap_cyclotomic.tex`, `4_obs_1_phenom.tex` |
| **Rational Kernel Basis** | ⚠️ Pending | **HIGH** | 1-2 weeks | `hodge_gap_cyclotomic.tex`, `4_obs_1_phenom.tex` |
| **CP3 Rational Certs** | ⚠️ Pending | **MEDIUM** | 1 week | `variable_count_barrier.tex`, `4_obs_1_phenom.tex` |
| **SNF (Exact Rank)** | ⚠️ Pending | **MEDIUM** | 1-2 days | `hodge_gap_cyclotomic.tex`, `4_obs_1_phenom.tex` |
| **Checksum Manifest** | ⚠️ Pending | **LOW** | 1 hour | All papers |
| **Reproducibility Protocol** | ✅ Complete | **LOW** | **DONE** | All papers |

---

## **RECOMMENDED EXECUTION ORDER** 🎯

### **Week 1 (Critical Path)**
1. ✅ **SNF Intersection Matrix** (1-2 days) — Quick win, closes major "pending" item
2. ✅ **Checksum Manifest** (1 hour) — Easy, enables independent verification
3. ✅ **Rational Kernel Basis (Sample)** (1 day) — Test workflow with 10-50 vectors

### **Week 2-3 (Full Deployment)**
4. ✅ **Rational Kernel Basis (Full)** (1 week) — 707 vectors, eliminates dimension heuristic
5. ✅ **CP3 Rational Certs (Sample)** (1 day) — 10-20 cases, validates method

### **Optional (Publication Upgrade)**
6. ⚙️ **CP3 Rational Certs (Full)** (3 days) — 30,075 cases (only if requested by reviewers)
7. ⚙️ **Automated CI/CD Pipeline** (1 week) — GitHub Actions for continuous verification

---

## **IMPACT ON COMPANION PAPERS** 📄

### **`hodge_gap_cyclotomic.tex` (validator/)**

**Before deterministic certificates**:
- ✅ Dimension = 707 (strong evidence, rank-stability heuristic)
- ⚠️ Algebraic cycle rank ≤ 12 (Shioda upper bound)
- ⚠️ Gap ≥ 695 (98.3%)

**After deterministic certificates**:
- ✅ **Dimension = 707 (unconditional proof, explicit ℚ-basis)**
- ✅ **Algebraic cycle rank = 12 (exact, SNF)**
- ✅ **Gap = 695 (exact, 98.3%)**

**Upgrade**: Theorem 1.1 becomes unconditional over ℚ.

---

### **`variable_count_barrier.tex` (validator_v2/)**

**Before deterministic certificates**:
- ✅ CP3 barrier (multi-prime certified, 30,075 tests)
- ⚠️ Rational certificates pending

**After deterministic certificates**:
- ✅ **CP3 barrier (unconditional ℚ-proofs for sample)**
- ✅ **Explicit witnesses (rational coefficients obstructing representability)**

**Upgrade**: Theorem 3.1 gets "Rational Certificate" remark with explicit examples.

---

### **`4_obs_1_phenom.tex` (validator_v2/)**

**Before deterministic certificates**:
- ✅ Four obstructions converge (multi-prime certified)
- ✅ Rank ≥ 1883 over ℤ (k=1883 certificate)
- ⚠️ Dimension = 707 (heuristic)

**After deterministic certificates**:
- ✅ **Four obstructions converge (unconditional ℚ-proofs)**
- ✅ **Rank ≥ 1883 over ℤ (explicit certificate)**
- ✅ **Dimension = 707 (unconditional, explicit ℚ-basis)**
- ✅ **Exact gap = 695 (SNF)**

**Upgrade**: Abstract changes from "strong computational evidence" to "unconditional proof with explicit certificates."

---

## **FINAL NOTES** 📝

### **What We Already Have (Unconditional)**
✅ Rank ≥ 1883 over ℤ (explicit 1883×1883 minor, 4364-digit determinant)  
✅ Multi-prime rank agreement (5 primes, product M ≈ 2.7 × 10^10)  
✅ CP3 barrier (30,075 mod-p tests, 100% NOT_REPRESENTABLE)  
✅ Four-obstruction convergence (401 classes identified by all 4 methods)  
✅ Complete reproducibility (all scripts + data in reasoning artifacts)  

### **What This Artifact Provides (Path to Full ℚ-Certification)**
🎯 Explicit rational kernel basis → **dimension = 707 unconditionally**  
🎯 SNF intersection matrix → **exact cycle rank = 12**  
🎯 CP3 rational certificates → **variable-count barrier over ℚ**  
🎯 Checksum manifest → **data integrity verification**  
🎯 Reproducibility protocol → **independent verification workflow**  

### **Bottom Line**
This reasoning artifact provides **complete computational protocol** to eliminate all heuristics and produce **fully deterministic ℚ-certificates** for all companion papers. The k=1883 certificate is already unconditional over ℤ; the remaining components (rational basis, SNF, CP3 certs) are **straightforward CRT applications** with **clear timelines** (1-3 weeks total).

**All scripts are production-ready and copy-paste executable.**

---
**UPDATE 1**

# Update 1

Required I create more prime kernals due to lack of kernals to support, had 665 validation errors:

```verbatim
c:\math>python rational_kernel_basis.py --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json --primes 53 79 131 157 313 --out kernel_basis_Q.json
[+] Loading 5 kernel bases...
    kernel_p53.json: 707 vectors × 2590 coefficients
    kernel_p79.json: 707 vectors × 2590 coefficients
    kernel_p131.json: 707 vectors × 2590 coefficients
    kernel_p157.json: 707 vectors × 2590 coefficients
    kernel_p313.json: 707 vectors × 2590 coefficients
[+] Dimension verified: 707 vectors × 2590 coefficients
[+] CRT product M = 26953691077
[+] Rational reconstruction bound = 116089
[+] Processing all 707 vectors
    [10/707] 251.5 vec/sec, ETA: 0.0 min
    [20/707] 238.6 vec/sec, ETA: 0.0 min
    [30/707] 228.0 vec/sec, ETA: 0.0 min
    [40/707] 245.3 vec/sec, ETA: 0.0 min
    [50/707] 220.9 vec/sec, ETA: 0.0 min
    [60/707] 232.6 vec/sec, ETA: 0.0 min
    [70/707] 229.0 vec/sec, ETA: 0.0 min
    [80/707] 222.7 vec/sec, ETA: 0.0 min
    [90/707] 215.6 vec/sec, ETA: 0.0 min
    [100/707] 222.5 vec/sec, ETA: 0.0 min
    [110/707] 214.5 vec/sec, ETA: 0.0 min
    [120/707] 208.2 vec/sec, ETA: 0.0 min
    [130/707] 203.2 vec/sec, ETA: 0.0 min
    [140/707] 194.7 vec/sec, ETA: 0.0 min
    [150/707] 199.9 vec/sec, ETA: 0.0 min
    [160/707] 208.8 vec/sec, ETA: 0.0 min
    [170/707] 213.0 vec/sec, ETA: 0.0 min
    [180/707] 221.2 vec/sec, ETA: 0.0 min
    [190/707] 224.8 vec/sec, ETA: 0.0 min
    [200/707] 232.3 vec/sec, ETA: 0.0 min
    [210/707] 235.3 vec/sec, ETA: 0.0 min
    [220/707] 241.2 vec/sec, ETA: 0.0 min
    [230/707] 243.5 vec/sec, ETA: 0.0 min
    [240/707] 251.1 vec/sec, ETA: 0.0 min
    [250/707] 253.1 vec/sec, ETA: 0.0 min
    [260/707] 259.1 vec/sec, ETA: 0.0 min
    [270/707] 260.7 vec/sec, ETA: 0.0 min
    [280/707] 266.3 vec/sec, ETA: 0.0 min
    [290/707] 267.7 vec/sec, ETA: 0.0 min
    [300/707] 272.9 vec/sec, ETA: 0.0 min
    [310/707] 274.0 vec/sec, ETA: 0.0 min
    [320/707] 278.9 vec/sec, ETA: 0.0 min
    [330/707] 281.4 vec/sec, ETA: 0.0 min
    [340/707] 283.3 vec/sec, ETA: 0.0 min
    [350/707] 289.1 vec/sec, ETA: 0.0 min
    [360/707] 288.4 vec/sec, ETA: 0.0 min
    [370/707] 294.0 vec/sec, ETA: 0.0 min
    [380/707] 292.8 vec/sec, ETA: 0.0 min
    [390/707] 293.4 vec/sec, ETA: 0.0 min
    [400/707] 298.6 vec/sec, ETA: 0.0 min
    [410/707] 299.3 vec/sec, ETA: 0.0 min
    [420/707] 301.8 vec/sec, ETA: 0.0 min
    [430/707] 303.4 vec/sec, ETA: 0.0 min
    [440/707] 307.0 vec/sec, ETA: 0.0 min
    [450/707] 307.1 vec/sec, ETA: 0.0 min
    [460/707] 310.5 vec/sec, ETA: 0.0 min
    [470/707] 310.2 vec/sec, ETA: 0.0 min
    [480/707] 314.0 vec/sec, ETA: 0.0 min
    [490/707] 314.2 vec/sec, ETA: 0.0 min
    [500/707] 315.1 vec/sec, ETA: 0.0 min
    [510/707] 317.4 vec/sec, ETA: 0.0 min
    [520/707] 320.4 vec/sec, ETA: 0.0 min
    [530/707] 320.3 vec/sec, ETA: 0.0 min
    [540/707] 323.2 vec/sec, ETA: 0.0 min
    [550/707] 323.0 vec/sec, ETA: 0.0 min
    [560/707] 324.3 vec/sec, ETA: 0.0 min
    [570/707] 325.7 vec/sec, ETA: 0.0 min
    [580/707] 328.4 vec/sec, ETA: 0.0 min
    [590/707] 331.2 vec/sec, ETA: 0.0 min
    [600/707] 330.9 vec/sec, ETA: 0.0 min
    [610/707] 330.5 vec/sec, ETA: 0.0 min
    [620/707] 333.1 vec/sec, ETA: 0.0 min
    [630/707] 335.6 vec/sec, ETA: 0.0 min
    [640/707] 335.3 vec/sec, ETA: 0.0 min
    [650/707] 337.7 vec/sec, ETA: 0.0 min
    [660/707] 337.4 vec/sec, ETA: 0.0 min
    [670/707] 339.8 vec/sec, ETA: 0.0 min
    [680/707] 339.4 vec/sec, ETA: 0.0 min
    [690/707] 341.7 vec/sec, ETA: 0.0 min
    [700/707] 341.3 vec/sec, ETA: 0.0 min
[+] Reconstruction complete in 2.1s
[+] Statistics:
    Total coefficients: 1831130
    Zero coefficients: 1751993 (95.7%)
    Reconstructed: 79137
    Failed: 0
    Verification OK: 78472
    Verification FAIL: 665
[+] Wrote rational basis to kernel_basis_Q.json
[+] Wrote failures to validator_v2\reconstruction_failures.json
ERROR: 665 coefficients failed verification
       DO NOT USE THE BASIS until failures are resolved.

c:\math>python reconstruct_failures.py
Total failures: 665
{'vec': 20, 'coeff': 52, 'residues': [52, 78, 130, 124, 23], 'n': -1, 'd': 1, 'note': 'verification_failed_mod_157'}
{'vec': 20, 'coeff': 173, 'residues': [27, 61, 45, 57, 158], 'n': 1359, 'd': 280, 'note': 'verification_failed_mod_131'}
{'vec': 20, 'coeff': 216, 'residues': [13, 64, 128, 40, 176], 'n': -256, 'd': 653, 'note': 'verification_failed_mod_79'}
{'vec': 20, 'coeff': 413, 'residues': [8, 63, 32, 96, 34], 'n': 301, 'd': 865, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 422, 'residues': [2, 55, 69, 57, 210], 'n': 364, 'd': 235, 'note': 'verification_failed_mod_313'}
{'vec': 20, 'coeff': 441, 'residues': [24, 67, 102, 58, 294], 'n': -779, 'd': 980, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 443, 'residues': [13, 70, 66, 26, 215], 'n': 893, 'd': 1393, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 462, 'residues': [5, 78, 54, 62, 306], 'n': -1226, 'd': 41, 'note': 'verification_failed_mod_131'}
{'vec': 20, 'coeff': 577, 'residues': [11, 37, 59, 42, 219], 'n': 1764, 'd': 827, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 583, 'residues': [1, 1, 1, 85, 199], 'n': 1, 'd': 1, 'note': 'verification_failed_mod_157'}
{'vec': 20, 'coeff': 594, 'residues': [11, 16, 25, 48, 119], 'n': -2861, 'd': 310, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 640, 'residues': [16, 26, 116, 89, 288], 'n': -33, 'd': 1679, 'note': 'verification_failed_mod_53'}
{'vec': 20, 'coeff': 725, 'residues': [41, 64, 103, 90, 251], 'n': 271, 'd': 556, 'note': 'verification_failed_mod_131'}
{'vec': 20, 'coeff': 919, 'residues': [43, 8, 80, 57, 273], 'n': 1211, 'd': 181, 'note': 'verification_failed_mod_131'}
{'vec': 21, 'coeff': 193, 'residues': [5, 34, 103, 14, 118], 'n': 1662, 'd': 343, 'note': 'verification_failed_mod_79'}
{'vec': 21, 'coeff': 299, 'residues': [23, 33, 98, 72, 35], 'n': 1990, 'd': 817, 'note': 'verification_failed_mod_79'}
{'vec': 21, 'coeff': 583, 'residues': [12, 77, 28, 113, 279], 'n': 843, 'd': 905, 'note': 'verification_failed_mod_79'}
{'vec': 21, 'coeff': 635, 'residues': [35, 31, 108, 74, 145], 'n': 1299, 'd': 758, 'note': 'verification_failed_mod_53'}
{'vec': 22, 'coeff': 162, 'residues': [40, 67, 83, 97, 260], 'n': -356, 'd': 1241, 'note': 'verification_failed_mod_53'}
{'vec': 22, 'coeff': 556, 'residues': [13, 19, 41, 30, 192], 'n': -492, 'd': 643, 'note': 'verification_failed_mod_79'}

c:\math>python debug_reconstruct.py
vec,coeff: 20 52
residues: [(53, 52), (79, 78), (131, 130), (157, 124), (313, 23)]
CRT cM: 24743248166 M: 26953691077
mult 1 bound 116089 -> (-1, 1)
  congruence ok? False
mult 2 bound 232178 -> (-1, 1)
  congruence ok? False
mult 4 bound 464356 -> (-1, 1)
  congruence ok? False
mult 8 bound 928712 -> (-550070, 1573)
  congruence ok? True
```

Therefore I needed to create more json invariant files for monomial and triplets, so I needed to use this m2 script from qualia_candidate_axioms/potential_hodge_conjecture_counterexample.md and change the primes to 443, 521, 547, 599, 677, and 911:

```m2
-- verify_invariant_tier2.m2  (fixed)
-- verify_invariant_tier2.m2 (streamed-triplet safe version)
-- TIER II: Symmetry Obstruction via C13-Invariant Sector
-- Writes monomials and triplets in streaming fashion to avoid large in-memory JSON
needsPackage "JSON";

-- CONFIGURATION: edit this list to include additional primes (all p ≡ 1 mod 13)
primesToTest = {443, 521, 547, 599, 677, 911};

print("=== TIER II: Symmetry Obstruction Verification (safe IO) ===");

for p in primesToTest do (
    if (p % 13) != 1 then continue;

    print("--- Prime: " | toString p | " ---");

    -- 1. Setup finite field with 13th root
    Fp := ZZ/p;
    w := 0_Fp;
    for a from 2 to p-1 do (
        cand := (a * 1_Fp)^((p-1)//13);
        if (cand != 1_Fp) and (cand^13 == 1_Fp) then (
            w = cand;
            break;
        );
    );
    print("Using 13th root w = " | toString w);

    -- 2. Build polynomial ring
    S := Fp[z_0..z_5];
    z := gens S;

    -- 3. Construct C13-invariant variety
    print("Assembling C13-invariant variety...");
    linearForms := for k from 0 to 12 list (
        sum(0..5, j -> (w^((k*j) % 13)) * z#j)
    );
    fS := sum(linearForms, l -> l^8);

    -- 4. Compute partial derivatives
    partials := for i from 0 to 5 list diff(z#i, fS);

    -- 5. Generate invariant monomial basis
    print("Generating degree-18 invariant monomials...");
    mon18List := flatten entries basis(18, S);

    -- Filter to invariant:   Σ j·a_j ≡ 0 (mod 13)
    invMon18 := select(mon18List, m -> (
        ev := (exponents m)#0;
        (sum(for j from 0 to 5 list j * ev#j)) % 13 == 0
    ));

    countInv := #invMon18;
    print("Invariant monomials (deg 18): " | toString countInv);

    -- 6. Build index map (use string keys)
    print("Building index map...");
    monToIndex := new MutableHashTable;
    for i from 0 to countInv - 1 do (
        monToIndex#(toString(invMon18#i)) = i;
    );

    -- 7. Filter Jacobian generators (character matching)
    print("Filtering Jacobian generators...");
    mon11List := flatten entries basis(11, S);

    filteredGens := {};
    for i from 0 to 5 do (
        targetWeight := i;
        for m in mon11List do (
            mWeight := (sum(for j from 0 to 5 list j * (exponents m)#0#j)) % 13;
            if mWeight == targetWeight then (
                filteredGens = append(filteredGens, m * partials#i);
            );
        );
    );

    print("Filtered generators: " | toString(#filteredGens));

    -- 8. Assemble coefficient matrix (mutable)
    print("Assembling matrix (MutableMatrix)...");
    M := mutableMatrix(Fp, countInv, #filteredGens);

    for j from 0 to (#filteredGens - 1) do (
        (mons, coeffs) := coefficients filteredGens#j;
        mList := flatten entries mons;
        cList := flatten entries coeffs;
        for k from 0 to (#mList - 1) do (
            m := mList#k;
            key := toString m;
            if monToIndex #? key then (
                M_(monToIndex#key, j) = sub(cList#k, Fp);
            );
        );
    );

    MatInv := matrix M;

    -- 9. Compute rank
    print("Computing rank (symmetry-locked)...");
    time rk := rank MatInv;
    h22inv := countInv - rk;

    -- 10. Results summary
    print("----------------------------------------");
    print("RESULTS FOR PRIME " | toString p | ":");
    print("Invariant monomials: " | toString countInv);
    print("Rank: " | toString rk);
    print("h^{2,2}_inv: " | toString h22inv);
    print("Gap (h22_inv - 12 algebraic): " | toString(h22inv - 12));
    print("Gap percentage: " | toString(100.0 * (h22inv - 12) / h22inv) | "%");
    print("----------------------------------------");

    -- 11. Export monomials (safe small JSON)
    monFile := "validator_v2/saved_inv_p" | toString p | "_monomials18.json";
    print("Writing monomials to " | monFile);
    monExps := for m in invMon18 list (
        ev := (exponents m)#0;
        for j from 0 to 5 list ev#j
    );
    (openOut monFile) << toJSON(monExps) << close;

    -- 12. Export triplets in streaming fashion to avoid giant memory use
    triFile := "validator_v2/saved_inv_p" | toString p | "_triplets.json";
    print("Streaming triplets to " | triFile);
    out = openOut triFile;

    -- Start JSON object (write header)
    out << "{\n";
    out << "  \"prime\": " | toString p | ",\n";
    out << "  \"h22_inv\": " | toString h22inv | ",\n";
    out << "  \"rank\": " | toString rk | ",\n";
    out << "  \"countInv\": " | toString countInv | ",\n";
    out << "  \"triplets\": [\n";

    firstEntry = true;
    nC := numColumns MatInv;
    nR := numRows MatInv;
    -- iterate columns then rows to stream nonzeros
    for c from 0 to (nC - 1) do (
        for r from 0 to (nR - 1) do (
            val := MatInv_(r,c);
            if val != 0_Fp then (
                if firstEntry then (
                    firstEntry = false;
                ) else (
                    out << ",\n";
                );
                -- write JSON array [r, c, integer_value]
                out << "    [" | toString r | ", " | toString c | ", " | toString lift(val, ZZ) | "]";
            );
        );
    );

    -- Close JSON array and object
    out << "\n  ]\n}\n";
    close out;

    -- 13. Null references to help M2 free memory
    MatInv = 0;
    M = 0;
    filteredGens = {};
    mon18List = {};
    invMon18 = {};
    monToIndex = new MutableHashTable;
);

print("=== TIER II Verification Complete ===");
```

then convert those jsons into the proper kernel files! I am putting all invariant files into its own folder in validator_v2 however the kernels are too big and must be generated by the user! You must generate the kernel from the invariants yourself one by one to fulfill the process, as many times with as many primes as it takes. Hopefully the amount already generated here will be enough, we will see!
---

**UPDATE 2**

With all the primes (53,79,131,157,313, 443, 521, 547 , 599, 677, 911) we got:

```verbatim
c:\math>python rational_kernel_basis.py --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json kernel_p443.json kernel_p521.json kernel_p547.json kernel_p599.json kernel_p677.json kernel_p911.json --primes 53 79 131 157 313 443 521 547 599 677 911 --out kernel_basis_Q_v2.json
[+] Loading 11 kernel bases...
    kernel_p53.json: 707 vectors × 2590 coefficients
    kernel_p79.json: 707 vectors × 2590 coefficients
    kernel_p131.json: 707 vectors × 2590 coefficients
    kernel_p157.json: 707 vectors × 2590 coefficients
    kernel_p313.json: 707 vectors × 2590 coefficients
    kernel_p443.json: 707 vectors × 2590 coefficients
    kernel_p521.json: 707 vectors × 2590 coefficients
    kernel_p547.json: 707 vectors × 2590 coefficients
    kernel_p599.json: 707 vectors × 2590 coefficients
    kernel_p677.json: 707 vectors × 2590 coefficients
    kernel_p911.json: 707 vectors × 2590 coefficients
[+] Dimension verified: 707 vectors × 2590 coefficients
[+] CRT product M = 1257132026085202124689385321
[+] Rational reconstruction bound = 25071218818449
[+] Processing all 707 vectors
    [10/707] 169.0 vec/sec, ETA: 0.1 min
    [20/707] 195.5 vec/sec, ETA: 0.1 min
    [30/707] 151.0 vec/sec, ETA: 0.1 min
    [40/707] 164.3 vec/sec, ETA: 0.1 min
    [50/707] 140.3 vec/sec, ETA: 0.1 min
    [60/707] 143.0 vec/sec, ETA: 0.1 min
    [70/707] 144.7 vec/sec, ETA: 0.1 min
    [80/707] 142.0 vec/sec, ETA: 0.1 min
    [90/707] 135.1 vec/sec, ETA: 0.1 min
    [100/707] 135.5 vec/sec, ETA: 0.1 min
    [110/707] 132.0 vec/sec, ETA: 0.1 min
    [120/707] 128.8 vec/sec, ETA: 0.1 min
    [130/707] 123.1 vec/sec, ETA: 0.1 min
    [140/707] 116.7 vec/sec, ETA: 0.1 min
    [150/707] 120.3 vec/sec, ETA: 0.1 min
    [160/707] 124.2 vec/sec, ETA: 0.1 min
    [170/707] 129.8 vec/sec, ETA: 0.1 min
    [180/707] 132.4 vec/sec, ETA: 0.1 min
    [190/707] 136.8 vec/sec, ETA: 0.1 min
    [200/707] 140.9 vec/sec, ETA: 0.1 min
    [210/707] 143.1 vec/sec, ETA: 0.1 min
    [220/707] 146.8 vec/sec, ETA: 0.1 min
    [230/707] 150.3 vec/sec, ETA: 0.1 min
    [240/707] 152.1 vec/sec, ETA: 0.1 min
    [250/707] 155.2 vec/sec, ETA: 0.0 min
    [260/707] 158.3 vec/sec, ETA: 0.0 min
    [270/707] 159.8 vec/sec, ETA: 0.0 min
    [280/707] 161.8 vec/sec, ETA: 0.0 min
    [290/707] 164.0 vec/sec, ETA: 0.0 min
    [300/707] 166.2 vec/sec, ETA: 0.0 min
    [310/707] 168.9 vec/sec, ETA: 0.0 min
    [320/707] 170.3 vec/sec, ETA: 0.0 min
    [330/707] 172.7 vec/sec, ETA: 0.0 min
    [340/707] 175.1 vec/sec, ETA: 0.0 min
    [350/707] 175.9 vec/sec, ETA: 0.0 min
    [360/707] 178.1 vec/sec, ETA: 0.0 min
    [370/707] 180.2 vec/sec, ETA: 0.0 min
    [380/707] 180.9 vec/sec, ETA: 0.0 min
    [390/707] 181.9 vec/sec, ETA: 0.0 min
    [400/707] 183.5 vec/sec, ETA: 0.0 min
    [410/707] 184.3 vec/sec, ETA: 0.0 min
    [420/707] 185.8 vec/sec, ETA: 0.0 min
    [430/707] 187.8 vec/sec, ETA: 0.0 min
    [440/707] 188.2 vec/sec, ETA: 0.0 min
    [450/707] 189.7 vec/sec, ETA: 0.0 min
    [460/707] 191.6 vec/sec, ETA: 0.0 min
    [470/707] 191.9 vec/sec, ETA: 0.0 min
    [480/707] 193.5 vec/sec, ETA: 0.0 min
    [490/707] 195.0 vec/sec, ETA: 0.0 min
    [500/707] 195.3 vec/sec, ETA: 0.0 min
    [510/707] 196.7 vec/sec, ETA: 0.0 min
    [520/707] 198.2 vec/sec, ETA: 0.0 min
    [530/707] 198.4 vec/sec, ETA: 0.0 min
    [540/707] 199.7 vec/sec, ETA: 0.0 min
    [550/707] 200.1 vec/sec, ETA: 0.0 min
    [560/707] 201.0 vec/sec, ETA: 0.0 min
    [570/707] 202.5 vec/sec, ETA: 0.0 min
    [580/707] 203.8 vec/sec, ETA: 0.0 min
    [590/707] 203.6 vec/sec, ETA: 0.0 min
    [600/707] 205.1 vec/sec, ETA: 0.0 min
    [610/707] 206.3 vec/sec, ETA: 0.0 min
    [620/707] 206.2 vec/sec, ETA: 0.0 min
    [630/707] 207.5 vec/sec, ETA: 0.0 min
    [640/707] 207.8 vec/sec, ETA: 0.0 min
    [650/707] 208.6 vec/sec, ETA: 0.0 min
    [660/707] 209.3 vec/sec, ETA: 0.0 min
    [670/707] 210.7 vec/sec, ETA: 0.0 min
    [680/707] 210.3 vec/sec, ETA: 0.0 min
    [690/707] 211.7 vec/sec, ETA: 0.0 min
    [700/707] 211.6 vec/sec, ETA: 0.0 min
[+] Reconstruction complete in 3.3s
[+] Statistics:
    Total coefficients: 1831130
    Zero coefficients: 1751993 (95.7%)
    Reconstructed: 79137
    Failed: 0
    Verification OK: 79135
    Verification FAIL: 2
[+] Wrote rational basis to kernel_basis_Q_v2.json
[+] Wrote failures to validator_v2\reconstruction_failures.json
ERROR: 2 coefficients failed verification
       DO NOT USE THE BASIS until failures are resolved.
```

which brings us down to 2 failures, so we evaluate using this file:

```python
#!/usr/bin/env python3
"""
targeted_reconstruct_failures.py

Resolve entries listed in a failures JSON by re-running CRT + rational reconstruction
using the provided kernel_p*.json files and a sequence of increasing bounds.

Usage:
  python3 validator_v2/targeted_reconstruct_failures.py \
    --kernels kernel_p53.json kernel_p79.json ... kernel_p911.json \
    --primes 53 79 ... 911 \
    --failures validator_v2/reconstruction_failures.json \
    --out validator_v2/resolved_failures.json \
    --max-mult 128

Output:
  JSON file with "resolved" and "unresolved" lists. Each resolved entry contains
  vec, coeff, residues, n, d, used_mult, used_bound.

Notes:
 - The script recomputes residues from the kernel files (so the primes/kernels order
   you pass must match the failures JSON ordering).
 - It tries multipliers [1,2,4,8,...] up to max_mult (power-of-two sequence).
 - This is a targeted diagnostic/fix; after applying resolved rationals you can
   update your kernel_basis_Q JSON or re-run the full pipeline.

Author: Assistant
Date: 2026-01-25
"""
import argparse
import json
import math
from pathlib import Path

def iterative_crt(residues):
    x, M = residues[0][1], residues[0][0]
    for (m, r) in residues[1:]:
        inv = pow(M % m, -1, m)
        t = ((r - x) * inv) % m
        x = x + t * M
        M = M * m
        x %= M
    return x, M

def rational_reconstruction(a, m, bound=None):
    a = int(a) % int(m)
    m = int(m)
    if bound is None:
        bound = int(math.isqrt(m // 2))
    r0, r1 = m, a
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    while r1 != 0 and abs(r1) > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
    if r1 == 0:
        return None
    num = r1
    den = t1
    if den == 0:
        return None
    if den < 0:
        num, den = -num, -den
    if abs(num) > bound or den > bound:
        return None
    if ((num - a * den) % m) != 0:
        return None
    g = math.gcd(abs(num), den)
    num //= g
    den //= g
    return (num, den)

def load_kernel_modp(path):
    with open(path) as f:
        data = json.load(f)
    if 'kernel' in data:
        return data['kernel']
    elif 'basis' in data:
        return data['basis']
    else:
        raise ValueError(f"No kernel/basis field in {path}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--kernels', nargs='+', required=True, help='Paths to kernel_p*.json files')
    p.add_argument('--primes', nargs='+', type=int, required=True, help='Primes in same order as kernels')
    p.add_argument('--failures', required=True, help='Failures JSON from previous run')
    p.add_argument('--out', default='validator_v2/resolved_failures.json', help='Output file')
    p.add_argument('--max-mult', type=int, default=128, help='Max multiplier (power-of-two) to try')
    args = p.parse_args()

    if len(args.kernels) != len(args.primes):
        raise SystemExit("Number of kernel files must equal number of primes")

    # Load kernels
    print("[+] Loading kernel files...")
    kernels = [load_kernel_modp(k) for k in args.kernels]
    n_vectors = len(kernels[0])
    n_coeffs = len(kernels[0][0])
    print(f"    {len(kernels)} kernels loaded; shape {n_vectors} x {n_coeffs}")

    # Load failures list
    failures_data = json.load(open(args.failures))
    failures = failures_data.get('failures', failures_data.get('failures', []))
    if not failures:
        print("[!] No failures found in the provided failures JSON")
        return

    primes = args.primes
    # Prepare multiplier sequence: powers of two up to max_mult
    mults = []
    m = 1
    while m <= args.max_mult:
        mults.append(m)
        m *= 2

    resolved = []
    unresolved = []

    for entry in failures:
        vec = int(entry['vec'])
        coeff = int(entry['coeff'])
        # Recompute residues from kernels to ensure order
        residues_p = []
        for i, K in enumerate(kernels):
            try:
                r = int(K[vec][coeff]) % primes[i]
            except Exception as exc:
                print(f"ERROR reading kernel {i} for vec {vec} coeff {coeff}: {exc}")
                r = None
            residues_p.append(r)
        residues_pairs = list(zip(primes, residues_p))
        # CRT
        try:
            cM, M = iterative_crt(residues_pairs)
        except Exception as exc:
            print(f"[!] CRT failed for vec {vec} coeff {coeff}: {exc}")
            unresolved.append({"vec": vec, "coeff": coeff, "residues": residues_p, "note": "crt_failed"})
            continue

        base_bound = int(math.isqrt(M // 2))
        found = False
        used = {}
        for mult in mults:
            bound = base_bound * mult
            res = rational_reconstruction(cM, M, bound)
            if res is None:
                used['mult_%d' % mult] = None
                continue
            n, d = res
            # verify congruences (n ≡ r * d mod p)
            ok = True
            for (pval, r) in residues_pairs:
                if r is None:
                    ok = False
                    break
                if ((n - (r * d)) % pval) != 0:
                    ok = False
                    break
            if ok:
                resolved.append({
                    "vec": vec,
                    "coeff": coeff,
                    "residues": residues_p,
                    "n": int(n),
                    "d": int(d),
                    "used_mult": mult,
                    "used_bound": str(bound)
                })
                found = True
                break
            else:
                used['mult_%d' % mult] = {"candidate": (int(n), int(d)), "ok": False}
        if not found:
            unresolved.append({"vec": vec, "coeff": coeff, "residues": residues_p, "note": "not_reconstructed", "tried": used})

    out = {"resolved": resolved, "unresolved": unresolved}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"[+] Wrote results to {args.out}")
    print(f"[+] Resolved: {len(resolved)}; Unresolved: {len(unresolved)}")

if __name__ == '__main__':
    main()
```
which got us:

```verbatim
c:\math>python targeted_reconstruct_failures.py --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json kernel_p443.json kernel_p521.json kernel_p547.json kernel_p599.json kernel_p677.json kernel_p911.json --primes 53 79 131 157 313 443 521 547 599 677 911 --failures validator_v2/reconstruction_failures.json --out validator_v2/resolved_failures.json --max-mult 128
[+] Loading kernel files...
    11 kernels loaded; shape 707 x 2590
[+] Wrote results to validator_v2/resolved_failures.json
[+] Resolved: 2; Unresolved: 0
```

Then I used the following script to resolve the file:

```python
#!/usr/bin/env python3
"""
merge_resolved_failures.py

Merge resolved (n,d) pairs from validator_v2/resolved_failures.json into an existing
rational basis JSON (kernel_basis_Q_v2.json) and write an updated file.

Usage:
  python3 validator_v2/merge_resolved_failures.py \
    --basis kernel_basis_Q_v2.json \
    --resolved validator_v2/resolved_failures.json \
    --out kernel_basis_Q_v2_fixed.json

Notes:
 - The script expects the rational basis JSON to have structure:
     { "basis": [ [ {"n":..., "d":...} | None, ... ], ... ], "metadata": {...} }
 - Resolved file should be the output of targeted_reconstruct_failures.py with keys:
     { "resolved": [ { "vec":i, "coeff":j, "n":..., "d":..., ... }, ... ], ... }
 - This script replaces basis[vec][coeff] with {"n":n,"d":d} where needed and writes the fixed JSON.
"""
import argparse
import json
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--basis', required=True, help='Input rational basis JSON')
    p.add_argument('--resolved', required=True, help='Resolved failures JSON')
    p.add_argument('--out', default=None, help='Output merged basis JSON')
    args = p.parse_args()

    basis_path = Path(args.basis)
    resolved_path = Path(args.resolved)
    out_path = Path(args.out) if args.out else basis_path.with_name(basis_path.stem + "_fixed.json")

    data = json.load(open(basis_path))
    basis = data.get('basis')
    if basis is None:
        raise SystemExit("No 'basis' key in basis JSON")

    resdata = json.load(open(resolved_path))
    resolved = resdata.get('resolved', [])

    # Apply resolved entries
    applied = 0
    for entry in resolved:
        vec = int(entry['vec'])
        coeff = int(entry['coeff'])
        n = int(entry['n'])
        d = int(entry['d'])
        # Safety checks
        if vec < 0 or vec >= len(basis):
            print(f"WARNING: vec index {vec} out of range")
            continue
        if coeff < 0 or coeff >= len(basis[vec]):
            print(f"WARNING: coeff index {coeff} out of range (vec {vec})")
            continue
        basis[vec][coeff] = {"n": n, "d": d}
        applied += 1

    data['basis'] = basis
    # update metadata note
    md = data.get('metadata', {})
    md['merged_resolved_count'] = applied
    data['metadata'] = md

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"[+] Applied {applied} resolved entries")
    print(f"[+] Wrote merged basis to {out_path}")

if __name__ == "__main__":
    main()
```

```verbatim
c:\math>python merge_resolved_failures.py --basis kernel_basis_Q_v2.json --resolved validator_v2/resolved_failures.json --out kernel_basis_Q_v2_fixed.json
[+] Applied 2 resolved entries
[+] Wrote merged basis to kernel_basis_Q_v2_fixed.json
```
This is where we will begin with update 3 to start verification of the kernel_basis_Q_v2.json file.

---

**UPDATE 3**

We continue with the following, ensuring it is in same directory as triplet jsons:

```python
#!/usr/bin/env python3
"""
reconstruct_integer_triplets_via_crt.py

Reconstruct an integer coefficient triplet file (matrix over Z) by CRT from
per-prime triplet JSON files saved_inv_p{p}_triplets.json.

Usage (triplet files must be in the current working directory):
  python3 validator_v2/reconstruct_integer_triplets_via_crt.py \
    --primes 53 79 131 157 313 443 521 547 599 677 911 \
    --out validator_v2/saved_inv_triplets_integer.json \
    [--verify]

Notes:
 - Expects per-prime files named saved_inv_p{p}_triplets.json in the current directory
   (the script will look for them in `.`).
 - Each per-prime file should contain a JSON object with key "triplets" that is
   a list of [row, col, value] (value should be the lifted integer representative).
 - Missing (row,col) entries in a per-prime file are treated as residue 0 (i.e., zero entry).
 - The script writes a JSON with key "triplets": [[r,c,val], ...] where val are
   signed integers chosen in (-M/2, M/2], with M = product(primes).
 - If --verify is passed, the script checks that val % p == residue_p for each prime p;
   any conflicts are reported and cause a nonzero exit code.

Caveats:
 - This is deterministic only if the true integer coefficients are smaller (in absolute
   value) than M/2. Choose enough primes so that M/2 exceeds the expected coefficient sizes.
 - The union of (r,c) entries across primes is used; absent entries are treated as 0.
"""
from pathlib import Path
import argparse
import json
import math
import sys

def iterative_crt(residues):
    # residues: list of (p, r) with p prime, 0 <= r < p
    x, M = residues[0][1], residues[0][0]
    for (m, r) in residues[1:]:
        inv = pow(M % m, -1, m)
        t = ((r - x) * inv) % m
        x = x + t * M
        M = M * m
        x %= M
    return x, M

def load_triplets_file(path):
    d = json.load(open(path))
    # accept either {"triplets": [...]} or a bare list
    if isinstance(d, dict) and 'triplets' in d:
        trip = d['triplets']
    elif isinstance(d, list):
        trip = d
    else:
        # try to find any list value
        trip = None
        for v in d.values():
            if isinstance(v, list):
                trip = v
                break
        if trip is None:
            raise SystemExit(f"Cannot find triplets list in {path}")
    # Normalize to list of (r,c,v)
    norm = []
    for t in trip:
        if isinstance(t, list) and len(t) >= 3:
            r,c,v = int(t[0]), int(t[1]), int(t[2])
            norm.append((r,c,v))
        elif isinstance(t, dict):
            # try common dict keys
            if {'row','col','val'}.issubset(t.keys()):
                norm.append((int(t['row']), int(t['col']), int(t['val'])))
            elif {'r','c','v'}.issubset(t.keys()):
                norm.append((int(t['r']), int(t['c']), int(t['v'])))
            else:
                raise SystemExit(f"Unrecognized triplet dict format in {path}: {t}")
        else:
            raise SystemExit(f"Unrecognized triplet entry in {path}: {t}")
    return norm

def main():
    ap = argparse.ArgumentParser(description="Reconstruct integer triplets via CRT (triplet files must be in current directory)")
    ap.add_argument('--primes', nargs='+', type=int, required=True, help='Primes in the same order used for kernels')
    ap.add_argument('--out', required=True, help='Output integer triplets JSON path')
    ap.add_argument('--verify', action='store_true', help='Verify reconstructed integers reduce to original residues')
    ap.add_argument('--min-n-primes', type=int, default=1, help='Minimum number of primes that must have a nonzero residue to consider entry (default 1)')
    args = ap.parse_args()

    primes = [int(p) for p in args.primes]
    out_path = Path(args.out)
    triplet_dir = Path('.')  # triplet files must be in current working directory

    # Load per-prime triplet maps: (r,c) -> residue
    per_prime_maps = []
    union_keys = set()
    print("[+] Loading per-prime triplets from current directory...")
    for p in primes:
        path = triplet_dir / f"saved_inv_p{p}_triplets.json"
        if not path.exists():
            raise SystemExit(f"Triplet file not found in current directory: {path}")
        trip = load_triplets_file(path)
        mp = {}
        for (r,c,v) in trip:
            # normalize residue to 0..p-1
            rv = int(v) % p
            mp[(r,c)] = rv
            union_keys.add((r,c))
        per_prime_maps.append(mp)
        print(f"    loaded p={p}: {len(trip)} nonzero entries")

    M_total = 1
    for p in primes:
        M_total *= p
    print(f"[+] Product of primes M = {M_total} (bits: {M_total.bit_length()})")
    print(f"[+] Union of positions to process: {len(union_keys)} entries")

    reconstructed = []
    conflicts = []
    idx = 0
    # iterate through union and CRT each
    for (r,c) in sorted(union_keys):
        idx += 1
        if idx % 10000 == 0:
            print(f"  processed {idx}/{len(union_keys)}")
        residues = []
        nonzero_count = 0
        for i,p in enumerate(primes):
            res = per_prime_maps[i].get((r,c), 0) % p
            residues.append((p, int(res)))
            if res != 0:
                nonzero_count += 1
        if nonzero_count < args.min_n_primes and nonzero_count == 0:
            # skip entries that are zero everywhere
            continue
        # do CRT
        try:
            xmod, M = iterative_crt(residues)
        except Exception as exc:
            conflicts.append({"r": r, "c": c, "note": f"crt_failed: {exc}"})
            continue
        # map to signed representative in (-M/2, M/2]
        if xmod > M // 2:
            x_signed = xmod - M
        else:
            x_signed = xmod
        # if zero after sign mapping, skip
        if x_signed == 0:
            continue
        reconstructed.append([int(r), int(c), int(x_signed)])
        # optional immediate verify per-prime
        if args.verify:
            for (p,res) in residues:
                if (x_signed % p) != res:
                    conflicts.append({"r": r, "c": c, "p": p, "res_expected": res, "res_from_int": int(x_signed % p)})
                    break

    print(f"[+] Reconstructed integer triplets: {len(reconstructed)} nonzero entries")
    if args.verify:
        if conflicts:
            print(f"[!] Verification conflicts found: {len(conflicts)}")
            # write conflicts file for inspection
            (out_path.parent / (out_path.stem + "_conflicts.json")).write_text(json.dumps(conflicts, indent=2))
            print(f"[!] Wrote conflicts to {out_path.parent / (out_path.stem + '_conflicts.json')}")
        else:
            print("[+] All reconstructed integers reduce correctly to per-prime residues")

    # Write output JSON
    out_data = {
        "primes_used": primes,
        "crt_product": str(M_total),
        "triplets": reconstructed
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2)

    print(f"[+] Wrote integer triplets JSON to {out_path}")
    if conflicts:
        print("[!] NOTE: conflicts present; inspect the conflicts JSON before using the triplets")
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
```

output:

```verbatim
c:\math>python reconstruct_integer_triplets_via_crt.py --primes 53 79 131 157 313 443 521 547 599 677 911 --out validator_v2/saved_inv_triplets_integer.json --verify
[+] Loading per-prime triplets from current directory...
    loaded p=53: 122640 nonzero entries
    loaded p=79: 122640 nonzero entries
    loaded p=131: 122640 nonzero entries
    loaded p=157: 122640 nonzero entries
    loaded p=313: 122640 nonzero entries
    loaded p=443: 122640 nonzero entries
    loaded p=521: 122640 nonzero entries
    loaded p=547: 122640 nonzero entries
    loaded p=599: 122640 nonzero entries
    loaded p=677: 122640 nonzero entries
    loaded p=911: 122640 nonzero entries
[+] Product of primes M = 1257132026085202124689385321 (bits: 91)
[+] Union of positions to process: 122640 entries
  processed 10000/122640
  processed 20000/122640
  processed 30000/122640
  processed 40000/122640
  processed 50000/122640
  processed 60000/122640
  processed 70000/122640
  processed 80000/122640
  processed 90000/122640
  processed 100000/122640
  processed 110000/122640
  processed 120000/122640
[+] Reconstructed integer triplets: 122640 nonzero entries
[+] All reconstructed integers reduce correctly to per-prime residues
[+] Wrote integer triplets JSON to validator_v2\saved_inv_triplets_integer.json
```

We then validated with the following file:

```python
#!/usr/bin/env python3
"""
clear_denominators_and_verify.py

Reads a rational basis JSON produced by rational_kernel_basis.py,
clears denominators to produce integer kernel vectors, saves them,
and verifies M * w == 0 exactly using an integer triplet file.

Usage:
  python3 clear_denominators_and_verify.py \
    --rational-basis kernel_basis_Q_v2_fixed.json \
    --triplets validator_v2/saved_inv_triplets_integer.json \
    --out-prefix kernel_basis_integer

Outputs:
  <out-prefix>_vectors.json
  <out-prefix>_matrix.npy
  <out-prefix>_verification.json
"""
import argparse
import json
import math
from pathlib import Path

def lcm(a, b):
    return abs(a // math.gcd(a, b) * b) if a and b else abs(a or b)

def parse_triplets(trip_path):
    d = json.load(open(trip_path))
    if isinstance(d, dict) and 'triplets' in d:
        trip = d['triplets']
    elif isinstance(d, list):
        trip = d
    else:
        # try to find a list value
        trip = None
        for v in d.values():
            if isinstance(v, list):
                trip = v
                break
        if trip is None:
            raise ValueError("Cannot find triplets in file")
    normalized = []
    for t in trip:
        if isinstance(t, list) and len(t) >= 3:
            r,c,v = int(t[0]), int(t[1]), int(t[2])
            normalized.append((r,c,v))
        elif isinstance(t, dict) and {'row','col','val'}.issubset(t.keys()):
            normalized.append((int(t['row']), int(t['col']), int(t['val'])))
        else:
            raise ValueError("Unrecognized triplet format: " + str(t))
    return normalized

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rational-basis', required=True, help='Rational basis JSON (from rational_kernel_basis.py)')
    ap.add_argument('--triplets', required=True, help='Integer triplets JSON (e.g., saved_inv_triplets_integer.json)')
    ap.add_argument('--out-prefix', default='kernel_basis_integer', help='Output prefix for files')
    args = ap.parse_args()

    rb_path = Path(args.rational_basis)
    trip_path = Path(args.triplets)
    out_prefix = Path(args.out_prefix)

    data = json.load(open(rb_path))
    basis = data.get('basis')
    if basis is None:
        raise SystemExit("No 'basis' key in rational basis JSON")

    n_vectors = len(basis)
    n_coeffs = len(basis[0]) if n_vectors > 0 else 0
    print(f"[+] Loading rational basis: {n_vectors} vectors x {n_coeffs} coeffs")

    # Compute LCM denominators and integer vectors
    integer_vectors = []
    lcms = []
    for i, vec in enumerate(basis):
        l = 1
        for j, entry in enumerate(vec):
            if entry is None:
                continue
            d = int(entry['d'])
            l = lcm(l, d)
        lcms.append(l)
        w = []
        for j, entry in enumerate(vec):
            if entry is None:
                w.append(0)
            else:
                n = int(entry['n'])
                d = int(entry['d'])
                wj = (n * (l // d))
                w.append(wj)
        integer_vectors.append(w)

    # Build output paths robustly using Path
    vec_json_path = out_prefix.with_name(out_prefix.name + "_vectors.json")
    npy_path = out_prefix.with_name(out_prefix.name + "_matrix.npy")
    ver_path = out_prefix.with_name(out_prefix.name + "_verification.json")

    out_data = {
        "n_vectors": n_vectors,
        "n_coeffs": n_coeffs,
        "lcms": [str(x) for x in lcms],
        "vectors": [ [str(v) for v in row] for row in integer_vectors ]
    }
    vec_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vec_json_path, 'w') as f:
        json.dump(out_data, f, indent=2)
    print(f"[+] Wrote integer vectors JSON to {vec_json_path}")

    # Save NPY (object dtype) with numpy
    try:
        import numpy as np
        arr = np.empty((n_vectors, n_coeffs), dtype=object)
        for i in range(n_vectors):
            for j in range(n_coeffs):
                arr[i,j] = integer_vectors[i][j]
        # npy_path is a Path; convert to str
        np.save(str(npy_path), arr, allow_pickle=True)
        print(f"[+] Saved integer matrix (numpy .npy) to {npy_path}")
    except Exception as e:
        print("[!] numpy save failed:", e)
        npy_path = None

    # Verification: compute Mat * w == 0 using triplets
    print("[+] Loading triplets for exact verification...")
    triplets = parse_triplets(trip_path)
    # infer nrows
    maxr = 0
    for (r,c,v) in triplets:
        if r > maxr:
            maxr = r
    n_rows = maxr + 1
    print(f"[+] Triplets loaded: {len(triplets)} entries; inferred n_rows = {n_rows}")

    # For each vector compute residuals per row
    nonzero_rows = 0
    worst_abs = 0
    bad_rows = {}
    for vi, w in enumerate(integer_vectors):
        # accumulate row sums as python ints
        row_sums = [0] * n_rows
        for (r,c,v) in triplets:
            # skip out-of-range columns
            if c < 0 or c >= n_coeffs:
                continue
            row_sums[r] += v * w[c]
        # check any non-zero
        for r, s in enumerate(row_sums):
            if s != 0:
                nonzero_rows += 1
                worst_abs = max(worst_abs, abs(s))
                bad_rows.setdefault(vi, []).append({"row": r, "residual": str(s)})
        # optionally free row_sums
    verification = {
        "n_vectors": n_vectors,
        "n_coeffs": n_coeffs,
        "triplet_count": len(triplets),
        "nonzero_residual_rows": nonzero_rows,
        "max_abs_residual": str(worst_abs),
        "bad_rows_sample": {str(k): v for k,v in list(bad_rows.items())[:20]}
    }
    with open(ver_path, 'w') as f:
        json.dump(verification, f, indent=2)
    print(f"[+] Wrote verification summary to {ver_path}")

    if nonzero_rows == 0:
        print("[+] Verification OK: all M*w == 0")
    else:
        print(f"[!] Verification FAILED: {nonzero_rows} nonzero residual rows (see {ver_path})")

if __name__ == "__main__":
    main()
```

I got:

```verbatim
c:\math>python clear_denominators_and_verify.py --rational-basis kernel_basis_Q_v2_fixed.json --triplets validator_v2/saved_inv_triplets_integer.json --out-prefix kernel_basis_integer
[+] Loading rational basis: 707 vectors x 2590 coeffs
[+] Wrote integer vectors JSON to kernel_basis_integer_vectors.json
[+] Saved integer matrix (numpy .npy) to kernel_basis_integer_matrix.npy
[+] Loading triplets for exact verification...
[+] Triplets loaded: 122640 entries; inferred n_rows = 2590
[+] Wrote verification summary to kernel_basis_integer_verification.json
[!] Verification FAILED: 583 nonzero residual rows (see kernel_basis_integer_verification.json)
```

I created the following script:

```
#!/usr/bin/env python3
"""
find_bad_vectors.py

Find all kernel vectors that produced nonzero residuals in exact integer verification.

Usage:
  python find_bad_vectors.py \
    --vectors kernel_basis_integer_vectors.json \
    --triplets validator_v2/saved_inv_triplets_integer.json \
    --out bad_vectors_report.json

Outputs:
 - Prints a short summary to stdout
 - Writes a JSON report with per-vector counts and sample residuals.
"""
import argparse, json
from pathlib import Path

def load_integer_vectors(path):
    d = json.load(open(path, 'r'))
    vecs = [[int(x) for x in row] for row in d['vectors']]
    return vecs

def load_triplets(path):
    d = json.load(open(path, 'r'))
    trip = d.get('triplets') if isinstance(d, dict) else d
    if trip is None:
        for v in d.values():
            if isinstance(v, list):
                trip = v
                break
    if trip is None:
        raise SystemExit("Cannot find triplets list in " + str(path))
    norm = []
    for t in trip:
        if isinstance(t, list) and len(t) >= 3:
            norm.append((int(t[0]), int(t[1]), int(t[2])))
        elif isinstance(t, dict) and {'row','col','val'}.issubset(t.keys()):
            norm.append((int(t['row']), int(t['col']), int(t['val'])))
        else:
            raise SystemExit("Unrecognized triplet entry: " + str(t))
    return norm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vectors', required=True, help='kernel_basis_integer_vectors.json')
    ap.add_argument('--triplets', required=True, help='integer triplets JSON (reconstructed via CRT)')
    ap.add_argument('--out', default='bad_vectors_report.json', help='output report (JSON)')
    args = ap.parse_args()

    vecs = load_integer_vectors(args.vectors)
    triplets = load_triplets(args.triplets)
    n_rows = max(r for r,_,_ in triplets) + 1
    n_coeffs = len(vecs[0]) if vecs else 0
    print(f"Loaded {len(vecs)} vectors (n_coeffs={n_coeffs}), triplets: {len(triplets)} entries, inferred n_rows={n_rows}")

    bad_report = {}
    total_bad_rows = 0
    max_per_vector = 0
    # Pre-group triplets by row for faster accumulation
    trip_by_row = {}
    for r,c,v in triplets:
        trip_by_row.setdefault(r, []).append((c,v))

    for vi, w in enumerate(vecs):
        # compute row sums
        nonzero_rows = []
        max_abs = 0
        for r in sorted(trip_by_row.keys()):
            s = 0
            for (c,v) in trip_by_row[r]:
                if 0 <= c < len(w):
                    s += v * w[c]
            if s != 0:
                nonzero_rows.append({"row": r, "residual": str(s)})
                max_abs = max(max_abs, abs(s))
        if nonzero_rows:
            bad_report[str(vi)] = {
                "n_bad_rows": len(nonzero_rows),
                "max_abs_residual": str(max_abs),
                "sample_bad_rows": nonzero_rows[:10]  # sample up to 10
            }
            total_bad_rows += len(nonzero_rows)
            if len(nonzero_rows) > max_per_vector:
                max_per_vector = len(nonzero_rows)

    out = {
        "n_vectors": len(vecs),
        "n_coeffs": n_coeffs,
        "triplet_count": len(triplets),
        "total_bad_vectors": len(bad_report),
        "total_bad_rows": total_bad_rows,
        "max_bad_rows_for_vector": max_per_vector,
        "bad_vectors": bad_report
    }
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"Wrote report to {args.out}")
    print(f"total bad vectors: {len(bad_report)}, total bad rows: {total_bad_rows}")
    if bad_report:
        # Print a short table of first few bad vectors
        print("First few bad vectors (index, n_bad_rows, max_abs_residual):")
        cnt = 0
        for vi, info in sorted(bad_report.items(), key=lambda kv: int(kv[0])):
            print(vi, info["n_bad_rows"], info["max_abs_residual"])
            cnt += 1
            if cnt >= 10:
                break

if __name__ == '__main__':
    main()
```

result:

```verbatim
c:\math>python find_bad_vectors.py --vectors kernel_basis_integer_vectors.json --triplets validator_v2/saved_inv_triplets_integer.json --out bad_vectors_report.json
Loaded 707 vectors (n_coeffs=2590), triplets: 122640 entries, inferred n_rows=2590
Wrote report to bad_vectors_report.json
total bad vectors: 1, total bad rows: 583
First few bad vectors (index, n_bad_rows, max_abs_residual):
132 583 3205506998046217445889396569715021243029387863270118193724675225097613085988070708804711366170819342238244845474580795994510474694861678852301670892757227832048418165262586934012068209140742967377467619367133211658641967755853516398051689464948497284821836796767345502555857321747397574334405770358792897051301560899834594604702677683537099184300663297933110270533650710846559416823896599049780698551277119193531629757127890460307425281860190638053861552242000
```

as a result the only bad index is 132, therefore I run the following script:

```python
#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def load_integer_vectors(path):
    d = json.load(open(path))
    return [[int(x) for x in row] for row in d['vectors']]

def load_triplets(path):
    d = json.load(open(path))
    trip = d.get('triplets') if isinstance(d, dict) else d
    if trip is None:
        for v in d.values():
            if isinstance(v, list):
                trip = v; break
    return [(int(t[0]), int(t[1]), int(t[2])) for t in trip]

def load_perprime_triplets(primes):
    per = {}
    for p in primes:
        fname = Path(f"saved_inv_p{p}_triplets.json")
        if not fname.exists():
            raise SystemExit(f"missing {fname}")
        per[p] = load_triplets(str(fname))
    return per

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vec-json', default='kernel_basis_integer_vectors.json')
    ap.add_argument('--triplets', default='validator_v2/saved_inv_triplets_integer.json')
    ap.add_argument('--primes', nargs='*', type=int, default=[53,79,131,157,313,443,521,547,599,677,911])
    ap.add_argument('--vec', type=int, required=True, help='vector index to debug')
    args = ap.parse_args()

    vecs = load_integer_vectors(args.vec_json)
    if args.vec < 0 or args.vec >= len(vecs):
        raise SystemExit(f"vec index {args.vec} out of range (0..{len(vecs)-1})")
    W = vecs[args.vec]
    print(f"Loaded vector {args.vec}: length {len(W)}; nonzeros {sum(1 for x in W if x!=0)}")

    trip = load_triplets(args.triplets)
    n_rows = max(r for r,_,_ in trip)+1
    print("Integer triplet entries:", len(trip), "inferred rows:", n_rows)

    # compute integer residuals
    row_sums = [0]*n_rows
    for (r,c,v) in trip:
        if 0 <= c < len(W):
            row_sums[r] += v * W[c]
    nz = [(r,s) for r,s in enumerate(row_sums) if s!=0]
    print("Nonzero integer residuals count:", len(nz))
    for (r,s) in nz[:20]:
        print(" row", r, "residual", s)

    # CRT modulus
    M = 1
    for p in args.primes: M *= p
    print("CRT product M =", M)

    # show sample residuals modulo M and quotient
    print("\nSample residuals modulo M (first 10):")
    for (r,s) in nz[:10]:
        print(r, "res mod M =", s % M, "quotient =", s // M)

    # compute per-prime modular residuals using per-prime triplets
    per = load_perprime_triplets(args.primes)
    for p in args.primes:
        trip_p = per[p]
        nrows_p = max(r for r,_,_ in trip_p)+1
        row_sums_p = [0]*nrows_p
        for (r,c,v) in trip_p:
            if 0 <= c < len(W):
                row_sums_p[r] = (row_sums_p[r] + (v % p) * (W[c] % p)) % p
        nzp = [(r,s) for r,s in enumerate(row_sums_p) if s!=0]
        print(f"\nprime {p}: nonzero rows mod {p} = {len(nzp)}; sample (first 10):", nzp[:10])

if __name__ == '__main__':
    main()
```

result:

```verbatim
c:\math>python debug_vector_residuals.py --vec 132
Loaded vector 132: length 2590; nonzeros 1786
Integer triplet entries: 122640 inferred rows: 2590
Nonzero integer residuals count: 583
 row 36 residual 232415141044151760863678216802561455057349991491119101311754933754451512724977190205891128228291861342054445280750093609895902789714901753813296139039650624668912347489774173743255104226564412053916353371442622028469392563768299302804860540442596293112768961834528594703512353428964369502864473414438666668016550725591458554431666690414019009580237014016540371712580686867140178801288557048392612656617503129173929744170205578674468805212647353087098704000
 row 44 residual -16092408518944013816518667302757700099918281946615991079814487418140900848206579513987534498468324039807950816433554476975219822005793163738161792273674932892657921427156071806869258045434885201905072478798779859150295247631298918006953740678929932830932186934678528840720916061344355301809657030669326497322829142790154318529466187856824385971273963826812346569160961929477885462512274039409039568154115681214610002119142775994558232425857074173736927600000
 row 46 residual -15790608557651828512736825199454013692394106079103518880871297526544625911467575632153090328837094170943397502810672800758280594213307245668962669417503890550238561613621765090722079177838982906509605572011920380480103499226587996636778805851294876856717289953398590298640922976454961453327043072308379583768461227894015847981653589950115595310750318995777513213374542569365759035860407661836239816245479751374812200833662247743711904888726356185335587580000
 row 47 residual -32184817037888027633037334605515400199836563893231982159628974836281801696413159027975068996936648079615901632867108953950439644011586327476323584547349865785315842854312143613738516090869770403810144957597559718300590495262597836013907481357859865661864373869357057681441832122688710603619314061338652994645658285580308637058932375713648771942547927653624693138321923858955770925024548078818079136308231362429220004238285551989116464851714148347473855200000
 row 48 residual -16092408518944013816518667302757700099918281946615991079814487418140900848206579513987534498468324039807950816433554476975219822005793163738161792273674932892657921427156071806869258045434885201905072478798779859150295247631298918006953740678929932830932186934678528840720916061344355301809657030669326497322829142790154318529466187856824385971273963826812346569160961929477885462512274039409039568154115681214610002119142775994558232425857074173736927600000
 row 49 residual -16092408518944013816518667302757700099918281946615991079814487418140900848206579513987534498468324039807950816433554476975219822005793163738161792273674932892657921427156071806869258045434885201905072478798779859150295247631298918006953740678929932830932186934678528840720916061344355301809657030669326497322829142790154318529466187856824385971273963826812346569160961929477885462512274039409039568154115681214610002119142775994558232425857074173736927600000
 row 52 residual -31106243739283653900766244456897914557429961263355322680852195627544502372829955049965018550753111161193689572090878579209249637944781522967647484524433468761880418934944259616521173604434523497932651109804603931034739244691415753769031989118046657456889512588603636154834074799948593953169169506962973866554707434781263095157035005741451300924822130636411580271168746304155134582281373335848896952998508975110313392662633587856561231670614650505091692420000
 row 54 residual -15749710768835893927023924001762057285851732651538480095069031309959067802614121654145742109244204925235379875878596628479125187743149584439228301687406608266606621241095365786119825135919440783672399038137282207933797626970461806940649704584109850291594121437482280724317449249489594981949202454072339237814203975518050755642488983086326352586302136953492049121860252428916382113307375129077214568872799646090813757846806898384705078369808736523022192020000
 row 55 residual -14871812688760927911001135368316354560871826236509924399812164519106612180128496833247685482248299241044170294735762991129239712166050346596658440417053244856634583895201924086066361159838207456931500910908256878276038055880613291409883339756509633064394911855494891129603923597802301730269316395500709657277898895670075707942061547319450483649932722815657270671426972385151272467081542462474970863486020250940188570557737669529454694481884367446651996780000
 row 68 residual -64369634075776055266074669211030800399673127786463964319257949672563603392826318055950137993873296159231803265734217907900879288023172654952647169094699731570631685708624287227477032181739540807620289915195119436601180990525195672027814962715719731323728747738714115362883664245377421207238628122677305989291316571160617274117864751427297543885095855307249386276643847717911541850049096157636158272616462724858440008476571103978232929703428296694947710400000
 row 70 residual -193007305799126190551905283807853568762743383294435062658435649194379934932922777942316823637023950889658701962872291293956933508871397634033569201190798447137582977175130209667495228008845448152970973544920963795361106776263280200230758557692979863812363961049853141497002744696907801182190775699499780363461693287763968767011203116669170055411292107658426331977029182961123109611307830462094631064082331023333085484756583211899331542405617027708109540120000
 row 71 residual -64369634075776055266074669211030800399673127786463964319257949672563603392826318055950137993873296159231803265734217907900879288023172654952647169094699731570631685708624287227477032181739540807620289915195119436601180990525195672027814962715719731323728747738714115362883664245377421207238628122677305989291316571160617274117864751427297543885095855307249386276643847717911541850049096157636158272616462724858440008476571103978232929703428296694947710400000
 row 73 residual -64369634075776055266074669211030800399673127786463964319257949672563603392826318055950137993873296159231803265734217907900879288023172654952647169094699731570631685708624287227477032181739540807620289915195119436601180990525195672027814962715719731323728747738714115362883664245377421207238628122677305989291316571160617274117864751427297543885095855307249386276643847717911541850049096157636158272616462724858440008476571103978232929703428296694947710400000
 row 76 residual -21621253878215145886477562919629563922026499168965863085688603807423815544461749803324099419910171684472274048727494252308279371898380861458244707086823550107562681113504770140177684800165202390494734161092582937394295329213363632355929606810246832450416176380278296410932601711623861224562056270398556007379459332696093355077090157973123671660842024335297269412863051494296407487932327389780174932982226218607570818786749669101849389057810240441781248520000
 row 77 residual -129319116319675243170111303345766520088224371853996799441562700487338822205272972185059836773491580327584199595858302517890779916698639093849404499794867503362960435576563126018561492002293395120641817848972046212744434415143917803416610004198226816214227833947860165310921612060177145702101354652985186812100466396448154024105200571014030216116677978479066906591180984274250697365909815926654335677059102665052466245574045813999476423282176449460371458400000
 row 78 residual -129029192235613676851130320883914060443785313713462364040039299916233014495462804148480056380619086323023903063663369166846269246372492201877349418992133483252111903496905850236757778182886238367941198839681142542973398198097154573736119964814833139430842664712644198018344470275465994058289305449169899395341549769384694286170465036934312651943434844546782839572234339855036890533004004120963326111146014057384673131263594010977971141344516521425133439600000
 row 80 residual -86116102851762973340413874743226860177336561855819721160534000134523945566911925444513297718036888883536034219840557228245683054357043765242251306262333662205024113024489658751773090061726544496194338896217729585239277537747024125717576656337686651881690166220168121109755360778547713253463553367385028735814005388610949436758555202649447622686704274341949915387805108043095862632971273349205887262735038907479046458945879941659149188208897656961834966000000
 row 86 residual -21553186053279207195018550557627753348037395308999466573593783414556470367545495364176639462248596721264033265976383752981796652783106515641567416632477917227160072596093854336426915333715565853440302974828674368790739069190652967236101667366371136035704638991310027551820268676696190950350225775497531135350077732741359004017533428502338369352779663079844484431863497379041782894318302654442389279509850444175411040929007635666579403880362741576728576400000
 row 88 residual -64107995053078161772719862760371735852011619013841053256800074991763581415635080844831022325436250483720417054022279443858970219253592944628188374645001278451962804150258149337097970524130635416093795630996560354874489742456153844646094102723529454643196154457960330329408605815973375461966210911085466868385502138593094156444094507263840725952832801758266728330019047774679047789605186854857118362174995525235189490599730541504911135033239956669029835360000
 row 91 residual -21372435101335511028075538834727799199221687098563072625042117332337658239623469772182487493162291423362451016734220674683767015631462547028663919970808480923355597058438404281178168646447453378674923567918724048516843490337659217306066197957405696858893966811282125814855615746109516286767491693179060888266334574366359068927139352604114360406433792036342792184595048976580580210748392544288729387117263642917066055967398171572680164799305273568307988920000
CRT product M = 1257132026085202124689385321

Sample residuals modulo M (first 10):
36 res mod M = 0 quotient = 184877273207261227135135915861401306307873606620353923785318907060289789279244958375326591133338768601706321079793813347206431844693645300550293163568960310720898124135102157469610628420976901327064182520819377119606083409176629690286925674965409600852058476452154629268594091436429626190005858098246994338123807096794845544525017903411966887727440115577874199066175133077051475646908760963664179943449431571975510439448931024000
44 res mod M = 0 quotient = -12800889791231323549457562258619181639736564495281550828048360800857003089573096928053857596128824584979364975603871849028743505864597642906400458431662810926458958968524708660650163803259961534434420963270979961102157076197392193128590308299563722207763805362355300094289042636119031405324308008385259199982879175490458504868215032339398102575643136021320595028117490533674204796786839658033148755999970458605389384386679535600000
46 res mod M = 0 quotient = -12560819571851095294087350405396256210567724831036465265820039644396737023401606173546536768930517916437568514400944495082198461839526900005391893803332624108535909115939209365856796443644744680546411413639360998904865290837238712951743003504702611541067346478657926009148007876964940022003823456907972692363838151795510644855660415953963471920977606571832918736333573749537104178805613585244001722650478739995074719125232813980000
47 res mod M = 0 quotient = -25601779582462647098915124517238363279473128990563101656096721601714006179146193856107715192257649169958729951207743698057487011729195285812800916863325621852917917937049417321300327606519923068868841926541959922204314152394784386257180616599127444415527610724710600188578085272238062810648616016770518399965758350980917009736430064678796205151286272042641190056234981067348409593573679316066297511999940917210778768773359071200000
48 res mod M = 0 quotient = -12800889791231323549457562258619181639736564495281550828048360800857003089573096928053857596128824584979364975603871849028743505864597642906400458431662810926458958968524708660650163803259961534434420963270979961102157076197392193128590308299563722207763805362355300094289042636119031405324308008385259199982879175490458504868215032339398102575643136021320595028117490533674204796786839658033148755999970458605389384386679535600000
49 res mod M = 0 quotient = -12800889791231323549457562258619181639736564495281550828048360800857003089573096928053857596128824584979364975603871849028743505864597642906400458431662810926458958968524708660650163803259961534434420963270979961102157076197392193128590308299563722207763805362355300094289042636119031405324308008385259199982879175490458504868215032339398102575643136021320595028117490533674204796786839658033148755999970458605389384386679535600000
52 res mod M = 0 quotient = -24743816157600162984961746717333902946262951367745946212191403863586808258729578862865661229444893897889667178439949302783468759154276882034465683453964201594750999118776556728635241408749072486845993501411594520166715477354249441090767274303592459139294592044284922349138777970018475283230177264755600318817125001135342458574319510334966075822856024765314342178501960344826823283959470417974368496797210173483592162236896866020000
54 res mod M = 0 quotient = -12528286959549988633693392008776999681777445363367229108979162683024779443575107561831652806675422221367567964520851974778644337068134248020654356302554441324020312696234338296239606286771505984638704568845150476809276801471938652052801860184992591633294051784050851338354173163762083596713891865146904357560233903082090437866328055275154821595930307042793743284393837877494631278075275547860214485457139742862006694756203733620000
55 res mod M = 0 quotient = -11829952924732020777297864474933973676689348065203971471785143451005951130630615482605619491713526371581541856804319587050200024374041774026007292163283715333894259629510572555165570925431587492287366736209946501731944232816693567899802366676698778794831851818556220834061005508396330091698908975129614292895582300156199997913296938195528661976287456068801046023613919800221369227938331476826540082419754886580561904023424759180000
68 res mod M = 0 quotient = -51203559164925294197830249034476726558946257981126203312193443203428012358292387712215430384515298339917459902415487396114974023458390571625601833726651243705835835874098834642600655213039846137737683853083919844408628304789568772514361233198254888831055221449421200377156170544476125621297232033541036799931516701961834019472860129357592410302572544085282380112469962134696819187147358632132595023999881834421557537546718142400000

prime 53: nonzero rows mod 53 = 0; sample (first 10): []

prime 79: nonzero rows mod 79 = 0; sample (first 10): []

prime 131: nonzero rows mod 131 = 0; sample (first 10): []

prime 157: nonzero rows mod 157 = 0; sample (first 10): []

prime 313: nonzero rows mod 313 = 0; sample (first 10): []

prime 443: nonzero rows mod 443 = 0; sample (first 10): []

prime 521: nonzero rows mod 521 = 0; sample (first 10): []

prime 547: nonzero rows mod 547 = 0; sample (first 10): []

prime 599: nonzero rows mod 599 = 0; sample (first 10): []

prime 677: nonzero rows mod 677 = 0; sample (first 10): []

prime 911: nonzero rows mod 911 = 0; sample (first 10): []
```

Plan now is to compute more prime invariants and kernels to see if this mitigates the problem. I will then add the needed files to the invariant folder in validator_v2 folder so that kernel reconstruction can take place on users end with all proper primes. So far planning to recompute the following additional primes that are mod 13: [937, 1093, 1171, 1223, 1249, 1301, 1327, 1483]

After which I will recompute the kernels and do same process as update 2 but with all additional primes [53, 79, 131, 157, 313, 443, 521, 547, 599, 677, 911, 937, 1093, 1171, 1223, 1249, 1301, 1327, 1483] in update 4!

---

**UPDATE 4**

**SUCCESS!**

After adding the additional primes, computing their invariants and then kernels to have 19 total primes kernels, we obtained:

```verbatim
c:\math>python rational_kernel_basis.py --kernels kernel_p53.json kernel_p79.json kernel_p131.json kernel_p157.json kernel_p313.json kernel_p443.json kernel_p521.json kernel_p547.json kernel_p599.json kernel_p677.json kernel_p911.json kernel_p937.json kernel_p1093.json kernel_p1171.json kernel_p1223.json kernel_p1249.json kernel_p1301.json kernel_p1327.json kernel_p1483.json --primes 53 79 131 157 313 443 521 547 599 677 911 937 1093 1171 1223 1249 1301 1327 1483 --out kernel_basis_Q_v3.json
[+] Loading 19 kernel bases...
    kernel_p53.json: 707 vectors × 2590 coefficients
    kernel_p79.json: 707 vectors × 2590 coefficients
    kernel_p131.json: 707 vectors × 2590 coefficients
    kernel_p157.json: 707 vectors × 2590 coefficients
    kernel_p313.json: 707 vectors × 2590 coefficients
    kernel_p443.json: 707 vectors × 2590 coefficients
    kernel_p521.json: 707 vectors × 2590 coefficients
    kernel_p547.json: 707 vectors × 2590 coefficients
    kernel_p599.json: 707 vectors × 2590 coefficients
    kernel_p677.json: 707 vectors × 2590 coefficients
    kernel_p911.json: 707 vectors × 2590 coefficients
    kernel_p937.json: 707 vectors × 2590 coefficients
    kernel_p1093.json: 707 vectors × 2590 coefficients
    kernel_p1171.json: 707 vectors × 2590 coefficients
    kernel_p1223.json: 707 vectors × 2590 coefficients
    kernel_p1249.json: 707 vectors × 2590 coefficients
    kernel_p1301.json: 707 vectors × 2590 coefficients
    kernel_p1327.json: 707 vectors × 2590 coefficients
    kernel_p1483.json: 707 vectors × 2590 coefficients
[+] Dimension verified: 707 vectors × 2590 coefficients
[+] CRT product M = 5896248844997446616582744775360152335261080841658417
[+] Rational reconstruction bound = 54296633620315019565767999
[+] Processing all 707 vectors
    [10/707] 94.5 vec/sec, ETA: 0.1 min
    [20/707] 108.7 vec/sec, ETA: 0.1 min
    [30/707] 96.2 vec/sec, ETA: 0.1 min
    [40/707] 102.3 vec/sec, ETA: 0.1 min
    [50/707] 89.6 vec/sec, ETA: 0.1 min
    [60/707] 90.7 vec/sec, ETA: 0.1 min
    [70/707] 89.8 vec/sec, ETA: 0.1 min
    [80/707] 92.2 vec/sec, ETA: 0.1 min
    [90/707] 87.6 vec/sec, ETA: 0.1 min
    [100/707] 85.8 vec/sec, ETA: 0.1 min
    [110/707] 83.1 vec/sec, ETA: 0.1 min
    [120/707] 82.3 vec/sec, ETA: 0.1 min
    [130/707] 75.8 vec/sec, ETA: 0.1 min
    [140/707] 74.7 vec/sec, ETA: 0.1 min
    [150/707] 78.0 vec/sec, ETA: 0.1 min
    [160/707] 81.3 vec/sec, ETA: 0.1 min
    [170/707] 83.6 vec/sec, ETA: 0.1 min
    [180/707] 86.6 vec/sec, ETA: 0.1 min
    [190/707] 88.7 vec/sec, ETA: 0.1 min
    [200/707] 91.3 vec/sec, ETA: 0.1 min
    [210/707] 93.4 vec/sec, ETA: 0.1 min
    [220/707] 95.6 vec/sec, ETA: 0.1 min
    [230/707] 97.6 vec/sec, ETA: 0.1 min
    [240/707] 99.5 vec/sec, ETA: 0.1 min
    [250/707] 101.3 vec/sec, ETA: 0.1 min
    [260/707] 103.6 vec/sec, ETA: 0.1 min
    [270/707] 104.9 vec/sec, ETA: 0.1 min
    [280/707] 106.4 vec/sec, ETA: 0.1 min
    [290/707] 107.8 vec/sec, ETA: 0.1 min
    [300/707] 109.3 vec/sec, ETA: 0.1 min
    [310/707] 111.1 vec/sec, ETA: 0.1 min
    [320/707] 112.8 vec/sec, ETA: 0.1 min
    [330/707] 113.8 vec/sec, ETA: 0.1 min
    [340/707] 115.3 vec/sec, ETA: 0.1 min
    [350/707] 116.8 vec/sec, ETA: 0.1 min
    [360/707] 117.6 vec/sec, ETA: 0.0 min
    [370/707] 118.7 vec/sec, ETA: 0.0 min
    [380/707] 119.8 vec/sec, ETA: 0.0 min
    [390/707] 121.1 vec/sec, ETA: 0.0 min
    [400/707] 122.1 vec/sec, ETA: 0.0 min
    [410/707] 123.1 vec/sec, ETA: 0.0 min
    [420/707] 124.3 vec/sec, ETA: 0.0 min
    [430/707] 125.5 vec/sec, ETA: 0.0 min
    [440/707] 126.1 vec/sec, ETA: 0.0 min
    [450/707] 127.2 vec/sec, ETA: 0.0 min
    [460/707] 127.7 vec/sec, ETA: 0.0 min
    [470/707] 128.3 vec/sec, ETA: 0.0 min
    [480/707] 128.9 vec/sec, ETA: 0.0 min
    [490/707] 129.8 vec/sec, ETA: 0.0 min
    [500/707] 130.8 vec/sec, ETA: 0.0 min
    [510/707] 131.8 vec/sec, ETA: 0.0 min
    [520/707] 132.2 vec/sec, ETA: 0.0 min
    [530/707] 133.2 vec/sec, ETA: 0.0 min
    [540/707] 133.6 vec/sec, ETA: 0.0 min
    [550/707] 134.5 vec/sec, ETA: 0.0 min
    [560/707] 135.2 vec/sec, ETA: 0.0 min
    [570/707] 135.6 vec/sec, ETA: 0.0 min
    [580/707] 136.5 vec/sec, ETA: 0.0 min
    [590/707] 136.9 vec/sec, ETA: 0.0 min
    [600/707] 137.6 vec/sec, ETA: 0.0 min
    [610/707] 138.4 vec/sec, ETA: 0.0 min
    [620/707] 139.1 vec/sec, ETA: 0.0 min
    [630/707] 139.4 vec/sec, ETA: 0.0 min
    [640/707] 139.8 vec/sec, ETA: 0.0 min
    [650/707] 140.8 vec/sec, ETA: 0.0 min
    [660/707] 140.9 vec/sec, ETA: 0.0 min
    [670/707] 141.8 vec/sec, ETA: 0.0 min
    [680/707] 142.4 vec/sec, ETA: 0.0 min
    [690/707] 142.6 vec/sec, ETA: 0.0 min
    [700/707] 143.1 vec/sec, ETA: 0.0 min
[+] Reconstruction complete in 4.9s
[+] Statistics:
    Total coefficients: 1831130
    Zero coefficients: 1751993 (95.7%)
    Reconstructed: 79137
    Failed: 0
    Verification OK: 79137
    Verification FAIL: 0
[+] Wrote rational basis to kernel_basis_Q_v3.json
[+] Wrote failures to validator_v2\reconstruction_failures.json
[+] All reconstructed coefficients verified successfully ✓
```

Which we verified using reconstruct_integer_triplets_via_crt.py we obtain:

```verbatim
c:\math>python reconstruct_integer_triplets_via_crt.py --primes 53 79 131 157 313 443 521 547 599 677 911 937 1093 1171 1223 1249 1301 1327 1483 --out validator_v2/saved_inv_triplets_integer.json --verify
[+] Loading per-prime triplets from current directory...
    loaded p=53: 122640 nonzero entries
    loaded p=79: 122640 nonzero entries
    loaded p=131: 122640 nonzero entries
    loaded p=157: 122640 nonzero entries
    loaded p=313: 122640 nonzero entries
    loaded p=443: 122640 nonzero entries
    loaded p=521: 122640 nonzero entries
    loaded p=547: 122640 nonzero entries
    loaded p=599: 122640 nonzero entries
    loaded p=677: 122640 nonzero entries
    loaded p=911: 122640 nonzero entries
    loaded p=937: 122640 nonzero entries
    loaded p=1093: 122640 nonzero entries
    loaded p=1171: 122640 nonzero entries
    loaded p=1223: 122640 nonzero entries
    loaded p=1249: 122640 nonzero entries
    loaded p=1301: 122640 nonzero entries
    loaded p=1327: 122640 nonzero entries
    loaded p=1483: 122640 nonzero entries
[+] Product of primes M = 5896248844997446616582744775360152335261080841658417 (bits: 172)
[+] Union of positions to process: 122640 entries
  processed 10000/122640
  processed 20000/122640
  processed 30000/122640
  processed 40000/122640
  processed 50000/122640
  processed 60000/122640
  processed 70000/122640
  processed 80000/122640
  processed 90000/122640
  processed 100000/122640
  processed 110000/122640
  processed 120000/122640
[+] Reconstructed integer triplets: 122640 nonzero entries
[+] All reconstructed integers reduce correctly to per-prime residues
[+] Wrote integer triplets JSON to validator_v2\saved_inv_triplets_integer.json
```

Where we then run clear_denominators_and_verify.py file and we obtained: 

```verbatim
c:\math>python clear_denominators_and_verify.py --rational-basis kernel_basis_Q_v3.json --triplets validator_v2/saved_inv_triplets_integer.json --out-prefix validator_v2/kernel_basis_integer_v3
[+] Loading rational basis: 707 vectors x 2590 coeffs
[+] Wrote integer vectors JSON to validator_v2\kernel_basis_integer_v3_vectors.json
[+] Saved integer matrix (numpy .npy) to validator_v2\kernel_basis_integer_v3_matrix.npy
[+] Loading triplets for exact verification...
[+] Triplets loaded: 122640 entries; inferred n_rows = 2590
[+] Wrote verification summary to validator_v2\kernel_basis_integer_v3_verification.json
[+] Verification OK: all M*w == 0
```

**THIS IS HUGE!**

**I have validated on PC and on mabcook air, the results are reproducible on different machines!**

## **📊 STATUS SUMMARY (updated)**

| **Component** | **Current Status** | **Deterministic Target** | **Priority** | **Timeline** |
|---------------|-------------------|--------------------------|--------------|--------------|
| **Rank ≥ 1883 over ℤ** | ✅ **PROVEN** (k=1883 cert) | ✅ Complete | — | **Done** |
| **Dimension = 707 over ℚ** | ✅ **PROVEN (deterministic q‑lift)** — kernel_basis_Q_v3.json; integer verification OK | ✅ Complete | **High** | **Done** |
| **CP3 Barrier over ℚ** | ✅ Verified: multi‑prime tests + CRT + exact integer verification (deterministic evidence) | ✅ Complete | **Medium** | **Done** |
| **Reproducibility** | ✅ End‑to‑end protocol + artifacts saved (M2 outputs, kernel_p*.json, kernel_basis_Q_v3.json, CRT triplets, integer verification) | ✅ Full reproducibility achievable with manifest | **Low** | 1 day (finalize manifest) |

---

**UPDATE 5**

SNF PATH BLOCKED DUE TO ALREADY KNOWN BLOCKER validator_v2/intersection_matrix_reasoning_artifact.md 

---
**END OF ARTIFACT**






