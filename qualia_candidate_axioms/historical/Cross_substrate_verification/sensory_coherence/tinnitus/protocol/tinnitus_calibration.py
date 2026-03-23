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

SEGMENTED SESSION SUPPORT:
  Sessions can be interrupted and resumed at any
  phase boundary. The script detects which phases
  are complete per ear and resumes from the correct
  point. No completed work is repeated.

  At the end of each phase, the script offers a
  pause option. If taken, all data is saved and
  the script exits cleanly. On next run, resume
  is offered and the session continues from where
  it stopped.

  Ctrl+C at any point saves current state before
  exiting. Partial phases are not marked complete
  — they will be re-run on resume from their start.

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
import sys

# ════════════��══════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SAMPLE_RATE           = 44100
LOG_FILE              = "tinnitus_calibration_log.json"
OUTPUT_WAV_L          = "remedy_left.wav"
OUTPUT_WAV_R          = "remedy_right.wav"
OUTPUT_WAV_B          = "remedy_binaural.wav"

DEFAULT_TONE_DURATION = 15

# Post-tone settling window before feedback (seconds).
# Fixed at 5s — not personalised, not skippable.
POST_TONE_SETTLE_S    = 5

# Starting amplitude — adjusted by Phase 0A.
AMPLITUDE = 0.10

# Fade in/out duration (ms) — prevents clicks.
FADE_MS = 80

# Phase identifiers — used as completion flag keys.
PHASE_0B  = "phase_0b"
PHASE_1   = "phase_1"
PHASE_2   = "phase_2"
PHASE_3   = "phase_3"
PHASE_4   = "phase_4"
PHASE_5   = "phase_5"
PHASE_6   = "phase_6"

PHASE_ORDER = [PHASE_0B, PHASE_1, PHASE_2,
               PHASE_3,  PHASE_4, PHASE_5, PHASE_6]

PHASE_LABELS = {
    PHASE_0B: "Phase 0B — Beanie Pre-Calibration",
    PHASE_1:  "Phase 1  — Rainbow Sweep",
    PHASE_2:  "Phase 2  — Gradient Descent",
    PHASE_3:  "Phase 3  — Phase Calibration",
    PHASE_4:  "Phase 4  — FR Sweep",
    PHASE_5:  "Phase 5  — Orthogonal Re-Sweep",
    PHASE_6:  "Phase 6  — WAV Generation",
}

# ═══════════════════════════════════════════════════════════
# GREENWOOD FUNCTION — COCHLEAR EIGENFUNCTION POSITIONS
# ═══════════════════════════════════════════════════════════

def greenwood_freq(x_norm, A=165.4, a=2.1, k=0.88):
    return A * (10 ** (a * x_norm) - k)

def greenwood_pos(freq, A=165.4, a=2.1, k=0.88):
    return np.log10((freq / A) + k) / a

def eigenfunction_rainbow(n_tones=12,
                           pos_lo=0.30,
                           pos_hi=0.95):
    positions = np.linspace(pos_lo, pos_hi, n_tones)
    return [(float(p), float(greenwood_freq(p)))
            for p in positions]

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
    if amplitude is None:
        amplitude = AMPLITUDE
    n  = int(sr * duration_s)
    t  = np.linspace(0, duration_s, n, endpoint=False)
    ph = np.deg2rad(phase_deg)

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
# SESSION — DATA MODEL WITH PHASE FLAGS
# ═══════════════════════════════════════════════════════════

class Session:
    """
    Holds all calibration data for one session.

    Each ear dict contains:
      — Beanie calibration values
      — Rainbow and dissolution data
      — Calibrated parameters (FA, FR, phase)
      — Phase completion flags

    Phase completion flags are set as the LAST
    act of each phase function, after all data
    is written and saved. This ensures that an
    interrupted phase is never marked complete
    and will be re-run on resume.
    """

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
            "dissolution_map":    {},
            "fa_hz":              None,
            "fr_hz":              None,
            "phase_deg":          180.0,
            "amplitude":          AMPLITUDE,
            "ri_duration_s":      None,
            "suppression":        None,
            "converged":          False,
            "orthogonal_clear":   False,
            # Phase completion flags
            # Set only after phase data is fully saved.
            # Never set during a phase — only at its end.
            "phases_complete":    [],
        }

    def ear(self, side):
        return self.left if side == "L" else self.right

    def phase_complete(self, side, phase_id):
        """Return True if the given phase is complete."""
        return phase_id in self.ear(side)["phases_complete"]

    def mark_phase_complete(self, side, phase_id):
        """
        Mark a phase complete and save immediately.
        Called as the last act of each phase function.
        """
        ear = self.ear(side)
        if phase_id not in ear["phases_complete"]:
            ear["phases_complete"].append(phase_id)
        self.save()

    def next_incomplete_phase(self, side):
        """
        Return the first phase not yet complete,
        or None if all phases are done.
        """
        for phase_id in PHASE_ORDER:
            if not self.phase_complete(side, phase_id):
                return phase_id
        return None

    def status_summary(self, side):
        """
        Return a human-readable status string
        showing which phases are done and which
        remain for the given ear.
        """
        lines = [f"  {side} EAR STATUS:"]
        for phase_id in PHASE_ORDER:
            done  = self.phase_complete(side, phase_id)
            label = PHASE_LABELS[phase_id]
            mark  = "✓" if done else "·"
            lines.append(f"    {mark} {label}")
        return "\n".join(lines)

    def save(self):
        with open(LOG_FILE, "w") as f:
            json.dump(self.__dict__, f, indent=2)
        print(f"\n  [Saved → {LOG_FILE}]")

    @classmethod
    def load(cls):
        if not os.path.exists(LOG_FILE):
            return None
        try:
            with open(LOG_FILE) as f:
                data = json.load(f)
            s = cls()
            s.__dict__.update(data)
            # Ensure phases_complete list exists in
            # both ear dicts — handles sessions saved
            # before this field was added.
            for ear_data in [s.left, s.right]:
                if "phases_complete" not in ear_data:
                    ear_data["phases_complete"] = []
                    # Infer completed phases from data
                    # so old sessions resume correctly.
                    _infer_completed_phases(ear_data)
            return s
        except (json.JSONDecodeError, KeyError):
            return None


