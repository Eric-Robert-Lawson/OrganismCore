"""
MEODOSETLA DIAGNOSTIC v1
Old English: meodosetla [meodosetlɑ]
Beowulf line 6, word 3
February 2026

DIAGNOSTICS:
  D1   M nasal [m]
  D2   EO diphthong [eo]       NEW
  D3   EO F2 movement
  D4   EO vs EA distinction
  D5   D stop [d]
  D6   O vowel [o]
  D7   S fricative [s]
  D8   E vowel [e]
  D9   T stop [t]
  D10  L lateral [l]
  D11  A vowel [ɑ]
  D12  Full word
  D13  Perceptual

KEY CHECKS:
  D3  [eo] F2 movement:
      onset ~1900 Hz, offset ~800 Hz
      delta >= 700 Hz falling.

  D4  [eo] vs [eɑ] distinction:
      [eo] F1 stays low (~450 Hz)
      [eɑ] F1 rises (450→700 Hz)
      F1 trajectory is the key
      distinction between the two
      diphthongs.
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
    print("MEODOSETLA DIAGNOSTIC v1")
    print("Old English [meodosetlɑ]")
    print("Beowulf line 6, word 3")
    print("=" * 60)
    print()

    try:
        from meodosetla_reconstruction import (
            synth_meodosetla,
            synth_M,  synth_EO,
            synth_D,  synth_O,
            synth_S,  synth_E,
            synth_T,  synth_L,
            synth_A,
            apply_simple_room,
            M_F, EO_F_ON, EO_F_OFF,
            O_F, E_F, L_F, A_F)
        print("  meodosetla_reconstruction"
              ".py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 M ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — M NASAL [m]")
    print()
    m_seg = synth_M(None, EO_F_ON,
                     145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(m_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m_seg), 0.005, 0.25)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EO ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — EO DIPHTHONG [eo]")
    print()
    print("  Short front-mid diphthong.")
    print("  OE digraph 'eo'.")
    print("  Onset [e] → offset [o].")
    print("  F2 falls, F1 stays low.")
    print()
    eo_seg = synth_EO(M_F, None,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(eo_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(eo_seg),
               0.010, 0.90)
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EO MOVEMENT ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [eo] F2 MOVEMENT")
    print()
    n_eo   = len(eo_seg)
    onset  = eo_seg[:int(0.25 * n_eo)]
    offset = eo_seg[int(0.80 * n_eo):]
    f2_on  = measure_band_centroid(
        onset,  1200.0, 2500.0)
    f2_off = measure_band_centroid(
        offset,  500.0, 1400.0)
    delta  = f2_on - f2_off
    print(f"  F2 onset:  {f2_on:.0f} Hz")
    print(f"  F2 offset: {f2_off:.0f} Hz")
    print(f"  Delta:     {delta:.0f} Hz"
          f" (falling)")
    print()
    p1 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 550.0, 1100.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 delta ({delta:.0f} Hz)',
        delta, 700.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 EO vs EA ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [eo] vs [eɑ]"
          " DISTINCTION")
    print()
    print("  [eo]: F1 stays low ~450 Hz")
    print("  [eɑ]: F1 rises 450→700 Hz")
    print("  F1 trajectory is the")
    print("  key distinction.")
    print()
    f1_on_eo  = measure_band_centroid(
        onset,  200.0, 700.0)
    f1_off_eo = measure_band_centroid(
        offset, 200.0, 700.0)
    f1_delta  = abs(f1_off_eo - f1_on_eo)
    print(f"  [eo] F1 onset:  {f1_on_eo:.0f} Hz")
    print(f"  [eo] F1 offset: {f1_off_eo:.0f} Hz")
    print(f"  [eo] F1 delta:  {f1_delta:.0f} Hz"
          f" (must be < 150 Hz — stable)")
    print(f"  [eɑ] F1 delta:  ~250 Hz"
          f" (verified SCEAÞENA)")
    print()
    p1 = check(
        f'F1 onset ({f1_on_eo:.0f} Hz)',
        f1_on_eo, 300.0, 600.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F1 stability (delta'
        f' {f1_delta:.0f} Hz)',
        f1_delta, 0.0, 150.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — D STOP [d]")
    print()
    d_seg = synth_D(EO_F_OFF, O_F,
                     145.0, 1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.70)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 30.0, 90.0,
        unit=' ms', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — O VOWEL [o]")
    print()
    o_seg  = synth_O(O_F, None,
                      145.0, 1.0, SR)
    n_o    = len(o_seg)
    body_o = o_seg[int(0.12*n_o):
                   n_o-int(0.12*n_o)]
    p1 = check('voicing',
               measure_voicing(body_o),
               0.50, 1.0)
    cent_o = measure_band_centroid(
        body_o, 550.0, 1100.0)
    p2 = check(
        f'F2 centroid ({cent_o:.0f} Hz)',
        cent_o, 600.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — S FRICATIVE [s]")
    print()
    s_seg   = synth_S(O_F, E_F, 1.0, SR)
    cent_s  = measure_band_centroid(
        s_seg, 4000.0, 12000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(s_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 E ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — E VOWEL [e]")
    print()
    e_seg  = synth_E(E_F, None,
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
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 T ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — T STOP [t]")
    print()
    t_seg = synth_T(E_F, L_F, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(t_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(t_seg),
               0.005, 0.80)
    d9 = p1 and p2
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 L ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — L LATERAL [l]")
    print()
    l_seg = synth_L(L_F, A_F,
                     145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(l_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(l_seg),
               0.005, 0.80)
    d10 = p1 and p2
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 A ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — A VOWEL [ɑ]")
    print()
    a_seg  = synth_A(L_F, None,
                      145.0, 1.0, SR)
    n_a    = len(a_seg)
    body_a = a_seg[int(0.12*n_a):
                   n_a-int(0.12*n_a)]
    p1 = check('voicing',
               measure_voicing(body_a),
               0.50, 1.0)
    cent_a = measure_band_centroid(
        body_a, 800.0, 1500.0)
    p2 = check(
        f'F2 centroid ({cent_a:.0f} Hz)',
        cent_a, 900.0, 1400.0,
        unit=' Hz', fmt='.1f')
    d11 = p1 and p2
    all_pass &= d11
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — FULL WORD"
          " [meodosetlɑ]")
    print()
    w_dry  = synth_meodosetla(
        145.0, 1.0, False)
    w_hall = synth_meodosetla(
        145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 480.0, 780.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_meod_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_meod_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_meod_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_meod_eo.wav",
        ola_stretch(eo_seg / (
            np.max(np.abs(eo_seg))+1e-8)
            * 0.75, 4.0))
    d12 = p1 and p2
    all_pass &= d12
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — PERCEPTUAL")
    print()
    for fn in [
        "diag_meod_eo.wav",
        "diag_meod_slow.wav",
        "diag_meod_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  EO: vowel that moves —")
    print("    front onset, rounds back")
    print("    stays at mid height")
    print("    distinct from EA:")
    print("      EA opens (jaw drops)")
    print("      EO stays mid (jaw stays)")
    print("  Full: M·EO·D·O·S·E·T·L·A")
    print("  Nine events.")
    print("  'myeh-do-set-la'")
    print("  approximately.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   M nasal",          d1),
        ("D2   EO diphthong",     d2),
        ("D3   EO F2 movement",   d3),
        ("D4   EO/EA distinction",d4),
        ("D5   D stop",           d5),
        ("D6   O vowel",          d6),
        ("D7   S fricative",      d7),
        ("D8   E vowel",          d8),
        ("D9   T stop",           d9),
        ("D10  L lateral",        d10),
        ("D11  A vowel",          d11),
        ("D12  Full word",        d12),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:24s}  {sym}")
    print(f"  {'D13 Perceptual':24s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  MEODOSETLA [meodosetlɑ]"
              " verified.")
        print("  [eo] added to inventory.")
        print("  35 phonemes verified.")
        print()
        print("  Next: OFTEAH [ofteɑx]")
        print("  Beowulf line 6, word 4.")
        print("  Zero new phonemes.")
        print("  Line 6 final word.")
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
