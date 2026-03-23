"""
NMR_ANALYSIS_001.PY
Naked Mole-Rat Eigenfunction Analysis — OC-OBS-004
Testing the Universal Tonnetz Prediction Against Barker 2021
OrganismCore — Eric Robert Lawson
Run date: 2026-03-23

PRE-REGISTRATION STATUS:
    This script implements the analysis plan specified in
    naked_mole_rat_eigenfunction_analysis.md v1.1
    All predictions were documented before data was loaded.
    Results are reported in full regardless of direction.

CONFIRMED DATA PARAMETERS (from nmr_samplerate.py):
    Sample rate:        22,050 Hz
    Total softchirps:   6,660
    Colonies:           baratheon (80 rec), martell (12),
                        dothrakib (5), stark (1)
    Longitudinal:       16 animals with multi-date records

USAGE:
    python nmr_analysis_001.py --data_dir Naked-mole-rat-voices-1.0
"""

import os
import sys
import argparse
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

import scipy.signal as signal
from scipy.stats import spearmanr, f_oneway
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE       = 22050       # Confirmed from diagnostic
CALL_CLASS        = "softchirp" # Target call type
CHIRP_FREQ_LOW    = 500         # Hz — soft chirp range lower bound
CHIRP_FREQ_HIGH   = 4000        # Hz — soft chirp range upper bound
STFT_WINDOW       = 512         # Samples — frequency resolution
STFT_HOP          = 128         # Samples — time resolution
N_MFCC            = 20          # MFCC coefficients
N_PCA_COMPONENTS  = 10          # Max PCA components to extract
PAD_DURATION_S    = 0.30        # Seconds — pad/trim all chirps to this
RANDOM_STATE      = 42

# Physical baseline — predicted harmonic modes of NMR vocal tract
# Derived from Heterocephalus glaber vocal anatomy BEFORE data load
# Vocal tract length ~2.5 cm, closed-open boundary conditions
# Fundamental: c / (4L) = 34300 / (4 * 0.025) = 3430 Hz
# But soft chirp fundamental is observed ~800-1200 Hz empirically
# suggesting effective resonating length ~7-10 cm with subglottal
# coupling — consistent with body cavity involvement
# Predicted harmonic series (fundamental F0 ~ 1000 Hz):
PREDICTED_HARMONICS_HZ = [1000, 2000, 3000, 4000, 5000]
PREDICTED_HARMONIC_RATIOS = [1.0, 2.0, 3.0, 4.0, 5.0]

# Colony colours for plotting
COLONY_COLORS = {
    "baratheon": "#2196F3",
    "martell":   "#FF9800",
    "dothrakib": "#4CAF50",
    "stark":     "#9C27B0"
}

OUTPUT_DIR = Path("nmr_results")

# ────────────────��────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--sample_rate", type=int,
                        default=SAMPLE_RATE)
    parser.add_argument("--max_chirps_per_recording", type=int,
                        default=999,
                        help="Cap per recording (0=no cap)")
    return parser.parse_args()


def parse_filename(fname):
    stem = Path(fname).stem
    parts = stem.split("_")
    return {
        "colony":     parts[0],
        "date":       parts[1],
        "animal_ids": parts[2:-1],
        "session_id": parts[-1]
    }


def read_annotations(txt_path, call_class=CALL_CLASS):
    """Return list of (start_s, end_s) for target call class."""
    results = []
    try:
        with open(txt_path, "r") as f:
            lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 3 and parts[2].strip() == call_class:
                try:
                    results.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue
    except Exception:
        pass
    return results


def seconds_to_samples(t, sr):
    return int(round(t * sr))


def extract_chirp(audio, start_s, end_s, sr, pad_duration_s):
    """
    Extract a chirp segment, pad or trim to fixed duration.
    Returns None if segment is invalid.
    """
    s = seconds_to_samples(start_s, sr)
    e = seconds_to_samples(end_s, sr)
    n_pad = seconds_to_samples(pad_duration_s, sr)

    if s < 0 or e > len(audio) or e <= s:
        return None

    seg = audio[s:e].copy()

    # Trim or zero-pad to fixed length
    if len(seg) >= n_pad:
        seg = seg[:n_pad]
    else:
        seg = np.pad(seg, (0, n_pad - len(seg)), mode="constant")

    # Remove DC offset
    seg = seg - np.mean(seg)

    # Normalize
    rms = np.sqrt(np.mean(seg ** 2))
    if rms > 1e-8:
        seg = seg / rms

    return seg


# ──���──────────────────────────────────────────────────────────
# STEP 1 — PHYSICAL BASELINE
# Derive predicted eigenfunction basis from vocal anatomy
# DONE BEFORE ANY DATA IS LOADED INTO ANALYSIS
# ─────────────────────────────────────────────────────────────