def _infer_completed_phases(ear_data):
    """
    For sessions saved before phase flags existed,
    infer which phases were complete from the
    presence of their output data.
    Called once during load for old sessions only.
    """
    if ear_data.get("formation_lag_s") is not None:
        if PHASE_0B not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_0B)
    if ear_data.get("rainbow"):
        if PHASE_1 not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_1)
    if ear_data.get("fa_hz") is not None:
        if PHASE_2 not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_2)
    # Phase 3 output is phase_deg — but default is 180.0
    # so presence alone is ambiguous. Only infer if
    # Phase 2 is done and FR is also set (meaning
    # Phase 3 must have run between them).
    if (ear_data.get("fa_hz") is not None and
            ear_data.get("fr_hz") is not None):
        if PHASE_3 not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_3)
    if ear_data.get("fr_hz") is not None:
        if PHASE_4 not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_4)
    if ear_data.get("orthogonal_clear") is not False:
        if PHASE_5 not in ear_data["phases_complete"]:
            ear_data["phases_complete"].append(PHASE_5)

# ═══════════════════════════════════════════════════════════
# INPUT HELPERS
# ═══════════════════════════════════════════════════════════

def ask(prompt, valid=None):
    """Prompt for input, validate against allowed set."""
    while True:
        raw = input(f"  {prompt} ").strip().upper()
        if valid is None or raw in valid:
            return raw
        print(f"  → Please enter one of: "
              f"{', '.join(sorted(valid))}")


def offer_break(session, side, after_phase):
    """
    After completing a phase, offer the person
    the option to pause and save before continuing.

    If they take the break:
      — Print resume instructions
      — Exit the script cleanly

    This is the designed session boundary.
    The next run will detect the saved session
    and resume from the next incomplete phase.

    Returns True if continuing, False if pausing.
    """
    r = ask(
        f"Phase complete. Take a break? "
        f"(Y to save and exit / N to continue):",
        valid={"Y", "N"}
    )
    if r == "Y":
        session.save()
        ear = session.ear(side)
        next_phase = session.next_incomplete_phase(side)
        print(f"""
  ── SESSION PAUSED ─────────────────────────────
  All data saved to: {LOG_FILE}

  Completed so far ({side} ear):
{session.status_summary(side)}

  Next phase when you return:
    {PHASE_LABELS.get(next_phase, "All phases complete")}

  TO RESUME:
    Run the script again.
    When asked "Resume previous session?",
    answer Y.
    The script will continue from where
    you stopped — no completed work repeated.
  ───────────────────────────────────────────────
        """)
        sys.exit(0)
    return True


# ═══════════════════════════════════════════════════════════
# CTRL+C HANDLER — SAVE ON INTERRUPT
# ═══════════════════════════════════════════════════════════

_current_session = None

def _save_on_interrupt(session):
    """Register session for save-on-interrupt."""
    global _current_session
    _current_session = session


import signal as _signal

def _signal_handler(sig, frame):
    print("\n\n  [Interrupted — saving session ...]")
    if _current_session is not None:
        try:
            _current_session.save()
            print(f"  Saved to {LOG_FILE}")
            print("  Run the script again and answer Y")
            print("  to resume from where you stopped.")
        except Exception:
            pass
    sys.exit(0)

_signal.signal(_signal.SIGINT, _signal_handler)

