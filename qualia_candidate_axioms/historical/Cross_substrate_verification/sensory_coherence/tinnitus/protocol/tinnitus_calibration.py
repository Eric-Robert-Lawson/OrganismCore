"""
TINNITUS EIGENFUNCTION CALIBRATION SYSTEM
OC-TINNITUS-001 — OrganismCore
Eric Robert Lawson — 2026-03-23

PROTOCOL:
  Phase 0A — Volume calibration
             Confirm tones audible and comfortable.

  Phase 0B — Beanie pre-calibration
             Measure formation lag and dissolution lag
             of the individual's false attractor using
             manual occlusion (hand or beanie over ear).
             These two measurements set personalised
             tone duration and inter-trial interval
             for all subsequent phases.

             BEANIE PRINCIPLE:
             The false attractor is not a switch.
             It is a resonance that builds and decays
             according to the dynamics of the physical
             system. Formation and dissolution both
             have temporal lag. Feedback requested
             before the effect stabilises is feedback
             at the point of maximum ambiguity.
             Feedback requested before dissolution
             is complete contaminates the next trial.
             These lags must be measured individually
             before the sweep begins.

             Formation lag:  time from occlusion onset
                             to first perceptible change.
                             Sets minimum tone duration.
             Dissolution lag: time from occlusion removal
                             to return to baseline.
                             Sets minimum inter-trial interval.

  Phase 1  — Rainbow sweep (eigenfunction sampler)
             One ear at a time.
             Each tone = one structural position
             on the basilar membrane, equally spaced
             in cochlear geometry (Greenwood function).
             Tone duration: personalised from Phase 0B.
             Feedback window: 5s post-tone settling
             period before B/W/N is requested.
             Inter-trial: confirmed by person
             (press ENTER when back to baseline).
             Dissolution time logged per tone —
             second feedback channel, proxy for
             attractor well depth at each position.

  Phase 2  — Gradient descent from landscape
             Follow directionality from sweep.
             Fine-tune toward cancellation optimum.
             Same timing protocol as Phase 1.
             Feedback: B / W / N / L (lock).

  Phase 3  — Phase calibration
             At locked FA, sweep phase 0-360.
             Find actual cancellation phase for
             this individual's cochlear geometry.
             Same timing protocol.

  Phase 4  — FR sweep (residual resonant frequency)
             Find frequency adjacent to FA where
             damaged structure still responds to
             external signal (cracked violin layer).
             Same timing protocol.

  Phase 5  — Orthogonal re-sweep
             Second rainbow sweep with FA anti-signal
             active continuously.
             Checks for residual gradient in other
             eigenfunction dimensions.
             Same timing protocol.

  Phase 6  — WAV file generation
             Personalised sleep remedy from all
             calibrated parameters.
             Per-ear. Independent L/R channels.

SELF-ADMINISTRABLE:
  No second person required.
  You are the measurement instrument.
  Run on yourself.

BEANIE INSIGHT (Eric Robert Lawson, 2026-03-23):
  False attractor formation and dissolution both
  have temporal lag. The effect of a signal on the
  false attractor is not instantaneous — it builds
  during delivery and continues after the tone stops.
  The return to baseline after the tone stops is
  also not instantaneous — the attractor must drain
  before the next tone can be measured independently.

  This means:
    — Tones must be long enough for the effect
      to stabilise before feedback is requested.
    — Feedback must be requested in a post-tone
      settling window, not at tone offset.
    — Inter-trial rest must be confirmed by the
      person, not set by a fixed timer.
    — Dissolution time is itself structural data:
      longer dissolution = deeper attractor well
      = more severe damage at that position.
    — Both lags are personalised: deep attractor
      wells (severe tinnitus) fill fast and drain
      slow. Shallow wells fill slow and drain fast.
      Fixed timing gets severe cases exactly wrong.

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

# These are DEFAULTS — both are overridden by
# Phase 0B beanie pre-calibration for each ear.
# Minimum tone duration (seconds).
# Phase 0B sets this per-ear from formation lag.
DEFAULT_TONE_DURATION   = 15

# Post-tone settling window before feedback (seconds).
# Effect may continue building after tone stops.
# Fixed at 5s — not personalised, not skippable.
POST_TONE_SETTLE_S      = 5

# Starting amplitude — adjusted by Phase 0A.
AMPLITUDE = 0.10

# Fade in/out duration (ms) — prevents clicks.
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

    pos_lo=0.30 → ~500 Hz  (avoid very low)
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
              amplitude=None,
              phase_deg=0.0,
              harmonic_2=0.0,
              harmonic_3=0.0,
              sr=SAMPLE_RATE):
    """
    Generate a sine tone with optional harmonics
    and smooth fade in/out.
    """
    if amplitude is None:
        amplitude = AMPLITUDE
    n   = int(sr * duration_s)
    t   = np.linspace(0, duration_s, n, endpoint=False)
    ph  = np.deg2rad(phase_deg)

    sig = np.sin(2 * np.pi * freq_hz * t + ph)
    if harmonic_2 > 0:
        sig += harmonic_2 * np.sin(
            2 * np.pi * 2 * freq_hz * t + ph)
    if harmonic_3 > 0:
        sig += harmonic_3 * np.sin(
            2 * np.pi * 3 * freq_hz * t + ph)
    sig *= amplitude

    fade_n = int(FADE_MS * sr / 1000)
    fade_n = min(fade_n, n // 4)
    sig[:fade_n]  *= np.linspace(0, 1, fade_n)
    sig[-fade_n:] *= np.linspace(1, 0, fade_n)
    return sig.astype(np.float32)

def make_pink_noise(duration_s, amplitude=0.03,
                    sr=SAMPLE_RATE):
    """
    Approximate pink noise (1/f) by summing
    octave-spaced sine waves with 1/f amplitudes.
    """
    n   = int(sr * duration_s)
    t   = np.linspace(0, duration_s, n, endpoint=False)
    octave_freqs = [125, 250, 500, 1000,
                    2000, 4000, 8000]
    sig = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(octave_freqs):
        a  = amplitude / (i + 1) ** 0.5
        ph = np.random.uniform(0, 2 * np.pi)
        sig += (a * np.sin(2 * np.pi * f * t + ph)
                ).astype(np.float32)
    return sig

def stereo_left(mono):
    z = np.zeros_like(mono)
    return np.stack([mono, z], axis=1)

def stereo_right(mono):
    z = np.zeros_like(mono)
    return np.stack([z, mono], axis=1)

def play_left(sig):
    sd.play(stereo_left(sig), SAMPLE_RATE)
    sd.wait()

def play_right(sig):
    sd.play(stereo_right(sig), SAMPLE_RATE)
    sd.wait()

def play_both(sig_l, sig_r):
    n = max(len(sig_l), len(sig_r))
    l = np.zeros(n, dtype=np.float32)
    r = np.zeros(n, dtype=np.float32)
    l[:len(sig_l)] = sig_l
    r[:len(sig_r)] = sig_r
    sd.play(np.stack([l, r], axis=1), SAMPLE_RATE)
    sd.wait()

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

class Session:
    """Holds all calibration data for one session."""

    def __init__(self):
        self.timestamp = datetime.datetime.now(
            ).isoformat()
        self.left  = self._ear()
        self.right = self._ear()
        self.notes = []

    def _ear(self):
        return {
            # Beanie pre-calibration (Phase 0B)
            "formation_lag_s":    None,
            "dissolution_lag_s":  None,
            "tone_duration_s":    DEFAULT_TONE_DURATION,
            # Rainbow and descent
            "rainbow":            {},
            "dissolution_map":    {},  # freq → dissolution_s
            "fa_hz":              None,
            "fr_hz":              None,
            "phase_deg":          180.0,
            "amplitude":          AMPLITUDE,
            "ri_duration_s":      None,
            "suppression":        None,
            "converged":          False,
            "orthogonal_clear":   False,
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
    Prompt for input, validate against allowed set.
    Case-insensitive.
    """
    while True:
        raw = input(f"  {prompt} ").strip().upper()
        if valid is None or raw in valid:
            return raw
        print(f"  → Please enter one of: "
              f"{', '.join(sorted(valid))}")

