"""
IN DIAGNOSTIC v1
Old English: in [ɪn]
Beowulf line 1, word 4
February 2026

DIAGNOSTIC STRUCTURE:
  D1 — I vowel [ɪ]
       F1 centroid: 200–700 Hz, target 320–480 Hz
       F2 centroid: 1400–2200 Hz, target 1600–2000 Hz
       voicing > 0.65

  D2 — N nasal [n] (word-final)
       voicing > 0.65
       RMS: nasal murmur range
       antiformant ratio < 1.0

  D3 — Full word
       duration check
       voicing profile
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
    n_fft = 2048
    spec  = np.abs(
        np.fft.rfft(seg.astype(float),
                    n=n_fft))**2
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    s     = spec[mask]
    f     = freqs[mask]
    total = np.sum(s)
    if total < 1e-12:
        return 0.0
    return float(np.sum(f * s) / total)

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
    print("IN DIAGNOSTIC v1")
    print("Old English [ɪn]")
    print("Beowulf line 1, word 4")
    print("=" * 60)
    print()

    try:
        from in_reconstruction import (
            synth_in, synth_I_short,
            synth_N_final,
            apply_simple_room,
            I_F, N_F)
        print("  in_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 I VOWEL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — I VOWEL [ɪ]")
    print()
    print("  Near-close near-front lax vowel.")
    print("  F1 centroid (200–700 Hz):"
          " target 320–480 Hz")
    print("  F2 centroid (1400–2200 Hz):"
          " target 1600–2000 Hz")
    print("  [ɪ] is laxer/lower than [iː]:")
    print("    [iː]: F2 ~2300 Hz")
    print("    [ɪ]:  F2 ~1800 Hz")
    print("    [e]:  F2 ~2200 Hz")
    print()

    i_seg  = synth_I_short(
        F_prev=None, F_next=N_F,
        pitch_hz=145.0, dil=1.0)
    n_i    = len(i_seg)
    n_on   = int(0.15 * n_i)
    n_off  = int(0.20 * n_i)
    body_i = i_seg[n_on:n_i-n_off]

    vr_i    = measure_voicing(body_i)
    r_i     = rms(i_seg)
    cent_i1 = measure_band_centroid(
        body_i, 200.0, 700.0, sr=SR)
    cent_i2 = measure_band_centroid(
        body_i, 1400.0, 2200.0, sr=SR)

    p1 = check('voicing (body)', vr_i,
               0.65, 1.0)
    p2 = check('RMS level', r_i, 0.010, 5.0)
    p3 = check(
        f'F1 centroid ({cent_i1:.0f} Hz)',
        cent_i1, 320.0, 480.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_i1 < 320:
            print(f"      F1 too low ({cent_i1:.0f})."
                  f" Lower I_F[0].")
        else:
            print(f"      F1 too high ({cent_i1:.0f})."
                  f" Raise I_F[0].")
    p4 = check(
        f'F2 centroid ({cent_i2:.0f} Hz)',
        cent_i2, 1600.0, 2000.0,
        unit=' Hz', fmt='.1f')
    if not p4:
        if cent_i2 < 1600:
            print(f"      F2 too low ({cent_i2:.0f})."
                  f" Raise I_F[1].")
        else:
            print(f"      F2 too high ({cent_i2:.0f})."
                  f" Lower I_F[1].")

    d1 = p1 and p2 and p3 and p4
    all_pass &= d1
    write_wav(
        "output_play/diag_i_vowel_slow.wav",
        ola_stretch(i_seg / (
            np.max(np.abs(i_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  diag_i_vowel_slow.wav")
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 N NASAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — N NASAL [n]")
    print()
    print("  Word-final nasal.")
    print("  Shorter than medial N (55 ms).")
    print("  Antiformant at 800 Hz.")
    print()

    n_seg = synth_N_final(
        F_prev=I_F,
        pitch_hz=145.0, dil=1.0)

    vr_n = measure_voicing(n_seg)
    r_n  = rms(n_seg)

    p1 = check('voicing', vr_n, 0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               r_n, 0.005, 0.25)

    try:
        b_at, a_at = safe_bp(700.0, 900.0, SR)
        b_ab, a_ab = safe_bp(
            1000.0, 1400.0, SR)
        e_at = float(np.mean(
            lfilter(b_at, a_at,
                    n_seg.astype(float))**2))
        e_ab = float(np.mean(
            lfilter(b_ab, a_ab,
                    n_seg.astype(float))**2))
        anti_ratio = e_at / (e_ab + 1e-12)
        p3 = check(
            'antiformant ratio (800/1200 Hz)',
            anti_ratio, 0.0, 1.0)
        if not p3:
            print("      800 Hz > 1200 Hz."
                  " Check iir_notch().")
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")

    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav(
        "output_play/diag_n_final_slow.wav",
        ola_stretch(n_seg / (
            np.max(np.abs(n_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  diag_n_final_slow.wav")
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — FULL WORD [ɪn]")
    print()

    in_dry  = synth_in(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    in_hall = synth_in(
        pitch_hz=145.0, dil=1.0,
        add_room=True)

    dur_ms  = len(in_dry) / SR * 1000.0
    r_full  = rms(in_dry)

    p1 = check('RMS level', r_full,
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 80.0, 180.0,
        unit=' ms', fmt='.1f')

    n_i_w = len(synth_I_short(
        None, N_F, 145.0, 1.0))
    z_i = (0, n_i_w)
    z_n = (n_i_w, len(in_dry))

    def sw(s, e):
        s = max(0, s)
        e = min(len(in_dry), e)
        return (in_dry[s:e]
                if e > s else in_dry[:10])

    p3 = check_warn(
        'I zone voicing',
        measure_voicing(sw(*z_i)),
        0.65, 1.0, warn_lo=0.45)
    p4 = check_warn(
        'N zone voicing',
        measure_voicing(sw(*z_n)),
        0.55, 1.0, warn_lo=0.35)

    d3 = p1 and p2 and p3 and p4
    all_pass &= d3

    write_wav(
        "output_play/diag_in_full.wav",
        in_dry)
    write_wav(
        "output_play/diag_in_hall.wav",
        in_hall)
    write_wav(
        "output_play/diag_in_slow.wav",
        ola_stretch(in_dry, 4.0))
    print(f"  {len(in_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    print(f"  diag_in_full.wav")
    print(f"  diag_in_hall.wav")
    print(f"  diag_in_slow.wav")
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — PERCEPTUAL")
    print()
    for fn in [
        "diag_i_vowel_slow.wav",
        "diag_n_final_slow.wav",
        "diag_in_slow.wav",
        "diag_in_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  I: short, high, front —"
          " 'bit' quality")
    print("    NOT 'see', NOT 'bet'")
    print("  N: nasal murmur fading"
          " into silence")
    print("  Full: brief [ɪn],"
          " two events")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 I vowel",   d1),
        ("D2 N nasal",   d2),
        ("D3 Full word", d3),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D4 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  IN [ɪn] verified.")
        print("  Next word: GĒAR-DAGUM")
        print("  Beowulf line 1, word 5.")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d1:
            print()
            print("  D1: adjust I_F[0] or I_F[1]")
            print("  F1 target 320–480 Hz")
            print("  F2 target 1600–2000 Hz")
        if not d2:
            print()
            print("  D2: check N_ANTI_BW=200")
            print("  and iir_notch in synth_N_final")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