# ═══════════════════════════════════════════════════════════
# CORE TRIAL PRIMITIVE
# ═══════════════════════════════════════��═══════════════════

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
      4. Request B/W/N feedback at settled perception.
      5. Dissolution timer until baseline confirmed.
      6. Return (response, dissolution_s).
    """
    if amplitude is None:
        amplitude = AMPLITUDE

    baseline_score = None
    if ask_baseline:
        baseline_score = int(input(
            "  Tinnitus bother RIGHT NOW (0–10): "
        ).strip())

    probe = make_tone(freq_hz, tone_duration_s,
                      amplitude=amplitude,
                      phase_deg=phase_deg)

    if extra_signal is not None:
        n  = len(probe)
        bg = (extra_signal[:n]
              if len(extra_signal) >= n
              else np.pad(extra_signal,
                          (0, n - len(extra_signal))))
        combined = np.clip(
            probe + bg, -1.0, 1.0).astype(np.float32)
    else:
        combined = probe

    print(f"  Playing{' ' + label if label else ''} "
          f"{freq_hz:.0f} Hz  ({tone_duration_s}s) ...")
    play_fn(combined)

    print(f"  [Settling {POST_TONE_SETTLE_S}s "
          f"— notice what is happening ...]")
    time.sleep(POST_TONE_SETTLE_S)

    response = ask("B / W / N  "
                   "(better / worse / no difference):",
                   valid={"B", "W", "N"})

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
# (Not per-ear, not tracked by phase flags —
#  runs at session start regardless of resume state)
# ═══════════════════════════════════════════════════════════

def calibrate_volume():
    global AMPLITUDE

    print("""
  ── PHASE 0A: VOLUME CHECK ──────────────────────
  The tones should be:
    — Clearly audible
    — Comfortable — never loud or sharp
    — Quieter than normal conversation

  If all rainbow tones produce N responses later,
  return here and increase volume.
  ─────────────────────────────────────────────────
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
    Measure formation lag and dissolution lag.
    Sets personalised tone duration for all phases.

    Marks PHASE_0B complete as its final act.
    Returns: (formation_lag_s, dissolution_lag_s,
              tone_duration_s)
    """
    ear = session.ear(side)

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 0B: BEANIE PRE-CALIBRATION           │
  │  {side} EAR                                       │
  │                                             │
  │  Measures how quickly your false attractor  │
  │  forms and dissolves. Personalises all      │
  │  subsequent tone durations and inter-trial  │
  │  timing for your attractor depth.           │
  │                                             │
  │  Use your hand or a beanie to gently cover  │
  │  the ear canal. Fold palm over ear —        │
  │  enough to muffle sound, not to cause       │
  │  pressure or discomfort.                    │
  │                                             │
  │  Do not press hard. Gentle occlusion only.  │
  └─────────────────────────────────────────────┘
    """)

    # ── FORMATION LAG ──────────────────────────────
    print("  ── FORMATION LAG ──────────────────────────")
    print("""
  Sit quietly. Notice tinnitus at baseline.

  Press ENTER, then immediately occlude your ear.
  Press ENTER again the moment you notice ANY
  change (louder, different, new tone appearing).

  If nothing changes after 30 seconds, press
  ENTER anyway.
    """)
    input("  Press ENTER, then occlude your ear ...")
    t_form_start = time.time()
    input("  Press ENTER at first detectable change ...")
    formation_lag_s = time.time() - t_form_start

    if formation_lag_s > 28:
        print("  Formation lag: >28s (no clear change)")
        print("  Using default tone duration.")
        formation_lag_s = DEFAULT_TONE_DURATION / 2.5
    else:
        print(f"  Formation lag: {formation_lag_s:.1f}s")

    # ── DISSOLUTION LAG ────────────────────────────
    print("\n  ── DISSOLUTION LAG ────────────────────────")
    print("""
  Keep occlusion for 15 more seconds to fully
  establish the false attractor.

  Then remove your hand when prompted.
  Press ENTER the moment tinnitus is back to
  exactly what it was before you covered the ear.
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
    tone_duration_s = min(tone_duration_s, 45.0)
    tone_duration_s = round(tone_duration_s)

    depth_label = (
        "DEEP (severe — fills fast, drains slow)"
        if dissolution_lag_s > formation_lag_s * 1.5
        else "MODERATE"
        if dissolution_lag_s > 5
        else "SHALLOW (mild — fills slow, drains fast)"
    )

    print(f"""
  ── BEANIE CALIBRATION RESULT ───────────────────
  Formation lag      : {formation_lag_s:.1f}s
  Dissolution lag    : {dissolution_lag_s:.1f}s
  Tone duration set  : {tone_duration_s}s
  Attractor depth    : {depth_label}
  ─────────────────────────────────────────────────
    """)

    ear["formation_lag_s"]  = formation_lag_s
    ear["dissolution_lag_s"] = dissolution_lag_s
    ear["tone_duration_s"]  = tone_duration_s
    ear["amplitude"]        = AMPLITUDE

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_0B)

    return formation_lag_s, dissolution_lag_s, \
           tone_duration_s

# ═══════════════════════════════════════════════════════════
# PHASE 1 — RAINBOW SWEEP
# ═══════════════════════════════════════════════════════════

def rainbow_sweep(session, side):
    """
    Play each eigenfunction position tone.
    Marks PHASE_1 complete as its final act.
    Returns: (responses dict, dissolution_map dict)
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]
    dissolution_map = {}

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 1: RAINBOW SWEEP — {side} EAR               │
  │                                             │
  │  {len(RAINBOW)} tones at Greenwood-spaced positions. │
  │  Each tone: {tone_duration}s + {POST_TONE_SETTLE_S}s settling.          │
  │                                             │
  │  B — tinnitus BETTER (any reduction)        │
  │  W — tinnitus WORSE                         │
  │  N — NO DIFFERENCE                          │
  │                                             │
  │  Confirm baseline before each next tone.    │
  │  Dissolution time is also logged.           │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER when ready ...")

    responses = {}
    for i, (pos, freq) in enumerate(RAINBOW):
        hz_label = f"{freq:.0f} Hz"
        mm_label = f"{pos * 35:.1f} mm"
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  "
              f"{hz_label:>9}  cochlear {mm_label}")
        input("  Press ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = freq,
            tone_duration_s = tone_duration,
            play_fn         = play,
            label           = f"[{i+1}/{len(RAINBOW)}]"
        )
        responses[freq]       = response
        dissolution_map[freq] = dissolution_s

        if i < len(RAINBOW) - 1:
            print("  Waiting for baseline ...")
            input("  Press ENTER when tinnitus "
                  "is back to normal baseline ...")

    ear["rainbow"]         = {str(k): v
                               for k, v in
                               responses.items()}
    ear["dissolution_map"] = {str(k): v
                               for k, v in
                               dissolution_map.items()}

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_1)

    return responses, dissolution_map


