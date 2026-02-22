"""
ǢREST DIAGNOSTIC v2
Old English: ǣrest [æːrest]
Beowulf line 7, word 4
Zero new phonemes — pure assembly
February 2026

v2: R_TRILL_DEPTH 0.55 → 0.40
    performance output added
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


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
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz         = norm > 1e-8
    out[nz]   /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def measure_voicing(seg, sr=SR):
    if len(seg) < 256:
        return 0.0
    n    = len(seg)
    core = seg[n//4: 3*n//4].astype(float)
    core -= np.mean(core)
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    acorr  = np.correlate(core, core,
                          mode='full')
    acorr  = acorr[len(acorr)//2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(
        np.max(acorr[lo:hi]), 0.0, 1.0))

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
    if len(seg) < 64:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048))**2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(
        freqs[mask] * spec[mask]) / total)

def check(label, value, lo, hi,
          unit='', fmt='.4f'):
    ok     = (lo <= value <= hi)
    status = 'PASS' if ok else 'FAIL'
    bar    = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    print(f"    [{status}] {label}: "
          f"{format(value, fmt)}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok


def run_diagnostics():
    print()
    print("=" * 60)
    print("ǢREST DIAGNOSTIC v2")
    print("Old English [æːrest]")
    print("Beowulf line 7, word 4")
    print("v2: R_TRILL_DEPTH 0.55 → 0.40")
    print("=" * 60)
    print()

    try:
        from aerest_reconstruction import (
            synth_aerest,
            synth_AEY, synth_R, synth_E,
            synth_S, synth_T,
            apply_simple_room,
            AEY_F, R_F, E_F,
            PITCH_PERF, DIL_PERF)
        print("  aerest_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 AEY ────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — AEY LONG VOWEL [æː]")
    print()
    aey_seg = synth_AEY(None, R_F,
                         145.0, 1.0, SR)
    n_aey   = len(aey_seg)
    body_aey= aey_seg[int(0.10*n_aey):
                      n_aey-int(0.10*n_aey)]
    p1 = check('voicing',
               measure_voicing(body_aey),
               0.50, 1.0)
    cent_aey = measure_band_centroid(
        body_aey, 1200.0, 2200.0)
    p2 = check(
        f'F2 centroid ({cent_aey:.0f} Hz)',
        cent_aey, 1400.0, 2100.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 AEY DURATION ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [æː] DURATION")
    print()
    dur_aey = n_aey / SR * 1000.0
    print(f"  Duration: {dur_aey:.0f} ms")
    p1 = check(
        f'duration ({dur_aey:.0f} ms)',
        dur_aey, 90.0, 150.0,
        unit=' ms', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — R TRILL [r]")
    print("  v2: TRILL_DEPTH 0.55 → 0.40")
    print()
    r_seg  = synth_R(AEY_F, E_F,
                      145.0, 1.0, SR)
    voic_r = measure_voicing(r_seg)
    print(f"  v1 voicing: 0.4320  FAILED")
    print(f"  v2 voicing: {voic_r:.4f}"
          f"  {'— expect PASS' if voic_r >= 0.50 else '— still below threshold'}")
    print()
    p1 = check('voicing',
               voic_r, 0.50, 1.0)
    p2 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 E ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — E VOWEL [e]")
    print()
    e_seg  = synth_E(R_F, None,
                      145.0, 1.0, SR)
    n_e    = len(e_seg)
    body_e = e_seg[int(0.12*n_e):
                   n_e-int(0.12*n_e)]
    p1 = check('voicing',
               measure_voicing(body_e),
               0.50, 1.0)
    cent_e = measure_band_centroid(
        body_e, 1500.0, 2500.0)
    p2 = check(
        f'F2 centroid ({cent_e:.0f} Hz)',
        cent_e, 1600.0, 2300.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — S FRICATIVE [s]")
    print()
    s_seg  = synth_S(E_F, None, 1.0, SR)
    cent_s = measure_band_centroid(
        s_seg, 4000.0, 12000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(s_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 T ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — T STOP [t]")
    print()
    t_seg  = synth_T(None, None,
                      145.0, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(t_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(t_seg),
               0.005, 0.70)
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 ST CLUSTER ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [st] CLUSTER")
    print()
    voic_s = measure_voicing(s_seg)
    voic_t = measure_voicing(t_seg)
    p1 = check('[s] voiceless',
               voic_s, 0.0, 0.35)
    p2 = check('[t] voiceless',
               voic_t, 0.0, 0.35)
    p3 = check(
        f'[s] centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d7 = p1 and p2 and p3
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [æːrest]")
    print()
    w_dry  = synth_aerest(145.0, 1.0, False)
    w_hall = synth_aerest(145.0, 1.0, True)
    w_slow = ola_stretch(w_dry, 4.0)
    w_perf = synth_aerest(
        PITCH_PERF, DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 300.0, 480.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    write_wav(
        "output_play/diag_aerest_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_aerest_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_aerest_slow.wav",
        w_slow)
    write_wav(
        "output_play/diag_aerest_perf.wav",
        w_perf)
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────��───────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_aerest_full.wav",
        "diag_aerest_slow.wav",
        "diag_aerest_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_aerest_perf.wav")
    print(f"  [{PITCH_PERF} Hz,"
          f" dil {DIL_PERF},"
          f" hall RT60=2.0s]")
    print()
    print("  LISTEN FOR:")
    print("  AEY — long open front")
    print("    held — longer than short [æ]")
    print("  R   — trill")
    print("    v2: slightly smoother")
    print("    than v1 but still trill")
    print("  E   — short front vowel")
    print("  S   — voiceless fricative")
    print("  T   — stop close")
    print("  Performance: slower, deeper,")
    print("    hall reverb — scop register")
    print("  syþðan ǣrest wearð —")
    print("  since first it came to be")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  AEY long vowel",      d1),
        ("D2  AEY duration",        d2),
        ("D3  R trill (v2)",        d3),
        ("D4  E vowel",             d4),
        ("D5  S fricative",         d5),
        ("D6  T stop",              d6),
        ("D7  ST cluster",          d7),
        ("D8  Full word",           d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D9 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ǢREST [æːrest] verified.")
        print("  Zero new phonemes.")
        print("  39 phonemes verified.")
        print()
        print("  Output files:")
        print("  diag_aerest_full.wav"
              "  — dry 145 Hz")
        print("  diag_aerest_hall.wav"
              "  — hall 145 Hz")
        print("  diag_aerest_slow.wav"
              "  — 4x slow")
        print("  diag_aerest_perf.wav"
              "  — 110 Hz dil 2.5 hall")
        print()
        print("  Line 7 status:")
        print("  egsode  ✓")
        print("  eorlas  ✓")
        print("  syþðan  ✓")
        print("  ǣrest   ✓")
        print("  wearð   — remaining")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
