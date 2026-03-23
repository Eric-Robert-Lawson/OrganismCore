"""
TINNITUS EIGENFUNCTION CALIBRATION SYSTEM
OC-TINNITUS-001 — OrganismCore
Eric Robert Lawson — 2026-03-23

PROTOCOL:
  Phase 1 — Rainbow sweep (eigenfunction sampler)
             One ear at a time.
             Each tone = one structural position
             on the basilar membrane.
             Feedback: B (better) / W (worse) / N (no difference)

  Phase 2 — Gradient descent from landscape
             Follow directionality from sweep.
             Fine-tune toward cancellation optimum.
             Feedback: B / W / N continuously.

  Phase 3 — Phase calibration
             At locked FA, sweep phase 0-360.
             Find actual cancellation phase for
             this individual's cochlear geometry.

  Phase 4 — FR sweep (residual resonant frequency)
             Find frequency adjacent to FA where
             damaged structure still responds to
             external signal.

  Phase 5 — Orthogonal re-sweep
             Second rainbow sweep to check for
             remaining gradient in other dimensions.
             If improvement found: more work to do.
             If no improvement anywhere: converged.

  Phase 6 — WAV file generation
             Personalized sleep remedy from all
             calibrated parameters.
             Per-ear. Independent L/R channels.

SELF-ADMINISTRABLE:
  No second person required.
  You are the measurement instrument.
  Run on yourself.

INSTALL:
  pip install sounddevice numpy scipy

USAGE:
  python tinnitus_calibration.py
"""

import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
import time
import datetime
import json
import os

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SAMPLE_RATE    = 44100
LOG_FILE       = "tinnitus_calibration_log.json"
OUTPUT_WAV_L   = "remedy_left.wav"
OUTPUT_WAV_R   = "remedy_right.wav"
OUTPUT_WAV_B   = "remedy_binaural.wav"

# Tone duration for rainbow sweep (seconds)
SWEEP_TONE_DURATION = 10

# Tone duration for gradient descent steps
GRADIENT_TONE_DURATION = 6

# Starting amplitude — adjust if tones inaudible
# 0.0 to 1.0. Start low. Increase if needed.
AMPLITUDE = 0.10

# Fade in/out duration (ms) — prevents clicks
FADE_MS = 80

# ═══════════════════════════════════════════════════════════
# GREENWOOD FUNCTION — COCHLEAR EIGENFUNCTION POSITIONS
# ═══════════════════════════════════════════════════════════

def greenwood_freq(x_norm, A=165.4, a=2.1, k=0.88):
    """
    Frequency at normalised cochlear position x_norm.
    x_norm: 0.0 = apex (low freq), 1.0 = base (high freq)
    Human parameters: A=165.4, a=2.1, k=0.88
    """
    return A * (10 ** (a * x_norm) - k)

def greenwood_pos(freq, A=165.4, a=2.1, k=0.88):
    """Normalised cochlear position for a given frequency."""
    return np.log10((freq / A) + k) / a

def eigenfunction_rainbow(n_tones=12,
                           pos_lo=0.30,
                           pos_hi=0.95):
    """
    Generate n_tones frequencies equally spaced in
    cochlear position (geometric invariance on
    basilar membrane).

    pos_lo=0.30 → ~500 Hz  (avoid very low — not tinnitus)
    pos_hi=0.95 → ~14 kHz  (avoid extreme base)

    Returns list of (cochlear_pos, frequency_hz) tuples.
    """
    positions = np.linspace(pos_lo, pos_hi, n_tones)
    return [(float(p), float(greenwood_freq(p)))
            for p in positions]

# Pre-compute the standard rainbow
RAINBOW = eigenfunction_rainbow(n_tones=12)

# ═══════════════════════════════════════════════════════════
# SIGNAL GENERATION
# ═══════════════════════════════════════════════════════════

