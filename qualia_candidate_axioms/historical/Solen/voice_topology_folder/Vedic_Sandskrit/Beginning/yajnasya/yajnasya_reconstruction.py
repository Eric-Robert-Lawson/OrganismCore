#!/usr/bin/env python3
"""
YAJÑASYA RECONSTRUCTION v6
Vedic Sanskrit: yajñasya  [jɑɟɲɑsjɑ]
Rigveda 1.1.1 — word 5
"of the sacrifice" (genitive singular)

v5 → v6 CHANGES:

  1. [s] VOICELESS DENTAL SIBILANT — OBSERVER POSITION

     v5 applied unified source correctly (subglottal floor,
     closing tail, opening head). But the [s] sounded like
     listening from INSIDE the mouth — raw turbulence at full
     amplitude, sustained for 80ms.

     In natural speech, the listener hears [s] from OUTSIDE:
       - The turbulence is generated at the dental constriction
       - It radiates through the short front cavity and lips
       - The radiation attenuates and colors the noise
       - The sibilant is BRIEF in a cluster like -sya
       - It sits BELOW vowel amplitude perceptually

     The v5 [s] was the source signal. The v6 [s] is the
     radiated signal at the observer position.

     v6 CHANGES TO [s]:

       a. DURATION: 80ms → 55ms
          In a consonant cluster -sy-, the sibilant is brief.
          It is a gesture, not a sustained event.

       b. PEAK GAIN: 0.22 → 0.10
          [s] is perceptually quieter than vowels.
          The turbulence energy is high-frequency — the ear
          is less sensitive there (equal loudness contours).
          And the radiation from lips attenuates the source.

       c. FINAL NORMALIZATION: 0.42 → 0.25
          Sits well below vowel amplitude (0.72).
          The sibilant is a whisper between voiced segments.

       d. ENVELOPE: Plateau → Gaussian hill
          The tongue doesn't snap into sibilant position and hold.
          It glides through the constriction. The amplitude rises
          smoothly, peaks briefly, and decays smoothly.
          Gaussian envelope: peak at center, smooth tails.

       e. RADIATION ROLLOFF: 6dB/octave above 8000 Hz
          Models the acoustic radiation from the lip aperture.
          High frequencies radiate efficiently but the short
          front cavity doesn't amplify them as much as the
          constriction source produces. A gentle first-order
          lowpass at 8000 Hz approximates the listener position.

     The result: [s] becomes a brief, quiet dental whisper
     between voiced segments — what an observer hears, not
     what the constriction produces.

  2. ALL OTHER PHONEMES — unchanged from v5.

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# PHONEME PARAMETERS
# ============================================================================

# ── [j] voiced palatal approximant ──────────────────────────────
VS_J_F         = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B         = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS     = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS    = 55.0
VS_J_COART_ON  = 0.18
VS_J_COART_OFF = 0.18

# ── [ɟ] voiced palatal stop — v4 4-PHASE (from ṚTVIJAM v9) ────
VS_JJ_F      = [280.0, 2100.0, 2800.0, 3300.0]
VS_JJ_B      = [100.0,  200.0,  300.0,  350.0]
VS_JJ_GAINS  = [ 10.0,    6.0,    1.5,    0.5]
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_CUTBACK_MS  = 15.0

VS_JJ_VOICEBAR_F  = 250.0
VS_JJ_VOICEBAR_BW = 80.0
VS_JJ_VOICEBAR_G  = 12.0
VS_JJ_MURMUR_PEAK = 0.25

VS_JJ_BURST_F     = [500.0, 3200.0, 3800.0, 4200.0]
VS_JJ_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_JJ_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_JJ_BURST_DECAY = 180.0
VS_JJ_BURST_PEAK  = 0.15

VS_JJ_CLOSED_F    = [250.0,  800.0, 2200.0, 3200.0]
VS_JJ_CLOSED_B    = [150.0,  250.0,  300.0,  350.0]
VS_JJ_CLOSED_G    = [ 10.0,    3.0,    0.8,    0.3]
VS_JJ_CLOSED_PEAK = 0.40
VS_JJ_OPEN_PEAK   = 0.65
VS_JJ_CUTBACK_PEAK = 0.55

# ── [ɲ] voiced palatal nasal ───────────────────────────────────
VS_NY_F        = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B        = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS   = 65.0
VS_NY_ANTI_F   = 1200.0
VS_NY_ANTI_BW  = 250.0
VS_NY_COART_ON  = 0.15
VS_NY_COART_OFF = 0.15

# ── [s] voiceless dental sibilant — v6 OBSERVER POSITION ───────
VS_S_NOISE_CF  = 7500.0
VS_S_NOISE_BW  = 3000.0
VS_S_DUR_MS    = 55.0            # v6: 80→55ms (brief gesture)
VS_S_PEAK_GAIN = 0.10            # v6: 0.22→0.10 (observer, not source)
VS_S_FINAL_NORM = 0.25           # v6: 0.42→0.25 (sits below vowels)
VS_S_SUBGLOTTAL_FLOOR = 0.001
VS_S_RADIATION_CUTOFF = 8000.0   # v6: 1st-order LPF for radiation

# Pluck parameters for sibilant boundaries
VS_S_CLOSING_MS = 25.0
VS_S_OPENING_MS = 15.0

# ── [ɑ] short open central — VERIFIED AGNI ─────────────────────
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

PITCH_HZ = 120.0
DIL      = 1.0

# ============================================================================
# SYNTHESIS HELPERS
# ============================================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = np.clip(sig * 32767.0, -32768, 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())
    print(f"Wrote {path}")

def rosenberg_pulse(n_samples, pitch_hz, oq=0.65, sr=SR):
    """Rosenberg glottal pulse model."""
    period = int(sr / pitch_hz)
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
    """Formant filter bank (IIR resonators) — b=[g] convention."""
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f0, bw, g in zip(freqs, bws, gains):
        if f0 <= 0 or f0 >= nyq:
            continue
        r = np.exp(-np.pi * bw / sr)
        cosf = 2.0 * np.cos(2.0 * np.pi * f0 / sr)
        a = [1.0, -r * cosf, r * r]
        b = [g]
        filt = lfilter(b, a, src.astype(float))
        out += filt
    return f32(out)

def iir_notch(sig, fc, bw=200.0, sr=SR):
    """Nasal antiresonance notch."""
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))

def norm_to_peak(sig, target_peak):
    mx = np.max(np.abs(sig))
    if mx > 1e-10:
        return f32(sig * (target_peak / mx))
    return f32(sig)

def ola_stretch(sig, factor=6.0, sr=SR):
    """Time-stretch via overlap-add."""
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
    norm = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos + win_n] * window
        out[out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    nz = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def apply_simple_room(sig, rt60=1.5, direct_ratio=0.55, sr=SR):
    """Temple courtyard reverb."""
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
# PLUCK HELPERS — CLOSING TAIL / OPENING HEAD
# ============================================================================

def make_closing_tail(voiced_seg, tail_ms, pitch_hz=PITCH_HZ, sr=SR):
    """
    The vowel OWNS the closure.

    Append a closing tail: extend the voiced signal with a
    smooth amplitude fade. The articulator moves toward the
    constriction position. The signal decays within the vowel's
    own resonance — no concatenation boundary to silence.
    """
    n_tail = int(tail_ms / 1000.0 * sr)
    if n_tail < 2:
        return voiced_seg

    period = int(sr / pitch_hz)
    if len(voiced_seg) >= period:
        template = voiced_seg[-period:]
        n_reps = (n_tail // period) + 2
        tail_src = np.tile(template, n_reps)[:n_tail]
    else:
        tail_src = np.zeros(n_tail, dtype=DTYPE)

    fade = np.linspace(1.0, 0.0, n_tail) ** 2
    tail = f32(tail_src * fade)

    return f32(np.concatenate([voiced_seg, tail]))


def make_opening_head(voiced_seg, head_ms, pitch_hz=PITCH_HZ, sr=SR):
    """
    The next segment OWNS the onset.

    Prepend an opening head: the first head_ms of voiced signal
    rises from near-zero as voicing resumes after a voiceless
    segment.
    """
    n_head = int(head_ms / 1000.0 * sr)
    if n_head < 2:
        return voiced_seg

    period = int(sr / pitch_hz)
    if len(voiced_seg) >= period:
        template = voiced_seg[:period]
        n_reps = (n_head // period) + 2
        head_src = np.tile(template, n_reps)[:n_head]
    else:
        head_src = np.zeros(n_head, dtype=DTYPE)

    rise = np.linspace(0.0, 1.0, n_head) ** 2
    head = f32(head_src * rise)

    return f32(np.concatenate([head, voiced_seg]))


# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_J(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_voiceless=False):
    """
    [j] voiced palatal approximant.

    opening_from_voiceless=True: prepend opening head (15ms).
    """
    n = int(VS_J_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_J_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_J_F))):
            f_mean[k] = (F_prev[k] * VS_J_COART_ON +
                         VS_J_F[k] * (1.0 - VS_J_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_J_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_J_COART_OFF) +
                         F_next[k] * VS_J_COART_OFF)

    out = apply_formants(src, f_mean, VS_J_B, VS_J_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65

    if opening_from_voiceless:
        out = make_opening_head(f32(out), VS_S_OPENING_MS,
                                pitch_hz=pitch_hz)

    return f32(out)


def synth_JJ(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [ɟ] voiced palatal stop — v4 4-PHASE
    (from ṚTVIJAM v9 verified implementation)

    Phase 1: Voice bar closure (250 Hz, BW 80)
    Phase 2: Spike + turbulence burst at palatal locus
    Phase 3: Crossfade cutback (closed → open)
    """
    n_cl = int(VS_JJ_CLOSURE_MS * dil / 1000.0 * SR)
    n_b  = int(VS_JJ_BURST_MS * dil / 1000.0 * SR)
    n_cb = int(VS_JJ_CUTBACK_MS * dil / 1000.0 * SR)

    f_next = F_next if F_next is not None else VS_A_F

    # Phase 1: Voice bar closure
    if n_cl > 0:
        src_cl = rosenberg_pulse(n_cl, pitch_hz, oq=0.65)
        murmur_cl = apply_formants(
            src_cl,
            [VS_JJ_VOICEBAR_F],
            [VS_JJ_VOICEBAR_BW],
            [VS_JJ_VOICEBAR_G])
        env_cl = np.ones(n_cl, dtype=float)
        ramp_n = max(1, int(0.3 * n_cl))
        env_cl[:ramp_n] = np.linspace(0.3, 1.0, ramp_n)
        murmur_cl = f32(murmur_cl * env_cl)
        closure = norm_to_peak(murmur_cl, VS_JJ_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: Spike + turbulence burst (palatal locus)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]

    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_JJ_BURST_F, VS_JJ_BURST_B, VS_JJ_BURST_G)

    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_JJ_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_JJ_BURST_PEAK)

    # Phase 3: Crossfade cutback (closed → open)
    if n_cb > 0:
        src_cb = rosenberg_pulse(n_cb, pitch_hz)
        sig_closed = apply_formants(
            src_cb, VS_JJ_CLOSED_F, VS_JJ_CLOSED_B, VS_JJ_CLOSED_G)
        sig_closed = norm_to_peak(sig_closed, VS_JJ_CLOSED_PEAK)

        sig_open = apply_formants(
            src_cb, list(f_next),
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5])
        sig_open = norm_to_peak(sig_open, VS_JJ_OPEN_PEAK)

        t_fade = np.linspace(0.0, np.pi / 2.0, n_cb)
        fade_out = np.cos(t_fade).astype(DTYPE)
        fade_in  = np.sin(t_fade).astype(DTYPE)
        cutback = f32(sig_closed * fade_out + sig_open * fade_in)
        cb_env = np.linspace(0.6, 1.0, n_cb).astype(DTYPE)
        cutback = f32(cutback * cb_env)
        cutback = norm_to_peak(cutback, VS_JJ_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, cutback])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)


