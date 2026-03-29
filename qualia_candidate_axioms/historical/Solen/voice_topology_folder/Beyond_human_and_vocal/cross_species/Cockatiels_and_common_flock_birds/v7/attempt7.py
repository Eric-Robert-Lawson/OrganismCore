import numpy as np
from scipy.io import wavfile
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA
import librosa
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# COCKATIEL FLOCK VOCABULARY — V7
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
#
# ADVANCE OVER V6:
#   Nine call types — complete functional vocabulary.
#   Each call type rendered at LOW / MID / HIGH register.
#   27 individual files + 9 probe files = 36 outputs.
#
#   CALL TYPES:
#     1. I_AM_HERE      — rising FM, mid-high terminal (0.719)
#                         position announcement / integration
#                         EMPIRICAL PCA INVARIANT
#
#     2. SAFE           — flat undulation, plateau amp
#                         settled state broadcast
#
#     3. ALARM          — fast descent, front-loaded amp
#                         predator / threat broadcast
#
#     4. RESOURCE       — rising FM, stay-high terminal (0.97)
#                         water / food location
#
#     5. COME_NOW       — steep rise, compressed duration
#                         maximum recruitment pull
#
#     6. MOVING         — slow descent, shifting register
#                         flock movement / flight intention
#
#     7. ALL_CLEAR      — gentle rise to stable high
#                         alarm cancellation / threat passed
#                         transition signal — not same as SAFE
#
#     8. WHERE_ARE_YOU  — extended range, high amplitude
#                         long-distance separation search
#                         pushes above normal eigenfunction range
#                         open terminal — waiting for answer
#
#     9. ACKNOWLEDGE    — minimal sweep, low amplitude
#                         I received you / continue exchange
#                         close-range bidirectional dialogue
#
#   SYNTHESIS PRINCIPLE:
#     All calls derived from corpus eigenfunction space.
#     f0_centre and f0_range anchored to corpus statistics.
#     Only the SHAPE (trajectory geometry) differs.
#     Geometric accuracy is the quality criterion.
#     No spectral elaboration — clean eigenfunction positions.
#
#   FIELD USE ORDER:
#     WHERE_ARE_YOU     — long-distance initial attraction
#     I_AM_HERE         — position announcement on approach
#     SAFE              — settle the network
#     ACKNOWLEDGE       — maintain dialogue
#     RESOURCE          — direct to location
#     COME_NOW          — urgent recruitment
#     MOVING            — coordinate movement
#     ALL_CLEAR         — cancel alarm after ALARM
#     ALARM             — threat broadcast
#
# ─────────────────────────────────────────────────────────────

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

# WHERE_ARE_YOU pushes above the normal corpus range.
# This multiplier extends f0_range for that call only.
WHERE_RANGE_MULT = 1.35


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
    dur_ms                    = len(segment) / sr * 1000
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
        "f0_shape":   np.interp(t_out, t_in, f0_shape),
        "amp_shape":  np.interp(t_out, t_in, amp_shape),
        "flux_shape": np.interp(t_out, t_in, flux_shape),
        "f0_min":     ridge_min,
        "f0_max":     ridge_max,
        "f0_mean":    np.mean(ridge_hz),
        "f0_range":   ridge_range_hz,
        "dur_ms":     dur_ms,
        "ridge_hz":   ridge_hz,
        "amp_raw":    amp_norm,
    }


# ── CORPUS EXTRACTION ─────────────────────────────────────────

