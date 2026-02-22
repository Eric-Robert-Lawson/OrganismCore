"""
FUNDEN RECONSTRUCTION
Old English: funden
Meaning: found (past participle of findan)
IPA: [fundən]
Beowulf: Line 8, word 2 (overall word 32)
February 2026

PHONEME STRUCTURE:
  F   [f]   voiceless labiodental fricative — verified
  U   [u]   short close back rounded        — verified
  N   [n]   voiced alveolar nasal           — verified
  D   [d]   voiced alveolar stop            — verified
  Ə   [ə]   mid central vowel               — NEW #40
  N   [n]   voiced alveolar nasal           — second instance

NEW PHONEME: [ə] — schwa — phoneme 40.
  The dominant of vocal space.
  C([ə],H) ≈ 0.75.
  The perfect fifth. One step from home.
  VRFY_002 from Tonnetz bridge document.

THEORETICAL BASIS:
  Unstressed syllables → reduced articulatory
  effort → movement toward H → schwa.
  This is physics, not convention.

  The Tonnetz bridge document predicted this:
  C([ə],H) ≈ 0.75 — named, positioned,
  coherence value computed — before this
  word was reached. VRFY_002 has been
  waiting. FUNDEN runs it.

EVIDENCE STREAMS — all six converge:
  1. Orthographic: OE -en suffix consistent
     across West Saxon. Metrically light.
  2. Comparative: ModG 'gefunden' [gəˈfʊndən]
     — final syllable [ən]. Direct cognate.
     Schwa + nasal. The reduction is preserved.
  3. Acoustic: All Germanic -en unstressed
     endings → [ən] in living languages.
  4. Documentary: OE metre treats all
     unstressed syllables as equivalent
     weight — consistent with merger
     toward central reduced vowel.
  5. Articulatory: Reduced effort in all
     five vocal topology dimensions =
     movement toward H = schwa position.
  6. Perceptual: Hyper-articulated unstressed
     [e] in oral epic performance would
     disrupt rhythmic flow and alliterative
     pattern. The hall required reduction.

SCHWA PARAMETERS — derived from first principles:
  F1: ~500 Hz — slight jaw opening from H
  F2: ~1500 Hz — tongue at rest, central
  F3: ~2500 Hz — neutral lip rounding
  BW: wider than peripheral vowels
  Duration: 45 ms — short, unstressed
  The minimum-effort vowel.
  The dominant of the vocal topology.

CONTEXT:
  feasceaft funden —
  found wretched / found destitute.
  FUNDEN is the verb — the discovery.
  The past participle that closes
  the description of Scyld's origin.

SYLLABLE STRUCTURE:
  Syllable 1: [fun]  — stressed
  Syllable 2: [dən]  — unstressed

CHANGE LOG:
  v1 — initial parameters
       [ə] introduced — phoneme 40
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS — all from verified inventory
# except [ə] which is new
# ============================================================

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28

# U — short close back rounded [u]
U_F     = [300.0,  800.0, 2300.0, 3000.0]
U_B     = [100.0,  150.0,  250.0,  300.0]
U_GAINS = [ 14.0,    6.0,    1.2,    0.4]
U_DUR_MS    = 60.0
U_COART_ON  = 0.12
U_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F     = [250.0,  1700.0, 2600.0, 3200.0]
N_B     = [300.0,   150.0,  250.0,  300.0]
N_GAINS = [  8.0,     4.0,    1.0,    0.4]
N_DUR_MS    = 60.0
N_COART_ON  = 0.15
N_COART_OFF = 0.15

# D — voiced alveolar stop [d]
D_DUR_MS      = 60.0
D_CLOSURE_MS  = 35.0
D_BURST_F     = 3500.0
D_BURST_BW    = 1500.0
D_BURST_MS    = 8.0
D_VOT_MS      = 5.0
D_BURST_GAIN  = 0.35
D_VOT_GAIN    = 0.10
D_VOICING_MS  = 20.0

# Ə — mid central vowel [ə] — NEW PHONEME 40
# Derived from first principles:
# One step from H. Minimum effort position.
# F1 ~500 Hz: slight jaw opening
# F2 ~1500 Hz: tongue at rest, central
# F3 ~2500 Hz: neutral lips
# Short duration: unstressed syllable
# Wide bandwidth: reduced articulatory
# precision in unstressed position
SCHWA_F     = [500.0, 1500.0, 2500.0, 3200.0]
SCHWA_B     = [150.0,  200.0,  280.0,  320.0]
SCHWA_GAINS = [ 14.0,    7.0,    1.5,    0.4]
SCHWA_DUR_MS    = 45.0
SCHWA_COART_ON  = 0.15
SCHWA_COART_OFF = 0.15

PITCH_HZ   = 145.0
PITCH_PERF = 110.0
DIL        = 1.0
DIL_PERF   = 2.5


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
    b, a = butter(2, [lo_, hi_], btype='band')
    return b, a

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
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# ROSENBERG PULSE
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
# FORMANT FILTERS
# ============================================================

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    T      = 1.0 / sr
    n      = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(freqs)):
        fc = float(freqs[fi])
        bw = float(bws[fi])
        g  = float(gains[fi])
        a2 = -np.exp(-2 * np.pi * bw * T)
        a1 =  2 * np.exp(-np.pi * bw * T) \
               * np.cos(2 * np.pi * fc * T)
        b0 = 1.0 - a1 - a2
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            y      = (b0 * float(src[i])
                      + a1 * y1 + a2 * y2)
            y2     = y1
            y1     = y
            out[i] = y
        result += out * g
    return f32(result)


# ============================================================
# PHONEME SYNTHESIZERS
# ============================================================

def synth_F(dil=DIL, sr=SR):
    """Voiceless labiodental fricative [f]."""
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(F_NOISE_CF - F_NOISE_BW/2,
                 200.0)
    hi_    = min(F_NOISE_CF + F_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(1.0, 0.3, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_vowel_coart(F_tgts, F_bws, F_gains,
                       dur_ms, coart_on,
                       coart_off, F_prev,
                       F_next, pitch_hz,
                       dil, sr, norm_gain):
    """Generic coarticulated vowel synthesiser.
    Used for [u] and [ə]."""
    d_ms = dur_ms * dil
    n_s  = max(4, int(d_ms / 1000.0 * sr))
    T    = 1.0 / sr
    src  = rosenberg_pulse(n_s, pitch_hz,
                            oq=0.65, sr=sr)
    n_atk = min(int(0.010 * sr), n_s // 4)
    n_rel = min(int(0.015 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src   = f32(src * env)
    n_on  = int(coart_on  * n_s)
    n_off = int(coart_off * n_s)
    fp    = F_prev if F_prev is not None \
            else F_tgts
    fn    = F_next if F_next is not None \
            else F_tgts
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(F_tgts)):
        f_s   = (float(fp[fi])
                 if fi < len(fp)
                 else float(F_tgts[fi]))
        f_e   = (float(fn[fi])
                 if fi < len(fn)
                 else float(F_tgts[fi]))
        f_b   = float(F_tgts[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(F_bws[fi])
        g   = float(F_gains[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2_ = -np.exp(-2*np.pi*bw*T)
            a1_ =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0_ = 1.0 - a1_ - a2_
            yy  = (b0_ * float(src[i])
                   + a1_ * y1 + a2_ * y2)
            y2  = y1
            y1  = yy
            out[i] = yy
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * norm_gain)
    return f32(result)


def synth_U(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Short close back rounded [u]."""
    return synth_vowel_coart(
        U_F, U_B, U_GAINS,
        U_DUR_MS, U_COART_ON, U_COART_OFF,
        F_prev, F_next,
        pitch_hz, dil, sr, 0.65)