# ═══════════════════════════════════════════════════════════
# CORE TRIAL PRIMITIVE
# Encapsulates the corrected timing protocol for
# every tone played in every phase.
# ═══════════════════════════════════════════════════════════

def run_trial(freq_hz, tone_duration_s, play_fn,
              amplitude=None,
              phase_deg=0.0,
              extra_signal=None,
              label="",
              ask_baseline=False):
    """
    Play one calibration trial with correct timing:

      1. Optional baseline bother check.
      2. Play tone (+ optional extra_signal mixed in).
      3. Post-tone settling window (POST_TONE_SETTLE_S).
         Effect may continue building after tone stops.
         Feedback is NOT requested during this window.
      4. Request B/W/N feedback at settled perception.
      5. Start dissolution timer.
      6. Wait for person to confirm baseline restored.
      7. Log and return result.

    Parameters:
      freq_hz        : frequency of probe tone
      tone_duration_s: how long to play (from beanie cal)
      play_fn        : play_left or play_right
      amplitude      : override global AMPLITUDE
      phase_deg      : phase of probe tone
      extra_signal   : numpy array mixed with probe
                       (used in FR sweep and ortho sweep)
      label          : display label for this trial
      ask_baseline   : if True, ask bother score before

    Returns:
      (response, dissolution_s)
      response      : "B", "W", or "N"
      dissolution_s : seconds until baseline restored
    """
    if amplitude is None:
        amplitude = AMPLITUDE

    baseline_score = None
    if ask_baseline:
        baseline_score = int(input(
            "  Tinnitus bother RIGHT NOW (0–10): "
        ).strip())

    # Build probe tone
    probe = make_tone(freq_hz, tone_duration_s,
                      amplitude=amplitude,
                      phase_deg=phase_deg)

    # Mix extra signal if provided
    if extra_signal is not None:
        n = len(probe)
        bg = extra_signal[:n] if len(
            extra_signal) >= n else np.pad(
            extra_signal, (0, n - len(extra_signal)))
        combined = np.clip(probe + bg, -1.0, 1.0
                           ).astype(np.float32)
    else:
        combined = probe

    # Play tone
    print(f"  Playing{' ' + label if label else ''} "
          f"{freq_hz:.0f} Hz  "
          f"({tone_duration_s}s) ...")
    play_fn(combined)

    # Post-tone settling window — do not ask yet.
    # The effect may still be building.
    print(f"  [Settling {POST_TONE_SETTLE_S}s "
          f"— notice what is happening ...]")
    time.sleep(POST_TONE_SETTLE_S)

    # Request feedback at settled perception
    response = ask("B / W / N  "
                   "(better / worse / no difference):",
                   valid={"B", "W", "N"})

    # Dissolution timer — starts at feedback moment
    print("  Press ENTER the moment tinnitus "
          "returns to your normal baseline ...")
    t0 = time.time()
    input()
    dissolution_s = time.time() - t0

    print(f"  → {response}  |  "
          f"dissolution {dissolution_s:.1f}s")

    if baseline_score is not None:
        return response, dissolution_s, baseline_score
    return response, dissolution_s

