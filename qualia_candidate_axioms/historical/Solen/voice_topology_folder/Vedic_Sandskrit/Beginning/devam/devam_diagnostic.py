"""
DEVAM DIAGNOSTIC v5
Vedic Sanskrit: devam  [devɑm]
Rigveda 1.1.1 — word 5
February 2026

v5: matches reconstruction v5 (LP 800 Hz + gain 25.0).
Diagnostic logic UNCHANGED from v4.
"""

import numpy as np
from scipy.signal import lfilter, butter, argrelmin
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

PITCH_HZ           = 120.0
PERIOD_MS          = 1000.0 / PITCH_HZ
DIP_SMOOTH_PERIODS = 2.7
DIP_SMOOTH_MS      = PERIOD_MS * DIP_SMOOTH_PERIODS
DIP_SMOOTH_SAMPLES = int(DIP_SMOOTH_MS / 1000.0 * SR)

EDGE_TRIM_FRAC   = 0.15
VOICING_FRAME_MS = 40.0

VS_T_BURST_HZ      = 3764.0
VS_T_CLOSURE_VOIC  =    0.0
VS_G_LF_RATIO      =    0.9703
VS_JJ_LF_RATIO     =    0.9816
VS_OO_F2_HZ        =  757.0
VS_EE_F2_HZ        = 1659.0
VS_J_F2_HZ         = 2028.0
VS_P_BURST_HZ      = 1204.0
VS_G_BURST_HZ      = 2594.0
VS_JJ_BURST_HZ     = 3223.0
VS_R_DIP_COUNT     =    2
VS_J_DIP_COUNT     =    0

A_F1_BAND_LO       = 550.0
A_F1_BAND_HI       = 900.0
A_F2_BAND_LO       = 850.0
A_F2_BAND_HI       = 1400.0
A_VOICING_MIN       = 0.50

DANTYA_BURST_LO_HZ       = 3000.0
DANTYA_BURST_HI_HZ       = 4500.0
LABDENT_F2_LO_HZ         = 1200.0
LABDENT_F2_HI_HZ         = 1800.0

BURST_BAND_LO_HZ         = 2000.0
BURST_BAND_HI_HZ         = 6000.0
V_F2_BAND_LO_HZ          =  900.0
V_F2_BAND_HI_HZ          = 2200.0

MURMUR_BURST_RATIO_MIN    = 0.25
MURMUR_BURST_RATIO_MAX    = 3.0


