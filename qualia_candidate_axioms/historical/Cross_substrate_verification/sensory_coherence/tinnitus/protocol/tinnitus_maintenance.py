"""
TINNITUS PRESCRIPTION MAINTENANCE TOOL
OC-TINNITUS-001 — OrganismCore
Eric Robert Lawson — 2026-03-23

Reads the calibration JSON produced by tinnitus_calibration.py.
Runs a fast daily drift-correction protocol.

TOPOLOGY:
  The initial calibration established an origin point:
    FA  — false attractor frequency (Hz)
    φ   — cancellation phase (degrees)
    FR  — residual resonant frequency (Hz)

  This tool probes the space immediately surrounding
  that origin using small radial steps. The residual
  tinnitus volume when the remedy plays is the gradient
  signal — the perceptual encoding of distance between
  the current prescription and the true current attractor
  position. Like the beat between two mismatched guitar
  strings. The beat encodes the mismatch. You adjust
  until the beat disappears.

STRUCTURE:
  Step 1 — Load prescription from calibration JSON.
  Step 2 — Play current remedy. Assess residual volume.
            No drift: done. Sleep.
            Drift detected: continue.
  Step 3 — Estimate magnitude from residual level.
            Sets radial step size r.
  Step 4 — Radial sweep: numbered tones around origin.
            Person picks best number or reports none.
            Drill into that region. Repeat until locked.
  Step 5 — If frequency and phase both need adjustment:
            handle one axis at a time.
            If unresolvable in two rounds: escalate
            to full recalibration recommendation.
  Step 6 — Lock new values. Regenerate remedy WAV.
            Log the drift entry.

USAGE:
  python tinnitus_maintenance.py
  python tinnitus_maintenance.py --log tinnitus_calibration_log.json

INSTALL:
  pip install sounddevice numpy scipy
"""

import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
import time
import datetime
import json
import os
import sys
import argparse

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SAMPLE_RATE        = 44100
DEFAULT_LOG_FILE   = "tinnitus_calibration_log.json"
MAINTENANCE_LOG    = "tinnitus_maintenance_log.json"
OUTPUT_WAV_L       = "remedy_left.wav"
OUTPUT_WAV_R       = "remedy_right.wav"
OUTPUT_WAV_B       = "remedy_binaural.wav"

FADE_MS            = 80
POST_TONE_SETTLE_S = 5

# Maintenance tone duration — shorter than calibration.
# The attractor position is already known. We are
# checking proximity, not mapping unknown territory.
# 8 seconds is sufficient for the comparison signal
# to interact with the attractor at close range.
MAINTENANCE_TONE_S = 8

# Radial step sizes by drift magnitude estimate.
# Small: fine tuning. Medium: moderate drift.
# Large: significant drift — boundary of maintenance.
RADIAL_HZ = {
    "SMALL":  50,
    "MEDIUM": 150,
    "LARGE":  350,
}
RADIAL_DEG = {
    "SMALL":  15,
    "MEDIUM": 35,
    "LARGE":  60,
}

AMPLITUDE = 0.10

# ═══════════════════════════════════════════════════════════
# SIGNAL GENERATION — shared with calibration script
# ═══════════════════════════════════════════════════════════