# ═══════════════════════════════════════════════════════════
# PHASE 0A — VOLUME CALIBRATION
# ═══════════════════════════════════════════════════════════

def calibrate_volume():
    """
    Confirm tones are audible and comfortable.
    Adjust AMPLITUDE until reference tone is
    clearly perceptible and never uncomfortable.
    """
    global AMPLITUDE

    print("""
  ── PHASE 0A: VOLUME CHECK ──────────────────────
  The tones should be:
    — Clearly audible
    — Comfortable — never loud or sharp
    — Quieter than normal conversation

  If all rainbow tones produce N responses later,
  return here and increase volume.
  ─────────────────���───────────────────────────────
    """)

    ref_freq = 6000.0
    while True:
        input(f"  Playing {ref_freq:.0f} Hz reference "
              f"(both ears) — ENTER ...")
        tone   = make_tone(ref_freq, 4,
                           amplitude=AMPLITUDE)
        stereo = np.stack([tone, tone], axis=1)
        sd.play(stereo, SAMPLE_RATE)
        sd.wait()

        r = ask("Clearly audible and comfortable? "
                "(Y / LOUDER / QUIETER):",
                valid={"Y", "LOUDER", "QUIETER"})

        if r == "Y":
            print(f"  Volume set. "
                  f"Amplitude = {AMPLITUDE:.3f}")
            break
        elif r == "LOUDER":
            AMPLITUDE = min(AMPLITUDE * 1.5, 0.5)
            print(f"  Increased → {AMPLITUDE:.3f}")
        elif r == "QUIETER":
            AMPLITUDE = max(AMPLITUDE * 0.7, 0.01)
            print(f"  Decreased → {AMPLITUDE:.3f}")

# ═══════════════════════════════════════════════════════════
# PHASE 0B — BEANIE PRE-CALIBRATION
# ═══════════════════════════════════════════════════════════

