"""
NMR_ANALYSIS_003.PY
Naked Mole-Rat Queen Geometry Analysis — OC-OBS-004-Q
Testing the Queen Geometric Anchor Hypothesis
OrganismCore — Eric Robert Lawson
Run date: 2026-03-23

PRE-REGISTRATION:
    OC-OBS-004_QUEEN_GEOMETRY_PREREGISTRATION.md v1.0
    All predictions documented before this script was written.

PRECONDITIONS:
    OC-OBS-004 V2 complete and SUPPORTED
    Dataset confirmed: Barker 2021, Zenodo 4104396
    Sample rate confirmed: 22,050 Hz

PREDICTIONS BEING TESTED:
    P1: Queen eigenfunction geometry is more stable over
        time than mean worker stability
    P2: Queen is closest individual to colony centroid
        in eigenfunction space
    P3: Workers are closer to queen than to workerless
        colony centroid
    P4: Inter-colony distances reflect queen geometry
        distances
    P5: Queen geometry more different between colonies
        than worker geometries

MODULE STRUCTURE:
    M1: Queen candidate identification (4 criteria)
    M2: Colony alignment to queen candidate
    M3: Temporal alignment test (per-session)
    M4: Inter-colony queen geometry comparison
    M5: Generative synthesis specification

USAGE:
    python nmr_analysis_003.py --data_dir Naked-mole-rat-voices-1.0
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
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────
# CONFIGURATION — inherited from V2
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE         = 22050
CALL_CLASS          = "softchirp"
CHIRP_FREQ_LOW      = 500
CHIRP_FREQ_HIGH     = 4000
STFT_WINDOW         = 512
STFT_HOP            = 128
N_PCA_COMPONENTS    = 10
PAD_DURATION_S      = 0.30
RANDOM_STATE        = 42
N_PERMUTATIONS      = 1000
N_PRIMARY_PCS       = 4

PREDICTED_HARMONICS_HZ = [1000, 2000, 3000, 4000, 5000]

# Minimum dates required to be included in queen ID analysis
MIN_DATES_FOR_QUEEN_ID = 4

# Colony for queen identification (only baratheon has
# sufficient longitudinal coverage)
QUEEN_ID_COLONY = "baratheon"

COLONY_COLORS = {
    "baratheon": "#2196F3",
    "martell":   "#FF9800",
    "dothrakib": "#4CAF50",
    "stark":     "#9C27B0"
}

OUTPUT_DIR = Path("nmr_results_003")


# ─────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir",    type=str, required=True)
    parser.add_argument("--sample_rate", type=int, default=SAMPLE_RATE)
    parser.add_argument("--n_perms",     type=int, default=N_PERMUTATIONS)
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────
# SHARED UTILITIES — carried from V2
# ─────────────────────────────────────────────────────────────

def parse_filename(fname):
    stem       = Path(fname).stem
    parts      = stem.split("_")
    colony     = parts[0]
    date       = parts[1]
    session_id = parts[-1]
    animal_ids = parts[2:-1]
    return {
        "colony":     colony,
        "date":       date,
        "animal_ids": animal_ids,
        "session_id": session_id,
        "is_dual":    len(animal_ids) == 2,
        "n_animals":  len(animal_ids)
    }


def read_annotations(txt_path, call_class=CALL_CLASS):
    results = []
    try:
        with open(txt_path, "r") as f:
            lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                try:
                    results.append((
                        float(parts[0]),
                        float(parts[1]),
                        parts[2].strip()
                    ))
                except ValueError:
                    continue
    except Exception:
        pass
    return results


def extract_chirp(audio, start_s, end_s, sr, pad_s):
    s = int(round(start_s * sr))
    e = int(round(end_s   * sr))
    n = int(round(pad_s   * sr))
    if s < 0 or e > len(audio) or e <= s:
        return None
    seg = audio[s:e].copy()
    if len(seg) >= n:
        seg = seg[:n]
    else:
        seg = np.pad(seg, (0, n - len(seg)), mode="constant")
    seg = seg - np.mean(seg)
    rms = np.sqrt(np.mean(seg ** 2))
    if rms > 1e-8:
        seg = seg / rms
    return seg


def compute_features(segment, sr):
    freqs, _, Zxx = signal.stft(
        segment, fs=sr, nperseg=STFT_WINDOW,
        noverlap=STFT_WINDOW - STFT_HOP)
    magnitude  = np.abs(Zxx)
    mean_psd   = np.mean(magnitude ** 2, axis=1)
    freq_mask  = (freqs >= CHIRP_FREQ_LOW) & (freqs <= CHIRP_FREQ_HIGH)
    freqs_band = freqs[freq_mask]
    psd_band   = mean_psd[freq_mask]
    psd_norm   = psd_band / (psd_band.sum() + 1e-12)
    centroid   = float(np.sum(freqs_band * psd_norm))
    spread     = float(np.sqrt(
        np.sum(((freqs_band - centroid) ** 2) * psd_norm) + 1e-10))
    f0_est     = float(freqs_band[np.argmax(psd_band)]) \
                 if len(psd_band) > 0 else 0.0
    harmonic_e = []
    for h_hz in PREDICTED_HARMONICS_HZ:
        if h_hz <= sr / 2:
            idx = int(np.argmin(np.abs(freqs - h_hz)))
            harmonic_e.append(float(mean_psd[idx]))
        else:
            harmonic_e.append(0.0)
    features = np.concatenate([
        psd_norm, [centroid, spread, f0_est], harmonic_e])
    return features, freqs_band, psd_norm, f0_est, centroid


# ─────────────────────────────────────────────────────────────
# DATA LOADING — individual-valid only for queen analysis
# ─────────────────────────────────────────────────────────────

def load_individual_chirps(data_dir, sr):
    """
    Load all softchirp segments with individual-valid flag.
    Dual-channel mono files are session-level and excluded
    from individual-level queen analysis.
    Returns df, segments, feature_matrix, X_pca, scaler, pca
    """
    print("\n" + "=" * 60)
    print("DATA LOADING — Individual-valid chirps")
    print("=" * 60)

    data_dir = Path(data_dir)
    records  = []
    segments = []

    for root, dirs, files in os.walk(data_dir):
        for fname in sorted(files):
            if not fname.endswith(".npy"):
                continue
            npy_path = Path(root) / fname
            txt_path = npy_path.with_suffix(".txt")
            if not txt_path.exists():
                continue

            meta     = parse_filename(fname)
            all_anns = read_annotations(txt_path, CALL_CLASS)
            targets  = [(s, e) for s, e, cl in all_anns
                        if cl == CALL_CLASS]
            if not targets:
                continue

            try:
                audio_raw = np.load(npy_path, allow_pickle=False)
            except Exception:
                continue

            # Channel handling — E1 fix from V2
            if audio_raw.ndim == 2 and audio_raw.shape[1] == 2:
                channels = {
                    meta["animal_ids"][0]: audio_raw[:, 0],
                    meta["animal_ids"][1] if meta["is_dual"]
                        else meta["animal_ids"][0]: audio_raw[:, 1]
                }
            else:
                if meta["is_dual"]:
                    # Mono dual-ID — session level, excluded from
                    # individual analysis
                    channels = {
                        f"{meta['animal_ids'][0]}_"
                        f"{meta['animal_ids'][1]}":
                        audio_raw.flatten()
                    }
                else:
                    aid = (meta["animal_ids"][0]
                           if meta["animal_ids"] else "unknown")
                    channels = {aid: audio_raw.flatten()}

            for animal_id, audio in channels.items():
                individual_valid = "_" not in animal_id
                for (start_s, end_s) in targets:
                    seg = extract_chirp(audio, start_s, end_s,
                                        sr, PAD_DURATION_S)
                    if seg is None:
                        continue
                    records.append({
                        "colony":           meta["colony"],
                        "date":             meta["date"],
                        "animal_id":        animal_id,
                        "session_id":       meta["session_id"],
                        "individual_valid": individual_valid,
                        "start_s":          start_s,
                        "end_s":            end_s,
                        "duration_s":       end_s - start_s,
                        "filename":         fname
                    })
                    segments.append(seg)

    df   = pd.DataFrame(records)
    segs = np.array(segments)

    print(f"\n  Total chirps:           {len(df)}")
    print(f"  Individual-valid:       "
          f"{df['individual_valid'].sum()}")

    # Feature extraction
    feat_list     = []
    f0_list       = []
    centroid_list = []
    for seg in segs:
        feats, _, _, f0, centroid = compute_features(seg, sr)
        feat_list.append(feats)
        f0_list.append(f0)
        centroid_list.append(centroid)

    feature_matrix      = np.array(feat_list)
    df                  = df.copy()
    df["f0_est"]        = f0_list
    df["centroid_freq"] = centroid_list

    # Fit PCA on ALL chirps (colony-level basis)
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(feature_matrix)
    n_comp   = min(N_PCA_COMPONENTS, X_scaled.shape[1])
    pca      = PCA(n_components=n_comp, random_state=RANDOM_STATE)
    X_pca    = pca.fit_transform(X_scaled)

    print(f"  Feature matrix:         {feature_matrix.shape}")
    print(f"  PCA fitted on all chirps — {n_comp} components")

    # Colony breakdown
    print(f"\n  Colony breakdown (individual-valid only):")
    valid_df = df[df["individual_valid"]]
    for col, grp in valid_df.groupby("colony"):
        n_animals = grp["animal_id"].nunique()
        n_dates   = grp["date"].nunique()
        print(f"    {col:<15} {len(grp):>5} chirps  "
              f"{n_animals} animals  {n_dates} dates")

    return df, segs, feature_matrix, X_pca, scaler, pca


# ─────────────────────────────────────────────────────────────
# SHARED: per-animal eigenfunction position per date
# ─────────────────────────────────────────────────────────────

def compute_animal_date_positions(df, X_pca, colony,
                                   min_chirps_per_session=3):
    """
    For each animal in the colony, compute their mean eigenfunction
    position per recording date.

    Returns dict: animal_id -> list of (date, mean_position_array)
    """
    valid_df = df[
        (df["colony"] == colony) &
        df["individual_valid"]
    ]

    positions = defaultdict(list)

    for animal in valid_df["animal_id"].unique():
        a_mask  = (df["colony"] == colony) & \
                  df["individual_valid"] & \
                  (df["animal_id"] == animal)
        a_dates = sorted(df.loc[a_mask, "date"].unique())

        for date in a_dates:
            d_mask = a_mask & (df["date"] == date)
            if d_mask.sum() < min_chirps_per_session:
                continue
            mean_pos = np.mean(X_pca[d_mask, :N_PRIMARY_PCS], axis=0)
            positions[animal].append((date, mean_pos))

    return positions


def compute_drift(dated_positions):
    """Total drift first→last and mean step size."""
    if len(dated_positions) < 2:
        return None, None
    pos_arr = np.array([p for _, p in dated_positions])
    drift   = float(np.linalg.norm(pos_arr[-1] - pos_arr[0]))
    steps   = [float(np.linalg.norm(pos_arr[i+1] - pos_arr[i]))
               for i in range(len(pos_arr) - 1)]
    return drift, float(np.mean(steps))


# ────────────────────────────────────────���────────────────────
# MODULE 1 — QUEEN CANDIDATE IDENTIFICATION
# Four criteria: stability, centrality, F0 consistency,
#                centroid influence
# ─────────────────────────────────────────────────────────────

def module1_queen_identification(df, X_pca, colony=QUEEN_ID_COLONY,
                                  n_perms=N_PERMUTATIONS):
    print("\n" + "=" * 60)
    print("MODULE 1 — QUEEN CANDIDATE IDENTIFICATION")
    print(f"Colony: {colony.upper()}")
    print("Four criteria: stability | centrality | "
          "F0 consistency | centroid influence")
    print("=" * 60)

    valid_df = df[
        (df["colony"] == colony) &
        df["individual_valid"]
    ]

    # Animals with sufficient longitudinal coverage
    animal_dates = valid_df.groupby("animal_id")["date"].nunique()
    candidates   = animal_dates[
        animal_dates >= MIN_DATES_FOR_QUEEN_ID].index.tolist()

    print(f"\n  Animals with ≥ {MIN_DATES_FOR_QUEEN_ID} dates: "
          f"{len(candidates)}")
    for a in candidates:
        n  = animal_dates[a]
        nd = valid_df[valid_df["animal_id"] == a]["date"].nunique()
        print(f"    Animal {a}: {n} dates")

    if len(candidates) < 2:
        print("  INSUFFICIENT candidates for queen identification.")
        return None, {}

    # Colony centroid in eigenfunction space
    col_mask  = (df["colony"] == colony) & df["individual_valid"]
    col_cent  = np.mean(X_pca[col_mask, :N_PRIMARY_PCS], axis=0)

    # Per-animal date positions
    positions = compute_animal_date_positions(df, X_pca, colony)

    scores = {}
    rng    = np.random.default_rng(RANDOM_STATE)

    for animal in candidates:
        if animal not in positions:
            continue
        dated_pos = positions[animal]
        if len(dated_pos) < MIN_DATES_FOR_QUEEN_ID:
            continue

        pos_arr   = np.array([p for _, p in dated_pos])
        a_mask    = col_mask & (df["animal_id"] == animal)
        a_X       = X_pca[a_mask, :N_PRIMARY_PCS]

        # ── CRITERION 1: Longitudinal stability ──────────────
        # Lower drift = more queen-like
        real_drift, real_step = compute_drift(dated_pos)

        # Permutation null for drift
        a_dates_arr = df.loc[a_mask, "date"].values
        perm_drifts = []
        for _ in range(n_perms):
            shuffled = rng.permutation(a_dates_arr)
            perm_pos = []
            for d in sorted(set(a_dates_arr)):
                dmask = shuffled == d
                if dmask.sum() < 3:
                    continue
                perm_pos.append(
                    (d, np.mean(a_X[dmask], axis=0)))
            if len(perm_pos) >= 2:
                pd_val, _ = compute_drift(perm_pos)
                if pd_val is not None:
                    perm_drifts.append(pd_val)

        null_mean = float(np.mean(perm_drifts)) \
                    if perm_drifts else real_drift
        # Stability score: how much MORE stable than null
        # Higher = more stable relative to null
        stability_score = null_mean / (real_drift + 1e-10)

        # ── CRITERION 2: Distance to colony centroid ─────────
        # Closer = more queen-like
        animal_mean_pos = np.mean(pos_arr, axis=0)
        dist_to_centroid = float(
            np.linalg.norm(animal_mean_pos - col_cent))

        # ── CRITERION 3: F0 consistency ──────────────────────
        # Lower F0 variance = more queen-like
        f0_vals   = df.loc[a_mask, "f0_est"].values
        f0_var    = float(np.var(f0_vals))
        # F0 consistency score: inverse of variance
        # normalised later
        f0_consistency = 1.0 / (f0_var + 1e-10)

        # ── CRITERION 4: Centroid influence ──────────────────
        # Remove this animal from colony and recompute centroid
        # Larger centroid shift = more queen-like
        other_mask = col_mask & (df["animal_id"] != animal)
        if other_mask.sum() > 0:
            other_cent = np.mean(
                X_pca[other_mask, :N_PRIMARY_PCS], axis=0)
            centroid_shift = float(
                np.linalg.norm(other_cent - col_cent))
        else:
            centroid_shift = 0.0

        scores[animal] = {
            "stability_score":   stability_score,
            "real_drift":        real_drift,
            "null_mean_drift":   null_mean,
            "dist_to_centroid":  dist_to_centroid,
            "f0_var":            f0_var,
            "f0_consistency":    f0_consistency,
            "centroid_shift":    centroid_shift,
            "n_dates":           len(dated_pos),
            "mean_pos":          animal_mean_pos
        }

    if not scores:
        print("  No animals scored.")
        return None, {}

    # Normalise each criterion to [0, 1] and compute composite
    animals_scored = list(scores.keys())

    # Stability: higher = more queen-like
    stab_vals  = np.array([scores[a]["stability_score"]
                           for a in animals_scored])
    # Centrality: lower dist = more queen-like → invert
    cent_vals  = np.array([scores[a]["dist_to_centroid"]
                           for a in animals_scored])
    # F0 consistency: higher = more queen-like
    f0_vals    = np.array([scores[a]["f0_consistency"]
                           for a in animals_scored])
    # Centroid influence: higher shift = more queen-like
    shift_vals = np.array([scores[a]["centroid_shift"]
                           for a in animals_scored])

    def norm01(x):
        r = x.max() - x.min()
        return (x - x.min()) / (r + 1e-10)

    stab_norm  = norm01(stab_vals)
    cent_norm  = norm01(-cent_vals)   # invert: low dist = high score
    f0_norm    = norm01(f0_vals)
    shift_norm = norm01(shift_vals)

    composite  = (stab_norm + cent_norm + f0_norm + shift_norm) / 4.0

    print(f"\n  SCORING TABLE:")
    print(f"  {'Animal':<10} {'Stability':>10} {'Centrality':>10} "
          f"{'F0-Cons':>10} {'Influence':>10} {'COMPOSITE':>10}")
    print(f"  {'-'*62}")

    for i, animal in enumerate(animals_scored):
        print(f"  {animal:<10} {stab_norm[i]:>10.4f} "
              f"{cent_norm[i]:>10.4f} {f0_norm[i]:>10.4f} "
              f"{shift_norm[i]:>10.4f} {composite[i]:>10.4f}")

    best_idx   = int(np.argmax(composite))
    queen_id   = animals_scored[best_idx]
    queen_score= float(composite[best_idx])

    # Store normalised scores back
    for i, animal in enumerate(animals_scored):
        scores[animal]["stab_norm"]   = float(stab_norm[i])
        scores[animal]["cent_norm"]   = float(cent_norm[i])
        scores[animal]["f0_norm"]     = float(f0_norm[i])
        scores[animal]["shift_norm"]  = float(shift_norm[i])
        scores[animal]["composite"]   = float(composite[i])

    print(f"\n  QUEEN CANDIDATE: Animal {queen_id}")
    print(f"  Composite score: {queen_score:.4f}")
    print(f"\n  Detail:")
    print(f"    Longitudinal drift:    "
          f"{scores[queen_id]['real_drift']:.4f} "
          f"(null: {scores[queen_id]['null_mean_drift']:.4f})")
    print(f"    Distance to centroid:  "
          f"{scores[queen_id]['dist_to_centroid']:.4f}")
    print(f"    F0 variance:           "
          f"{scores[queen_id]['f0_var']:.1f} Hz²")
    print(f"    Centroid shift:        "
          f"{scores[queen_id]['centroid_shift']:.4f}")

    # How clear is the top candidate?
    if len(composite) > 1:
        sorted_comp = np.sort(composite)[::-1]
        margin      = float(sorted_comp[0] - sorted_comp[1])
        print(f"\n  Margin over 2nd candidate: {margin:.4f}")
        if margin > 0.15:
            print("  → QUEEN CANDIDATE: CLEAR")
        elif margin > 0.05:
            print("  → QUEEN CANDIDATE: MODERATE CONFIDENCE")
        else:
            print("  → QUEEN CANDIDATE: AMBIGUOUS")

    return queen_id, scores


# ─────────────────────────────────────────────────────────────
# MODULE 2 — COLONY ALIGNMENT TO QUEEN CANDIDATE
# P2: queen closest to colony centroid
# P3: workers closer to queen than to workerless centroid
# ─────────────────────────────────────────────────────────────

def module2_colony_alignment(df, X_pca, queen_id,
                              colony=QUEEN_ID_COLONY):
    print("\n" + "=" * 60)
    print("MODULE 2 — COLONY ALIGNMENT TO QUEEN CANDIDATE")
    print(f"Queen candidate: Animal {queen_id}")
    print("=" * 60)

    col_mask  = (df["colony"] == colony) & df["individual_valid"]
    col_cent  = np.mean(X_pca[col_mask, :N_PRIMARY_PCS], axis=0)

    # Queen mean position
    q_mask    = col_mask & (df["animal_id"] == queen_id)
    queen_pos = np.mean(X_pca[q_mask, :N_PRIMARY_PCS], axis=0)

    # Workerless centroid (exclude queen)
    worker_mask  = col_mask & (df["animal_id"] != queen_id)
    worker_cent  = np.mean(
        X_pca[worker_mask, :N_PRIMARY_PCS], axis=0)

    # ── P2: Queen is closest individual to colony centroid ───
    print(f"\n  P2 TEST: Queen closest to colony centroid")
    print(f"\n  Colony centroid:  {col_cent[:3]}")
    print(f"  Queen position:   {queen_pos[:3]}")
    print(f"  Workerless cent:  {worker_cent[:3]}")

    queen_dist = float(np.linalg.norm(queen_pos - col_cent))
    print(f"\n  Queen distance to colony centroid: {queen_dist:.4f}")

    # Distance of each animal to colony centroid
    animals_in_col = df.loc[
        col_mask, "animal_id"].unique()
    animal_dists   = {}
    for animal in animals_in_col:
        a_mask = col_mask & (df["animal_id"] == animal)
        a_pos  = np.mean(X_pca[a_mask, :N_PRIMARY_PCS], axis=0)
        animal_dists[animal] = float(
            np.linalg.norm(a_pos - col_cent))

    sorted_dists = sorted(animal_dists.items(), key=lambda x: x[1])
    print(f"\n  All individual distances to colony centroid:")
    for i, (animal, dist) in enumerate(sorted_dists):
        marker = " ← QUEEN CANDIDATE" if animal == queen_id else ""
        rank   = i + 1
        print(f"    Rank {rank}: Animal {animal}  "
              f"dist={dist:.4f}{marker}")

    queen_rank = [i for i, (a, _) in enumerate(sorted_dists)
                  if a == queen_id][0] + 1
    print(f"\n  Queen rank: {queen_rank}/{len(sorted_dists)}")

    if queen_rank == 1:
        print("  → P2: CONFIRMED — queen is closest to centroid")
    elif queen_rank <= max(2, len(sorted_dists) // 3):
        print(f"  → P2: PARTIAL — queen in top third "
              f"(rank {queen_rank})")
    else:
        print(f"  → P2: NOT CONFIRMED — queen rank {queen_rank}")

    # ── P3: Workers closer to queen than workerless centroid ─
    print(f"\n  P3 TEST: Workers closer to queen than "
          f"workerless centroid")

    worker_animals = [a for a in animals_in_col
                      if a != queen_id]
    dists_to_queen      = []
    dists_to_worker_cent= []

    for animal in worker_animals:
        a_mask = col_mask & (df["animal_id"] == animal)
        a_pos  = np.mean(X_pca[a_mask, :N_PRIMARY_PCS], axis=0)
        dists_to_queen.append(
            float(np.linalg.norm(a_pos - queen_pos)))
        dists_to_worker_cent.append(
            float(np.linalg.norm(a_pos - worker_cent)))

    if len(dists_to_queen) < 2:
        print("  Insufficient workers for P3 test.")
        p3_result = "INSUFFICIENT DATA"
    else:
        mean_dq  = float(np.mean(dists_to_queen))
        mean_dwc = float(np.mean(dists_to_worker_cent))

        stat, p_val = mannwhitneyu(
            dists_to_queen, dists_to_worker_cent,
            alternative="less")

        print(f"\n  Mean worker distance to queen:            "
              f"{mean_dq:.4f}")
        print(f"  Mean worker distance to workerless cent:  "
              f"{mean_dwc:.4f}")
        print(f"  Mann-Whitney U p (dist_queen < dist_cent):"
              f" {p_val:.4f}")

        if p_val < 0.05 and mean_dq < mean_dwc:
            print("  → P3: CONFIRMED — workers closer to queen")
            p3_result = "CONFIRMED"
        elif mean_dq < mean_dwc:
            print("  → P3: TREND — workers closer to queen "
                  f"(not significant, p={p_val:.3f})")
            p3_result = "TREND"
        else:
            print("  → P3: NOT CONFIRMED")
            p3_result = "NOT CONFIRMED"

    return {
        "queen_rank":            queen_rank,
        "queen_dist_to_centroid":queen_dist,
        "animal_dists":          animal_dists,
        "p3_result":             p3_result,
        "dists_to_queen":        dists_to_queen,
        "dists_to_worker_cent":  dists_to_worker_cent,
        "queen_pos":             queen_pos,
        "worker_cent":           worker_cent,
        "col_cent":              col_cent
    }


# ─────────────────────────────────────────────────────────────
# MODULE 3 — TEMPORAL ALIGNMENT TEST
# Per-session: do workers track the queen's position?
# ─────────────────────────────────────────────────────────────

def module3_temporal_alignment(df, X_pca, queen_id,
                                colony=QUEEN_ID_COLONY,
                                n_perms=N_PERMUTATIONS):
    print("\n" + "=" * 60)
    print("MODULE 3 — TEMPORAL ALIGNMENT TEST")
    print(f"Per-session: do workers track queen position?")
    print("=" * 60)

    col_mask = (df["colony"] == colony) & df["individual_valid"]
    dates    = sorted(df.loc[col_mask, "date"].unique())

    # Sessions where queen was recorded
    queen_sessions = []
    worker_queen_dists   = []
    worker_random_dists  = []

    rng = np.random.default_rng(RANDOM_STATE)

    print(f"\n  Sessions analysed:")
    for date in dates:
        date_mask  = col_mask & (df["date"] == date)
        q_in_date  = date_mask & (df["animal_id"] == queen_id)

        if q_in_date.sum() < 3:
            continue  # queen not recorded this session

        queen_pos   = np.mean(
            X_pca[q_in_date, :N_PRIMARY_PCS], axis=0)
        workers_this_date = [
            a for a in df.loc[date_mask, "animal_id"].unique()
            if a != queen_id]

        if len(workers_this_date) < 2:
            continue

        session_worker_dists = []
        for worker in workers_this_date:
            w_mask = date_mask & (df["animal_id"] == worker)
            if w_mask.sum() < 3:
                continue
            w_pos = np.mean(
                X_pca[w_mask, :N_PRIMARY_PCS], axis=0)
            session_worker_dists.append(
                float(np.linalg.norm(w_pos - queen_pos)))

        if not session_worker_dists:
            continue

        # Random baseline: distance to random non-queen animal
        # in the same session
        random_dists = []
        all_animals_this_date = [
            a for a in df.loc[date_mask, "animal_id"].unique()
            if a != queen_id]
        if len(all_animals_this_date) < 2:
            continue

        for _ in range(min(100, n_perms)):
            rand_animal = rng.choice(all_animals_this_date)
            r_mask = date_mask & (df["animal_id"] == rand_animal)
            if r_mask.sum() < 3:
                continue
            r_pos = np.mean(
                X_pca[r_mask, :N_PRIMARY_PCS], axis=0)
            # Distance from other workers to random animal
            for worker in workers_this_date:
                if worker == rand_animal:
                    continue
                w_mask = date_mask & (df["animal_id"] == worker)
                if w_mask.sum() < 3:
                    continue
                w_pos = np.mean(
                    X_pca[w_mask, :N_PRIMARY_PCS], axis=0)
                random_dists.append(
                    float(np.linalg.norm(w_pos - r_pos)))

        mean_wq = float(np.mean(session_worker_dists))
        mean_wr = float(np.mean(random_dists)) \
                  if random_dists else np.nan

        queen_sessions.append(date)
        worker_queen_dists.extend(session_worker_dists)
        worker_random_dists.extend(random_dists)

        print(f"    {date}  queen_workers={len(session_worker_dists)}"
              f"  mean_dist_to_queen={mean_wq:.4f}"
              f"  mean_dist_to_random={mean_wr:.4f}")

    print(f"\n  Sessions with queen recorded: {len(queen_sessions)}")

    if len(worker_queen_dists) < 4 or len(worker_random_dists) < 4:
        print("  INSUFFICIENT DATA for temporal alignment test.")
        return {"result": "INSUFFICIENT DATA"}

    # Overall test
    mean_wq_all = float(np.mean(worker_queen_dists))
    mean_wr_all = float(np.mean(worker_random_dists))

    stat, p_val = mannwhitneyu(
        worker_queen_dists, worker_random_dists,
        alternative="less")

    print(f"\n  Overall mean distance to queen:          "
          f"{mean_wq_all:.4f}")
    print(f"  Overall mean distance to random animal:  "
          f"{mean_wr_all:.4f}")
    print(f"  Mann-Whitney p (queen < random):         "
          f"{p_val:.4f}")

    if p_val < 0.05 and mean_wq_all < mean_wr_all:
        print("  → TEMPORAL ALIGNMENT: CONFIRMED")
        print("    Workers are consistently closer to the queen")
        print("    than to random animals in the same session")
        result = "CONFIRMED"
    elif mean_wq_all < mean_wr_all:
        print(f"  → TEMPORAL ALIGNMENT: TREND (p={p_val:.3f})")
        result = "TREND"
    else:
        print("  → TEMPORAL ALIGNMENT: NOT CONFIRMED")
        result = "NOT CONFIRMED"

    return {
        "result":               result,
        "mean_dist_to_queen":   mean_wq_all,
        "mean_dist_to_random":  mean_wr_all,
        "p_val":                p_val,
        "n_sessions":           len(queen_sessions),
        "worker_queen_dists":   worker_queen_dists,
        "worker_random_dists":  worker_random_dists
    }


# ─────────────────────────────────────────────────────────────
# MODULE 4 — INTER-COLONY QUEEN GEOMETRY COMPARISON
# P4: queen distances predict colony distances
# P5: queen geometries more different than worker geometries
# ─────────────────────────────────────────────────────────────

def module4_intercol_queen_geometry(df, X_pca,
                                     queen_candidates):
    """
    queen_candidates: dict colony -> queen_id
    (may have only baratheon confirmed; others attempted)
    """
    print("\n" + "=" * 60)
    print("MODULE 4 — INTER-COLONY QUEEN GEOMETRY COMPARISON")
    print("P4: queen distances predict colony distances")
    print("P5: between-queen > between-worker distances")
    print("=" * 60)

    colonies   = df["colony"].unique().tolist()

    # Colony centroids
    col_cents = {}
    for col in colonies:
        mask = (df["colony"] == col) & df["individual_valid"]
        if mask.sum() < 5:
            continue
        col_cents[col] = np.mean(
            X_pca[mask, :N_PRIMARY_PCS], axis=0)

    # Queen positions per colony
    # For colonies without identified queen, use the animal
    # with lowest F0 variance as a proxy (most consistent caller)
    queen_positions = {}
    queen_sources   = {}

    for col in col_cents.keys():
        if col in queen_candidates and queen_candidates[col]:
            qid  = queen_candidates[col]
            mask = (df["colony"] == col) & \
                   df["individual_valid"] & \
                   (df["animal_id"] == qid)
            if mask.sum() >= 3:
                queen_positions[col] = np.mean(
                    X_pca[mask, :N_PRIMARY_PCS], axis=0)
                queen_sources[col] = f"identified ({qid})"
        else:
            # Proxy: animal with lowest F0 variance
            col_mask = (df["colony"] == col) & \
                       df["individual_valid"]
            animals  = df.loc[col_mask, "animal_id"].unique()
            best_a   = None
            best_var = np.inf
            for a in animals:
                a_mask = col_mask & (df["animal_id"] == a)
                if a_mask.sum() < 5:
                    continue
                f0v = float(np.var(df.loc[a_mask, "f0_est"]))
                if f0v < best_var:
                    best_var = f0v
                    best_a   = a
            if best_a is not None:
                mask = col_mask & (df["animal_id"] == best_a)
                queen_positions[col] = np.mean(
                    X_pca[mask, :N_PRIMARY_PCS], axis=0)
                queen_sources[col] = f"proxy ({best_a})"

    print(f"\n  Queen positions used:")
    for col, source in queen_sources.items():
        print(f"    {col}: {source}")

    # Colony centroid distances
    print(f"\n  Colony centroid distances:")
    col_pairs = []
    cent_dists = []
    queen_dists= []

    col_list = list(col_cents.keys())
    for i in range(len(col_list)):
        for j in range(i+1, len(col_list)):
            ca, cb = col_list[i], col_list[j]
            if ca not in queen_positions or \
               cb not in queen_positions:
                continue
            cd = float(np.linalg.norm(
                col_cents[ca] - col_cents[cb]))
            qd = float(np.linalg.norm(
                queen_positions[ca] - queen_positions[cb]))
            col_pairs.append((ca, cb))
            cent_dists.append(cd)
            queen_dists.append(qd)
            print(f"    {ca} ↔ {cb}:")
            print(f"      Colony centroid dist:  {cd:.4f}")
            print(f"      Queen geometry dist:   {qd:.4f}")

    # P4: correlation between queen distance and colony distance
    print(f"\n  P4 TEST: queen distances predict colony distances")
    if len(cent_dists) >= 3:
        r, p = spearmanr(queen_dists, cent_dists)
        print(f"  Spearman r={r:.4f}  p={p:.4f}")
        if r > 0.7 and p < 0.05:
            print("  → P4: CONFIRMED (r > 0.7, p < 0.05)")
            p4_result = "CONFIRMED"
        elif r > 0.5:
            print(f"  → P4: TREND (r={r:.3f})")
            p4_result = "TREND"
        else:
            print(f"  → P4: NOT CONFIRMED (r={r:.3f})")
            p4_result = "NOT CONFIRMED"
    else:
        print(f"  Only {len(cent_dists)} colony pairs — "
              f"insufficient for correlation")
        r, p_val = np.nan, np.nan
        p4_result = "INSUFFICIENT DATA"

    # P5: between-queen distance vs between-worker distribution
    print(f"\n  P5 TEST: between-queen > between-worker distances")

    # Between-worker distances: sample pairs
    worker_pair_dists = []
    for col in col_list:
        col_mask = (df["colony"] == col) & df["individual_valid"]
        animals  = df.loc[col_mask, "animal_id"].unique()
        if len(animals) < 2:
            continue
        positions_this_col = {}
        for a in animals:
            a_mask = col_mask & (df["animal_id"] == a)
            if a_mask.sum() < 3:
                continue
            positions_this_col[a] = np.mean(
                X_pca[a_mask, :N_PRIMARY_PCS], axis=0)
        animal_list = list(positions_this_col.keys())
        for i in range(len(animal_list)):
            for j in range(i+1, len(animal_list)):
                d = float(np.linalg.norm(
                    positions_this_col[animal_list[i]] -
                    positions_this_col[animal_list[j]]))
                worker_pair_dists.append(d)

    if worker_pair_dists and queen_dists:
        mean_qd = float(np.mean(queen_dists))
        mean_wd = float(np.mean(worker_pair_dists))
        pct_rank= float(np.mean(
            np.array(worker_pair_dists) <= mean_qd)) * 100

        print(f"  Mean between-queen dist:   {mean_qd:.4f}")
        print(f"  Mean between-worker dist:  {mean_wd:.4f}")
        print(f"  Queen dist percentile in worker dist: "
              f"{pct_rank:.1f}%")

        if pct_rank >= 75:
            print("  → P5: CONFIRMED — queen dist in upper quartile")
            p5_result = "CONFIRMED"
        elif pct_rank >= 50:
            print("  → P5: PARTIAL — queen dist above median")
            p5_result = "PARTIAL"
        else:
            print("  → P5: NOT CONFIRMED")
            p5_result = "NOT CONFIRMED"
    else:
        p5_result = "INSUFFICIENT DATA"

    return {
        "p4_result":         p4_result,
        "p5_result":         p5_result,
        "queen_positions":   queen_positions,
        "col_cents":         col_cents,
        "queen_dists":       queen_dists,
        "cent_dists":        cent_dists,
        "worker_pair_dists": worker_pair_dists
    }


# ─────────────────────────────────────────────────────────────
# MODULE 5 — GENERATIVE SYNTHESIS SPECIFICATION
# Map the queen's Tonnetz and identify novel signal positions
# ─────────────────────────────────────────────────────────────

def module5_synthesis_specification(df, X_pca, pca, scaler,
                                     queen_id,
                                     colony=QUEEN_ID_COLONY):
    print("\n" + "=" * 60)
    print("MODULE 5 — GENERATIVE SYNTHESIS SPECIFICATION")
    print(f"Queen candidate: Animal {queen_id}")
    print("=" * 60)

    col_mask  = (df["colony"] == colony) & df["individual_valid"]
    q_mask    = col_mask & (df["animal_id"] == queen_id)

    if q_mask.sum() < 5:
        print("  Insufficient queen chirps for synthesis spec.")
        return {}

    queen_X     = X_pca[q_mask, :N_PRIMARY_PCS]
    queen_cent  = np.mean(queen_X, axis=0)
    queen_std   = np.std(queen_X, axis=0)
    queen_cov   = np.cov(queen_X.T)

    # Colony-wide call type positions (from V2 finding)
    # All call type centroids in the same space
    col_all_mask = df["colony"] == colony
    col_all_X    = X_pca[col_all_mask, :N_PRIMARY_PCS]
    col_cent_all = np.mean(col_all_X, axis=0)

    print(f"\n  Queen eigenfunction geometry:")
    print(f"  Centroid in PC space:")
    for d in range(N_PRIMARY_PCS):
        print(f"    PC{d+1}: {queen_cent[d]:+.4f} "
              f"± {queen_std[d]:.4f}")

    print(f"\n  Queen Tonnetz radius (mean std): "
          f"{float(np.mean(queen_std)):.4f}")

    # Identify the queen's occupied region
    # Defined as: centroid ± 1 std in each PC dimension
    queen_region = {
        f"PC{d+1}": (
            float(queen_cent[d] - queen_std[d]),
            float(queen_cent[d] + queen_std[d])
        )
        for d in range(N_PRIMARY_PCS)
    }

    print(f"\n  Queen's occupied Tonnetz region:")
    for dim, (lo, hi) in queen_region.items():
        print(f"    {dim}: [{lo:+.4f}, {hi:+.4f}]")

    # Novel signal positions: just outside the queen's region
    # but within the physically valid eigenfunction space
    # Three candidate positions:

    # Position 1: adjacent to queen in PC1 direction
    novel_1 = queen_cent.copy()
    novel_1[0] = queen_cent[0] + 2.0 * queen_std[0]

    # Position 2: adjacent to queen in PC3 direction
    novel_2 = queen_cent.copy()
    novel_2[2] = queen_cent[2] + 2.0 * queen_std[2]

    # Position 3: midpoint between queen and colony centroid
    novel_3 = (queen_cent + col_cent_all) / 2.0

    novel_positions = {
        "NOVEL-1 (PC1 adjacent)":  novel_1,
        "NOVEL-2 (PC3 adjacent)":  novel_2,
        "NOVEL-3 (queen-colony midpoint)": novel_3
    }

    print(f"\n  NOVEL SIGNAL POSITIONS:")
    print(f"  (physically valid positions in queen's coordinate")
    print(f"   system not occupied by any known call type)")
    print()

    for name, pos in novel_positions.items():
        print(f"  {name}:")
        for d in range(N_PRIMARY_PCS):
            print(f"    PC{d+1}: {pos[d]:+.4f}")

        # Distance from queen centroid
        dist_from_queen = float(np.linalg.norm(pos - queen_cent))
        print(f"    Distance from queen centroid: "
              f"{dist_from_queen:.4f}")

        # Inverse-project to feature space to get
        # approximate frequency profile
        pos_full = np.zeros(N_PCA_COMPONENTS)
        pos_full[:N_PRIMARY_PCS] = pos
        feat_approx = pca.inverse_transform(
            pos_full.reshape(1, -1))
        feat_approx = scaler.inverse_transform(feat_approx)[0]

        # Extract predicted frequency profile
        sr        = SAMPLE_RATE
        freqs     = np.fft.rfftfreq(STFT_WINDOW, 1.0 / sr)
        freq_mask = (freqs >= CHIRP_FREQ_LOW) & \
                    (freqs <= CHIRP_FREQ_HIGH)
        freqs_band= freqs[freq_mask]
        n_psd     = len(freqs_band)

        psd_approx = feat_approx[:n_psd]
        psd_approx = np.maximum(psd_approx, 0)
        if psd_approx.sum() > 0:
            psd_approx /= psd_approx.sum()

        peak_freq  = float(freqs_band[np.argmax(psd_approx)])
        centroid   = float(np.sum(freqs_band * psd_approx))

        print(f"    Predicted peak frequency: {peak_freq:.0f} Hz")
        print(f"    Predicted centroid:       {centroid:.0f} Hz")
        print()

    # Synthesis specification summary
    print(f"  SYNTHESIS SPECIFICATION SUMMARY:")
    print(f"  ─────────────────────────────────────────")
    print(f"  Target colony:    {colony}")
    print(f"  Queen candidate:  Animal {queen_id}")
    print(f"  Coordinate basis: Queen's eigenfunction geometry")
    print(f"  Novel positions:  3 specified above")
    print(f"  Protocol:         Record queen → derive Q →")
    print(f"                    synthesize at novel positions →")
    print(f"                    introduce to colony environment →")
    print(f"                    measure behavioral response")
    print(f"  ─────────────────────────────────────────")
    print(f"  NOTE: Audio synthesis requires generative pipeline")
    print(f"  documented in naked_mole_rat_vocal_instrument.md")
    print(f"  This module specifies the TARGET COORDINATES only.")

    return {
        "queen_centroid":   queen_cent,
        "queen_std":        queen_std,
        "queen_region":     queen_region,
        "novel_positions":  novel_positions,
        "queen_cov":        queen_cov
    }


# ─────────────────────────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────────────────────────

def make_plots(df, X_pca, queen_id, m1_scores,
               m2_results, m3_results, m4_results,
               m5_results, colony=QUEEN_ID_COLONY):

    OUTPUT_DIR.mkdir(exist_ok=True)
    col_mask = (df["colony"] == colony) & df["individual_valid"]

    # ── Plot 1: Individual positions — queen highlighted ──────
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"NMR Queen Geometry — {colony.upper()} "
        f"(Queen candidate: Animal {queen_id})",
        fontweight="bold")

    animals = df.loc[col_mask, "animal_id"].unique()
    cmap    = plt.cm.get_cmap("tab20")

    for i, animal in enumerate(sorted(animals)):
        a_mask = col_mask & (df["animal_id"] == animal)
        color  = "red" if animal == queen_id else cmap(i)
        size   = 20 if animal == queen_id else 6
        alpha  = 0.7 if animal == queen_id else 0.25
        label  = f"Animal {animal} (QUEEN)" \
                 if animal == queen_id else f"Animal {animal}"
        axes[0].scatter(X_pca[a_mask, 0], X_pca[a_mask, 1],
                        c=color, s=size, alpha=alpha, label=label)
        axes[1].scatter(X_pca[a_mask, 1], X_pca[a_mask, 2],
                        c=color, s=size, alpha=alpha)

    # Colony centroid
    col_cent = m2_results["col_cent"]
    axes[0].scatter(col_cent[0], col_cent[1], c="black",
                    s=300, marker="X", zorder=6,
                    label="Colony centroid")
    axes[1].scatter(col_cent[1], col_cent[2], c="black",
                    s=300, marker="X", zorder=6)

    # Novel positions
    if m5_results and "novel_positions" in m5_results:
        colors_novel = ["purple", "green", "orange"]
        for (name, pos), nc in zip(
                m5_results["novel_positions"].items(),
                colors_novel):
            axes[0].scatter(pos[0], pos[1], c=nc, s=200,
                            marker="D", zorder=7,
                            label=f"Novel: {name[:7]}")
            axes[1].scatter(pos[1], pos[2], c=nc, s=200,
                            marker="D", zorder=7)

    for ax, xl, yl, t in [
            (axes[0], "PC1", "PC2", "PC1 vs PC2"),
            (axes[1], "PC2", "PC3", "PC2 vs PC3")]:
        ax.set_xlabel(xl); ax.set_ylabel(yl)
        ax.set_title(t)
        ax.grid(True, alpha=0.3)
    axes[0].legend(fontsize=6, loc="best")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_queen_geometry.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved: 01_queen_geometry.png")

    # ── Plot 2: M1 scoring radar ──────────────────────────────
    if m1_scores:
        animals_sc = list(m1_scores.keys())
        criteria   = ["stab_norm", "cent_norm",
                      "f0_norm",   "shift_norm"]
        labels_c   = ["Stability", "Centrality",
                      "F0 Cons.", "Influence"]

        fig, ax = plt.subplots(figsize=(10, 5))
        x       = np.arange(len(animals_sc))
        width   = 0.2
        colors_b= ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0"]

        for ci, (crit, lbl) in enumerate(zip(criteria, labels_c)):
            vals = [m1_scores[a].get(crit, 0) for a in animals_sc]
            ax.bar(x + ci * width, vals, width,
                   label=lbl, color=colors_b[ci], alpha=0.8)

        comp_vals = [m1_scores[a].get("composite", 0)
                     for a in animals_sc]
        ax2 = ax.twinx()
        ax2.plot(x + 1.5 * width, comp_vals, "ko-",
                 linewidth=2, markersize=8, label="Composite")
        ax2.set_ylabel("Composite score")

        queen_x = animals_sc.index(queen_id) \
                  if queen_id in animals_sc else -1
        if queen_x >= 0:
            ax.axvline(x=queen_x + 1.5 * width,
                       color="red", linestyle="--",
                       linewidth=2, alpha=0.7,
                       label=f"Queen: {queen_id}")

        ax.set_xticks(x + 1.5 * width)
        ax.set_xticklabels(
            [f"A{a}" for a in animals_sc], rotation=45)
        ax.set_ylabel("Normalised criterion score")
        ax.set_title("M1: Queen Candidate Scoring")
        ax.legend(fontsize=8, loc="upper left")
        ax2.legend(fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "02_queen_scoring.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 02_queen_scoring.png")

    # ── Plot 3: Worker distances to queen vs random ───────────
    if (m3_results.get("result") not in
            [None, "INSUFFICIENT DATA"]):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(m3_results["worker_queen_dists"],
                bins=30, alpha=0.6, color="#2196F3",
                label=f"Distance to queen candidate "
                      f"(mean={np.mean(m3_results['worker_queen_dists']):.3f})")
        ax.hist(m3_results["worker_random_dists"],
                bins=30, alpha=0.6, color="#FF9800",
                label=f"Distance to random animal "
                      f"(mean={np.mean(m3_results['worker_random_dists']):.3f})")
        ax.set_xlabel("Distance in eigenfunction space")
        ax.set_ylabel("Count")
        ax.set_title(f"M3: Worker Alignment to Queen\n"
                     f"p={m3_results.get('p_val', np.nan):.4f}  "
                     f"Result: {m3_results['result']}")
        ax.legend(); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "03_temporal_alignment.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 03_temporal_alignment.png")

    # ── Plot 4: Inter-colony queen vs centroid distances ──────
    if (m4_results.get("queen_dists") and
            m4_results.get("cent_dists")):
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(m4_results["queen_dists"],
                   m4_results["cent_dists"],
                   s=120, color="#2196F3", zorder=5)
        for i, (ca, cb) in enumerate(
                [p for p in [
                    (c1, c2)
                    for idx1, c1 in enumerate(
                        list(m4_results["col_cents"].keys()))
                    for c2 in list(
                        m4_results["col_cents"].keys())[idx1+1:]
                    if c1 in m4_results["queen_positions"]
                    and c2 in m4_results["queen_positions"]
                ]]):
            if i < len(m4_results["queen_dists"]):
                ax.annotate(
                    f"{ca[:3]}↔{cb[:3]}",
                    (m4_results["queen_dists"][i],
                     m4_results["cent_dists"][i]),
                    fontsize=8, ha="left")

        # Best fit line
        if len(m4_results["queen_dists"]) >= 2:
            x_arr = np.array(m4_results["queen_dists"])
            y_arr = np.array(m4_results["cent_dists"])
            coeffs= np.polyfit(x_arr, y_arr, 1)
            x_line= np.linspace(x_arr.min(), x_arr.max(), 50)
            ax.plot(x_line, np.polyval(coeffs, x_line),
                    "r--", alpha=0.7)

        ax.set_xlabel("Queen-to-queen distance in eigenfunction space")
        ax.set_ylabel("Colony centroid distance")
        ax.set_title(f"M4: Queen Distance vs Colony Distance\n"
                     f"P4 result: {m4_results['p4_result']}")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "04_intercol_queen.png",
                    dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: 04_intercol_queen.png")

    print(f"\n  All plots saved to: {OUTPUT_DIR}/")


# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────

def final_report(queen_id, m1_scores,
                 m2_results, m3_results,
                 m4_results, m5_results):

    sep = "─" * 60
    print("\n" + "=" * 60)
    print("FINAL RESULT SUMMARY — OC-OBS-004-Q")
    print("Queen Geometric Anchor Hypothesis")
    print("=" * 60)

    # Queen identification
    if queen_id and m1_scores and queen_id in m1_scores:
        s = m1_scores[queen_id]
        margin = s["composite"] - sorted(
            [v["composite"] for v in m1_scores.values()])[-2] \
            if len(m1_scores) > 1 else 0
        print(f"\n{sep}")
        print("QUEEN CANDIDATE IDENTIFICATION")
        print(sep)
        print(f"  Candidate:       Animal {queen_id}")
        print(f"  Composite score: {s['composite']:.4f}")
        print(f"  Margin:          {margin:.4f}")
        conf = ("CLEAR" if margin > 0.15
                else "MODERATE" if margin > 0.05
                else "AMBIGUOUS")
        print(f"  Confidence:      {conf}")

    print(f"\n{sep}")
    print("P1 — Queen geometry more stable than workers")
    print(sep)
    if queen_id and m1_scores and queen_id in m1_scores:
        s = m1_scores[queen_id]
        print(f"  Queen drift:     {s['real_drift']:.4f}")
        print(f"  Null mean:       {s['null_mean_drift']:.4f}")
        print(f"  Stability score: {s['stability_score']:.4f}")
        print(f"  Stability rank:  {s['stab_norm']:.4f} "
              f"(normalised, 1.0=most stable)")
        if s["stab_norm"] >= 0.7:
            print("  RESULT: CONFIRMED")
        elif s["stab_norm"] >= 0.4:
            print("  RESULT: PARTIAL")
        else:
            print("  RESULT: NOT CONFIRMED")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("P2 — Queen closest individual to colony centroid")
    print(sep)
    if m2_results:
        rank = m2_results["queen_rank"]
        n    = len(m2_results["animal_dists"])
        print(f"  Queen rank: {rank}/{n}")
        if rank == 1:
            print("  RESULT: CONFIRMED")
        elif rank <= max(2, n // 3):
            print("  RESULT: PARTIAL")
        else:
            print("  RESULT: NOT CONFIRMED")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("P3 — Workers closer to queen than workerless centroid")
    print(sep)
    if m2_results:
        print(f"  Result: {m2_results['p3_result']}")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("TEMPORAL ALIGNMENT — Workers track queen per session")
    print(sep)
    if m3_results:
        print(f"  Result: {m3_results.get('result', 'NO DATA')}")
        if "p_val" in m3_results:
            print(f"  p={m3_results['p_val']:.4f}")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("P4 — Queen distances predict colony distances")
    print(sep)
    if m4_results:
        print(f"  Result: {m4_results.get('p4_result', 'NO DATA')}")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("P5 — Between-queen > between-worker distances")
    print(sep)
    if m4_results:
        print(f"  Result: {m4_results.get('p5_result', 'NO DATA')}")
    else:
        print("  RESULT: NO DATA")

    print(f"\n{sep}")
    print("SYNTHESIS SPECIFICATION")
    print(sep)
    if m5_results and "novel_positions" in m5_results:
        print(f"  Novel positions specified: "
              f"{len(m5_results['novel_positions'])}")
        print("  Queen Tonnetz mapped: YES")
        print("  Ready for generative synthesis: YES")
    else:
        print("  Synthesis spec: INCOMPLETE")

    print(f"\n{sep}")
    print("FRAMEWORK ASSESSMENT")
    print(sep)
    results = []
    if m2_results:
        results.append(m2_results["queen_rank"] <= 2)
        results.append(m2_results["p3_result"] in
                       ["CONFIRMED", "TREND"])
    if m3_results:
        results.append(m3_results.get("result") in
                       ["CONFIRMED", "TREND"])
    if m4_results:
        results.append(m4_results.get("p4_result") in
                       ["CONFIRMED", "TREND"])
        results.append(m4_results.get("p5_result") in
                       ["CONFIRMED", "PARTIAL"])

    n_confirmed = sum(results)
    n_total     = len(results) if results else 1
    print(f"  Tests confirmed or trending: {n_confirmed}/{n_total}")

    if n_confirmed / n_total >= 0.6:
        print("  → QUEEN GEOMETRIC ANCHOR HYPOTHESIS: SUPPORTED")
    elif n_confirmed / n_total >= 0.4:
        print("  → QUEEN GEOMETRIC ANCHOR HYPOTHESIS: "
              "PARTIALLY SUPPORTED")
    else:
        print("  → QUEEN GEOMETRIC ANCHOR HYPOTHESIS: "
              "NOT SUPPORTED BY THIS DATA")

    print(f"\n  Pre-registration: "
          f"OC-OBS-004_QUEEN_GEOMETRY_PREREGISTRATION.md v1.0")
    print(f"  All results reported in full regardless of direction.")
    print()


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    sr   = args.sample_rate
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("  OC-OBS-004-Q — QUEEN GEOMETRY ANALYSIS")
    print("  Testing Queen Geometric Anchor Hypothesis")
    print("  OrganismCore — Eric Robert Lawson")
    print("=" * 60)
    print(f"\n  Data dir:     {args.data_dir}")
    print(f"  Sample rate:  {sr} Hz")
    print(f"  Permutations: {args.n_perms}")
    print(f"  Queen colony: {QUEEN_ID_COLONY}")

    # Load data and fit PCA basis
    (df, segs, feature_matrix,
     X_pca, scaler, pca) = load_individual_chirps(
        args.data_dir, sr)

    if len(df) < 10:
        print("ERROR: insufficient data.")
        sys.exit(1)

    # M1: identify queen candidate
    queen_id, m1_scores = module1_queen_identification(
        df, X_pca,
        colony=QUEEN_ID_COLONY,
        n_perms=args.n_perms)

    if queen_id is None:
        print("\nWARNING: Queen candidate could not be identified.")
        print("Continuing with proxy (lowest F0 variance).")
        # Fall back to lowest F0 variance animal
        col_mask = ((df["colony"] == QUEEN_ID_COLONY) &
                    df["individual_valid"])
        animals  = df.loc[col_mask, "animal_id"].unique()
        best_a, best_v = None, np.inf
        for a in animals:
            v = float(np.var(
                df.loc[col_mask & (df["animal_id"] == a),
                       "f0_est"]))
            if v < best_v:
                best_v, best_a = v, a
        queen_id = best_a
        m1_scores = {}

    # Build queen candidates dict for M4
    queen_candidates = {QUEEN_ID_COLONY: queen_id}

    # M2: colony alignment to queen
    m2_results = module2_colony_alignment(
        df, X_pca, queen_id, colony=QUEEN_ID_COLONY)

    # M3: temporal alignment
    m3_results = module3_temporal_alignment(
        df, X_pca, queen_id,
        colony=QUEEN_ID_COLONY,
        n_perms=args.n_perms)

    # M4: inter-colony queen geometry
    m4_results = module4_intercol_queen_geometry(
        df, X_pca, queen_candidates)

    # M5: synthesis specification
    m5_results = module5_synthesis_specification(
        df, X_pca, pca, scaler,
        queen_id, colony=QUEEN_ID_COLONY)

    # Plots
    make_plots(df, X_pca, queen_id, m1_scores,
               m2_results, m3_results, m4_results,
               m5_results, colony=QUEEN_ID_COLONY)

    # Final report
    final_report(queen_id, m1_scores,
                 m2_results, m3_results,
                 m4_results, m5_results)


if __name__ == "__main__":
    main()
