"""
GŌD RECONSTRUCTION
Old English: gōd
Meaning: good
IPA: [ɡoːd]
Beowulf: Line 4, Word 3 (overall word 16)
February 2026

PHONEME STRUCTURE:
  G   [ɡ]   voiced velar stop           — verified GĀR-DENA
  Ō   [oː]  long close-mid back rounded — NEW
  D   [d]   voiced alveolar stop        — verified GĀR-DENA

NEW PHONEMES:
  [oː]: long close-mid back rounded.
        Long counterpart of [o].
        Same formant targets as [o]:
          F1 ~430 Hz — close-mid height
          F2 ~700 Hz — back position
        Duration 120–200 ms — long vowel.
        Pure monophthong — no offglide.
        Modern English [oʊ] in 'go','no'
        has diphthongized. OE [oː] has not.
        Lips rounded throughout.
        Tongue body raised toward velum.
        Word-medial �� standard long vowel
        envelope, no word-final extension.

        Appears in core heroic vocabulary:
        gōd, mōd, dōm, blōd, gōdne.
        Hundreds of instances in Beowulf.
        Getting this right pays dividends
        for the entire poem.

REUSED PHONEMES:
  [ɡ]:  GĀR-DENA, GĒAR-DAGUM, GEFRŪNON,
        ÆÞELINGAS, FREMEDON (×5 total)
  [d]:  GĀR-DENA (×3), FREMEDON

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

# G — voiced velar stop [ɡ]
G_DUR_MS  = 75.0
G_BURST_F = 1400.0
G_BURST_BW= 600.0
G_BURST_MS= 12.0
G_VOT_MS  = 8.0

# OO — long close-mid back rounded [oː]
# Same formant targets as short [o].
# Duration 150 ms — long vowel.
# Pure monophthong — steady state held.
# Word-medial — symmetric envelope.
OO_F      = [430.0,  700.0, 2400.0, 3200.0]
OO_B      = [ 90.0,  120.0,  200.0,  280.0]
OO_GAINS  = [ 18.0,    7.0,    1.2,    0.4]
OO_DUR_MS = 150.0
OO_COART_ON  = 0.10   # 10% transition in
OO_COART_OFF = 0.10   # 10% transition out

# Short [o] for reference/coarticulation
O_F = [430.0, 700.0, 2400.0, 3200.0]

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

def synth_G(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms    = G_DUR_MS * dil
    n_s       = max(4, int(dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(G_BURST_MS
                           / 1000.0 * sr))
    n_vot     = max(2, int(G_VOT_MS
                           / 1000.0 * sr))
    n_closure = max(2, n_s - n_burst - n_vot)
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
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    burst  = f32(lfilter(b_bp, a_bp, noise)
                 * 0.6)
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    f_nxt  = (F_next if F_next is not None
              else OO_F)
    vot    = apply_formants(
        src_v, f_nxt,
        [100.0, 150.0, 200.0, 280.0],
        [14.0, 7.0, 1.2, 0.4], sr=sr)
    vot    = f32(vot * 0.5)
    seg    = np.concatenate([murmur,
                              burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.65)
    return f32(seg)


def synth_OO(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Long close-mid back rounded [oː].
    Same formant targets as short [o].
    Duration 150 ms — long vowel standard.
    Pure monophthong — no offglide.
    Symmetric envelope word-medial.
    """
    dur_ms = OO_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Symmetric envelope — long vowel
    # has longer steady state than short.
    n_atk  = min(int(0.015 * sr), n_s // 5)
    n_rel  = min(int(0.020 * sr), n_s // 5)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(OO_COART_ON  * n_s)
    n_off  = int(OO_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else OO_F
    f_next = F_next if F_next is not None \
             else OO_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(OO_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(OO_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(OO_F[fi]))
        f_b   = float(OO_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(OO_B[fi])
        g   = float(OO_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
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
        result = f32(result / mx * 0.72)
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
    f_nxt  = (F_next if F_next is not None
              else OO_F)
    vot    = apply_formants(
        src_v, f_nxt,
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

def synth_god(pitch_hz=PITCH_HZ,
               dil=DIL,
               add_room=False,
               sr=SR):
    """[ɡ·oː·d]"""
    g_seg  = synth_G(
        F_prev=None, F_next=OO_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    oo_seg = synth_OO(
        F_prev=OO_F, F_next=OO_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=OO_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        g_seg, oo_seg, d_seg])
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
    print("GŌD RECONSTRUCTION v1")
    print("Old English [ɡoːd]")
    print("Beowulf line 4, word 3")
    print()

    w_dry = synth_god(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/god_dry.wav",
        w_dry, SR)
    print(f"  god_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_god(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/god_hall.wav",
        w_hall, SR)
    print("  god_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/god_slow.wav",
        w_slow, SR)
    print("  god_slow.wav")

    w_perf = synth_god(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/god_performance.wav",
        w_perf, SR)
    print(f"  god_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # [oː] vs [o] comparison
    oo_seg = synth_OO(OO_F, OO_F,
                       145.0, 1.0, SR)
    from scipy.signal import butter
    # short [o] for comparison
    o_n  = max(4, int(65.0 / 1000.0 * SR))
    o_src = rosenberg_pulse(
        o_n, 145.0, 0.65, SR)
    o_env = np.ones(o_n, dtype=DTYPE)
    n_a = min(int(0.012 * SR), o_n // 4)
    n_r = min(int(0.020 * SR), o_n // 4)
    if n_a < o_n:
        o_env[:n_a] = np.linspace(
            0.4, 1.0, n_a)
    if n_r < o_n:
        o_env[-n_r:] = np.linspace(
            1.0, 0.5, n_r)
    o_src = f32(o_src * o_env)
    o_seg = apply_formants(
        o_src, OO_F,
        [90.0, 120.0, 200.0, 280.0],
        [18.0, 7.0, 1.2, 0.4], SR)
    mx_o = np.max(np.abs(o_seg))
    if mx_o > 1e-8:
        o_seg = f32(o_seg / mx_o * 0.68)

    write_wav(
        "output_play/god_oo_long.wav",
        ola_stretch(oo_seg / (
            np.max(np.abs(oo_seg))+1e-8)
            * 0.75, 4.0), SR)
    write_wav(
        "output_play/god_o_short.wav",
        ola_stretch(o_seg / (
            np.max(np.abs(o_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  god_oo_long.wav   (4x slow)")
    print("  god_o_short.wav   (4x slow)")
    print()
    print("  afplay output_play/"
          "god_o_short.wav")
    print("  afplay output_play/"
          "god_oo_long.wav")
    print("  afplay output_play/god_dry.wav")
    print("  afplay output_play/god_slow.wav")
    print("  afplay output_play/god_hall.wav")
    print()
    print("  Line 4 in progress:")
    print("  þæt wæs gōd cyning")
    print()