def beanie_calibration(session, side):
    """
    Measure the formation lag and dissolution lag
    of the individual's false attractor using manual
    ear occlusion (hand or beanie pressed over ear).

    WHAT IS BEING MEASURED:

    Formation lag:
      Time from occlusion onset to first perceptible
      change in tinnitus (any change — louder, different
      quality, new tone). The false attractor is forming
      under the occluded resonant cavity.
      This is the minimum tone duration needed to allow
      the cancellation effect to stabilise before
      feedback is requested.

    Dissolution lag:
      Time from occlusion removal to return to normal
      baseline tinnitus. The false attractor is draining.
      This is the minimum inter-trial interval — the
      time the person needs between tones to ensure
      each trial is measured on a clean baseline.

    RELATIONSHIP TO ATTRACTOR WELL DEPTH:
      Deep wells (severe tinnitus, acute trauma):
        formation lag SHORT — deep wells fill fast
        dissolution lag LONG — deep wells drain slow
      Shallow wells (mild tinnitus):
        formation lag LONGER — shallow wells fill slow
        dissolution lag SHORT — shallow wells drain fast

      Fixed timing assumes the opposite relationship
      and gets severe cases exactly wrong.
      This measurement corrects that.

    TONE DURATION RULE:
      tone_duration_s = max(formation_lag_s * 2.5,
                            DEFAULT_TONE_DURATION)
      The factor of 2.5 ensures the effect has fully
      stabilised before the post-tone settling window.

    Returns: (formation_lag_s, dissolution_lag_s,
              tone_duration_s)
    """
    ear  = session.ear(side)
    play = play_left if side == "L" else play_right

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 0B: BEANIE PRE-CALIBRATION           │
  │  {side} EAR                                       │
  │                                             │
  │  This measures how quickly your false       │
  │  attractor forms and dissolves.             │
  │                                             │
  │  These two timings personalise the entire   │
  │  sweep for your specific attractor depth.   │
  │                                             │
  │  You will use your hand or a beanie to      │
  │  partially occlude the ear canal.           │
  │  Fold your palm gently over the ear —       │
  │  enough to muffle outside sound but not     │
  │  enough to cause discomfort or pressure.    │
  │                                             │
  │  Do not press hard. Gentle occlusion only.  │
  └─────────────────────────────────────────────┘
    """)

    # ── FORMATION LAG ──────────────────────────────
    print("  ── FORMATION LAG ──────────────────────────")
    print("""
  Sit quietly. Notice your tinnitus at its
  current baseline level.

  When you press ENTER below, start timing.
  Gently press your palm over the affected ear
  to partially occlude it.

  The moment you notice ANY change in the
  tinnitus — louder, different, a new tone
  appearing — press ENTER again immediately.

  If nothing changes after 30 seconds,
  press ENTER anyway and we will note that.
    """)
    input("  Press ENTER, then occlude your ear ...")
    t_form_start = time.time()
    input("  Press ENTER the moment you notice "
          "ANY change in the tinnitus ...")
    formation_lag_s = time.time() - t_form_start

    if formation_lag_s > 28:
        print(f"  Formation lag: >28s (no clear change)")
        print("  This may indicate:")
        print("    — Noise-like tinnitus without a")
        print("      single dominant frequency")
        print("    — Very shallow attractor well")
        print("    — Occlusion insufficient")
        print("  Using default tone duration.")
        formation_lag_s = DEFAULT_TONE_DURATION / 2.5
    else:
        print(f"  Formation lag: {formation_lag_s:.1f}s")

    # ── DISSOLUTION LAG ────────────────────────────
    print("\n  ── DISSOLUTION LAG ────────────────────────")
    print("""
  Keep your palm over the ear for 15 more
  seconds to allow the false attractor to
  fully establish.

  Then remove your hand when prompted.
  Press ENTER the moment the tinnitus returns
  to what it was BEFORE you covered the ear
  — your normal baseline.
    """)
    print("  Holding occlusion for 15 seconds ...")
    time.sleep(15)
    input("  Remove your hand NOW — "
          "press ENTER when baseline is restored ...")
    t_diss_start = time.time()
    input("  Press ENTER when tinnitus is back "
          "to its normal baseline ...")
    dissolution_lag_s = time.time() - t_diss_start

    print(f"  Dissolution lag: {dissolution_lag_s:.1f}s")

    # ── COMPUTE TONE DURATION ──────────────────────
    tone_duration_s = max(
        formation_lag_s * 2.5,
        DEFAULT_TONE_DURATION
    )
    # Cap at 45s — practical limit for session length
    tone_duration_s = min(tone_duration_s, 45.0)
    # Round to nearest second
    tone_duration_s = round(tone_duration_s)

    print(f"""
  ── BEANIE CALIBRATION RESULT ───────────────────
  Formation lag      : {formation_lag_s:.1f}s
  Dissolution lag    : {dissolution_lag_s:.1f}s
  Tone duration set  : {tone_duration_s}s
  Inter-trial timing : person-confirmed
                       (press ENTER when baseline
                        restored between every tone)

  ATTRACTOR DEPTH ESTIMATE:
    {"DEEP (severe — fills fast, drains slow)" 
      if dissolution_lag_s > formation_lag_s * 1.5 
      else "MODERATE" 
      if dissolution_lag_s > 5 
      else "SHALLOW (mild — fills slow, drains fast)"}
  ───────────────────────────��─────────────────────
    """)

    ear["formation_lag_s"]   = formation_lag_s
    ear["dissolution_lag_s"] = dissolution_lag_s
    ear["tone_duration_s"]   = tone_duration_s
    ear["amplitude"]         = AMPLITUDE
    session.save()

    return formation_lag_s, dissolution_lag_s, \
           tone_duration_s

# ═══════════════════════════════════════════════════════════
# PHASE 1 — RAINBOW SWEEP
# ═══════════════════════════════════════════════════════════

def rainbow_sweep(session, side):
    """
    Play each eigenfunction position tone.
    Tone duration from beanie calibration.
    Post-tone settling window before feedback.
    Inter-trial: person-confirmed return to baseline.
    Dissolution time logged per tone as second channel.

    Returns dict: freq_hz → response
    """
    ear            = session.ear(side)
    play           = play_left if side == "L" else play_right
    tone_duration  = ear["tone_duration_s"]
    dissolution_map = {}

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 1: RAINBOW SWEEP — {side} EAR               │
  │                                             │
  │  {len(RAINBOW)} tones at cochlear eigenfunction       │
  │  positions. Equally spaced on basilar       │
  │  membrane geometry (Greenwood function).    │
  │                                             │
  │  Each tone: {tone_duration}s                          │
  │  After each tone: {POST_TONE_SETTLE_S}s settling window.    │
  │  Then: B / W / N feedback.                 │
  │  Then: confirm baseline before next tone.  │
  │                                             │
  │  B — tinnitus BETTER (any reduction,        │
  │      even subtle — trust it)               │
  │  W — tinnitus WORSE (louder, stronger)      │
  │  N — NO DIFFERENCE                          │
  │                                             │
  │  The dissolution time between tones is      │
  │  also logged — it maps attractor depth      │
  │  across the eigenfunction space.            │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER when ready ...")

    responses = {}
    for i, (pos, freq) in enumerate(RAINBOW):
        hz_label = f"{freq:.0f} Hz"
        mm_label = f"{pos * 35:.1f} mm"
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  "
              f"{hz_label:>9}  "
              f"cochlear {mm_label}")
        input("  Press ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz        = freq,
            tone_duration_s= tone_duration,
            play_fn        = play,
            label          = f"[{i+1}/{len(RAINBOW)}]"
        )

        responses[freq]           = response
        dissolution_map[freq]     = dissolution_s

        # Wait for confirmed baseline before next tone.
        # Do not proceed until person confirms.
        # This is enforced — not optional.
        if i < len(RAINBOW) - 1:
            print("  Waiting for baseline to restore ...")
            input("  Press ENTER when your tinnitus "
                  "is back to normal baseline ...")

    ear["rainbow"]          = {str(k): v
                                for k, v in
                                responses.items()}
    ear["dissolution_map"]  = {str(k): v
                                for k, v in
                                dissolution_map.items()}
    session.save()
    return responses, dissolution_map


def interpret_rainbow(responses, dissolution_map):
    """
    Analyse rainbow sweep results.
    Uses both subjective B/W/N and dissolution times
    as convergent evidence for eigenfunction position.

    Returns: best_freq, landscape dict
    """
    better = [f for f, r in responses.items() if r == "B"]
    worse  = [f for f, r in responses.items() if r == "W"]
    same   = [f for f, r in responses.items() if r == "N"]

    # Find frequency with longest dissolution time —
    # structural evidence independent of B/W/N.
    # Longest dissolution = deepest interaction =
    # closest to FA eigenfunction position.
    best_dissolution_freq = None
    if dissolution_map:
        best_dissolution_freq = max(
            dissolution_map, key=dissolution_map.get)

    print(f"""
  ── RAINBOW LANDSCAPE ────────────────────────────
  Better responses   : {len(better)} tones
    {[f"{f:.0f}" for f in sorted(better)]}
  Worse responses    : {len(worse)} tones
    {[f"{f:.0f}" for f in sorted(worse)]}
  No difference      : {len(same)} tones

  Longest dissolution: {
    f"{best_dissolution_freq:.0f} Hz"
    f" ({dissolution_map[best_dissolution_freq]:.1f}s)"
    if best_dissolution_freq else "none"
  }
  ─────────────────────────────────────────────────
    """)

    # Report dissolution map as depth profile
    print("  Attractor depth by eigenfunction position:")
    for freq in sorted(dissolution_map.keys()):
        d = dissolution_map[freq]
        r = responses.get(freq, "?")
        bar = "█" * min(int(d * 2), 30)
        print(f"  {freq:7.0f} Hz  {r}  "
              f"{d:5.1f}s  {bar}")
    print()

    if not better and best_dissolution_freq is None:
        print("  No Better responses and no dissolution "
              "signal detected.")
        print("  Possible causes:")
        print("    1. Volume too low — increase AMPLITUDE.")
        print("    2. Noise-like / broadband tinnitus.")
        print("    3. No tinnitus in this ear.")
        return None, {}

    # Determine best starting frequency.
    # Primary: B responses.
    # Secondary (if no B): longest dissolution time.
    if better:
        if len(better) == 1:
            best = better[0]
        else:
            best = sorted(better)[-1]
            if worse:
                worst_min = min(worse)
                candidates = [f for f in better
                               if f < worst_min]
                if candidates:
                    best = max(candidates)

        # Cross-check with dissolution signal.
        # If dissolution peak is far from B cluster,
        # note the discrepancy — may indicate
        # B response was subjective noise.
        if (best_dissolution_freq and
                abs(best_dissolution_freq - best) > 2000):
            print(f"  NOTE: B cluster at {best:.0f} Hz")
            print(f"  Dissolution peak at "
                  f"{best_dissolution_freq:.0f} Hz")
            print("  These diverge. Gradient descent will")
            print("  clarify. Trust the dissolution signal")
            print("  if B/W feedback is ambiguous.")

    else:
        # No B responses — use dissolution peak
        best = best_dissolution_freq
        print(f"  No B responses. Using dissolution peak "
              f"as start: {best:.0f} Hz")

    print(f"\n  Starting gradient descent at: {best:.0f} Hz")
    return best, {"better":   better,
                  "worse":    worse,
                  "same":     same,
                  "best_dissolution": best_dissolution_freq}

# ═══════════════════════════════════════════════════════════
# PHASE 2 — GRADIENT DESCENT
# ════════════════════════════════════════��══════════════════

def gradient_descent(session, side, start_freq):
    """
    Patient-guided gradient descent toward FA.

    Uses corrected timing from beanie calibration:
    personalised tone duration, post-tone settling
    window, person-confirmed inter-trial interval.

    Dissolution time logged per step — cross-validates
    subjective B/W/N with objective attractor depth.

    Returns: fa_hz
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 2: GRADIENT DESCENT — {side} EAR            │
  │                                             │
  │  Starting at {start_freq:.0f} Hz                     │
  │  Tone duration: {tone_duration}s                        │
  │                                             │
  │  After each tone + {POST_TONE_SETTLE_S}s settling:         │
  │    B — better    W — worse    N — same      │
  │    L — LOCK (this is the optimum)           │
  │                                             │
  │  After feedback: confirm baseline before    │
  │  each next step.                            │
  │                                             │
  │  Watch for convergence: dissolving longer   │
  │  after B responses means you are near FA.   │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    freq      = float(start_freq)
    step      = 300.0
    direction = 0
    history   = []   # (freq_hz, response, dissolution_s)
    fa        = freq

    for iteration in range(80):
        f_int = max(200, min(16000, int(round(freq))))
        pos   = greenwood_pos(f_int)
        mm    = pos * 35

        print(f"\n  Step {iteration+1:2d}: "
              f"{f_int} Hz  "
              f"cochlear {mm:.1f} mm  "
              f"step={step:.0f} Hz")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz        = f_int,
            tone_duration_s= tone_duration,
            play_fn        = play,
            label          = f"step {iteration+1}"
        )
        history.append((f_int, response, dissolution_s))

        # After feedback, confirm baseline before next
        if response != "L":
            print("  Confirm baseline before next step.")
            input("  Press ENTER when tinnitus "
                  "is back to normal baseline ...")

        # Navigation logic
        if response == "L":
            fa = f_int
            print(f"\n  Locked at {fa} Hz")
            print(f"  Final dissolution: {dissolution_s:.1f}s")
            break

        elif response == "B":
            fa = f_int
            if direction == 0:
                direction = 1
            step = max(step * 0.65, 5.0)
            freq += direction * step

        elif response == "W":
            if direction == 0:
                direction = -1
            else:
                direction *= -1
            step = max(step * 0.65, 5.0)
            freq += direction * step

        elif response == "N":
            step = min(step * 1.4, 500.0)
            direction = 1 if direction <= 0 else -1
            freq += direction * step

        # Convergence: 3 consecutive B, step < 8 Hz
        if (len(history) >= 3 and
                all(h[1] == "B" for h in history[-3:])
                and step <= 8.0):
            fa = f_int
            print(f"\n  Converged at {fa} Hz")
            # Report dissolution trend at convergence
            recent_d = [h[2] for h in history[-3:]]
            print(f"  Dissolution at convergence: "
                  f"{recent_d[0]:.1f}s → "
                  f"{recent_d[1]:.1f}s → "
                  f"{recent_d[2]:.1f}s")
            break

    ear["fa_hz"] = fa
    session.save()
    return fa

