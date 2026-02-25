#!/usr/bin/env python3
"""
========================================================================
ĪḶE RECONSTRUCTION v1
Vedic Sanskrit: īḷe  [iːɭeː]
Rigveda 1.1.1 — word 2
February 2026
========================================================================

PHONEMES:
  [iː] long close front unrounded  — length variant of verified [i]
  [ɭ]  retroflex lateral approximant — NEW (mūrdhanya + lateral)
  [eː] long close-mid front unrounded — verified DEVAM v1

SYLLABLE STRUCTURE:
  Ī  — [iː] — long vowel, heavy syllable
  ḶE — [ɭeː] — retroflex lateral + mid vowel

SYNTHESIS ENGINE: canonical HOTĀRAM v9 infrastructure.
  rosenberg_pulse, apply_formants (b=[1.0-r]),
  iir_notch, norm_to_peak, write_wav.

ALL PARAMETERS derived from:
  1. Physics of the vocal tract
  2. Śikṣā treatise classification
  3. Vedic orthographic record
  4. Comparative Indo-European evidence
  5. Acoustic measurement of living cognate languages and reciters

ŚIKṢĀ CLASSIFICATION:
  [iː] — tālavya (palatal)
          Same position as verified [i] (AGNI).
          Duration is the only distinction.
          Śikṣā does not distinguish short and long by quality —
          only by quantity. Same tongue position. Same formant
          targets. Longer hold.

  [ɭ]  — mūrdhanya (retroflex/cerebral) + lateral manner
          Tongue tip retroflexed to post-alveolar region.
          Lateral airflow around the sides of the tongue.
          Two simultaneous constraints:
            Retroflex: F3 depressed < 2500 Hz (mūrdhanya marker)
            Lateral:   F2 reduced ~1000–1200 Hz
          The first VS phoneme in two Śikṣā classes simultaneously.

  [eː] — tālavya (palatal)
          Mid front vowel. Between [i] and [ɑ] in both F1 and F2.
          Sanskrit [e] is always long — no short counterpart.
          Tālavya because the tongue body is raised toward the palate,
          though not as high as for [i].

NEW ARCHITECTURE:
  [ɭ]: lateral approximant synthesis.
       Rosenberg source through formant bank at lateral targets.
       The lateral configuration reduces F2 relative to central
       approximants at the same place.
       Additionally: iir_notch() at F3 for the mūrdhanya marker.
       The F3 dip must be present — otherwise the tongue is not
       curled and the phoneme is a plain [l], not [ɭ].

  [iː]: same synthesiser as [i]. Duration parameter doubled.
        No new architecture required.

  [eː]: verified in DEVAM v1. Same formant targets.

COARTICULATION:
  [iː] → [ɭ]: long close front into retroflex lateral.
               F2 drops from ~2200 Hz to ~1100 Hz through transition.
               F3 drops as tongue curls back.
  [ɭ]  → [eː]: retroflex lateral into mid front vowel.
                F2 rises from ~1100 Hz to ~1750 Hz.
                F3 rises back toward neutral as tongue uncurls.

ALL-VOICED word — no pluck, no closing tail / opening head.
Continuous Rosenberg voicing throughout.

Ancestors:
  HOTĀRAM v9 (canonical infrastructure)
  DEVAM v1 ([eː] parameters verified, all-voiced architecture)
  AGNI ([i] formant targets verified)
  ṚG ([ɻ̩] mūrdhanya F3 depression verified)
  RATNADHĀTAMAM v17 (norm_to_peak canonical)

========================================================================
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================================
# PHYSICS CONSTANTS
# ============================================================================

NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
# F3 of an unconstricted alveolar vocal tract.
# Calculated from tube acoustics.
# Language-independent physics constant.
# The baseline from which retroflex F3 depression is measured.


# ============================================================================
# ŚIKṢĀ REFERENCES — VS-internal verified values
# ============================================================================

MURDHANYA_F3_DEPRESSION_MIN_HZ = 200.0
# Mūrdhanya F3 depression minimum.
# Established in ṚG: [ɻ̩] depression 345 Hz.
# Same criterion applies to all mūrdhanya phonemes including [ɭ].

MURDHANYA_F2_LO_HZ = 1000.0
MURDHANYA_F2_HI_HZ = 1500.0
# Mūrdhanya lateral F2 range.
# Lower than central mūrdhanya [ɻ̩] because lateral airflow
# further reduces F2 relative to central approximants at the same place.

TALAVYA_F2_MID_LO_HZ = 1500.0
TALAVYA_F2_MID_HI_HZ = 2000.0
# Tālavya mid vowel [eː] F2 range.
# Below [i] (2124 Hz — AGNI verified).
# Above [ɑ] (1106 Hz — AGNI verified).

TALAVYA_F1_MID_LO_HZ = 380.0
TALAVYA_F1_MID_HI_HZ = 550.0
# [eː] F1 range. Mid height.
# Above [i] (~280 Hz). Below [ɑ] (631 Hz — AGNI verified).


# ============================================================================
# VS-INTERNAL VERIFIED REFERENCES
# ============================================================================

VS_I_F2_HZ   = 2124.0
VS_I_DUR_MS  = 50.0
# [i] verified AGNI — February 2026.

VS_RV_F2_HZ  = 1212.0
VS_RV_F3_HZ  = 2355.0
# [ɻ̩] verified ṚG — February 2026.

VS_A_F1_HZ   = 631.0
VS_A_F2_HZ   = 1106.0
# [ɑ] verified AGNI — February 2026.


# ============================================================================
# PHONEME PARAMETERS
# ============================================================================

# ── [iː] — long close front unrounded — ई ──────────────────────────────────
# Śikṣā: tālavya
# Same position as verified [i]. Duration >= 1.7× VS_I_DUR_MS = 85 ms.
VS_II_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_II_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_II_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_II_DUR_MS = 100.0    # long: 2.0× [i] at 50 ms
VS_II_COART_ON  = 0.10
VS_II_COART_OFF = 0.10

# ── [ɭ] — retroflex lateral approximant — ळ ─────────────────────────────────
# Śikṣā: mūrdhanya + lateral
# Two simultaneous constraints:
#   Retroflex: F3 < 2500 Hz (mūrdhanya marker)
#   Lateral:   F2 ~1100 Hz (reduced by lateral flow)
# The F3 dip is the primary diagnostic.
# If F3 is not depressed, the tongue is not curled — the phoneme is wrong.
VS_LL_F      = [400.0, 1100.0, 2100.0, 3000.0]
VS_LL_B      = [200.0,  350.0,  400.0,  400.0]
VS_LL_GAINS  = [ 10.0,    5.0,    1.5,    0.4]
VS_LL_DUR_MS = 70.0
VS_LL_F3_NOTCH    = 2100.0
VS_LL_F3_NOTCH_BW = 350.0
VS_LL_COART_ON    = 0.15
VS_LL_COART_OFF   = 0.15

# ── [eː] — long close-mid front unrounded — ए ──────────────────────────────
# Śikṣā: tālavya
# Sanskrit [e] is always long. No short counterpart.
# Mid front — between [i] and [ɑ].
# Verified: DEVAM v1 (F1 390 Hz, F2 1757 Hz)
VS_EE_F      = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B      = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS = 90.0
VS_EE_COART_ON  = 0.10
VS_EE_COART_OFF = 0.10

PITCH_HZ = 120.0
DIL      = 1.0


# ============================================================================
# SEGMENT MAP — ĪḶE [iːɭeː]
# ============================================================================

SEG_II = 0    # [iː] long close front
SEG_LL = 1    # [ɭ]  retroflex lateral approximant
SEG_EE = 2    # [eː] long close-mid front

SEG_NAMES = [
    "[iː] long close front",
    "[ɭ] retroflex lateral approximant",
    "[eː] long close-mid front",
]

SEG_DURATIONS_MS = [
    VS_II_DUR_MS,    # 100.0
    VS_LL_DUR_MS,    #  70.0
    VS_EE_DUR_MS,    #  90.0
]

# All voiced — no unvoiced segments
UNVOICED_INDICES = set()


# ============================================================================
# DSP INFRASTRUCTURE (canonical from HOTĀRAM v9)
# ============================================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)


def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))


def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())
    print(f"  Wrote {path}")


def norm_to_peak(sig, target_peak):
    """Normalize signal to target peak amplitude."""
    mx = np.max(np.abs(sig))
    if mx > 1e-8:
        return f32(sig / mx * target_peak)
    return f32(sig)


def rosenberg_pulse(n_samples, pitch_hz, oq=0.65, sr=SR):
    """Differentiated Rosenberg glottal pulse train."""
    period = int(sr / pitch_hz)
    if period < 1:
        period = 1
    pulse = np.zeros(period, dtype=float)
    t1 = int(period * oq * 0.6)
    t2 = int(period * oq)
    for i in range(t1):
        pulse[i] = 0.5 * (1.0 - np.cos(np.pi * i / t1))
    for i in range(t1, t2):
        pulse[i] = np.cos(np.pi * (i - t1) / (2.0 * (t2 - t1)))
    d_pulse = np.diff(pulse, prepend=pulse[0])
    n_reps = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])


def apply_formants(src, freqs, bws, gains, sr=SR):
    """Parallel IIR resonator bank — canonical from HOTĀRAM v9."""
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f0, bw, g in zip(freqs, bws, gains):
        if f0 <= 0 or f0 >= nyq:
            continue
        r = np.exp(-np.pi * bw / sr)
        cosf = 2.0 * np.cos(2.0 * np.pi * f0 / sr)
        a = [1.0, -r * cosf, r * r]
        b_ = [1.0 - r]
        res = lfilter(b_, a, src.astype(float))
        out += res * g
    return f32(out)


def iir_notch(sig, fc, bw=200.0, sr=SR):
    """
    IIR notch filter for spectral zeros.
    Used for mūrdhanya F3 depression and nasal antiformants.
    fc: centre frequency of the zero.
    bw: bandwidth of the notch.
    """
    nyq = sr / 2.0
    fc = min(max(fc, 20.0), nyq - 20.0)
    w0 = 2.0 * np.pi * fc / sr
    r = 1.0 - np.pi * bw / sr
    r = np.clip(r, 0.0, 0.999)
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))


def ola_stretch(sig, factor=6.0, sr=SR):
    """Overlap-add time stretch for slow playback."""
    win_ms = 40.0
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in = win_n // 4
    hop_out = int(hop_in * factor)
    window = np.hanning(win_n).astype(DTYPE)
    n_in = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out = hop_out * n_frames + win_n
    out = np.zeros(n_out, dtype=DTYPE)
    norm_buf = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos + win_n] * window
        out[out_pos:out_pos + win_n] += frame
        norm_buf[out_pos:out_pos + win_n] += window
    nz = norm_buf > 1e-8
    out[nz] /= norm_buf[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


def apply_simple_room(sig, rt60=1.5, direct_ratio=0.55, sr=SR):
    """Temple courtyard reverb — canonical."""
    n_rev = int(rt60 * sr)
    ir = np.zeros(n_rev, dtype=float)
    ir[0] = 1.0
    decay = np.exp(-6.908 * np.arange(n_rev) / (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
    ir = direct_ratio * ir + (1.0 - direct_ratio) * noise_ir
    ir = ir / (np.max(np.abs(ir)) + 1e-12)
    out = np.convolve(sig.astype(float), ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_II(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [iː] — long close front unrounded vowel.

    Śikṣā: tālavya.
    Same formant targets as verified [i] (AGNI).
    Duration is the phonemic distinction: 100ms (2× short [i] at 50ms).
    Length >= 1.7× [i] duration per Śikṣā quantity rules.

    Coarticulation: 10% weight from neighbors.
    """
    n = int(VS_II_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_II_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_II_F))):
            f_mean[k] = (F_prev[k] * VS_II_COART_ON
                         + VS_II_F[k] * (1.0 - VS_II_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_II_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_II_COART_OFF)
                         + F_next[k] * VS_II_COART_OFF)

    out = apply_formants(src, f_mean, VS_II_B, VS_II_GAINS, sr=sr)
    out = norm_to_peak(out, 0.70)
    return f32(out)