def interpret_rainbow(responses, dissolution_map):
    """
    Analyse rainbow sweep results.
    Returns: (best_freq, landscape dict)
    """
    better = [f for f, r in responses.items() if r == "B"]
    worse  = [f for f, r in responses.items() if r == "W"]
    same   = [f for f, r in responses.items() if r == "N"]

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

    print("  Attractor depth by eigenfunction position:")
    for freq in sorted(dissolution_map.keys()):
        d   = dissolution_map[freq]
        r   = responses.get(freq, "?")
        bar = "█" * min(int(d * 2), 30)
        print(f"  {freq:7.0f} Hz  {r}  {d:5.1f}s  {bar}")
    print()

    if not better and best_dissolution_freq is None:
        print("  No gradient detected.")
        print("  1. Volume too low — increase AMPLITUDE.")
        print("  2. Noise-like tinnitus.")
        print("  3. No tinnitus in this ear.")
        return None, {}

    if better:
        best = sorted(better)[-1] if len(better) > 1 \
               else better[0]
        if worse:
            worst_min  = min(worse)
            candidates = [f for f in better
                          if f < worst_min]
            if candidates:
                best = max(candidates)
        if (best_dissolution_freq and
                abs(best_dissolution_freq - best) > 2000):
            print(f"  NOTE: B cluster at {best:.0f} Hz, "
                  f"dissolution peak at "
                  f"{best_dissolution_freq:.0f} Hz.")
            print("  These diverge. Trust dissolution "
                  "if B/W is ambiguous.")
    else:
        best = best_dissolution_freq
        print(f"  No B responses. Using dissolution "
              f"peak: {best:.0f} Hz")

    print(f"\n  Starting gradient descent at: {best:.0f} Hz")
    return best, {"better":           better,
                  "worse":            worse,
                  "same":             same,
                  "best_dissolution": best_dissolution_freq}

# ═══════════════════════════════════════════════════════════
# PHASE 2 — GRADIENT DESCENT
# ═══════════════════════════════════════════════════════════