# ═══════════════════════════════════════════════════════════
# PHASE 3 — PHASE CALIBRATION
# ═══════════════════════════════════════════════════════════

def phase_calibration(session, side, fa):
    """
    Sweep phase 0–360° at locked FA frequency.
    Find individual cancellation phase.

    Uses corrected timing from beanie calibration.
    Dissolution time used as cross-check on B/W/N.

    Returns: best_phase_deg
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 3: PHASE CALIBRATION — {side} EAR           │
  │  FA locked at: {fa} Hz                    │
  │  Tone duration: {tone_duration}s                        │
  │                                             │
  │  Finding your cochlea's cancellation phase. │
  │  180° is the standard assumption.           │
  │  Your cochlear geometry may differ.         │
  │                                             │
  │  Watch for the phase that produces the      │
  │  longest dissolution — this is the          │
  │  structural cross-check on your B/W/N.      │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    # Score map: B=2, N=1, W=0
    # Dissolution time used as tiebreaker
    score_map     = {"B": 2, "N": 1, "W": 0}
    coarse_phases = [0, 45, 90, 135, 180, 225, 270, 315]
    best_phase    = 180
    best_score    = -1
    best_diss     = 0.0
    phase_results = {}

    print("\n  ── Coarse phase sweep (8 angles) ──")
    for ph in coarse_phases:
        print(f"\n  Phase {ph}°")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz        = fa,
            tone_duration_s= tone_duration,
            play_fn        = play,
            phase_deg      = ph,
            label          = f"phase {ph}°"
        )
        score = score_map.get(response, 0)
        phase_results[ph] = (response, score,
                             dissolution_s)
        print(f"  → {response}  dissolution {dissolution_s:.1f}s")

        # Better score, or same score with longer dissolution
        if (score > best_score or
                (score == best_score and
                 dissolution_s > best_diss)):
            best_score = score
            best_phase = ph
            best_diss  = dissolution_s

        input("  Press ENTER when back to baseline ...")

    print(f"\n  Best coarse phase: {best_phase}°  "
          f"(score={best_score}, "
          f"dissolution={best_diss:.1f}s)")
    print("  Fine-tuning ±40° in 10° steps ...")

    fine_phases = range(best_phase - 40,
                        best_phase + 41, 10)
    for ph in fine_phases:
        ph_n = ph % 360
        print(f"\n  Phase {ph_n}°")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz        = fa,
            tone_duration_s= tone_duration,
            play_fn        = play,
            phase_deg      = ph_n,
            label          = f"phase {ph_n}°"
        )
        score = score_map.get(response, 0)
        phase_results[ph_n] = (response, score,
                               dissolution_s)
        print(f"  → {response}  dissolution {dissolution_s:.1f}s")

        if (score > best_score or
                (score == best_score and
                 dissolution_s > best_diss)):
            best_score = best_score
            best_phase = ph_n
            best_diss  = dissolution_s

        input("  Press ENTER when back to baseline ...")

    print(f"\n  Phase locked at: {best_phase}°")
    ear["phase_deg"] = best_phase
    session.save()
    return best_phase

# ═══════════════════════════════════════════════════════════
# PHASE 4 — FR SWEEP (RESIDUAL RESONANT FREQUENCY)
# ═══════════════════════════════════════════════════════════

def fr_sweep(session, side, fa, phase):
    """
    Find residual resonant frequency (FR):
    the frequency where the damaged zone retains
    mechanical response capacity.

    Each trial: anti-signal at FA + probe at test freq.
    Dissolution time cross-validates B/W/N.
    Longest dissolution at a B response = FR.

    Returns: fr_hz
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    amp           = ear["amplitude"]
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 4: FR SWEEP — {side} EAR                    │
  │  FA locked at: {fa} Hz                    │
  │  Tone duration: {tone_duration}s                        │
  │                                             │
  │  Each tone = anti-signal at FA              │
  │            + probe at test frequency.       │
  │                                             │
  │  You are finding the note the cracked       │
  │  instrument can still play.                 │
  │                                             │
  │  B/W/N + dissolution time both logged.      │
  │  Longest dissolution at B = FR.             │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    offsets    = [-400, -300, -200, -150,
                  -100, -50, 0,
                  50, 100, 150, 200, 300, 400]
    score_map  = {"B": 2, "N": 1, "W": 0}
    best_fr    = fa
    best_score = 0
    best_diss  = 0.0

    # Pre-build anti-signal long enough for any trial
    max_dur   = tone_duration + POST_TONE_SETTLE_S + 5
    anti_long = make_tone(fa,
                          max_dur,
                          amplitude=amp,
                          phase_deg=phase)

    for offset in offsets:
        f_test = fa + offset
        if f_test < 300 or f_test > 16000:
            continue
        label = f"FA{'+' if offset >= 0 else ''}{offset}"
        print(f"\n  {label} = {f_test} Hz")
        input("  ENTER to play ...")

        # Probe tone at test frequency
        probe = make_tone(f_test, tone_duration,
                          amplitude=amp * 0.45,
                          phase_deg=0)

        response, dissolution_s = run_trial(
            freq_hz        = f_test,
            tone_duration_s= tone_duration,
            play_fn        = play,
            amplitude      = amp * 0.45,
            extra_signal   = anti_long,
            label          = label
        )

        score = score_map.get(response, 0)
        print(f"  dissolution {dissolution_s:.1f}s")

        if (score > best_score or
                (score == best_score and
                 response == "B" and
                 dissolution_s > best_diss)):
            best_score = score
            best_fr    = f_test
            best_diss  = dissolution_s

        input("  Press ENTER when back to baseline ...")

    print(f"\n  FR identified: {best_fr} Hz")
    print(f"  FA→FR gap: {best_fr - fa:+d} Hz")
    print(f"  FR dissolution: {best_diss:.1f}s")

    if best_fr < fa:
        print("  → CRACKED VIOLIN CASE:")
        print("    Damaged zone capacity below FA.")
    elif best_fr == fa:
        print("  → CANCELLATION-ONLY CASE.")
    else:
        print("  → FR ABOVE FA (less common).")

    ear["fr_hz"] = best_fr
    session.save()
    return best_fr

