import librosa
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# COCKATIEL SPECIES EIGENFUNCTION SPACE — V2
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
# F0 range corrected to fundamental only
# Duration filter tightened to contact calls
# ─────────────────────────────────────────────

CORPUS_DIR = os.path.join(os.path.dirname(__file__),
                           "audio_files")
SR          = 22050
N_MFCC      = 13
N_PCA       = 4
MIN_DUR_MS  = 100    # tightened — exclude noise bursts
MAX_DUR_MS  = 350    # tightened — exclude long song phrases
TOP_DB      = 25
F0_MIN      = 300    # Hz — true fundamental lower bound
F0_MAX      = 1200   # Hz — true fundamental upper bound
                     # Forces pyin to find F0, not harmonics


def extract_features(filepath):
    try:
        y, sr = librosa.load(filepath, sr=SR, mono=True)
    except Exception as e:
        print(f"  SKIP — could not load: {filepath}")
        print(f"         {e}")
        return []

    intervals = librosa.effects.split(
        y,
        top_db=TOP_DB,
        frame_length=512,
        hop_length=128
    )

    features = []
    for start, end in intervals:
        segment = y[start:end]
        duration_ms = len(segment) / SR * 1000

        if not (MIN_DUR_MS < duration_ms < MAX_DUR_MS):
            continue

        try:
            mfcc = librosa.feature.mfcc(
                y=segment, sr=SR, n_mfcc=N_MFCC)
            mfcc_mean = np.mean(mfcc, axis=1)
        except Exception:
            continue

        try:
            centroid = float(np.mean(
                librosa.feature.spectral_centroid(
                    y=segment, sr=SR)))
            bandwidth = float(np.mean(
                librosa.feature.spectral_bandwidth(
                    y=segment, sr=SR)))
            rolloff = float(np.mean(
                librosa.feature.spectral_rolloff(
                    y=segment, sr=SR, roll_percent=0.85)))
        except Exception:
            continue

        try:
            f0, voiced, _ = librosa.pyin(
                segment,
                fmin=F0_MIN,   # corrected — fundamental only
                fmax=F0_MAX,   # corrected — fundamental only
                sr=SR)
            if f0 is None or not np.any(voiced):
                continue
            f0_voiced = f0[voiced]
            f0_mean = float(np.nanmean(f0_voiced))
            if np.isnan(f0_mean) or f0_mean <= 0:
                continue
        except Exception:
            continue

        feature_vector = np.concatenate([
            mfcc_mean,
            [centroid, bandwidth, rolloff,
             f0_mean, duration_ms]
        ])

        features.append(feature_vector)

    return features


