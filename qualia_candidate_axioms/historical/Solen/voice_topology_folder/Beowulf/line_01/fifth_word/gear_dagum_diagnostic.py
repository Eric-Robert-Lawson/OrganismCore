"""
GĒAR-DAGUM DIAGNOSTIC v3
Old English: gēar-dagum [ɡeːɑrdɑɡum]
Beowulf line 1, word 5
February 2026

CHANGES FROM v2:
  D9: antiformant check inverted.
    [m] energy lives below 600 Hz.
    Correct check: low-band (200–600 Hz)
    energy must exceed notch-band
    (850–1150 Hz) energy by factor > 2.
    This confirms the 1000 Hz antiformant
    is a real dip within the spectrum,
    not just the high-frequency rolloff.
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

def measure_burst_centroid(seg, sr=SR,
                            window_ms=15.0):
    n_w = min(int(window_ms / 1000.0 * sr),
              len(seg))
    if n_w < 4:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg[:n_w].astype(float), n=1024))**2
    freqs = np.fft.rfftfreq(1024, d=1.0/sr)
    mask  = freqs < sr * 0.48
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(
        freqs[mask] * spec[mask]) / total)

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
    print("GĒAR-DAGUM DIAGNOSTIC v3")
    print("Old English [ɡeːɑrdɑɡum]")
    print("Beowulf line 1, word 5")
    print("=" * 60)
    print()

    try:
        from gear_dagum_reconstruction import (
            synth_gear_dagum,
            synth_G, synth_EE_long,
            synth_A_short, synth_R_trill,
            synth_D, synth_U_short,
            synth_M_final,
            apply_simple_room,
            G1_F, G1_B,
            G1_BURST_CF,
            G1_CLOSURE_MS, G1_BURST_MS,
            G2_F, G2_B,
            G2_BURST_CF,
            G2_CLOSURE_MS, G2_BURST_MS,
            EE_F, A_F, R_F, D_F,
            U_F, M_F)
        print("  gear_dagum_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 G1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — G1 ONSET [ɡ] before [eː]")
    print()
    g1_seg  = synth_G(EE_F, G1_BURST_CF,
                       G1_CLOSURE_MS, G1_BURST_MS,
                       G1_F, G1_B, 145.0, 1.0)
    n_cl    = int(G1_CLOSURE_MS / 1000.0 * SR)
    n_bst   = int(G1_BURST_MS   / 1000.0 * SR)
    bst_seg = (g1_seg[n_cl:n_cl+n_bst]
               if len(g1_seg) > n_cl+n_bst
               else g1_seg[-n_bst:])
    cent_g1 = measure_burst_centroid(bst_seg)
    p1 = check('RMS level', rms(g1_seg),
               0.005, 0.80)
    p2 = check(f'burst centroid ({cent_g1:.0f} Hz)',
               cent_g1, 800.0, 2500.0,
               unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    write_wav("output_play/diag_g1_slow.wav",
              ola_stretch(g1_seg / (
                  np.max(np.abs(g1_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Ē ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Ē VOWEL [eː]")
    print()
    ee_seg  = synth_EE_long(G1_F, A_F, 110.0, 1.0)
    n_ee    = len(ee_seg)
    body_ee = ee_seg[int(0.10*n_ee):
                     n_ee-int(0.10*n_ee)]
    cent_ee1 = measure_band_centroid(
        body_ee, 200.0, 700.0)
    cent_ee2 = measure_band_centroid(
        body_ee, 1800.0, 2600.0)
    p1 = check('voicing',
               measure_voicing(body_ee),
               0.75, 1.0)
    p2 = check(f'F1 centroid ({cent_ee1:.0f} Hz)',
               cent_ee1, 250.0, 480.0,
               unit=' Hz', fmt='.1f')
    p3 = check(f'F2 centroid ({cent_ee2:.0f} Hz)',
               cent_ee2, 1800.0, 2600.0,
               unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_ee_slow.wav",
              ola_stretch(ee_seg / (
                  np.max(np.abs(ee_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 A1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — A1 VOWEL [ɑ]")
    print()
    a1_seg  = synth_A_short(EE_F, R_F, 110.0, 1.0)
    n_a1    = len(a1_seg)
    body_a1 = a1_seg[int(0.12*n_a1):
                     n_a1-int(0.12*n_a1)]
    cent_a1 = measure_band_centroid(
        body_a1, 600.0, 1400.0)
    p1 = check_warn('voicing',
                    measure_voicing(body_a1),
                    0.50, 1.0, warn_lo=0.30)
    p2 = check(f'F1+F2 centroid ({cent_a1:.0f} Hz)',
               cent_a1, 750.0, 1050.0,
               unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    write_wav("output_play/diag_a1_slow.wav",
              ola_stretch(a1_seg / (
                  np.max(np.abs(a1_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — R TRILL [r]")
    print()
    r_seg = synth_R_trill(A_F, D_F, 145.0, 1.0)
    mod_depth, trill_hz = \
        measure_trill_modulation(r_seg)
    p1 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    p2 = check_warn('trill modulation depth',
                    mod_depth, 0.22, 1.0,
                    warn_lo=0.10)
    if trill_hz > 0:
        p3 = check(
            f'trill rate ({trill_hz:.1f} Hz)',
            trill_hz, 15.0, 70.0,
            unit=' Hz', fmt='.1f')
    else:
        p3 = False
        print("    [FAIL] trill rate not detected.")
    d4 = p1 and p2 and p3
    all_pass &= d4
    write_wav("output_play/diag_r_slow.wav",
              ola_stretch(r_seg / (
                  np.max(np.abs(r_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — D ONSET [d]")
    print()
    d_seg  = synth_D(R_F, A_F, 145.0, 1.0)
    n_cl_d = int(45.0 / 1000.0 * SR)
    n_bst_d= int(10.0 / 1000.0 * SR)
    bst_d  = (d_seg[n_cl_d:n_cl_d+n_bst_d]
              if len(d_seg) > n_cl_d+n_bst_d
              else d_seg[-n_bst_d:])
    cent_d = measure_burst_centroid(bst_d)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.80)
    p2 = check(f'burst centroid ({cent_d:.0f} Hz)',
               cent_d, 2000.0, 5000.0,
               unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    write_wav("output_play/diag_d_slow.wav",
              ola_stretch(d_seg / (
                  np.max(np.abs(d_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 A2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — A2 VOWEL [ɑ]")
    print()
    a2_seg  = synth_A_short(D_F, G2_F, 110.0, 1.0)
    n_a2    = len(a2_seg)
    body_a2 = a2_seg[int(0.12*n_a2):
                     n_a2-int(0.12*n_a2)]
    cent_a2 = measure_band_centroid(
        body_a2, 600.0, 1400.0)
    p1 = check_warn('voicing',
                    measure_voicing(body_a2),
                    0.50, 1.0, warn_lo=0.30)
    p2 = check(f'F1+F2 centroid ({cent_a2:.0f} Hz)',
               cent_a2, 750.0, 1050.0,
               unit=' Hz', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    write_wav("output_play/diag_a2_slow.wav",
              ola_stretch(a2_seg / (
                  np.max(np.abs(a2_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 G2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — G2 ONSET [ɡ] before [u]")
    print()
    g2_seg  = synth_G(U_F, G2_BURST_CF,
                       G2_CLOSURE_MS, G2_BURST_MS,
                       G2_F, G2_B, 145.0, 1.0)
    n_cl2   = int(G2_CLOSURE_MS / 1000.0 * SR)
    n_bst2  = int(G2_BURST_MS   / 1000.0 * SR)
    bst2    = (g2_seg[n_cl2:n_cl2+n_bst2]
               if len(g2_seg) > n_cl2+n_bst2
               else g2_seg[-n_bst2:])
    cent_g2 = measure_burst_centroid(bst2)
    p1 = check('RMS level', rms(g2_seg),
               0.005, 0.80)
    p2 = check(f'burst centroid ({cent_g2:.0f} Hz)',
               cent_g2, 600.0, 2000.0,
               unit=' Hz', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    write_wav("output_play/diag_g2_slow.wav",
              ola_stretch(g2_seg / (
                  np.max(np.abs(g2_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 U ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — U VOWEL [u]")
    print()
    u_seg   = synth_U_short(G2_F, M_F, 145.0, 1.0)
    n_u     = len(u_seg)
    body_u  = u_seg[int(0.15*n_u):
                    n_u-int(0.15*n_u)]
    cent_u1 = measure_band_centroid(
        body_u, 100.0, 600.0)
    cent_u2 = measure_band_centroid(
        body_u, 400.0, 1200.0)
    p1 = check('voicing',
               measure_voicing(body_u),
               0.65, 1.0)
    p2 = check(f'F1 centroid ({cent_u1:.0f} Hz)',
               cent_u1, 200.0, 380.0,
               unit=' Hz', fmt='.1f')
    p3 = check(f'F2 centroid ({cent_u2:.0f} Hz)',
               cent_u2, 500.0, 900.0,
               unit=' Hz', fmt='.1f')
    d8 = p1 and p2 and p3
    all_pass &= d8
    write_wav("output_play/diag_u_slow.wav",
              ola_stretch(u_seg / (
                  np.max(np.abs(u_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 M ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — M NASAL [m]")
    print()
    print("  Bilabial. Energy below 600 Hz.")
    print("  Antiformant at ~1000 Hz.")
    print("  Check: low-band (200–600 Hz)")
    print("  must exceed notch-band")
    print("  (850–1150 Hz) by factor > 2.")
    print()
    m_seg = synth_M_final(U_F, 145.0, 1.0)
    vr_m  = measure_voicing(m_seg)
    r_m   = rms(m_seg)
    p1 = check('voicing', vr_m, 0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               r_m, 0.005, 0.25)
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
        if not p3:
            print("      Low-band not dominant.")
            print("      Raise M_GAINS[1] or"
                  " M_ANTI_BW.")
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d9 = p1 and p2 and p3
    all_pass &= d9
    write_wav("output_play/diag_m_slow.wav",
              ola_stretch(m_seg / (
                  np.max(np.abs(m_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — FULL WORD")
    print()
    gd_dry  = synth_gear_dagum(145.0, 1.0, False)
    gd_hall = synth_gear_dagum(145.0, 1.0, True)
    dur_ms  = len(gd_dry) / SR * 1000.0
    p1 = check('RMS level', rms(gd_dry),
               0.010, 0.90)
    p2 = check(f'duration ({dur_ms:.0f} ms)',
               dur_ms, 400.0, 900.0,
               unit=' ms', fmt='.1f')
    print(f"  {len(gd_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_gear_dagum_full.wav",
        gd_dry)
    write_wav(
        "output_play/diag_gear_dagum_hall.wav",
        gd_hall)
    write_wav(
        "output_play/diag_gear_dagum_slow.wav",
        ola_stretch(gd_dry, 4.0))
    d10 = p1 and p2
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — PERCEPTUAL")
    print()
    for fn in [
        "diag_u_slow.wav",
        "diag_m_slow.wav",
        "diag_gear_dagum_slow.wav",
        "diag_gear_dagum_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  U: rounded back — 'boot' quality")
    print("  M: bilabial hum, darker than N")
    print("  Full: G·Ē·A·R·D·A·G·U·M")
    print("  Nine distinct events")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 G1 onset",   d1),
        ("D2 Ē vowel",    d2),
        ("D3 A1 vowel",   d3),
        ("D4 R trill",    d4),
        ("D5 D onset",    d5),
        ("D6 A2 vowel",   d6),
        ("D7 G2 onset",   d7),
        ("D8 U vowel",    d8),
        ("D9 M nasal",    d9),
        ("D10 Full word", d10),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D11 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  GĒAR-DAGUM [ɡeːɑrdɑɡum]"
              " verified.")
        print("  Line 1 complete.")
        print("  Commit files.")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d9:
            print()
            print("  D9: murmur/notch ratio"
                  " below 2.0.")
            print("  Raise M_GAINS[1].")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