# ═══════════════════════════════════════════════════════════
# PHASE 5 — ORTHOGONAL RE-SWEEP
# ═══════════════════════════════════════════════════════════

def orthogonal_resweep(session, side, fa):
    """
    Rainbow sweep with FA anti-signal active throughout.
    Tests whether the calibration has converged or
    whether residual gradient exists in other
    eigenfunction dimensions (complex tinnitus).

    Uses corrected timing. Dissolution time logged.

    Returns: converged (bool)
    """
    ear           = session.ear(side)
    phase         = ear["phase_deg"]
    amp           = ear["amplitude"]
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 5: ORTHOGONAL RE-SWEEP — {side} EAR         │
  │                                             │
  │  FA anti-signal active throughout.          │
  │  Probing for residual gradient in other     │
  │  eigenfunction dimensions.                  │
  │                                             │
  │  B anywhere = more structure to find.       │
  │  No B anywhere = converged.                 │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    responses       = {}
    dissolution_map = {}

    max_dur   = tone_duration + POST_TONE_SETTLE_S + 5
    anti_long = make_tone(fa,
                          max_dur,
                          amplitude=amp,
                          phase_deg=phase)

    for i, (pos, freq) in enumerate(RAINBOW):
        if abs(freq - fa) < 50:
            continue
        hz_label = f"{freq:.0f} Hz"
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  {hz_label}")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz        = freq,
            tone_duration_s= tone_duration,
            play_fn        = play,
            amplitude      = amp * 0.5,
            extra_signal   = anti_long,
            label          = f"[ortho {i+1}]"
        )
        responses[freq]       = response
        dissolution_map[freq] = dissolution_s
        print(f"  dissolution {dissolution_s:.1f}s")

        input("  Press ENTER when back to baseline ...")

    better = [f for f, r in responses.items() if r == "B"]

    if better:
        print(f"""
  ── ORTHOGONAL SWEEP RESULT ─────────────────────
  New Better responses at:
    {[f"{f:.0f} Hz" for f in sorted(better)]}

  Dissolution at Better frequencies:
    {[f"{f:.0f} Hz: {dissolution_map[f]:.1f}s"
      for f in sorted(better)]}

  INTERPRETATION: Residual gradient exists.
  Complex tinnitus — components at multiple
  eigenfunction positions.
  Consider gradient descent from new B cluster.
  ─────────────────────────────────────────────────
        """)
        ear["orthogonal_clear"] = False
    else:
        print(f"""
  ── ORTHOGONAL SWEEP RESULT ─────────────────────
  No new Better responses.

  INTERPRETATION: CONVERGED.
  Calibration is at the optimum for this
  individual's cochlear eigenfunction map.
  ─────────────────────────────────────────────────
        """)
        ear["orthogonal_clear"] = True

    session.save()
    return ear["orthogonal_clear"]