def gradient_descent(session, side, start_freq):
    """
    Patient-guided gradient descent toward FA.
    Marks PHASE_2 complete as its final act.
    Returns: fa_hz
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 2: GRADIENT DESCENT — {side} EAR            │
  │  Starting at {start_freq:.0f} Hz                     │
  │  Tone duration: {tone_duration}s                        │
  │                                             │
  │  B — better   W — worse   N — same          │
  │  L — LOCK (this is the optimum)             │
  │                                             │
  │  Confirm baseline before each step.         │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    freq      = float(start_freq)
    step      = 300.0
    direction = 0
    history   = []
    fa        = freq

    for iteration in range(80):
        f_int = max(200, min(16000, int(round(freq))))
        pos   = greenwood_pos(f_int)
        mm    = pos * 35

        print(f"\n  Step {iteration+1:2d}: "
              f"{f_int} Hz  cochlear {mm:.1f} mm  "
              f"step={step:.0f} Hz")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = f_int,
            tone_duration_s = tone_duration,
            play_fn         = play,
            label           = f"step {iteration+1}"
        )
        history.append((f_int, response, dissolution_s))

        if response != "L":
            print("  Confirm baseline before next step.")
            input("  Press ENTER when tinnitus "
                  "is back to normal baseline ...")

        if response == "L":
            fa = f_int
            print(f"\n  Locked at {fa} Hz")
            break
        elif response == "B":
            fa = f_int
            if direction == 0:
                direction = 1
            step  = max(step * 0.65, 5.0)
            freq += direction * step
        elif response == "W":
            if direction == 0:
                direction = -1
            else:
                direction *= -1
            step  = max(step * 0.65, 5.0)
            freq += direction * step
        elif response == "N":
            step      = min(step * 1.4, 500.0)
            direction = 1 if direction <= 0 else -1
            freq     += direction * step

        if (len(history) >= 3 and
                all(h[1] == "B" for h in history[-3:])
                and step <= 8.0):
            fa = f_int
            recent_d = [h[2] for h in history[-3:]]
            print(f"\n  Converged at {fa} Hz")
            print(f"  Dissolution: "
                  f"{recent_d[0]:.1f}s → "
                  f"{recent_d[1]:.1f}s → "
                  f"{recent_d[2]:.1f}s")
            break

    ear["fa_hz"] = fa

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_2)

    return fa

# ═══════════════════════════════════════════════════════════
# PHASE 3 — PHASE CALIBRATION
# ═══════════════════════════════════════════════════════════

def phase_calibration(session, side, fa):
    """
    Sweep phase 0–360° at locked FA.
    Marks PHASE_3 complete as its final act.
    Returns: best_phase_deg
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 3: PHASE CALIBRATION — {side} EAR           │
  │  FA: {fa} Hz   Tone duration: {tone_duration}s          │
  │                                             │
  │  Finding your cochlea's cancellation phase. │
  │  Longest dissolution = structural           │
  │  cross-check on B/W/N.                      │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    score_map     = {"B": 2, "N": 1, "W": 0}
    coarse_phases = [0, 45, 90, 135, 180, 225, 270, 315]
    best_phase    = 180
    best_score    = -1
    best_diss     = 0.0

    print("\n  ── Coarse phase sweep (8 angles) ──")
    for ph in coarse_phases:
        print(f"\n  Phase {ph}°")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = fa,
            tone_duration_s = tone_duration,
            play_fn         = play,
            phase_deg       = ph,
            label           = f"phase {ph}°"
        )
        score = score_map.get(response, 0)
        print(f"  → {response}  dissolution {dissolution_s:.1f}s")

        if (score > best_score or
                (score == best_score and
                 dissolution_s > best_diss)):
            best_score = score
            best_phase = ph
            best_diss  = dissolution_s

        input("  Press ENTER when back to baseline ...")

    print(f"\n  Best coarse phase: {best_phase}°  "
          f"dissolution={best_diss:.1f}s")
    print("  Fine-tuning ±40° in 10° steps ...")

    for ph in range(best_phase - 40, best_phase + 41, 10):
        ph_n = ph % 360
        print(f"\n  Phase {ph_n}°")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = fa,
            tone_duration_s = tone_duration,
            play_fn         = play,
            phase_deg       = ph_n,
            label           = f"phase {ph_n}°"
        )
        score = score_map.get(response, 0)
        print(f"  → {response}  dissolution {dissolution_s:.1f}s")

        if (score > best_score or
                (score == best_score and
                 dissolution_s > best_diss)):
            best_score = score
            best_phase = ph_n
            best_diss  = dissolution_s

        input("  Press ENTER when back to baseline ...")

    print(f"\n  Phase locked at: {best_phase}°")
    ear["phase_deg"] = best_phase

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_3)

    return best_phase

# ═══════════════════════════════════════════════════════════
# PHASE 4 — FR SWEEP
# ═══════════════════════════════════════════════════════════

def fr_sweep(session, side, fa, phase):
    """
    Find residual resonant frequency (FR).
    Marks PHASE_4 complete as its final act.
    Returns: fr_hz
    """
    ear           = session.ear(side)
    play          = play_left if side == "L" else play_right
    amp           = ear["amplitude"]
    tone_duration = ear["tone_duration_s"]

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE 4: FR SWEEP — {side} EAR                    │
  │  FA: {fa} Hz   Tone duration: {tone_duration}s          │
  │                                             │
  │  Anti-signal at FA active throughout.       │
  │  Finding the note the cracked instrument    │
  │  can still play.                            │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    offsets   = [-400, -300, -200, -150,
                 -100, -50, 0,
                 50, 100, 150, 200, 300, 400]
    score_map = {"B": 2, "N": 1, "W": 0}
    best_fr   = fa
    best_score = 0
    best_diss  = 0.0

    max_dur   = tone_duration + POST_TONE_SETTLE_S + 5
    anti_long = make_tone(fa, max_dur,
                          amplitude=amp,
                          phase_deg=phase)

    for offset in offsets:
        f_test = fa + offset
        if f_test < 300 or f_test > 16000:
            continue
        label = f"FA{'+' if offset >= 0 else ''}{offset}"
        print(f"\n  {label} = {f_test} Hz")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = f_test,
            tone_duration_s = tone_duration,
            play_fn         = play,
            amplitude       = amp * 0.45,
            extra_signal    = anti_long,
            label           = label
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
    print(f"  FA→FR gap: {best_fr - fa:+d} Hz  "
          f"dissolution: {best_diss:.1f}s")

    if best_fr < fa:
        print("  → CRACKED VIOLIN CASE")
    elif best_fr == fa:
        print("  → CANCELLATION-ONLY CASE")
    else:
        print("  → FR ABOVE FA (less common)")

    ear["fr_hz"] = best_fr

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_4)

    return best_fr

# ═══════════════════════════════════════════════════════════
# PHASE 5 — ORTHOGONAL RE-SWEEP
# ═══════════════════════════════════════════════════════════

