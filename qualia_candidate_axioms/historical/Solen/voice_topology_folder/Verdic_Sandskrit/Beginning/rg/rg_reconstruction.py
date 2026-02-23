"""
ṚG RECONSTRUCTION v1
Vedic Sanskrit: ṛg  [ɻ̩g]
Rigveda — first syllable, proof of concept
February 2026

PHONEMES:
  [ɻ̩]  syllabic retroflex approximant — NEW
  [g]   voiced velar stop — from OE inventory

NEW ARCHITECTURE:
  Retroflex F3 dip model.
  [ɻ̩] synthesised as a vowel, not a consonant.
  Sustained voicing, no AM modulation.
  F3 depressed to ~2200 Hz — the mūrdhanya marker.

PERFORMANCE PARAMETERS:
  pitch_hz:     120.0  (Vedic recitation register)
  dil:          1.0    (diagnostic — non-dilated)
  rt60:         1.5    (temple courtyard estimate)
  direct_ratio: 0.55

COARTICULATION:
  [ɻ̩] → [g]: retroflex F2 (~1300 Hz) rises
             to velar locus (~2500 Hz) at closure.
             The coarticulation window is the
             map of this new territory.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ── PHONEME PARAMETERS ────────────────────────────────

# [ɻ̩] — syllabic retroflex approximant — ऋ
# Śikṣā: mūrdhanya
# F3 ~2200 Hz — the retroflex dip marker
RV_F      = [420.0, 1300.0, 2200.0, 3100.0]
RV_B      = [150.0,  200.0,  280.0,  300.0]
RV_GAINS  = [ 14.0,    7.0,    1.5,    0.4]
RV_DUR_MS = 60.0
RV_COART_ON  = 0.15
RV_COART_OFF = 0.15

# [g] — voiced velar stop — ग
# Direct transfer from OE inventory.
# Velar locus ~2500 Hz.
# LF energy ratio diagnostic (not voicing fraction).
G_F      = [300.0, 1900.0, 2500.0, 3200.0]
G_B      = [120.0,  200.0,  280.0,  350.0]
G_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
G_CLOSURE_MS  = 30.0
G_BURST_F     = 2500.0
G_BURST_BW    = 1200.0
G_BURST_MS    = 8.0
G_VOT_MS      = 10.0
G_MURMUR_GAIN = 0.70
G_BURST_GAIN  = 0.30

PITCH_HZ = 120.0
DIL      = 1.0


# ── UTILITIES ─────────────────────────────────────────

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(
        np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig),
                     -1.0, 1.0) * 32767
             ).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo  = max(lo, 20.0)
    hi  = min(hi, nyq - 20.0)
    if lo >= hi:
        return None, None
    return butter(2, [lo / nyq, hi / nyq],
                  btype='band')

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc  = min(fc, nyq - 20.0)
    return butter(2, fc / nyq, btype='low')

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms  = 40.0
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    window  = np.hanning(win_n).astype(DTYPE)
    n_in    = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = (sig[in_pos:in_pos + win_n]
                 * window)
        out [out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=SR):
    """
    Glottal pulse model.
    oq: open quotient — 0.65 male voice.
    Differentiated for formant filtering.
    """
    period = int(sr / pitch_hz)
    pulse  = np.zeros(period, dtype=float)
    t1     = int(period * oq * 0.6)
    t2     = int(period * oq)
    for i in range(t1):
        pulse[i] = (0.5 * (1.0
                    - np.cos(np.pi * i / t1)))
    for i in range(t1, t2):
        pulse[i] = np.cos(
            np.pi * (i - t1) /
            (2.0 * (t2 - t1)))
    d_pulse  = np.diff(pulse,
                       prepend=pulse[0])
    n_reps   = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])


def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    """
    IIR resonator bank — four formants.
    """
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f0, bw, g in zip(freqs, bws, gains):
        if f0 <= 0 or f0 >= nyq:
            continue
        r    = np.exp(-np.pi * bw / sr)
        cosf = 2.0 * np.cos(
            2.0 * np.pi * f0 / sr)
        a    = [1.0, -r * cosf, r * r]
        b_   = [1.0 - r]
        res  = lfilter(b_, a,
                       src.astype(float))
        out += res * g
    return f32(out)


# ── PHONEME SYNTHESISERS ──────────────────────────────

def synth_RV(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [ɻ̩] — syllabic retroflex approximant.

    Synthesised as a sustained vowel with
    retroflex formant targets.
    Key: F3 at ~2200 Hz — the mūrdhanya marker.
    No AM modulation (not a trill).
    Sustained voicing throughout.

    Coarticulation:
      F_prev: formants of preceding phoneme
              (None at word onset)
      F_next: formants of following phoneme
              (G_F for the velar stop)
    """
    n_ms  = RV_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            sr=sr)

    # Coarticulation windows
    on_n  = int(RV_COART_ON * n)
    off_n = int(RV_COART_OFF * n)

    # Build formant trajectory
    freqs = np.zeros((n, 4), dtype=float)
    for k in range(4):
        target = RV_F[k]
        # Onset: interpolate from F_prev
        if F_prev is not None and on_n > 0:
            start = F_prev[k] if k < len(F_prev) \
                    else target
            t = np.linspace(0.0, 1.0, on_n)
            freqs[:on_n, k] = (
                start + (target - start) * t)
        else:
            freqs[:on_n, k] = target
        # Body
        freqs[on_n:n - off_n, k] = target
        # Offset: interpolate toward F_next
        if F_next is not None and off_n > 0:
            end = F_next[k] if k < len(F_next) \
                  else target
            t = np.linspace(0.0, 1.0, off_n)
            freqs[n - off_n:, k] = (
                target + (end - target) * t)
        else:
            freqs[n - off_n:, k] = target

    # Apply formants sample-by-sample
    # Use mean formants (good approximation
    # for the short coarticulation windows)
    f_mean = np.mean(freqs, axis=0)
    out    = apply_formants(src,
                            f_mean.tolist(),
                            RV_B, RV_GAINS,
                            sr=sr)

    # Normalise
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)


