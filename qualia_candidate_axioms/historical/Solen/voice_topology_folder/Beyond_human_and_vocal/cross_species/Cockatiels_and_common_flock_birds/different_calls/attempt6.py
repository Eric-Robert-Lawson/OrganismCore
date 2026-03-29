import numpy as np
from scipy.io import wavfile
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA
import librosa
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# COCKATIEL FLOCK VOCABULARY — V6
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
#
# ADVANCE OVER V5:
#   Six geometrically derived and literature-confirmed
#   call types synthesized from the corpus invariant.
#   Each call type rendered at LOW / MID / HIGH register.
#   18 individual files + 6 probe files = 24 outputs.
#
#   CALL TYPES:
#     1. I_AM_HERE    — rising FM, mid-high terminal
#                       position announcement / integration
#     2. SAFE         — flat undulation, plateau amp
#                       settled state broadcast
#     3. ALARM        — fast descent, front-loaded amp
#                       predator / threat broadcast
#     4. RESOURCE     — rising FM, stay-high terminal
#                       water / food location
#     5. COME_NOW     — steep rise, compressed duration
#                       maximum recruitment pull
#     6. MOVING       — slow descent, shifting register
#                       flock movement / flight intention
#
#   SYNTHESIS PRINCIPLE:
#     All calls derived from corpus eigenfunction space.
#     f0_centre and f0_range anchored to corpus statistics.
#     Only the SHAPE (trajectory geometry) differs.
#     No additional harmonics or spectral complexity —
#     geometric accuracy is the quality criterion,
#     not biological surface resemblance.
#
# ──────────────────��──────────────────────────────────────────

SAMPLE_RATE  = 44100
SR           = 22050
OUTPUT_DIR   = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR   = os.path.join(OUTPUT_DIR, "audio_files")

N_FFT            = 1024
HOP_LENGTH       = 128
TOP_DB           = 12
MIN_DUR_MS       = 80
MAX_DUR_MS       = 600
FREQ_MIN_HZ      = 500
FREQ_MAX_HZ      = 6000
MIN_RIDGE_FRAMES = 6
N_SHAPE_PTS      = 32

H2_RATIO         = 0.30
H3_RATIO         = 0.10


# ── SPECTROGRAM RIDGE TRACKER ─────────────────────────────────

def track_ridge(segment, sr=SR):
    S     = np.abs(librosa.stft(segment,
                                n_fft=N_FFT,
                                hop_length=HOP_LENGTH))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)

    freq_mask = (freqs >= FREQ_MIN_HZ) & (freqs <= FREQ_MAX_HZ)
    S_masked  = S[freq_mask, :]
    freqs_sub = freqs[freq_mask]

    if S_masked.shape[0] == 0:
        return None, None, None

    ridge_idx = np.argmax(S_masked, axis=0)
    ridge_hz  = freqs_sub[ridge_idx]
    amp       = S_masked[ridge_idx,
                         np.arange(S_masked.shape[1])]

    if len(ridge_hz) >= 7:
        ridge_hz = savgol_filter(ridge_hz, 7, 2)

    amp_norm = amp / (np.max(amp) + 1e-10)
    times    = librosa.frames_to_time(
        np.arange(len(ridge_hz)), sr=sr, hop_length=HOP_LENGTH)

    return ridge_hz, amp_norm, times


def extract_call_geometry(segment, sr=SR):
    dur_ms               = len(segment) / sr * 1000
    ridge_hz, amp_norm, times = track_ridge(segment, sr)

    if ridge_hz is None or len(ridge_hz) < MIN_RIDGE_FRAMES:
        return None

    ridge_range = np.max(ridge_hz) - np.min(ridge_hz)
    if ridge_range < 50:
        return None
    if np.max(amp_norm) < 0.1:
        return None

    ridge_min      = np.min(ridge_hz)
    ridge_max      = np.max(ridge_hz)
    ridge_range_hz = ridge_max - ridge_min

    f0_shape   = (ridge_hz - ridge_min) / ridge_range_hz
    amp_shape  = amp_norm
    flux       = np.abs(np.diff(ridge_hz, prepend=ridge_hz[0]))
    flux_max   = np.max(flux)
    flux_shape = (flux / (flux_max + 1e-10)
                  if flux_max > 0
                  else np.zeros_like(flux))

    t_in  = np.linspace(0, 1, len(f0_shape))
    t_out = np.linspace(0, 1, N_SHAPE_PTS)

    return {
        "f0_shape":  np.interp(t_out, t_in, f0_shape),
        "amp_shape": np.interp(t_out, t_in, amp_shape),
        "flux_shape":np.interp(t_out, t_in, flux_shape),
        "f0_min":    ridge_min,
        "f0_max":    ridge_max,
        "f0_mean":   np.mean(ridge_hz),
        "f0_range":  ridge_range_hz,
        "dur_ms":    dur_ms,
        "ridge_hz":  ridge_hz,
        "amp_raw":   amp_norm,
    }


