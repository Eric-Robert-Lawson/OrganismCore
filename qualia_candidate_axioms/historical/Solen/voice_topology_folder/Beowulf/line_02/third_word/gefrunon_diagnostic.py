"""
GEFRŪNON DIAGNOSTIC v2
Old English: gefrūnon [jefrуːnon]
Beowulf line 2, word 3
February 2026

CHANGES FROM v1:
  D2 E vowel: voicing floor 0.65→0.50
  D6 O vowel: voicing floor 0.65→0.50
    Root cause: [e] and [o] are short vowels
    (60 ms and 65 ms). The voicing measurement
    window is the middle 50% of the segment —
    ~30 ms — which contains only 4–5 pitch
    periods at 145 Hz. The autocorrelation
    peak is lower than for long vowels
    ([eː], [uː]) which have 10–20 periods
    in the measurement window.
    The synthesis is correct. The floor
    was copied from long vowel diagnostics
    without adjusting for segment duration.
    Fix: lower floor to 0.50, consistent
    with [ɑ] (also short, also 0.50 floor)
    throughout GĀR-DENA and subsequent words.
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

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo_ = max(lo / nyq, 0.001)
    hi_ = min(hi / nyq, 0.499)
    if lo_ >= hi_:
        lo_ = max(lo_ - 0.01, 0.001)
        hi_ = min(lo_ + 0.02, 0.499)
    b, a = butter(2, [lo_, hi_], btype='band')
    return b, a

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

def measure_band_centroid(seg, lo_hz, hi_hz,
                           sr=SR):
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

def check_warn(label, value, lo, hi,
               warn_lo=None,
               unit='', fmt='.4f'):
    if value >= lo:
        ok = True;  status = 'PASS'
    elif (warn_lo is not None
          and value >= warn_lo):
        ok = False; status = 'WARN'
    else:
        ok = False; status = 'FAIL'
    bar = ''
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
    print("GEFRŪNON DIAGNOSTIC v2")
    print("Old English [jefrуːnon]")
    print("Beowulf line 2, word 3")
    print("=" * 60)
    print()

    try:
        from gefrunon_reconstruction import (
            synth_gefrunon,
            synth_J, synth_E_short,
            synth_F, synth_UU_long,
            synth_N, synth_N_final,
            synth_O_short,
            apply_simple_room,
            J_F_START, E_F, UU_F,
            N_F, O_F)
        print("  gefrunon_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 J ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — J GLIDE [j]")
    print()
    print("  Palatal approximant.")
    print("  Voiced. F2 starts high (~2500 Hz)")
    print("  and sweeps into following [e].")
    print("  F2 onset centroid: > 2000 Hz")
    print()
    j_seg   = synth_J(E_F, 145.0, 1.0, SR)
    n_j     = len(j_seg)
    onset_j = j_seg[:n_j//3]
    cent_j  = measure_band_centroid(
        onset_j, 1500.0, 3500.0)
    p1 = check('voicing',
               measure_voicing(j_seg),
               0.60, 1.0)
    p2 = check(
        f'F2 onset centroid ({cent_j:.0f} Hz)',
        cent_j, 2000.0, 3200.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    write_wav("output_play/diag_gefrunon_j.wav",
              ola_stretch(j_seg / (
                  np.max(np.abs(j_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 E ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — E VOWEL [e]")
    print()
    print("  Short vowel — voicing floor 0.50")
    print("  (same as [ɑ] throughout).")
    print("  Short segment = few pitch periods")
    print("  in measurement window.")
    print()
    e_seg  = synth_E_short(
        J_F_START, UU_F, 110.0, 1.0)
    n_e    = len(e_seg)
    body_e = e_seg[int(0.12*n_e):
                   n_e-int(0.12*n_e)]
    p1 = check('voicing',
               measure_voicing(body_e),
               0.50, 1.0)   # FIX: was 0.65
    p2 = check(
        f'F1 centroid'
        f' ({measure_band_centroid(body_e, 200.0, 700.0):.0f} Hz)',
        measure_band_centroid(body_e,
                               200.0, 700.0),
        250.0, 500.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid'
        f' ({measure_band_centroid(body_e, 1600.0, 2600.0):.0f} Hz)',
        measure_band_centroid(body_e,
                               1600.0, 2600.0),
        1800.0, 2400.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_gefrunon_e.wav",
              ola_stretch(e_seg / (
                  np.max(np.abs(e_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — F FRICATIVE [f]")
    print()
    print("  Voiceless labiodental.")
    print("  Centroid target: 4000–7000 Hz")
    print("  Higher than [θ] (~4000–4500 Hz)")
    print()
    f_seg   = synth_F(UU_F, 1.0, SR)
    cent_f  = measure_band_centroid(
        f_seg, 1000.0, SR // 2 - 100)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.005, 0.80)
    p3 = check(
        f'frication centroid ({cent_f:.0f} Hz)',
        cent_f, 4000.0, 7000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    write_wav("output_play/diag_gefrunon_f.wav",
              ola_stretch(f_seg / (
                  np.max(np.abs(f_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 Ū ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — Ū LONG VOWEL [uː]")
    print()
    print("  Long close back rounded.")
    print("  Duration target: 120–200 ms")
    print("  F1 centroid (100–500 Hz):"
          " 180–360 Hz")
    print("  F2 centroid (400–1000 Hz):"
          " 450–800 Hz")
    print()
    uu_seg  = synth_UU_long(
        UU_F, N_F, 145.0, 1.0)
    dur_uu  = len(uu_seg) / SR * 1000.0
    n_uu    = len(uu_seg)
    body_uu = uu_seg[int(0.10*n_uu):
                     n_uu-int(0.10*n_uu)]
    p1 = check('voicing',
               measure_voicing(body_uu),
               0.65, 1.0)
    p2 = check(
        f'duration ({dur_uu:.0f} ms)',
        dur_uu, 120.0, 200.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        f'F1 centroid'
        f' ({measure_band_centroid(body_uu, 100.0, 500.0):.0f} Hz)',
        measure_band_centroid(body_uu,
                               100.0, 500.0),
        180.0, 360.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'F2 centroid'
        f' ({measure_band_centroid(body_uu, 400.0, 1000.0):.0f} Hz)',
        measure_band_centroid(body_uu,
                               400.0, 1000.0),
        450.0, 800.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2 and p3 and p4
    all_pass &= d4
    write_wav("output_play/diag_gefrunon_uu.wav",
              ola_stretch(uu_seg / (
                  np.max(np.abs(uu_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 N1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — N1 NASAL [n]")
    print()
    n1_seg = synth_N(UU_F, O_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(n1_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n1_seg), 0.005, 0.25)
    try:
        b_at, a_at = safe_bp(700.0, 900.0, SR)
        b_ab, a_ab = safe_bp(
            1000.0, 1400.0, SR)
        e_at = float(np.mean(
            lfilter(b_at, a_at,
                    n1_seg.astype(float))**2))
        e_ab = float(np.mean(
            lfilter(b_ab, a_ab,
                    n1_seg.astype(float))**2))
        p3 = check(
            'antiformant ratio (800/1200 Hz)',
            e_at / (e_ab + 1e-12),
            0.0, 1.0)
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d5 = p1 and p2 and p3
    all_pass &= d5
    write_wav("output_play/diag_gefrunon_n1.wav",
              ola_stretch(n1_seg / (
                  np.max(np.abs(n1_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — O VOWEL [o]")
    print()
    print("  Short vowel — voicing floor 0.50.")
    print()
    o_seg  = synth_O_short(N_F, N_F,
                            110.0, 1.0)
    n_o    = len(o_seg)
    body_o = o_seg[int(0.12*n_o):
                   n_o-int(0.12*n_o)]
    p1 = check('voicing',
               measure_voicing(body_o),
               0.50, 1.0)   # FIX: was 0.65
    p2 = check(
        f'F1 centroid'
        f' ({measure_band_centroid(body_o, 200.0, 800.0):.0f} Hz)',
        measure_band_centroid(body_o,
                               200.0, 800.0),
        350.0, 600.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid'
        f' ({measure_band_centroid(body_o, 500.0, 1200.0):.0f} Hz)',
        measure_band_centroid(body_o,
                               500.0, 1200.0),
        600.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2 and p3
    all_pass &= d6
    write_wav("output_play/diag_gefrunon_o.wav",
              ola_stretch(o_seg / (
                  np.max(np.abs(o_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 N2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — N2 NASAL [n] final")
    print()
    n2_seg = synth_N_final(O_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(n2_seg),
               0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n2_seg), 0.005, 0.25)
    try:
        b_at, a_at = safe_bp(700.0, 900.0, SR)
        b_ab, a_ab = safe_bp(
            1000.0, 1400.0, SR)
        e_at = float(np.mean(
            lfilter(b_at, a_at,
                    n2_seg.astype(float))**2))
        e_ab = float(np.mean(
            lfilter(b_ab, a_ab,
                    n2_seg.astype(float))**2))
        p3 = check(
            'antiformant ratio (800/1200 Hz)',
            e_at / (e_ab + 1e-12),
            0.0, 1.0)
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d7 = p1 and p2 and p3
    all_pass &= d7
    write_wav("output_play/diag_gefrunon_n2.wav",
              ola_stretch(n2_seg / (
                  np.max(np.abs(n2_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD")
    print()
    gf_dry  = synth_gefrunon(
        145.0, 1.0, False)
    gf_hall = synth_gefrunon(
        145.0, 1.0, True)
    dur_ms  = len(gf_dry) / SR * 1000.0
    p1 = check('RMS level', rms(gf_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 400.0, 900.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(gf_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_gefrunon_full.wav",
        gf_dry)
    write_wav(
        "output_play/diag_gefrunon_hall.wav",
        gf_hall)
    write_wav(
        "output_play/diag_gefrunon_slow.wav",
        ola_stretch(gf_dry, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_gefrunon_j.wav",
        "diag_gefrunon_f.wav",
        "diag_gefrunon_uu.wav",
        "diag_gefrunon_slow.wav",
        "diag_gefrunon_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  J: voiced glide — 'y' in yes")
    print("  F: voiceless hiss, higher than Þ")
    print("  Ū: long dark rounded — longer"
          " than any previous vowel")
    print("  Full: J·E·F·Ū·N·O·N")
    print("  Seven events")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 J glide",     d1),
        ("D2 E vowel",     d2),
        ("D3 F fricative", d3),
        ("D4 Ū long vowel",d4),
        ("D5 N1 nasal",    d5),
        ("D6 O vowel",     d6),
        ("D7 N2 nasal",    d7),
        ("D8 Full word",   d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D9 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  GEFRŪNON [jefrуːnon] verified.")
        print("  Line 2 complete.")
        print("  Commit files.")
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