def make_tone(freq_hz, duration_s,
              amplitude=AMPLITUDE,
              phase_deg=0.0,
              harmonic_2=0.0,
              harmonic_3=0.0,
              sr=SAMPLE_RATE):
    """
    Generate a sine tone with optional harmonics
    and smooth fade in/out.

    freq_hz:    fundamental frequency
    duration_s: duration in seconds
    amplitude:  peak amplitude (0–1)
    phase_deg:  phase offset in degrees
    harmonic_2: H2 amplitude relative to H1 (0–1)
    harmonic_3: H3 amplitude relative to H1 (0–1)
    """
    n      = int(sr * duration_s)
    t      = np.linspace(0, duration_s, n, endpoint=False)
    ph     = np.deg2rad(phase_deg)

    sig = np.sin(2 * np.pi * freq_hz * t + ph)
    if harmonic_2 > 0:
        sig += harmonic_2 * np.sin(
            2 * np.pi * 2 * freq_hz * t + ph)
    if harmonic_3 > 0:
        sig += harmonic_3 * np.sin(
            2 * np.pi * 3 * freq_hz * t + ph)

    sig *= amplitude

    # Fade
    fade_n = int(FADE_MS * sr / 1000)
    fade_n = min(fade_n, n // 4)
    fade_in  = np.linspace(0, 1, fade_n)
    fade_out = np.linspace(1, 0, fade_n)
    sig[:fade_n]  *= fade_in
    sig[-fade_n:] *= fade_out

    return sig.astype(np.float32)

def make_pink_noise(duration_s, amplitude=0.03,
                    sr=SAMPLE_RATE):
    """
    Approximate pink noise (1/f) by summing
    octave-spaced sine waves with 1/f amplitudes.
    Used as environmental reference floor in WAV.
    """
    n      = int(sr * duration_s)
    t      = np.linspace(0, duration_s, n, endpoint=False)
    octave_freqs = [125, 250, 500, 1000,
                    2000, 4000, 8000]
    sig = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(octave_freqs):
        a   = amplitude / (i + 1) ** 0.5
        ph  = np.random.uniform(0, 2 * np.pi)
        sig += (a * np.sin(2 * np.pi * f * t + ph)
                ).astype(np.float32)
    return sig

def stereo_left(mono):
    """Pack mono signal into left channel only."""
    z = np.zeros_like(mono)
    return np.stack([mono, z], axis=1)

def stereo_right(mono):
    """Pack mono signal into right channel only."""
    z = np.zeros_like(mono)
    return np.stack([z, mono], axis=1)

def play_left(sig):
    sd.play(stereo_left(sig), SAMPLE_RATE)
    sd.wait()

def play_right(sig):
    sd.play(stereo_right(sig), SAMPLE_RATE)
    sd.wait()

def play_both(sig_l, sig_r):
    """Play different signals to each ear simultaneously."""
    n   = max(len(sig_l), len(sig_r))
    l   = np.zeros(n, dtype=np.float32)
    r   = np.zeros(n, dtype=np.float32)
    l[:len(sig_l)] = sig_l
    r[:len(sig_r)] = sig_r
    stereo = np.stack([l, r], axis=1)
    sd.play(stereo, SAMPLE_RATE)
    sd.wait()

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

class Session:
    """Holds all calibration data for one session."""

    def __init__(self):
        self.timestamp  = datetime.datetime.now(
            ).isoformat()
        self.left  = self._ear()
        self.right = self._ear()
        self.notes = []

    def _ear(self):
        return {
            "rainbow":       {},   # freq → response
            "fa_hz":         None,
            "fr_hz":         None,
            "phase_deg":     180.0,
            "amplitude":     AMPLITUDE,
            "ri_duration_s": None,
            "suppression":   None,
            "converged":     False,
            "orthogonal_clear": False,
        }

    def ear(self, side):
        return self.left if side == "L" else self.right

    def save(self):
        with open(LOG_FILE, "w") as f:
            json.dump(self.__dict__, f, indent=2)
        print(f"\n  [Saved → {LOG_FILE}]")

    @classmethod
    def load(cls):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                data = json.load(f)
            s = cls()
            s.__dict__.update(data)
            return s
        return None


def ask(prompt, valid=None):
    """
    Ask for input, optionally validate against
    a set of valid responses (case-insensitive).
    """
    while True:
        raw = input(f"  {prompt} ").strip().upper()
        if valid is None or raw in valid:
            return raw
        print(f"  → Please enter one of: "
              f"{', '.join(valid)}")

# ═══════════════════════════════════════════════════════════
# PHASE 1 — RAINBOW SWEEP
# ═══════════════════════════════════════════════════════════

def rainbow_sweep(session, side):
    """
    Play each eigenfunction position tone for
    SWEEP_TONE_DURATION seconds, one ear only.
    Collect B / W / N feedback for each.

    Returns dict: freq_hz → response
    """
    ear  = session.ear(side)
    play = play_left if side == "L" else play_right

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  RAINBOW SWEEP — {side} EAR                         │
  │                                             │
  │  You will hear {len(RAINBOW)} tones in sequence.       │
  │  Each tone plays for {SWEEP_TONE_DURATION} seconds.           │
  │                                             │
  │  After EACH tone, press:                    │
  │    B  — tinnitus BETTER (reduced)           │
  │    W  — tinnitus WORSE  (louder/stronger)   │
  │    N  — NO DIFFERENCE                       │
  │                                             │
  │  If you cannot hear the tone at all: say N  │
  │  and we will adjust volume afterward.       │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER when ready ...")

    responses = {}
    for i, (pos, freq) in enumerate(RAINBOW):
        hz_label = f"{freq:.0f} Hz"
        mm_label = f"{pos * 35:.1f} mm"
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  "
              f"{hz_label:>9}  "
              f"(cochlear pos {mm_label})")
        input(f"  Press ENTER to play ...")
        tone = make_tone(freq, SWEEP_TONE_DURATION)
        play(tone)
        r = ask("B / W / N:", valid={"B", "W", "N"})
        responses[freq] = r
        print(f"  → Logged: {r}")

    ear["rainbow"] = {str(k): v
                      for k, v in responses.items()}
    session.save()
    return responses


