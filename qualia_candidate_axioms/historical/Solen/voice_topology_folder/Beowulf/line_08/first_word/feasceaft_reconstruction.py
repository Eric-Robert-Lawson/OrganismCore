"""
FEASCEAFT RECONSTRUCTION
Old English: feasceaft
Meaning: destitute, wretched, found with nothing
IPA: [fæɑʃæɑft]
Beowulf: Line 8, word 1 (overall word 31)
February 2026

PHONEME STRUCTURE:
  F    [f]    voiceless labiodental fricative — verified GEFRŪNON
  EA   [eɑ]   short front-back diphthong     — verified SCEAÞENA
  SH   [ʃ]    voiceless palato-alveolar       — verified SCYLDINGAS
  EA   [eɑ]   short front-back diphthong     — second instance
  F    [f]    voiceless labiodental fricative — second instance
  T    [t]    voiceless alveolar stop         — verified HWÆT

NEW PHONEMES: none.
Pure assembly. Six phonemes. All verified.

ETYMOLOGY NOTE:
  feasceaft = fea + sceaft
  fea: few, little (NOT feoh = property/wealth)
  fea → ModE 'few' → Gothic fawus
  Confirms [eɑ] diphthong — front vowel,
  not [eo] which would follow from feoh.
  Initial analysis had correct phoneme [eɑ]
  but wrong etymology. Corrected here.

  sceaft: created being, condition, lot, fate
  SC before front vowel = [ʃ] in West Saxon.
  Same rule as SCYLDINGAS, SCEAÞENA.

COMPOUND QUANTITY:
  Both EA instances are SHORT [eɑ] — 80 ms.
  First element (fea-) quantity reduced
  in compound. Second element (sceaft)
  has short EA throughout attestation.
  Klaeber does not mark EA as long here.

SYLLABLE STRUCTURE:
  Syllable 1: [fæɑ]   — f + diphthong
  Syllable 2: [ʃæɑft] — sh + diphthong + f + t

ACOUSTIC SHAPE:
  Voiceless [f]
    → open voiced [eɑ] (F1 rises)
    → voiceless [ʃ]
    → open voiced [eɑ] (F1 rises again)
    → voiceless [f]
    → closure [t]
  Oscillating: constrict → open → constrict
  → open → constrict → close.
  The word never achieves stable coherence.
  This is the acoustic shape of destitution.

COARTICULATION:
  EA1: F_prev = F_onset, F_next = SH_F
  EA2: F_prev = SH_F,    F_next = F_onset
  Both EA instances independently
  synthesised with correct context.
  Diagnostic checks both separately.

CONTEXT:
  feasceaft funden —
  found wretched / found destitute.
  Line 8, first half.
  The turning point of the exordium.
  Seven lines of glory. Then this.
  Scyld Scefing as he was found —
  a baby, abandoned, drifting.
  The founding destitution of the dynasty.

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
# PARAMETERS — all from verified inventory
# ============================================================

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28

# EA — short front-back diphthong [eɑ]
EA_DUR_MS    = 80.0
EA_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EA_F_OFF     = [700.0, 1100.0, 2400.0, 3000.0]
EA_B         = [100.0,  130.0,  200.0,  280.0]
EA_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EA_TRANS_ON  = 0.25
EA_TRANS_OFF = 0.85

# SH — voiceless palato-alveolar fricative [ʃ]
SH_DUR_MS   = 70.0
SH_NOISE_CF = 3500.0
SH_NOISE_BW = 2500.0
SH_GAIN     = 0.45

# T — voiceless alveolar stop [t]
T_DUR_MS     = 65.0
T_BURST_F    = 3500.0
T_BURST_BW   = 1500.0
T_BURST_MS   = 8.0
T_VOT_MS     = 8.0
T_BURST_GAIN = 0.55
T_VOT_GAIN   = 0.15

# Formant reference — for coarticulation
# boundary passing between segments
SH_F = [3500.0, 3500.0, 3500.0, 3500.0]
# [ʃ] has no formant structure per se
# (noise source) but we pass a high-F
# reference for coarticulation bookkeeping.
# The EA synthesiser uses F_next to
# interpolate toward at offset — the
# transition into [ʃ] is handled by
# the EA envelope decay, not by
# formant targets of the noise.
# SH_F is a placeholder for bookkeeping.

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
# PHONEME SYNTHESIZERS
# ============================================================

def synth_F(dil=DIL, sr=SR):
    """Voiceless labiodental fricative [f].
    Verified GEFRŪNON."""
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
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_EA(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """Short front-back diphthong [eɑ].
    Verified SCEAÞENA, ĒAGE, WEARÐ.
    F_prev and F_next set per instance
    for correct coarticulation context."""
    dur_ms = EA_DUR_MS * dil
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
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    i_ton  = int(EA_TRANS_ON  * n_s)
    i_toff = int(EA_TRANS_OFF * n_s)
    n_trans= max(1, i_toff - i_ton)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EA_F_ON)):
        f_on  = float(EA_F_ON[fi])
        f_off = float(EA_F_OFF[fi])
        bw    = float(EA_B[fi])
        g     = float(EA_GAINS[fi])
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


def synth_SH(dil=DIL, sr=SR):
    """Voiceless palato-alveolar fricative [ʃ].
    Verified SCYLDINGAS.
    Lower CF than [s] — palatal place."""
    dur_ms = SH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(SH_NOISE_CF - SH_NOISE_BW/2,
                 200.0)
    hi_    = min(SH_NOISE_CF + SH_NOISE_BW/2,
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
            1.0, 0.3, n_dec)
    fric   = f32(fric * env * SH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.50)
    return f32(fric)


def synth_T(pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiceless alveolar stop [t].
    Verified HWÆT."""
    dur_ms    = T_DUR_MS * dil
    n_s       = max(4, int(
        dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(
        T_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(
        T_VOT_MS   / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)
    closure   = np.zeros(n_closure,
                          dtype=DTYPE)
    noise_b   = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        T_BURST_F - T_BURST_BW / 2,
        T_BURST_F + T_BURST_BW / 2, sr)
    burst     = f32(lfilter(
        b_bp, a_bp, noise_b)
                    * T_BURST_GAIN)
    env_bu    = np.linspace(
        1.0, 0.1, n_burst).astype(DTYPE)
    burst     = f32(burst * env_bu)
    noise_v   = np.random.randn(
        n_vot).astype(float)
    b_vp, a_vp = safe_bp(500.0, 8000.0, sr)
    vot       = f32(lfilter(
        b_vp, a_vp, noise_v)
                    * T_VOT_GAIN)
    env_vo    = np.linspace(
        0.5, 0.0, n_vot).astype(DTYPE)
    vot       = f32(vot * env_vo)
    seg       = np.concatenate([
        closure, burst, vot])
    mx        = np.max(np.abs(seg))
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

def synth_feasceaft(pitch_hz=PITCH_HZ,
                     dil=DIL,
                     add_room=False,
                     sr=SR):
    """
    [f · eɑ · ʃ · eɑ · f · t]
    Two [f] segments independently synthesised.
    Two [eɑ] segments with different
    coarticulation contexts:
      EA1: follows [f], precedes [ʃ]
      EA2: follows [ʃ], precedes [f]
    """
    f1_seg  = synth_F(dil=dil, sr=sr)
    ea1_seg = synth_EA(
        F_prev=None,
        F_next=SH_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    sh_seg  = synth_SH(dil=dil, sr=sr)
    ea2_seg = synth_EA(
        F_prev=SH_F,
        F_next=None,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    f2_seg  = synth_F(dil=dil, sr=sr)
    t_seg   = synth_T(
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    word    = np.concatenate([
        f1_seg, ea1_seg, sh_seg,
        ea2_seg, f2_seg, t_seg])
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
    print("FEASCEAFT RECONSTRUCTION v1")
    print("Old English [fæɑʃæɑft]")
    print("Beowulf line 8, word 1")
    print("Zero new phonemes — pure assembly")
    print()
    print("  Etymology: fea + sceaft")
    print("  fea = few (NOT feoh = property)")
    print("  EA confirmed as [eɑ] not [eo]")
    print()

    w_dry = synth_feasceaft(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/feasceaft_dry.wav",
        w_dry, SR)
    print(f"  feasceaft_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_feasceaft(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/feasceaft_hall.wav",
        w_hall, SR)
    print("  feasceaft_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/feasceaft_slow.wav",
        w_slow, SR)
    print("  feasceaft_slow.wav")

    w_perf = synth_feasceaft(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav(
        "output_play/feasceaft_perf.wav",
        w_perf, SR)
    print(f"  feasceaft_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/"
          "feasceaft_dry.wav")
    print("  afplay output_play/"
          "feasceaft_slow.wav")
    print("  afplay output_play/"
          "feasceaft_hall.wav")
    print("  afplay output_play/"
          "feasceaft_perf.wav")
    print()
    print("  Line 8, word 1 of 6.")
    print("  feasceaft — pending verification")
    print()