def synth_NY(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɲ] voiced palatal nasal."""
    n = int(VS_NY_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_NY_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_NY_F))):
            f_mean[k] = (F_prev[k] * VS_NY_COART_ON +
                         VS_NY_F[k] * (1.0 - VS_NY_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_NY_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_NY_COART_OFF) +
                         F_next[k] * VS_NY_COART_OFF)

    out = apply_formants(src, f_mean, VS_NY_B, VS_NY_GAINS)
    out = iir_notch(out, VS_NY_ANTI_F, VS_NY_ANTI_BW)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)


def synth_S(dil=DIL):
    """
    [s] voiceless dental sibilant — v6 OBSERVER POSITION

    Śikṣā: dantya aghoṣa ūṣman (sibilant/fricative)

    The turbulence is generated at the dental constriction.
    But the LISTENER hears what RADIATES from the lips —
    not the raw source at the constriction.

    v6 models the observer position:

      1. ONE continuous noise buffer (the breath through
         the dental constriction).

      2. Bandpass at dental sibilant locus (7500 ± 1500 Hz)
         — the constriction selects the frequency band.

      3. Radiation rolloff (1st-order LPF at 8000 Hz)
         — models the acoustic radiation from the lip aperture.
         The listener hears less extreme HF than the source
         produces.

      4. Gaussian amplitude envelope — the tongue GLIDES
         through the constriction. It doesn't snap into position.
         Peak at center, smooth rise and fall. The sibilant
         is a brief gesture, not a sustained event.

      5. Subglottal floor at edges (0.001) — never digital zero.
         The breath exists before and after the constriction.

      6. Low final amplitude (0.25) — [s] sits well below
         vowel amplitude (0.72). In natural speech, sibilants
         are quieter than vowels. The high-frequency energy
         is perceptually weighted lower by the ear.

    The result: a brief dental whisper between voiced segments.
    What the observer hears from across the courtyard.
    Not what the tongue feels at the constriction.
    """
    n = int(VS_S_DUR_MS * dil / 1000.0 * SR)

    # ── UNIFIED NOISE SOURCE ──────────────────────────────
    noise_source = np.random.randn(n).astype(float)

    # ── BANDPASS AT DENTAL SIBILANT LOCUS ─────────────────
    lo = max(VS_S_NOISE_CF - VS_S_NOISE_BW / 2, 20.0)
    hi = min(VS_S_NOISE_CF + VS_S_NOISE_BW / 2, SR / 2.0 - 20.0)

    if lo < hi:
        b_bp, a_bp = butter(2,
                            [lo / (SR / 2.0), hi / (SR / 2.0)],
                            btype='band')
        noise_shaped = lfilter(b_bp, a_bp, noise_source)
    else:
        noise_shaped = noise_source

    # ── RADIATION ROLLOFF ─────────────────────────────────
    # 1st-order lowpass at 8000 Hz.
    # Models the acoustic radiation from the lip aperture.
    # The listener hears less extreme HF than the constriction
    # source produces. This is what makes it sound like you're
    # listening from outside the mouth, not inside.
    fc_rad = VS_S_RADIATION_CUTOFF
    if fc_rad < SR / 2.0:
        b_rad, a_rad = butter(1, fc_rad / (SR / 2.0), btype='low')
        noise_shaped = lfilter(b_rad, a_rad, noise_shaped)

    # ── GAUSSIAN AMPLITUDE ENVELOPE ───────────────────────
    # The tongue glides through the dental constriction.
    # It doesn't snap into position and hold.
    # Gaussian: peak at center, smooth rise and fall.
    # sigma chosen so the edges are at ~5% of peak.
    t = np.linspace(-3.0, 3.0, n)
    gaussian = np.exp(-0.5 * t * t)

    # Scale: peak at VS_S_PEAK_GAIN, floor at subglottal
    env = VS_S_SUBGLOTTAL_FLOOR + \
        (VS_S_PEAK_GAIN - VS_S_SUBGLOTTAL_FLOOR) * gaussian

    # ── APPLY ENVELOPE ────────────────────────────────────
    out = f32(noise_shaped[:n] * env[:n])

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * VS_S_FINAL_NORM
    return f32(out)


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            closing_for_voiceless=False):
    """
    [ɑ] short open central unrounded (VERIFIED AGNI).

    closing_for_voiceless=True: append closing tail (25ms).
    """
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = (F_prev[k] * VS_A_COART_ON +
                         VS_A_F[k] * (1.0 - VS_A_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_A_COART_OFF) +
                         F_next[k] * VS_A_COART_OFF)

    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72

    if closing_for_voiceless:
        out = make_closing_tail(f32(out), VS_S_CLOSING_MS,
                                pitch_hz=pitch_hz)

    return f32(out)


# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_yajnasya(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    YAJÑASYA [jɑɟɲɑsjɑ] — v6
    Rigveda 1.1.1, word 5
    Syllables: YAJ.ÑA.SYA

    v6 OBSERVER POSITION for [s]:

      The sibilant is a brief dental whisper between
      voiced segments — what the observer hears from
      across the courtyard, not what the constriction
      produces inside the mouth.

      Gaussian envelope (glide, not snap).
      Radiation rolloff (lips, not source).
      Low amplitude (whisper, not shout).
      55ms duration (gesture, not event).

    Segment map:
      [j]₁                         55ms
      [ɑ]₁                         55ms
      [ɟ]                           54ms   (voice bar + burst + cutback)
      [ɲ]                           65ms
      [ɑ]₂ + closing tail          80ms   (55ms + 25ms fade)
      [s] UNIFIED (observer)        55ms   (Gaussian, radiated)
      head + [j]₂                  70ms   (15ms rise + 55ms)
      [ɑ]₃                         55ms
    """
    segs = [
        # YA-
        synth_J(F_prev=None, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_J_F, F_next=VS_JJ_F,
                pitch_hz=pitch_hz, dil=dil),

        # -JÑA-
        synth_JJ(F_prev=VS_A_F, F_next=VS_NY_F,
                 pitch_hz=pitch_hz, dil=dil),
        synth_NY(F_prev=VS_JJ_F, F_next=VS_A_F,
                 pitch_hz=pitch_hz, dil=dil),

        # [ɑ]₂ with closing tail (vowel owns closure before [s])
        synth_A(F_prev=VS_NY_F, F_next=None,
                pitch_hz=pitch_hz, dil=dil,
                closing_for_voiceless=True),

        # [s] UNIFIED SOURCE (observer position)
        synth_S(dil=dil),

        # [j]₂ with opening head (approximant owns onset after [s])
        synth_J(F_prev=None, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil,
                opening_from_voiceless=True),

        # [ɑ]₃
        synth_A(F_prev=VS_J_F, F_next=None,
                pitch_hz=pitch_hz, dil=dil),
    ]

    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55)

    return f32(word)