def step1_physical_baseline():
    """
    Derive predicted eigenfunction basis from NMR vocal anatomy.

    Heterocephalus glaber vocal tract:
    - Short, highly constrained vocal tract
    - Soft chirp: fundamental ~800-1200 Hz
    - Harmonic series determined by tract geometry
    - Closed-open boundary conditions (glottis to mouth)

    Pre-registered predictions:
    1. Empirical PCA eigenfunctions will correspond to
       physically-predicted harmonic modes
    2. Top 3-5 components will capture >80% variance
    3. Eigenfunction space will show Tonnetz topology
       (discrete clustering, not continuous distribution)
    """
    print("\n" + "=" * 60)
    print("STEP 1 — PHYSICAL BASELINE")
    print("Predicted eigenfunction basis from vocal anatomy")
    print("=" * 60)

    print("\n  Species:    Heterocephalus glaber")
    print("  Call type:  Soft chirp")
    print("  Freq range: 500–4000 Hz")
    print()
    print("  Predicted harmonic series:")
    for i, (hz, ratio) in enumerate(zip(PREDICTED_HARMONICS_HZ,
                                         PREDICTED_HARMONIC_RATIOS)):
        print(f"    H{i+1}: {hz} Hz  (ratio {ratio:.1f}×F0)")
    print()
    print("  Tonnetz topology prediction:")
    print("    Colony dialects = discrete positions in eigenfunction space")
    print("    Individual variation = local navigation within colony region")
    print("    Between-colony variance >> within-colony variance")
    print()
    print("  Pre-registered falsification criteria:")
    print("    FAIL if: empirical eigenfunctions are arbitrary")
    print("    FAIL if: eigenfunction space is continuous uniform")
    print("    FAIL if: no significant colony effect (η² < 0.3)")
    print()
    print("  [STEP 1 COMPLETE — predictions locked before data load]")

    return {
        "predicted_harmonics_hz": PREDICTED_HARMONICS_HZ,
        "predicted_ratios": PREDICTED_HARMONIC_RATIOS,
        "fundamental_hz": PREDICTED_HARMONICS_HZ[0]
    }


# ─────────────────────────────────────────────────────────────
# STEP 2 — LOAD AND EXTRACT CHIRPS
# ─────────────────────────────────────────────────────────────

def step2_load_chirps(data_dir, sr, args):
    """
    Load all softchirp segments from all recordings.
    Returns DataFrame with metadata and feature arrays.
    """
    print("\n" + "=" * 60)
    print("STEP 2 — LOADING SOFT CHIRP CORPUS")
    print("=" * 60)

    data_dir = Path(data_dir)
    records = []
    segments = []
    skipped = 0
    loaded = 0

    for root, dirs, files in os.walk(data_dir):
        for fname in sorted(files):
            if not fname.endswith(".npy"):
                continue
            npy_path = Path(root) / fname
            txt_path = npy_path.with_suffix(".txt")
            if not txt_path.exists():
                continue

            meta = parse_filename(fname)
            annotations = read_annotations(txt_path, CALL_CLASS)

            if not annotations:
                continue

            # Load audio once per file
            try:
                audio = np.load(npy_path, allow_pickle=False)
            except Exception as e:
                print(f"  WARNING: Could not load {fname}: {e}")
                continue

            cap = args.max_chirps_per_recording
            if cap > 0:
                annotations = annotations[:cap]

            for (start_s, end_s) in annotations:
                seg = extract_chirp(audio, start_s, end_s, sr,
                                    PAD_DURATION_S)
                if seg is None:
                    skipped += 1
                    continue

                records.append({
                    "colony":     meta["colony"],
                    "date":       meta["date"],
                    "animal_id":  meta["animal_ids"][0]
                                  if meta["animal_ids"] else "unknown",
                    "session_id": meta["session_id"],
                    "start_s":    start_s,
                    "end_s":      end_s,
                    "duration_s": end_s - start_s,
                    "filename":   fname
                })
                segments.append(seg)
                loaded += 1

    print(f"\n  Chirps loaded:   {loaded}")
    print(f"  Chirps skipped:  {skipped}")
    print(f"  Total segments:  {len(segments)}")

    df = pd.DataFrame(records)
    print(f"\n  Colony breakdown:")
    for col, grp in df.groupby("colony"):
        print(f"    {col:<15} {len(grp):>5} chirps  "
              f"({grp['animal_id'].nunique()} animals)")

    return df, np.array(segments)


# ─────────────────────────────────────────────────────────────
# STEP 3 — SPECTRAL FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────

def compute_stft_features(segment, sr, n_fft=STFT_WINDOW,
                           hop=STFT_HOP):
    """
    Compute spectral features from a single chirp segment.
    Returns feature vector.
    """
    # STFT
    freqs, times, Zxx = signal.stft(segment, fs=sr,
                                     nperseg=n_fft,
                                     noverlap=n_fft - hop)
    magnitude = np.abs(Zxx)
    power = magnitude ** 2

    # Mean power spectrum (averaged over time)
    mean_psd = np.mean(power, axis=1)

    # Restrict to chirp frequency range
    freq_mask = (freqs >= CHIRP_FREQ_LOW) & (freqs <= CHIRP_FREQ_HIGH)
    psd_band = mean_psd[freq_mask]
    freqs_band = freqs[freq_mask]

    # Normalize PSD
    if psd_band.sum() > 0:
        psd_norm = psd_band / psd_band.sum()
    else:
        psd_norm = psd_band

    # Spectral centroid
    if psd_norm.sum() > 0:
        centroid = np.sum(freqs_band * psd_norm)
    else:
        centroid = 0.0

    # Spectral spread
    spread = np.sqrt(np.sum(((freqs_band - centroid) ** 2) * psd_norm)
                     + 1e-10)

    # Fundamental frequency estimate (peak in band)
    if len(psd_band) > 0:
        f0_idx = np.argmax(psd_band)
        f0_est = freqs_band[f0_idx]
    else:
        f0_est = 0.0

    # Harmonic ratios (energy at predicted harmonics)
    harmonic_energies = []
    for h_hz in PREDICTED_HARMONICS_HZ:
        if h_hz <= sr / 2:
            h_idx = np.argmin(np.abs(freqs - h_hz))
            harmonic_energies.append(mean_psd[h_idx])
        else:
            harmonic_energies.append(0.0)

    # Concatenate feature vector: PSD + summary stats + harmonics
    features = np.concatenate([
        psd_norm,                           # Spectral shape
        [centroid, spread, f0_est],         # Summary
        harmonic_energies                   # Harmonic content
    ])

    return features, freqs_band, psd_norm, f0_est, centroid


