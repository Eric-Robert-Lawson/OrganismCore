#!/usr/bin/env python3
"""
v8_wild_flock.py — Wild Flock Substrate Engagement Protocol
OC-OBS-005 — OrganismCore — Eric Robert Lawson

Based on v7 cockatiel flock vocabulary.
Adapted for documented wild flock substrate engagement.

FIELD OBSERVATION STATE (2026-04-27):
  CONFIRMED WORKING PROTOCOL: I_AM_HERE_MID → RESOURCE_MID → SAFE_MID
  SPECIES RESPONDING:
    - Small passerines: finches, sparrows, chickadees (primary confirmed)
    - Red-winged blackbird male: territorial, responds occasionally to signals
    - Mallard duck: appearing, emerging low-frequency channel
    - Squirrel: non-avian, resource-confirmed, substrate-adjacent

WHAT THIS FILE GENERATES:
  1. WORKING_PROTOCOL     — confirmed three-call field sequence (3 registers)
  2. FULL_SESSION         — complete approach-to-close session (3 registers)
  3. DIALOGUE_SEQUENCE    — I_AM_HERE + ACKNOWLEDGE exchange loop
  4. RWBB_PROTOCOL        — territory-respectful sequence for RWBB
  5. MALLARD_PROTOCOL     — low-frequency adapted resource + safe
  6. ALARM_RECOVERY       — ALARM → ALL_CLEAR → SAFE de-escalation
  7. Individual calls     — all vocabulary, all species profiles, all registers

SIGNAL ACCURACY IS THE CURRENCY (The_Flock_Economy.md):
  RESOURCE signal must be followed by food.
  SAFE signal must reflect actual safe conditions.
  Never transmit a signal you cannot confirm.
  Inaccurate nodes are disintegrated by the network.
  Signal before placing food — not after.

SUBSTRATE PRINCIPLE (The_Flock_Substrate.md):
  The flock substrate is not species-specific.
  It is the shared eigenfunction space that
  all bounded vocal systems navigating under
  selection pressure are driven toward by physics.
  Different instruments. Different sounds.
  Same substrate. Same positions.

RESOURCE SIGNAL THEORY (Resource_Signal_Theory.md):
  Standard feeding: neophobia extinction over 2-4 weeks.
    Relationship is to the FOOD, not the NODE.
  Substrate signal: trust precedes physical investigation.
    Relationship is to YOU as a flock node.
    Remove food — relationship persists.
    Remove you — relationship is disrupted.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import savgol_filter
import os
import warnings

try:
    import librosa
    from sklearn.decomposition import PCA
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────

SAMPLE_RATE      = 44100
SR               = 22050
OUTPUT_DIR       = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR       = os.path.join(OUTPUT_DIR, "audio_files")

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
WHERE_RANGE_MULT = 1.35  # WHERE_ARE_YOU pushes above normal range


# ─────────────────────────────────────────────────────────────────
# SPECIES PROFILES
#
# Each profile defines the eigenfunction frequency space for that
# species' communication channel.
#
# The flock substrate is species-agnostic at the structural level —
# the same FM trajectory shapes (rising, flat, descending, etc.)
# carry the same affective content across species.
# What differs is the absolute frequency range: the same structure
# played in the instrument's natural register.
#
# SONGBIRD (default):
#   Cockatiel-derived corpus statistics.
#   Covers finches, sparrows, chickadees — confirmed working.
#   If corpus audio files are present, these are overridden.
#
# RWBB (Red-winged blackbird):
#   1400–2800 Hz range for flock substrate calls.
#   Territorial male has established the area as its territory.
#   RWBB integrating into your node is an advanced flock economy
#   outcome — it is treating you as a reliable flock member.
#   Constraint: avoid strong recruitment signals (COME_NOW,
#   WHERE_ARE_YOU at max range) — these may read as territorial
#   challenge or boundary assertion. Use SAFE + RESOURCE only.
#
# MALLARD (mallard duck):
#   400–850 Hz — much lower than passerine substrate.
#   Duck contact calls: female 700–900 Hz, male ~450–550 Hz.
#   Duck appearing is a resource-economy signal, not flock
#   substrate integration in the strict sense.
#   The low-frequency RESOURCE + SAFE signals are what matter.
#   Resource confirmation is primary.
# ─────────────────────────────────────────────────────────────────

SPECIES_PROFILES = {
    "SONGBIRD": {
        "label":        "Small passerines",
        "species":      "finches, sparrows, chickadees",
        "f0_mean_p25":  2100,   # LOW register
        "f0_mean_p50":  2800,   # MID register
        "f0_mean_p75":  3600,   # HIGH register
        "f0_range_p50": 1200,   # eigenfunction range per call
        "dur_p50":      163,    # ms — corpus median
        "h2_ratio":     0.30,
        "h3_ratio":     0.10,
        "confirmed":    True,
        "note": "Primary confirmed substrate. Override with corpus if available.",
    },
    "RWBB": {
        "label":        "Red-winged blackbird",
        "species":      "Agelaius phoeniceus — territorial node",
        "f0_mean_p25":  1400,
        "f0_mean_p50":  2000,
        "f0_mean_p75":  2800,
        "f0_range_p50": 800,
        "dur_p50":      180,
        "h2_ratio":     0.25,
        "h3_ratio":     0.08,
        "confirmed":    False,
        "note": "Territorial — SAFE + RESOURCE only. Avoid COME_NOW.",
    },
    "MALLARD": {
        "label":        "Mallard duck",
        "species":      "Anas platyrhynchos — low-frequency resource channel",
        "f0_mean_p25":  420,
        "f0_mean_p50":  620,
        "f0_mean_p75":  850,
        "f0_range_p50": 300,
        "dur_p50":      220,
        "h2_ratio":     0.45,   # ducks have stronger harmonic content
        "h3_ratio":     0.22,
        "confirmed":    False,
        "note": "Resource + safe primary. Place food near water if possible.",
    },
}


# ─────────────────────────────────────────────────────────────────
# CORPUS EXTRACTION
# Identical to v7. If cockatiel audio files are present in
# ./audio_files/, extracts eigenfunction statistics and overrides
# the SONGBIRD estimated profile.
# ─────────────────────────────────────────────────────────────────

def track_ridge(segment, sr=SR):
    S     = np.abs(librosa.stft(segment, n_fft=N_FFT, hop_length=HOP_LENGTH))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)

    freq_mask = (freqs >= FREQ_MIN_HZ) & (freqs <= FREQ_MAX_HZ)
    S_masked  = S[freq_mask, :]
    freqs_sub = freqs[freq_mask]

    if S_masked.shape[0] == 0:
        return None, None, None

    ridge_idx = np.argmax(S_masked, axis=0)
    ridge_hz  = freqs_sub[ridge_idx]
    amp       = S_masked[ridge_idx, np.arange(S_masked.shape[1])]

    if len(ridge_hz) >= 7:
        ridge_hz = savgol_filter(ridge_hz, 7, 2)

    amp_norm = amp / (np.max(amp) + 1e-10)
    times    = librosa.frames_to_time(
        np.arange(len(ridge_hz)), sr=sr, hop_length=HOP_LENGTH)

    return ridge_hz, amp_norm, times


def extract_call_geometry(segment, sr=SR):
    dur_ms                    = len(segment) / sr * 1000
    ridge_hz, amp_norm, times = track_ridge(segment, sr)

    if ridge_hz is None or len(ridge_hz) < MIN_RIDGE_FRAMES:
        return None

    if (np.max(ridge_hz) - np.min(ridge_hz)) < 50:
        return None
    if np.max(amp_norm) < 0.1:
        return None

    ridge_min      = np.min(ridge_hz)
    ridge_max      = np.max(ridge_hz)
    ridge_range_hz = ridge_max - ridge_min

    f0_shape  = (ridge_hz - ridge_min) / ridge_range_hz
    flux      = np.abs(np.diff(ridge_hz, prepend=ridge_hz[0]))
    flux_max  = np.max(flux)
    flux_shape = flux / (flux_max + 1e-10) if flux_max > 0 else np.zeros_like(flux)

    t_in  = np.linspace(0, 1, len(f0_shape))
    t_out = np.linspace(0, 1, N_SHAPE_PTS)

    return {
        "f0_shape":   np.interp(t_out, t_in, f0_shape),
        "amp_shape":  np.interp(t_out, t_in, amp_norm),
        "flux_shape": np.interp(t_out, t_in, flux_shape),
        "f0_min":     ridge_min,
        "f0_max":     ridge_max,
        "f0_mean":    np.mean(ridge_hz),
        "f0_range":   ridge_range_hz,
        "dur_ms":     dur_ms,
    }


def extract_all_geometries(corpus_dir):
    geometries = []
    if not os.path.isdir(corpus_dir):
        return geometries

    audio_ext = ('.mp3', '.wav', '.flac', '.ogg')
    all_files = sorted([f for f in os.listdir(corpus_dir)
                        if f.lower().endswith(audio_ext)])
    if not all_files:
        return geometries

    print(f"Extracting corpus geometry from {corpus_dir} ...")
    print(f"{'─'*65}")
    total_valid = 0

    for fname in all_files:
        fpath = os.path.join(corpus_dir, fname)
        try:
            y, sr = librosa.load(fpath, sr=SR, mono=True)
        except Exception:
            continue

        intervals  = librosa.effects.split(
            y, top_db=TOP_DB, frame_length=N_FFT, hop_length=HOP_LENGTH)
        file_valid = 0

        for start, end in intervals:
            segment = y[start:end]
            dur_ms  = len(segment) / sr * 1000
            if not (MIN_DUR_MS < dur_ms < MAX_DUR_MS):
                continue
            geom = extract_call_geometry(segment, sr)
            if geom is not None:
                geom["source"] = fname
                geometries.append(geom)
                file_valid  += 1
                total_valid += 1

        if file_valid > 0:
            print(f"  {fname[:55]:<55} {file_valid:>3} calls")

    print(f"{'─'*65}")
    print(f"Valid geometries: {total_valid}")
    return geometries


def find_structural_invariant(geometries):
    shape_matrix = np.array([
        np.concatenate([g["f0_shape"], g["amp_shape"], g["flux_shape"]])
        for g in geometries
    ])

    pca = PCA(n_components=min(4, len(geometries)))
    pca.fit(shape_matrix)

    print("\nShape PCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{i+1}: {v:.4f}  {'█'*int(v*50)}")

    comp    = pca.components_[0]
    inv_f0  = comp[:N_SHAPE_PTS]
    inv_amp = comp[N_SHAPE_PTS:2*N_SHAPE_PTS]

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

    print(f"\nCorpus statistics (overriding SONGBIRD estimates):")
    print(f"  F0 p25/p50/p75:  "
          f"{stats['f0_mean_p25']:.0f} / "
          f"{stats['f0_mean_p50']:.0f} / "
          f"{stats['f0_mean_p75']:.0f} Hz")
    print(f"  F0 range median: {stats['f0_range_p50']:.0f} Hz")
    print(f"  Duration median: {stats['dur_p50']:.0f} ms")

    return inv_f0, inv_amp, stats


# ─────────────────────────────────────────────────────────────────
# CALL SHAPE LIBRARY
# All nine calls from v7, preserved exactly.
# Each returns: (f0_shape, amp_shape, dur_ms, gap_ms,
#                n_repeats, label, range_mult)
#
# Shapes are normalised [0,1] over N_SHAPE_PTS.
# Absolute frequencies are set at synthesis time via species profile.
# ─────────────────────────────────────────────────────────────────

def shape_i_am_here(inv_f0=None, inv_amp=None, n=N_SHAPE_PTS):
    """
    CALL 1 — I AM HERE
    Position announcement / flock integration request.
    Rising FM to t=77%, terminal 0.719 (come to me, not go there).
    Amplitude: onset burst, near-silence at t=13%, peak at t=48%.
    Duration 163ms. Gap 800ms. 3 repeats.

    Uses empirical PCA invariant when corpus is available.
    Falls back to geometric approximation otherwise.
    """
    if inv_f0 is not None and inv_amp is not None:
        return inv_f0.copy(), inv_amp.copy(), 163, 800, 3, "I_AM_HERE", 1.0

    # Geometric fallback: rising FM, terminal drop to 0.719
    t  = np.linspace(0, 1, n)
    f0 = np.where(
        t < 0.77,
        t / 0.77,
        1.0 - (t - 0.77) / 0.23 * (1.0 - 0.719)
    ).clip(0, 1)

    amp = np.zeros(n)
    amp[0] = 0.7
    amp[1] = 0.05
    peak   = int(0.48 * n)
    amp[1:peak] = np.linspace(0.05, 1.0, peak - 1)
    amp[peak:]  = np.linspace(1.0, 0.231, n - peak)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 163, 800, 3, "I_AM_HERE", 1.0


def shape_safe(n=N_SHAPE_PTS):
    """
    CALL 2 — SAFE / SETTLED
    Stable basin announcement.
    Flat gentle undulation — no net FM direction.
    Sustained plateau amplitude.
    Terminal returns to starting position — loop closed, resolved.
    Duration 280ms. Gap 1200ms. 3 repeats.
    """
    t   = np.linspace(0, 2 * np.pi, n)
    f0  = 0.5 + 0.1 * np.sin(t)
    f0  = (f0 - f0.min()) / (f0.max() - f0.min() + 1e-10)

    amp          = np.zeros(n)
    rise         = n // 5
    fall         = n // 5
    amp[:rise]       = np.linspace(0.0, 0.7, rise)
    amp[rise:n-fall] = 0.7
    amp[n-fall:]     = np.linspace(0.7, 0.0, fall)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 280, 1200, 3, "SAFE", 1.0


def shape_alarm(n=N_SHAPE_PTS):
    """
    CALL 3 — ALARM
    Predator / threat broadcast.
    Fast linear descent. Front-loaded amplitude.
    80ms. Tight 200ms gap. 6 repeats. HIGH register.
    Open terminal — unresolved, act NOW.
    ALWAYS follow with ALL_CLEAR when threat passes.
    """
    f0  = np.linspace(1.0, 0.2, n)
    amp = np.exp(-np.linspace(0, 3.5, n))
    amp /= (amp.max() + 1e-10)
    return f0, amp, 80, 200, 6, "ALARM", 1.0


def shape_resource(n=N_SHAPE_PTS):
    """
    CALL 4 — RESOURCE HERE
    Food / water location signal.
    Rising FM — same direction as I_AM_HERE.
    CRITICAL DISTINCTION: terminal stays at 0.97 (points OUTWARD).
      I_AM_HERE terminal: 0.719 (come to ME)
      RESOURCE terminal:  0.97  (go TOWARD THAT)
    Amplitude peaks at t=35%, sustains to t=70%.
    Duration 240ms. Gap 600ms. 4 repeats.

    ECONOMY RULE: If you transmit RESOURCE you must confirm
    with food. One failed resource signal degrades node trust.
    Signal first, place food immediately after.
    """
    rise_end      = int(0.80 * n)
    f0            = np.zeros(n)
    f0[:rise_end] = np.linspace(0.0, 1.0, rise_end)
    f0[rise_end:] = np.linspace(1.0, 0.97, n - rise_end)

    peak_pt     = int(0.35 * n)
    sustain_end = int(0.70 * n)
    amp         = np.zeros(n)
    amp[:peak_pt]            = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:sustain_end] = 1.0
    amp[sustain_end:]        = np.linspace(1.0, 0.20, n - sustain_end)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 240, 600, 4, "RESOURCE", 1.0


def shape_come_now(n=N_SHAPE_PTS):
    """
    CALL 5 — COME HERE NOW
    Maximum recruitment pull.
    Steeper FM rise than I_AM_HERE. Higher urgency encoding.
    Compressed 120ms. Tight 400ms gap. 5 repeats.

    NOTE: Do NOT use with RWBB — territorial misread risk.
    Use for songbird recruitment only.
    """
    steep_end      = int(0.60 * n)
    f0             = np.zeros(n)
    f0[:steep_end] = np.linspace(0.0, 0.85, steep_end)
    f0[steep_end:] = np.linspace(0.85, 0.5, n - steep_end)

    peak_pt = int(0.35 * n)
    amp     = np.zeros(n)
    amp[:peak_pt] = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:] = np.linspace(1.0, 0.1, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 120, 400, 5, "COME_NOW", 1.0


def shape_moving(n=N_SHAPE_PTS):
    """
    CALL 6 — I AM MOVING
    Flock movement / flight intention.
    Slow purposeful descent — rate distinguishes from ALARM panic.
    Amplitude peak at t=48% — cohesion midpoint (come with me).
    Terminal low stable 0.3 — settled new position exists.
    Register shifts downward across 3 repeats: trajectory moves
    through the space as it is transmitted.
    """
    f0      = np.linspace(1.0, 0.3, n)
    peak_pt = int(0.48 * n)
    amp     = np.zeros(n)
    amp[:peak_pt] = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:] = np.linspace(1.0, 0.15, n - peak_pt)
    amp /= (amp.max() + 1e-10)
    return f0, amp, 200, 500, 3, "MOVING", 1.0


def shape_all_clear(n=N_SHAPE_PTS):
    """
    CALL 7 — ALL CLEAR
    Alarm cancellation. Threat has passed.
    This is NOT SAFE. SAFE = baseline. ALL_CLEAR = transition.
    Gentle rise from mid (0.4) to stable high (0.8).
    Distributed amplitude — no front-loading (urgency is gone).
    Terminal stable high 0.8 — resolved and closed.
    Duration 200ms. Gap 600ms. 3 repeats.

    CRITICAL: Without ALL_CLEAR after ALARM, the network
    remains in alarm state. You cannot re-establish the
    resource node until ALL_CLEAR + SAFE are transmitted.
    """
    f0           = np.zeros(n)
    rise_end     = int(0.65 * n)
    f0[:rise_end] = np.linspace(0.4, 0.8, rise_end)
    f0[rise_end:] = 0.8

    amp  = np.zeros(n)
    rise = int(0.20 * n)
    fall = int(0.20 * n)
    amp[:rise]       = np.linspace(0.0, 0.75, rise)
    amp[rise:n-fall] = 0.75
    amp[n-fall:]     = np.linspace(0.75, 0.1, fall)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 200, 600, 3, "ALL_CLEAR", 1.0


def shape_where_are_you(n=N_SHAPE_PTS):
    """
    CALL 8 — WHERE ARE YOU
    Long-distance separation search.
    Full rising sweep — same direction as I_AM_HERE.
    BUT: range_mult=1.35 pushes ABOVE normal eigenfunction range.
    Terminal returns to MID (0.5) — open question, not resolved.
    HIGH register only in field — maximum penetration.
    Duration 230ms. Gap 400ms. 4 repeats.

    Use at session START when approaching from a distance.
    Wait for response before beginning working protocol.
    """
    f0            = np.zeros(n)
    rise_end      = int(0.70 * n)
    f0[:rise_end] = np.linspace(0.0, 1.0, rise_end)
    f0[rise_end:] = np.linspace(1.0, 0.5, n - rise_end)

    peak_pt     = int(0.40 * n)
    sustain_end = int(0.65 * n)
    amp         = np.zeros(n)
    amp[:peak_pt]            = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:sustain_end] = 1.0
    amp[sustain_end:]        = np.linspace(1.0, 0.25, n - sustain_end)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 230, 400, 4, "WHERE_ARE_YOU", WHERE_RANGE_MULT


def shape_acknowledge(n=N_SHAPE_PTS):
    """
    CALL 9 — ACKNOWLEDGE
    Dialogue maintenance. I received you, continue exchange.
    Minimal sweep (~25% of range). Low amplitude.
    This is the acoustic equivalent of a nod.
    Play ONCE after each flock vocalization.
    Do NOT loop — loop = new position announcement, not reply.
    Duration 90ms. 1 repeat only.
    """
    f0            = np.zeros(n)
    rise_end      = int(0.60 * n)
    f0[:rise_end] = np.linspace(0.2, 0.45, rise_end)
    f0[rise_end:] = np.linspace(0.45, 0.35, n - rise_end)

    amp      = np.zeros(n)
    peak_pt  = int(0.45 * n)
    amp[:peak_pt] = np.linspace(0.0, 0.55, peak_pt)
    amp[peak_pt:] = np.linspace(0.55, 0.0, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 90, 500, 1, "ACKNOWLEDGE", 1.0


# ─────────────────────────────────────────────────────────────────
# SYNTHESIS ENGINE
# ─────────────────────────────────────────────────────────────────

# MOVING shifts register downward across repeats to encode
# that the node itself is physically moving through space.
REGISTER_SHIFT_MOVING = {
    "LOW":  ["LOW",  "LOW",  "LOW"],
    "MID":  ["HIGH", "MID",  "LOW"],
    "HIGH": ["HIGH", "MID",  "LOW"],
}


def synthesize_call(f0_shape, amp_shape, profile,
                    register="MID", dur_ms=None,
                    range_mult=1.0,
                    sample_rate=SAMPLE_RATE):
    """
    Render a normalised (f0_shape, amp_shape) pair to audio
    using a species profile for absolute frequency placement.
    """
    f0_centre = {
        "LOW":  profile["f0_mean_p25"],
        "MID":  profile["f0_mean_p50"],
        "HIGH": profile["f0_mean_p75"],
    }[register]

    f0_range = profile["f0_range_p50"] * range_mult
    f0_abs   = (f0_shape * f0_range) + (f0_centre - f0_range / 2)
    f0_abs   = np.clip(f0_abs, 80, 12000)

    if dur_ms is None:
        dur_ms = profile["dur_p50"]

    n_samples = max(2, int(dur_ms * sample_rate / 1000))

    f0_t  = np.interp(np.linspace(0, N_SHAPE_PTS - 1, n_samples),
                      np.arange(N_SHAPE_PTS), f0_abs)
    amp_t = np.interp(np.linspace(0, N_SHAPE_PTS - 1, n_samples),
                      np.arange(N_SHAPE_PTS), amp_shape)

    h2 = profile.get("h2_ratio", H2_RATIO)
    h3 = profile.get("h3_ratio", H3_RATIO)

    phase  = 2 * np.pi * np.cumsum(f0_t) / sample_rate
    signal = (np.sin(phase)
              + h2 * np.sin(2 * phase)
              + h3 * np.sin(3 * phase))
    signal = signal * amp_t

    fade = min(int(0.005 * sample_rate), n_samples // 4)
    if fade > 0:
        signal[:fade]  *= np.linspace(0, 1, fade)
        signal[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal * (0.9 / peak)

    return signal, f0_abs


def build_sequence(calls_list, gap_ms, sample_rate=SAMPLE_RATE):
    gap   = np.zeros(int(gap_ms * sample_rate / 1000))
    parts = []
    for i, call in enumerate(calls_list):
        parts.append(call)
        if i < len(calls_list) - 1:
            parts.append(gap)
    return np.concatenate(parts)


def make_call_audio(call_spec, profile, register,
                    sample_rate=SAMPLE_RATE):
    """
    Synthesize a complete repeated call sequence from a call_spec tuple.
    Handles register-shifting for MOVING automatically.
    """
    f0_shape, amp_shape, dur_ms, gap_ms, n_repeats, label, range_mult = call_spec

    if label == "MOVING":
        reg_seq = REGISTER_SHIFT_MOVING[register]
        parts   = []
        for rep_reg in reg_seq:
            sig, _ = synthesize_call(f0_shape, amp_shape, profile,
                                     register=rep_reg, dur_ms=dur_ms,
                                     range_mult=range_mult,
                                     sample_rate=sample_rate)
            parts.append(sig)
        return build_sequence(parts, gap_ms, sample_rate)

    sig, _ = synthesize_call(f0_shape, amp_shape, profile,
                              register=register, dur_ms=dur_ms,
                              range_mult=range_mult,
                              sample_rate=sample_rate)
    return build_sequence([sig] * n_repeats, gap_ms, sample_rate)


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    dur = len(signal) / sample_rate
    kb  = len(out) * 2 / 1024
    print(f"  ✓ {os.path.basename(filename):<62}  {dur:.1f}s  {kb:.0f}KB")


def silence(seconds, sample_rate=SAMPLE_RATE):
    return np.zeros(int(seconds * sample_rate))


# ─────────────────────────────────────────────────────────────────
# PROTOCOL SEQUENCE BUILDERS
# ─────────────────────────────────────────────────────────────────

def build_working_protocol(profile, inv_f0=None, inv_amp=None,
                            register="MID", sample_rate=SAMPLE_RATE):
    """
    THE CONFIRMED FIELD PROTOCOL
    I_AM_HERE → RESOURCE → SAFE

    This is the sequence currently working.
    Attracting: finches, sparrows, chickadees, RWBB (occasional),
    mallard duck (emerging).

    PROCEDURE:
      1. Play I_AM_HERE (3×) — announce yourself as a flock node
      2. Wait 3 seconds — let the signal propagate
      3. Place food at the site NOW (between I_AM_HERE and RESOURCE)
         OR signal RESOURCE then immediately place food
      4. Play RESOURCE (4×) — direct to the food location
      5. Wait 3 seconds
      6. Play SAFE (3×) — confirm the site is settled and safe

    Gap between calls: 3 seconds — allow network to register.

    RESOURCE SIGNAL THEORY NOTE:
      Signal BEFORE physical investigation, not after.
      The substrate signal creates trust that precedes approach.
      Birds responding to signal trust > birds responding to food.
      The relationship is to YOU, not to the food.
      Remove food temporarily: relationship persists.
      Remove yourself: relationship is disrupted.
    """
    iam  = make_call_audio(shape_i_am_here(inv_f0, inv_amp), profile, register)
    res  = make_call_audio(shape_resource(), profile, register)
    safe = make_call_audio(shape_safe(), profile, register)

    return np.concatenate([
        silence(1.0),
        iam,  silence(3.0),
        res,  silence(3.0),
        safe,
        silence(1.0),
    ])


def build_full_session(profile, inv_f0=None, inv_amp=None,
                       register="MID", sample_rate=SAMPLE_RATE):
    """
    FULL SESSION PROTOCOL
    WHERE_ARE_YOU (HIGH) → I_AM_HERE → RESOURCE → SAFE → ACKNOWLEDGE

    Use at the start of each session when approaching the area.
    WHERE_ARE_YOU (HIGH register, extended range) is the
    long-distance initial attractor — it reaches the flock
    before you are in visual range.

    PROCEDURE:
      Phase 1 — Long-distance entry (still 20+ meters out):
        Play WHERE_ARE_YOU (HIGH) — 4 repeats
        Pause 5 seconds — listen for response
        Begin walking toward the site

      Phase 2 — Site arrival (place food as you arrive):
        Play working protocol: I_AM_HERE → RESOURCE → SAFE

      Phase 3 — Node maintenance (once birds present):
        Play ACKNOWLEDGE once after each flock vocalization
        Do NOT loop ACKNOWLEDGE — it becomes a new announcement
    """
    where = make_call_audio(shape_where_are_you(), profile, "HIGH")
    iam   = make_call_audio(shape_i_am_here(inv_f0, inv_amp), profile, register)
    res   = make_call_audio(shape_resource(), profile, register)
    safe  = make_call_audio(shape_safe(), profile, register)
    ack   = make_call_audio(shape_acknowledge(), profile, register)

    return np.concatenate([
        silence(1.0),
        where, silence(5.0),      # long-distance entry — listen here
        iam,   silence(3.0),      # position announcement
        res,   silence(3.0),      # resource signal — place food now
        safe,  silence(3.0),      # settle the network
        ack,                      # acknowledge first response
        silence(1.0),
    ])


def build_dialogue_sequence(profile, inv_f0=None, inv_amp=None,
                             n_exchanges=5, sample_rate=SAMPLE_RATE):
    """
    DIALOGUE MAINTENANCE SEQUENCE
    I_AM_HERE → [ACKNOWLEDGE with response window × n_exchanges]

    Use when the flock is present and vocalising.
    The 3-second pause after each ACKNOWLEDGE is your
    listening window — in field use, play ACKNOWLEDGE
    only after a flock vocalization.

    The pattern simulated here:
      I_AM_HERE (establishes exchange context)
      ACKNOWLEDGE (you speak)
      [3s pause — flock speaks here]
      ACKNOWLEDGE again
      [3s pause]
      ... repeating

    n_exchanges=5 generates a ~40 second dialogue pattern.
    """
    iam = make_call_audio(shape_i_am_here(inv_f0, inv_amp), profile, "MID")
    ack = make_call_audio(shape_acknowledge(), profile, "MID")

    parts = [silence(1.0), iam, silence(3.0)]
    for _ in range(n_exchanges):
        parts.extend([ack, silence(3.0)])
    parts.append(silence(1.0))

    return np.concatenate(parts)


def build_rwbb_protocol(profile_rwbb, profile_songbird,
                        inv_f0=None, inv_amp=None,
                        sample_rate=SAMPLE_RATE):
    """
    RED-WINGED BLACKBIRD PROTOCOL
    SAFE (RWBB) → RESOURCE (RWBB) → I_AM_HERE (songbird, MID)

    FIELD CONTEXT:
      RWBB male has established the area as his territory.
      He comes when you signal — occasionally.
      This is advanced node integration: a territorial species
      is treating your node as compatible with his territory.
      This is NOT a confrontation — it is recognition.

    CONSTRAINT — DO NOT USE:
      COME_NOW with RWBB: may be read as territorial challenge
      WHERE_ARE_YOU at max range: boundary assertion signal
      High register I_AM_HERE in RWBB profile: overpowering

    PROCEDURE:
      1. SAFE (RWBB MID) — confirm non-competitive presence
         in his frequency register
      2. RESOURCE (RWBB MID) — confirm you are a reliable source
         Use his register: shows you know he is there
      3. I_AM_HERE (songbird MID) — re-state your species-neutral
         flock node identity — not his territory, but compatible

    Gap: 4 seconds — respect territorial timing.
    Monitor: does he respond more to RWBB-profile calls
    or songbird-profile calls? Record this.
    """
    safe_rwbb = make_call_audio(shape_safe(), profile_rwbb, "MID")
    res_rwbb  = make_call_audio(shape_resource(), profile_rwbb, "MID")
    iam_song  = make_call_audio(
        shape_i_am_here(inv_f0, inv_amp), profile_songbird, "MID")

    return np.concatenate([
        silence(1.0),
        safe_rwbb, silence(4.0),
        res_rwbb,  silence(4.0),
        iam_song,
        silence(1.0),
    ])


def build_mallard_protocol(profile_mallard, sample_rate=SAMPLE_RATE):
    """
    MALLARD DUCK PROTOCOL
    SAFE (MALLARD) → RESOURCE (MALLARD) → RESOURCE (MALLARD LOW)

    FIELD CONTEXT:
      Mallard duck appearing is a low-frequency channel event.
      The duck is resource-driven — the flock substrate signals
      are reaching it because its contact call range (400–900 Hz)
      overlaps with the lower harmonic content of your signals.
      It is not integrating into the songbird substrate —
      it is detecting a resource node through its own channel.

    PROCEDURE:
      1. SAFE (MID) — low-frequency settled state broadcast
      2. RESOURCE (MID) — pointing signal at normal duck range
      3. RESOURCE (LOW) — heavier harmonic content,
         more overlap with duck vocal register
      Place food near water if possible after step 2.

    OBSERVATION QUESTIONS:
      Does the duck approach before or after food is placed?
      Before = substrate signal response (substrate entry confirmed)
      After  = visual/olfactory discovery (resource-only response)
      Record the delta — it tells you whether you have substrate
      contact or just a reliable food source.
    """
    safe  = make_call_audio(shape_safe(), profile_mallard, "MID")
    res_m = make_call_audio(shape_resource(), profile_mallard, "MID")
    res_l = make_call_audio(shape_resource(), profile_mallard, "LOW")

    return np.concatenate([
        silence(1.0),
        safe,  silence(3.0),
        res_m, silence(3.0),
        res_l,
        silence(1.0),
    ])


def build_alarm_recovery(profile, sample_rate=SAMPLE_RATE):
    """
    ALARM RECOVERY SEQUENCE
    ALARM (HIGH) → ALL_CLEAR (MID) → SAFE (MID)

    Use when an actual threat appears (hawk, cat, dog).
    Transmit ALARM immediately when threat is present.
    Wait until threat is gone, then transmit ALL_CLEAR + SAFE.

    CRITICAL: Without ALL_CLEAR the network stays in alarm
    state. You cannot re-establish the resource node until
    the full recovery sequence is transmitted.
    Signal accuracy rule: only transmit ALL_CLEAR when the
    threat is genuinely gone. False ALL_CLEAR degrades
    the alarm signal's trust — the most critical signal
    in the vocabulary.

    TIMING:
      ALARM: play immediately, repeat until threat is gone
      ALL_CLEAR: 5 seconds after threat disappears
      SAFE: follow ALL_CLEAR directly
      Working protocol: re-establish after further 3 minutes
    """
    alarm     = make_call_audio(shape_alarm(), profile, "HIGH")
    all_clear = make_call_audio(shape_all_clear(), profile, "MID")
    safe      = make_call_audio(shape_safe(), profile, "MID")

    return np.concatenate([
        silence(1.0),
        alarm,     silence(5.0),
        all_clear, silence(5.0),
        safe,
        silence(1.0),
    ])


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("OC-OBS-005 — WILD FLOCK SUBSTRATE PROTOCOL — v8")
    print("OrganismCore — Eric Robert Lawson")
    print("=" * 65)
    print()
    print("DOCUMENTED SUBSTRATE STATE:")
    print("  Confirmed:  Finches, sparrows, chickadees (primary)")
    print("  Territorial: Red-winged blackbird male (established)")
    print("  Emerging:   Mallard duck (low-frequency channel)")
    print("  Adjacent:   Squirrel (resource-confirmed, non-avian)")
    print()

    # ── Resolve profiles ──────────────────────────────────────
    profile_songbird = SPECIES_PROFILES["SONGBIRD"].copy()
    profile_rwbb     = SPECIES_PROFILES["RWBB"].copy()
    profile_mallard  = SPECIES_PROFILES["MALLARD"].copy()

    inv_f0 = inv_amp = None

    if HAS_AUDIO_LIBS:
        geometries = extract_all_geometries(CORPUS_DIR)
        if len(geometries) >= 10:
            inv_f0, inv_amp, stats = find_structural_invariant(geometries)
            profile_songbird.update({
                "f0_mean_p25":  stats["f0_mean_p25"],
                "f0_mean_p50":  stats["f0_mean_p50"],
                "f0_mean_p75":  stats["f0_mean_p75"],
                "f0_range_p50": stats["f0_range_p50"],
                "dur_p50":      stats["dur_p50"],
            })
            print(f"\n  Corpus: {len(geometries)} calls — "
                  f"SONGBIRD profile updated from corpus.")
        elif os.path.isdir(CORPUS_DIR):
            print(f"\n  Corpus: {len(geometries)} calls found "
                  f"(need ≥10). Using estimated SONGBIRD profile.")
        else:
            print(f"\n  No corpus directory found at {CORPUS_DIR}.")
            print("  Using estimated species profiles.")
    else:
        print("\n  librosa/sklearn not available.")
        print("  Install: pip install librosa scikit-learn")
        print("  Using estimated species profiles.")

    print()
    print(f"  SONGBIRD  F0: {profile_songbird['f0_mean_p25']:.0f} / "
          f"{profile_songbird['f0_mean_p50']:.0f} / "
          f"{profile_songbird['f0_mean_p75']:.0f} Hz  "
          f"(LOW/MID/HIGH)")
    print(f"  RWBB      F0: {profile_rwbb['f0_mean_p25']:.0f} / "
          f"{profile_rwbb['f0_mean_p50']:.0f} / "
          f"{profile_rwbb['f0_mean_p75']:.0f} Hz  "
          f"(LOW/MID/HIGH)")
    print(f"  MALLARD   F0: {profile_mallard['f0_mean_p25']:.0f} / "
          f"{profile_mallard['f0_mean_p50']:.0f} / "
          f"{profile_mallard['f0_mean_p75']:.0f} Hz  "
          f"(LOW/MID/HIGH)")
    print()
    print("=" * 65)

    # ── 1. Working Protocol (confirmed) ───────────────────────
    print("\n── 1. WORKING PROTOCOL  (I_AM_HERE → RESOURCE → SAFE)")
    for reg in ["LOW", "MID", "HIGH"]:
        audio = build_working_protocol(
            profile_songbird, inv_f0, inv_amp, register=reg)
        save_wav(audio,
                 os.path.join(OUTPUT_DIR, f"v8_WORKING_PROTOCOL_{reg}.wav"))

    # ── 2. Full Session ───────────────────────────────────────
    print("\n── 2. FULL SESSION  "
          "(WHERE_ARE_YOU → I_AM_HERE → RESOURCE → SAFE → ACK)")
    for reg in ["LOW", "MID", "HIGH"]:
        audio = build_full_session(
            profile_songbird, inv_f0, inv_amp, register=reg)
        save_wav(audio,
                 os.path.join(OUTPUT_DIR, f"v8_FULL_SESSION_{reg}.wav"))

    # ── 3. Dialogue Sequence ──────────────────────────────────
    print("\n── 3. DIALOGUE SEQUENCE  (I_AM_HERE → ACKNOWLEDGE × 5)")
    audio = build_dialogue_sequence(
        profile_songbird, inv_f0, inv_amp, n_exchanges=5)
    save_wav(audio, os.path.join(OUTPUT_DIR, "v8_DIALOGUE_SEQUENCE.wav"))

    # ── 4. RWBB Protocol ──────────────────────────────────────
    print("\n── 4. RWBB PROTOCOL  "
          "(SAFE_RWBB → RESOURCE_RWBB → I_AM_HERE_SONGBIRD)")
    audio = build_rwbb_protocol(
        profile_rwbb, profile_songbird, inv_f0, inv_amp)
    save_wav(audio, os.path.join(OUTPUT_DIR, "v8_RWBB_PROTOCOL.wav"))

    # ── 5. Mallard Protocol ───────────────────────────────────
    print("\n── 5. MALLARD PROTOCOL  "
          "(SAFE_MALLARD → RESOURCE_MALLARD × 2)")
    audio = build_mallard_protocol(profile_mallard)
    save_wav(audio, os.path.join(OUTPUT_DIR, "v8_MALLARD_PROTOCOL.wav"))

    # ── 6. Alarm Recovery ─────────────────────────────────────
    print("\n── 6. ALARM RECOVERY  (ALARM → ALL_CLEAR → SAFE)")
    audio = build_alarm_recovery(profile_songbird)
    save_wav(audio, os.path.join(OUTPUT_DIR, "v8_ALARM_RECOVERY.wav"))

    # ── 7. Individual calls — all profiles, all registers ─────
    # Full vocabulary for calibration
    ALL_CALL_SHAPES = [
        shape_i_am_here(inv_f0, inv_amp),
        shape_resource(),
        shape_safe(),
        shape_acknowledge(),
        shape_where_are_you(),
        shape_alarm(),
        shape_all_clear(),
        shape_come_now(),
        shape_moving(),
    ]

    print("\n── 7. INDIVIDUAL CALLS — SONGBIRD profile")
    for spec in ALL_CALL_SHAPES:
        label = spec[5]
        for reg in ["LOW", "MID", "HIGH"]:
            audio = make_call_audio(spec, profile_songbird, reg)
            save_wav(audio, os.path.join(
                OUTPUT_DIR, f"v8_{label}_SONGBIRD_{reg}.wav"))

    # RWBB: safe + resource + alarm + all_clear only
    # (no recruitment calls per territorial constraint)
    RWBB_CALLS = [
        shape_safe(),
        shape_resource(),
        shape_acknowledge(),
        shape_alarm(),
        shape_all_clear(),
    ]
    print("\n── 8. INDIVIDUAL CALLS — RWBB profile")
    for spec in RWBB_CALLS:
        label = spec[5]
        for reg in ["LOW", "MID", "HIGH"]:
            audio = make_call_audio(spec, profile_rwbb, reg)
            save_wav(audio, os.path.join(
                OUTPUT_DIR, f"v8_{label}_RWBB_{reg}.wav"))

    # Mallard: safe + resource only
    MALLARD_CALLS = [shape_safe(), shape_resource()]
    print("\n── 9. INDIVIDUAL CALLS — MALLARD profile")
    for spec in MALLARD_CALLS:
        label = spec[5]
        for reg in ["LOW", "MID", "HIGH"]:
            audio = make_call_audio(spec, profile_mallard, reg)
            save_wav(audio, os.path.join(
                OUTPUT_DIR, f"v8_{label}_MALLARD_{reg}.wav"))

    # ── Summary ───────────────────────────────────────────────
    print()
    print("=" * 65)
    print("V8 COMPLETE")
    print("=" * 65)
    print()
    print("DAILY FIELD USE:")
    print()
    print("  ① APPROACH (before visual contact with site):")
    print("    v8_FULL_SESSION_MID.wav")
    print("    WHERE_ARE_YOU (HIGH) × 4 → 5s listen → working protocol")
    print()
    print("  ② STANDARD SESSION (confirmed working):")
    print("    v8_WORKING_PROTOCOL_MID.wav")
    print("    I_AM_HERE × 3 → 3s → RESOURCE × 4 → 3s → SAFE × 3")
    print("    PLACE FOOD between I_AM_HERE and RESOURCE.")
    print("    Signal before food. Not after.")
    print()
    print("  ③ ACTIVE DIALOGUE (flock present, vocalising):")
    print("    v8_ACKNOWLEDGE_SONGBIRD_MID.wav")
    print("    Play ONCE after each flock call. Do not loop.")
    print("    Or use: v8_DIALOGUE_SEQUENCE.wav to practice pattern.")
    print()
    print("  ④ WHEN RWBB IS PRESENT:")
    print("    v8_RWBB_PROTOCOL.wav  (then return to songbird protocol)")
    print("    SAFE_RWBB → RESOURCE_RWBB → I_AM_HERE_SONGBIRD")
    print("    Do NOT use COME_NOW or WHERE_ARE_YOU with RWBB.")
    print()
    print("  ⑤ WHEN MALLARD IS PRESENT:")
    print("    v8_MALLARD_PROTOCOL.wav")
    print("    SAFE_MALLARD → RESOURCE_MALLARD × 2")
    print("    Note whether duck arrives before or after food is placed.")
    print("    Before = substrate contact.  After = visual discovery.")
    print()
    print("  ⑥ ACTIVE THREAT (hawk, cat, dog):")
    print("    v8_ALARM_RECOVERY.wav")
    print("    ALARM (HIGH) × 6 → 5s → ALL_CLEAR × 3 → SAFE × 3")
    print("    Only transmit ALL_CLEAR when threat is ACTUALLY gone.")
    print("    False ALL_CLEAR degrades the alarm signal permanently.")
    print()
    print("  ⑦ REGISTER CALIBRATION (find your flock's register):")
    print("    v8_I_AM_HERE_SONGBIRD_LOW.wav")
    print("    v8_I_AM_HERE_SONGBIRD_MID.wav  ← start here")
    print("    v8_I_AM_HERE_SONGBIRD_HIGH.wav")
    print("    The register that produces the fastest first response")
    print("    is your calibrated baseline. Use it consistently.")
    print()
    print("OBSERVATION RECORD (after each session):")
    print("  - Species present and arrival order")
    print("  - Which call produced first response")
    print("  - Which register produced first response")
    print("  - RWBB: responded to RWBB profile or songbird profile?")
    print("  - Mallard: arrived before or after food placement?")
    print("  - Response time delta (signal → first bird arrival)")
    print("  - Any new species not previously documented")
    print("  - Squirrel: signal-triggered arrival or food-triggered?")
    print()
    print("ECONOMY RULES (The_Flock_Economy.md):")
    print("  Signal accuracy IS the currency.")
    print("  Node trust IS the wealth.")
    print("  Integration IS the return on investment.")
    print("  Never transmit a signal you cannot confirm.")
    print("=" * 65)


if __name__ == "__main__":
    main()
