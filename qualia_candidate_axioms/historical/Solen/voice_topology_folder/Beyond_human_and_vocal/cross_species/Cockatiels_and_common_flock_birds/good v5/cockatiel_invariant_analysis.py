import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, savgol_filter
from scipy.signal import stft
from sklearn.decomposition import PCA
import librosa
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# COCKATIEL STRUCTURAL INVARIANT ANALYSIS — V4
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
#
# APPROACH:
#   Each call is treated as a geometric object.
#   Three normalised shape descriptors extracted
#   from each call individually:
#     1. F0 shape     — pitch trajectory, scale-free
#     2. Amplitude    — dynamic contour, scale-free
#     3. Spectral flux — timbral movement, scale-free
#
#   PCA on the SHAPES (not the values) finds the
#   structural invariant — what is geometrically
#   consistent across all calls.
#
#   Synthesis re-scales the invariant shape back
#   into absolute values using corpus statistics.
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE  = 44100
SR_ANALYSIS  = 44100
OUTPUT_DIR   = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR   = os.path.join(OUTPUT_DIR, "audio_files")

F0_MIN       = 300
F0_MAX       = 1200
MIN_DUR_MS   = 100
MAX_DUR_MS   = 380
TOP_DB       = 20
HOP_LENGTH   = 32     # fine resolution
FRAME_LENGTH = 1024
N_SHAPE_PTS  = 32     # normalised time points per call


# ── STEP 1: EXTRACT EACH CALL AS A GEOMETRIC OBJECT ──────────