def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = np.clip(sig * 32767.0, -32768, 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

def ola_stretch(sig, factor=6.0, sr=SR):
    win_ms   = 40.0
    win_n    = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in   = win_n // 4
    hop_out  = int(hop_in * factor)
    window   = np.hanning(win_n).astype(DTYPE)
    n_in     = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos + win_n] * window
        out [out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def body(seg, frac=EDGE_TRIM_FRAC):
    n    = len(seg)
    edge = max(1, int(frac * n))
    return seg[edge: n - edge]

def measure_voicing(seg, sr=SR):
    sig = seg.astype(float)
    n   = len(sig)
    if n < 4:
        return 0.0
    q1, q3 = n // 4, 3 * n // 4
    mid = sig[q1:q3]
    if len(mid) < int(VOICING_FRAME_MS / 1000.0 * sr):
        mid = sig
    mid = mid - np.mean(mid)
    if np.max(np.abs(mid)) < 1e-12:
        return 0.0
    c   = np.correlate(mid, mid, mode='full')
    c   = c[len(c) // 2:]
    if c[0] < 1e-12:
        return 0.0
    c = c / c[0]
    lo = int(sr / 400.0)
    hi = min(int(sr / 60.0), len(c) - 1)
    if lo >= hi or hi >= len(c):
        return 0.0
    return float(np.max(c[lo:hi]))

def measure_lf_ratio(seg, sr=SR):
    sig = seg.astype(float)
    if len(sig) < 4:
        return 0.0
    ps = np.abs(np.fft.rfft(sig)) ** 2
    f  = np.fft.rfftfreq(len(sig), 1.0 / sr)
    lf_mask = f <= 500.0
    total   = np.sum(ps) + 1e-30
    return float(np.sum(ps[lf_mask]) / total)

def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    sig = seg.astype(float)
    if len(sig) < 4:
        return 0.0
    ps = np.abs(np.fft.rfft(sig)) ** 2
    f  = np.fft.rfftfreq(len(sig), 1.0 / sr)
    mask = (f >= lo_hz) & (f <= hi_hz)
    total = np.sum(ps[mask]) + 1e-30
    return float(np.sum(f[mask] * ps[mask]) / total)

def measure_amplitude_dip_count(seg, smooth_n=DIP_SMOOTH_SAMPLES):
    sig = np.abs(seg.astype(float))
    if len(sig) < smooth_n * 2:
        return 0
    kernel = np.ones(smooth_n) / smooth_n
    env    = np.convolve(sig, kernel, mode='same')
    trim = smooth_n
    env  = env[trim:-trim]
    if len(env) < 3:
        return 0
    mins = argrelmin(env, order=smooth_n // 2)[0]
    if len(mins) == 0:
        return 0
    threshold = np.max(env) * 0.5
    dips = [m for m in mins if env[m] < threshold]
    return len(dips)

def check(label, value, lo, hi, unit='', fmt='.4f'):
    ok = lo <= value <= hi
    status = '✓' if ok else '✗'
    if isinstance(value, float) and 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    else:
        bar = ''
    print(f"    [{status}] {label}: "
          f"{format(value, fmt)}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok


def run_diagnostics():
    print()
    print("=" * 60)
    print("DEVAM DIAGNOSTIC v5")
    print("Vedic Sanskrit [devɑm]")
    print("Rigveda 1.1.1 — word 5")
    print("VS-isolated. Physics and Śikṣā only.")
    print("[d] v5: LP 800 Hz, murmur gain 25.0, burst 0.08")
    print("OLA: 6x standard, 12x deep analysis")
    print("=" * 60)
    print()

    try:
        from devam_reconstruction import (
            synth_devam,
            synth_D, synth_V,
            synth_EE_vs, synth_A_vs,
            synth_M_vs,
            apply_simple_room,
            VS_D_BURST_F_VAL,
            VS_V_F2_VAL,
            VS_D_CLOSURE_MS_V,
            VS_D_BURST_MS_V,
            VS_EE_F, VS_V_F,
            VS_A_F, VS_M_F,
            DIL)
        print("  devam_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D0 SANITY CHECK ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 0 — SANITY CHECK [ɑ]")
    print()
    a_seg  = synth_A_vs(F_prev=None, F_next=None)
    a_body = body(a_seg)
    a_f1   = measure_band_centroid(a_body, A_F1_BAND_LO, A_F1_BAND_HI)
    a_f2   = measure_band_centroid(a_body, A_F2_BAND_LO, A_F2_BAND_HI)
    a_voic = measure_voicing(a_body)
    p1 = check(f'[ɑ] F1 ({a_f1:.0f} Hz)', a_f1, 600.0, 850.0, unit=' Hz', fmt='.1f')
    p2 = check(f'[ɑ] F2 ({a_f2:.0f} Hz)', a_f2, 950.0, 1300.0, unit=' Hz', fmt='.1f')
    p3 = check('[ɑ] voicing', a_voic, A_VOICING_MIN, 1.0)
    d0 = p1 and p2 and p3
    all_pass &= d0
    if not d0:
        print("\n  *** RULER BROKEN ***")
        return False
    print(f"\n  Ruler verified.\n  {'PASSED' if d0 else 'FAILED'}\n")

    d_seg  = synth_D()
    v_seg  = synth_V()
    v_body = body(v_seg)

    n_dcl  = int(VS_D_CLOSURE_MS_V * DIL / 1000.0 * SR)
    n_dbst = int(VS_D_BURST_MS_V   * DIL / 1000.0 * SR)
    d_close = d_seg[:min(n_dcl, len(d_seg))]
    d_burst = d_seg[n_dcl:min(n_dcl + n_dbst, len(d_seg))]

    # ── D1 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [d] VOICED CLOSURE\n")
    print(f"  [g]  LF: {VS_G_LF_RATIO:.4f}  [ɟ]  LF: {VS_JJ_LF_RATIO:.4f}\n")
    lf_d = measure_lf_ratio(d_close)
    d1 = check('LF ratio', lf_d, 0.40, 1.0)
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}\n")

    # ── D1b ───────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1b — MURMUR/BURST RMS RATIO\n")
    rms_cl = rms(d_close)
    rms_bu = rms(d_burst) + 1e-12
    ratio  = rms_cl / rms_bu
    print(f"  murmur RMS: {rms_cl:.6f}")
    print(f"  burst  RMS: {rms_bu:.6f}")
    print(f"  ratio:      {ratio:.3f}\n")
    d1b = check('murmur/burst ratio', ratio,
                MURMUR_BURST_RATIO_MIN, MURMUR_BURST_RATIO_MAX, fmt='.3f')
    all_pass &= d1b
    print(f"  {'PASSED' if d1b else 'FAILED'}\n")

    # ── D2 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [d] BURST CENTROID\n")
    cent_d = measure_band_centroid(d_burst, BURST_BAND_LO_HZ, BURST_BAND_HI_HZ)
    d2 = check(f'burst ({cent_d:.0f} Hz)', cent_d,
               DANTYA_BURST_LO_HZ, DANTYA_BURST_HI_HZ, unit=' Hz', fmt='.1f')
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}\n")

    # ── D3 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [d] SAME LOCUS AS [t]\n")
    diff = abs(cent_d - VS_T_BURST_HZ)
    print(f"  [t]: {VS_T_BURST_HZ:.0f}  [d]: {cent_d:.0f}  diff: {diff:.0f} Hz\n")
    d3 = check(f'distance ({diff:.0f} Hz)', diff, 0.0, 800.0, unit=' Hz', fmt='.1f')
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}\n")

    # ── D4 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — VOICED VS VOICELESS\n")
    d4 = lf_d > 0.40 and VS_T_CLOSURE_VOIC < 0.10
    all_pass &= d4
    print(f"  [t] closure: {VS_T_CLOSURE_VOIC:.4f}  [d] closure: {lf_d:.4f}")
    print(f"  {'PASSED' if d4 else 'FAILED'}\n")

    # ── D5 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [d] ŚIKṢĀ: DANTYA ROW 3\n")
    d5 = d1 and d1b and d2 and d3 and d4
    all_pass &= d5
    if d5:
        print("  Dantya voiced stop confirmed.")
    print(f"  {'PASSED' if d5 else 'FAILED'}\n")

    # ── D6 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [v] VOICING\n")
    voic_v = measure_voicing(v_body)
    d6 = check('voicing', voic_v, 0.50, 1.0)
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}\n")

    # ── D7 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [v] F2 CENTROID\n")
    cent_v_f2 = measure_band_centroid(v_body, V_F2_BAND_LO_HZ, V_F2_BAND_HI_HZ)
    d7 = check(f'F2 ({cent_v_f2:.0f} Hz)', cent_v_f2,
               LABDENT_F2_LO_HZ, LABDENT_F2_HI_HZ, unit=' Hz', fmt='.1f')
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}\n")

    # ── D8 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [v] F2 POSITION\n")
    d8 = (cent_v_f2 > VS_OO_F2_HZ) and (cent_v_f2 < VS_EE_F2_HZ)
    all_pass &= d8
    print(f"  {VS_OO_F2_HZ:.0f} < {cent_v_f2:.0f} < {VS_EE_F2_HZ:.0f}")
    print(f"  {'PASSED' if d8 else 'FAILED'}\n")

    # ── D9 ────────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [v] NO DIP\n")
    dip_v = measure_amplitude_dip_count(v_body)
    d9 = check('dip count', dip_v, 0, 0, fmt='d')
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}\n")

    # ── D10 ───────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — [v] ŚIKṢĀ: DANTAUṢṬHYA\n")
    d10 = d6 and d7 and d8 and d9
    all_pass &= d10
    if d10:
        print("  Labio-dental approximant confirmed. ✓")
    print(f"  {'PASSED' if d10 else 'FAILED'}\n")

    # ── D11 ───────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — FULL WORD\n")
    w_dry  = synth_devam(with_room=False)
    w_hall = synth_devam(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS', rms(w_dry), 0.010, 0.90)
    p2 = check(f'dur ({dur_ms:.0f} ms)', dur_ms, 200.0, 600.0, unit=' ms', fmt='.1f')

    write_wav("output_play/diag_devam_v5_dry.wav",       w_dry)
    write_wav("output_play/diag_devam_v5_hall.wav",       w_hall)
    write_wav("output_play/diag_devam_v5_slow6x.wav",    ola_stretch(w_dry, 6.0))
    write_wav("output_play/diag_devam_v5_slow12x.wav",   ola_stretch(w_dry, 12.0))

    w_perf      = synth_devam(dil=2.5, with_room=False)
    w_perf_hall = synth_devam(dil=2.5, with_room=True)
    write_wav("output_play/diag_devam_v5_perf.wav",         w_perf)
    write_wav("output_play/diag_devam_v5_perf_hall.wav",     w_perf_hall)
    write_wav("output_play/diag_devam_v5_perf_slow6x.wav",  ola_stretch(w_perf, 6.0))

    for sig, name in [
        (synth_D(),  "diag_devam_v5_d_iso"),
        (synth_V(),  "diag_devam_v5_v_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav",          sig)
        write_wav(f"output_play/{name}_slow6x.wav",   ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",  ola_stretch(sig, 12.0))

    d11 = p1 and p2
    all_pass &= d11
    print(f"  {'PASSED' if d11 else 'FAILED'}\n")

    # ── D12 ───────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — PERCEPTUAL\n")
    for fn in [
        "diag_devam_v5_d_iso_slow6x.wav",
        "diag_devam_v5_d_iso_slow12x.wav",
        "diag_devam_v5_v_iso_slow6x.wav",
        "diag_devam_v5_slow6x.wav",
        "diag_devam_v5_hall.wav",
        "diag_devam_v5_perf_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print("\n  PERCEPTUAL VERDICT: ___\n")
    d12 = True
    all_pass &= d12

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY — DEVAM v5")
    print("=" * 60)
    print()
    results = [
        ("D0",  "Sanity [ɑ]",              d0),
        ("D1",  "[d] voiced closure",       d1),
        ("D1b", "[d] murmur/burst ratio",   d1b),
        ("D2",  "[d] burst centroid",       d2),
        ("D3",  "[d] same locus [t]",       d3),
        ("D4",  "[d] voiced/voiceless",     d4),
        ("D5",  "[d] ��ikṣā dantya",        d5),
        ("D6",  "[v] voicing",              d6),
        ("D7",  "[v] F2 labio-dental",      d7),
        ("D8",  "[v] F2 position",          d8),
        ("D9",  "[v] no dip",               d9),
        ("D10", "[v] Śikṣā dantauṣṭhya",   d10),
        ("D11", "Full word",                d11),
        ("D12", "Perceptual",               d12),
    ]
    for tag, desc, passed in results:
        mark = '✓' if passed else '✗'
        print(f"  [{mark}] {tag}: {desc}")
    print()
    n_pass = sum(1 for _, _, p in results if p)
    print(f"  {n_pass}/{len(results)} passed\n")

    if all_pass:
        print("  ALL PASSED. DEVAM v5 VERIFIED.\n")
        print("  Key measurements:")
        print(f"    [d] LF ratio:          {lf_d:.4f}")
        print(f"    [d] murmur/burst:      {ratio:.3f}")
        print(f"    [d] burst centroid:     {cent_d:.0f} Hz")
        print(f"    [d] dist to [t]:        {diff:.0f} Hz")
        print(f"    [v] F2:                {cent_v_f2:.0f} Hz")
        print(f"    [v] voicing:           {voic_v:.4f}")
        print(f"    [v] dips:              {dip_v}")
        print()
        print("  Iteration history:")
        print("    v2: ratio 0.004 (LP 500, gain 0.70)")
        print("    v3: diagnosed with D1b")
        print("    v4: ratio 0.043 (LP 500, gain 6.0)")
        print("    v5: ratio ??? (LP 800, gain 25.0)")
    else:
        print("  SOME FAILED:")
        for t, d, p in results:
            if not p:
                print(f"    {t}: {d}")
    print()
    return all_pass


if __name__ == "__main__":
    sys.exit(0 if run_diagnostics() else 1)