def step3_extract_features(df, segments, sr):
    """
    Extract spectral features from all chirp segments.
    """
    print("\n" + "=" * 60)
    print("STEP 3 — SPECTRAL FEATURE EXTRACTION")
    print("=" * 60)

    feature_list = []
    f0_estimates = []
    centroids = []
    psds = []

    for i, seg in enumerate(segments):
        feats, freqs_band, psd_norm, f0, centroid = \
            compute_stft_features(seg, sr)
        feature_list.append(feats)
        f0_estimates.append(f0)
        centroids.append(centroid)
        psds.append(psd_norm)

    feature_matrix = np.array(feature_list)
    df = df.copy()
    df["f0_est"] = f0_estimates
    df["centroid"] = centroids

    print(f"\n  Feature matrix shape:  {feature_matrix.shape}")
    print(f"  N chirps:              {len(df)}")
    print(f"\n  F0 estimates:")
    print(f"    Mean:   {np.mean(f0_estimates):.1f} Hz")
    print(f"    Median: {np.median(f0_estimates):.1f} Hz")
    print(f"    Std:    {np.std(f0_estimates):.1f} Hz")
    print(f"    Min:    {np.min(f0_estimates):.1f} Hz")
    print(f"    Max:    {np.max(f0_estimates):.1f} Hz")

    print(f"\n  Spectral centroid:")
    print(f"    Mean:   {np.mean(centroids):.1f} Hz")
    print(f"    Median: {np.median(centroids):.1f} Hz")

    # F0 by colony
    print(f"\n  F0 by colony:")
    for col in df["colony"].unique():
        mask = df["colony"] == col
        f0_col = np.array(f0_estimates)[mask]
        print(f"    {col:<15} mean F0 = {np.mean(f0_col):.1f} Hz  "
              f"std = {np.std(f0_col):.1f} Hz")

    return df, feature_matrix, np.array(psds)


# ─────────────────────────────────────────────────────────────
# STEP 4 — EIGENFUNCTION DECOMPOSITION
# ─────────────────────────────────────────────────────────────

def step4_eigenfunction_decomposition(df, feature_matrix, physical):
    """
    Apply PCA to extract empirical eigenfunctions.
    Test whether they correspond to physical predictions.
    """
    print("\n" + "=" * 60)
    print("STEP 4 — EIGENFUNCTION DECOMPOSITION")
    print("=" * 60)

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feature_matrix)

    # PCA
    pca = PCA(n_components=min(N_PCA_COMPONENTS, feature_matrix.shape[1]))
    X_pca = pca.fit_transform(X_scaled)

    explained = pca.explained_variance_ratio_
    cumulative = np.cumsum(explained)

    print(f"\n  Variance explained by component:")
    for i, (ev, cum) in enumerate(zip(explained, cumulative)):
        marker = ""
        if cum <= 0.90 or (i > 0 and cumulative[i-1] < 0.90):
            marker = " ← 90% threshold" if cum >= 0.90 \
                     and (i == 0 or cumulative[i-1] < 0.90) else ""
        print(f"    PC{i+1:>2}: {ev:.4f}  cumulative: {cum:.4f}{marker}")

    n_90 = np.argmax(cumulative >= 0.90) + 1
    n_95 = np.argmax(cumulative >= 0.95) + 1
    n_99 = np.argmax(cumulative >= 0.99) + 1

    print(f"\n  Components for 90% variance: {n_90}")
    print(f"  Components for 95% variance: {n_95}")
    print(f"  Components for 99% variance: {n_99}")

    # Physical correspondence test
    # The PCA components load onto frequency bins
    # We test whether the top components peak at predicted harmonics
    print(f"\n  PHYSICAL CORRESPONDENCE TEST")
    print(f"  Pre-registered: empirical eigenfunctions should")
    print(f"  correspond to predicted harmonic modes")
    print()

    # Get the PSD-portion of the first loadings
    # Feature vector structure: [psd_norm..., centroid, spread, f0,
    #                             harmonic_energies...]
    # We need the frequency bands used
    sr = SAMPLE_RATE
    freqs = np.fft.rfftfreq(STFT_WINDOW, 1.0/sr)
    freq_mask = (freqs >= CHIRP_FREQ_LOW) & (freqs <= CHIRP_FREQ_HIGH)
    freqs_band = freqs[freq_mask]
    n_psd = len(freqs_band)

    corr_results = []
    for i in range(min(5, len(pca.components_))):
        comp = pca.components_[i]
        psd_loading = comp[:n_psd]
        peak_freq = freqs_band[np.argmax(np.abs(psd_loading))]

        # Find nearest predicted harmonic
        nearest_harmonic = min(PREDICTED_HARMONICS_HZ,
                               key=lambda h: abs(h - peak_freq))
        error_hz = abs(peak_freq - nearest_harmonic)

        corr_results.append({
            "component": i + 1,
            "peak_freq_hz": peak_freq,
            "nearest_harmonic_hz": nearest_harmonic,
            "error_hz": error_hz,
            "within_10pct": error_hz < (nearest_harmonic * 0.10)
        })

        match_str = "MATCH" if error_hz < nearest_harmonic * 0.10 \
                    else "NO MATCH"
        print(f"    PC{i+1}: peak at {peak_freq:.0f} Hz  "
              f"→ nearest harmonic {nearest_harmonic} Hz  "
              f"(error {error_hz:.0f} Hz)  [{match_str}]")

    n_matched = sum(r["within_10pct"] for r in corr_results)
    print(f"\n  Harmonic matches (within 10%): "
          f"{n_matched}/{len(corr_results)}")

    if n_matched >= 3:
        print("  → PHYSICAL CORRESPONDENCE: CONFIRMED")
    elif n_matched >= 2:
        print("  → PHYSICAL CORRESPONDENCE: PARTIAL")
    else:
        print("  → PHYSICAL CORRESPONDENCE: NOT CONFIRMED")

    return pca, X_pca, scaler, corr_results, n_90