def extract_call_geometry(segment, sr):
    """
    Extract the three normalised shape descriptors
    from a single call segment.

    Returns dict with:
      f0_shape    : F0 trajectory, time-normalised,
                    frequency-normalised to [0,1]
      amp_shape   : amplitude contour, time-normalised,
                    amplitude-normalised to [0,1]
      flux_shape  : spectral flux contour, time-normalised,
                    normalised to [0,1]
      f0_min      : absolute F0 minimum (Hz)
      f0_max      : absolute F0 maximum (Hz)
      f0_mean     : absolute F0 mean (Hz)
      amp_peak    : absolute peak amplitude
      dur_ms      : absolute duration (ms)
      f0_range    : absolute F0 range (Hz)
      voiced_frac : fraction of frames voiced
    """

    dur_ms = len(segment) / sr * 1000

    # ── F0 trajectory ──
    try:
        f0, voiced, _ = librosa.pyin(
            segment,
            fmin=F0_MIN, fmax=F0_MAX,
            sr=sr,
            hop_length=HOP_LENGTH,
            frame_length=FRAME_LENGTH)
        if f0 is None or np.sum(voiced) < 6:
            return None
    except Exception:
        return None

    voiced_frac = np.sum(voiced) / len(voiced)
    if voiced_frac < 0.4:
        return None

    # Interpolate unvoiced frames
    f0_filled = f0.copy()
    vi  = np.where(voiced)[0]
    ui  = np.where(~voiced)[0]
    if len(ui) > 0:
        f0_filled[ui] = np.interp(ui, vi, f0[vi])

    # Smooth
    win = min(9, (len(f0_filled) // 2) * 2 - 1)
    if win >= 5:
        f0_filled = savgol_filter(f0_filled, win, 2)

    f0_min  = np.min(f0_filled)
    f0_max  = np.max(f0_filled)
    f0_range = f0_max - f0_min

    if f0_range < 30:
        return None   # no meaningful trajectory

    # Normalise F0 to [0,1] — scale-free shape
    f0_norm = (f0_filled - f0_min) / f0_range

    # ── Amplitude contour ──
    rms = librosa.feature.rms(
        y=segment,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH)[0]

    # Align to F0 length
    rms = np.interp(
        np.linspace(0, len(rms)-1, len(f0_norm)),
        np.arange(len(rms)), rms)

    amp_peak = np.max(rms)
    if amp_peak < 1e-6:
        return None

    amp_norm = rms / amp_peak  # normalised to [0,1]

    # ── Spectral flux contour ──
    # Frame-to-frame spectral change — timbral movement
    S = np.abs(librosa.stft(
        segment,
        hop_length=HOP_LENGTH,
        n_fft=FRAME_LENGTH))
    flux = np.concatenate([[0], np.sqrt(
        np.sum(np.diff(S, axis=1)**2, axis=0))])

    flux = np.interp(
        np.linspace(0, len(flux)-1, len(f0_norm)),
        np.arange(len(flux)), flux)

    flux_max = np.max(flux)
    flux_norm = flux / (flux_max + 1e-10)

    # ── Resample all shapes to N_SHAPE_PTS ��─
    t_in  = np.linspace(0, 1, len(f0_norm))
    t_out = np.linspace(0, 1, N_SHAPE_PTS)

    f0_shape   = np.interp(t_out, t_in, f0_norm)
    amp_shape  = np.interp(t_out, t_in, amp_norm)
    flux_shape = np.interp(t_out, t_in, flux_norm)

    return {
        "f0_shape":    f0_shape,
        "amp_shape":   amp_shape,
        "flux_shape":  flux_shape,
        "f0_min":      f0_min,
        "f0_max":      f0_max,
        "f0_mean":     np.mean(f0_filled[voiced]),
        "f0_range":    f0_range,
        "amp_peak":    amp_peak,
        "dur_ms":      dur_ms,
        "voiced_frac": voiced_frac,
    }


def extract_all_geometries(corpus_dir):
    """
    Extract call geometry from every call in corpus.
    Each call is treated individually.
    """
    geometries = []
    audio_ext  = ('.mp3', '.wav', '.flac', '.ogg')
    all_files  = sorted([
        f for f in os.listdir(corpus_dir)
        if f.lower().endswith(audio_ext)
    ])

    print(f"Extracting call geometry from each call...")
    print(f"Each call treated as individual geometric object.")
    print(f"{'─'*65}")

    total_segments = 0
    total_valid    = 0

    for fname in all_files:
        fpath = os.path.join(corpus_dir, fname)
        try:
            y, sr = librosa.load(fpath, sr=SR_ANALYSIS,
                                  mono=True)
        except Exception:
            continue

        intervals = librosa.effects.split(
            y, top_db=TOP_DB,
            frame_length=1024, hop_length=HOP_LENGTH)

        file_valid = 0
        for start, end in intervals:
            segment = y[start:end]
            dur_ms  = len(segment) / sr * 1000

            if not (MIN_DUR_MS < dur_ms < MAX_DUR_MS):
                continue

            total_segments += 1
            geom = extract_call_geometry(segment, sr)

            if geom is not None:
                geom["source"] = fname
                geometries.append(geom)
                file_valid += 1
                total_valid += 1

        if file_valid > 0:
            print(f"  {fname[:55]:<55} "
                  f"{file_valid:>3} valid")

    print(f"{'─'*65}")
    print(f"Total segments examined: {total_segments}")
    print(f"Valid geometries:        {total_valid}")
    return geometries


# ── STEP 2: FIND THE STRUCTURAL INVARIANT ────────────────────

def find_structural_invariant(geometries):
    """
    PCA on the SHAPES — not the values.
    PC1 of the shape PCA is the structural invariant:
    the geometric pattern common to all calls.

    The feature vector for each call is:
      [f0_shape(32) | amp_shape(32) | flux_shape(32)]
      = 96-dimensional shape descriptor

    PCA finds the directions of maximum shape consistency.
    PC1 is the most common shape.
    That is the invariant.
    """

    # Build shape matrix — each row is one call's shape
    shape_matrix = np.array([
        np.concatenate([
            g["f0_shape"],
            g["amp_shape"],
            g["flux_shape"]
        ]) for g in geometries
    ])

    print(f"\nShape matrix: {shape_matrix.shape}")
    print(f"  {shape_matrix.shape[0]} calls × "
          f"{shape_matrix.shape[1]} shape dimensions")
    print(f"  ({N_SHAPE_PTS} F0 pts + "
          f"{N_SHAPE_PTS} amp pts + "
          f"{N_SHAPE_PTS} flux pts)")

    pca = PCA(n_components=4)
    pca.fit(shape_matrix)

    print(f"\nShape PCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        bar = '█' * int(v * 50)
        print(f"  PC{i+1}: {v:.4f}  {bar}")

    # PC1 IS the invariant shape
    invariant = pca.components_[0]

    # Split back into three shape components
    inv_f0   = invariant[:N_SHAPE_PTS]
    inv_amp  = invariant[N_SHAPE_PTS:2*N_SHAPE_PTS]
    inv_flux = invariant[2*N_SHAPE_PTS:]

    # Normalise each component to [0,1]
    def norm01(x):
        xmin, xmax = x.min(), x.max()
        if xmax - xmin < 1e-10:
            return np.ones_like(x) * 0.5
        return (x - xmin) / (xmax - xmin)

    inv_f0   = norm01(inv_f0)
    inv_amp  = norm01(inv_amp)

    # Absolute statistics from corpus
    f0_means  = np.array([g["f0_mean"]  for g in geometries])
    f0_ranges = np.array([g["f0_range"] for g in geometries])
    f0_mins   = np.array([g["f0_min"]   for g in geometries])
    dur_ms    = np.array([g["dur_ms"]   for g in geometries])

    stats = {
        "f0_mean_p25":  np.percentile(f0_means,  25),
        "f0_mean_p50":  np.percentile(f0_means,  50),
        "f0_mean_p75":  np.percentile(f0_means,  75),
        "f0_range_p50": np.percentile(f0_ranges, 50),
        "f0_min_p50":   np.percentile(f0_mins,   50),
        "dur_p50":      np.percentile(dur_ms,     50),
    }

    print(f"\nCorpus absolute statistics:")
    print(f"  F0 mean  p25/p50/p75: "
          f"{stats['f0_mean_p25']:.0f} / "
          f"{stats['f0_mean_p50']:.0f} / "
          f"{stats['f0_mean_p75']:.0f} Hz")
    print(f"  F0 range median:      "
          f"{stats['f0_range_p50']:.0f} Hz")
    print(f"  F0 min median:        "
          f"{stats['f0_min_p50']:.0f} Hz")
    print(f"  Duration median:      "
          f"{stats['dur_p50']:.0f} ms")

    print(f"\nStructural invariant F0 shape "
          f"(normalised 0-1):")
    for i, v in enumerate(inv_f0):
        pct = i / (N_SHAPE_PTS-1) * 100
        bar = int(v * 30)
        print(f"  t={pct:4.0f}%  "
              f"{'█'*bar}{'·'*(30-bar)}  {v:.3f}")

    print(f"\nStructural invariant amplitude shape:")
    for i, v in enumerate(inv_amp):
        pct = i / (N_SHAPE_PTS-1) * 100
        bar = int(v * 30)
        print(f"  t={pct:4.0f}%  "
              f"{'█'*bar}{'·'*(30-bar)}  {v:.3f}")

    return inv_f0, inv_amp, stats


# ── STEP 3: SYNTHESIZE FROM INVARIANT ────────────────────────

def synthesize_from_invariant(
        inv_f0_shape,
        inv_amp_shape,
        stats,
        register      = "MID",
        h2_ratio      = 0.35,
        h3_ratio      = 0.12,
        sample_rate   = SAMPLE_RATE):
    """
    Re-scale the invariant shape back into
    absolute acoustic values and synthesize.

    register: "LOW" / "MID" / "HIGH"
      scales the F0 range using corpus percentiles
    """

    dur_ms = stats["dur_p50"]

    # Select F0 centre for this register
    f0_centre = {
        "LOW":  stats["f0_mean_p25"],
        "MID":  stats["f0_mean_p50"],
        "HIGH": stats["f0_mean_p75"],
    }[register]

    f0_range = stats["f0_range_p50"]

    # Re-scale F0 shape from [0,1] to absolute Hz
    # inv_f0_shape spans [0,1]
    # 0 = f0_centre - f0_range/2
    # 1 = f0_centre + f0_range/2
    f0_abs = (inv_f0_shape * f0_range) + \
             (f0_centre - f0_range / 2)

    # Synthesize
    n_samples = int(dur_ms * sample_rate / 1000)

    f0_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS),
        f0_abs)

    amp_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS),
        inv_amp_shape)

    # FM synthesis — phase integrated from F0 trajectory
    phase  = 2 * np.pi * np.cumsum(f0_t) / sample_rate

    signal = (
        np.sin(phase) +
        h2_ratio * np.sin(2 * phase) +
        h3_ratio * np.sin(3 * phase)
    )

    signal = signal * amp_t

    # 5ms fade in/out — remove clicks
    fade = int(0.005 * sample_rate)
    signal[:fade]  *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    # Normalise
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal * (0.9 / peak)

    return signal, f0_abs, dur_ms


