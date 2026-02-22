"""
GĀR-DENA RECONSTRUCTION
Old English: Gār-Dena
Meaning: of the Spear-Danes
IPA: [ɡɑːr ˈdenɑ]
Beowulf: Line 1, Word 3
February 2026

PHONEME STRUCTURE:
  GĀR  (primary stress — spear)
    G   [ɡ]   voiced velar stop
    Ā   [ɑː]  long open back vowel
    R   [r]   short trill (2 closures)

  DENA (secondary stress on DE, unstressed NA)
    D   [d]   voiced alveolar stop
    E   [e]   short close-mid front vowel
    N   [n]   voiced alveolar nasal
    A   [ɑ]   short open back vowel

NOTES:
  G before back vowel Ā = plain velar stop [ɡ].
  No palatalization. No ambiguity.

  Ā = long open back vowel.
  Pre-shift. Not [æ], not [eɪ].
  The vowel of German "Bahn", Italian "padre".
  F1 high (~750 Hz) — jaw open.
  F2 low (~1000 Hz) — back tongue.
  Contrast: [æ] had F1=668, F2=1873.
  [ɑː] inverts both — high F1, low F2.

  R = short trill. Two glottal closures.
  Not modern English approximant [ɹ].
  Germanic trill as in Icelandic, German.
  Each closure ~20ms. Inter-closure voiced
  period ~25ms. Total trill ~85ms at dil=1.0.
  F3 suppressed throughout (~1690 Hz) —
  the rhoticity is in the formant even during
  the open phases of the trill.

  D = voiced alveolar stop.
  Closure period + burst + short VOT.
  Onset of DENA — voiced from the start.
  No aspiration (voiced stop).

  E = short close-mid front [e].
  NOT the long [eː] of Wē.
  Shorter duration, same formant target.
  F1 ~420 Hz, F2 ~2200 Hz.

  N = voiced alveolar nasal.
  Antiformant at ~800 Hz (nasal tract).
  Murmur quality. F2 transitions mark
  the alveolar locus (~1800 Hz).

  A = short open back vowel [ɑ].
  Same formant target as Ā but short.
  Unstressed — reduced duration.
  The genitive ending.

COMPOUND BOUNDARY:
  GĀR-DENA has a compound seam at R-D.
  The R coda of GĀR releases into brief
  silence (the D closure) before the D burst.
  This is the first stop cluster in the
  reconstruction. The silence of the D
  closure IS part of the phoneme.

CHANGE LOG:
  v1 — initial parameters
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS — v1
# ============================================================

# G onset — voiced velar stop
# Closure: near-silence with low voicing bar
# Burst: broadband noise + velar formants
G_F          = [250.0,  2200.0, 3000.0, 3500.0]
G_B          = [200.0,   250.0,  300.0,  350.0]
G_CLOSURE_MS = 50.0    # closure period
G_BURST_MS   = 12.0    # burst duration
G_BURST_CF   = 1500.0  # velar burst center freq

# Ā vowel — long open back vowel [ɑː]
# F1 high (open jaw), F2 low (back tongue)
# Contrast with [æ]: F1=668, F2=1873
# Contrast with [eː]: F1=409, F2=2132
AA_F      = [750.0,  1000.0, 2500.0, 3300.0]
AA_B      = [120.0,   110.0,  170.0,  250.0]
AA_GAINS  = [ 20.0,     6.0,    1.5,    0.5]
AA_DUR_MS = 180.0   # long vowel

AA_COART_ON  = 0.10
AA_COART_OFF = 0.08

# R trill — short trill [r], 2 closures
# Each closure: voiced occlusion (~20ms)
# Inter-closure: voiced open phase (~25ms)
# F3 suppressed throughout (~1690 Hz)
# F2 held at ~1350 Hz during open phases
R_F          = [450.0,  1350.0, 1690.0, 3200.0]
R_B          = [100.0,   150.0,  200.0,  280.0]
R_GAINS      = [ 15.0,     4.0,    2.0,    0.5]
R_CLOSURE_MS = 20.0   # each closure
R_OPEN_MS    = 25.0   # each open phase
R_N_CLOSURES = 2      # short trill = 2

# D onset — voiced alveolar stop
D_F          = [250.0,  1800.0, 2600.0, 3400.0]
D_B          = [200.0,   220.0,  280.0,  320.0]
D_CLOSURE_MS = 45.0
D_BURST_MS   = 10.0
D_BURST_CF   = 3500.0  # alveolar burst high

# E vowel — short close-mid front [e]
# Same formant as Wē [eː] but shorter
E_F      = [430.0, 2200.0, 2900.0, 3400.0]
E_B      = [ 90.0,  120.0,  160.0,  200.0]
E_GAINS  = [ 18.0,    8.0,    1.5,    0.5]
E_DUR_MS = 80.0    # short — not long vowel

E_COART_ON  = 0.12
E_COART_OFF = 0.10

# N nasal — voiced alveolar nasal
# Murmur: low F1, antiformant ~800 Hz
# F2 transition marks alveolar locus
N_F      = [250.0,  1800.0, 2600.0, 3300.0]
N_B      = [100.0,   200.0,  300.0,  350.0]
N_GAINS  = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS = 70.0
N_ANTI_F = 800.0   # antiformant position

# A vowel — short open back [ɑ]
# Genitive ending. Unstressed. Reduced.
A_F      = [720.0,  1050.0, 2500.0, 3300.0]
A_B      = [130.0,   120.0,  200.0,  280.0]
A_GAINS  = [ 16.0,     5.0,    1.2,    0.4]
A_DUR_MS = 70.0    # short, unstressed

A_COART_ON  = 0.10
A_COART_OFF = 0.15  # word-final: longer release

# Performance parameters
PITCH_HZ   = 145.0
DIL        = 1.0


# ============================================================
# UTILITIES
# ============================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(
        np.mean(sig.astype(float)**2)))

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
    nyq  = sr / 2.0
    lo_  = max(lo / nyq, 0.001)
    hi_  = min(hi / nyq, 0.499)
    if lo_ >= hi_:
        lo_ = max(lo_ - 0.01, 0.001)
        hi_ = min(lo_ + 0.02, 0.499)
    b, a = butter(2, [lo_, hi_],
                  btype='band')
    return b, a

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = min(fc / nyq, 0.499)
    b, a = butter(2, fc_, btype='low')
    return b, a

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms   = 40.0
    win_n    = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in   = win_n // 4
    hop_out  = int(hop_in * factor)
    window   = np.hanning(win_n).astype(DTYPE)
    n_in     = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos+win_n] * window
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz         = norm > 1e-8
    out[nz]   /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# ROSENBERG PULSE SOURCE
# ============================================================

def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=SR):
    T     = 1.0 / sr
    phase = 0.0
    src   = np.zeros(n_samples, dtype=DTYPE)
    for i in range(n_samples):
        phase += pitch_hz * T
        if phase >= 1.0:
            phase -= 1.0
        if phase < oq:
            src[i] = ((phase / oq)
                      * (2 - phase / oq))
        else:
            src[i] = (1 - (phase - oq)
                      / (1 - oq + 1e-9))
    return f32(np.diff(src, prepend=src[0]))


# ============================================================
# FORMANT FILTER — static targets
# ============================================================

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    T      = 1.0 / sr
    n      = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(freqs)):
        fc  = float(freqs[fi])
        bw  = float(bws[fi])
        g   = float(gains[fi])
        a2  = -np.exp(-2 * np.pi * bw * T)
        a1  =  2 * np.exp(-np.pi * bw * T) \
               * np.cos(2 * np.pi * fc * T)
        b0  = 1.0 - a1 - a2
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            y       = (b0 * float(src[i])
                       + a1 * y1 + a2 * y2)
            y2      = y1
            y1      = y
            out[i]  = y
        result += out * g
    return f32(result)


# ============================================================
# FORMANT FILTER — time-varying trajectory
# ============================================================

def apply_formants_trajectory(src,
                               f_start,
                               f_end,
                               bws, gains,
                               sr=SR):
    """
    Apply formant resonators with linearly
    interpolated frequency trajectories.
    Used for coarticulation zones.
    """
    T   = 1.0 / sr
    n   = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(f_start)):
        f_arr = np.linspace(
            float(f_start[fi]),
            float(f_end[fi]),
            n, dtype=DTYPE)
        bw  = float(bws[fi])
        g   = float(gains[fi])
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            fc  = max(20.0,
                      min(sr * 0.48,
                          float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    return f32(result)


# ============================================================
# G — VOICED VELAR STOP
# ============================================================

def synth_G(F_next, pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced velar stop [ɡ] before back vowel.

    Structure:
      Closure: near-silence with voicing bar.
               The vocal folds continue
               vibrating during the closure.
               Low amplitude — the tract is
               occluded but voicing leaks.
      Burst:   Broadband noise at velar
               center frequency (~1500 Hz).
               Voiced burst — very brief.
      Transition: formants move from
               G_F toward F_next (the vowel).

    No aspiration. Voiced stop.
    """
    n_cl  = max(4, int(
        G_CLOSURE_MS * dil / 1000.0 * sr))
    n_bst = max(4, int(
        G_BURST_MS * dil / 1000.0 * sr))
    T     = 1.0 / sr

    # Closure: voiced bar — very low amplitude
    src_cl = rosenberg_pulse(
        n_cl, pitch_hz, oq=0.65, sr=sr)
    # Low-pass to get only fundamental energy
    b, a   = safe_lp(400.0, sr)
    bar    = lfilter(b, a,
                     src_cl.astype(float))
    bar    = f32(bar * 0.05)  # quiet

    # Burst: shaped noise at velar freq
    noise  = f32(np.random.randn(n_bst)
                 * 0.15)
    bw_bst = 600.0
    b2, a2 = safe_bp(
        G_BURST_CF - bw_bst/2,
        G_BURST_CF + bw_bst/2, sr)
    burst  = f32(lfilter(b2, a2,
                          noise.astype(float)))
    # Voiced component in burst
    src_bst = rosenberg_pulse(
        n_bst, pitch_hz, oq=0.65, sr=sr)
    voiced_bst = apply_formants(
        src_bst, G_F, G_B,
        [g * 0.3 for g in [1.0, 0.5, 0.3, 0.1]],
        sr=sr)
    burst = f32(burst + voiced_bst * 0.4)

    # Release transition: G_F → F_next
    n_rel  = max(4, int(0.030 * dil * sr))
    src_rel = rosenberg_pulse(
        n_rel, pitch_hz, oq=0.65, sr=sr)
    release = apply_formants_trajectory(
        src_rel,
        f_start=G_F,
        f_end=F_next,
        bws=G_B,
        gains=[1.0, 0.5, 0.3, 0.1],
        sr=sr)

    seg = np.concatenate([bar, burst, release])
    mx  = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.60)
    return f32(seg)