# ═══════════════════════════════════════════════════════════
# PHASE 6 — WAV FILE GENERATION
# ═══════════════════════════════════════════════════════════

def generate_remedy(session, side, duration_minutes=60):
    """
    Generate personalised sleep remedy WAV file.

    Three layers:
      1. Pink noise floor (FA notched)
      2. Anti-signal at FA, calibrated phase
      3. FR boost (cracked violin layer)
    """
    ear   = session.ear(side)
    fa    = ear["fa_hz"]
    fr    = ear["fr_hz"]
    phase = ear["phase_deg"]
    amp   = ear["amplitude"]

    if fa is None:
        print(f"  No FA calibrated for {side} ear. "
              "Skipping.")
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

    # Layer 1: Pink noise with FA notched
    pink          = make_pink_noise(duration_s,
                                    amplitude=0.03)
    fa_notch_depth = 0.015
    pink -= (fa_notch_depth *
             np.sin(2 * np.pi * fa * t +
                    np.random.uniform(0, 2*np.pi))
             ).astype(np.float32)

    # Layer 2: Anti-signal at FA, calibrated phase
    ph_rad = np.deg2rad(phase)
    anti   = (amp * 0.85 *
               np.sin(2 * np.pi * fa * t + ph_rad)
               ).astype(np.float32)

    # Layer 3: FR boost (cracked violin)
    boost = np.zeros(n_samples, dtype=np.float32)
    if fr is not None and fr != fa:
        boost = (amp * 0.38 *
                 np.sin(2 * np.pi * fr * t)
                 ).astype(np.float32)

    combined = np.clip(pink + anti + boost, -1.0, 1.0)

    # Fade in/out 3 seconds
    fade_s = int(3 * SAMPLE_RATE)
    combined[:fade_s]  *= np.linspace(
        0, 1, fade_s).astype(np.float32)
    combined[-fade_s:] *= np.linspace(
        1, 0, fade_s).astype(np.float32)

    out_int16 = (combined * 32767).astype(np.int16)
    fname     = (OUTPUT_WAV_L if side == "L"
                 else OUTPUT_WAV_R)
    wavfile.write(fname, SAMPLE_RATE, out_int16)
    print(f"  Saved: {fname}")
    return fname


