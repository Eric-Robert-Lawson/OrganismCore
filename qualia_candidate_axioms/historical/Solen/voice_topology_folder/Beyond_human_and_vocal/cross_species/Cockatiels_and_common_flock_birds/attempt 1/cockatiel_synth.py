import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
import os

# ─────────────────────────────���───────────────────────────────
# COCKATIEL CONTACT CALL SYNTHESIZER
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
# Parameters derived from Xeno-Canto corpus
# 39 quality-A recordings, 313 contact call segments
# Run date: 2026-03-27
# ─────────────────────────────────────────────────────────────
#
# CORPUS PARAMETERS (do not change — derived from data):
#   F0 median:          946 Hz
#   F0 25th pctile:     612 Hz
#   F0 75th pctile:    1027 Hz
#   Duration median:    180 ms
#   Spectral centroid: 2776 Hz
#
# THREE VARIANTS:
#   LOW  — f0=612  Hz  — lower-register birds
#   MID  — f0=946  Hz  — species centroid
#   HIGH — f0=1027 Hz  — upper-register birds
#
# FIRST MEETING PROTOCOL:
#   Play all three variants to the birds.
#   2 second gap between each.
#   Observe which variant gets a response.
#   The responding variant is the calibration seed
#   for individual eigenfunction mapping.
# ─────────────────────────────────────────────────────────────

SAMPLE_RATE = 44100
OUTPUT_DIR  = os.path.dirname(__file__)


def synthesize_contact_call(
        f0_hz,
        duration_ms      = 180,
        formant_hz       = 2776,
        formant_bw       = 900,
        h2_ratio         = 0.42,
        h3_ratio         = 0.18,
        f0_slope_hz_ms   = 1.2,    # slight upward chirp
        rise_ms          = 22,
        fall_ms          = 45,     # natural asymmetric decay
        sample_rate      = SAMPLE_RATE):
    """
    Synthesize a single cockatiel contact call.

    Architecture:
      Source:  Harmonic stack (H1+H2+H3) with
               slight upward F0 slope (natural chirp).
      Filter:  Vocal tract formant bandpass centred
               on spectral centroid from corpus.
      Mix:     60% direct source + 40% filtered.
               Natural calls have both components.
      Envelope: Asymmetric gaussian — fast rise,
                slower fall. Matches natural call shape.

    Parameters
    ----------
    f0_hz          : float  — fundamental frequency (Hz)
    duration_ms    : float  — call duration (ms)
    formant_hz     : float  — vocal tract resonance (Hz)
    formant_bw     : float  — formant bandwidth (Hz)
    h2_ratio       : float  — H2 amplitude / H1 amplitude
    h3_ratio       : float  — H3 amplitude / H1 amplitude
    f0_slope_hz_ms : float  — F0 slope (Hz per ms)
                              positive = upward chirp
    rise_ms        : float  — envelope rise time (ms)
    fall_ms        : float  — envelope fall time (ms)
    sample_rate    : int    — output sample rate (Hz)
    """

    n_samples = int(duration_ms * sample_rate / 1000)
    t         = np.linspace(0, duration_ms / 1000,
                             n_samples, endpoint=False)
    t_ms      = t * 1000

    # F0 trajectory — slight upward slope
    f0_t = f0_hz + f0_slope_hz_ms * t_ms

    # Instantaneous phase by integration
    # prevents phase discontinuity from linear F0 change
    phase = 2 * np.pi * np.cumsum(f0_t) / sample_rate

    # Harmonic stack H1 + H2 + H3
    signal = (
        np.sin(phase) +
        h2_ratio * np.sin(2 * phase) +
        h3_ratio * np.sin(3 * phase)
    )

    # Asymmetric gaussian envelope
    # Peak at 35% of duration — natural contact call shape
    peak_ms  = duration_ms * 0.35
    sigma_r  = rise_ms / 2.0
    sigma_f  = fall_ms / 2.0

    envelope = np.where(
        t_ms <= peak_ms,
        np.exp(-0.5 * ((t_ms - peak_ms) / sigma_r) ** 2),
        np.exp(-0.5 * ((t_ms - peak_ms) / sigma_f) ** 2)
    )

    signal_direct = signal * envelope

    # Vocal tract formant filter
    # Bandpass centred on corpus spectral centroid
    nyq  = sample_rate / 2.0
    low  = max((formant_hz - formant_bw / 2) / nyq, 0.005)
    high = min((formant_hz + formant_bw / 2) / nyq, 0.995)

    b, a            = butter(2, [low, high], btype='band')
    signal_filtered = filtfilt(b, a, signal_direct)

    # Mix direct and filtered
    signal_out = 0.60 * signal_direct + \
                 0.40 * signal_filtered

    # Normalise to peak 0.9 — headroom for playback
    peak = np.max(np.abs(signal_out))
    if peak > 0:
        signal_out = signal_out * (0.9 / peak)

    return signal_out


def build_sequence(call, n_repeats=3,
                   gap_ms=800,
                   sample_rate=SAMPLE_RATE):
    """
    Build a repeated call sequence with silence gaps.
    Natural contact call delivery: 3 repetitions,
    ~800 ms inter-call interval.
    """
    gap_samples = int(gap_ms * sample_rate / 1000)
    silence     = np.zeros(gap_samples)

    parts = []
    for i in range(n_repeats):
        parts.append(call)
        if i < n_repeats - 1:
            parts.append(silence)

    return np.concatenate(parts)


