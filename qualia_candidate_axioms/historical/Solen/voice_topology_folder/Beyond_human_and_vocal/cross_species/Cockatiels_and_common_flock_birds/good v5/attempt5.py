import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, savgol_filter
from scipy.ndimage import gaussian_filter1d
from sklearn.decomposition import PCA
import librosa
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# COCKATIEL STRUCTURAL INVARIANT ANALYSIS — V5
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
#
# ROOT CAUSE FIX:
#   pyin cannot track short FM calls — locks on one bin.
#   Replaced with spectrogram ridge tracking:
#   find the brightest frequency at each time frame.
#   That IS the F0 trajectory. No estimation needed.
#   It is a direct geometric measurement.
#
# SEGMENTATION FIX:
#   top_db=20 over-splits. Using top_db=12 with
#   minimum gap merging to find whole calls.
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE  = 44100
SR           = 22050          # analysis SR
OUTPUT_DIR   = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR   = os.path.join(OUTPUT_DIR, "audio_files")

# Spectrogram parameters
N_FFT        = 1024           # frequency resolution
HOP_LENGTH   = 128            # ~5.8ms per frame at SR=22050
                              # enough time for ridge tracking

# Call detection
TOP_DB       = 12             # less aggressive splitting
MIN_DUR_MS   = 80
MAX_DUR_MS   = 600

# Ridge tracking
FREQ_MIN_HZ  = 500            # ignore below this
FREQ_MAX_HZ  = 6000           # ignore above this
MIN_RIDGE_FRAMES = 6          # minimum frames for valid call

# Geometry
N_SHAPE_PTS  = 32             # normalised time points


# ── SPECTROGRAM RIDGE TRACKER ─────��───────────────────────────

def track_ridge(segment, sr=SR):
    """
    Track the dominant frequency ridge in the spectrogram.

    This is direct geometric measurement:
      At each time frame, find the frequency bin
      with maximum energy within [FREQ_MIN, FREQ_MAX].
      That frequency IS the trajectory.
      No estimation. No modelling. No locking artifact.

    Returns:
      ridge_hz  : frequency at each frame (Hz)
      amp       : amplitude at each frame (RMS)
      times     : time of each frame (s)
    """
    # Spectrogram
    S = np.abs(librosa.stft(
        segment,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH))

    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)

    # Restrict to frequency range of interest
    freq_mask = (freqs >= FREQ_MIN_HZ) & \
                (freqs <= FREQ_MAX_HZ)
    S_masked  = S[freq_mask, :]
    freqs_sub = freqs[freq_mask]

    if S_masked.shape[0] == 0:
        return None, None, None

    # Ridge = brightest bin at each time frame
    ridge_idx = np.argmax(S_masked, axis=0)
    ridge_hz  = freqs_sub[ridge_idx]

    # Amplitude = energy at the ridge bin
    amp = S_masked[ridge_idx,
                   np.arange(S_masked.shape[1])]

    # Smooth ridge — remove frame-to-frame jitter
    # but preserve genuine movement
    if len(ridge_hz) >= 7:
        ridge_hz = savgol_filter(ridge_hz, 7, 2)

    # Amplitude envelope
    amp_norm = amp / (np.max(amp) + 1e-10)

    times = librosa.frames_to_time(
        np.arange(len(ridge_hz)),
        sr=sr, hop_length=HOP_LENGTH)

    return ridge_hz, amp_norm, times


def extract_call_geometry(segment, sr=SR):
    """
    Extract normalised shape geometry from one call.
    Uses spectrogram ridge tracking — not pyin.
    """
    dur_ms = len(segment) / sr * 1000

    ridge_hz, amp_norm, times = track_ridge(segment, sr)

    if ridge_hz is None or len(ridge_hz) < MIN_RIDGE_FRAMES:
        return None

    # Ridge must show real movement
    ridge_range = np.max(ridge_hz) - np.min(ridge_hz)
    if ridge_range < 50:
        return None

    # Amplitude must be meaningful
    if np.max(amp_norm) < 0.1:
        return None

    # ── Normalise shapes to [0,1] ──────────────────────────
    # This removes absolute pitch and absolute loudness.
    # Only the SHAPE remains.

    ridge_min = np.min(ridge_hz)
    ridge_max = np.max(ridge_hz)
    ridge_range_hz = ridge_max - ridge_min

    # F0 shape: 0=lowest point in call, 1=highest
    f0_shape = (ridge_hz - ridge_min) / ridge_range_hz

    # Amplitude shape: already 0-1
    amp_shape = amp_norm

    # Spectral flux shape: frame-to-frame frequency change
    flux = np.abs(np.diff(ridge_hz, prepend=ridge_hz[0]))
    flux_max = np.max(flux)
    flux_shape = flux / (flux_max + 1e-10) \
                 if flux_max > 0 else np.zeros_like(flux)

    # ── Resample all shapes to N_SHAPE_PTS ──────────────────
    t_in  = np.linspace(0, 1, len(f0_shape))
    t_out = np.linspace(0, 1, N_SHAPE_PTS)

    f0_shape_r   = np.interp(t_out, t_in, f0_shape)
    amp_shape_r  = np.interp(t_out, t_in, amp_shape)
    flux_shape_r = np.interp(t_out, t_in, flux_shape)

    return {
        "f0_shape":    f0_shape_r,
        "amp_shape":   amp_shape_r,
        "flux_shape":  flux_shape_r,
        "f0_min":      ridge_min,
        "f0_max":      ridge_max,
        "f0_mean":     np.mean(ridge_hz),
        "f0_range":    ridge_range_hz,
        "dur_ms":      dur_ms,
        "ridge_hz":    ridge_hz,    # keep raw for synthesis
        "amp_raw":     amp_norm,
    }