# Expose for diagnostic reference
VS_JJ_BURST_F_VAL = VS_JJ_BURST_F[1]
VS_S_NOISE_CF_VAL = VS_S_NOISE_CF

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("YAJÑASYA v6 — OBSERVER POSITION")
    print("=" * 70)
    print()
    print("v5→v6: [s] WAS INSIDE THE MOUTH. NOW IT'S AT THE LISTENER.")
    print()
    print("  v5 problem:")
    print("    [s] sounded like listening from inside the mouth.")
    print("    Raw turbulence at full amplitude, sustained 80ms.")
    print("    Deliberate aspiration. Too loud. Too long.")
    print()
    print("  v6 solution: OBSERVER POSITION")
    print()
    print("    Duration:  80ms → 55ms  (brief gesture, not event)")
    print("    Peak gain: 0.22 → 0.10  (radiated, not source)")
    print("    Final amp: 0.42 → 0.25  (whisper, not shout)")
    print("    Envelope:  plateau → Gaussian (glide, not snap)")
    print("    Radiation: 1st-order LPF at 8000 Hz")
    print("               (what leaves the lips, not what the")
    print("                constriction produces)")
    print()
    print("  The sibilant is a brief dental whisper.")
    print("  What the observer hears from across the courtyard.")
    print()

    # Diagnostic speed
    word_dry = synth_yajnasya(PITCH_HZ, 1.0)
    word_slow = ola_stretch(word_dry, 6.0)
    word_slow12 = ola_stretch(word_dry, 12.0)

    # Performance speed
    word_perf = synth_yajnasya(PITCH_HZ, 2.5)
    word_perf_hall = synth_yajnasya(PITCH_HZ, 2.5, with_room=True)

    # Hall
    word_hall = synth_yajnasya(PITCH_HZ, 1.0, with_room=True)

    write_wav("output_play/yajnasya_v6_dry.wav", word_dry)
    write_wav("output_play/yajnasya_v6_slow6x.wav", word_slow)
    write_wav("output_play/yajnasya_v6_slow12x.wav", word_slow12)
    write_wav("output_play/yajnasya_v6_hall.wav", word_hall)
    write_wav("output_play/yajnasya_v6_perf.wav", word_perf)
    write_wav("output_play/yajnasya_v6_perf_hall.wav", word_perf_hall)

    # Isolated [ɟ]
    jj_iso = synth_JJ(F_prev=VS_A_F, F_next=VS_NY_F,
                       pitch_hz=PITCH_HZ, dil=DIL)
    mx = np.max(np.abs(jj_iso))
    if mx > 1e-8:
        jj_iso = jj_iso / mx * 0.75
    jj_iso = f32(jj_iso)

    write_wav("output_play/yajnasya_v6_jj_iso.wav", jj_iso)
    write_wav("output_play/yajnasya_v6_jj_iso_slow6x.wav",
              ola_stretch(jj_iso, 6.0))
    write_wav("output_play/yajnasya_v6_jj_iso_slow12x.wav",
              ola_stretch(jj_iso, 12.0))

    # Isolated [s] unified (observer)
    s_iso = synth_S(dil=DIL)
    mx = np.max(np.abs(s_iso))
    if mx > 1e-8:
        s_iso = s_iso / mx * 0.75
    s_iso = f32(s_iso)

    write_wav("output_play/yajnasya_v6_s_observer.wav", s_iso)
    write_wav("output_play/yajnasya_v6_s_observer_slow6x.wav",
              ola_stretch(s_iso, 6.0))

    # aSya syllable (boundary test)
    a_closing = synth_A(F_prev=VS_NY_F, F_next=None,
                        closing_for_voiceless=True)
    s_seg = synth_S()
    j_opening = synth_J(F_prev=None, F_next=VS_A_F,
                        opening_from_voiceless=True)
    asya_syl = np.concatenate([a_closing, s_seg, j_opening])
    mx = np.max(np.abs(asya_syl))
    if mx > 1e-8:
        asya_syl = asya_syl / mx * 0.75
    asya_syl = f32(asya_syl)

    write_wav("output_play/yajnasya_v6_aSya_syllable.wav", asya_syl)
    write_wav("output_play/yajnasya_v6_aSya_syllable_slow6x.wav",
              ola_stretch(asya_syl, 6.0))
    write_wav("output_play/yajnasya_v6_aSya_syllable_slow12x.wav",
              ola_stretch(asya_syl, 12.0))

    print()
    print("=" * 70)
    print("v6 synthesis complete.")
    print()
    print("LISTEN:")
    print("  afplay output_play/yajnasya_v6_aSya_syllable_slow6x.wav")
    print("  afplay output_play/yajnasya_v6_s_observer_slow6x.wav")
    print("  afplay output_play/yajnasya_v6_slow6x.wav")
    print("  afplay output_play/yajnasya_v6_perf_hall.wav")
    print()
    print("LISTEN FOR:")
    print("  [s] — Should be a brief, quiet dental whisper.")
    print("        Not a sustained hiss. Not loud.")
    print("        A moment between voiced segments.")
    print("        Like hearing it from across the room,")
    print("        not from inside the mouth.")
    print()
    print("  Compare v6 to v5:")
    print("    v5: [s] = 80ms, gain 0.22, norm 0.42, plateau")
    print("         → inside the mouth, deliberate aspiration")
    print("    v6: [s] = 55ms, gain 0.10, norm 0.25, Gaussian")
    print("         → across the courtyard, brief whisper")
    print()
    print("  If [s] is still too loud: reduce VS_S_PEAK_GAIN (0.10)")
    print("  If [s] is inaudible: increase VS_S_FINAL_NORM (0.25)")
    print("  If [s] is too bright: lower VS_S_RADIATION_CUTOFF (8000)")
    print("=" * 70)
    print()
