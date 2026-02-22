"""
PÆÞ RECONSTRUCTION
Old English: pæþ
Meaning: path, way
IPA: [pæθ]
Purpose: Verify [p] — voiceless bilabial stop
Inventory completion series — word 4 of 4
February 2026

PHONEME STRUCTURE:
  P   [p]    voiceless bilabial stop    — NEW
  AE  [æ]    open front unrounded       — verified HWÆT
  TH  [θ]    voiceless dental fricative — verified ÞĒOD-CYNINGA

NEW PHONEMES:
  [p]: voiceless bilabial stop.
       Bilabial closure — both lips
       pressed together.
       Voiceless — no murmur during
       closure.
       Burst at release — broadband
       low-frequency dominated.
       Bilabial burst: lower frequency
       than alveolar [t] (~3500 Hz)
       or velar [k] (~1800 Hz).
       Bilabial burst centroid ~800 Hz.
       Aspiration follows burst —
       short VOT ~10 ms.

       [p] vs [t] vs [k]:
         [p]: bilabial — lips
              burst ~800 Hz
         [t]: alveolar — tongue tip
              burst ~3500 Hz
         [k]: velar — tongue dorsum
              burst ~1800 Hz
       Place of articulation encoded
       in burst frequency.

       [p] vs [b]:
         [p]: voiceless — no murmur
         [b]: voiced — murmur present
       Voicing is the sole distinction.
       [b] arrives next — line 8.
       The [p]/[b] pair will then
       be complete.

WORD STRUCTURE:
  pæþ — one syllable.
  [p] onset, [æ] nucleus, [θ] coda.
  Simple CVC.

ETYMOLOGY:
  pæþ — path, way, track.
  ModE 'path' — direct descendant.
  One of the clearest OE→ModE
  survival cases. Word, meaning,
  and rough sound all preserved.
  [p] is rare in native OE
  vocabulary — this is one of
  the cleaner examples.
  Cognate with German 'Pfad'.

NOTE ON [p] RARITY IN OE:
  [p] is the rarest stop in native
  OE vocabulary. Most OE words
  with [p] are Latin loanwords
  (papa, port, plante) or Norse
  borrowings. Native OE preferred
  [f] initially where other Germanic
  languages have [p]:
    OE 'feoh' vs German 'Pferd'
    OE 'fæder' vs Latin 'pater'
  The [p] in 'pæþ' is one of the
  genuine native OE [p] instances.

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

# P — voiceless bilabial stop [p]
# NEW PHONEME
# Bilabial closure — both lips.
# No murmur — voiceless throughout.
# Burst: low frequency bilabial ~800 Hz.
# VOT: aspiration ~10 ms.
P_DUR_MS    = 65.0
P_BURST_F   = 800.0
P_BURST_BW  = 600.0
P_BURST_MS  = 12.0
P_VOT_MS    = 10.0
P_BURST_GAIN= 0.60
P_VOT_GAIN  = 0.20

# AE — open front unrounded [æ]
AE_F      = [700.0, 1700.0, 2600.0, 3300.0]
AE_B      = [120.0,  150.0,  200.0,  280.0]
AE_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
AE_DUR_MS = 60.0
AE_COART_ON  = 0.12
AE_COART_OFF = 0.12

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

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

def synth_P(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    """
    Voiceless bilabial stop [p].
    NEW PHONEME.
    Three phases:
      1. Closure — silence.
         Both lips sealed.
         No voicing — no murmur.
         Intraoral pressure builds.
      2. Burst — broadband noise
         filtered around ~800 Hz.
         Bilabial release is
         lower frequency than
         alveolar [t] (~3500 Hz)
         or velar [k] (~1800 Hz).
         Place encoded in burst
         frequency.
      3. VOT — aspiration.
         Broadband noise decaying.
         Vocal folds not yet
         vibrating.
         Short — ~10 ms.
         Voiceless stop in OE
         word-initial position.

    [p] vs [b]:
      [p]: no murmur in closure
      [b]: murmur during closure
      Voicing is sole distinction.
      [b] verified next — line 8.
    """
    dur_ms    = P_DUR_MS * dil
    n_s       = max(4, int(
        dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(
        P_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(
        P_VOT_MS   / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)

    # Phase 1: closure — silence
    closure = np.zeros(n_closure,
                        dtype=DTYPE)

    # Phase 2: burst — bilabial ~800 Hz
    noise_b  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        P_BURST_F - P_BURST_BW / 2,
        P_BURST_F + P_BURST_BW / 2, sr)
    burst    = f32(lfilter(
        b_bp, a_bp, noise_b)
                   * P_BURST_GAIN)
    env_bu   = np.linspace(
        1.0, 0.1, n_burst).astype(DTYPE)
    burst    = f32(burst * env_bu)

    # Phase 3: VOT — aspiration
    noise_v  = np.random.randn(
        n_vot).astype(float)
    b_vp, a_vp = safe_bp(
        500.0, 8000.0, sr)
    vot      = f32(lfilter(
        b_vp, a_vp, noise_v)
                   * P_VOT_GAIN)
    env_vo   = np.linspace(
        0.5, 0.0, n_vot).astype(DTYPE)
    vot      = f32(vot * env_vo)

    seg      = np.concatenate([
        closure, burst, vot])
    mx       = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
    return f32(seg)


def synth_AE(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = AE_DUR_MS * dil
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
    n_on   = int(AE_COART_ON  * n_s)
    n_off  = int(AE_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else AE_F
    f_next = F_next if F_next is not None \
             else AE_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AE_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(AE_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(AE_F[fi]))
        f_b   = float(AE_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(AE_B[fi])
        g   = float(AE_GAINS[fi])
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
        result = f32(result / mx * 0.68)
    return f32(result)


def synth_TH(F_prev=None, F_next=None,
              dil=DIL, sr=SR):
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(TH_NOISE_CF - TH_NOISE_BW/2,
                 200.0)
    hi_    = min(TH_NOISE_CF + TH_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env * TH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.35)
    return f32(fric)


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

def synth_paeth(pitch_hz=PITCH_HZ,
                 dil=DIL,
                 add_room=False,
                 sr=SR):
    """[p·æ·θ]"""
    p_seg  = synth_P(
        F_prev=None, F_next=AE_F,
        dil=dil, sr=sr)
    ae_seg = synth_AE(
        F_prev=AE_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg = synth_TH(
        F_prev=AE_F, F_next=None,
        dil=dil, sr=sr)
    word   = np.concatenate([
        p_seg, ae_seg, th_seg])
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
    print("PÆÞ RECONSTRUCTION v1")
    print("Old English [pæθ]")
    print("Inventory completion — word 4 of 4")
    print("New phoneme: [p]")
    print()

    w_dry = synth_paeth(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/paeth_dry.wav",
        w_dry, SR)
    print(f"  paeth_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_paeth(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/paeth_hall.wav",
        w_hall, SR)
    print("  paeth_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/paeth_slow.wav",
        w_slow, SR)
    print("  paeth_slow.wav")

    # [p] burst isolated for inspection
    p_seg = synth_P(None, AE_F, 1.0, SR)
    write_wav(
        "output_play/paeth_p_only.wav",
        ola_stretch(p_seg / (
            np.max(np.abs(p_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  paeth_p_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "paeth_p_only.wav")
    print("  afplay output_play/"
          "paeth_dry.wav")
    print("  afplay output_play/"
          "paeth_slow.wav")
    print()
    print("  Inventory completion progress:")
    print("  [iː]  ✓ DONE — WĪF")
    print("  [eːɑ] ✓ DONE — ĒAGE")
    print("  [eːo] ✓ DONE — ÞĒOD")
    print("  [p]   — pending verification")
    print("  [b]   — pending — line 8")
    print()
