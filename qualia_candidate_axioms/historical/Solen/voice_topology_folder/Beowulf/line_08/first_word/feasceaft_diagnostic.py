"""
FEASCEAFT DIAGNOSTIC v1
Old English: feasceaft [fæɑʃæɑft]
Beowulf line 8, word 1 (overall word 31)
Zero new phonemes — pure assembly
February 2026

DIAGNOSTICS:
  D1  F1 first fricative [f]
  D2  EA1 diphthong — first instance
      F_prev=None, F_next=SH_F
  D3  EA1 F1 movement — jaw opens
  D4  SH fricative [ʃ]
  D5  SH vs S distinction
      [ʃ] centroid lower than [s]
  D6  EA2 diphthong — second instance
      F_prev=SH_F, F_next=None
  D7  EA2 F1 movement
  D8  EA1 vs EA2 consistency
      both instances same diphthong
  D9  F2 second fricative [f]
  D10 T stop [t]
  D11 Full word
  D12 Perceptual

KEY CHECKS:
  D5: [ʃ] centroid < [s] centroid
      [ʃ] ~3500 Hz vs [s] ~7500 Hz
      place distinction confirmed
  D8: both EA instances consistent
      F2 onset ~1850 Hz both
      F1 delta ~250-280 Hz both
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
    win_ms  = 40.0
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    window  = np.hanning(win_n).astype(DTYPE)
    n_in    = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
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
    print("FEASCEAFT DIAGNOSTIC v1")
    print("Old English [fæɑʃæɑft]")
    print("Beowulf line 8, word 1")
    print("Zero new phonemes — pure assembly")
    print("=" * 60)
    print()

    try:
        from feasceaft_reconstruction import (
            synth_feasceaft,
            synth_F, synth_EA,
            synth_SH, synth_T,
            apply_simple_room,
            EA_F_ON, EA_F_OFF,
            SH_F,
            PITCH_PERF, DIL_PERF)
        print("  feasceaft_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 F1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — F1 FIRST [f]")
    print()
    f1_seg  = synth_F(1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f1_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f1_seg),
               0.001, 0.50)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EA1 F2 ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — EA1 DIPHTHONG"
          " [eɑ] first instance")
    print("  Context: follows [f],"
          " precedes [ʃ]")
    print()
    ea1_seg = synth_EA(None, SH_F,
                        145.0, 1.0, SR)
    n_ea1   = len(ea1_seg)
    onset1  = ea1_seg[:int(0.25 * n_ea1)]
    offset1 = ea1_seg[int(0.85 * n_ea1):]
    f2_on1  = measure_band_centroid(
        onset1,  1200.0, 2500.0)
    f2_off1 = measure_band_centroid(
        offset1,  700.0, 1500.0)
    delta_f2_1 = f2_on1 - f2_off1
    print(f"  F2 onset:  {f2_on1:.0f} Hz")
    print(f"  F2 offset: {f2_off1:.0f} Hz")
    print(f"  Delta:     {delta_f2_1:.0f} Hz"
          f" (falling)")
    print()
    p1 = check('voicing',
               measure_voicing(ea1_seg),
               0.50, 1.0)
    p2 = check(
        f'F2 onset ({f2_on1:.0f} Hz)',
        f2_on1, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 offset ({f2_off1:.0f} Hz)',
        f2_off1, 700.0, 1400.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'F2 delta ({delta_f2_1:.0f} Hz)',
        delta_f2_1, 400.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3 and p4
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EA1 F1 ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — EA1 F1 MOVEMENT"
          " — jaw opens")
    print()
    f1_on1  = measure_band_centroid(
        onset1,  200.0, 700.0)
    f1_off1 = measure_band_centroid(
        offset1, 400.0, 900.0)
    delta_f1_1 = f1_off1 - f1_on1
    print(f"  F1 onset:  {f1_on1:.0f} Hz")
    print(f"  F1 offset: {f1_off1:.0f} Hz")
    print(f"  Delta:     {delta_f1_1:.0f} Hz"
          f" (rising)")
    print()
    p1 = check(
        f'F1 delta ({delta_f1_1:.0f} Hz)',
        delta_f1_1, 100.0, 400.0,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 SH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — SH FRICATIVE [ʃ]")
    print()
    sh_seg  = synth_SH(1.0, SR)
    cent_sh = measure_band_centroid(
        sh_seg, 1500.0, 6000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(sh_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_sh:.0f} Hz)',
        cent_sh, 2000.0, 5000.0,
        unit=' Hz', fmt='.1f')
    p3 = check('RMS level', rms(sh_seg),
               0.001, 0.50)
    d4 = p1 and p2 and p3
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 SH vs S ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [ʃ] vs [s]"
          " place distinction")
    print()
    from scipy.signal import butter, lfilter \
        as _lfilter
    noise_s = np.random.randn(
        int(65.0/1000*SR)).astype(float)
    nyq = SR / 2.0
    lo_ = max((7500.0-4000.0/2)/nyq, 0.001)
    hi_ = min((7500.0+4000.0/2)/nyq, 0.499)
    b_, a_ = butter(2, [lo_, hi_],
                    btype='band')
    s_ref   = _lfilter(b_, a_, noise_s)
    cent_s  = measure_band_centroid(
        f32(s_ref), 4000.0, 12000.0)
    print(f"  [ʃ] centroid: {cent_sh:.0f} Hz"
          f"  (palatal — lower)")
    print(f"  [s] centroid: {cent_s:.0f} Hz"
          f"  (alveolar — higher)")
    sep = cent_s - cent_sh
    print(f"  Separation:   {sep:.0f} Hz")
    print()
    p1 = check(
        f'[ʃ]<[s] separation'
        f' ({sep:.0f} Hz)',
        sep, 1000.0, 8000.0,
        unit=' Hz', fmt='.1f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 EA2 F2 ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — EA2 DIPHTHONG"
          " [eɑ] second instance")
    print("  Context: follows [ʃ],"
          " precedes [f]")
    print()
    ea2_seg = synth_EA(SH_F, None,
                        145.0, 1.0, SR)
    n_ea2   = len(ea2_seg)
    onset2  = ea2_seg[:int(0.25 * n_ea2)]
    offset2 = ea2_seg[int(0.85 * n_ea2):]
    f2_on2  = measure_band_centroid(
        onset2,  1200.0, 2500.0)
    f2_off2 = measure_band_centroid(
        offset2,  700.0, 1500.0)
    delta_f2_2 = f2_on2 - f2_off2
    print(f"  F2 onset:  {f2_on2:.0f} Hz")
    print(f"  F2 offset: {f2_off2:.0f} Hz")
    print(f"  Delta:     {delta_f2_2:.0f} Hz"
          f" (falling)")
    print()
    p1 = check('voicing',
               measure_voicing(ea2_seg),
               0.50, 1.0)
    p2 = check(
        f'F2 onset ({f2_on2:.0f} Hz)',
        f2_on2, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 offset ({f2_off2:.0f} Hz)',
        f2_off2, 700.0, 1400.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'F2 delta ({delta_f2_2:.0f} Hz)',
        delta_f2_2, 400.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2 and p3 and p4
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 EA2 F1 ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — EA2 F1 MOVEMENT")
    print()
    f1_on2  = measure_band_centroid(
        onset2,  200.0, 700.0)
    f1_off2 = measure_band_centroid(
        offset2, 400.0, 900.0)
    delta_f1_2 = f1_off2 - f1_on2
    print(f"  F1 onset:  {f1_on2:.0f} Hz")
    print(f"  F1 offset: {f1_off2:.0f} Hz")
    print(f"  Delta:     {delta_f1_2:.0f} Hz"
          f" (rising)")
    print()
    p1 = check(
        f'F1 delta ({delta_f1_2:.0f} Hz)',
        delta_f1_2, 100.0, 400.0,
        unit=' Hz', fmt='.1f')
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 EA1 vs EA2 CONSISTENCY ─────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — EA1 vs EA2"
          " CONSISTENCY")
    print("  Same phoneme, different context.")
    print("  Both should produce same")
    print("  F2 onset and F1 delta.")
    print()
    print(f"  EA1 F2 onset:  {f2_on1:.0f} Hz")
    print(f"  EA2 F2 onset:  {f2_on2:.0f} Hz")
    print(f"  Difference:    "
          f"{abs(f2_on1-f2_on2):.0f} Hz")
    print()
    print(f"  EA1 F1 delta:  {delta_f1_1:.0f} Hz")
    print(f"  EA2 F1 delta:  {delta_f1_2:.0f} Hz")
    print(f"  Difference:    "
          f"{abs(delta_f1_1-delta_f1_2):.0f} Hz")
    print()
    f2_diff   = abs(f2_on1 - f2_on2)
    f1d_diff  = abs(delta_f1_1 - delta_f1_2)
    p1 = check(
        f'F2 onset difference'
        f' ({f2_diff:.0f} Hz)',
        f2_diff, 0.0, 200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F1 delta difference'
        f' ({f1d_diff:.0f} Hz)',
        f1d_diff, 0.0, 100.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 F2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — F2 SECOND [f]")
    print()
    f2_seg  = synth_F(1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f2_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f2_seg),
               0.001, 0.50)
    d9 = p1 and p2
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 T ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — T STOP [t]")
    print()
    t_seg   = synth_T(145.0, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(t_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(t_seg),
               0.005, 0.70)
    d10 = p1 and p2
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — FULL WORD"
          " [fæɑʃæɑft]")
    print()
    w_dry  = synth_feasceaft(
        145.0, 1.0, False)
    w_hall = synth_feasceaft(
        145.0, 1.0, True)
    w_perf = synth_feasceaft(
        PITCH_PERF, DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 350.0, 600.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    write_wav(
        "output_play/diag_feasceaft_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_feasceaft_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_feasceaft_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_feasceaft_perf.wav",
        w_perf)
    d11 = p1 and p2
    all_pass &= d11
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_feasceaft_full.wav",
        "diag_feasceaft_slow.wav",
        "diag_feasceaft_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_feasceaft_perf.wav")
    print(f"  [{PITCH_PERF} Hz,"
          f" dil {DIL_PERF},"
          f" hall RT60=2.0s]")
    print()
    print("  LISTEN FOR:")
    print("  F  — voiceless onset")
    print("  EA — diphthong opens")
    print("       jaw rises, F2 falls")
    print("  SH — palatal constriction")
    print("       lower than [s]")
    print("  EA — diphthong opens again")
    print("       same shape as first")
    print("  F  — voiceless again")
    print("  T  — stop close")
    print("  Oscillating shape:")
    print("    constrict→open→constrict")
    print("    →open→constrict→close")
    print("  feasceaft funden —")
    print("  found wretched")
    print("  The turning point.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   F1 fricative",         d1),
        ("D2   EA1 F2 movement",      d2),
        ("D3   EA1 F1 movement",      d3),
        ("D4   SH fricative",         d4),
        ("D5   SH vs S place",        d5),
        ("D6   EA2 F2 movement",      d6),
        ("D7   EA2 F1 movement",      d7),
        ("D8   EA1/EA2 consistency",  d8),
        ("D9   F2 fricative",         d9),
        ("D10  T stop",               d10),
        ("D11  Full word",            d11),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D12 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  FEASCEAFT [fæɑʃæɑft] verified.")
        print("  Zero new phonemes.")
        print("  39 phonemes verified.")
        print()
        print("  Line 8 status:")
        print("  feasceaft  ✓")
        print("  funden     — next")
        print("  hē         — next")
        print("  þæs        — next")
        print("  frōfre     — next")
        print("  gebād      — [b] arrives")
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