def orthogonal_resweep(session, side, fa):
    """
    Rainbow sweep with FA anti-signal active.
    Checks for residual gradient (complex tinnitus).
    Marks PHASE_5 complete as its final act.
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
  │  B anywhere = more structure to find.       │
  │  No B anywhere = converged.                 │
  └─────────────────────────────────────────────┘
    """)
    input("  Press ENTER to begin ...")

    responses       = {}
    dissolution_map = {}
    max_dur         = tone_duration + POST_TONE_SETTLE_S + 5
    anti_long       = make_tone(fa, max_dur,
                                amplitude=amp,
                                phase_deg=phase)

    for i, (pos, freq) in enumerate(RAINBOW):
        if abs(freq - fa) < 50:
            continue
        print(f"\n  [{i+1:2d}/{len(RAINBOW)}]  {freq:.0f} Hz")
        input("  ENTER to play ...")

        response, dissolution_s = run_trial(
            freq_hz         = freq,
            tone_duration_s = tone_duration,
            play_fn         = play,
            amplitude       = amp * 0.5,
            extra_signal    = anti_long,
            label           = f"[ortho {i+1}]"
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
  Dissolution:
    {[f"{f:.0f} Hz: {dissolution_map[f]:.1f}s"
      for f in sorted(better)]}
  INTERPRETATION: Complex tinnitus.
  Residual gradient — more structure to find.
  ─────────────────────────────────────────────────
        """)
        ear["orthogonal_clear"] = False
    else:
        print("""
  ── ORTHOGONAL SWEEP RESULT ─────────────────────
  No new Better responses.
  INTERPRETATION: CONVERGED.
  ─────────────────────────────────────────────────
        """)
        ear["orthogonal_clear"] = True

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_5)

    return ear["orthogonal_clear"]

# ═══════════════════════════════════════════════════════════
# PHASE 6 — WAV FILE GENERATION
# ═══════════════════════════════════════════════════════════

def generate_remedy(session, side, duration_minutes=60):
    """
    Generate personalised sleep remedy WAV file.
    Marks PHASE_6 complete as its final act.
    Returns: output filename or None.
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
    FA = {fa} Hz   FR = {fr} Hz
    Phase = {phase}°   Duration = {duration_minutes} min
    """)

    duration_s = duration_minutes * 60
    n_samples  = int(SAMPLE_RATE * duration_s)
    t          = np.linspace(0, duration_s,
                              n_samples, endpoint=False)

    pink = make_pink_noise(duration_s, amplitude=0.03)
    pink -= (0.015 *
             np.sin(2 * np.pi * fa * t +
                    np.random.uniform(0, 2*np.pi))
             ).astype(np.float32)

    ph_rad = np.deg2rad(phase)
    anti   = (amp * 0.85 *
               np.sin(2 * np.pi * fa * t + ph_rad)
               ).astype(np.float32)

    boost = np.zeros(n_samples, dtype=np.float32)
    if fr is not None and fr != fa:
        boost = (amp * 0.38 *
                 np.sin(2 * np.pi * fr * t)
                 ).astype(np.float32)

    combined = np.clip(pink + anti + boost, -1.0, 1.0)
    fade_s   = int(3 * SAMPLE_RATE)
    combined[:fade_s]  *= np.linspace(
        0, 1, fade_s).astype(np.float32)
    combined[-fade_s:] *= np.linspace(
        1, 0, fade_s).astype(np.float32)

    out_int16 = (combined * 32767).astype(np.int16)
    fname     = (OUTPUT_WAV_L if side == "L"
                 else OUTPUT_WAV_R)
    wavfile.write(fname, SAMPLE_RATE, out_int16)
    print(f"  Saved: {fname}")

    # Mark complete — must be last write before return.
    session.mark_phase_complete(side, PHASE_6)

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
        return np.clip(
            pink - fa_notch + anti + boost, -1.0, 1.0)

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
# CALIBRATE EAR — SEGMENTED SESSION AWARE
# ═══════════════════════════════════════════════════════════

def calibrate_ear(session, side):
    """
    Run (or resume) the full calibration for one ear.

    Checks phase completion flags before each phase.
    Skips completed phases entirely.
    Resumes from the first incomplete phase.
    Offers a break after each completed phase.

    Phase data needed by later phases is read from
    the session object, so resumed phases have access
    to all values set by earlier phases regardless of
    whether those phases ran in this session or a
    previous one.
    """
    side = side.upper()
    ear  = session.ear(side)

    # ── Show current status on entry ──────────────────
    next_phase = session.next_incomplete_phase(side)
    if next_phase is None:
        print(f"\n  {side} ear: all phases already complete.")
        print(f"  Skipping to WAV regeneration if needed.")
        if not os.path.exists(
                OUTPUT_WAV_L if side == "L"
                else OUTPUT_WAV_R):
            generate_remedy(session, side)
        return

    # Show what is done and what remains
    print(f"\n{session.status_summary(side)}")
    if next_phase != PHASE_0B:
        print(f"\n  Resuming at: "
              f"{PHASE_LABELS[next_phase]}")
    input("\n  Press ENTER to continue ...")

    # ── PHASE 0B ──────────────────────────────────────
    if not session.phase_complete(side, PHASE_0B):
        print(f"\n  ── {PHASE_LABELS[PHASE_0B]} ──")
        formation_lag, dissolution_lag, tone_duration = \
            beanie_calibration(session, side)
        print(f"\n  Tone duration: {tone_duration}s  "
              f"Formation: {formation_lag:.1f}s  "
              f"Dissolution: {dissolution_lag:.1f}s")
        offer_break(session, side, PHASE_0B)
    else:
        print(f"\n  ✓ {PHASE_LABELS[PHASE_0B]} "
              f"(tone duration: "
              f"{ear['tone_duration_s']}s)")

    # ── PHASE 1 ───────────────��───────────────────────
    if not session.phase_complete(side, PHASE_1):
        print(f"\n  ── {PHASE_LABELS[PHASE_1]} ──")
        responses, dissolution_map = rainbow_sweep(
            session, side)
        start_freq, landscape = interpret_rainbow(
            responses, dissolution_map)
        if start_freq is None:
            print(f"  Cannot calibrate {side} ear — "
                  "no gradient detected.")
            print("  Check volume. "
                  "Confirm tinnitus present.")
            return
        # Store start_freq for Phase 2 handoff
        ear["_start_freq"] = start_freq
        session.save()
        offer_break(session, side, PHASE_1)
    else:
        print(f"\n  ✓ {PHASE_LABELS[PHASE_1]}")
        # Reconstruct start_freq from saved rainbow data
        # for use by Phase 2 if it hasn't run yet.
        if not session.phase_complete(side, PHASE_2):
            responses_raw    = ear.get("rainbow", {})
            dissolution_raw  = ear.get("dissolution_map",
                                       {})
            responses       = {float(k): v
                               for k, v in
                               responses_raw.items()}
            dissolution_map = {float(k): v
                               for k, v in
                               dissolution_raw.items()}
            start_freq, _   = interpret_rainbow(
                responses, dissolution_map)
            ear["_start_freq"] = start_freq
            session.save()

    # ── PHASE 2 ───────────────────────────────────────
    if not session.phase_complete(side, PHASE_2):
        print(f"\n  ── {PHASE_LABELS[PHASE_2]} ──")
        start_freq = ear.get("_start_freq")
        if start_freq is None:
            print("  ERROR: No start frequency available.")
            print("  Re-run Phase 1 (delete log file).")
            return
        fa = gradient_descent(session, side, start_freq)
        print(f"\n  FA locked: {fa} Hz")
        offer_break(session, side, PHASE_2)
    else:
        fa = ear["fa_hz"]
        print(f"\n  ✓ {PHASE_LABELS[PHASE_2]}  "
              f"FA = {fa} Hz")

    # ── PHASE 3 ───────────────────────────────────────
    if not session.phase_complete(side, PHASE_3):
        print(f"\n  ── {PHASE_LABELS[PHASE_3]} ──")
        phase = phase_calibration(session, side, fa)
        print(f"\n  Phase locked: {phase}°")
        offer_break(session, side, PHASE_3)
    else:
        phase = ear["phase_deg"]
        print(f"\n  ✓ {PHASE_LABELS[PHASE_3]}  "
              f"Phase = {phase}°")

    # ── PHASE 4 ────────────��──────────────────────────
    if not session.phase_complete(side, PHASE_4):
        print(f"\n  ── {PHASE_LABELS[PHASE_4]} ──")
        fr = fr_sweep(session, side, fa, phase)
        print(f"\n  FR locked: {fr} Hz")
        offer_break(session, side, PHASE_4)
    else:
        fr = ear["fr_hz"]
        print(f"\n  ✓ {PHASE_LABELS[PHASE_4]}  "
              f"FR = {fr} Hz")

    # ── PHASE 5 ───────────────────────────────────────
    if not session.phase_complete(side, PHASE_5):
        print(f"\n  ── {PHASE_LABELS[PHASE_5]} ──")
        converged = orthogonal_resweep(
            session, side, fa)
        offer_break(session, side, PHASE_5)
    else:
        converged = ear["orthogonal_clear"]
        print(f"\n  ✓ {PHASE_LABELS[PHASE_5]}  "
              f"Converged = {converged}")

    # ── PHASE 6 ───────────────────────────────────────
    if not session.phase_complete(side, PHASE_6):
        print(f"\n  ── {PHASE_LABELS[PHASE_6]} ──")
        generate_remedy(session, side)
    else:
        print(f"\n  ✓ {PHASE_LABELS[PHASE_6]}")

    # ── SUMMARY ───────────────────────────────────────
    formation_lag  = ear.get("formation_lag_s",  "?")
    dissolution_lag = ear.get("dissolution_lag_s", "?")
    tone_dur       = ear.get("tone_duration_s",  "?")

    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  {side} EAR CALIBRATION COMPLETE                   ║
  ╠═════════════════════════════════════════════╣
  ║  Formation lag:          {str(round(formation_lag, 1)) + 's' if isinstance(formation_lag, float) else str(formation_lag):>10}    ║
  ║  Dissolution lag:        {str(round(dissolution_lag, 1)) + 's' if isinstance(dissolution_lag, float) else str(dissolution_lag):>10}    ║
  ║  Tone duration:          {str(tone_dur) + 's':>10}    ║
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
  ╠═════════════════════════════════════════════════════╣
  ║                                                     ║
  ║   Segmented session support — resume at any         ║
  ║   phase boundary. No completed work repeated.       ║
  ║                                                     ║
  ║   Duration: ~2–2.5 hours bilateral (severe case)   ║
  ║             ~45–60 minutes unilateral (mild case)  ║
  ║                                                     ║
  ║   Output:   remedy_left.wav                         ║
  ║             remedy_right.wav                        ║
  ║             remedy_binaural.wav                     ║
  ║                                                     ║
  ║   INSTALL: pip install sounddevice numpy scipy      ║
  ╚═════════════════════════════════════════════════════╝
    """)

    # ── Session load / create ──────────────────────────
    session = None
    prev    = Session.load()

    if prev:
        # Show what is already done before asking
        any_done = False
        for s in ["L", "R"]:
            completed = prev.ear(s)["phases_complete"]
            if completed:
                any_done = True
                print(prev.status_summary(s))

        if any_done:
            r = ask(
                "Previous session found with completed "
                "phases. Resume? (Y/N):",
                valid={"Y", "N"}
            )
            if r == "Y":
                session = prev
                print("  Session resumed.")
            else:
                confirm = ask(
                    "Start fresh? All saved data will "
                    "be lost. (Y/N):",
                    valid={"Y", "N"}
                )
                if confirm == "Y":
                    session = Session()
                    print("  New session started.")
                else:
                    session = prev
                    print("  Keeping existing session.")
        else:
            session = Session()
    else:
        session = Session()

    # Register for Ctrl+C save
    _save_on_interrupt(session)

    # ── Phase 0A — Volume calibration ─────────────────
    # Always run at session start — not phase-flagged.
    # Takes 2 minutes. Confirms hardware is working.
    # If resuming, volume must be re-confirmed because
    # headphones may have been reconnected.
    calibrate_volume()
    # Sync AMPLITUDE into any ear that hasn't run 0B yet
    for s in ["L", "R"]:
        if not session.phase_complete(s, PHASE_0B):
            session.ear(s)["amplitude"] = AMPLITUDE

    # ── Which ears? ────────────────────────────────────
    # On resume, pre-select ears that have incomplete
    # phases. On fresh start, ask.
    incomplete_ears = [
        s for s in ["L", "R"]
        if session.next_incomplete_phase(s) is not None
    ]

    if session.timestamp != Session().timestamp or \
            not incomplete_ears:
        # Fresh session or all ears complete — ask
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
    else:
        sides = incomplete_ears
        if len(sides) == 1:
            print(f"\n  Resuming {sides[0]} ear "
                  f"(other ear already complete or "
                  f"not selected).")
        else:
            print(f"\n  Resuming both ears.")

    # ── Calibrate each ear ────────────────────────────
    for i, side in enumerate(sides):
        calibrate_ear(session, side)

        # Inter-ear break for bilateral sessions
        if len(sides) > 1 and i == 0:
            remaining = sides[1]
            if session.next_incomplete_phase(
                    remaining) is not None:
                print(f"""
  ── Break before {remaining} ear ──────────────────────
  Take at least 10 minutes.
  Auditory attention degrades with sustained
  perceptual engagement. The second ear
  calibration requires the same quality of
  attention as the first.

  For severe bilateral cases: consider
  scheduling the second ear as a separate
  session (run script again, answer Y to
  resume — it will go directly to {remaining} ear).
  ──────────────────────────────────────────────
                """)
                input(f"  Press ENTER when ready "
                      f"for {remaining} ear ...")

    # ── Generate binaural if both ears complete ────────
    both_done = all(
        session.phase_complete(s, PHASE_6)
        for s in ["L", "R"]
    )
    if both_done and not os.path.exists(OUTPUT_WAV_B):
        print("\n  Generating binaural remedy ...")
        generate_binaural(session)
    elif both_done:
        r = ask(
            f"Binaural file exists ({OUTPUT_WAV_B}). "
            f"Regenerate? (Y/N):",
            valid={"Y", "N"}
        )
        if r == "Y":
            generate_binaural(session)

    # ── Final prescription summary ─────────────────────
    print("""
  ╔═════════════════════════════════════════════════════╗
  ║   CALIBRATION COMPLETE — PRESCRIPTION SUMMARY       ║
  ╚══════════════════════════════════════════���══════════╝
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

    print("  REMEDY FILES:")
    for fname in [OUTPUT_WAV_L, OUTPUT_WAV_R,
                  OUTPUT_WAV_B]:
        if os.path.exists(fname):
            print(f"    {fname}")

    print("""
  TO USE:
    Play remedy_binaural.wav on loop
    through headphones while sleeping.
    Volume: barely audible.

  RE-CALIBRATE:
    Run again when efficacy changes.
    Answer Y to resume → N to start fresh.
    Re-calibration: 25–35 minutes.

  SESSION LOG:
    """)
    print(f"    {LOG_FILE}\n")
    session.save()


if __name__ == "__main__":
    main()