def build_species_eigenfunction_space(corpus_dir):
    all_features   = []
    files_processed = 0
    files_skipped   = 0

    audio_extensions = ('.mp3', '.wav', '.flac', '.ogg')
    all_files = sorted([
        f for f in os.listdir(corpus_dir)
        if f.lower().endswith(audio_extensions)
    ])

    if len(all_files) == 0:
        print(f"ERROR: No audio files found in {corpus_dir}")
        return None, None, None, None

    print(f"Found {len(all_files)} audio files.")
    print(f"Extracting features (F0 range: "
          f"{F0_MIN}–{F0_MAX} Hz)...\n")

    for fname in all_files:
        fpath = os.path.join(corpus_dir, fname)
        feats = extract_features(fpath)
        n = len(feats)
        if n > 0:
            all_features.extend(feats)
            files_processed += 1
            print(f"  {fname:<60} {n:>3} segments")
        else:
            files_skipped += 1
            print(f"  {fname:<60}   0 segments (skipped)")

    print(f"\n{'─'*65}")
    print(f"Files processed:          {files_processed}")
    print(f"Files skipped:            {files_skipped}")
    print(f"Total segments extracted: {len(all_features)}")
    print(f"{'─'*65}\n")

    if len(all_features) < 50:
        print("WARNING: Very few segments extracted.")
        print("Try lowering TOP_DB to 20 and re-running.")
        if len(all_features) == 0:
            return None, None, None, None

    X = np.array(all_features)

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_components = min(N_PCA, X_scaled.shape[0],
                       X_scaled.shape[1])
    pca   = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    centroid    = np.mean(X_pca, axis=0)
    centroid_sd = np.std(X_pca,  axis=0)

    f0_values   = X[:, -2]
    dur_values  = X[:, -1]
    cent_values = X[:, N_MFCC]

    print("=" * 65)
    print("SPECIES EIGENFUNCTION SPACE — V2 RESULTS")
    print("=" * 65)

    print(f"\nSegments used: {len(all_features)}")
    print(f"F0 search range enforced: {F0_MIN}–{F0_MAX} Hz")
    print(f"Duration filter: {MIN_DUR_MS}–{MAX_DUR_MS} ms")

    print(f"\nF0 statistics (Hz) — FUNDAMENTAL ONLY:")
    print(f"  Mean:        {np.mean(f0_values):>8.1f}")
    print(f"  Median:      {np.median(f0_values):>8.1f}")
    print(f"  SD:          {np.std(f0_values):>8.1f}")
    print(f"  5th pctile:  {np.percentile(f0_values,  5):>8.1f}")
    print(f"  25th pctile: {np.percentile(f0_values, 25):>8.1f}")
    print(f"  75th pctile: {np.percentile(f0_values, 75):>8.1f}")
    print(f"  95th pctile: {np.percentile(f0_values, 95):>8.1f}")

    print(f"\nDuration statistics (ms):")
    print(f"  Mean:        {np.mean(dur_values):>8.1f}")
    print(f"  Median:      {np.median(dur_values):>8.1f}")
    print(f"  SD:          {np.std(dur_values):>8.1f}")
    print(f"  5th pctile:  {np.percentile(dur_values,  5):>8.1f}")
    print(f"  95th pctile: {np.percentile(dur_values, 95):>8.1f}")

    print(f"\nSpectral centroid statistics (Hz):")
    print(f"  Mean:        {np.mean(cent_values):>8.1f}")
    print(f"  Median:      {np.median(cent_values):>8.1f}")
    print(f"  SD:          {np.std(cent_values):>8.1f}")

    print(f"\nPCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        bar = '█' * int(v * 40)
        print(f"  PC{i+1}: {v:.4f}  {bar}")

    print(f"\nSpecies eigenfunction centroid:")
    for i in range(len(centroid)):
        print(f"  PC{i+1}: {centroid[i]:>+8.4f}  "
              f"(SD: {centroid_sd[i]:.4f})")

    print(f"\nSYNTHESIS PARAMETERS:")
    print(f"  f0_hz       = {np.median(f0_values):.0f}")
    print(f"  duration_ms = {np.median(dur_values):.0f}")
    print(f"  formant_hz  = {np.median(cent_values):.0f}")
    print(f"\n  LOW variant:  f0_hz = "
          f"{np.percentile(f0_values, 25):.0f}")
    print(f"  MID variant:  f0_hz = "
          f"{np.median(f0_values):.0f}")
    print(f"  HIGH variant: f0_hz = "
          f"{np.percentile(f0_values, 75):.0f}")
    print("=" * 65)

    return pca, scaler, centroid, X_pca


if __name__ == "__main__":
    print("=" * 65)
    print("OC-OBS-005 — COCKATIEL SPECIES ANALYSIS V2")
    print("OrganismCore — Eric Robert Lawson")
    print("=" * 65)
    print(f"\nCorpus directory: {CORPUS_DIR}\n")

    if not os.path.isdir(CORPUS_DIR):
        print(f"ERROR: Directory not found: {CORPUS_DIR}")
        print("Expected structure:")
        print("  cockatiel/")
        print("  ├── cockatiel_species_analysis_v2.py")
        print("  └── audio_files/")
        print("      └── *.mp3 / *.wav")
    else:
        pca, scaler, centroid, X_pca = \
            build_species_eigenfunction_space(CORPUS_DIR)

        if pca is not None:
            print("\nAnalysis complete.")
            print("Paste the full output into the chat")
            print("to get your calibrated synthesis targets.")
