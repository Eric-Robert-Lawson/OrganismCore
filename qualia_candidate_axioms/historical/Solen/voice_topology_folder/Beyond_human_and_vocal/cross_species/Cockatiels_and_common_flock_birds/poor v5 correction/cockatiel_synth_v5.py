import numpy as np
from scipy.io import wavfile
import os

# ─────────────────────────────────────────────────────────────
# COCKATIEL CONTACT CALL SYNTHESIZER — V5 CORRECTED
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
#
# The structural invariant shape is confirmed correct
# from 434 calls across 38 files:
#
#   F0 SHAPE: ramp-and-hold
#     Starts at 0% of range
#     Sweeps up through first 77% of call duration
#     Peaks at t=77%, holds briefly
#     Slight rolloff to 72% of range at end
#
#   AMPLITUDE SHAPE: asymmetric bell
#     Onset at 17% amplitude
#     Brief dip to 0% (pre-call breath artifact)
#     Rises to peak at t=48% of duration
#     Gradual decay to 23% at end
#
# FREQUENCY CORRECTION:
#   Ridge tracker was following 2nd/3rd harmonic.
#   Fundamental of cockatiel contact call: 500-1200 Hz.
#   Shape is rescaled to correct absolute range.
#   Shape geometry is preserved exactly.
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE  = 44100
OUTPUT_DIR   = os.path.dirname(os.path.abspath(__file__))

# ── STRUCTURAL INVARIANT — from V5 analysis ───────────────────
# These values are the actual PC1 shape from 434 calls.
# Do not change — these are the measured invariant.

F0_SHAPE = np.array([
    0.000, 0.044, 0.102, 0.173, 0.261, 0.347, 0.438,
    0.527, 0.616, 0.681, 0.716, 0.740, 0.775, 0.802,
    0.839, 0.877, 0.899, 0.917, 0.943, 0.964, 0.977,
    0.977, 0.982, 0.985, 1.000, 0.993, 0.959, 0.913,
    0.867, 0.819, 0.765, 0.719
])

AMP_SHAPE = np.array([
    0.175, 0.060, 0.012, 0.006, 0.000, 0.005, 0.077,
    0.180, 0.261, 0.343, 0.457, 0.565, 0.715, 0.847,
    0.933, 1.000, 0.985, 0.960, 0.924, 0.867, 0.764,
    0.663, 0.575, 0.516, 0.433, 0.380, 0.339, 0.265,
    0.176, 0.105, 0.137, 0.231
])

N_SHAPE_PTS = len(F0_SHAPE)  # 32


def synthesize_contact_call(
        f0_centre_hz,
        f0_range_hz  = 280,   # corpus range / harmonic ratio
                              # 793Hz at 3rd harmonic ÷ 3 ≈ 264Hz
                              # rounded to 280Hz
        duration_ms  = 163,   # corpus median
        h2_ratio     = 0.40,
        h3_ratio     = 0.15,
        sample_rate  = SAMPLE_RATE):
    """
    Synthesize using the confirmed structural invariant shape.

    f0_centre_hz: the mean F0 of this call.
    The shape spans f0_range_hz around that centre,
    starting at (centre - range/2) and peaking at
    (centre + range/2) following the invariant shape.
    """

    n_samples = int(duration_ms * sample_rate / 1000)

    # Rescale F0 shape to absolute Hz
    # Shape 0.0 = f0_centre - f0_range/2
    # Shape 1.0 = f0_centre + f0_range/2
    f0_lo  = f0_centre_hz - f0_range_hz / 2
    f0_hi  = f0_centre_hz + f0_range_hz / 2
    f0_abs = f0_lo + F0_SHAPE * f0_range_hz

    # Interpolate shape to sample length
    f0_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS),
        f0_abs)

    amp_t = np.interp(
        np.linspace(0, N_SHAPE_PTS-1, n_samples),
        np.arange(N_SHAPE_PTS),
        AMP_SHAPE)

    # FM synthesis — phase integrated from trajectory
    phase  = 2 * np.pi * np.cumsum(f0_t) / sample_rate

    signal = (
        np.sin(phase) +
        h2_ratio * np.sin(2 * phase) +
        h3_ratio * np.sin(3 * phase)
    )

    signal = signal * amp_t

    # 5ms fade in/out
    fade = int(0.005 * sample_rate)
    signal[:fade]  *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal * (0.9 / peak)

    return signal, f0_abs