def synth_LL(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [ɭ] — retroflex lateral approximant.

    Śikṣā: mūrdhanya + lateral.

    Two simultaneous constraints:
      1. Mūrdhanya: F3 depression >= 200 Hz below neutral alveolar (2700 Hz).
         The tongue tip is retroflexed. iir_notch() at VS_LL_F3_NOTCH
         models the acoustic zero from the retroflexed tongue position.

      2. Lateral: F2 reduced to ~1100 Hz.
         Lateral airflow around the tongue sides lowers F2 relative to
         central approximants at the same place.

    Both must be present simultaneously.
    If only the lateral: plain [l], not [ɭ].
    If only the retroflex: [ɻ̩], not [ɭ].
    The combination is the phoneme.

    Wider bandwidths (200-400 Hz) than vowels — constriction damping.
    Coarticulation: 15% weight (stronger than vowels — approximants
    are more context-sensitive, same as [v] in DEVAM).
    """
    n = int(VS_LL_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_LL_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_LL_F))):
            f_mean[k] = (F_prev[k] * VS_LL_COART_ON
                         + VS_LL_F[k] * (1.0 - VS_LL_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_LL_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_LL_COART_OFF)
                         + F_next[k] * VS_LL_COART_OFF)

    out = apply_formants(src, f_mean, VS_LL_B, VS_LL_GAINS, sr=sr)

    # Apply mūrdhanya F3 notch — the retroflex tongue curl depresses F3.
    # Same physics as [ɻ̩] — different manner (lateral vs central)
    # but same place (mūrdhanya).
    out = iir_notch(out, VS_LL_F3_NOTCH, VS_LL_F3_NOTCH_BW, sr=sr)

    out = norm_to_peak(out, 0.65)
    return f32(out)


def synth_EE(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [eː] — long close-mid front unrounded vowel.

    Śikṣā: tālavya.
    Sanskrit [e] is always long — no short counterpart.
    Mid front — between [i] and [ɑ] in both F1 and F2.

    Verified: DEVAM v1 (F1 390 Hz, F2 1757 Hz, 39/39 PASS).
    Same parameters reused here.

    Coarticulation: 10% weight from neighbors.
    """
    n = int(VS_EE_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_EE_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_EE_F))):
            f_mean[k] = (F_prev[k] * VS_EE_COART_ON
                         + VS_EE_F[k] * (1.0 - VS_EE_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_EE_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_EE_COART_OFF)
                         + F_next[k] * VS_EE_COART_OFF)

    out = apply_formants(src, f_mean, VS_EE_B, VS_EE_GAINS, sr=sr)
    out = norm_to_peak(out, 0.70)
    return f32(out)


# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_ile(pitch_hz=PITCH_HZ, dil=DIL, with_room=False, sr=SR):
    """
    ĪḶE [iːɭeː] v1 — Principles-First Reconstruction
    Rigveda 1.1.1, word 2
    "I praise."

    Syllable structure: Ī.ḶE

    [iː] → [ɭ] → [eː]

    All voiced. No pluck. No closing tail / opening head.
    Continuous Rosenberg voicing throughout.

    Coarticulation chain:
      [iː]: word-initial, F_prev=None. Coarticulates toward [ɭ] formants.
      [ɭ]:  receives context from [iː] and [eː]. F2 drops into lateral,
            F3 depressed by retroflex notch.
      [eː]: receives context from [ɭ]. Word-final, F_next=None.

    The dramatic F2 trajectory (2200 → 1100 → 1750 Hz) is the acoustic
    signature of this word: high front → retroflex lateral → mid front.
    """
    # SEG 0: [iː] long close front — word-initial
    seg_ii = synth_II(F_prev=None, F_next=VS_LL_F,
                      pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 1: [ɭ] retroflex lateral approximant
    seg_ll = synth_LL(F_prev=VS_II_F, F_next=VS_EE_F,
                      pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 2: [eː] long close-mid front — word-final
    seg_ee = synth_EE(F_prev=VS_LL_F, F_next=None,
                      pitch_hz=pitch_hz, dil=dil, sr=sr)

    # ── Concatenate and normalize ─────────────────────────────
    word = np.concatenate([seg_ii, seg_ll, seg_ee])

    # Word-level norm_to_peak(0.75) — canonical
    word = norm_to_peak(word, 0.75)

    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55, sr=sr)

    return f32(word)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("ĪḶE v1 — Principles-First Reconstruction")
    print("Rigveda 1.1.1, word 2")
    print("[iːɭeː] — \"I praise\"")
    print("=" * 70)
    print()
    print("Architecture:")
    print("  [iː] long close front (tālavya) F2≈2200 Hz, 100ms")
    print("  [ɭ]  retroflex lateral (mūrdhanya+lateral)")
    print("       F2≈1100 Hz, F3 notch at 2100 Hz, 70ms")
    print("  [eː] long close-mid front (tālavya) F2≈1750 Hz, 90ms")
    print()
    print("F2 trajectory: 2200 → 1100 → 1750 Hz")
    print("F3 trajectory: 2900 → depressed → 2650 Hz")
    print()
    print("Ancestors:")
    print("  HOTĀRAM v9 (infrastructure)")
    print("  DEVAM v1 ([eː] verified)")
    print("  AGNI ([i] formant targets verified)")
    print("  ṚG ([ɻ̩] mūrdhanya F3 depression verified)")
    print()

    # ── Standard outputs ──────────────────────────────────────
    dry = synth_ile(with_room=False)
    hall = synth_ile(with_room=True)
    write_wav("output_play/ile_v1_dry.wav", dry)
    write_wav("output_play/ile_v1_hall.wav", hall)
    write_wav("output_play/ile_v1_slow6x.wav", ola_stretch(dry, 6.0))
    write_wav("output_play/ile_v1_slow12x.wav", ola_stretch(dry, 12.0))

    # ── Performance tempo (dil=2.5) ───────────────────────────
    perf = synth_ile(dil=2.5, with_room=False)
    perf_hall = synth_ile(dil=2.5, with_room=True)
    write_wav("output_play/ile_v1_perf.wav", perf)
    write_wav("output_play/ile_v1_perf_hall.wav", perf_hall)
    write_wav("output_play/ile_v1_perf_slow6x.wav",
              ola_stretch(perf, 6.0))

    # ── Isolated phonemes ─────────────────────────────────────
    for fn, label in [
        (lambda: synth_II(F_prev=None, F_next=None), "ile_v1_ii_iso"),
        (lambda: synth_LL(F_prev=None, F_next=None), "ile_v1_ll_iso"),
        (lambda: synth_EE(F_prev=None, F_next=None), "ile_v1_ee_iso"),
    ]:
        sig = fn()
        sig = norm_to_peak(sig, 0.75)
        write_wav(f"output_play/{label}.wav", sig)
        write_wav(f"output_play/{label}_slow6x.wav",
                  ola_stretch(sig, 6.0))
        write_wav(f"output_play/{label}_slow12x.wav",
                  ola_stretch(sig, 12.0))

    print()
    print("Segment map:")
    for i, (name, dur) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        n_samp = int(dur / 1000.0 * SR)
        print(f"  SEG {i}: {name:40s} {dur:6.1f} ms  ({n_samp:5d} samples)")
    print(f"  {'TOTAL':>47s} {sum(SEG_DURATIONS_MS):6.1f} ms")
    print()
    print("Done.")
    print("  afplay output_play/ile_v1_dry.wav")
    print("  afplay output_play/ile_v1_perf_hall.wav")
    print("  afplay output_play/ile_v1_ll_iso_slow6x.wav")
    print()
    print("Run ile_diagnostic.py to verify.")