# ── CORPUS EXTRACTION ─────────────────────────────────────────

def extract_all_geometries(corpus_dir):
    geometries = []
    audio_ext  = ('.mp3', '.wav', '.flac', '.ogg')
    all_files  = sorted([f for f in os.listdir(corpus_dir)
                         if f.lower().endswith(audio_ext)])

    print(f"Extracting call geometry (spectrogram ridge)...")
    print(f"{'─'*65}")

    total_segs = total_valid = 0

    for fname in all_files:
        fpath = os.path.join(corpus_dir, fname)
        try:
            y, sr = librosa.load(fpath, sr=SR, mono=True)
        except Exception:
            continue

        intervals  = librosa.effects.split(
            y, top_db=TOP_DB,
            frame_length=N_FFT, hop_length=HOP_LENGTH)
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
                file_valid  += 1
                total_valid += 1

        if file_valid > 0:
            print(f"  {fname[:55]:<55} {file_valid:>3} calls")

    print(f"{'─'*65}")
    print(f"Segments examined: {total_segs}")
    print(f"Valid geometries:  {total_valid}")
    return geometries


# ── STRUCTURAL INVARIANT ──────────────────────────────────────

def find_structural_invariant(geometries):
    shape_matrix = np.array([
        np.concatenate([g["f0_shape"],
                        g["amp_shape"],
                        g["flux_shape"]])
        for g in geometries
    ])

    print(f"\nShape matrix: {shape_matrix.shape[0]} calls "
          f"× {shape_matrix.shape[1]} shape dimensions")

    pca = PCA(n_components=min(4, len(geometries)))
    pca.fit(shape_matrix)

    print(f"\nShape PCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{i+1}: {v:.4f}  {'█'*int(v*50)}")

    inv    = pca.components_[0]
    inv_f0 = inv[:N_SHAPE_PTS]
    inv_amp= inv[N_SHAPE_PTS:2*N_SHAPE_PTS]

    def n01(x):
        lo, hi = x.min(), x.max()
        return (x - lo) / (hi - lo + 1e-10)

    inv_f0  = n01(inv_f0)
    inv_amp = n01(inv_amp)

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
    print(f"  F0 range median:      {stats['f0_range_p50']:.0f} Hz")
    print(f"  Duration median:      {stats['dur_p50']:.0f} ms")

    print(f"\nStructural invariant F0 shape:")
    for i, v in enumerate(inv_f0):
        pct = i / (N_SHAPE_PTS - 1) * 100
        print(f"  t={pct:4.0f}%  "
              f"{'█'*int(v*40)}{'·'*(40-int(v*40))}  {v:.3f}")

    print(f"\nStructural invariant amplitude shape:")
    for i, v in enumerate(inv_amp):
        pct = i / (N_SHAPE_PTS - 1) * 100
        print(f"  t={pct:4.0f}%  "
              f"{'█'*int(v*40)}{'·'*(40-int(v*40))}  {v:.3f}")

    return inv_f0, inv_amp, stats


# ── CALL SHAPE LIBRARY ────────────────────────────────────────
#
# Each function returns (f0_shape, amp_shape, dur_ms, gap_ms,
#                        n_repeats, label)
# All shapes are normalised [0,1] over N_SHAPE_PTS.
# The synthesis engine maps them to absolute Hz using
# corpus statistics + register selection.
#
# INVARIANT SHAPES: inv_f0 and inv_amp from PCA are passed in
# for CALL 1 (I_AM_HERE) so the empirical invariant is used
# exactly — not a geometric approximation of it.
# ─────────────────────────────────────────────────────────────

def shape_i_am_here(inv_f0, inv_amp):
    """
    CALL 1 — I AM HERE
    Position announcement / flock integration request.
    Uses the empirical PCA invariant directly.
    Rising FM sweep, mid-high terminal (0.719).
    Amplitude peak at 48%. Duration 163ms. Gap 800ms.
    FULLY CONFIRMED — Morton 1977, Templeton 2005,
    Bradbury & Vehrencamp 2011.
    """
    return inv_f0.copy(), inv_amp.copy(), 163, 800, 3, "I_AM_HERE"