def interpret_rainbow(responses):
    """
    Analyse rainbow sweep results.
    Returns:
      best_freq: frequency with most B responses
                 or closest to B cluster
      landscape: summary dict
    """
    better = [f for f, r in responses.items() if r == "B"]
    worse  = [f for f, r in responses.items() if r == "W"]
    same   = [f for f, r in responses.items() if r == "N"]

    print(f"""
  ── RAINBOW LANDSCAPE ──────────────────────────
  Better responses : {len(better)} tones
    {[f"{f:.0f}" for f in sorted(better)]}
  Worse responses  : {len(worse)} tones
    {[f"{f:.0f}" for f in sorted(worse)]}
  No difference    : {len(same)} tones
  ───────────────────────────────────────────────
    """)

    if not better:
        print("  No 'Better' responses detected.")
        print("  Possible causes:")
        print("    1. Volume too low — increase AMPLITUDE")
        print("       in config and re-run sweep.")
        print("    2. Tinnitus is noise-like / broadband")
        print("       — cancellation approach may have")
        print("       lower confidence for this case.")
        print("    3. No tinnitus in this ear — confirm.")
        return None, {}

    # Best starting frequency: highest-freq Better
    # response (tinnitus most commonly 4–10 kHz)
    # If multiple Better responses, pick the one
    # adjacent to the worst cluster (steepest gradient)
    if len(better) == 1:
        best = better[0]
    else:
        # Pick Better freq closest to boundary with
        # Worse responses (steepest gradient = most
        # information about eigenfunction position)
        best = sorted(better)[-1]  # default: highest
        if worse:
            worst_min = min(worse)
            # Better freq just below the Worse cluster
            candidates = [f for f in better if f < worst_min]
            if candidates:
                best = max(candidates)

    print(f"  Starting gradient descent at: {best:.0f} Hz")
    return best, {"better": better,
                  "worse": worse,
                  "same": same}

# ═══════════════════════════════════════════════════════════
# PHASE 2 — GRADIENT DESCENT
# ═══════════════════════════════════════════════════════════

def gradient_descent(session, side, start_freq):
    """
    Patient-guided gradient descent in cochlear
    eigenfunction space.

    Starts at start_freq.
    Steps up or down based on B/W/N feedback.
    Step size halves on direction change.
    Converges when step < 5 Hz and 3 consecutive B.

    Returns: fa_hz (false attractor frequency)
    """
    ear  = session.ear(side)
    play = play_left if side == "L" else play_right

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  GRADIENT DESCENT — {side} EAR                      │
  │                                             │
  │  Starting at {start_freq:.0f} Hz                     │
  │                                             │
  │  Each tone plays for {GRADIENT_TONE_DURATION} seconds.          │
  │  Give feedback after EACH tone:             │
  │    B — better    W — worse    N — same      │
  │    L — LOCK (this is the best position)     │
  │                                             │
  │  Follow your perception. Trust it.          │
  │  You are navigating toward the cancellation │
  │  optimum for your specific cochlea.         │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    freq      = float(start_freq)
    step      = 300.0
    direction = 0      # 0=unset, +1=up, -1=down
    history   = []
    fa        = freq

    for iteration in range(80):
        f_int = max(200, min(16000, int(round(freq))))
        pos   = greenwood_pos(f_int)
        mm    = pos * 35

        print(f"\n  Step {iteration+1:2d}: "
              f"{f_int} Hz  "
              f"(cochlear {mm:.1f} mm)  "
              f"step={step:.0f} Hz")
        input("  ENTER to play ...")
        tone = make_tone(f_int, GRADIENT_TONE_DURATION)
        play(tone)

        r = ask("B / W / N / L:", valid={"B","W","N","L"})
        history.append((f_int, r))
        print(f"  → {r}")

        if r == "L":
            fa = f_int
            print(f"\n  Locked at {fa} Hz")
            break

        elif r == "B":
            fa = f_int
            if direction == 0:
                direction = 1
            step = max(step * 0.65, 5.0)
            freq += direction * step

        elif r == "W":
            if direction == 0:
                direction = -1
            else:
                direction *= -1
            step = max(step * 0.65, 5.0)
            freq += direction * step

        elif r == "N":
            # No interaction — try larger step
            step = min(step * 1.4, 500.0)
            direction = 1 if direction <= 0 else -1
            freq += direction * step

        # Convergence: 3 consecutive B, step < 8 Hz
        if (len(history) >= 3 and
                all(h[1] == "B" for h in history[-3:]) and
                step <= 8.0):
            fa = f_int
            print(f"\n  Converged at {fa} Hz")
            break

    ear["fa_hz"] = fa
    session.save()
    return fa