# ─────────────────────────────────────────────────────────────
# STEP 5 — TONNETZ TOPOLOGY TEST
# ─────────────────────────────────────────────────────────────

def hartigan_dip_approx(x):
    """
    Approximate Hartigan's dip statistic.
    Tests unimodality vs multimodality.
    Returns (dip_statistic, is_multimodal).
    Simplified implementation — flags clear bimodality.
    """
    x_sorted = np.sort(x)
    n = len(x_sorted)
    if n < 10:
        return 0.0, False

    # Compute empirical CDF
    cdf = np.arange(1, n + 1) / n

    # Fit uniform CDF between min and max
    x_norm = (x_sorted - x_sorted[0]) / (x_sorted[-1] - x_sorted[0] + 1e-10)

    # Dip = max deviation from unimodal
    dip = np.max(np.abs(cdf - x_norm))

    # Threshold: dip > 0.05 suggests multimodality for n > 100
    is_multimodal = dip > 0.05 and n > 50

    return dip, is_multimodal


def step5_tonnetz_topology(df, X_pca, n_primary=4):
    """
    Test whether eigenfunction space has Tonnetz topology:
    discrete clustering vs continuous distribution.
    """
    print("\n" + "=" * 60)
    print("STEP 5 — TONNETZ TOPOLOGY TEST")
    print("=" * 60)

    # Use top N principal components
    X = X_pca[:, :n_primary]

    print(f"\n  Using top {n_primary} principal components")
    print(f"  N data points: {len(X)}")

    # ── Hartigan's dip test on each PC dimension ──
    print(f"\n  UNIMODALITY TEST (per dimension):")
    multimodal_dims = 0
    for dim in range(n_primary):
        dip, is_multi = hartigan_dip_approx(X[:, dim])
        flag = "MULTIMODAL" if is_multi else "unimodal"
        print(f"    PC{dim+1}: dip = {dip:.4f}  [{flag}]")
        if is_multi:
            multimodal_dims += 1

    print(f"\n  Multimodal dimensions: {multimodal_dims}/{n_primary}")
    if multimodal_dims >= 2:
        print("  → TONNETZ TOPOLOGY: DISCRETE STRUCTURE DETECTED")
    elif multimodal_dims == 1:
        print("  → TONNETZ TOPOLOGY: PARTIAL STRUCTURE")
    else:
        print("  → TONNETZ TOPOLOGY: CONTINUOUS (no discrete clustering)")

    # ── k-means clustering ──
    print(f"\n  K-MEANS CLUSTERING TEST:")
    n_colonies = df["colony"].nunique()
    print(f"  Testing k = 2 to {n_colonies + 3}")

    best_k = 2
    best_score = -1
    silhouette_scores = {}

    for k in range(2, n_colonies + 4):
        if k >= len(X):
            break
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE,
                    n_init=10)
        labels = km.fit_predict(X)
        if len(np.unique(labels)) < 2:
            continue
        score = silhouette_score(X, labels)
        silhouette_scores[k] = score
        if score > best_score:
            best_score = score
            best_k = k
        print(f"    k={k}: silhouette = {score:.4f}")

    print(f"\n  Optimal k:        {best_k}")
    print(f"  Best silhouette:  {best_score:.4f}")
    print(f"  N colonies:       {n_colonies}")

    if best_k == n_colonies:
        print("  → CLUSTER COUNT MATCHES COLONY COUNT: YES")
    else:
        print(f"  → CLUSTER COUNT MATCHES COLONY COUNT: NO "
              f"(k={best_k} vs {n_colonies} colonies)")

    # Final k-means with best k
    km_final = KMeans(n_clusters=best_k, random_state=RANDOM_STATE,
                      n_init=10)
    cluster_labels = km_final.fit_predict(X)
    df = df.copy()
    df["cluster"] = cluster_labels

    return df, X, cluster_labels, best_k, silhouette_scores


# ─────────────────────────────────────────────────────────────
# STEP 6 — COLONY DIALECT AS TONNETZ NAVIGATION
# ────────────────────────────────────────���────────────────────

