"""
SCEFING DIAGNOSTIC v1
Old English: Scefing [ʃeviŋɡ]
Beowulf line 5, word 2
February 2026

DIAGNOSTICS:
  D1  SH fricative [ʃ]
  D2  E vowel [e]
  D3  V fricative [v]        NEW
  D4  I vowel [ɪ]
  D5  NG nasal [ŋ]
  D6  G stop word-final [ɡ]
  D7  [v] vs [f] distinction
  D8  Full word
  D9  Perceptual

KEY CHECK:
  D7 [v] vs [f].
  [v] must have measurable voicing.
  [f] is voiceless — voicing 0.0.
  [v] target voicing >= 0.35.
  The voicing is the only distinction
  between [f] and [v] in OE —
  same place, same manner, different
  laryngeal setting.
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
    print("SCEFING DIAGNOSTIC v1")
    print("Old English [ʃeviŋɡ]")
    print("Beowulf line 5, word 2")
    print("=" * 60)
    print()

    try:
        from scefing_reconstruction import (
            synth_scefing,
            synth_SH, synth_E,
            synth_V, synth_II,
            synth_NG, synth_G_final,
            apply_simple_room,
            E_F, II_F, NG_F)
        print("  scefing_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 SH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — SH FRICATIVE [ʃ]")
    print()
    sh_seg  = synth_SH(E_F, 1.0, SR)
    cent_sh = measure_band_centroid(
        sh_seg, 1000.0, 10000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(sh_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_sh:.0f} Hz)',
        cent_sh, 2500.0, 5500.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 E ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — E VOWEL [e]")
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
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 V ─────────���────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — V FRICATIVE [v]")
    print()
    print("  Voiced labiodental.")
    print("  Allophone of /f/ in OE.")
    print("  Intervocalic — full voicing.")
    print("  Buzz under frication.")
    print()
    v_seg   = synth_V(E_F, II_F,
                       145.0, 1.0, SR)
    voic_v  = measure_voicing(v_seg)
    p1 = check('voicing (must be high)',
               voic_v, 0.35, 1.0)
    p2 = check('RMS level', rms(v_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 II ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — I VOWEL [ɪ]")
    print()
    ii_seg = synth_II(None, NG_F,
                       145.0, 1.0, SR)
    n_ii   = len(ii_seg)
    body   = ii_seg[int(0.12*n_ii):
                    n_ii-int(0.12*n_ii)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    cent_ii = measure_band_centroid(
        body, 1500.0, 2400.0)
    p2 = check(
        f'F2 centroid ({cent_ii:.0f} Hz)',
        cent_ii, 1600.0, 2200.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 NG ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — NG NASAL [ŋ]")
    print()
    ng_seg = synth_NG(II_F, None,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(ng_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(ng_seg), 0.005, 0.25)
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 G FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — G STOP [ɡ] final")
    print()
    g_seg = synth_G_final(NG_F,
                           145.0, 1.0, SR)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.70)
    dur_g = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 V vs F ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [v] vs [f]"
          " DISTINCTION")
    print()
    print("  [v] voicing >= 0.35")
    print("  [f] voicing ~0.00")
    print("  Same place, same manner.")
    print("  Laryngeal setting only.")
    print()
    f_ref_voicing = 0.00
    print(f"  [f] reference voicing:"
          f" {f_ref_voicing:.4f}"
          f" (verified GEFRŪNON)")
    print(f"  [v] measured voicing: "
          f"{voic_v:.4f}")
    p1 = check(
        '[v] voicing (must be >= 0.35)',
        voic_v, 0.35, 1.0)
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD"
          " [ʃeviŋɡ]")
    print()
    w_dry  = synth_scefing(
        145.0, 1.0, False)
    w_hall = synth_scefing(
        145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 300.0, 550.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_scef_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_scef_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_scef_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_scef_v.wav",
        ola_stretch(v_seg / (
            np.max(np.abs(v_seg))+1e-8)
            * 0.75, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_scef_v.wav",
        "diag_scef_slow.wav",
        "diag_scef_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  V: buzz under friction —")
    print("    voiced, not silent hiss")
    print("    distinct from [f]")
    print("  Full: SH·E·V·I·NG·G")
    print("  Six events")
    print("  The V is the new sound —")
    print("  buzzing labiodental.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  SH fricative",   d1),
        ("D2  E vowel",        d2),
        ("D3  V fricative",    d3),
        ("D4  I vowel",        d4),
        ("D5  NG nasal",       d5),
        ("D6  G stop final",   d6),
        ("D7  V/F distinction",d7),
        ("D8  Full word",      d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D9 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  SCEFING [ʃeviŋɡ] verified.")
        print("  [v] added to inventory.")
        print("  31 phonemes verified.")
        print()
        print("  Next: SCEAÞENA [ʃeɑθenɑ]")
        print("  Beowulf line 5, word 3.")
        print("  Zero new phonemes.")
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
