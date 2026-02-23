"""
DEVAM RECONSTRUCTION v1
Vedic Sanskrit: devam  [devɑm]
Rigveda 1.1.1 — word 5
February 2026

PHONEMES:
  [d]  voiced dental stop             — NEW (dantya row 3)
  [eː] long close-mid front           — VS-verified ĪḶE
  [v]  voiced labio-dental approximant — NEW (dantauṣṭhya)
  [ɑ]  short open central             — VS-verified AGNI
  [m]  voiced bilabial nasal          — VS-verified PUROHITAM

SYLLABLE STRUCTURE:
  DE — VAM
  [deː] — [vɑm]

NEW PHONEMES — TWO:

[d] — voiced dental stop — द
  Śikṣā: dantya (row 3 — voiced unaspirated)
  Three-phase architecture:
    Phase 1: voiced closure murmur
             LF ratio >= 0.40
             Vocal folds vibrate during closure.
             Low-frequency energy throughout
             the silent interval.
    Phase 2: dental burst ~3500 Hz
             Same locus as [t] (3764 Hz verified).
             Burst weaker than [t]: voicing
             during closure partially vents
             intraoral pressure.
    Phase 3: short voiced VOT (10 ms)
             Into following vowel [eː].
  The voiced/voiceless distinction is in
  Phase 1 (LF ratio), not Phase 2 (burst locus).
  Both [d] and [t] are dantya — same place.
  The closure before the burst is what differs.

[v] — voiced labio-dental approximant — व
  Śikṣā: Pāṇinīya Śikṣā — oṣṭhya (labial).
          Ṛgveda Prātiśākhya — dantauṣṭhya
          (dental-labial — both teeth and lips).
          The Ṛgveda Prātiśākhya is the
          authoritative phonetic treatise for
          the Rigveda text being reconstructed.
          Its description — dantauṣṭhya —
          is adopted here.
  Articulation: lower lip to upper teeth.
  Approximant: no turbulence, no closure.
  NOT a fricative. Lower lip approaches
  the upper teeth without creating a
  turbulent jet. The distinction from
  modern English [v] (fricative) is
  acoustically significant.
  F2 target: ~1500 Hz — labio-dental range.
  This is ABOVE the bilabial range (~800–1200)
  and BELOW the palatal approximant [j] (2100 Hz).
  F2 sits between [oː] (757 Hz) and [eː] (1659 Hz).
  Clean position. Clear separation from both.

PHILOLOGICAL NOTE ON [v]:
  Pāṇinīya Śikṣā places va in oṣṭhya (labial).
  Ṛgveda Prātiśākhya III.30: "vaḥ dantauṣṭhyaḥ"
  — va is dental-labial.
  Taittirīya Prātiśākhya: oṣṭhya.
  The prātiśākhyas disagree.
  For this project (Rigveda 1.1):
  the Ṛgveda Prātiśākhya is the specific
  phonetic authority. Its dantauṣṭhya
  description is adopted. F2 ~1500 Hz.
  This is acoustically and philologically
  the better-grounded position for this text.

COARTICULATION:
  [d]  → [eː]: dental burst into long front vowel.
               F2 rises from ~3500 Hz burst locus
               into [eː] 1659 Hz steady state.
               (burst locus ≠ vowel F2 — the burst
               centroid is not the same dimension
               as the vowel formant. They are
               different spectral events.)
  [eː] → [v]:  long front vowel into labio-dental
               approximant. F2 falls from 1659 Hz
               toward 1500 Hz. Small drop.
               The [v] inherits the front vowel
               colouring from [eː].
  [v]  → [ɑ]:  labio-dental approximant into
               open vowel. F2 rises from 1500 Hz
               to 1106 Hz... wait: [ɑ] F2 is 1106 Hz.
               1500 → 1106: F2 FALLS slightly.
               The [v] is higher F2 than [ɑ].
               The transition is a modest F2 descent.
  [ɑ]  → [m]:  open vowel into bilabial nasal.
               F2 falls from 1106 Hz toward ~900 Hz.
               Nasal antiresonance appears.
               Standard nasal closure.

PERFORMANCE PARAMETERS:
  pitch_hz:     120.0
  dil:          1.0
  rt60:         1.5  (temple courtyard)
  direct_ratio: 0.55
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ── PHYSICS CONSTANTS ─────────────────────────────────

NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
DANTYA_BURST_LO_HZ     = 3000.0
DANTYA_BURST_HI_HZ     = 4500.0


# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────

VS_T_BURST_HZ    = 3764.0   # PUROHITAM verified
VS_G_BURST_HZ    = 2594.0   # ṚG/AGNI verified
VS_P_BURST_HZ    = 1204.0   # PUROHITAM verified
VS_JJ_BURST_HZ   = 3223.0   # YAJÑASYA verified
VS_M_F2_HZ       =  552.0   # PUROHITAM verified
VS_N_F2_HZ       =  900.0   # AGNI params
VS_J_F2_HZ       = 2028.0   # YAJÑASYA verified

# [eː] — ĪḶE verified
VS_EE_F          = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B          = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS      = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS     = 90.0

# [ɑ] — AGNI verified
VS_A_F           = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B           = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS       = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS      = 55.0

# [m] — PUROHITAM verified
VS_M_F           = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B           = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS       = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS      = 60.0
VS_M_ANTI_F      = 800.0
VS_M_ANTI_BW     = 200.0


# ── NEW PHONEME PARAMETERS ────────────────────────────

# [d] — voiced dental stop — द
# Śikṣā: dantya row 3 (voiced unaspirated)
# Same locus as [t] — dental burst ~3500 Hz.
# Voiced closure: LF ratio.
# Shorter VOT than [t]: voiced release.
VS_D_CLOSURE_MS  = 28.0
VS_D_BURST_F     = 3500.0
VS_D_BURST_BW    = 1500.0
VS_D_BURST_MS    = 8.0
VS_D_VOT_MS      = 10.0
VS_D_MURMUR_GAIN = 0.70
VS_D_BURST_GAIN  = 0.28   # slightly weaker than [t]
                           # voicing vents pressure

# [v] — voiced labio-dental approximant — व
# Ṛgveda Prātiśākhya: dantauṣṭhya
# F2 ~1500 Hz — labio-dental range.
# Broad bandwidths — approximant (loose contact).
# No Rosenberg amplitude dip — not a tap.
# No burst — not a stop.
# No turbulence — not a fricative.
VS_V_F           = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B           = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS       = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS      = 60.0
VS_V_COART_ON    = 0.18
VS_V_COART_OFF   = 0.18

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
    period  = int(sr / pitch_hz)
    pulse   = np.zeros(period, dtype=float)
    t1      = int(period * oq * 0.6)
    t2      = int(period * oq)
    for i in range(t1):
        pulse[i] = 0.5 * (
            1.0 - np.cos(np.pi * i / t1))
    for i in range(t1, t2):
        pulse[i] = np.cos(
            np.pi * (i - t1) /
            (2.0 * (t2 - t1)))
    d_pulse  = np.diff(pulse, prepend=pulse[0])
    n_reps   = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
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

def iir_notch(sig, fc, bw=200.0, sr=SR):
    nyq  = sr / 2.0
    fc   = min(max(fc, 20.0), nyq - 20.0)
    w0   = 2.0 * np.pi * fc / sr
    r    = 1.0 - np.pi * bw / sr
    r    = np.clip(r, 0.0, 0.999)
    b_n  = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n  = [1.0,
            -2.0 * r * np.cos(w0),
            r * r]
    return f32(lfilter(b_n, a_n,
                       sig.astype(float)))


# ── PHONEME SYNTHESISERS ──────────────────────────────

def synth_D(F_prev=None, F_next=None,
            dil=DIL, sr=SR):
    """
    [d] — voiced dental stop.
    Śikṣā: dantya row 3.
    Three-phase: murmur → burst → VOT.
    Voiced closure confirmed by LF ratio.
    Burst at dental locus ~3500 Hz.
    Same place as [t] — different voicing.
    """
    n_closure = int(
        VS_D_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        VS_D_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        VS_D_VOT_MS     * dil / 1000.0 * sr)

    # Phase 1: voiced closure murmur
    if n_closure > 0:
        src_cl = rosenberg_pulse(
            n_closure, PITCH_HZ, sr=sr)
        b_lp, a_lp = butter(
            2, 500.0 / (sr / 2.0),
            btype='low')
        murmur  = lfilter(
            b_lp, a_lp,
            src_cl.astype(float))
        closure = f32(murmur
                      * VS_D_MURMUR_GAIN)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: dental burst
    noise = np.random.randn(
        max(n_burst, 4)).astype(float)
    b_bp, a_bp = safe_bp(
        VS_D_BURST_F - VS_D_BURST_BW / 2,
        VS_D_BURST_F + VS_D_BURST_BW / 2,
        sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))
    burst = f32(burst * VS_D_BURST_GAIN)

    # Phase 3: voiced VOT into following vowel
    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, PITCH_HZ, sr=sr)
        f_vot   = (F_next if F_next is not None
                   else VS_EE_F)
        vot_env = np.linspace(0.0, 1.0, n_vot)
        vot     = apply_formants(
            src_vot, f_vot,
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5], sr=sr)
        vot     = f32(vot * vot_env * 0.12)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_V(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [v] — voiced labio-dental approximant.
    Ṛgveda Prātiśākhya: dantauṣṭhya.
    Lower lip to upper teeth.
    Approximant: no closure, no turbulence.
    NOT a fricative. NOT a tap. NOT a stop.
    Rosenberg pulse through formant bank.
    F2 ~1500 Hz — labio-dental position.
    Broad bandwidths model loose contact.
    No amplitude dip — NOT a tap.
    Same smooth envelope architecture as [j]
    but at labio-dental F2, not palatal F2.
    """
    n_ms  = VS_V_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_V_COART_ON  * n)
    off_n = int(VS_V_COART_OFF * n)

    f_mean = list(VS_V_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_V_F))):
            f_mean[k] = (F_prev[k] * 0.18
                         + VS_V_F[k] * 0.82)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_V_F))):
            f_mean[k] = (f_mean[k] * 0.82
                         + F_next[k] * 0.18)

    out = apply_formants(src, f_mean,
                         VS_V_B, VS_V_GAINS,
                         sr=sr)

    # Smooth envelope — approximant, not tap
    env = np.ones(n, dtype=float)
    atk = min(int(0.015 * sr), n // 4)
    rel = min(int(0.015 * sr), n // 4)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = f32(out * env)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.62
    return f32(out)


def synth_EE_vs(F_prev=None, F_next=None,
                pitch_hz=PITCH_HZ,
                dil=DIL, sr=SR):
    """[eː] — VS-verified ĪḶE."""
    n_ms  = VS_EE_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    coart = 0.10
    on_n  = int(coart * n)
    off_n = int(coart * n)

    f_mean = list(VS_EE_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_EE_F))):
            f_mean[k] = (F_prev[k] * 0.10
                         + VS_EE_F[k] * 0.90)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_EE_F))):
            f_mean[k] = (f_mean[k] * 0.90
                         + F_next[k] * 0.10)

    out = apply_formants(src, f_mean,
                         VS_EE_B, VS_EE_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_A_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """[ɑ] — VS-verified AGNI."""
    n_ms  = VS_A_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    coart = 0.12
    on_n  = int(coart * n)
    off_n = int(coart * n)

    f_mean = list(VS_A_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_A_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + VS_A_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_A_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         VS_A_B, VS_A_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_M_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """[m] — VS-verified PUROHITAM."""
    n_ms  = VS_M_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    coart = 0.15
    on_n  = int(coart * n)
    off_n = int(coart * n)

    f_mean = list(VS_M_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_M_F))):
            f_mean[k] = (F_prev[k] * 0.15
                         + VS_M_F[k] * 0.85)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_M_F))):
            f_mean[k] = (f_mean[k] * 0.85
                         + F_next[k] * 0.15)

    out = apply_formants(src, f_mean,
                         VS_M_B, VS_M_GAINS,
                         sr=sr)
    out = iir_notch(out,
                    VS_M_ANTI_F,
                    VS_M_ANTI_BW, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)


