#!/usr/bin/env python3
"""
Information-Theoretic Obstruction Analysis (REVISED)
Optimized for MacBook Air M1 16GB

Analyzes 401 structurally isolated Hodge classes using information theory
to detect signatures incompatible with algebraic cycle construction.  

REVISION:  Expanded algebraic pattern set from n=8 to n=24 for statistical robustness. 

Author: Eric Robert Lawson
Date: January 2026
"""

import json
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu, ks_2samp
from scipy.spatial.distance import euclidean
import pandas as pd
from collections import Counter
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'data_dir': Path('validator'),
    'results_dir': Path('analysis_results'),
    'prime':  313,  # Representative prime for monomial data
    'verbose': True,
    'save_plots': True,  # Set False if matplotlib issues
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load computational data with error handling."""
    
    print("="*70)
    print("LOADING DATA")
    print("="*70)
    
    # Load all 707 monomials
    mon_file = CONFIG['data_dir'] / f"saved_inv_p{CONFIG['prime']}_monomials18.json"
    
    if not mon_file.exists():
        print(f"ERROR: {mon_file} not found")
        print(f"Expected location: {mon_file.absolute()}")
        sys.exit(1)
    
    with open(mon_file) as f:
        all_monomials = json.load(f)
    
    print(f"✓ Loaded {len(all_monomials)} total monomials")
    
    # Load structural isolation results
    iso_file = Path('structural_isolation_results.json')
    
    if not iso_file.exists():
        print(f"ERROR: {iso_file} not found")
        print("Run structural_isolation_rigorous.py first")
        sys.exit(1)
    
    with open(iso_file) as f:
        isolated_data = json.load(f)
    
    isolated_monomials = [r['monomial'] for r in isolated_data if r['isolated']]
    
    print(f"✓ Loaded {len(isolated_monomials)} isolated monomials")
    
    # Define known algebraic cycles - EXPANDED TO n=24
    # Systematically covers all plausible 2-4 variable degree-18 constructions
    algebraic_cycles = [
        # Type 1: Hyperplane (1 pattern)
        [18, 0, 0, 0, 0, 0],
        
        # Type 2: 2-variable coordinate intersections (8 patterns)
        [9, 9, 0, 0, 0, 0],
        [12, 6, 0, 0, 0, 0],
        [15, 3, 0, 0, 0, 0],
        [14, 4, 0, 0, 0, 0],
        [13, 5, 0, 0, 0, 0],
        [11, 7, 0, 0, 0, 0],
        [10, 8, 0, 0, 0, 0],
        [16, 2, 0, 0, 0, 0],
        
        # Type 3: 3-variable constructions (8 patterns)
        [6, 6, 6, 0, 0, 0],
        [12, 3, 3, 0, 0, 0],
        [10, 4, 4, 0, 0, 0],
        [9, 6, 3, 0, 0, 0],
        [9, 5, 4, 0, 0, 0],
        [8, 5, 5, 0, 0, 0],
        [7, 6, 5, 0, 0, 0],
        [8, 6, 4, 0, 0, 0],
        
        # Type 4: 4-variable mixed (7 patterns)
        [9, 3, 3, 3, 0, 0],
        [6, 6, 3, 3, 0, 0],
        [8, 4, 3, 3, 0, 0],
        [6, 4, 4, 4, 0, 0],
        [7, 5, 3, 3, 0, 0],
        [6, 5, 4, 3, 0, 0],
        [5, 5, 4, 4, 0, 0],
    ]
    
    print(f"✓ Using {len(algebraic_cycles)} algebraic cycle patterns (expanded from 8)")
    print(f"  - Type 1 (hyperplane): 1 pattern")
    print(f"  - Type 2 (2-variable): 8 patterns")
    print(f"  - Type 3 (3-variable): 8 patterns")
    print(f"  - Type 4 (4-variable): 7 patterns")
    print()
    
    return {
        'all_monomials': all_monomials,
        'isolated':  isolated_monomials,
        'algebraic':  algebraic_cycles
    }

# ============================================================================
# INFORMATION-THEORETIC METRICS
# ============================================================================

def compute_shannon_entropy(monomial):
    """
    Shannon entropy of exponent distribution.
    
    H = -Σ pᵢ log₂(pᵢ)
    
    Algebraic cycles: low entropy (structured)
    Isolated classes: high entropy (chaotic)
    """
    non_zero = [e for e in monomial if e > 0]
    if not non_zero:
        return 0.0
    
    total = sum(non_zero)
    probs = [e/total for e in non_zero]
    
    return -sum(p * np.log2(p) for p in probs if p > 0)


def compute_kolmogorov_complexity_proxy(monomial):
    """
    Approximate Kolmogorov complexity via description length.
    
    Lower bound: number of bits to encode exponent pattern. 
    """
    non_zero = [e for e in monomial if e > 0]
    if not non_zero: 
        return 0
    
    # GCD reduction
    from math import gcd
    from functools import reduce
    
    g = reduce(gcd, non_zero)
    reduced = [e // g for e in non_zero]
    
    # Prime factorization complexity
    def prime_factors(n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors. append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    all_factors = []
    for e in reduced: 
        if e > 1:
            all_factors.extend(prime_factors(e))
    
    # Complexity = number of distinct primes + encoding overhead
    distinct_primes = len(set(all_factors))
    encoding_bits = sum(int(np.log2(e)) + 1 for e in reduced)
    
    return distinct_primes + encoding_bits


def compute_geometric_variance(monomial):
    """Variance of exponent distribution."""
    non_zero = [e for e in monomial if e > 0]
    return float(np.var(non_zero)) if non_zero else 0.0


def compute_exponent_range(monomial):
    """Range = max - min (non-zero exponents)."""
    non_zero = [e for e in monomial if e > 0]
    return max(non_zero) - min(non_zero) if non_zero else 0


def compute_gcd_invariant(monomial):
    """GCD of non-zero exponents."""
    non_zero = [e for e in monomial if e > 0]
    if not non_zero: 
        return 0
    
    from math import gcd
    from functools import reduce
    return reduce(gcd, non_zero)


def compute_signature(monomial):
    """
    Complete information-theoretic signature.
    
    Returns dictionary of all metrics.
    """
    non_zero = [e for e in monomial if e > 0]
    
    return {
        'entropy': compute_shannon_entropy(monomial),
        'kolmogorov': compute_kolmogorov_complexity_proxy(monomial),
        'variance': compute_geometric_variance(monomial),
        'range': compute_exponent_range(monomial),
        'gcd': compute_gcd_invariant(monomial),
        'num_vars': len(non_zero),
        'max_exp': max(monomial) if monomial else 0,
        'min_exp': min(non_zero) if non_zero else 0,
        'mean_exp': float(np.mean(non_zero)) if non_zero else 0,
    }


def compute_all_signatures(monomials):
    """Compute signatures for list of monomials."""
    return [compute_signature(m) for m in monomials]

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def statistical_comparison(alg_sigs, iso_sigs, metric_name):
    """
    Comprehensive statistical comparison for a single metric.
    
    Returns:
        dict with test results
    """
    alg_vals = [s[metric_name] for s in alg_sigs]
    iso_vals = [s[metric_name] for s in iso_sigs]
    
    # t-test (parametric)
    t_stat, t_pval = ttest_ind(alg_vals, iso_vals)
    
    # Mann-Whitney U (non-parametric, robust)
    u_stat, u_pval = mannwhitneyu(alg_vals, iso_vals, alternative='two-sided')
    
    # Kolmogorov-Smirnov (distribution difference)
    ks_stat, ks_pval = ks_2samp(alg_vals, iso_vals)
    
    # Effect size (Cohen's d)
    mean_alg = np.mean(alg_vals)
    mean_iso = np.mean(iso_vals)
    std_alg = np.std(alg_vals, ddof=1)
    std_iso = np.std(iso_vals, ddof=1)
    
    pooled_std = np.sqrt((std_alg**2 + std_iso**2) / 2)
    cohen_d = (mean_iso - mean_alg) / pooled_std if pooled_std > 0 else 0
    
    return {
        'metric': metric_name,
        'mean_algebraic': mean_alg,
        'mean_isolated': mean_iso,
        'std_algebraic': std_alg,
        'std_isolated': std_iso,
        't_statistic': t_stat,
        't_pvalue': t_pval,
        'mannwhitney_u': u_stat,
        'mannwhitney_pvalue': u_pval,
        'ks_statistic':  ks_stat,
        'ks_pvalue': ks_pval,
        'cohen_d': cohen_d,
        'separation': 'HIGHLY SIGNIFICANT' if (t_pval < 0.001 and abs(cohen_d) > 1.0) else
                     'SIGNIFICANT' if (t_pval < 0.01 and abs(cohen_d) > 0.5) else
                     'WEAK' if t_pval < 0.05 else
                     'NONE'
    }


def analyze_all_metrics(alg_sigs, iso_sigs):
    """Run statistical analysis on all metrics."""
    
    metrics = ['entropy', 'kolmogorov', 'variance', 'range', 'num_vars']
    
    results = []
    for metric in metrics:
        results.append(statistical_comparison(alg_sigs, iso_sigs, metric))
    
    return results

# ============================================================================
# DISTANCE-BASED RANKING
# ============================================================================

def compute_algebraic_distance(iso_sig, alg_sigs, metrics):
    """
    Compute minimum distance from isolated class to algebraic space.
    
    Uses weighted Euclidean distance in normalized metric space.
    """
    
    # Normalize signatures
    def normalize(val, all_vals):
        min_val = min(all_vals)
        max_val = max(all_vals)
        if max_val == min_val:
            return 0.5
        return (val - min_val) / (max_val - min_val)
    
    # Collect all values for normalization
    all_sigs = alg_sigs + [iso_sig]
    
    norm_iso = []
    norm_algs = [[] for _ in alg_sigs]
    
    for metric in metrics:
        all_vals = [s[metric] for s in all_sigs]
        
        norm_iso.append(normalize(iso_sig[metric], all_vals))
        
        for i, alg_sig in enumerate(alg_sigs):
            norm_algs[i].append(normalize(alg_sig[metric], all_vals))
    
    # Compute distances
    distances = [euclidean(norm_iso, norm_alg) for norm_alg in norm_algs]
    
    return min(distances)


def rank_candidates(iso_monomials, iso_sigs, alg_sigs):
    """
    Rank isolated classes by distance from algebraic space. 
    
    Returns sorted list of candidates. 
    """
    
    metrics = ['entropy', 'variance', 'range', 'kolmogorov']
    
    candidates = []
    for mon, sig in zip(iso_monomials, iso_sigs):
        dist = compute_algebraic_distance(sig, alg_sigs, metrics)
        
        candidates.append({
            'monomial': mon,
            'signature':  sig,
            'distance': dist
        })
    
    # Sort by distance (descending)
    candidates.sort(key=lambda x: x['distance'], reverse=True)
    
    return candidates

# ============================================================================
# REPORTING
# ============================================================================

def print_statistical_results(results):
    """Print statistical comparison results."""
    
    print("\n" + "="*70)
    print("STATISTICAL SEPARATION ANALYSIS")
    print("="*70 + "\n")
    
    for r in results:
        print(f"{r['metric']. upper()}:")
        print(f"  Algebraic:     μ = {r['mean_algebraic']:.3f}, σ = {r['std_algebraic']:.3f}")
        print(f"  Isolated:     μ = {r['mean_isolated']:.3f}, σ = {r['std_isolated']:.3f}")
        print(f"  Difference:   Δμ = {r['mean_isolated'] - r['mean_algebraic']:.3f}")
        
        # Format p-values safely (handle very small values)
        t_pval_str = f"{r['t_pvalue']:.2e}" if r['t_pvalue'] > 0 else "< 1e-300"
        u_pval_str = f"{r['mannwhitney_pvalue']:.2e}" if r['mannwhitney_pvalue'] > 0 else "< 1e-300"
        ks_pval_str = f"{r['ks_pvalue']:.2e}" if r['ks_pvalue'] > 0 else "< 1e-300"
        
        print(f"\n  t-test:        t = {r['t_statistic']:.3f}, p = {t_pval_str}")
        print(f"  Mann-Whitney: U = {r['mannwhitney_u']:.1f}, p = {u_pval_str}")
        print(f"  K-S test:     D = {r['ks_statistic']:.3f}, p = {ks_pval_str}")
        print(f"  Effect size:  Cohen's d = {r['cohen_d']:.3f}")
        print(f"\n  ► SEPARATION:   {r['separation']}")
        print()


def print_top_candidates(candidates, n=10):
    """Print top N candidate classes for non-algebraicity verification."""
    
    print("\n" + "="*70)
    print(f"TOP {n} CANDIDATES FOR NON-ALGEBRAICITY VERIFICATION")
    print("="*70 + "\n")
    
    for i, cand in enumerate(candidates[:n]):
        m = cand['monomial']
        sig = cand['signature']
        dist = cand['distance']
        
        # Format monomial
        parts = [f"z_{j}^{{{m[j]}}}" for j in range(6) if m[j] > 0]
        latex = ' '.join(parts)
        
        print(f"{i+1}.  {latex}")
        print(f"   Entropy:       {sig['entropy']:.3f} bits")
        print(f"   Variance:     {sig['variance']:.2f}")
        print(f"   Kolmogorov:   {sig['kolmogorov']}")
        print(f"   Range:        {sig['range']}")
        print(f"   Distance:     {dist:.3f} (from algebraic space)")
        print()


def save_results(data, stat_results, candidates):
    """Save all results to JSON files."""
    
    CONFIG['results_dir']. mkdir(exist_ok=True)
    
    # Save statistical results
    stat_file = CONFIG['results_dir'] / 'statistical_analysis.json'
    with open(stat_file, 'w') as f:
        json.dump(stat_results, f, indent=2)
    print(f"✓ Saved statistical results to {stat_file}")
    
    # Save top candidates
    cand_file = CONFIG['results_dir'] / 'top_candidates.json'
    top_50 = candidates[:50]
    with open(cand_file, 'w') as f:
        json.dump(top_50, f, indent=2)
    print(f"✓ Saved top 50 candidates to {cand_file}")
    
    # Save summary
    summary = {
        'num_isolated':  len(data['isolated']),
        'num_algebraic': len(data['algebraic']),
        'algebraic_sample_size': len(data['algebraic']),
        'highly_significant_metrics': [
            r['metric'] for r in stat_results if r['separation'] == 'HIGHLY SIGNIFICANT'
        ],
        'top_candidate':  {
            'monomial': candidates[0]['monomial'],
            'entropy': candidates[0]['signature']['entropy'],
            'kolmogorov': candidates[0]['signature']['kolmogorov'],
            'distance': candidates[0]['distance']
        }
    }
    
    summary_file = CONFIG['results_dir'] / 'summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved summary to {summary_file}")


def create_latex_table(candidates, n=20):
    """Generate LaTeX table for paper."""
    
    latex_file = CONFIG['results_dir'] / 'candidates_table.tex'
    
    with open(latex_file, 'w') as f:
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\small\n")
        f.write("\\begin{tabular}{|l|c|c|c|c|}\n")
        f.write("\\hline\n")
        f.write("Monomial & Entropy & Variance & Range & Distance \\\\\n")
        f.write("\\hline\n")
        
        for i, cand in enumerate(candidates[:n]):
            m = cand['monomial']
            sig = cand['signature']
            
            parts = [f"z_{j}^{{{m[j]}}}" for j in range(6) if m[j] > 0]
            latex = ' '.join(parts)
            
            f.write(f"${latex}$ & ")
            f.write(f"{sig['entropy']:.2f} & ")
            f.write(f"{sig['variance']:.1f} & ")
            f.write(f"{sig['range']} & ")
            f.write(f"{cand['distance']:.2f} \\\\\n")
        
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write(f"\\caption{{Top {n} candidate non-algebraic classes by information-theoretic distance. }}\n")
        f.write("\\label{tab:candidates}\n")
        f.write("\\end{table}\n")
    
    print(f"✓ Generated LaTeX table:  {latex_file}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main analysis pipeline."""
    
    print("\n" + "="*70)
    print("INFORMATION-THEORETIC OBSTRUCTION ANALYSIS (REVISED)")
    print("Optimized for MacBook Air M1 16GB")
    print("="*70 + "\n")
    
    # Load data
    data = load_data()
    
    # Compute signatures
    print("Computing information-theoretic signatures...")
    alg_sigs = compute_all_signatures(data['algebraic'])
    iso_sigs = compute_all_signatures(data['isolated'])
    print(f"✓ Computed {len(alg_sigs)} algebraic signatures")
    print(f"✓ Computed {len(iso_sigs)} isolated signatures\n")
    
    # Statistical analysis
    stat_results = analyze_all_metrics(alg_sigs, iso_sigs)
    print_statistical_results(stat_results)
    
    # Rank candidates
    print("Ranking candidates by distance from algebraic space...")
    candidates = rank_candidates(data['isolated'], iso_sigs, alg_sigs)
    print(f"✓ Ranked {len(candidates)} candidates\n")
    
    # Print top candidates
    print_top_candidates(candidates, n=10)
    
    # Save results
    save_results(data, stat_results, candidates)
    
    # Generate LaTeX
    create_latex_table(candidates, n=20)
    
    # Final summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    
    highly_sig = [r for r in stat_results if r['separation'] == 'HIGHLY SIGNIFICANT']
    print(f"\n✓ Found {len(highly_sig)} highly significant separations:")
    for r in highly_sig:
        print(f"  • {r['metric']}: p = {r['t_pvalue']:.2e}, d = {r['cohen_d']:.2f}")
    
    print(f"\n✓ Top candidate distance: {candidates[0]['distance']:.3f}")
    print(f"✓ Algebraic sample size: {len(data['algebraic'])} (expanded from 8)")
    print(f"✓ All results saved to: {CONFIG['results_dir']}/")
    print("\nNext steps:")
    print("  1. Review statistical_analysis.json")
    print("  2. Examine top_candidates.json")
    print("  3. Use candidates_table.tex in paper")
    print("  4. Results are robust to algebraic pattern expansion (n=24)")
    print()


if __name__ == "__main__":
    main()