# ── CORPUS EXTRACTION ─────────────────────────────────────────

def extract_all_geometries(corpus_dir):
    geometries = []
    audio_ext  = ('.mp3', '.wav', '.flac', '.ogg')
    all_files  = sorted([
        f for f in os.listdir(corpus_dir)
        if f.lower().endswith(audio_ext)
    ])

    print(f"Extracting call geometry (spectrogram ridge)...")
    print(f"{'─'*65}")

    total_segs  = 0
    total_valid = 0

    for fname in all_files:
        fpath = os.path.join(corpus_dir, fname)
        try:
            y, sr = librosa.load(fpath, sr=SR, mono=True)
        except Exception:
            continue

        intervals = librosa.effects.split(
            y, top_db=TOP_DB,
            frame_length=N_FFT,
            hop_length=HOP_LENGTH)

        file_valid = 0
        for start, end in intervals:
            segment = y[start:end]
            dur_ms  = len(segment) / sr * 1000

            if not (MIN_DUR_MS < dur_ms < MAX_DUR_MS):
                continue

            total_segs += 1
            geom = extract_call_geometry(segment, sr)

            if geom is not None:
                geom["source"] = fname
                geometries.append(geom)
                file_valid += 1
                total_valid += 1

        if file_valid > 0:
            print(f"  {fname[:55]:<55} "
                  f"{file_valid:>3} calls")

    print(f"{'─'*65}")
    print(f"Segments examined: {total_segs}")
    print(f"Valid geometries:  {total_valid}")
    return geometries


# ── STRUCTURAL INVARIANT ──────────────────────────────────────