# ── ROOM MODEL ────────────────────────────────────────

def apply_simple_room(sig, rt60=1.5,
                      direct_ratio=0.55,
                      sr=SR):
    n_rev    = int(rt60 * sr)
    ir       = np.zeros(n_rev, dtype=float)
    ir[0]    = 1.0
    decay    = np.exp(
        -6.908 * np.arange(n_rev) /
        (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
    ir       = (direct_ratio * ir
                + (1.0 - direct_ratio)
                * noise_ir)
    ir       = ir / (np.max(np.abs(ir))
                     + 1e-12)
    out = np.convolve(
        sig.astype(float),
        ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ── WORD SYNTHESISER ──────────────────────────────────

def synth_devam(pitch_hz=PITCH_HZ,
                dil=DIL,
                with_room=False,
                sr=SR):
    """
    DEVAM [devɑm]
    Rigveda 1.1.1, word 5.
    The divine, the god, the shining one.

    Segments:
      D   [d]   voiced dental stop
      E   [eː]  long close-mid front (verified)
      V   [v]   labio-dental approximant
      A   [ɑ]   short open central (verified)
      M   [m]   bilabial nasal (verified)

    Coarticulation chain:
      D: word-initial, into [eː]
      E: from [d], into [v]
      V: from [eː], into [ɑ]
      A: from [v], into [m]
      M: from [ɑ], word-final
    """
    d_seg  = synth_D(F_prev=None,
                     F_next=VS_EE_F,
                     dil=dil, sr=sr)
    e_seg  = synth_EE_vs(F_prev=None,
                         F_next=VS_V_F,
                         pitch_hz=pitch_hz,
                         dil=dil, sr=sr)
    v_seg  = synth_V(F_prev=VS_EE_F,
                     F_next=VS_A_F,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)
    a_seg  = synth_A_vs(F_prev=VS_V_F,
                        F_next=VS_M_F,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)
    m_seg  = synth_M_vs(F_prev=VS_A_F,
                        F_next=None,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)

    word = np.concatenate([
        d_seg, e_seg, v_seg, a_seg, m_seg])

    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(
            word, rt60=1.5,
            direct_ratio=0.55, sr=sr)

    return f32(word)


# expose for diagnostic import
VS_D_BURST_F_VAL  = VS_D_BURST_F
VS_V_F2_VAL       = VS_V_F[1]
VS_D_CLOSURE_MS_V = VS_D_CLOSURE_MS
VS_D_BURST_MS_V   = VS_D_BURST_MS


# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Synthesising DEVAM [devɑm]...")

    dry  = synth_devam(with_room=False)
    hall = synth_devam(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/devam_dry.wav",  dry)
    write_wav("output_play/devam_hall.wav", hall)
    write_wav("output_play/devam_slow.wav", slow)

    # Isolated new phonemes
    for sig, name in [
        (synth_D(), "devam_d_iso"),
        (synth_V(), "devam_v_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))

    print("Written:")
    print("  output_play/devam_dry.wav")
    print("  output_play/devam_hall.wav")
    print("  output_play/devam_slow.wav")
    print("  Isolated: d, v")
    print()
    print("Run devam_diagnostic.py to verify.")