# ═══════════════════════════════════════════════════════════
# PHASE 3 — PHASE CALIBRATION
# ═══════════════════════════════════════════════════════════

def phase_calibration(session, side, fa):
    """
    Sweep phase from 0° to 360° in 45° steps,
    then fine-tune ±20° around best phase.

    The cochlear travelling wave produces individual
    phase relationships at each eigenfunction position.
    180° is an assumption. This finds the real value.

    Returns: best_phase_deg
    """
    ear  = session.ear(side)
    play = play_left if side == "L" else play_right

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE CALIBRATION — {side} EAR                     │
  │  Frequency locked at: {fa} Hz             │
  │                                             │
  │  Finding your cochlea's cancellation phase. │
  │  180° is the standard assumption.           │
  │  Your cochlea may differ.                   │
  │                                             │
  │  Feedback: B / W / N as before.             │
  │  The phase producing the most relief        │
  │  is your cancellation phase.                │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    score_map   = {"B": 2, "S": 1, "W": 0, "N": 1}
    coarse_phases = [0, 45, 90, 135, 180, 225, 270, 315]
    best_phase  = 180
    best_score  = -1

    print("\n  ── Coarse phase sweep ──")
    for ph in coarse_phases:
        print(f"\n  Phase {ph}°")
        input("  ENTER to play ...")
        tone = make_tone(fa, 5, phase_deg=ph)
        play(tone)
        r = ask("B / W / N:", valid={"B","W","N"})
        s = score_map.get(r, 0)
        print(f"  → {r}")
        if s > best_score:
            best_score = s
            best_phase = ph

    print(f"\n  Best coarse phase: {best_phase}°")
    print("  Fine-tuning ±40° ...")

    fine_phases = range(best_phase - 40,
                        best_phase + 41, 10)
    for ph in fine_phases:
        ph_n = ph % 360
        print(f"\n  Phase {ph_n}°")
        input("  ENTER to play ...")
        tone = make_tone(fa, 5, phase_deg=ph_n)
        play(tone)
        r = ask("B / W / N:", valid={"B","W","N"})
        s = score_map.get(r, 0)
        print(f"  → {r}")
        if s > best_score:
            best_score = s
            best_phase = ph_n

    print(f"\n  Phase locked at: {best_phase}°")
    ear["phase_deg"] = best_phase
    session.save()
    return best_phase

# ═══════════════════════════════════════════════════════════
# PHASE 4 — FR SWEEP (RESIDUAL RESONANT FREQUENCY)
# ═══════════════════════════════════════════════════════════