def build_sequence(call, n_repeats=3, gap_ms=800,
                   sample_rate=SAMPLE_RATE):
    gap   = np.zeros(int(gap_ms * sample_rate / 1000))
    parts = []
    for i in range(n_repeats):
        parts.append(call)
        if i < n_repeats - 1:
            parts.append(gap)
    return np.concatenate(parts)


def save_wav(signal, filename,
             sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    print(f"  Saved: {os.path.basename(filename)}"
          f"  ({len(signal)/sample_rate:.2f}s)")


# ── MAIN ─────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("OC-OBS-005 — COCKATIEL INVARIANT ANALYSIS V4")
    print("OrganismCore — Eric Robert Lawson")
    print("Geometric approach — structural invariant")
    print("Each call analysed individually.")
    print("Invariant extracted. Not averaged.")
    print("=" * 65 + "\n")

    # Step 1 — extract geometry from every call
    geometries = extract_all_geometries(CORPUS_DIR)

    if len(geometries) < 20:
        print(f"\nOnly {len(geometries)} valid geometries.")
        print("Try lowering TOP_DB or F0 range threshold.")
        return

    # Step 2 — find structural invariant
    inv_f0, inv_amp, stats = \
        find_structural_invariant(geometries)

    # Step 3 — synthesize three variants
    print(f"\n{'='*65}")
    print("Synthesizing from structural invariant...")

    calls = {}
    for register in ["LOW", "MID", "HIGH"]:
        signal, f0_abs, dur_ms = synthesize_from_invariant(
            inv_f0, inv_amp, stats, register=register)
        calls[register] = signal

        print(f"\n  {register}:")
        print(f"    F0 start: {f0_abs[0]:.1f} Hz")
        print(f"    F0 peak:  "
              f"{f0_abs[np.argmax(inv_amp)]:.1f} Hz")
        print(f"    F0 end:   {f0_abs[-1]:.1f} Hz")
        print(f"    F0 range: "
              f"{np.max(f0_abs)-np.min(f0_abs):.1f} Hz")
        print(f"    Duration: {dur_ms:.0f} ms")

        fname = os.path.join(OUTPUT_DIR,
            f"v4_contact_{register}.wav")
        save_wav(signal, fname)

        seq   = build_sequence(signal)
        fname = os.path.join(OUTPUT_DIR,
            f"v4_sequence_{register}_3x.wav")
        save_wav(seq, fname)

    # First meeting probe
    print(f"\n{'─'*65}")
    print("Building first meeting probe...")

    gap_2s = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s = np.zeros(int(1.0 * SAMPLE_RATE))

    probe = np.concatenate([
        gap_1s,
        build_sequence(calls["LOW"]),
        gap_2s,
        build_sequence(calls["MID"]),
        gap_2s,
        build_sequence(calls["HIGH"]),
        gap_1s,
    ])

    fname = os.path.join(OUTPUT_DIR,
        "v4_FIRST_MEETING_PROBE.wav")
    save_wav(probe, fname)

    print(f"\n{'='*65}")
    print("V4 complete.")
    print("Listen to v4_contact_MID.wav")
    print("You should hear a call that moves —")
    print("the shape of every cockatiel contact call,")
    print("not the average of their values.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