def build_sequence(call, n_repeats=3, gap_ms=800,
                   sample_rate=SAMPLE_RATE):
    gap   = np.zeros(int(gap_ms * sample_rate / 1000))
    parts = []
    for i in range(n_repeats):
        parts.append(call)
        if i < n_repeats - 1:
            parts.append(gap)
    return np.concatenate(parts)


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    print(f"  Saved: {os.path.basename(filename)}"
          f"  ({len(signal)/sample_rate:.2f}s)")


def main():
    print("=" * 65)
    print("OC-OBS-005 — SYNTHESIZER V5 CORRECTED")
    print("OrganismCore — Eric Robert Lawson")
    print("Invariant shape confirmed. Frequency corrected.")
    print("=" * 65)

    print(f"\nStructural invariant shape summary:")
    print(f"  Geometry: ramp-and-hold")
    print(f"  F0 start: {F0_SHAPE[0]:.0%} of range")
    print(f"  F0 peak:  {np.argmax(F0_SHAPE)/31*100:.0f}%"
          f" of call duration")
    print(f"  F0 end:   {F0_SHAPE[-1]:.0%} of range")
    print(f"  Amp peak: "
          f"{np.argmax(AMP_SHAPE)/31*100:.0f}%"
          f" of call duration")
    print(f"  Source:   434 calls, 38 files")

    # ── THREE VARIANTS ────────────────────────────────────────
    # F0 centre anchored to known contact call range
    # LOW  = 650 Hz centre  (range 520–780 Hz)
    # MID  = 820 Hz centre  (range 680–960 Hz)
    # HIGH = 980 Hz centre  (range 840–1120 Hz)

    variants = [
        {
            "name":        "LOW",
            "f0_centre":   650,
            "f0_range":    260,
            "description": "lower register contact call",
        },
        {
            "name":        "MID",
            "f0_centre":   820,
            "f0_range":    280,
            "description": "species centroid contact call",
        },
        {
            "name":        "HIGH",
            "f0_centre":   980,
            "f0_range":    300,
            "description": "upper register contact call",
        },
    ]

    print(f"\nSynthesizing three variants...")
    print(f"{'─'*65}")

    calls = {}
    for v in variants:
        signal, f0_abs = synthesize_contact_call(
            f0_centre_hz = v["f0_centre"],
            f0_range_hz  = v["f0_range"])
        calls[v["name"]] = signal

        print(f"\n  {v['name']} — {v['description']}")
        print(f"    F0 trajectory:  "
              f"{f0_abs[0]:.0f}Hz"
              f" → {f0_abs[np.argmax(F0_SHAPE)]:.0f}Hz"
              f" → {f0_abs[-1]:.0f}Hz")
        print(f"    F0 range:       "
              f"{np.max(f0_abs)-np.min(f0_abs):.0f}Hz")
        print(f"    Duration:       163ms")

        save_wav(signal, os.path.join(OUTPUT_DIR,
            f"v5c_contact_{v['name']}.wav"))
        save_wav(build_sequence(signal),
            os.path.join(OUTPUT_DIR,
            f"v5c_sequence_{v['name']}_3x.wav"))

    # ── FIRST MEETING PROBE ───────────────────────────────────
    print(f"\n{'─'*65}")
    print("Building first meeting probe...")

    gap_2s = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s = np.zeros(int(1.0 * SAMPLE_RATE))

    probe = np.concatenate([
        gap_1s,
        build_sequence(calls["LOW"]),   gap_2s,
        build_sequence(calls["MID"]),   gap_2s,
        build_sequence(calls["HIGH"]),  gap_1s,
    ])

    save_wav(probe, os.path.join(OUTPUT_DIR,
        "v5c_FIRST_MEETING_PROBE.wav"))

    print(f"\n{'='*65}")
    print("Complete.")
    print("Listen to v5c_contact_MID.wav")
    print("You should hear a 163ms call that:")
    print("  — starts low")
    print("  — sweeps upward through most of the call")
    print("  — peaks near the end")
    print("  — has a slight rolloff at the tail")
    print("Compare directly to the corpus recordings.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