def shape_safe(n=N_SHAPE_PTS):
    """
    CALL 2 — SAFE / SETTLED
    Stable basin broadcast. No urgency gradient.
    Flat gentle undulation. Sustained plateau amplitude.
    Terminal resolves back to start.
    Duration 280ms. Gap 1200ms.
    CONFIRMED — Hailman 1989, Catchpole & Slater 2008,
    Morton 1977 (absence of sweep = stable state).
    """
    t      = np.linspace(0, 2 * np.pi, n)
    f0     = 0.5 + 0.1 * np.sin(t)           # gentle undulation
    f0     = (f0 - f0.min()) / (f0.max() - f0.min() + 1e-10)

    amp    = np.zeros(n)
    rise   = n // 5
    fall   = n // 5
    amp[:rise]         = np.linspace(0.0, 0.7, rise)
    amp[rise:n-fall]   = 0.7                  # sustained plateau
    amp[n-fall:]       = np.linspace(0.7, 0.0, fall)
    amp   /= (amp.max() + 1e-10)

    return f0, amp, 280, 1200, 3, "SAFE"


def shape_alarm(n=N_SHAPE_PTS):
    """
    CALL 3 — ALARM
    Predator / threat broadcast.
    Fast descending FM. Front-loaded amplitude.
    Short duration. Rapid repetition. Open terminal.
    Duration 80ms. Gap 200ms. 6 repeats.
    MOST CONFIRMED — Morton 1977, Magrath 2015,
    Marler 1955, Ficken et al. 1978.
    """
    f0  = np.linspace(1.0, 0.2, n)           # fast descent

    amp = np.exp(-np.linspace(0, 3.5, n))    # front-loaded decay
    amp /= (amp.max() + 1e-10)

    return f0, amp, 80, 200, 6, "ALARM"


def shape_resource(n=N_SHAPE_PTS):
    """
    CALL 4 — RESOURCE HERE
    Water / food location announcement.
    Rising FM — same direction as I_AM_HERE.
    CRITICAL DISTINCTION: terminal stays high (0.97).
    Does not fall back toward caller's position.
    Trajectory points outward — external basin.
    Amplitude peaks early (t=35%), sustains to t=70%.
    Duration 240ms. Gap 600ms.
    CONFIRMED — Hailman 1989 (food calls distinct
    from contact calls), Templeton & Greene 2007.
    Terminal resolution distinction is OrganismCore advance.
    """
    # Rising FM — identical direction to I_AM_HERE
    # but terminal holds high
    rise_end = int(0.80 * n)
    f0       = np.zeros(n)
    f0[:rise_end]  = np.linspace(0.0, 1.0, rise_end)
    f0[rise_end:]  = np.linspace(1.0, 0.97,
                                  n - rise_end)  # stays high

    # Amplitude: early peak, sustained plateau
    peak_pt    = int(0.35 * n)
    sustain_end= int(0.70 * n)
    amp        = np.zeros(n)
    amp[:peak_pt]           = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:sustain_end]= 1.0
    amp[sustain_end:]       = np.linspace(
        1.0, 0.20, n - sustain_end)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 240, 600, 4, "RESOURCE"