def synth_SCHWA(F_prev=None, F_next=None,
                 pitch_hz=PITCH_HZ,
                 dil=DIL, sr=SR):
    """
    Mid central vowel [ə] — PHONEME 40.
    The dominant of vocal space.
    C([ə],H) ≈ 0.75.
    One step from H.

    Parameters derived from first principles:
    F1 500 Hz — slight jaw opening
    F2 1500 Hz — tongue at rest, central
    F3 2500 Hz — neutral lips
    Duration 45 ms — unstressed syllable
    Wide BW — reduced articulatory precision

    VRFY_002 from Tonnetz bridge document:
    'Measure schwa [ə] distance from H.
    Nearest unstressed vowel to H.
    The perfect fifth of vocal space.
    One step from home.'
    """
    return synth_vowel_coart(
        SCHWA_F, SCHWA_B, SCHWA_GAINS,
        SCHWA_DUR_MS,
        SCHWA_COART_ON, SCHWA_COART_OFF,
        F_prev, F_next,
        pitch_hz, dil, sr, 0.58)


def synth_N(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiced alveolar nasal [n]."""
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
    src    = f32(src * env)
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.58)
    return f32(result)


def synth_D(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiced alveolar stop [d]."""
    dur_ms     = D_DUR_MS * dil
    n_s        = max(4, int(
        dur_ms / 1000.0 * sr))
    n_closure  = max(2, int(
        D_CLOSURE_MS / 1000.0 * sr))
    n_burst    = max(2, int(
        D_BURST_MS / 1000.0 * sr))
    n_vot      = max(2, int(
        D_VOT_MS / 1000.0 * sr))
    n_voicing  = max(2, int(
        D_VOICING_MS / 1000.0 * sr))
    src_v      = rosenberg_pulse(
        n_voicing, pitch_hz,
        oq=0.65, sr=sr)
    env_v      = np.linspace(
        0.15, 0.0,
        n_voicing).astype(DTYPE)
    voiced_cl  = apply_formants(
        f32(src_v * env_v),
        [250.0], [300.0], [4.0], sr=sr)
    silence    = np.zeros(
        max(0, n_closure - n_voicing),
        dtype=DTYPE)
    closure    = np.concatenate([
        voiced_cl, silence])[:n_closure]
    noise_b    = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst      = f32(lfilter(
        b_bp, a_bp, noise_b)
                     * D_BURST_GAIN)
    env_bu     = np.linspace(
        1.0, 0.1, n_burst).astype(DTYPE)
    burst      = f32(burst * env_bu)
    noise_v2   = np.random.randn(
        n_vot).astype(float)
    b_vp, a_vp = safe_bp(500.0, 6000.0, sr)
    vot        = f32(lfilter(
        b_vp, a_vp, noise_v2)
                     * D_VOT_GAIN)
    env_vo     = np.linspace(
        0.3, 0.0, n_vot).astype(DTYPE)
    vot        = f32(vot * env_vo)
    seg        = np.concatenate([
        closure, burst, vot])
    n_pad      = max(0, n_s - len(seg))
    seg        = np.concatenate([
        seg, np.zeros(n_pad, dtype=DTYPE)])
    seg        = f32(seg[:n_s])
    mx         = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.50)
    return f32(seg)


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

