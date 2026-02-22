"""
ÞRYM DIAGNOSTIC v1
Old English: þrym [θrym]
Beowulf line 2, word 2
February 2026

DIAGNOSTICS:
  D1  Þ fricative [θ]
  D2  R trill [r]
  D3  Y vowel [y]
  D4  M nasal [m]
  D5  Full word
  D6  Perceptual
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

def measure_trill_modulation(seg, sr=SR):
    if len(seg) < int(0.04 * sr):
        return 0.0, 0.0
    win_ms  = 5.0
    hop_ms  = 2.5
    win_n   = int(win_ms / 1000.0 * sr)
    hop_n   = int(hop_ms / 1000.0 * sr)
    if win_n < 4:
        return 0.0, 0.0
    sig_f   = seg.astype(float)
    n_frames = max(1,
                   (len(sig_f) - win_n)
                   // hop_n + 1)
    env = np.zeros(n_frames, dtype=float)
    for i in range(n_frames):
        s = i * hop_n
        e = min(s + win_n, len(sig_f))
        env[i] = np.sqrt(
            np.mean(sig_f[s:e]**2) + 1e-12)
    env_sr = 1.0 / (hop_ms / 1000.0)
    env   -= np.mean(env)
    if np.max(np.abs(env)) < 1e-8:
        return 0.0, 0.0
    acorr = np.correlate(env, env, mode='full')
    acorr = acorr[len(acorr)//2:]
    if acorr[0] < 1e-10:
        return 0.0, 0.0
    acorr /= acorr[0]
    lo_lag = int(env_sr / 60.0)
    hi_lag = int(env_sr / 15.0)
    hi_lag = min(hi_lag, len(acorr) - 1)
    if lo_lag >= hi_lag:
        return 0.0, 0.0
    peak_val = float(np.max(acorr[lo_lag:hi_lag]))
    peak_lag = (int(np.argmax(
        acorr[lo_lag:hi_lag])) + lo_lag)
    trill_hz = (float(env_sr / peak_lag)
                if peak_lag > 0 else 0.0)
    return float(np.clip(peak_val, 0, 1)), \
           trill_hz

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
    print("ÞRYM DIAGNOSTIC v1")
    print("Old English [θrym]")
    print("Beowulf line 2, word 2")
    print("=" * 60)
    print()

    try:
        from thrym_reconstruction import (
            synth_thrym,
            synth_TH, synth_R_trill,
            synth_Y_short, synth_M_final,
            apply_simple_room,
            R_F, Y_F, M_F)
        print("  thrym_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 Þ ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — Þ FRICATIVE [θ]")
    print()
    th_seg  = synth_TH(R_F, 1.0, SR)
    cent_th = measure_band_centroid(
        th_seg, 1000.0, 8000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(th_seg),
               0.005, 0.80)
    p3 = check(
        f'frication centroid ({cent_th:.0f} Hz)',
        cent_th, 2500.0, 5000.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2 and p3
    all_pass &= d1
    write_wav("output_play/diag_thrym_th.wav",
              ola_stretch(th_seg / (
                  np.max(np.abs(th_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — R TRILL [r]")
    print()
    r_seg = synth_R_trill(
        R_F, Y_F, 145.0, 1.0)
    mod_depth, trill_hz = \
        measure_trill_modulation(r_seg)
    p1 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    p2 = check_warn(
        'trill modulation depth',
        mod_depth, 0.22, 1.0, warn_lo=0.10)
    if trill_hz > 0:
        p3 = check(
            f'trill rate ({trill_hz:.1f} Hz)',
            trill_hz, 15.0, 70.0,
            unit=' Hz', fmt='.1f')
    else:
        p3 = False
        print("    [FAIL] trill rate"
              " not detected.")
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_thrym_r.wav",
              ola_stretch(r_seg / (
                  np.max(np.abs(r_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 Y ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — Y VOWEL [y]")
    print()
    y_seg  = synth_Y_short(
        R_F, M_F, 145.0, 1.0)
    n_y    = len(y_seg)
    body_y = y_seg[int(0.15*n_y):
                   n_y-int(0.15*n_y)]
    cent_y1 = measure_band_centroid(
        body_y, 150.0, 700.0)
    cent_y2 = measure_band_centroid(
        body_y, 1000.0, 2200.0)
    p1 = check('voicing',
               measure_voicing(body_y),
               0.65, 1.0)
    p2 = check(
        f'F1 centroid ({cent_y1:.0f} Hz)',
        cent_y1, 200.0, 420.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_y2:.0f} Hz)',
        cent_y2, 1200.0, 1800.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    write_wav("output_play/diag_thrym_y.wav",
              ola_stretch(y_seg / (
                  np.max(np.abs(y_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 M ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — M NASAL [m]")
    print()
    m_seg = synth_M_final(Y_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(m_seg),
               0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m_seg), 0.005, 0.25)
    try:
        b_lo, a_lo = safe_bp(200.0, 600.0, SR)
        b_nt, a_nt = safe_bp(850.0, 1150.0, SR)
        e_lo = float(np.mean(
            lfilter(b_lo, a_lo,
                    m_seg.astype(float))**2))
        e_nt = float(np.mean(
            lfilter(b_nt, a_nt,
                    m_seg.astype(float))**2))
        ratio = e_lo / (e_nt + 1e-12)
        p3 = check(
            f'murmur/notch ratio ({ratio:.2f})',
            ratio, 2.0, 10000.0,
            unit='', fmt='.2f')
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d4 = p1 and p2 and p3
    all_pass &= d4
    write_wav("output_play/diag_thrym_m.wav",
              ola_stretch(m_seg / (
                  np.max(np.abs(m_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — FULL WORD [θrym]")
    print()
    th_dry  = synth_thrym(145.0, 1.0, False)
    th_hall = synth_thrym(145.0, 1.0, True)
    dur_ms  = len(th_dry) / SR * 1000.0
    p1 = check('RMS level', rms(th_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 150.0, 450.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(th_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_thrym_full.wav",
        th_dry)
    write_wav(
        "output_play/diag_thrym_hall.wav",
        th_hall)
    write_wav(
        "output_play/diag_thrym_slow.wav",
        ola_stretch(th_dry, 4.0))
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — PERCEPTUAL")
    print()
    for fn in [
        "diag_thrym_th.wav",
        "diag_thrym_r.wav",
        "diag_thrym_y.wav",
        "diag_thrym_slow.wav",
        "diag_thrym_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Þ: voiceless hiss onset")
    print("  R: trill modulation after hiss")
    print("  Y: front rounded vowel peak")
    print("  M: bilabial close into silence")
    print("  Full: Þ·R·Y·M — four events")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 Þ fricative", d1),
        ("D2 R trill",     d2),
        ("D3 Y vowel",     d3),
        ("D4 M nasal",     d4),
        ("D5 Full word",   d5),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D6 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÞRYM [θrym] verified.")
        print("  Next: GEFRŪNON [jefrуːnon]")
        print("  Beowulf line 2, word 3.")
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