def save_wav(signal, filename, sample_rate=SAMPLE_RATE):
    out = (signal * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, out)
    duration_s = len(signal) / sample_rate
    print(f"  Saved: {filename}  "
          f"({duration_s:.2f}s)")


def main():
    print("=" * 60)
    print("OC-OBS-005 — COCKATIEL CONTACT CALL SYNTHESIZER")
    print("OrganismCore — Eric Robert Lawson")
    print("Parameters from Xeno-Canto corpus (313 segments)")
    print("=" * 60)

    # ── THREE SPECIES-PRIOR VARIANTS ─────────────────────
    # Built directly from corpus statistics
    # LOW:  F0 = 612 Hz  (25th percentile)
    # MID:  F0 = 946 Hz  (median)
    # HIGH: F0 = 1027 Hz (75th percentile)

    variants = [
        {
            "name":        "LOW",
            "f0_hz":       612,
            "description": "25th percentile — lower-register birds",
            "h2_ratio":    0.48,   # slightly richer harmonics
            "h3_ratio":    0.20,   #  at lower F0
        },
        {
            "name":        "MID",
            "f0_hz":       946,
            "description": "Median — species centroid",
            "h2_ratio":    0.42,
            "h3_ratio":    0.18,
        },
        {
            "name":        "HIGH",
            "f0_hz":       1027,
            "description": "75th percentile — upper-register birds",
            "h2_ratio":    0.35,   # thinner harmonics
            "h3_ratio":    0.14,   #  at higher F0
        },
    ]

    print("\nSynthesizing single calls...")
    single_calls = {}

    for v in variants:
        call = synthesize_contact_call(
            f0_hz    = v["f0_hz"],
            h2_ratio = v["h2_ratio"],
            h3_ratio = v["h3_ratio"],
        )
        single_calls[v["name"]] = call
        fname = os.path.join(
            OUTPUT_DIR,
            f"cockatiel_contact_{v['name']}_"
            f"F0{v['f0_hz']}Hz.wav")
        save_wav(call, fname)
        print(f"    {v['name']:4s}  F0={v['f0_hz']:4d} Hz  "
              f"— {v['description']}")

    # ── PLAYBACK SEQUENCES (3 repeats each) ──────────────
    print("\nSynthesizing playback sequences (3 repeats)...")

    for v in variants:
        seq   = build_sequence(single_calls[v["name"]],
                               n_repeats=3, gap_ms=800)
        fname = os.path.join(
            OUTPUT_DIR,
            f"cockatiel_SEQUENCE_{v['name']}_"
            f"F0{v['f0_hz']}Hz_3x.wav")
        save_wav(seq, fname)

    # ── FIRST MEETING PROBE FILE ──────────────────────────
    # All three variants in one file with 2s gaps.
    # Play this file on first meeting.
    # Watch which variant gets a response.
    print("\nBuilding first-meeting probe file...")
    print("  Structure: LOW — 2s gap — MID — 2s gap — HIGH")
    print("  Play this file on first meeting with the birds.")

    gap_2s   = np.zeros(int(2.0 * SAMPLE_RATE))
    gap_1s   = np.zeros(int(1.0 * SAMPLE_RATE))

    probe = np.concatenate([
        gap_1s,                             # 1s lead-in silence
        build_sequence(single_calls["LOW"],  n_repeats=3),
        gap_2s,
        build_sequence(single_calls["MID"],  n_repeats=3),
        gap_2s,
        build_sequence(single_calls["HIGH"], n_repeats=3),
        gap_1s,                             # 1s tail silence
    ])

    probe_fname = os.path.join(
        OUTPUT_DIR,
        "cockatiel_FIRST_MEETING_PROBE_LOW_MID_HIGH.wav")
    save_wav(probe, probe_fname)

    print("\n" + "=" * 60)
    print("FILES GENERATED:")
    print("=" * 60)
    print("""
  Single calls (one call each):
    cockatiel_contact_LOW_F0612Hz.wav
    cockatiel_contact_MID_F0946Hz.wav
    cockatiel_contact_HIGH_F01027Hz.wav

  Playback sequences (3 repeats, 800ms gaps):
    cockatiel_SEQUENCE_LOW_F0612Hz_3x.wav
    cockatiel_SEQUENCE_MID_F0946Hz_3x.wav
    cockatiel_SEQUENCE_HIGH_F01027Hz_3x.wav

  First meeting probe (all three, 2s gaps):
    cockatiel_FIRST_MEETING_PROBE_LOW_MID_HIGH.wav
""")
    print("=" * 60)
    print("FIRST MEETING PROTOCOL:")
    print("=" * 60)
    print("""
  1. Play cockatiel_FIRST_MEETING_PROBE_LOW_MID_HIGH.wav
     from your phone at moderate volume.
     Hold phone at bird height, ~50 cm from the birds.
     Do not move or speak during playback.

  2. Observe response to each variant:
       - Antiphonal call back
       - Head turn toward speaker
       - Posture change (alert, lean forward)
       - Approach toward phone
       - Any vocalization within 10 seconds

  3. Note which variant (LOW / MID / HIGH) got
     the strongest response.
     That is your individual calibration seed.
     Report back and we build the individual
     eigenfunction mapping script from there.

  4. If no response to any variant:
     The birds are not in contact-call mode.
     Wait until they are calling to each other
     naturally, then play the probe again.
     Do not play during feeding or disturbance.
""")
    print("Analysis complete.")


if __name__ == "__main__":
    main()