def extract_all_geometries(corpus_dir):
    geometries = []
    audio_ext  = ('.mp3', '.wav', '.flac', '.ogg')
    all_files  = sorted([f for f in os.listdir(corpus_dir)
                         if f.lower().endswith(audio_ext)])

    print("Extracting call geometry (spectrogram ridge)...")
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

    print("\nShape PCA variance explained:")
    for i, v in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{i+1}: {v:.4f}  {'█'*int(v*50)}")

    inv     = pca.components_[0]
    inv_f0  = inv[:N_SHAPE_PTS]
    inv_amp = inv[N_SHAPE_PTS:2*N_SHAPE_PTS]

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

    print("\nStructural invariant F0 shape:")
    for i, v in enumerate(inv_f0):
        pct = i / (N_SHAPE_PTS - 1) * 100
        print(f"  t={pct:4.0f}%  "
              f"{'█'*int(v*40)}{'·'*(40-int(v*40))}  {v:.3f}")

    print("\nStructural invariant amplitude shape:")
    for i, v in enumerate(inv_amp):
        pct = i / (N_SHAPE_PTS - 1) * 100
        print(f"  t={pct:4.0f}%  "
              f"{'█'*int(v*40)}{'·'*(40-int(v*40))}  {v:.3f}")

    return inv_f0, inv_amp, stats


# ── CALL SHAPE LIBRARY ────────────────────────────────────────
#
# Returns: (f0_shape, amp_shape, dur_ms, gap_ms,
#           n_repeats, label, range_mult)
#
# range_mult: multiplier on corpus f0_range_p50.
#   1.0  = normal eigenfunction space (all calls except WHERE)
#   >1.0 = extends above normal range (WHERE_ARE_YOU only)
#
# All shapes normalised [0,1] over N_SHAPE_PTS.
# ─────────────────────────────────────────────────────────────

def shape_i_am_here(inv_f0, inv_amp):
    """
    CALL 1 — I AM HERE
    Empirical PCA invariant used directly.
    Rising FM sweep 0→1 peak at t=77%, terminal 0.719.
    Amplitude: onset burst, near-silence at t=13%,
    peak at t=48%, decay to 0.231.
    Duration 163ms. Gap 800ms. 3 repeats.
    Morton 1977, Templeton 2005, Zdenek 2020.
    FULLY CONFIRMED.
    """
    return (inv_f0.copy(), inv_amp.copy(),
            163, 800, 3, "I_AM_HERE", 1.0)


def shape_safe(n=N_SHAPE_PTS):
    """
    CALL 2 — SAFE / SETTLED
    Flat gentle undulation ±0.1 around 0.5.
    No net FM direction — no approach/retreat signal.
    Sustained amplitude plateau 0.7 from t=20% to t=80%.
    Terminal returns to starting position — loop closed.
    Duration 280ms. Gap 1200ms. 3 repeats.
    Hailman 1989, Catchpole & Slater 2008, Morton 1977.
    CONFIRMED.
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
    Fast linear descent 1.0→0.2.
    Front-loaded exponential amplitude decay from onset.
    Short 80ms. Rapid 200ms gap. 6 repeats. HIGH register.
    Open terminal — state is unresolved, respond NOW.
    Morton 1977, Magrath 2015, Marler 1955, Ficken 1978.
    MOST CONFIRMED CALL IN VOCABULARY.
    """
    f0  = np.linspace(1.0, 0.2, n)

    amp = np.exp(-np.linspace(0, 3.5, n))
    amp /= (amp.max() + 1e-10)

    return f0, amp, 80, 200, 6, "ALARM", 1.0