def find_structural_invariant(geometries):
    """
    PCA on normalised SHAPES.
    PC1 = the geometric pattern most consistent
    across all calls = the structural invariant.
    """

    shape_matrix = np.array([
        np.concatenate([
            g["f0_shape"],
            g["amp_shape"],
            g["flux_shape"]
        ]) for g in geometries
    ])

    print(f"\nShape matrix: {shape_matrix.shape[0]} calls "
          f"× {shape_matrix.shape[1]} shape dimensions")

    pca = PCA(n_components=min(4, len(geometries)))
    pca.fit(shape_matrix)

    print(f"\nShape PCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        bar = '█' * int(v * 50)
        print(f"  PC{i+1}: {v:.4f}  {bar}")

    # PC1 is the invariant
    inv = pca.components_[0]

    inv_f0   = inv[:N_SHAPE_PTS]
    inv_amp  = inv[N_SHAPE_PTS:2*N_SHAPE_PTS]

    # Normalise to [0,1]
    def n01(x):
        lo, hi = x.min(), x.max()
        return (x - lo) / (hi - lo + 1e-10)

    inv_f0  = n01(inv_f0)
    inv_amp = n01(inv_amp)

    # Corpus absolute statistics
    f0_means  = [g["f0_mean"]  for g in geometries]
    f0_ranges = [g["f0_range"] for g in geometries]
    f0_mins   = [g["f0_min"]   for g in geometries]
    durs      = [g["dur_ms"]   for g in geometries]

    stats = {
        "f0_mean_p25":  np.percentile(f0_means,  25),
        "f0_mean_p50":  np.percentile(f0_means,  50),
        "f0_mean_p75":  np.percentile(f0_means,  75),
        "f0_range_p50": np.percentile(f0_ranges, 50),
        "f0_min_p50":   np.percentile(f0_mins,   50),
        "dur_p50":      np.percentile(durs,       50),
    }

    print(f"\nCorpus statistics:")
    print(f"  F0 mean  p25/p50/p75: "
          f"{stats['f0_mean_p25']:.0f} / "
          f"{stats['f0_mean_p50']:.0f} / "
          f"{stats['f0_mean_p75']:.0f} Hz")
    print(f"  F0 range median:      "
          f"{stats['f0_range_p50']:.0f} Hz")
    print(f"  Duration median:      "
          f"{stats['dur_p50']:.0f} ms")

    print(f"\nStructural invariant F0 shape:")
    for i, v in enumerate(inv_f0):
        pct = i / (N_SHAPE_PTS-1) * 100
        bar = int(v * 40)
        print(f"  t={pct:4.0f}%  "
              f"{'█'*bar}{'·'*(40-bar)}  {v:.3f}")

    print(f"\nStructural invariant amplitude shape:")
    for i, v in enumerate(inv_amp):
        pct = i / (N_SHAPE_PTS-1) * 100
        bar = int(v * 40)
        print(f"  t={pct:4.0f}%  "
              f"{'█'*bar}{'·'*(40-bar)}  {v:.3f}")

    return inv_f0, inv_amp, stats


# ── SYNTHESIS ��────────────────────────────────────────────────

def synthesize_from_invariant(
        inv_f0_shape,
        inv_amp_shape,
        stats,
        register    = "MID",
        h2_ratio    = 0.30,
        h3_ratio    = 0.10,
        sample_rate = SAMPLE_RATE):

    dur_ms = stats["dur_p50"]

    f0_centre = {
        "LOW":  stats["f0_mean_p25"],
        "MID":  stats["f0_mean_p50"],
        "HIGH": stats["f0_mean_p75"],
    }[register]

    f0_range = stats["f0_range_p50"]
    f0_abs   = (inv_f0_shape * f0_range) + \
               (f0_centre - f0_range / 2)

    n_samples = int(dur_ms * sample_rate / 1000)

    f0_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS), f0_abs)

    amp_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS), inv_amp_shape)

    phase  = 2 * np.pi * np.cumsum(f0_t) / sample_rate
    signal = (np.sin(phase) +
              h2_ratio * np.sin(2 * phase) +
              h3_ratio * np.sin(3 * phase))

    signal = signal * amp_t

    fade = int(0.005 * sample_rate)
    signal[:fade]  *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal * (0.9 / peak)

    return signal, f0_abs


def build_sequence(call, n_repeats=3, gap_ms=800,
                   sample_rate=SAMPLE_RATE):
    gap   = np.zeros(int(gap_ms * sample_rate / 1000))
    parts = []
    for i in range(n_repeats):
        parts.append(call)
        if i < n_repeats - 1:
            parts.append(gap)
    return np.concatenate(parts)


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    print(f"  Saved: {os.path.basename(filename)}"
          f"  ({len(signal)/sample_rate:.2f}s)")


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("OC-OBS-005 — COCKATIEL INVARIANT V5")
    print("OrganismCore — Eric Robert Lawson")
    print("Ridge tracking. Geometric. No pyin.")
    print("=" * 65 + "\n")

    geometries = extract_all_geometries(CORPUS_DIR)

    if len(geometries) < 10:
        print(f"\nOnly {len(geometries)} geometries found.")
        print("Check FREQ_MIN_HZ / FREQ_MAX_HZ range.")
        return

    inv_f0, inv_amp, stats = \
        find_structural_invariant(geometries)

    print(f"\n{'='*65}")
    print("Synthesizing...")

    calls = {}
    for register in ["LOW", "MID", "HIGH"]:
        signal, f0_abs = synthesize_from_invariant(
            inv_f0, inv_amp, stats, register=register)
        calls[register] = signal

        print(f"\n  {register}:  "
              f"F0 {f0_abs[0]:.0f}Hz → "
              f"{f0_abs[np.argmax(inv_amp)]:.0f}Hz → "
              f"{f0_abs[-1]:.0f}Hz  "
              f"(range {np.max(f0_abs)-np.min(f0_abs):.0f}Hz)")

        save_wav(signal, os.path.join(OUTPUT_DIR,
            f"v5_contact_{register}.wav"))
        save_wav(build_sequence(signal),
            os.path.join(OUTPUT_DIR,
            f"v5_sequence_{register}_3x.wav"))

    gap_2s = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s = np.zeros(int(1.0 * SAMPLE_RATE))
    probe  = np.concatenate([
        gap_1s,
        build_sequence(calls["LOW"]),   gap_2s,
        build_sequence(calls["MID"]),   gap_2s,
        build_sequence(calls["HIGH"]),  gap_1s,
    ])
    save_wav(probe, os.path.join(OUTPUT_DIR,
        "v5_FIRST_MEETING_PROBE.wav"))

    print(f"\n{'='*65}")
    print("V5 complete.")
    print("Listen to v5_contact_MID.wav")
    print("The F0 trajectory above shows the actual")
    print("movement the invariant contains.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