def generate_binaural(session, duration_minutes=60):
    """
    Generate binaural WAV with independent L/R remedies.
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
            return pink
        ph_rad = np.deg2rad(phase)
        anti   = (amp * 0.85 *
                   np.sin(2 * np.pi * fa * t + ph_rad)
                   ).astype(np.float32)
        boost  = np.zeros(n, dtype=np.float32)
        if fr is not None and fr != fa:
            boost = (amp * 0.38 *
                     np.sin(2 * np.pi * fr * t)
                     ).astype(np.float32)
        fa_notch = (0.015 *
                    np.sin(2 * np.pi * fa * t)
                    ).astype(np.float32)
        return np.clip(pink - fa_notch + anti + boost,
                       -1.0, 1.0)

    l_chan = ear_channel(session.left)
    r_chan = ear_channel(session.right)

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
# FULL PROTOCOL — ONE EAR
# ═══════════════════════════════════════════════════════════

def calibrate_ear(session, side):
    """
    Run the full calibration protocol for one ear.

    Phase 0B — Beanie pre-calibration
    Phase 1   — Rainbow sweep
    Phase 2   — Gradient descent
    Phase 3   — Phase calibration
    Phase 4   — FR sweep
    Phase 5   — Orthogonal re-sweep
    Phase 6   — WAV generation
    """
    side = side.upper()
    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  CALIBRATING: {side} EAR                           ║
  ╚═════════════════════════════════════════════╝
    """)

    # Phase 0B — Beanie pre-calibration
    print("\n  PHASE 0B — BEANIE PRE-CALIBRATION")
    formation_lag, dissolution_lag, tone_duration = \
        beanie_calibration(session, side)
    print(f"\n  Tone duration set: {tone_duration}s")
    print(f"  Formation lag:     {formation_lag:.1f}s")
    print(f"  Dissolution lag:   {dissolution_lag:.1f}s")

    # Phase 1 — Rainbow sweep
    print("\n  PHASE 1 — RAINBOW SWEEP")
    responses, dissolution_map = rainbow_sweep(
        session, side)
    start_freq, landscape = interpret_rainbow(
        responses, dissolution_map)

    if start_freq is None:
        print(f"  Cannot calibrate {side} ear — "
              "no gradient detected.")
        print("  Check volume. Confirm tinnitus present.")
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

    ear = session.ear(side)
    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  {side} EAR CALIBRATION COMPLETE                   ║
  ╠═════════════════════════════════════════════╣
  ║  Formation lag:   {str(round(formation_lag, 1)) + 's':>10}       ║
  ║  Dissolution lag: {str(round(dissolution_lag, 1)) + 's':>10}       ║
  ║  Tone duration:   {str(tone_duration) + 's':>10}       ║
  ║  FA (false attractor):   {str(fa) + ' Hz':>10}    ║
  ║  FR (residual resonant): {str(fr) + ' Hz':>10}    ║
  ║  Phase (cancellation):   {str(phase) + '°':>10}    ║
  ║  Converged:              {str(converged):>10}    ║
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
  ║   Beanie timing correction applied                  ║
  ╠═════════════════════════════════════════════════════╣
  ║                                                     ║
  ║   Finds your tinnitus eigenfunction position        ║
  ║   and generates a personalised cancellation         ║
  ║   remedy. Glasses for a broken ear.                 ║
  ║                                                     ║
  ║   Self-administrable. No specialist required.       ║
  ║   You are the measurement instrument.               ║
  ║                                                     ║
  ║   Duration: ~45–60 minutes (full bilateral)         ║
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

    # Phase 0A — Volume calibration
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
  ── Break before {sides[1]} ear ───────────────────────
  Take a 5-minute break.
  Auditory system needs to rest between ears.
  Tinnitus perception can shift after sustained
  acoustic engagement.
  ──────────────────────────────────────────────
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
            print(f"    Formation lag  : "
                  f"{ear['formation_lag_s']}s")
            print(f"    Dissolution lag: "
                  f"{ear['dissolution_lag_s']}s")
            print(f"    Tone duration  : "
                  f"{ear['tone_duration_s']}s")
            print(f"    FA             : "
                  f"{ear['fa_hz']} Hz")
            print(f"    FR             : "
                  f"{ear['fr_hz']} Hz")
            print(f"    Phase          : "
                  f"{ear['phase_deg']}°")
            print(f"    Converged      : "
                  f"{ear['orthogonal_clear']}")
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
    Play remedy_binaural.wav on loop through
    headphones while sleeping.
    Volume: barely audible.

  RE-CALIBRATE:
    Run again when efficacy changes.
    The false attractor drifts over time.
    Re-calibration takes 20-25 minutes.
    Start fresh (N) when prompted.

  SESSION LOG:
    """)
    print(f"    {LOG_FILE}")
    print()
    session.save()


if __name__ == "__main__":
    main()