# ============================================================
# Ā — LONG OPEN BACK VOWEL
# ============================================================

def synth_AA_long(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Long open back vowel [ɑː].
    F1 high (~750 Hz) — jaw open.
    F2 low (~1000 Hz) — back tongue.
    The acoustic opposite of the front vowels.
    """
    dur_ms = AA_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    n_atk = min(int(0.020 * sr), n_s // 4)
    n_rel = min(int(0.040 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
    src = f32(src * env)

    n_on  = int(AA_COART_ON  * n_s)
    n_off = int(AA_COART_OFF * n_s)

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AA_F)):
        f_s   = float(F_prev[fi]) \
                if fi < len(F_prev) \
                else float(AA_F[fi])
        f_e   = float(F_next[fi]) \
                if fi < len(F_next) \
                else float(AA_F[fi])
        f_b   = float(AA_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)

        bw  = float(AA_B[fi])
        g   = float(AA_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0,
                      min(sr * 0.48,
                          float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.75)
    return f32(result)


# ============================================================
# R — SHORT TRILL [r]
# ============================================================

def synth_R_trill(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR,
                   n_closures=R_N_CLOSURES):
    """
    Short trill [r].

    Structure: alternating closure and open phases.
    N_closures = 2 for short trill.

    Each closure: near-silence with voicing bar.
      The tongue tip makes contact with the
      alveolar ridge. Tract is occluded.
      Voicing continues (voiced trill).
      Low-amplitude voiced bar only.

    Each open phase: voiced with R formants.
      F3 suppressed to ~1690 Hz — the
      rhoticity is carried acoustically
      even in the brief open phases.
      F2 at ~1350 Hz (retroflex/rhotic).

    Pattern (2 closures):
      [open] [close] [open] [close] [open]
      First and last open phases are the
      transitions from/to adjacent vowels.
    """
    n_cl = max(2, int(
        R_CLOSURE_MS * dil / 1000.0 * sr))
    n_op = max(2, int(
        R_OPEN_MS * dil / 1000.0 * sr))
    T    = 1.0 / sr

    def closure_seg():
        # Voiced bar during tongue contact
        src = rosenberg_pulse(
            n_cl, pitch_hz, oq=0.65, sr=sr)
        b, a = safe_lp(400.0, sr)
        bar  = f32(lfilter(b, a,
                            src.astype(float))
                   * 0.04)
        return bar

    def open_seg(f_s, f_e):
        # Voiced rhotic open phase
        # Interpolate from f_s to f_e
        src = rosenberg_pulse(
            n_op, pitch_hz, oq=0.65, sr=sr)
        result = np.zeros(n_op, dtype=DTYPE)
        for fi in range(len(R_F)):
            f_arr = np.linspace(
                float(f_s[fi]),
                float(f_e[fi]),
                n_op, dtype=DTYPE)
            bw  = float(R_B[fi])
            g   = float(R_GAINS[fi])
            y1 = y2 = 0.0
            out = np.zeros(n_op, dtype=DTYPE)
            for i in range(n_op):
                fc  = max(20.0,
                          min(sr * 0.48,
                              float(f_arr[i])))
                a2  = -np.exp(-2*np.pi*bw*T)
                a1  =  2*np.exp(-np.pi*bw*T) \
                       * np.cos(2*np.pi*fc*T)
                b0  = 1.0 - a1 - a2
                y   = (b0 * float(src[i])
                       + a1 * y1 + a2 * y2)
                y2  = y1
                y1  = y
                out[i] = y
            result += out * g
        return f32(result)

    # Build trill:
    # onset open: F_prev → R_F
    # then n_closures cycles of: closure + open
    # final open phase held at R_F
    # total open phases: n_closures + 1
    segments = []

    # First open: from previous vowel to R
    segments.append(open_seg(F_prev, R_F))

    for i in range(n_closures):
        segments.append(closure_seg())
        # Open phase: R_F → R_F
        # (last open transitions toward F_next)
        if i < n_closures - 1:
            segments.append(
                open_seg(R_F, R_F))
        else:
            # Final open: R_F → F_next
            segments.append(
                open_seg(R_F, F_next))

    trill = np.concatenate(segments)
    mx    = np.max(np.abs(trill))
    if mx > 1e-8:
        trill = f32(trill / mx * 0.65)
    return f32(trill)


# ============================================================
# D — VOICED ALVEOLAR STOP
# ============================================================

def synth_D(F_prev, F_next,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced alveolar stop [d].

    Structure:
      Closure: near-silence + voicing bar.
               Tongue tip at alveolar ridge.
               Vocal folds continue voicing.
      Burst:   Short broadband noise at
               high frequency (alveolar ~3500 Hz).
               Very brief.
      Release: Formants move from D_F to F_next.

    Voiced — no aspiration.
    Alveolar burst is higher than velar G.
    """
    n_cl  = max(4, int(
        D_CLOSURE_MS * dil / 1000.0 * sr))
    n_bst = max(4, int(
        D_BURST_MS * dil / 1000.0 * sr))
    T     = 1.0 / sr

    # Closure: voiced bar
    src_cl = rosenberg_pulse(
        n_cl, pitch_hz, oq=0.65, sr=sr)
    b, a   = safe_lp(400.0, sr)
    bar    = f32(lfilter(b, a,
                          src_cl.astype(float))
                 * 0.04)

    # Burst: alveolar = high frequency
    noise  = f32(np.random.randn(n_bst)
                 * 0.12)
    bw_bst = 800.0
    b2, a2 = safe_bp(
        D_BURST_CF - bw_bst/2,
        D_BURST_CF + bw_bst/2, sr)
    burst  = f32(lfilter(b2, a2,
                          noise.astype(float)))

    # Release: D_F → F_next
    n_rel   = max(4, int(0.025 * dil * sr))
    src_rel = rosenberg_pulse(
        n_rel, pitch_hz, oq=0.65, sr=sr)
    release = apply_formants_trajectory(
        src_rel,
        f_start=D_F,
        f_end=F_next,
        bws=D_B,
        gains=[1.0, 0.6, 0.3, 0.1],
        sr=sr)

    seg = np.concatenate([bar, burst, release])
    mx  = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
    return f32(seg)


# ============================================================
# E — SHORT CLOSE-MID FRONT VOWEL
# ============================================================

def synth_E_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Short close-mid front vowel [e].
    Same formant target as Wē [eː]
    but shorter duration.
    F1 ~430 Hz, F2 ~2200 Hz.
    """
    dur_ms = E_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    n_atk = min(int(0.015 * sr), n_s // 4)
    n_rel = min(int(0.025 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.5, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src = f32(src * env)

    n_on  = int(E_COART_ON  * n_s)
    n_off = int(E_COART_OFF * n_s)

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(E_F)):
        f_s   = float(F_prev[fi]) \
                if fi < len(F_prev) \
                else float(E_F[fi])
        f_e   = float(F_next[fi]) \
                if fi < len(F_next) \
                else float(E_F[fi])
        f_b   = float(E_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)

        bw  = float(E_B[fi])
        g   = float(E_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0,
                      min(sr * 0.48,
                          float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.70)
    return f32(result)


# ============================================================
# N — VOICED ALVEOLAR NASAL
# ============================================================

def synth_N(F_prev, F_next,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced alveolar nasal [n].

    Physics:
      Velum lowered — nasal cavity opens.
      Tongue tip at alveolar ridge — oral
      cavity is occluded.
      Air flows through nasal passage.
      Antiformant at ~800 Hz where the
      oral cavity resonance is cancelled
      by the nasal cavity coupling.
      F2 transitions mark alveolar locus.

    The antiformant is implemented as a
    notch filter at N_ANTI_F.
    """
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    env = np.ones(n_s, dtype=DTYPE)
    n_tr = min(int(0.020 * sr), n_s // 4)
    if n_tr < n_s:
        env[:n_tr] = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src = f32(src * env)

    # Nasal murmur formants
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)

    # Antiformant notch at ~800 Hz
    # Implemented as: subtract a
    # narrow resonator at the anti-freq
    bw_notch = 100.0
    anti_src = apply_formants(
        src,
        [N_ANTI_F],
        [bw_notch],
        [N_GAINS[0] * 0.6],
        sr=sr)
    result = f32(result - anti_src)

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


# ============================================================
# A — SHORT OPEN BACK VOWEL
# ============================================================

def synth_A_short(F_prev, pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Short open back vowel [ɑ].
    Genitive ending of Dena.
    Unstressed — reduced duration.
    Word-final — gentle release tail.
    """
    dur_ms = A_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    n_atk = min(int(0.012 * sr), n_s // 4)
    n_rel = min(int(0.060 * sr), n_s // 3)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src = f32(src * env)

    n_on  = int(A_COART_ON  * n_s)

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(A_F)):
        f_s   = float(F_prev[fi]) \
                if fi < len(F_prev) \
                else float(A_F[fi])
        f_b   = float(A_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)

        bw  = float(A_B[fi])
        g   = float(A_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0,
                      min(sr * 0.48,
                          float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.60)
    return f32(result)


# ============================================================
# APPLY ROOM
# ============================================================

def apply_simple_room(sig, rt60=2.0,
                       direct_ratio=0.42,
                       sr=SR):
    d1  = int(0.021 * sr)
    d2  = int(0.035 * sr)
    d3  = int(0.051 * sr)
    g   = 10 ** (-3.0 / (rt60 * sr))
    rev = np.zeros(len(sig) + d3 + 1,
                   dtype=float)
    for i, s in enumerate(sig.astype(float)):
        rev[i] += s
        if i + d1 < len(rev):
            rev[i+d1] += s * g * 0.6
        if i + d2 < len(rev):
            rev[i+d2] += s * g * 0.4
        if i + d3 < len(rev):
            rev[i+d3] += s * g * 0.25
    rev = rev[:len(sig)]
    mix = (direct_ratio * sig.astype(float)
           + (1 - direct_ratio) * rev)
    mx  = np.max(np.abs(mix))
    if mx > 1e-8:
        mix = mix / mx * 0.75
    return f32(mix)


# ============================================================
# FULL WORD
# ============================================================

def synth_gar_dena(pitch_hz=PITCH_HZ,
                    dil=DIL,
                    add_room=False,
                    sr=SR):
    """
    Synthesize Old English 'Gār-Dena' [ɡɑːrdenɑ].

    Segment sequence:
      G closure+burst+release
      Ā long vowel
      R short trill (2 closures)
      D closure+burst+release
      E short vowel
      N nasal
      A short vowel (word-final)
    """
    # Synthesize in order passing
    # formant context forward
    g_seg   = synth_G(
        F_next=AA_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    aa_seg  = synth_AA_long(
        F_prev=G_F,
        F_next=R_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    r_seg   = synth_R_trill(
        F_prev=AA_F,
        F_next=D_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    d_seg   = synth_D(
        F_prev=R_F,
        F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    e_seg   = synth_E_short(
        F_prev=D_F,
        F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    n_seg   = synth_N(
        F_prev=E_F,
        F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    a_seg   = synth_A_short(
        F_prev=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    word = np.concatenate([
        g_seg, aa_seg, r_seg,
        d_seg, e_seg, n_seg, a_seg])

    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = f32(word / mx * 0.75)

    if add_room:
        word = apply_simple_room(
            word, rt60=2.0,
            direct_ratio=0.38, sr=sr)

    return f32(word)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("GĀR-DENA RECONSTRUCTION v1")
    print("Old English [ɡɑːrdenɑ]")
    print("Beowulf line 1, word 3")
    print()

    gd_dry = synth_gar_dena(
        pitch_hz=145.0,
        dil=1.0,
        add_room=False)
    write_wav(
        "output_play/gar_dena_dry.wav",
        gd_dry, SR)
    print(f"  gar_dena_dry.wav  "
          f"{len(gd_dry)} samples  "
          f"({len(gd_dry)/SR*1000:.0f} ms)")

    gd_hall = synth_gar_dena(
        pitch_hz=145.0,
        dil=1.0,
        add_room=True)
    write_wav(
        "output_play/gar_dena_hall.wav",
        gd_hall, SR)
    print(f"  gar_dena_hall.wav")

    gd_slow = ola_stretch(gd_dry, 4.0)
    write_wav(
        "output_play/gar_dena_slow.wav",
        gd_slow, SR)
    print(f"  gar_dena_slow.wav")

    gd_perf = synth_gar_dena(
        pitch_hz=110.0,
        dil=2.5,
        add_room=True)
    write_wav(
        "output_play/gar_dena_performance.wav",
        gd_perf, SR)
    print(f"  gar_dena_performance.wav  "
          f"({len(gd_perf)/SR*1000:.0f} ms)")

    # R trill isolated for inspection
    r_iso = synth_R_trill(
        F_prev=AA_F,
        F_next=D_F,
        pitch_hz=145.0,
        dil=1.0, sr=SR)
    write_wav(
        "output_play/gar_dena_r_isolated.wav",
        ola_stretch(r_iso, 4.0), SR)
    print(f"  gar_dena_r_isolated.wav  "
          f"(trill 4x slow)")

    # Ā vowel isolated
    aa_iso = synth_AA_long(
        F_prev=G_F,
        F_next=R_F,
        pitch_hz=145.0,
        dil=1.0, sr=SR)
    write_wav(
        "output_play/gar_dena_aa_isolated.wav",
        ola_stretch(aa_iso, 4.0), SR)
    print(f"  gar_dena_aa_isolated.wav  "
          f"(Ā vowel 4x slow)")

    print()
    print("  afplay output_play/"
          "gar_dena_dry.wav")
    print("  afplay output_play/"
          "gar_dena_slow.wav")
    print("  afplay output_play/"
          "gar_dena_r_isolated.wav")
    print("  afplay output_play/"
          "gar_dena_aa_isolated.wav")
    print("  afplay output_play/"
          "gar_dena_performance.wav")
    print("  afplay output_play/"
          "gar_dena_hall.wav")
    print()
