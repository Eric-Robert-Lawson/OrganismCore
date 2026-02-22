"""
ÞĒOD RECONSTRUCTION
Old English: þēod
Meaning: people, nation, tribe
IPA: [θeːod]
Purpose: Verify [eːo] — long front-mid diphthong
Inventory completion series — word 3 of 4
February 2026

PHONEME STRUCTURE:
  TH  [θ]    voiceless dental fricative  — verified ÞĒOD-CYNINGA
  EYO [eːo]  long front-mid diphthong   — NEW
  D   [d]    voiced alveolar stop        — verified GĀR-DENA

NEW PHONEMES:
  [eːo]: long front-mid diphthong.
         Long counterpart of [eo].
         Onset [eː]: F1 ~450, F2 ~1900 Hz
         Offset [o]: F1 ~450, F2 ~800 Hz
         Duration ~150 ms — long diphthong.
         ~double short [eo] duration (75 ms).

         F1 STABLE throughout —
         jaw does not open.
         This is the key distinction
         from [eːɑ] where F1 rises 281 Hz.

         F2 falls steeply:
         1900 → 800 Hz — delta ~1100 Hz.
         Steeper F2 fall than [eːɑ]
         (737 Hz) because target is
         more back: [o] vs [ɑ].

         Distinct from [eːɑ]:
           [eːɑ]: F1 rises 281 Hz
                  F2 falls 737 Hz
           [eːo]: F1 stable ~0 Hz
                  F2 falls ~1100 Hz

WORD STRUCTURE:
  þēod — one syllable.
  [θ] onset, [eːo] nucleus, [d] coda.
  The long diphthong is the entire
  syllable body.

ETYMOLOGY:
  þēod — people, nation, tribe.
  The word appears in line 2:
  þēod-cyninga — of the people's kings.
  Cognate with German 'Deutsch' —
  both from PGmc *þeudō — the people.
  The [eːo] is the long diphthong
  that became ModE 'th-' words
  via OE → ME sound changes.
  'Dutch' and 'Deutsch' and 'Theodore'
  all contain this root.

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

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

# EYO — long front-mid diphthong [eːo]
# NEW PHONEME
# Long counterpart of [eo].
# F1 STABLE — jaw does not open.
# F2 falls steeply: 1900 → 800 Hz
# Duration ~150 ms — long diphthong.
EYO_DUR_MS   = 150.0
EYO_F_ON     = [450.0, 1900.0, 2600.0, 3300.0]
EYO_F_OFF    = [450.0,  800.0, 2400.0, 3000.0]
EYO_B        = [100.0,  130.0,  200.0,  280.0]
EYO_GAINS    = [ 16.0,    8.0,    1.5,    0.5]
EYO_TRANS_ON  = 0.25
EYO_TRANS_OFF = 0.85

# D — voiced alveolar stop [d]
D_DUR_MS   = 60.0
D_BURST_F  = 3500.0
D_BURST_BW = 1500.0
D_BURST_MS = 8.0
D_VOT_MS   = 5.0

# E — short close-mid front [e]
# used for F_next reference only
E_F = [450.0, 1900.0, 2600.0, 3300.0]

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


def synth_EYO(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """
    Long front-mid diphthong [eːo].
    NEW PHONEME.
    Long counterpart of short [eo].
    Identical trajectory — double duration.
    Onset:  F1 450, F2 1900 Hz
    Offset: F1 450, F2  800 Hz

    KEY: F1 STABLE at 450 Hz throughout.
    Jaw does not open.
    This distinguishes [eːo] from [eːɑ]
    where F1 rises 281 Hz.

    F2 falls steeply: 1900 → 800 Hz
    Delta ~1100 Hz — steeper than [eːɑ]
    (737 Hz) because [o] target is
    more back than [ɑ] target.
    """
    dur_ms = EYO_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    i_ton  = int(EYO_TRANS_ON  * n_s)
    i_toff = int(EYO_TRANS_OFF * n_s)
    n_trans= max(1, i_toff - i_ton)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EYO_F_ON)):
        f_on  = float(EYO_F_ON[fi])
        f_off = float(EYO_F_OFF[fi])
        bw    = float(EYO_B[fi])
        g     = float(EYO_GAINS[fi])
        f_arr = np.full(n_s, f_on,
                         dtype=DTYPE)
        if i_ton > 0:
            f_arr[:i_ton] = f_on
        if i_toff <= n_s:
            f_arr[i_ton:i_toff] = \
                np.linspace(f_on, f_off,
                             n_trans)
        if i_toff < n_s:
            f_arr[i_toff:] = f_off
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48,
                float(f_arr[i])))
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
        n_closure, pitch_hz,
        oq=0.65, sr=sr)
    env_c  = np.linspace(
        0.3, 0.1, n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(
        b_lp, a_lp,
        src_c.astype(float))
                 * env_c * 0.30)
    noise  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst  = f32(lfilter(
        b_bp, a_bp, noise) * 0.55)
    env_bu = np.linspace(
        1.0, 0.2, n_burst).astype(DTYPE)
    burst  = f32(burst * env_bu)
    f_next_use = F_next if F_next \
                 is not None else E_F
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    vot    = apply_formants(
        src_v, f_next_use,
        [100.0, 130.0, 200.0, 280.0],
        [14.0,   7.0,   1.5,   0.5],
        sr=sr)
    vot    = f32(vot * 0.40)
    seg    = np.concatenate([
        murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
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

def synth_theod(pitch_hz=PITCH_HZ,
                 dil=DIL,
                 add_room=False,
                 sr=SR):
    """[θ·eːo·d]"""
    th_seg  = synth_TH(
        F_prev=None, F_next=EYO_F_ON,
        dil=dil, sr=sr)
    eyo_seg = synth_EYO(
        F_prev=EYO_F_ON, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg   = synth_D(
        F_prev=EYO_F_OFF, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word    = np.concatenate([
        th_seg, eyo_seg, d_seg])
    mx      = np.max(np.abs(word))
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
    print("ÞĒOD RECONSTRUCTION v1")
    print("Old English [θeːod]")
    print("Inventory completion — word 3 of 4")
    print("New phoneme: [eːo]")
    print()

    w_dry = synth_theod(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/theod_dry.wav",
        w_dry, SR)
    print(f"  theod_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_theod(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/theod_hall.wav",
        w_hall, SR)
    print("  theod_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/theod_slow.wav",
        w_slow, SR)
    print("  theod_slow.wav")

    eyo_seg = synth_EYO(EYO_F_ON, None,
                         145.0, 1.0, SR)
    write_wav(
        "output_play/theod_eyo_only.wav",
        ola_stretch(eyo_seg / (
            np.max(np.abs(eyo_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  theod_eyo_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "theod_eyo_only.wav")
    print("  afplay output_play/"
          "theod_dry.wav")
    print("  afplay output_play/"
          "theod_slow.wav")
    print()
    print("  Inventory completion progress:")
    print("  [iː]  ✓ DONE — WĪF")
    print("  [eːɑ] ✓ DONE — ĒAGE")
    print("  [eːo] — pending verification")
    print("  [p]   — pending — PÆÞ")
    print("  [b]   — pending — line 8")
    print()