def synth_funden(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """
    [f · u · n · d · ə · n]
    Syllable 1: [fun]  — stressed
    Syllable 2: [dən]  — unstressed
    [ə] is phoneme 40.
    Short duration — 45 ms.
    Central formants — F1 500, F2 1500.
    """
    f_seg  = synth_F(dil=dil, sr=sr)
    u_seg  = synth_U(
        F_prev=None, F_next=N_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    n1_seg = synth_N(
        F_prev=U_F, F_next=None,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=None, F_next=SCHWA_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    schwa_seg = synth_SCHWA(
        F_prev=None, F_next=N_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    n2_seg = synth_N(
        F_prev=SCHWA_F, F_next=None,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    word   = np.concatenate([
        f_seg, u_seg, n1_seg,
        d_seg, schwa_seg, n2_seg])
    mx     = np.max(np.abs(word))
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
    print("FUNDEN RECONSTRUCTION v1")
    print("Old English [fundən]")
    print("Beowulf line 8, word 2")
    print("NEW PHONEME: [ə] schwa — #40")
    print("  F1 500 Hz / F2 1500 Hz / 45 ms")
    print("  The dominant of vocal space.")
    print("  VRFY_002.")
    print()

    w_dry = synth_funden(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/funden_dry.wav",
        w_dry, SR)
    print(f"  funden_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_funden(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/funden_hall.wav",
        w_hall, SR)
    print("  funden_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/funden_slow.wav",
        w_slow, SR)
    print("  funden_slow.wav")

    w_perf = synth_funden(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav(
        "output_play/funden_perf.wav",
        w_perf, SR)
    print(f"  funden_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/funden_dry.wav")
    print("  afplay output_play/funden_slow.wav")
    print("  afplay output_play/funden_hall.wav")
    print("  afplay output_play/funden_perf.wav")
    print()
    print("  feasceaft funden —")
    print("  found wretched.")
    print()