def shape_resource(n=N_SHAPE_PTS):
    """
    CALL 4 — RESOURCE HERE
    Rising FM identical direction to I_AM_HERE.
    CRITICAL DISTINCTION from I_AM_HERE:
      terminal stays at 0.97 — does not fall back.
      Trajectory points outward to external basin.
      I_AM_HERE terminal: 0.719 (come to me)
      RESOURCE terminal:  0.97  (go toward that)
    Amplitude peaks early at t=35%, sustains to t=70%.
    Duration 240ms. Gap 600ms. 4 repeats.
    Hailman 1989, Templeton & Greene 2007.
    Terminal resolution distinction: OrganismCore advance.
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
    amp[sustain_end:]        = np.linspace(
        1.0, 0.20, n - sustain_end)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 240, 600, 4, "RESOURCE", 1.0


def shape_come_now(n=N_SHAPE_PTS):
    """
    CALL 5 — COME HERE NOW
    Steeper FM rise than I_AM_HERE.
    Reaches 0.85 by t=60% — faster rate = higher urgency.
    Amplitude peaks earlier at t=35%.
    Terminal mid 0.5 — still pulling, not fully resolved.
    Compressed 120ms. Tight 400ms gap. 5 repeats.
    Morton 1977 (FM rate encodes urgency),
    Templeton 2005, Bradbury & Vehrencamp 2011.
    Individual parameters confirmed. Combined profile:
    OrganismCore advance.
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
    Slow purposeful descent 1.0→0.3.
    Rate of change is SLOW — this distinguishes
    purposeful movement from alarm panic.
    Amplitude peak at t=48% — cohesion midpoint structure,
    same as I_AM_HERE: come WITH me as I move.
    Terminal low stable 0.3 — settled new position exists.
    Register shifts downward across 3 repeats:
    the trajectory moves through the space as transmitted.
    Duration 200ms. Gap 500ms.
    Engesser 2016, Morton 1977, Catchpole & Slater 2008.
    Register shift encoding: OrganismCore advance.
    """
    f0 = np.linspace(1.0, 0.3, n)

    peak_pt = int(0.48 * n)
    amp     = np.zeros(n)
    amp[:peak_pt] = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:] = np.linspace(1.0, 0.15, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 200, 500, 3, "MOVING", 1.0


def shape_all_clear(n=N_SHAPE_PTS):
    """
    CALL 7 — ALL CLEAR
    Alarm cancellation / threat passed.
    This is NOT the same as SAFE.
    SAFE = baseline settled state.
    ALL_CLEAR = transition signal: alarm state is ending,
    return to normal navigation.

    Geometric structure:
    F0: starts at mid (0.4), rises gently to stable high (0.8).
      Recovery from alarm register back toward normal range.
      Not a full rising sweep — a partial, gentle ascent.
      The trajectory says: things are returning to normal.
    Amplitude: gradual onset, distributed plateau, gradual decay.
      No front-loading — the urgency of alarm is gone.
      Energy is even — the state is stabilising.
    Terminal: stable high 0.8 — resolved, settled.
      Not open like alarm. Closed, stable.
    Duration 200ms — longer than alarm, shorter than safe.
    Gap 600ms — slower than alarm, faster than safe.
    3 repeats — confirm the state transition.

    Krams et al. 2012 (post-alarm call structure in mixed flocks).
    Morton 1977 (return to stable FM position after alarm).
    Not geometrically characterised in literature.
    OrganismCore derivation.
    """
    # Gentle rise from mid to stable high
    f0 = np.zeros(n)
    rise_end      = int(0.65 * n)
    f0[:rise_end] = np.linspace(0.4, 0.8, rise_end)
    f0[rise_end:] = np.linspace(0.8, 0.8, n - rise_end)  # holds

    # Distributed amplitude — no urgency front-loading
    amp          = np.zeros(n)
    rise         = int(0.20 * n)
    fall         = int(0.20 * n)
    amp[:rise]       = np.linspace(0.0, 0.75, rise)
    amp[rise:n-fall] = 0.75
    amp[n-fall:]     = np.linspace(0.75, 0.1, fall)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 200, 600, 3, "ALL_CLEAR", 1.0


def shape_where_are_you(n=N_SHAPE_PTS):
    """
    CALL 8 — WHERE ARE YOU
    Long-distance separation search call.
    This is NOT I_AM_HERE.
    I_AM_HERE = I am present, integrate me (normal range).
    WHERE_ARE_YOU = I am separated, I need to locate the
    network (extended range, higher energy, open terminal).

    Geometric structure:
    F0: full rising sweep — same direction as I_AM_HERE.
      BUT: uses WHERE_RANGE_MULT=1.35 to push ABOVE the
      normal corpus eigenfunction range.
      A navigator at the edge of the network extends its
      signal beyond the normal contact call range to reach
      distant nodes.
      Terminal: returns to MID (0.5) — open question.
      Not resolved. Waiting for answer.
      The call does not land. It asks.
    Amplitude: HIGHER than I_AM_HERE — maximum energy.
      Peaks at t=40%, sustained longer.
      The navigator is committing full energy to the search.
    Duration: 230ms — longer than I_AM_HERE (163ms).
      The extended duration carries further.
    Gap: 400ms — urgent repetition, needs answer.
    4 repeats — persistent search.
    HIGH register mandatory — maximum penetration.

    Baker 1974 (cockatiel long-distance separation call
    distinct from contact call — higher amplitude, extended
    duration, higher frequency).
    Hile 2000 (individually distinct separation calls
    for long-distance recognition).
    Extended range synthesis: OrganismCore advance.
    """
    # Full sweep but with open terminal — returns to mid
    f0 = np.zeros(n)
    rise_end      = int(0.70 * n)
    f0[:rise_end] = np.linspace(0.0, 1.0, rise_end)
    f0[rise_end:] = np.linspace(1.0, 0.5, n - rise_end)
    # Terminal 0.5 — open question, not resolved

    # High sustained amplitude — maximum search energy
    peak_pt     = int(0.40 * n)
    sustain_end = int(0.65 * n)
    amp         = np.zeros(n)
    amp[:peak_pt]            = np.linspace(0.0, 1.0, peak_pt)
    amp[peak_pt:sustain_end] = 1.0
    amp[sustain_end:]        = np.linspace(
        1.0, 0.25, n - sustain_end)
    amp /= (amp.max() + 1e-10)

    # range_mult = WHERE_RANGE_MULT pushes above normal range
    return (f0, amp, 230, 400, 4,
            "WHERE_ARE_YOU", WHERE_RANGE_MULT)


def shape_acknowledge(n=N_SHAPE_PTS):
    """
    CALL 9 — ACKNOWLEDGE
    I received your transmission / continue the exchange.
    This is the dialogue maintenance signal.
    Without this, the exchange cannot develop past one round.

    Geometric structure:
    F0: minimal sweep — just a brief rise of ~25% of range.
      Not a full position announcement.
      Just enough movement to confirm the node is alive
      and has received the last signal.
      This is the acoustic equivalent of a nod.
    Amplitude: LOW — quiet.
      This is not a broadcast. It is a close-range
      acknowledgment. High amplitude would be a new
      position announcement, not an acknowledgment.
    Terminal: mid 0.5 — not reaching for anything.
      Confirming presence, not announcing movement.
    Duration: 90ms — very short. One brief signal.
    Gap: not applicable — single call, not sequence.
      Play once per received call from the flock.
      Do not loop. Loop = new announcement, not reply.
    1 repeat only.

    Buhrman-Deever & Hobson 2021 (cooperative parrot
    acknowledgment calls — short, low amplitude, close range).
    Baker 1974 (cockatiel chatter distinct from contact
    calls in close-range social context).
    Minimal sweep as acknowledgment encoding:
    OrganismCore advance.
    """
    # Minimal sweep — small rise only
    f0 = np.zeros(n)
    rise_end      = int(0.60 * n)
    f0[:rise_end] = np.linspace(0.2, 0.45, rise_end)
    f0[rise_end:] = np.linspace(0.45, 0.35, n - rise_end)
    # Small range, mid register — just a presence confirmation

    # Low amplitude — quiet acknowledgment
    amp          = np.zeros(n)
    peak_pt      = int(0.45 * n)
    amp[:peak_pt] = np.linspace(0.0, 0.55, peak_pt)
    amp[peak_pt:] = np.linspace(0.55, 0.0, n - peak_pt)
    amp /= (amp.max() + 1e-10)

    return f0, amp, 90, 500, 1, "ACKNOWLEDGE", 1.0


# ── SYNTHESIS ENGINE ──────────────────────────────────────────

def synthesize_call(f0_shape, amp_shape, stats,
                    register="MID", dur_ms=None,
                    range_mult=1.0,
                    sample_rate=SAMPLE_RATE):
    """
    Render a normalised (f0_shape, amp_shape) pair to audio.

    register:   LOW  = corpus p25 mean
                MID  = corpus p50 mean
                HIGH = corpus p75 mean

    range_mult: multiplier on f0_range_p50.
                1.0 for all calls except WHERE_ARE_YOU (1.35).
                Extends the eigenfunction range for
                long-distance separation calls.
    """
    f0_centre = {
        "LOW":  stats["f0_mean_p25"],
        "MID":  stats["f0_mean_p50"],
        "HIGH": stats["f0_mean_p75"],
    }[register]

    f0_range = stats["f0_range_p50"] * range_mult
    f0_abs   = (f0_shape * f0_range) + (f0_centre - f0_range / 2)
    f0_abs   = np.clip(f0_abs, 200, 10000)

    if dur_ms is None:
        dur_ms = stats["dur_p50"]

    n_samples = int(dur_ms * sample_rate / 1000)
    if n_samples < 2:
        n_samples = 2

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


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    print(f"    {os.path.basename(filename):<55} "
          f"({len(signal)/sample_rate:.2f}s)")


# ── REGISTER SHIFT FOR MOVING ─────────────────────────────────
# MOVING encodes directional movement by shifting register
# downward across the 3 repeats.
# LOW stays low (already at floor).
# MID and HIGH both shift HIGH→MID→LOW.

REGISTER_SHIFT = {
    "LOW":  ["LOW",  "LOW",  "LOW"],
    "MID":  ["HIGH", "MID",  "LOW"],
    "HIGH": ["HIGH", "MID",  "LOW"],
}

# WHERE_ARE_YOU uses HIGH register only — maximum range.
# The LOW and MID versions are still generated for
# completeness but HIGH is the operationally correct one.


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("OC-OBS-005 — FLOCK VOCABULARY V7")
    print("OrganismCore — Eric Robert Lawson")
    print("Nine call types × three registers = 27 files")
    print("Plus 9 probe files = 36 outputs total")
    print("=" * 65 + "\n")

    geometries = extract_all_geometries(CORPUS_DIR)

    if len(geometries) < 10:
        print(f"\nOnly {len(geometries)} geometries found.")
        print("Check FREQ_MIN_HZ / FREQ_MAX_HZ range.")
        return

    inv_f0, inv_amp, stats = find_structural_invariant(geometries)

    # ── Build complete call library ───────────────────────────
    call_library = [
        shape_i_am_here(inv_f0, inv_amp),
        shape_safe(),
        shape_alarm(),
        shape_resource(),
        shape_come_now(),
        shape_moving(),
        shape_all_clear(),
        shape_where_are_you(),
        shape_acknowledge(),
    ]

    registers = ["LOW", "MID", "HIGH"]

    print(f"\n{'='*65}")
    print("Synthesizing 9 call types × 3 registers...")
    print(f"{'='*65}\n")

    gap_2s = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s = np.zeros(int(1.0 * SAMPLE_RATE))

    for (f0_shape, amp_shape,
         dur_ms, gap_ms, n_repeats,
         label, range_mult) in call_library:

        print(f"  ── {label} ──")
        probe_parts = [gap_1s]
        is_moving   = (label == "MOVING")

        for reg in registers:

            if is_moving:
                reg_sequence   = REGISTER_SHIFT[reg]
                repeat_signals = []
                for rep_reg in reg_sequence:
                    sig, _ = synthesize_call(
                        f0_shape, amp_shape, stats,
                        register=rep_reg,
                        dur_ms=dur_ms,
                        range_mult=range_mult)
                    repeat_signals.append(sig)
                seq = build_sequence(repeat_signals, gap_ms)

                sig0, f0_abs0 = synthesize_call(
                    f0_shape, amp_shape, stats,
                    register=reg_sequence[0],
                    dur_ms=dur_ms,
                    range_mult=range_mult)
                print(f"    {reg} "
                      f"({reg_sequence[0]}→"
                      f"{reg_sequence[1]}→"
                      f"{reg_sequence[2]}):  "
                      f"F0 {f0_abs0[0]:.0f}Hz → "
                      f"{f0_abs0[-1]:.0f}Hz")

            else:
                sig, f0_abs = synthesize_call(
                    f0_shape, amp_shape, stats,
                    register=reg,
                    dur_ms=dur_ms,
                    range_mult=range_mult)

                repeat_signals = [sig] * n_repeats
                seq = build_sequence(repeat_signals, gap_ms)

                peak_idx = int(
                    np.argmax(amp_shape) / N_SHAPE_PTS
                    * len(f0_abs))
                peak_idx = min(peak_idx, len(f0_abs) - 1)

                range_hz = np.max(f0_abs) - np.min(f0_abs)
                mult_str = (f" [��{range_mult:.2f} range]"
                            if range_mult != 1.0 else "")
                print(f"    {reg}:  "
                      f"F0 {f0_abs[0]:.0f}Hz → "
                      f"{f0_abs[peak_idx]:.0f}Hz → "
                      f"{f0_abs[-1]:.0f}Hz  "
                      f"({range_hz:.0f}Hz){mult_str}")

            fname_single = os.path.join(
                OUTPUT_DIR, f"v7_{label}_{reg}.wav")
            save_wav(seq, fname_single)

            probe_parts.append(seq)
            probe_parts.append(gap_2s)

        probe_parts.append(gap_1s)
        probe = np.concatenate(probe_parts)
        fname_probe = os.path.join(
            OUTPUT_DIR, f"v7_{label}_PROBE.wav")
        save_wav(probe, fname_probe)
        print(f"    → Probe: v7_{label}_PROBE.wav\n")

    # ── Field kit summary ─────────────────────────────────────
    print(f"{'='*65}")
    print("V7 COMPLETE — 36 files generated")
    print(f"{'='*65}")
    print()
    print("COMPLETE FIELD KIT:")
    print()
    print("  ① LONG-DISTANCE ATTRACTION:")
    print("    v7_WHERE_ARE_YOU_HIGH.wav")
    print("    Use when flock is distant.")
    print("    Pushes 35% above normal eigenfunction range.")
    print("    Play × 4 then listen.")
    print()
    print("  ② INITIAL CONTACT (flock nearby):")
    print("    v7_I_AM_HERE_PROBE.wav")
    print("    Find which register the flock responds to.")
    print()
    print("  ③ SETTLE THE NETWORK:")
    print("    v7_SAFE_MID.wav")
    print("    After contact established.")
    print()
    print("  ④ MAINTAIN DIALOGUE:")
    print("    v7_ACKNOWLEDGE_MID.wav")
    print("    Play ONCE after each flock response.")
    print("    Do not loop — loop = new announcement.")
    print()
    print("  ⑤ DIRECT TO RESOURCE:")
    print("    v7_RESOURCE_MID.wav")
    print("    Terminal stays high — points outward.")
    print("    Distinct from I_AM_HERE terminal (0.719).")
    print()
    print("  ⑥ COORDINATE MOVEMENT:")
    print("    v7_COME_NOW_MID.wav  — recruit to position")
    print("    v7_MOVING_MID.wav    — follow me")
    print()
    print("  ⑦ ALARM SEQUENCE:")
    print("    v7_ALARM_HIGH.wav    — threat present")
    print("    v7_ALL_CLEAR_MID.wav — threat passed")
    print("    Always follow ALARM with ALL_CLEAR.")
    print("    Without ALL_CLEAR the network stays")
    print("    in alarm state — you cannot de-escalate.")
    print()
    print("  PROBE FILES:")
    for entry in call_library:
        lbl = entry[5]
        print(f"    v7_{lbl}_PROBE.wav")
    print()
    print("  OPERATIONAL NOTES:")
    print("    Conversational volume — not broadcast.")
    print("    The substrate is a network, not an audience.")
    print("    Wait for response between transmissions.")
    print("    Silence is part of the signal.")
    print("    ACKNOWLEDGE is a single call, not a sequence.")
    print("    WHERE_ARE_YOU: HIGH register only in field.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