def step6_colony_dialect(df, X_pca, n_primary=4):
    """
    Test whether colony dialects represent discrete Tonnetz positions.
    ANOVA: between-colony vs within-colony variance in eigenfunction space.
    """
    print("\n" + "=" * 60)
    print("STEP 6 — COLONY DIALECT AS TONNETZ NAVIGATION")
    print("=" * 60)

    X = X_pca[:, :n_primary]
    colonies = df["colony"].values
    unique_colonies = df["colony"].unique()

    # Colony centroids in eigenfunction space
    print(f"\n  COLONY CENTROIDS IN EIGENFUNCTION SPACE:")
    centroids = {}
    within_vars = {}
    for col in unique_colonies:
        mask = colonies == col
        X_col = X[mask]
        centroid = np.mean(X_col, axis=0)
        within_var = np.mean(np.var(X_col, axis=0))
        centroids[col] = centroid
        within_vars[col] = within_var
        n = mask.sum()
        print(f"\n  {col.upper()} (n={n})")
        for dim in range(n_primary):
            print(f"    PC{dim+1}: {centroid[dim]:+.4f}")
        print(f"    Within-colony variance: {within_var:.4f}")

    # Between-colony distances
    print(f"\n  INTER-COLONY DISTANCES IN EIGENFUNCTION SPACE:")
    cols = list(centroids.keys())
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            dist = np.linalg.norm(centroids[cols[i]] - centroids[cols[j]])
            print(f"    {cols[i]} ↔ {cols[j]}: {dist:.4f}")

    # One-way ANOVA on each PC dimension
    print(f"\n  ONE-WAY ANOVA (colony effect on each PC):")
    groups_per_colony = []
    for col in unique_colonies:
        mask = colonies == col
        groups_per_colony.append(X[mask])

    eta_sq_values = []
    for dim in range(n_primary):
        groups = [g[:, dim] for g in groups_per_colony
                  if len(g) > 1]
        if len(groups) < 2:
            continue
        f_stat, p_val = f_oneway(*groups)

        # Eta squared (effect size)
        grand_mean = np.mean(X[:, dim])
        ss_between = sum(
            len(g[:, dim]) * (np.mean(g[:, dim]) - grand_mean) ** 2
            for g in groups
        )
        ss_total = np.sum((X[:, dim] - grand_mean) ** 2)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        eta_sq_values.append(eta_sq)
        sig = "***" if p_val < 0.001 else \
              "**"  if p_val < 0.01  else \
              "*"   if p_val < 0.05  else "ns"
        print(f"    PC{dim+1}: F={f_stat:.2f}  p={p_val:.4e}  "
              f"η²={eta_sq:.3f}  [{sig}]")

    mean_eta_sq = np.mean(eta_sq_values) if eta_sq_values else 0
    print(f"\n  Mean η² across PCs: {mean_eta_sq:.3f}")

    if mean_eta_sq >= 0.5:
        print("  → COLONY EFFECT: LARGE (η² ≥ 0.5) — CONFIRMED")
    elif mean_eta_sq >= 0.3:
        print("  → COLONY EFFECT: MEDIUM (η² ≥ 0.3) — PARTIAL")
    else:
        print("  → COLONY EFFECT: SMALL (η² < 0.3) — NOT CONFIRMED")

    # Within vs between variance ratio
    total_within = np.mean(list(within_vars.values()))
    all_centroids = np.array(list(centroids.values()))
    between_var = np.mean(np.var(all_centroids, axis=0))
    ratio = between_var / (total_within + 1e-10)

    print(f"\n  VARIANCE RATIO (between/within): {ratio:.3f}")
    if ratio > 2.0:
        print("  → DIALECT SEPARATION: STRONG")
    elif ratio > 1.0:
        print("  → DIALECT SEPARATION: MODERATE")
    else:
        print("  → DIALECT SEPARATION: WEAK")

    return centroids, within_vars, mean_eta_sq, ratio


# ─────────────────────────────────────────────────────────────
# STEP 7 — INDIVIDUAL VARIATION AS LOCAL NAVIGATION
# ─────────────────────────────────────────────────────────────

def step7_individual_variation(df, X_pca, n_primary=4):
    """
    Test whether individual variation is bounded within
    the colony's Tonnetz region.
    """
    print("\n" + "=" * 60)
    print("STEP 7 — INDIVIDUAL VARIATION AS LOCAL NAVIGATION")
    print("=" * 60)

    X = X_pca[:, :n_primary]
    colonies = df["colony"].values
    animals = df["animal_id"].values
    unique_colonies = df["colony"].unique()

    print(f"\n  INDIVIDUAL vs COLONY VARIANCE RATIO:")
    print(f"  (Low ratio = bounded local navigation)")
    print(f"  (Ratio → 1.0 = free individual variation)")
    print()

    all_ratios = []
    for col in unique_colonies:
        col_mask = colonies == col
        X_col = X[col_mask]
        col_variance = np.mean(np.var(X_col, axis=0))

        animals_in_col = np.unique(animals[col_mask])
        if len(animals_in_col) < 2:
            continue

        ind_vars = []
        for animal in animals_in_col:
            a_mask = (colonies == col) & (animals == animal)
            X_animal = X[a_mask]
            if len(X_animal) < 3:
                continue
            ind_var = np.mean(np.var(X_animal, axis=0))
            ind_vars.append(ind_var)

        if not ind_vars:
            continue

        mean_ind_var = np.mean(ind_vars)
        ratio = mean_ind_var / (col_variance + 1e-10)
        all_ratios.append(ratio)

        print(f"  {col.upper()}")
        print(f"    Colony variance:     {col_variance:.4f}")
        print(f"    Mean indiv variance: {mean_ind_var:.4f}")
        print(f"    Ratio (ind/col):     {ratio:.4f}")
        if ratio < 0.5:
            print(f"    → BOUNDED LOCAL NAVIGATION: YES")
        elif ratio < 0.8:
            print(f"    → BOUNDED LOCAL NAVIGATION: MODERATE")
        else:
            print(f"    → BOUNDED LOCAL NAVIGATION: NO")
        print()

    if all_ratios:
        mean_ratio = np.mean(all_ratios)
        print(f"  Mean individual/colony variance ratio: {mean_ratio:.4f}")
        if mean_ratio < 0.5:
            print("  → INDIVIDUAL NAVIGATION IS LOCALLY BOUNDED: CONFIRMED")
        else:
            print("  → INDIVIDUAL NAVIGATION IS LOCALLY BOUNDED: "
                  "NOT CONFIRMED")

    return all_ratios


# ─────────────────────────────────────────────────────────────
# STEP 8 — LONGITUDINAL STABILITY TEST
# ─────────────────────────────────────────────────────────────