def fr_sweep(session, side, fa, phase):
    """
    Find the residual resonant frequency (FR):
    the frequency adjacent to FA where the damaged
    cochlear zone still responds to external signal.

    Plays anti-signal at FA + boost tone at test freq.
    Patient reports whether combined signal is better
    than anti-signal at FA alone.

    FR is the basis of the cracked violin layer:
    something real for the navigator to track after
    the false attractor is displaced.

    Returns: fr_hz
    """
    ear  = session.ear(side)
    play = play_left if side == "L" else play_right
    amp  = ear["amplitude"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  FR SWEEP — {side} EAR                              │
  │  FA locked at: {fa} Hz                   │
  │                                             │
  │  Testing frequencies above and below FA.    │
  │  Each test = anti-signal at FA              │
  │            + boost tone at test frequency.  │
  │                                             │
  │  You are finding where your damaged zone    │
  │  still responds to real input.              │
  │  This is the cracked violin principle.      │
  │                                             │
  │  Feedback: B / W / N                        │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    offsets    = [-400, -300, -200, -150,
                  -100, -50, 0,
                  50, 100, 150, 200, 300, 400]
    score_map  = {"B": 2, "N": 1, "W": 0}
    best_fr    = fa
    best_score = 0

    for offset in offsets:
        f_test = fa + offset
        if f_test < 300 or f_test > 16000:
            continue
        label = f"FA{'+' if offset >= 0 else ''}{offset}"
        print(f"\n  {label} = {f_test} Hz")
        input("  ENTER to play ...")

        anti  = make_tone(fa, 6,
                          amplitude=amp,
                          phase_deg=phase)
        boost = make_tone(f_test, 6,
                          amplitude=amp * 0.45,
                          phase_deg=0)
        combined = np.clip(anti + boost, -1.0, 1.0)
        play(combined)

        r = ask("B / W / N:", valid={"B","W","N"})
        s = score_map.get(r, 0)
        print(f"  → {r}")
        if s > best_score:
            best_score = s
            best_fr    = f_test

    print(f"\n  FR identified: {best_fr} Hz")
    print(f"  FA→FR gap: {best_fr - fa:+d} Hz")

    if best_fr < fa:
        print("  → CRACKED VIOLIN CASE:")
        print("    Damaged zone resonant capacity")
        print("    is slightly below the false attractor.")
    elif best_fr == fa:
        print("  → CANCELLATION-ONLY CASE:")
        print("    FA and FR coincide.")
        print("    Anti-signal at FA is sufficient.")
    else:
        print("  → FR ABOVE FA (less common).")
        print("    Document carefully.")

    ear["fr_hz"] = best_fr
    session.save()
    return best_fr

# ═══════════════════════════════════════════════════════════
# PHASE 5 — ORTHOGONAL RE-SWEEP
# ═══════════════════════════════════════════════════════════

def orthogonal_resweep(session, side, fa):
    """
    Run a second rainbow sweep with the anti-signal
    at FA active simultaneously.

    This tests whether there is remaining gradient
    in other eigenfunction dimensions — i.e., whether
    the calibration has found the global optimum or
    only a local one.

    If a new Better cluster appears: more structure
    exists. The gradient is not zero. More work can
    be done (e.g., the tinnitus has components at
    multiple eigenfunction positions — complex tinnitus).

    If no Better responses anywhere: converged.
    The protocol has found the calibration optimum
    for this individual's cochlear eigenfunction map.

    Returns: clear (bool) — True if converged
    """
    ear   = session.ear(side)
    phase = ear["phase_deg"]
    amp   = ear["amplitude"]
    play  = play_left if side == "L" else play_right

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  ORTHOGONAL RE-SWEEP — {side} EAR                   │
  │                                             │
  │  Anti-signal at FA ({fa} Hz) is now         │
  │  playing continuously under each tone.      │
  │                                             │
  │  You are checking whether there is any      │
  │  remaining gradient in the eigenfunction    │
  │  space. If you find improvement anywhere:   │
  │  there is more structure to find.           │
  │  If nothing helps: you have converged.      │
  │                                             │
  │  Feedback: B / W / N as before.             │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    responses  = {}
    anti_sig   = make_tone(fa,
                           SWEEP_TONE_DURATION + 1,
                           amplitude=amp,
                           phase_deg=phase)

    for i, (pos, freq) in enumerate(RAINBOW):
        if abs(freq - fa) < 50:
            # Skip — this is FA itself
            continue
        hz_label = f"{freq:.0f} Hz"
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  {hz_label}")
        input("  ENTER to play ...")

        probe = make_tone(freq,
                          SWEEP_TONE_DURATION,
                          amplitude=amp * 0.5)
        # Pad anti-signal to same length as probe
        n   = len(probe)
        bg  = anti_sig[:n]
        combined = np.clip(bg + probe, -1.0, 1.0)
        play(combined)

        r = ask("B / W / N:", valid={"B","W","N"})
        responses[freq] = r
        print(f"  → {r}")

    better = [f for f, r in responses.items() if r == "B"]

    if better:
        print(f"""
  ── ORTHOGONAL SWEEP RESULT ─────────────────────
  New Better responses found at:
    {[f"{f:.0f} Hz" for f in sorted(better)]}

  INTERPRETATION: There is residual gradient.
  The tinnitus may have components at multiple
  eigenfunction positions (complex tinnitus).
  Consider running gradient descent again from
  the new Better frequencies.
  ─────────────────────────────────────────────────
        """)
        ear["orthogonal_clear"] = False
    else:
        print(f"""
  ── ORTHOGONAL SWEEP RESULT ─────────────────────
  No new Better responses found.

  INTERPRETATION: CONVERGED.
  The calibration has found the optimum for
  this individual's cochlear eigenfunction map.
  No remaining gradient in other dimensions.
  ────────────────────��────────────────────────────
        """)
        ear["orthogonal_clear"] = True

    session.save()
    return ear["orthogonal_clear"]

# ═══════════════════════════════════════════════════════════
# PHASE 6 — WAV FILE GENERATION
# ═══════════════════════════════════════════════════════════

def generate_remedy(session, side, duration_minutes=60):
    """
    Generate a personalized sleep remedy WAV file
    for one ear using calibrated parameters.

    Three layers:
      1. Pink noise reference floor (with FA notched)
      2. Anti-signal at FA, calibrated phase
      3. FR boost (cracked violin layer)

    Returns: output filename
    """
    ear   = session.ear(side)
    fa    = ear["fa_hz"]
    fr    = ear["fr_hz"]
    phase = ear["phase_deg"]
    amp   = ear["amplitude"]

    if fa is None:
        print(f"  No FA calibrated for {side} ear. "
              f"Skipping.")
        return None

    print(f"""
  Generating {side} ear remedy:
    FA       = {fa} Hz
    FR       = {fr} Hz
    Phase    = {phase}°
    Duration = {duration_minutes} min
    """)

    duration_s = duration_minutes * 60
    n_samples  = int(SAMPLE_RATE * duration_s)
    t          = np.linspace(0, duration_s,
                              n_samples, endpoint=False)

    # Layer 1: Pink noise (FA notched)
    pink = make_pink_noise(duration_s, amplitude=0.03)

    # Notch FA from pink noise: attenuate narrow band
    # Simple approach: subtract a sine at FA scaled
    # to match the pink noise level at that frequency
    fa_notch_depth = 0.015
    pink -= (fa_notch_depth *
             np.sin(2 * np.pi * fa * t +
                    np.random.uniform(0, 2*np.pi))
             ).astype(np.float32)

    # Layer 2: Anti-signal at FA
    ph_rad = np.deg2rad(phase)
    anti   = (amp * 0.85 *
               np.sin(2 * np.pi * fa * t + ph_rad)
               ).astype(np.float32)

    # Layer 3: FR boost (cracked violin)
    boost  = np.zeros(n_samples, dtype=np.float32)
    if fr is not None and fr != fa:
        boost = (amp * 0.38 *
                 np.sin(2 * np.pi * fr * t)
                 ).astype(np.float32)

    # Combine
    combined = pink + anti + boost
    combined = np.clip(combined, -1.0, 1.0)

    # Fade in/out 3 seconds
    fade_s = int(3 * SAMPLE_RATE)
    combined[:fade_s] *= np.linspace(
        0, 1, fade_s).astype(np.float32)
    combined[-fade_s:] *= np.linspace(
        1, 0, fade_s).astype(np.float32)

    out_int16 = (combined * 32767).astype(np.int16)

    fname = (OUTPUT_WAV_L if side == "L"
             else OUTPUT_WAV_R)
    wavfile.write(fname, SAMPLE_RATE, out_int16)
    print(f"  Saved: {fname}")
    return fname


def generate_binaural(session, duration_minutes=60):
    """
    Generate a single binaural WAV with independent
    L and R channel remedies.
    If only one ear is calibrated, the other channel
    receives pink noise reference only.
    """
    dur_s = duration_minutes * 60
    n     = int(SAMPLE_RATE * dur_s)
    t     = np.linspace(0, dur_s, n, endpoint=False)

    def ear_channel(ear_data):
        fa    = ear_data.get("fa_hz")
        fr    = ear_data.get("fr_hz")
        phase = ear_data.get("phase_deg", 180.0)
        amp   = ear_data.get("amplitude", AMPLITUDE)

        pink  = make_pink_noise(dur_s, amplitude=0.03)

        if fa is None:
            # No tinnitus in this ear — pink noise only
            return pink

        ph_rad = np.deg2rad(phase)
        anti   = (amp * 0.85 *
                   np.sin(2 * np.pi * fa * t + ph_rad)
                   ).astype(np.float32)

        boost = np.zeros(n, dtype=np.float32)
        if fr is not None and fr != fa:
            boost = (amp * 0.38 *
                     np.sin(2 * np.pi * fr * t)
                     ).astype(np.float32)

        fa_notch = (0.015 *
                    np.sin(2 * np.pi * fa * t)
                    ).astype(np.float32)
        sig = np.clip(pink - fa_notch + anti + boost,
                      -1.0, 1.0)
        return sig

    l_chan = ear_channel(session.left)
    r_chan = ear_channel(session.right)

    # Fade
    fade_s = int(3 * SAMPLE_RATE)
    for ch in [l_chan, r_chan]:
        ch[:fade_s]  *= np.linspace(0, 1, fade_s)
        ch[-fade_s:] *= np.linspace(1, 0, fade_s)

    stereo    = np.stack([l_chan, r_chan], axis=1)
    out_int16 = (stereo * 32767).astype(np.int16)
    wavfile.write(OUTPUT_WAV_B, SAMPLE_RATE, out_int16)
    print(f"\n  Binaural remedy saved: {OUTPUT_WAV_B}")
    return OUTPUT_WAV_B

# ═══════════════════════════════════════════════════════════
# VOLUME CALIBRATION UTILITY
# ═══════════════════════════════════════════════════════════

def calibrate_volume():
    """
    Simple volume check before the sweep.
    Plays a reference tone and asks if it is audible.
    Guides the user to set system volume correctly.
    """
    global AMPLITUDE

    print("""
  ── VOLUME CHECK ───────────��────────────────────
  Before the sweep, we need to confirm you can
  hear the tones at the correct volume.

  The tones should be:
    — Clearly audible
    — Comfortable — never loud or sharp
    — Quieter than normal conversation
  ─────────────────────────────────────────────────
    """)

    ref_freq = 6000.0  # Hz — mid tinnitus zone
    while True:
        input(f"  Playing {ref_freq:.0f} Hz reference "
              f"(both ears) — ENTER ...")
        tone = make_tone(ref_freq, 4,
                         amplitude=AMPLITUDE)
        stereo = np.stack([tone, tone], axis=1)
        sd.play(stereo, SAMPLE_RATE)
        sd.wait()

        r = ask(
            "Can you hear it clearly? "
            "Is it comfortable? (Y / louder / quieter):",
            valid={"Y", "LOUDER", "QUIETER"})

        if r == "Y":
            print(f"  Volume set. Amplitude = {AMPLITUDE:.3f}")
            break
        elif r == "LOUDER":
            AMPLITUDE = min(AMPLITUDE * 1.5, 0.5)
            print(f"  Increased → {AMPLITUDE:.3f}")
        elif r == "QUIETER":
            AMPLITUDE = max(AMPLITUDE * 0.7, 0.01)
            print(f"  Decreased → {AMPLITUDE:.3f}")

# ═══════════════════════════════════════════════════════════
# FULL PROTOCOL — ONE EAR
# ═══════════════════════════════════════════════════════════

def calibrate_ear(session, side):
    """
    Run the full calibration protocol for one ear.

    Phases:
      1. Rainbow sweep
      2. Gradient descent
      3. Phase calibration
      4. FR sweep
      5. Orthogonal re-sweep
      6. WAV generation
    """
    side = side.upper()
    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  CALIBRATING: {side} EAR                           ║
  ╚═════════════════════════════════════════════╝
    """)

    # Phase 1 — Rainbow sweep
    print("\n  PHASE 1 — RAINBOW SWEEP")
    responses = rainbow_sweep(session, side)
    start_freq, landscape = interpret_rainbow(responses)

    if start_freq is None:
        print(f"  Cannot calibrate {side} ear "
              f"— no Better responses.")
        print("  Check volume or confirm tinnitus "
              "presence in this ear.")
        return

    # Phase 2 — Gradient descent
    print("\n  PHASE 2 — GRADIENT DESCENT")
    fa = gradient_descent(session, side, start_freq)
    print(f"\n  FA locked: {fa} Hz")

    # Phase 3 — Phase calibration
    print("\n  PHASE 3 — PHASE CALIBRATION")
    phase = phase_calibration(session, side, fa)
    print(f"\n  Phase locked: {phase}°")

    # Phase 4 — FR sweep
    print("\n  PHASE 4 — FR SWEEP")
    fr = fr_sweep(session, side, fa, phase)
    print(f"\n  FR locked: {fr} Hz")

    # Phase 5 — Orthogonal re-sweep
    print("\n  PHASE 5 — ORTHOGONAL RE-SWEEP")
    converged = orthogonal_resweep(session, side, fa)

    # Phase 6 — WAV generation
    print("\n  PHASE 6 — WAV GENERATION")
    generate_remedy(session, side)

    # Summary
    ear = session.ear(side)
    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  {side} EAR CALIBRATION COMPLETE                   ║
  ╠═════════════════════════════════════════════╣
  ║  FA  (false attractor):   {str(fa) + ' Hz':>10}       ║
  ║  FR  (residual resonant): {str(fr) + ' Hz':>10}       ║
  ║  Phase (cancellation):    {str(phase) + '°':>10}       ║
  ║  Converged:               {str(converged):>10}       ║
  ╚═════════════════════════════════════════════╝
    """)

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("""
  ╔═════════════════════════════════════════════════════╗
  ║   TINNITUS EIGENFUNCTION CALIBRATION SYSTEM         ║
  ║   OC-TINNITUS-001 — OrganismCore                    ║
  ║   Eric Robert Lawson — 2026-03-23                   ║
  ╠═════════════════════════════════════════════════════╣
  ║                                                     ║
  ║   This system finds your tinnitus eigenfunction     ║
  ║   position and generates a personalized             ║
  ║   cancellation remedy.                              ║
  ║                                                     ║
  ║   Self-administrable. No specialist required.       ║
  ║   You are the measurement instrument.               ║
  ║                                                     ║
  ║   Duration: ~30–45 minutes (full bilateral)         ║
  ║   Output:   remedy_left.wav                         ║
  ║             remedy_right.wav                        ║
  ║             remedy_binaural.wav                     ║
  ║                                                     ║
  ║   INSTALL: pip install sounddevice numpy scipy      ║
  ╚═════════════════════════════════════════════════════╝
    """)

    # Resume previous session?
    session = None
    prev    = Session.load()
    if prev:
        r = ask("Previous session found. Resume? (Y/N):",
                valid={"Y", "N"})
        if r == "Y":
            session = prev
            print("  Session resumed.")

    if session is None:
        session = Session()

    # Volume calibration
    calibrate_volume()

    # Which ears?
    print("""
  Which ears have tinnitus?
    L — left only
    R — right only
    B — both ears
    """)
    ears = ask("L / R / B:", valid={"L", "R", "B"})

    sides = []
    if ears in {"L", "B"}:
        sides.append("L")
    if ears in {"R", "B"}:
        sides.append("R")

    # Calibrate each ear independently
    for side in sides:
        calibrate_ear(session, side)

        if len(sides) > 1 and side == sides[0]:
            print(f"""
  ── Break before {sides[1]} ear ──────────────────────
  Take a 5-minute break.
  Let your auditory system rest.
  Tinnitus perception can shift after sustained
  acoustic engagement.
  ─────────────────────────────────────────────────
            """)
            input("  Press ENTER when ready for "
                  f"{sides[1]} ear ...")

    # Generate binaural remedy if both ears calibrated
    if len(sides) == 2:
        print("\n  Generating binaural remedy ...")
        generate_binaural(session)

    # Final prescription summary
    print("""
  ╔═════════════════════════════════════════════════════╗
  ║   CALIBRATION COMPLETE — PRESCRIPTION SUMMARY       ║
  ╚═════════════════════════════════════════════════════╝
    """)
    for side in ["L", "R"]:
        ear = session.ear(side)
        if ear["fa_hz"] is not None:
            print(f"  {side} EAR:")
            print(f"    FA        : {ear['fa_hz']} Hz")
            print(f"    FR        : {ear['fr_hz']} Hz")
            print(f"    Phase     : {ear['phase_deg']}°")
            print(f"    Converged : {ear['orthogonal_clear']}")
            print()

    print("  SLEEP REMEDY FILES:")
    for side in sides:
        fname = (OUTPUT_WAV_L if side == "L"
                 else OUTPUT_WAV_R)
        if os.path.exists(fname):
            print(f"    {side} ear : {fname}")
    if len(sides) == 2 and os.path.exists(OUTPUT_WAV_B):
        print(f"    Binaural  : {OUTPUT_WAV_B}")

    print("""
  TO USE:
    Play the remedy file on loop
    through headphones while sleeping.
    Volume: quiet — barely audible.

  RE-CALIBRATE:
    Run this script again when efficacy
    changes — tinnitus frequency drifts.
    Previous session auto-saved to:
  """)
    print(f"    {LOG_FILE}")
    print()
    session.save()


if __name__ == "__main__":
    main()