def synth_G(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [g] — voiced velar stop.

    Three phases:
      Phase 1: closure — voiced murmur
               Rosenberg pulse LP filtered
      Phase 2: burst — band noise at velar F
      Phase 3: VOT — short voiced release

    F_prev used for closure formant targets.
    F_next used for VOT formant targets.
    """
    n_closure = int(
        G_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        G_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        G_VOT_MS     * dil / 1000.0 * sr)

    # Phase 1: voiced closure
    src_cl  = rosenberg_pulse(
        n_closure, pitch_hz, sr=sr)
    b_lp, a_lp = safe_lp(800.0, sr)
    if b_lp is not None:
        murmur = lfilter(b_lp, a_lp,
                         src_cl.astype(float))
    else:
        murmur = src_cl.astype(float)
    murmur = f32(murmur * G_MURMUR_GAIN)

    # Phase 2: burst
    noise   = np.random.randn(n_burst)
    b_bp, a_bp = safe_bp(
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    burst = f32(burst * G_BURST_GAIN)

    # Phase 3: short voiced VOT
    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, pitch_hz, sr=sr)
        f_vot   = F_next if F_next is not None \
                  else G_F
        vot     = apply_formants(
            src_vot, f_vot, G_B, G_GAINS, sr=sr)
        vot     = f32(vot * 0.10)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([murmur, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)


# ── ROOM MODEL ────────────────────────────────────────

def apply_simple_room(sig, rt60=1.5,
                      direct_ratio=0.55,
                      sr=SR):
    """
    Simple Schroeder reverb approximation.
    rt60 = 1.5 s — temple courtyard estimate.
    Vedic recitation: outdoor ritual or
    open stone space. Less reverberant
    than the Beowulf mead hall (rt60=2.0).
    """
    n_rev = int(rt60 * sr)
    ir    = np.zeros(n_rev, dtype=float)
    ir[0] = 1.0
    decay = np.exp(
        -6.908 * np.arange(n_rev) /
        (rt60 * sr))
    noise_ir = (np.random.randn(n_rev)
                * decay)
    ir       = (direct_ratio * ir
                + (1.0 - direct_ratio)
                * noise_ir)
    ir       = ir / (np.max(np.abs(ir))
                     + 1e-12)
    out = np.convolve(sig.astype(float),
                      ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ── WORD SYNTHESISER ──────────────────────────────────

def synth_rg(pitch_hz=PITCH_HZ,
             dil=DIL,
             with_room=False,
             sr=SR):
    """
    ṚG [ɻ̩g] — proof of concept.

    Segment sequence:
      [ɻ̩]  syllabic retroflex vowel
      [g]  voiced velar stop

    Coarticulation:
      RV onset: word-initial, F_prev=None
      RV offset: coarticulates toward G_F
      G closure: coarticulates from RV_F
    """
    rv  = synth_RV(F_prev=None,
                   F_next=G_F,
                   pitch_hz=pitch_hz,
                   dil=dil, sr=sr)
    g   = synth_G(F_prev=RV_F,
                  F_next=None,
                  pitch_hz=pitch_hz,
                  dil=dil, sr=sr)

    word = np.concatenate([rv, g])

    # Normalise
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(
            word, rt60=1.5,
            direct_ratio=0.55, sr=sr)

    return f32(word)


# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Synthesising ṚG [ɻ̩g]...")

    dry  = synth_rg(with_room=False)
    hall = synth_rg(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/rg_dry.wav",  dry)
    write_wav("output_play/rg_hall.wav", hall)
    write_wav("output_play/rg_slow.wav", slow)

    # Isolated retroflex vowel for diagnosis
    rv_iso = synth_RV(F_prev=None,
                      F_next=None)
    mx = np.max(np.abs(rv_iso))
    if mx > 1e-8:
        rv_iso = rv_iso / mx * 0.75
    write_wav("output_play/rg_rv_isolated.wav",
              rv_iso)
    write_wav("output_play/rg_rv_slow.wav",
              ola_stretch(rv_iso, 4.0))

    print("Written:")
    print("  output_play/rg_dry.wav")
    print("  output_play/rg_hall.wav")
    print("  output_play/rg_slow.wav")
    print("  output_play/rg_rv_isolated.wav")
    print("  output_play/rg_rv_slow.wav")
    print()
    print("Run ṛg_diagnostic.py to verify.")