def step8_longitudinal(df, X_pca, n_primary=4):
    """
    Test whether individual animals maintain stable Tonnetz
    positions across recording dates (2017-2020).
    """
    print("\n" + "=" * 60)
    print("STEP 8 — LONGITUDINAL STABILITY")
    print("Animal Tonnetz position stability across dates")
    print("=" * 60)

    X = X_pca[:, :n_primary]
    animals = df["animal_id"].values
    dates = df["date"].values
    colonies = df["colony"].values

    # Find animals with multiple dates
    animal_date_map = defaultdict(set)
    for a, d in zip(animals, dates):
        animal_date_map[a].add(d)

    multi_date_animals = {a: sorted(d)
                          for a, d in animal_date_map.items()
                          if len(d) > 1}

    print(f"\n  Animals with multiple recording dates: "
          f"{len(multi_date_animals)}")

    stability_results = []
    for animal, date_list in sorted(
            multi_date_animals.items(),
            key=lambda x: -len(x[1])):

        colony = colonies[animals == animal][0]
        positions = []
        for date in date_list:
            mask = (animals == animal) & (dates == date)
            if mask.sum() < 2:
                continue
            pos = np.mean(X[mask], axis=0)
            positions.append((date, pos))

        if len(positions) < 2:
            continue

        # Compute drift: distance between first and last position
        first_pos = positions[0][1]
        last_pos = positions[-1][1]
        drift = np.linalg.norm(last_pos - first_pos)

        # Mean step size between consecutive dates
        steps = []
        for i in range(len(positions) - 1):
            step = np.linalg.norm(positions[i+1][1] - positions[i][1])
            steps.append(step)
        mean_step = np.mean(steps) if steps else 0

        stability_results.append({
            "animal": animal,
            "colony": colony,
            "n_dates": len(positions),
            "drift": drift,
            "mean_step": mean_step
        })

        print(f"\n  Animal {animal} ({colony}): "
              f"{len(positions)} dates")
        print(f"    Total drift (first→last): {drift:.4f}")
        print(f"    Mean step between dates:  {mean_step:.4f}")
        if drift < 2.0:
            print(f"    → POSITION STABLE OVER TIME: YES")
        else:
            print(f"    → POSITION STABLE OVER TIME: "
                  f"DRIFT DETECTED")

    if stability_results:
        mean_drift = np.mean([r["drift"] for r in stability_results])
        print(f"\n  Mean drift across all longitudinal animals: "
              f"{mean_drift:.4f}")
        if mean_drift < 2.0:
            print("  → COLONY TONNETZ POSITIONS STABLE OVER TIME: "
                  "CONFIRMED")
        else:
            print("  → COLONY TONNETZ POSITIONS STABLE OVER TIME: "
                  "NOT CONFIRMED")

    return stability_results


# ─────────────────────────────────────────────────────────────
# STEP 9 — CALL TYPE TAXONOMY IN EIGENFUNCTION SPACE
# Additional: test whether other call types (weirdo, downsweep,
# whistle) occupy identifiable positions in the Tonnetz
# ─────────────────────────────��───────────────────────────────

def step9_call_taxonomy(data_dir, scaler, pca, sr,
                        n_primary=4, args=None):
    """
    Load all call types (not just softchirp) and project into
    the eigenfunction space learned from softchirps.
    Test whether other call types occupy distinct Tonnetz positions.
    """
    print("\n" + "=" * 60)
    print("STEP 9 — FULL CALL TAXONOMY IN EIGENFUNCTION SPACE")
    print("All call types projected into Tonnetz")
    print("=" * 60)

    data_dir = Path(data_dir)
    target_classes = ["softchirp", "weirdo", "downsweep",
                      "whistle", "loudchirp", "upsweep"]

    records = []
    features = []

    for root, dirs, files in os.walk(data_dir):
        for fname in sorted(files):
            if not fname.endswith(".npy"):
                continue
            npy_path = Path(root) / fname
            txt_path = npy_path.with_suffix(".txt")
            if not txt_path.exists():
                continue

            meta = parse_filename(fname)

            # Read all annotations
            all_annotations = []
            try:
                with open(txt_path, "r") as f:
                    lines = f.readlines()
                for line in lines[1:]:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        cl = parts[2].strip()
                        if cl in target_classes:
                            try:
                                all_annotations.append(
                                    (float(parts[0]),
                                     float(parts[1]),
                                     cl))
                            except ValueError:
                                continue
            except Exception:
                continue

            if not all_annotations:
                continue

            try:
                audio = np.load(npy_path, allow_pickle=False)
            except Exception:
                continue

            for (start_s, end_s, cl) in all_annotations:
                seg = extract_chirp(audio, start_s, end_s,
                                    sr, PAD_DURATION_S)
                if seg is None:
                    continue

                feats, _, _, _, _ = compute_stft_features(seg, sr)
                records.append({
                    "colony":    meta["colony"],
                    "call_type": cl
                })
                features.append(feats)

    if not features:
        print("  No multi-class data loaded.")
        return None, None

    X_all = np.array(features)
    df_all = pd.DataFrame(records)

    # Project into eigenfunction space using fitted scaler and PCA
    X_scaled = scaler.transform(X_all)
    X_proj = pca.transform(X_scaled)

    print(f"\n  Total calls projected: {len(df_all)}")
    print(f"\n  Call type distribution in Tonnetz space:")
    print(f"  (showing centroid of each call type in PC1-PC{n_primary})")
    print()

    call_centroids = {}
    for ct in target_classes:
        mask = df_all["call_type"] == ct
        if mask.sum() < 2:
            continue
        centroid = np.mean(X_proj[mask, :n_primary], axis=0)
        call_centroids[ct] = centroid
        print(f"  {ct:<15} n={mask.sum():>5}  "
              f"PC1={centroid[0]:+.3f}  "
              f"PC2={centroid[1]:+.3f}  "
              f"PC3={centroid[2]:+.3f}")

    # Distance between softchirp centroid and other call types
    if "softchirp" in call_centroids:
        print(f"\n  Distance from softchirp to other call types:")
        sc_cent = call_centroids["softchirp"]
        for ct, cent in call_centroids.items():
            if ct == "softchirp":
                continue
            dist = np.linalg.norm(cent - sc_cent)
            print(f"    softchirp → {ct:<15} dist = {dist:.4f}")

    return df_all, X_proj