def make_tone(freq_hz, duration_s,
              amplitude=None,
              phase_deg=0.0,
              sr=SAMPLE_RATE):
    if amplitude is None:
        amplitude = AMPLITUDE
    n      = int(sr * duration_s)
    t      = np.linspace(0, duration_s, n, endpoint=False)
    ph     = np.deg2rad(phase_deg)
    sig    = amplitude * np.sin(2 * np.pi * freq_hz * t + ph)
    fade_n = min(int(FADE_MS * sr / 1000), n // 4)
    sig[:fade_n]  *= np.linspace(0, 1, fade_n)
    sig[-fade_n:] *= np.linspace(1, 0, fade_n)
    return sig.astype(np.float32)


def make_pink_noise(duration_s, amplitude=0.03,
                    sr=SAMPLE_RATE):
    n   = int(sr * duration_s)
    t   = np.linspace(0, duration_s, n, endpoint=False)
    sig = np.zeros(n, dtype=np.float32)
    for i, f in enumerate([125, 250, 500, 1000,
                            2000, 4000, 8000]):
        a  = amplitude / (i + 1) ** 0.5
        ph = np.random.uniform(0, 2 * np.pi)
        sig += (a * np.sin(2 * np.pi * f * t + ph)
                ).astype(np.float32)
    return sig


def play_ear(sig, side):
    z      = np.zeros_like(sig)
    stereo = (np.stack([sig, z], axis=1)
              if side == "L"
              else np.stack([z, sig], axis=1))
    sd.play(stereo, SAMPLE_RATE)
    sd.wait()


def play_both(sig_l, sig_r):
    n = max(len(sig_l), len(sig_r))
    l = np.zeros(n, dtype=np.float32)
    r = np.zeros(n, dtype=np.float32)
    l[:len(sig_l)] = sig_l
    r[:len(sig_r)] = sig_r
    sd.play(np.stack([l, r], axis=1), SAMPLE_RATE)
    sd.wait()


def build_remedy_signal(fa, fr, phase_deg, amplitude,
                         duration_s):
    """
    Build a single-ear remedy signal:
      Layer 1: pink noise, FA notched
      Layer 2: anti-signal at FA, calibrated phase
      Layer 3: FR boost
    """
    n      = int(SAMPLE_RATE * duration_s)
    t      = np.linspace(0, duration_s, n, endpoint=False)
    pink   = make_pink_noise(duration_s, amplitude=0.03)
    pink  -= (0.015 *
              np.sin(2 * np.pi * fa * t +
                     np.random.uniform(0, 2 * np.pi))
              ).astype(np.float32)
    ph_rad = np.deg2rad(phase_deg)
    anti   = (amplitude * 0.85 *
               np.sin(2 * np.pi * fa * t + ph_rad)
               ).astype(np.float32)
    boost  = np.zeros(n, dtype=np.float32)
    if fr is not None and fr != fa:
        boost = (amplitude * 0.38 *
                 np.sin(2 * np.pi * fr * t)
                 ).astype(np.float32)
    combined = np.clip(pink + anti + boost, -1.0, 1.0)
    fade_s   = int(3 * SAMPLE_RATE)
    combined[:fade_s]  *= np.linspace(
        0, 1, fade_s).astype(np.float32)
    combined[-fade_s:] *= np.linspace(
        1, 0, fade_s).astype(np.float32)
    return combined

# ═══════════════════════════════════════════════════════════
# PRESCRIPTION — load from calibration JSON
# ═══════════════════════════════════════════════════════════

class Prescription:
    """
    Loaded from the calibration log JSON.
    Holds current FA, FR, phase per ear.
    Tracks adjustments made during this session.
    """

    def __init__(self, log_file):
        self.log_file  = log_file
        self.timestamp = datetime.datetime.now(
            ).isoformat()
        self._raw      = self._load(log_file)
        self.left      = self._extract("left")
        self.right     = self._extract("right")

    def _load(self, path):
        if not os.path.exists(path):
            print(f"\n  ERROR: Log file not found: {path}")
            print("  Run tinnitus_calibration.py first.")
            sys.exit(1)
        with open(path) as f:
            return json.load(f)

    def _extract(self, side_key):
        raw = self._raw.get(side_key, {})
        return {
            "fa_hz":     raw.get("fa_hz"),
            "fr_hz":     raw.get("fr_hz"),
            "phase_deg": raw.get("phase_deg", 180.0),
            "amplitude": raw.get("amplitude", AMPLITUDE),
            "tone_duration_s": raw.get(
                "tone_duration_s", MAINTENANCE_TONE_S),
            # Maintenance adjustments — populated during
            # this session, applied to WAV at the end.
            "fa_adjusted":    None,
            "phase_adjusted": None,
            "fr_adjusted":    None,
        }

    def ear(self, side):
        return self.left if side == "L" else self.right

    def current_fa(self, side):
        e = self.ear(side)
        return (e["fa_adjusted"]
                if e["fa_adjusted"] is not None
                else e["fa_hz"])

    def current_phase(self, side):
        e = self.ear(side)
        return (e["phase_adjusted"]
                if e["phase_adjusted"] is not None
                else e["phase_deg"])

    def current_fr(self, side):
        e = self.ear(side)
        return (e["fr_adjusted"]
                if e["fr_adjusted"] is not None
                else e["fr_hz"])

    def has_calibration(self, side):
        return self.ear(side)["fa_hz"] is not None

    def summary(self, side):
        e    = self.ear(side)
        fa_o = e["fa_hz"]
        ph_o = e["phase_deg"]
        fr_o = e["fr_hz"]
        fa_n = self.current_fa(side)
        ph_n = self.current_phase(side)
        fr_n = self.current_fr(side)
        lines = [f"  {side} EAR PRESCRIPTION:"]
        lines.append(
            f"    FA  : {fa_o} Hz"
            + (f"  →  {fa_n} Hz  "
               f"(Δ {fa_n - fa_o:+d} Hz)"
               if fa_n != fa_o else "  (unchanged)"))
        lines.append(
            f"    φ   : {ph_o}°"
            + (f"  →  {ph_n}°  "
               f"(Δ {ph_n - ph_o:+d}°)"
               if ph_n != ph_o else "  (unchanged)"))
        lines.append(
            f"    FR  : {fr_o} Hz"
            + (f"  →  {fr_n} Hz"
               if fr_n != fr_o else "  (unchanged)"))
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════
# MAINTENANCE LOG
# ═══════════════════════════════════════════════════════════

def load_maintenance_log():
    if not os.path.exists(MAINTENANCE_LOG):
        return []
    with open(MAINTENANCE_LOG) as f:
        return json.load(f)


def save_maintenance_log(entries):
    with open(MAINTENANCE_LOG, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"  [Maintenance log saved → {MAINTENANCE_LOG}]")


def append_maintenance_entry(side, ear_data,
                              fa_old, fa_new,
                              phase_old, phase_new,
                              fr_old, fr_new,
                              drift_magnitude,
                              rounds_taken,
                              escalated):
    entries = load_maintenance_log()
    entries.append({
        "timestamp":      datetime.datetime.now(
            ).isoformat(),
        "ear":            side,
        "fa_old":         fa_old,
        "fa_new":         fa_new,
        "delta_fa_hz":    (fa_new - fa_old
                           if fa_new and fa_old
                           else 0),
        "phase_old":      phase_old,
        "phase_new":      phase_new,
        "delta_phase_deg":(phase_new - phase_old
                           if phase_new and phase_old
                           else 0),
        "fr_old":         fr_old,
        "fr_new":         fr_new,
        "drift_magnitude":drift_magnitude,
        "rounds_taken":   rounds_taken,
        "escalated":      escalated,
    })
    save_maintenance_log(entries)


def show_drift_history():
    entries = load_maintenance_log()
    if not entries:
        print("  No maintenance history yet.")
        return
    print(f"\n  ── DRIFT HISTORY "
          f"(last {min(10, len(entries))} sessions) ──")
    print(f"  {'DATE':<12} {'EAR':<4} "
          f"{'FA OLD':>8} {'FA NEW':>8} {'ΔFA':>6} "
          f"{'φ OLD':>6} {'φ NEW':>6} {'Δφ':>5}")
    print("  " + "─" * 62)
    for e in entries[-10:]:
        ts   = e["timestamp"][:10]
        ear  = e.get("ear", "?")
        fa_o = e.get("fa_old", "?")
        fa_n = e.get("fa_new", "?")
        d_fa = e.get("delta_fa_hz", 0)
        ph_o = e.get("phase_old", "?")
        ph_n = e.get("phase_new", "?")
        d_ph = e.get("delta_phase_deg", 0)
        print(f"  {ts:<12} {ear:<4} "
              f"{str(fa_o):>8} {str(fa_n):>8} "
              f"{d_fa:>+6} "
              f"{str(ph_o):>6} {str(ph_n):>6} "
              f"{d_ph:>+5}")
    print()

# ═══════════════════════════════════════════════════════════
# INPUT HELPERS
# ═══════════════════════════════════════════════════════════

def ask(prompt, valid=None):
    while True:
        raw = input(f"  {prompt} ").strip().upper()
        if valid is None or raw in valid:
            return raw
        print(f"  → Enter one of: "
              f"{', '.join(sorted(valid))}")


def ask_number(prompt, lo, hi):
    """Ask for an integer in [lo, hi] or 0 for none."""
    while True:
        raw = input(f"  {prompt} ").strip()
        if raw == "0":
            return 0
        try:
            n = int(raw)
            if lo <= n <= hi:
                return n
        except ValueError:
            pass
        print(f"  → Enter a number {lo}–{hi}, "
              f"or 0 for none.")


def confirm_baseline():
    """Wait for person to confirm baseline restored."""
    print("  Confirm baseline before next tone.")
    input("  Press ENTER when tinnitus is back "
          "to normal baseline ...")

# ═══════════════════════════════════════════════════════════
# VOLUME CHECK — lightweight version
# ═══════════════════════════════════════════════════════════

def quick_volume_check(amplitude):
    global AMPLITUDE
    AMPLITUDE = amplitude
    print("""
  ── VOLUME CHECK ────────────────────────────────
  Playing reference tone. Confirm comfortable.
  ─────────────────────────────────────────────────
    """)
    while True:
        input("  Playing 6000 Hz reference — ENTER ...")
        tone   = make_tone(6000.0, 3, amplitude=AMPLITUDE)
        stereo = np.stack([tone, tone], axis=1)
        sd.play(stereo, SAMPLE_RATE)
        sd.wait()
        r = ask("Comfortable? (Y / LOUDER / QUIETER):",
                valid={"Y", "LOUDER", "QUIETER"})
        if r == "Y":
            break
        elif r == "LOUDER":
            AMPLITUDE = min(AMPLITUDE * 1.4, 0.5)
        elif r == "QUIETER":
            AMPLITUDE = max(AMPLITUDE * 0.75, 0.01)
        print(f"  Amplitude → {AMPLITUDE:.3f}")
    return AMPLITUDE

# ═══════════════════════════════════════════════════════════
# STEP 1 — ASSESS CURRENT REMEDY
# ═══════════════════════════════════════════════════════════

def assess_current_remedy(rx, sides):
    """
    Play current remedy for each active ear.
    Ask person to rate residual tinnitus
    relative to their best remembered cancellation.

    Returns: dict of side → drift_magnitude
      "NONE"   — no drift, prescription current
      "SMALL"  — faint residual, fine adjustment
      "MEDIUM" — moderate residual, larger step
      "LARGE"  — near-baseline residual, may need
                 full recalibration
    """
    print("""
  ┌─────────────────────────────────────────────┐
  │  STEP 1: ASSESS CURRENT REMEDY              │
  │                                             │
  │  The remedy will play for 60 seconds.       │
  │  Notice how much the tinnitus is reduced    │
  │  compared to WITHOUT the remedy.            │
  │                                             │
  │  Compare to the BEST night you have had     │
  │  with the remedy — your reference point.   │
  │                                             │
  │  You will be asked to rate the residual     │
  │  tinnitus on a simple scale.                │
  └─────────────────────────────────────────────┘
    """)

    drift_map = {}

    for side in sides:
        if not rx.has_calibration(side):
            continue
        fa    = rx.current_fa(side)
        fr    = rx.current_fr(side)
        phase = rx.current_phase(side)
        amp   = rx.ear(side)["amplitude"]

        print(f"\n  Playing current {side} ear remedy "
              f"(60 seconds) ...")
        sig = build_remedy_signal(fa, fr, phase,
                                   amp, 60)
        play_ear(sig, side)

        print(f"""
  Rate the residual tinnitus while the remedy
  was playing:

    1 — NONE: tinnitus was fully suppressed
              or barely noticeable.
              Prescription is current.

    2 — FAINT: tinnitus was quieter than without
               the remedy, but not as quiet as
               your best night.
               Small drift. Fine adjustment needed.

    3 — MODERATE: tinnitus was somewhat quieter
                  than without the remedy.
                  Noticeable degradation from best.
                  Medium adjustment needed.

    4 — LOUD: tinnitus barely quieter than without
              the remedy. Prescription has drifted
              significantly.
              Full recalibration may be needed.
        """)

        r = ask_number("Enter 1 / 2 / 3 / 4:", 1, 4)

        drift_map[side] = {
            1: "NONE",
            2: "SMALL",
            3: "MEDIUM",
            4: "LARGE",
        }[r]

        print(f"  {side} ear drift estimate: "
              f"{drift_map[side]}")

    return drift_map

# ═══════════════════════════════════════════════════════════
# STEP 2 — RADIAL FREQUENCY SWEEP
# Numbered tones around current FA.
# Person picks best number or 0 for none.
# Drills into that region until locked.
# ═══════════════════════════════════════════════════════════

def radial_frequency_sweep(rx, side, magnitude):
    """
    Probe frequencies around current FA at radius r.

    Presents tones as numbered options.
    Person picks the number that felt best,
    or 0 if none felt better than current.

    On a pick: re-centre on that frequency,
    halve r, repeat. Continue until person
    reports 0 (current centre is optimum)
    or step size falls below 10 Hz.

    Returns: new_fa (int Hz), changed (bool)
    """
    fa    = rx.current_fa(side)
    amp   = rx.ear(side)["amplitude"]
    play  = lambda s: play_ear(s, side)
    r     = RADIAL_HZ[magnitude]
    tone_dur = MAINTENANCE_TONE_S

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  FREQUENCY SWEEP — {side} EAR                      │
  │  Current FA: {fa} Hz                      │
  │  Radial step: {r} Hz                       │
  │                                             │
  │  Tones will play in sequence, numbered.     │
  │  Pick the number that felt BEST —           │
  │  most reduction, most relief.               │
  │  Pick 0 if none felt better than current.  │
  └─────────────────────────────────────────────┘
    """)

    current_fa = fa
    changed    = False
    rounds     = 0

    while r >= 10 and rounds < 6:
        rounds += 1

        # Build probe frequencies: centre ± r, ± r/2
        # Presented as a numbered list.
        # Includes current FA as one of the options
        # so person can compare directly.
        candidates = sorted(set([
            int(current_fa - r),
            int(current_fa - r // 2),
            int(current_fa),
            int(current_fa + r // 2),
            int(current_fa + r),
        ]))
        # Clamp to audible range
        candidates = [c for c in candidates
                      if 200 <= c <= 16000]

        print(f"\n  Round {rounds} — "
              f"probing around {current_fa} Hz "
              f"(step ±{r} Hz)")
        print(f"  Centre frequency marked with  ←\n")

        # Play each numbered tone
        for i, freq in enumerate(candidates, 1):
            marker = "  ←  (current)" \
                     if freq == current_fa else ""
            print(f"  [{i}]  {freq} Hz{marker}")
            input(f"  ENTER to play [{i}] ...")
            tone = make_tone(freq, tone_dur,
                             amplitude=amp)
            play(tone)
            print(f"  [Settling {POST_TONE_SETTLE_S}s ...]")
            time.sleep(POST_TONE_SETTLE_S)
            confirm_baseline()

        print()
        choice = ask_number(
            f"Which number felt BEST? "
            f"(1–{len(candidates)}, or 0 for none):",
            0, len(candidates)
        )

        if choice == 0:
            print(f"  No improvement detected at "
                  f"this radius.")
            print(f"  Current FA confirmed: "
                  f"{current_fa} Hz")
            break

        selected = candidates[choice - 1]

        if selected == current_fa:
            print(f"  Current position confirmed optimal.")
            break

        print(f"  Moving to {selected} Hz  "
              f"(Δ {selected - current_fa:+d} Hz)")
        current_fa = selected
        changed    = True
        r          = max(r // 2, 10)

        print(f"  Narrowing step to ±{r} Hz ...")

    if changed:
        print(f"\n  Frequency adjusted: "
              f"{fa} Hz  →  {current_fa} Hz  "
              f"(Δ {current_fa - fa:+d} Hz)")
    else:
        print(f"\n  Frequency unchanged: {fa} Hz")

    return current_fa, changed

# ═══════════════════════��═══════════════════════════════════
# STEP 3 — RADIAL PHASE SWEEP
# Same numbered approach in phase space.
# ═══════════════════════════════════════════��═══════════════

def radial_phase_sweep(rx, side, magnitude, fa):
    """
    Probe phase angles around current φ at radius r_deg.

    Same numbered selection as frequency sweep.
    Returns: new_phase (int degrees), changed (bool)
    """
    phase    = rx.current_phase(side)
    amp      = rx.ear(side)["amplitude"]
    play     = lambda s: play_ear(s, side)
    r        = RADIAL_DEG[magnitude]
    tone_dur = MAINTENANCE_TONE_S

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  PHASE SWEEP — {side} EAR                         │
  │  Current φ: {phase}°                          │
  │  FA: {fa} Hz                               │
  │  Radial step: {r}°                          │
  │                                             │
  │  Tones at same frequency, different phase.  │
  │  Pick the number that felt BEST.            │
  │  Pick 0 if none felt better than current.  │
  └─────────────────────────────────────────────┘
    """)

    current_phase = phase
    changed       = False
    rounds        = 0

    while r >= 5 and rounds < 5:
        rounds += 1

        candidates = sorted(set([
            int((current_phase - r) % 360),
            int((current_phase - r // 2) % 360),
            int(current_phase % 360),
            int((current_phase + r // 2) % 360),
            int((current_phase + r) % 360),
        ]))

        print(f"\n  Round {rounds} — "
              f"probing around {current_phase}° "
              f"(step ±{r}°)")
        print(f"  Centre phase marked with  ←\n")

        for i, ph in enumerate(candidates, 1):
            marker = "  ←  (current)" \
                     if ph == current_phase % 360 \
                     else ""
            print(f"  [{i}]  {ph}°{marker}")
            input(f"  ENTER to play [{i}] ...")
            tone = make_tone(fa, tone_dur,
                             amplitude=amp,
                             phase_deg=ph)
            play(tone)
            print(f"  [Settling {POST_TONE_SETTLE_S}s ...]")
            time.sleep(POST_TONE_SETTLE_S)
            confirm_baseline()

        print()
        choice = ask_number(
            f"Which number felt BEST? "
            f"(1–{len(candidates)}, or 0 for none):",
            0, len(candidates)
        )

        if choice == 0:
            print(f"  No improvement at this radius.")
            print(f"  Current phase confirmed: "
                  f"{current_phase}°")
            break

        selected = candidates[choice - 1]

        if selected == current_phase % 360:
            print(f"  Current phase confirmed optimal.")
            break

        print(f"  Moving to {selected}°  "
              f"(Δ {selected - current_phase:+d}°)")
        current_phase = selected
        changed       = True
        r             = max(r // 2, 5)

        print(f"  Narrowing step to ±{r}° ...")

    if changed:
        print(f"\n  Phase adjusted: "
              f"{phase}°  →  {current_phase}°")
    else:
        print(f"\n  Phase unchanged: {phase}°")

    return current_phase, changed

# ═══════════════════════════════════════════════════════════
# STEP 4 — VERIFY ADJUSTMENT
# Play updated prescription, confirm improvement.
# ═══════════════════════════════════════════════════════════

def verify_adjustment(rx, side):
    """
    Play updated prescription for 30 seconds.
    Ask whether it is better than before the
    maintenance session started.
    Returns: True if improved, False if not.
    """
    fa    = rx.current_fa(side)
    fr    = rx.current_fr(side)
    phase = rx.current_phase(side)
    amp   = rx.ear(side)["amplitude"]

    print(f"\n  Playing updated prescription "
          f"({side} ear, 30s) ...")
    print(f"  FA={fa} Hz  φ={phase}°  FR={fr} Hz")
    sig = build_remedy_signal(fa, fr, phase, amp, 30)
    play_ear(sig, side)

    r = ask(
        "Is the tinnitus reduction BETTER than "
        "before this session? (Y / N / SAME):",
        valid={"Y", "N", "SAME"}
    )
    return r

# ═══════════════════════════════════════════════════════════
# WAV REGENERATION
# ═══════════════════════════════════════════════════════════

def regenerate_wavs(rx, sides):
    """
    Regenerate remedy WAV files from updated prescription.
    Overwrites existing files.
    """
    print("\n  Regenerating remedy files ...")
    duration_minutes = 60

    for side in sides:
        if not rx.has_calibration(side):
            continue
        fa    = rx.current_fa(side)
        fr    = rx.current_fr(side)
        phase = rx.current_phase(side)
        amp   = rx.ear(side)["amplitude"]

        sig       = build_remedy_signal(
            fa, fr, phase, amp,
            duration_minutes * 60)
        out_int16 = (sig * 32767).astype(np.int16)
        fname     = (OUTPUT_WAV_L if side == "L"
                     else OUTPUT_WAV_R)
        wavfile.write(fname, SAMPLE_RATE, out_int16)
        print(f"  Saved: {fname}  "
              f"(FA={fa} Hz  φ={phase}°  FR={fr} Hz)")

    # Binaural — regenerate if both ears present
    both_calibrated = all(
        rx.has_calibration(s) for s in ["L", "R"]
    )
    if both_calibrated and len(sides) >= 1:
        dur_s = duration_minutes * 60
        n     = int(SAMPLE_RATE * dur_s)
        t     = np.linspace(0, dur_s, n, endpoint=False)

        def chan(side_key):
            e   = rx.ear(side_key)
            fa  = rx.current_fa(side_key)
            fr  = rx.current_fr(side_key)
            ph  = rx.current_phase(side_key)
            amp = e["amplitude"]
            return build_remedy_signal(
                fa, fr, ph, amp, dur_s)

        l_chan    = chan("L")
        r_chan    = chan("R")
        stereo    = np.stack([l_chan, r_chan], axis=1)
        out_int16 = (stereo * 32767).astype(np.int16)
        wavfile.write(OUTPUT_WAV_B, SAMPLE_RATE,
                      out_int16)
        print(f"  Saved: {OUTPUT_WAV_B}")

# ═══════════════════════════════════════════════════════════
# ESCALATION — recommend full recalibration
# ═══════════════════════════════════════════════════════════

def escalate(side):
    print(f"""
  ╔═════════════════════════════════════════════╗
  ║  MAINTENANCE UNRESOLVED — {side} EAR               ║
  ╠═════════════════════════════════════════════╣
  ║                                             ║
  ║  Two rounds of radial adjustment did not    ║
  ║  restore cancellation quality.              ║
  ║                                             ║
  ║  The attractor has likely drifted beyond    ║
  ║  the maintenance radius.                    ║
  ║                                             ║
  ║  RECOMMENDED ACTION:                        ║
  ║  Run tinnitus_calibration.py                ║
  ║  Answer N to start fresh.                   ║
  ║  Full Phase 2 gradient descent from         ║
  ║  current FA as starting point.              ║
  ║  Takes 25–35 minutes.                       ║
  ║                                             ║
  ║  Current prescription kept unchanged.       ║
  ║  Use existing remedy until recalibration.   ║
  ╚═════════════════════════════════════════════╝
    """)

# ═══════════════════════════════════════════════════════════
# MAIN MAINTENANCE LOOP — ONE EAR
# ═══════════════════════════════════════════════════════════

def maintain_ear(rx, side, magnitude):
    """
    Run the full maintenance protocol for one ear.

    1. Radial frequency sweep — find new FA if drifted.
    2. Radial phase sweep — find new φ if drifted.
    3. Verify combined adjustment.
    4. If unresolved after 2 rounds: escalate.

    Updates rx in place with adjusted values.
    Returns: escalated (bool)
    """
    if magnitude == "NONE":
        print(f"\n  {side} ear: no drift detected. "
              "Prescription current.")
        return False

    if magnitude == "LARGE":
        print(f"\n  {side} ear: large drift detected.")
        print("  Attempting maintenance protocol.")
        print("  If unresolved, full recalibration "
              "will be recommended.")

    fa_original    = rx.current_fa(side)
    phase_original = rx.current_phase(side)
    escalated      = False

    for round_num in range(1, 3):
        print(f"\n  ── Round {round_num} of 2 "
              f"({side} ear) ──────────────────────")

        # Frequency axis
        new_fa, fa_changed = radial_frequency_sweep(
            rx, side, magnitude)
        rx.ear(side)["fa_adjusted"] = new_fa

        # Phase axis
        new_phase, phase_changed = radial_phase_sweep(
            rx, side, magnitude, new_fa)
        rx.ear(side)["phase_adjusted"] = new_phase

        # Verify
        result = verify_adjustment(rx, side)

        if result == "Y":
            print(f"\n  ✓ Adjustment confirmed. "
                  f"{side} ear updated.")
            break

        if result == "SAME":
            print(f"\n  No improvement detected.")
            if round_num == 1:
                print("  Running second round with "
                      "smaller step ...")
                # Reduce magnitude for second round
                magnitude = {
                    "LARGE":  "MEDIUM",
                    "MEDIUM": "SMALL",
                    "SMALL":  "SMALL",
                }[magnitude]
                continue
            else:
                escalated = True
                escalate(side)
                # Revert to original values
                rx.ear(side)["fa_adjusted"] = \
                    fa_original
                rx.ear(side)["phase_adjusted"] = \
                    phase_original
                break

        if result == "N":
            print(f"\n  Adjustment made things worse.")
            if round_num == 1:
                print("  Reverting and trying again "
                      "with smaller step ...")
                rx.ear(side)["fa_adjusted"] = \
                    fa_original
                rx.ear(side)["phase_adjusted"] = \
                    phase_original
                magnitude = {
                    "LARGE":  "MEDIUM",
                    "MEDIUM": "SMALL",
                    "SMALL":  "SMALL",
                }[magnitude]
                continue
            else:
                escalated = True
                escalate(side)
                rx.ear(side)["fa_adjusted"] = \
                    fa_original
                rx.ear(side)["phase_adjusted"] = \
                    phase_original
                break

    return escalated

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Tinnitus prescription maintenance tool"
    )
    parser.add_argument(
        "--log",
        default=DEFAULT_LOG_FILE,
        help=f"Path to calibration log JSON "
             f"(default: {DEFAULT_LOG_FILE})"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show drift history and exit"
    )
    args = parser.parse_args()

    print("""
  ╔═════════════════════════════════════════════════════╗
  ║   TINNITUS PRESCRIPTION MAINTENANCE                 ║
  ║   OC-TINNITUS-001 — OrganismCore                    ║
  ║   Eric Robert Lawson — 2026-03-23                   ║
  ╠═════════════════════════════════════════════════════╣
  ║                                                     ║
  ║   Daily drift correction for calibrated             ║
  ║   tinnitus prescription.                            ║
  ║                                                     ║
  ║   Reads: tinnitus_calibration_log.json              ║
  ║   Updates: remedy WAV files if drift found.         ║
  ║   Logs: tinnitus_maintenance_log.json               ║
  ║                                                     ║
  ║   Duration: 3–8 minutes typical.                    ║
  ║                                                     ║
  ║   INSTALL: pip install sounddevice numpy scipy      ║
  ╚═════════════════════════════════════════════════════╝
    """)

    if args.history:
        show_drift_history()
        sys.exit(0)

    # ── Load prescription ──────────────────────────────
    print(f"  Loading prescription from: {args.log}")
    rx = Prescription(args.log)

    # ── Which ears are calibrated? ───────────��─────────
    calibrated = [s for s in ["L", "R"]
                  if rx.has_calibration(s)]

    if not calibrated:
        print("\n  No calibrated ears found in log.")
        print("  Run tinnitus_calibration.py first.")
        sys.exit(1)

    print("\n  Calibrated ears found:")
    for s in calibrated:
        e = rx.ear(s)
        print(f"    {s}: FA={e['fa_hz']} Hz  "
              f"φ={e['phase_deg']}°  "
              f"FR={e['fr_hz']} Hz")

    if len(calibrated) == 2:
        r = ask("\n  Maintain which ears? "
                "(L / R / B):",
                valid={"L", "R", "B"})
        sides = (["L"] if r == "L"
                 else ["R"] if r == "R"
                 else ["L", "R"])
    else:
        sides = calibrated
        print(f"\n  Maintaining: {sides[0]} ear")

    # ── Show drift history ─────────────────────────────
    show_drift_history()

    # ── Volume check ──────────────────────────────────
    amp = rx.ear(sides[0])["amplitude"]
    amp = quick_volume_check(amp)
    for s in sides:
        rx.ear(s)["amplitude"] = amp

    # ── Step 1: Assess current remedy ─────────────────
    drift_map = assess_current_remedy(rx, sides)

    # ── Check if any drift ────────────────────────────
    all_clear = all(v == "NONE"
                    for v in drift_map.values())
    if all_clear:
        print("""
  ╔═════════════════════════════════════════════╗
  ║  PRESCRIPTION CURRENT — NO ADJUSTMENT       ║
  ║  Cancellation quality unchanged.            ║
  ║  No WAV regeneration needed.                ║
  ║  Sleep well.                                ║
  ╚═════════════════════════════════════════════╝
        """)
        sys.exit(0)

    # ── Step 2–4: Maintenance per ear ─────────────────
    escalated_ears = []

    for side in sides:
        magnitude = drift_map.get(side, "NONE")
        if magnitude == "NONE":
            continue

        print(f"\n  ── Maintaining {side} ear "
              f"(drift: {magnitude}) ──────────────")
        escalated = maintain_ear(rx, side, magnitude)
        if escalated:
            escalated_ears.append(side)

    # ── Regenerate WAVs for non-escalated ears ─────────
    adjusted_sides = [s for s in sides
                      if s not in escalated_ears]
    any_adjusted   = any(
        rx.ear(s)["fa_adjusted"] is not None or
        rx.ear(s)["phase_adjusted"] is not None
        for s in adjusted_sides
    )

    if any_adjusted:
        regenerate_wavs(rx, adjusted_sides)

    # ── Log entries ────────────────────────────────────
    for side in sides:
        e         = rx.ear(side)
        escalated = side in escalated_ears
        append_maintenance_entry(
            side        = side,
            ear_data    = e,
            fa_old      = e["fa_hz"],
            fa_new      = rx.current_fa(side),
            phase_old   = e["phase_deg"],
            phase_new   = rx.current_phase(side),
            fr_old      = e["fr_hz"],
            fr_new      = rx.current_fr(side),
            drift_magnitude = drift_map.get(side, "NONE"),
            rounds_taken    = 1,
            escalated       = escalated,
        )

    # ── Final summary ──────────────────────────────────
    print("""
  ╔═════════════════════════════════════════════════════╗
  ║   MAINTENANCE COMPLETE                              ║
  ╚═════════════════════════════════════════════════════╝
    """)
    for side in sides:
        print(rx.summary(side))
        print()

    if escalated_ears:
        print(f"  ESCALATED (full recalibration needed):")
        for s in escalated_ears:
            print(f"    {s} ear — run "
                  f"tinnitus_calibration.py")
        print()

    print("  REMEDY FILES:")
    for fname in [OUTPUT_WAV_L, OUTPUT_WAV_R,
                  OUTPUT_WAV_B]:
        if os.path.exists(fname):
            print(f"    {fname}")

    print("""
  Play remedy_binaural.wav on loop while sleeping.
  Volume: barely audible.
    """)


if __name__ == "__main__":
    main()
