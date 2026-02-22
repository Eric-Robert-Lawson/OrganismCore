"""
SCYLD RECONSTRUCTION
Old English: Scyld
Meaning: Shield (proper name —
         founding king of the Danes)
IPA: [ʃyld]
Beowulf: Line 5, Word 1 (overall word 18)
February 2026

PHONEME STRUCTURE:
  SC  [ʃ]   voiceless postalveolar fric. — NEW
  Y   [y]   short close front rounded    — verified
  L   [l]   voiced alveolar lateral      — verified
  D   [d]   voiced alveolar stop         — verified

NEW PHONEMES:
  [ʃ]: voiceless postalveolar fricative.
       The 'sh' sound.
       OE 'sc' is always [ʃ].
       Tongue blade raised toward
       postalveolar region — further
       back than alveolar [s].
       Constriction broader, more diffuse.
       Centroid lower than [s]:
         [s]  ~7500 Hz
         [ʃ]  ~3500–5000 Hz
       Noise band wider and lower.
       Lip rounding coarticulation
       from following [y] — pulls
       centroid slightly lower than
       bare [ʃ] before unrounded vowel.
       Word-initial here.
       Onset ramp from silence.

       Extremely frequent in OE:
       scyld, scip, sceal, scēaf,
       sculon, scīnan, sceaft.
       Parameters here serve all of them.

REUSED PHONEMES:
  [y]:  ÞĒOD-CYNINGA (×2), CYNING
  [l]:  ÆÞELINGAS, ELLEN (×2 in geminate)
  [d]:  GĀR-DENA (×3), FREMEDON, GŌD

NOTE ON [ʃ] CENTROID TARGET:
  Measuring in band 2000–7000 Hz.
  [ʃ] energy concentrated 3000–6000 Hz.
  Lower than [s] (5000–22000 Hz target).
  Higher than [θ] (3500–6000 Hz target).
  Distinct from both.

CHANGE LOG:
  v1 — initial parameters
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS
# ============================================================

# SH — voiceless postalveolar fricative [ʃ]
SH_DUR_MS   = 80.0
SH_NOISE_CF = 3800.0
SH_NOISE_BW = 2400.0
SH_GAIN     = 0.30
# Secondary band — broad postalveolar
SH_SEC_CF   = 6000.0
SH_SEC_BW   = 2000.0
SH_SEC_GAIN = 0.20

# Y — short close front rounded [y]
Y_F      = [300.0, 1700.0, 2100.0, 3000.0]
Y_B      = [ 80.0,  120.0,  180.0,  250.0]
Y_GAINS  = [ 16.0,    8.0,    2.0,    0.5]
Y_DUR_MS = 55.0
Y_COART_ON  = 0.12
Y_COART_OFF = 0.12

# L — voiced alveolar lateral [l]
L_F      = [350.0,  900.0, 2500.0, 3200.0]
L_B      = [100.0,  150.0,  200.0,  280.0]
L_GAINS  = [ 12.0,    6.0,    1.5,    0.5]
L_DUR_MS = 65.0
L_COART_ON  = 0.15
L_COART_OFF = 0.15

# D — voiced alveolar stop [d]
D_DUR_MS  = 70.0
D_BURST_F = 1800.0
D_BURST_BW= 600.0
D_BURST_MS= 10.0
D_VOT_MS  = 6.0

PITCH_HZ = 145.0
DIL      = 1.0


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

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = min(fc / nyq, 0.499)
    b, a = butter(2, fc_, btype='low')
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

def synth_SH(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless postalveolar fricative [ʃ].
    Word-initial — onset from silence.
    Lip rounding coarticulation from
    following [y] — slight lower bias
    on centroid vs neutral [ʃ].
    Two noise bands combined:
      primary:   3800 Hz CF, 2400 Hz BW
      secondary: 6000 Hz CF, 2000 Hz BW
    Together produce the characteristic
    broad mid-high spectral shape of [ʃ].
    """
    dur_ms = SH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    # Primary band
    lo1    = max(SH_NOISE_CF - SH_NOISE_BW/2,
                 200.0)
    hi1    = min(SH_NOISE_CF + SH_NOISE_BW/2,
                 sr * 0.48)
    b1, a1 = safe_bp(lo1, hi1, sr)
    fric1  = lfilter(b1, a1, noise)
    # Secondary band
    lo2    = max(SH_SEC_CF - SH_SEC_BW/2,
                 200.0)
    hi2    = min(SH_SEC_CF + SH_SEC_BW/2,
                 sr * 0.48)
    b2, a2 = safe_bp(lo2, hi2, sr)
    fric2  = lfilter(b2, a2, noise)
    fric   = (fric1 * SH_GAIN
              + fric2 * SH_SEC_GAIN)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_dec  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_Y(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = Y_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(Y_COART_ON  * n_s)
    n_off  = int(Y_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else Y_F
    f_next = F_next if F_next is not None \
             else Y_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(Y_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(Y_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(Y_F[fi]))
        f_b   = float(Y_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(Y_B[fi])
        g   = float(Y_GAINS[fi])
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
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_L(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = L_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
    src    = f32(src * env)
    n_on   = int(L_COART_ON  * n_s)
    n_off  = int(L_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else L_F
    f_next = F_next if F_next is not None \
             else L_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(L_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(L_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(L_F[fi]))
        f_b   = float(L_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(L_B[fi])
        g   = float(L_GAINS[fi])
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
        result = f32(result / mx * 0.62)
    return f32(result)


def synth_D(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms    = D_DUR_MS * dil
    n_s       = max(4, int(
        dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(
        D_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(
        D_VOT_MS   / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)
    T         = 1.0 / sr
    src_c  = rosenberg_pulse(
        n_closure, pitch_hz, oq=0.65, sr=sr)
    env_c  = np.linspace(
        0.1, 0.3, n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(b_lp, a_lp,
                          src_c.astype(float))
                 * env_c * 0.3)
    noise  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst  = f32(lfilter(b_bp, a_bp, noise)
                 * 0.55)
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    vot    = apply_formants(
        src_v, L_F,
        [100.0, 150.0, 200.0, 280.0],
        [14.0, 7.0, 1.2, 0.4], sr=sr)
    vot    = f32(vot * 0.5)
    seg    = np.concatenate([murmur,
                              burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.65)
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

def synth_scyld(pitch_hz=PITCH_HZ,
                 dil=DIL,
                 add_room=False,
                 sr=SR):
    """[ʃ·y·l·d]"""
    sh_seg = synth_SH(
        F_next=Y_F, dil=dil, sr=sr)
    y_seg  = synth_Y(
        F_prev=Y_F, F_next=L_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    l_seg  = synth_L(
        F_prev=Y_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=L_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        sh_seg, y_seg, l_seg, d_seg])
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
    print("SCYLD RECONSTRUCTION v1")
    print("Old English [ʃyld]")
    print("Beowulf line 5, word 1")
    print()

    w_dry = synth_scyld(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/scyld_dry.wav",
        w_dry, SR)
    print(f"  scyld_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_scyld(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/scyld_hall.wav",
        w_hall, SR)
    print("  scyld_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/scyld_slow.wav",
        w_slow, SR)
    print("  scyld_slow.wav")

    w_perf = synth_scyld(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/scyld_performance.wav",
        w_perf, SR)
    print(f"  scyld_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # [ʃ] isolated for comparison with [s]
    sh_seg = synth_SH(Y_F, 1.0, SR)
    write_wav(
        "output_play/scyld_sh_only.wav",
        ola_stretch(sh_seg / (
            np.max(np.abs(sh_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  scyld_sh_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "scyld_sh_only.wav")
    print("  afplay output_play/"
          "scyld_dry.wav")
    print("  afplay output_play/"
          "scyld_slow.wav")
    print("  afplay output_play/"
          "scyld_hall.wav")
    print()
    print("  Line 5 in progress:")
    print("  Scyld Scefing"
          " sceaþena þreatum")
    print()