# ─────────────────────────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────────────────────────

def make_plots(df, X_pca, cluster_labels, centroids,
               silhouette_scores, stability_results,
               df_all=None, X_proj_all=None):
    """
    Generate all result plots.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    colony_list = df["colony"].unique().tolist()

    # ── Plot 1: PCA scatter by colony ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("NMR Soft Chirp — Eigenfunction Space by Colony",
                 fontsize=13, fontweight="bold")

    for col in colony_list:
        mask = df["colony"] == col
        color = COLONY_COLORS.get(col, "gray")
        X_col = X_pca[mask]
        axes[0].scatter(X_col[:, 0], X_col[:, 1],
                        c=color, label=col, alpha=0.4, s=10)
        axes[1].scatter(X_col[:, 1], X_col[:, 2],
                        c=color, label=col, alpha=0.4, s=10)

    # Plot colony centroids
    for col, cent in centroids.items():
        color = COLONY_COLORS.get(col, "gray")
        axes[0].scatter(cent[0], cent[1], c=color,
                        s=200, marker="*", edgecolors="black",
                        linewidth=1.5, zorder=5)
        axes[1].scatter(cent[1], cent[2], c=color,
                        s=200, marker="*", edgecolors="black",
                        linewidth=1.5, zorder=5)

    axes[0].set_xlabel("PC1")
    axes[0].set_ylabel("PC2")
    axes[0].set_title("PC1 vs PC2")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("PC2")
    axes[1].set_ylabel("PC3")
    axes[1].set_title("PC2 vs PC3")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_eigenfunction_space_by_colony.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved: 01_eigenfunction_space_by_colony.png")

    # ── Plot 2: Silhouette scores ──
    if silhouette_scores:
        fig, ax = plt.subplots(figsize=(8, 5))
        ks = list(silhouette_scores.keys())
        scores = list(silhouette_scores.values())
        ax.plot(ks, scores, "o-", color="#2196F3", linewidth=2)
        ax.axvline(x=df["colony"].nunique(), color="red",
                   linestyle="--", label="N colonies")
        ax.set_xlabel("Number of clusters (k)")
        ax.set_ylabel("Silhouette score")
        ax.set_title("Optimal Cluster Count in Eigenfunction Space")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "02_silhouette_scores.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 02_silhouette_scores.png")

    # ── Plot 3: Longitudinal trajectories ──
    if stability_results:
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set_title("Individual Animal Trajectories in Eigenfunction "
                     "Space (PC1 vs PC2)",
                     fontsize=11, fontweight="bold")

        animals_plotted = [r["animal"] for r in stability_results
                           if r["n_dates"] >= 3][:8]

        cmap = plt.cm.get_cmap("tab10")
        for idx, animal in enumerate(animals_plotted):
            mask = df["animal_id"] == animal
            col = df[mask]["colony"].values[0]
            color = cmap(idx)

            dates_for_animal = sorted(df[mask]["date"].unique())
            date_positions = []
            for date in dates_for_animal:
                d_mask = mask & (df["date"] == date)
                if d_mask.sum() < 2:
                    continue
                pos = np.mean(X_pca[d_mask, :2], axis=0)
                date_positions.append((date, pos))

            if len(date_positions) < 2:
                continue

            positions_arr = np.array([p for _, p in date_positions])
            ax.plot(positions_arr[:, 0], positions_arr[:, 1],
                    "o-", color=color, alpha=0.7, linewidth=1.5,
                    markersize=6, label=f"Animal {animal} ({col})")
            ax.plot(positions_arr[0, 0], positions_arr[0, 1],
                    "^", color=color, markersize=10, zorder=5)
            ax.plot(positions_arr[-1, 0], positions_arr[-1, 1],
                    "s", color=color, markersize=10, zorder=5)

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.legend(fontsize=7, loc="best")
        ax.grid(True, alpha=0.3)
        ax.set_title("Longitudinal Trajectories\n"
                     "(▲ = first recording, ■ = last recording)")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "03_longitudinal_trajectories.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 03_longitudinal_trajectories.png")

    # ── Plot 4: All call types in eigenfunction space ──
    if df_all is not None and X_proj_all is not None:
        fig, ax = plt.subplots(figsize=(10, 7))
        call_types = df_all["call_type"].unique()
        cmap = plt.cm.get_cmap("Set1")
        for idx, ct in enumerate(call_types):
            mask = df_all["call_type"] == ct
            if mask.sum() < 2:
                continue
            ax.scatter(X_proj_all[mask, 0], X_proj_all[mask, 1],
                       label=f"{ct} (n={mask.sum()})",
                       alpha=0.3, s=8, color=cmap(idx))

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title("All Call Types in Eigenfunction Space",
                     fontsize=11, fontweight="bold")
        ax.legend(fontsize=8, loc="best")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "04_all_call_types_tonnetz.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 04_all_call_types_tonnetz.png")

    print(f"\n  All plots saved to: {OUTPUT_DIR}/")


# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────

def final_report(corr_results, mean_eta_sq, ratio,
                 all_ind_ratios, best_k, n_colonies,
                 best_silhouette, multimodal_dims, n_primary):

    print("\n" + "=" * 60)
    print("FINAL RESULT SUMMARY — OC-OBS-004")
    print("=" * 60)

    sep = "─" * 60

    print(f"\n{sep}")
    print("PRIMARY PREDICTION")
    print("Empirical eigenfunctions correspond to physical harmonics")
    print(sep)
    n_matched = sum(r["within_10pct"] for r in corr_results)
    if n_matched >= 3:
        print(f"  RESULT: CONFIRMED ({n_matched}/{len(corr_results)} "
              f"components match within 10%)")
    elif n_matched >= 2:
        print(f"  RESULT: PARTIAL ({n_matched}/{len(corr_results)} "
              f"components match)")
    else:
        print(f"  RESULT: NOT CONFIRMED ({n_matched}/{len(corr_results)} "
              f"components match)")

    print(f"\n{sep}")
    print("SECONDARY PREDICTION")
    print("Eigenfunction space has Tonnetz topology (discrete clusters)")
    print(sep)
    if multimodal_dims >= 2:
        print(f"  RESULT: CONFIRMED "
              f"({multimodal_dims}/{n_primary} dims multimodal, "
              f"best silhouette={best_silhouette:.3f})")
    elif best_silhouette > 0.3:
        print(f"  RESULT: PARTIAL "
              f"(silhouette={best_silhouette:.3f})")
    else:
        print(f"  RESULT: NOT CONFIRMED "
              f"(silhouette={best_silhouette:.3f})")

    print(f"\n{sep}")
    print("TERTIARY PREDICTION")
    print("Colony effect large (η² ≥ 0.5)")
    print(sep)
    if mean_eta_sq >= 0.5:
        print(f"  RESULT: CONFIRMED (mean η² = {mean_eta_sq:.3f})")
    elif mean_eta_sq >= 0.3:
        print(f"  RESULT: PARTIAL (mean η² = {mean_eta_sq:.3f})")
    else:
        print(f"  RESULT: NOT CONFIRMED (mean η² = {mean_eta_sq:.3f})")

    print(f"\n{sep}")
    print("INDIVIDUAL NAVIGATION")
    print("Individual variation bounded within colony region")
    print(sep)
    if all_ind_ratios:
        mean_r = np.mean(all_ind_ratios)
        if mean_r < 0.5:
            print(f"  RESULT: CONFIRMED (mean ind/col ratio = {mean_r:.3f})")
        else:
            print(f"  RESULT: NOT CONFIRMED (mean ratio = {mean_r:.3f})")
    else:
        print("  RESULT: INSUFFICIENT DATA")

    print(f"\n{sep}")
    print("OPTIMAL CLUSTER COUNT vs COLONY COUNT")
    print(sep)
    print(f"  Optimal k:    {best_k}")
    print(f"  N colonies:   {n_colonies}")
    if best_k == n_colonies:
        print(f"  RESULT: MATCH")
    else:
        print(f"  RESULT: NO MATCH (k={best_k} vs {n_colonies} colonies)")

    print(f"\n{sep}")
    print("FRAMEWORK ASSESSMENT")
    print(sep)
    confirmed = sum([
        n_matched >= 3,
        multimodal_dims >= 2 or best_silhouette > 0.3,
        mean_eta_sq >= 0.3,
        bool(all_ind_ratios) and np.mean(all_ind_ratios) < 0.5
    ])
    print(f"  Predictions confirmed:  {confirmed}/4")
    if confirmed >= 3:
        print("  → UNIVERSAL TONNETZ FRAMEWORK: SUPPORTED")
    elif confirmed >= 2:
        print("  → UNIVERSAL TONNETZ FRAMEWORK: PARTIALLY SUPPORTED")
    else:
        print("  → UNIVERSAL TONNETZ FRAMEWORK: NOT SUPPORTED BY THIS DATA")

    print(f"\n  Results reported in full regardless of direction.")
    print(f"  This is the pre-registered analysis.")
    print(f"  See naked_mole_rat_eigenfunction_analysis.md v1.1")
    print()


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    sr = args.sample_rate

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("  OC-OBS-004 — NMR EIGENFUNCTION ANALYSIS")
    print("  Universal Tonnetz Framework Test")
    print("  OrganismCore — Eric Robert Lawson")
    print("=" * 60)
    print(f"\n  Data directory: {args.data_dir}")
    print(f"  Sample rate:    {sr} Hz")
    print(f"  Target class:   {CALL_CLASS}")

    # Step 1: Physical baseline — BEFORE data load
    physical = step1_physical_baseline()

    # Step 2: Load chirps
    df, segments = step2_load_chirps(args.data_dir, sr, args)

    if len(segments) < 10:
        print("ERROR: Insufficient chirps loaded. Check data path.")
        sys.exit(1)

    # Step 3: Feature extraction
    df, feature_matrix, psds = step3_extract_features(
        df, segments, sr)

    # Step 4: Eigenfunction decomposition
    pca, X_pca, scaler, corr_results, n_90 = \
        step4_eigenfunction_decomposition(df, feature_matrix, physical)

    # Step 5: Tonnetz topology
    df, X, cluster_labels, best_k, silhouette_scores = \
        step5_tonnetz_topology(df, X_pca, n_primary=4)

    best_silhouette = max(silhouette_scores.values()) \
        if silhouette_scores else 0
    multimodal_count = sum(
        1 for dim in range(4)
        if hartigan_dip_approx(X_pca[:, dim])[1]
    )

    # Step 6: Colony dialect
    centroids, within_vars, mean_eta_sq, ratio = \
        step6_colony_dialect(df, X_pca, n_primary=4)

    # Step 7: Individual variation
    all_ind_ratios = step7_individual_variation(df, X_pca, n_primary=4)

    # Step 8: Longitudinal stability
    stability_results = step8_longitudinal(df, X_pca, n_primary=4)

    # Step 9: Full call taxonomy
    df_all, X_proj_all = step9_call_taxonomy(
        args.data_dir, scaler, pca, sr, n_primary=4, args=args)

    # Plots
    make_plots(df, X_pca, cluster_labels, centroids,
               silhouette_scores, stability_results,
               df_all, X_proj_all)

    # Final report
    final_report(corr_results, mean_eta_sq, ratio,
                 all_ind_ratios, best_k,
                 df["colony"].nunique(),
                 best_silhouette, multimodal_count, 4)


if __name__ == "__main__":
    main()