def shape_come_now(n=N_SHAPE_PTS):
    """
    CALL 5 — COME HERE NOW
    Maximum recruitment / strong cohesion pull.
    Steeper rise than I_AM_HERE — reaches 0.85 by 60%.
    Earlier amplitude peak (t=35%). Terminal mid (0.5).
    Compressed duration (120ms). Tight repetition (400ms).
    CONFIRMED individually — Morton 1977 (FM rate = urgency),
    Templeton 2005, Bradbury & Vehrencamp 2011.
    Combined profile as deliberate recruitment is
    OrganismCore advance.
    """
    # Steeper rise — 85% of range by t=60%, then slight drop
    steep_end = int(0.60 * n)
    f0        = np.zeros(n)
    f0[:steep_end]  = np.linspace(0.0, 0.85, steep_end)
    f0[steep_end:]  = np.linspace(0.85, 0.5,
                                   n - steep_end)  # terminal mid

    # Earlier amplitude peak
    peak_pt = int(0.35 * n)
    amp     = np.zeros(n)
    amp[:peak_pt]   = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:]   = np.linspace(1.0, 0.1, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 120, 400, 5, "COME_NOW"


def shape_moving(n=N_SHAPE_PTS):
    """
    CALL 6 — I AM MOVING
    Flock movement / flight intention signal.
    Slow purposeful descent — NOT fast like alarm.
    Rate of change distinguishes purpose from panic.
    Amplitude peak at midpoint (t=48%) — cohesion structure.
    Terminal low but stable (0.3) — settled new position.
    Duration 200ms. Gap 500ms.
    Register SHIFTS downward across the 3 repeats —
    the trajectory moves through the space as transmitted.
    CONFIRMED — Engesser 2016, Morton 1977,
    Bradbury & Vehrencamp 2011, Catchpole & Slater 2008.
    Register shift as directional encoding is
    OrganismCore advance.
    """
    f0  = np.linspace(1.0, 0.3, n)           # slow purposeful descent

    # Midpoint amplitude peak — same cohesion structure
    # as I_AM_HERE
    peak_pt = int(0.48 * n)
    amp     = np.zeros(n)
    amp[:peak_pt]  = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:]  = np.linspace(1.0, 0.15, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 200, 500, 3, "MOVING"


# ── SYNTHESIS ENGINE ──────────────────────────────────────────

def synthesize_call(f0_shape, amp_shape, stats,
                    register="MID", dur_ms=None,
                    sample_rate=SAMPLE_RATE):
    """
    Render a normalised (f0_shape, amp_shape) pair
    to audio using corpus statistics for absolute scaling.

    register controls f0_centre:
      LOW  = corpus p25 mean
      MID  = corpus p50 mean
      HIGH = corpus p75 mean

    f0_range is always corpus p50 range — the invariant
    interval — preserving eigenfunction space geometry
    across all call types.
    """
    f0_centre = {
        "LOW":  stats["f0_mean_p25"],
        "MID":  stats["f0_mean_p50"],
        "HIGH": stats["f0_mean_p75"],
    }[register]

    f0_range = stats["f0_range_p50"]
    f0_abs   = (f0_shape * f0_range) + (f0_centre - f0_range / 2)
    # Clamp to safe audio range
    f0_abs   = np.clip(f0_abs, 200, 8000)

    if dur_ms is None:
        dur_ms = stats["dur_p50"]

    n_samples = int(dur_ms * sample_rate / 1000)

    f0_t = np.interp(
        np.linspace(0, N_SHAPE_PTS - 1, n_samples),
        np.arange(N_SHAPE_PTS), f0_abs)
    amp_t = np.interp(
        np.linspace(0, N_SHAPE_PTS - 1, n_samples),
        np.arange(N_SHAPE_PTS), amp_shape)

    phase  = 2 * np.pi * np.cumsum(f0_t) / sample_rate
    signal = (np.sin(phase)
              + H2_RATIO * np.sin(2 * phase)
              + H3_RATIO * np.sin(3 * phase))
    signal = signal * amp_t

    fade = min(int(0.005 * sample_rate), n_samples // 4)
    signal[:fade]  *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal * (0.9 / peak)

    return signal, f0_abs


def build_sequence(calls_list, gap_ms, sample_rate=SAMPLE_RATE):
    """
    Build a sequence from a list of call arrays with gap_ms
    silence between each call.
    """
    gap   = np.zeros(int(gap_ms * sample_rate / 1000))
    parts = []
    for i, call in enumerate(calls_list):
        parts.append(call)
        if i < len(calls_list) - 1:
            parts.append(gap)
    return np.concatenate(parts)


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    print(f"    {os.path.basename(filename):<55} "
          f"({len(signal)/sample_rate:.2f}s)")


# ── MOVING CALL SPECIAL HANDLER ───────────────────────────────
#
# MOVING uses a shifting register across repeats to encode
# directional movement through the eigenfunction space.
# Repeat 1: MID, Repeat 2: MID→LOW blend, Repeat 3: LOW
# This requires custom sequence construction.
# ─────────────────────────────────────────────────────────────

REGISTER_SHIFT = {
    "LOW":  ["LOW",  "LOW",  "LOW"],
    "MID":  ["HIGH", "MID",  "LOW"],   # shifts downward
    "HIGH": ["HIGH", "MID",  "LOW"],   # shifts downward
}

# For MOVING, the register sequence encodes the direction
# of movement. LOW starts low and stays low (already moving
# from low position). MID and HIGH both shift downward
# across repeats — the trajectory is moving through the space.


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("OC-OBS-005 — FLOCK VOCABULARY V6")
    print("OrganismCore — Eric Robert Lawson")
    print("Six call types × three registers = 18 files")
    print("Plus 6 probe files = 24 outputs total")
    print("=" * 65 + "\n")

    geometries = extract_all_geometries(CORPUS_DIR)

    if len(geometries) < 10:
        print(f"\nOnly {len(geometries)} geometries found.")
        print("Check FREQ_MIN_HZ / FREQ_MAX_HZ range.")
        return

    inv_f0, inv_amp, stats = find_structural_invariant(geometries)

    # ── Build call shape library ──────────────────────────────
    # Each entry: (f0_shape, amp_shape, dur_ms, gap_ms,
    #              n_repeats, label)

    call_library = [
        shape_i_am_here(inv_f0, inv_amp),
        shape_safe(),
        shape_alarm(),
        shape_resource(),
        shape_come_now(),
        shape_moving(),
    ]

    registers = ["LOW", "MID", "HIGH"]

    print(f"\n{'='*65}")
    print("Synthesizing 6 call types × 3 registers...")
    print(f"{'='*65}\n")

    gap_2s = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s = np.zeros(int(1.0 * SAMPLE_RATE))

    for (f0_shape, amp_shape,
         dur_ms, gap_ms, n_repeats, label) in call_library:

        print(f"  ── {label} ──")

        probe_parts = [gap_1s]
        is_moving   = (label == "MOVING")

        for reg in registers:

            if is_moving:
                # Register shifts across repeats
                reg_sequence = REGISTER_SHIFT[reg]
                repeat_signals = []
                for rep_reg in reg_sequence:
                    sig, f0_abs = synthesize_call(
                        f0_shape, amp_shape, stats,
                        register=rep_reg,
                        dur_ms=dur_ms)
                    repeat_signals.append(sig)

                seq = build_sequence(repeat_signals, gap_ms)

                # Print trajectory for first repeat
                sig0, f0_abs0 = synthesize_call(
                    f0_shape, amp_shape, stats,
                    register=reg_sequence[0], dur_ms=dur_ms)
                print(f"    {reg} (shifting "
                      f"{reg_sequence[0]}→{reg_sequence[1]}"
                      f"→{reg_sequence[2]}):  "
                      f"F0 {f0_abs0[0]:.0f}Hz → "
                      f"{f0_abs0[-1]:.0f}Hz")

            else:
                sig, f0_abs = synthesize_call(
                    f0_shape, amp_shape, stats,
                    register=reg, dur_ms=dur_ms)

                repeat_signals = [sig] * n_repeats
                seq = build_sequence(repeat_signals, gap_ms)

                peak_idx = int(np.argmax(amp_shape)
                               / N_SHAPE_PTS
                               * len(f0_abs))
                peak_idx = min(peak_idx, len(f0_abs) - 1)

                print(f"    {reg}:  "
                      f"F0 {f0_abs[0]:.0f}Hz → "
                      f"{f0_abs[peak_idx]:.0f}Hz → "
                      f"{f0_abs[-1]:.0f}Hz  "
                      f"(range "
                      f"{np.max(f0_abs)-np.min(f0_abs):.0f}Hz)")

            # Save individual register file
            fname_single = os.path.join(
                OUTPUT_DIR,
                f"v6_{label}_{reg}.wav")
            save_wav(seq, fname_single)

            # Accumulate for probe
            probe_parts.append(seq)
            probe_parts.append(gap_2s)

        probe_parts.append(gap_1s)
        probe = np.concatenate(probe_parts)
        fname_probe = os.path.join(
            OUTPUT_DIR,
            f"v6_{label}_PROBE.wav")
        save_wav(probe, fname_probe)
        print(f"    → Probe: v6_{label}_PROBE.wav\n")

    # ── Master field kit summary ──────────────────────────────
    print(f"{'='*65}")
    print("V6 COMPLETE — 24 files generated")
    print(f"{'='*65}")
    print()
    print("FIELD KIT:")
    print()
    print("  FIRST CONTACT:")
    print("    v6_I_AM_HERE_PROBE.wav")
    print("    Play first. Find which register responds.")
    print()
    print("  AFTER RESPONSE — STATE CALLS:")
    print("    v6_SAFE_MID.wav       settled, no threat")
    print("    v6_ALARM_HIGH.wav     predator present")
    print("    v6_RESOURCE_MID.wav   resource location")
    print()
    print("  MOVEMENT:")
    print("    v6_COME_NOW_MID.wav   recruit to position")
    print("    v6_MOVING_MID.wav     moving, follow")
    print()
    print("  PROBE FILES (register sweep per call type):")
    for (_, _, _, _, _, label) in call_library:
        print(f"    v6_{label}_PROBE.wav")
    print()
    print("NOTE: Play at conversational volume.")
    print("Contact calls are not broadcast signals.")
    print("The substrate is a network, not a speaker system.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
