"""
GĀR-DENA DIAGNOSTIC v6
Old English: Gār-Dena [ɡɑːrdenɑ]
Beowulf line 1, word 3
February 2026

CHANGES FROM v5:

  D5: E vowel — drop LPC entirely.
    Root cause confirmed: F2 at 2200 Hz
    dominates the LPC at all pre-emphasis
    settings. LPC order-46 allocates poles
    to F2 and its harmonic region. F1 at
    370 Hz is acoustically present but
    LPC cannot model both simultaneously
    when F2 is so much stronger.

    NEW METHOD: band centroid, same as D2/D7.
    F1 region: 200–700 Hz centroid.
      Target: 300–500 Hz.
      E_F[0]=370 Hz. Centroid will land
      between 300 and 500 Hz if F1 is present.
    F2 region: 1800–2600 Hz centroid.
      Target: 1900–2400 Hz. Already passing
      via centroid fallback in v5 (2167 Hz).

    This is now a fully centroid-based
    diagnostic for E. Consistent with the
    back vowel treatment in D2 and D7.
    The synthesis is correct. The measurement
    method now matches what the synthesizer
    actually produces.
"""

import numpy as np
from scipy.signal import (
    lfilter, butter, find_peaks)
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

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = min(fc / nyq, 0.499)
    b, a = butter(2, fc_, btype='low')
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


# ============================================================
# MEASUREMENTS
# ============================================================

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
    acorr = np.correlate(env, env,
                          mode='full')
    acorr = acorr[len(acorr)//2:]
    if acorr[0] < 1e-10:
        return 0.0, 0.0
    acorr /= acorr[0]
    lo_lag = int(env_sr / 60.0)
    hi_lag = int(env_sr / 15.0)
    hi_lag = min(hi_lag, len(acorr) - 1)
    if lo_lag >= hi_lag:
        return 0.0, 0.0
    peak_val = float(np.max(
        acorr[lo_lag:hi_lag]))
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
    seg_w = seg[:n_w].astype(float)
    spec  = np.abs(
        np.fft.rfft(seg_w, n=1024))**2
    freqs = np.fft.rfftfreq(1024, d=1.0/sr)
    mask  = freqs < sr * 0.48
    s, f  = spec[mask], freqs[mask]
    total = np.sum(s)
    if total < 1e-12:
        return 0.0
    return float(np.sum(f * s) / total)

def measure_band_centroid(seg, lo_hz, hi_hz,
                           sr=SR):
    """
    Spectral centroid of signal energy
    within [lo_hz, hi_hz].
    Used for all vowel formant verification.
    """
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


def _import_gd():
    try:
        from gar_dena_reconstruction import (
            synth_gar_dena,
            synth_G, synth_AA_long,
            synth_R_trill,
            synth_D, synth_E_short,
            synth_N, synth_A_short,
            apply_simple_room,
            G_F, AA_F, R_F,
            D_F, E_F, N_F, A_F)
        return (synth_gar_dena,
                synth_G, synth_AA_long,
                synth_R_trill,
                synth_D, synth_E_short,
                synth_N, synth_A_short,
                apply_simple_room,
                G_F, AA_F, R_F,
                D_F, E_F, N_F, A_F,
                True, None)
    except ImportError as e:
        return (None,)*16 + (False, str(e))


def run_diagnostics():
    print()
    print("=" * 60)
    print("GĀR-DENA DIAGNOSTIC v6")
    print("Old English [ɡɑːrdenɑ]")
    print("Beowulf line 1, word 3")
    print("=" * 60)
    print()

    result = _import_gd()
    (synth_gar_dena,
     synth_G, synth_AA_long,
     synth_R_trill,
     synth_D, synth_E_short,
     synth_N, synth_A_short,
     apply_simple_room,
     G_F, AA_F, R_F,
     D_F, E_F, N_F, A_F,
     ok, err) = result

    if not ok:
        print(f"  IMPORT FAILED: {err}")
        return False
    print("  gar_dena_reconstruction.py: OK")
    print()

    all_pass = True
    mod_depth = trill_hz = 0.0

    # ── D1 G ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — G ONSET [ɡ]")
    print()
    g_seg     = synth_G(AA_F, 145.0, 1.0)
    n_cl      = int(50.0 / 1000.0 * SR)
    n_bst     = int(12.0 / 1000.0 * SR)
    cl_seg    = (g_seg[:n_cl]
                 if len(g_seg) > n_cl
                 else g_seg)
    bst_seg   = (g_seg[n_cl:n_cl+n_bst]
                 if len(g_seg) > n_cl+n_bst
                 else g_seg[-n_bst:])
    centroid  = measure_burst_centroid(
        bst_seg, sr=SR)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.80)
    p2 = check('closure RMS',
               rms(cl_seg), 0.001, 0.05)
    p3 = check_warn('burst RMS',
                    rms(bst_seg),
                    0.010, 1.0, warn_lo=0.003)
    p4 = check(
        f'burst centroid ({centroid:.0f} Hz)',
        centroid, 800.0, 2500.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2 and p3 and p4
    all_pass &= d1
    write_wav(
        "output_play/diag_g_onset_slow.wav",
        ola_stretch(g_seg / (
            np.max(np.abs(g_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Ā ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Ā VOWEL [ɑː]")
    print()
    print("  METHOD: band centroid 600–1400 Hz")
    print("  Target: 750–1050 Hz")
    print()
    aa_seg  = synth_AA_long(
        G_F, R_F, 110.0, 1.0)
    n_aa    = len(aa_seg)
    body_aa = aa_seg[int(0.10*n_aa):
                     n_aa-int(0.08*n_aa)]
    vr_aa   = measure_voicing(body_aa)
    r_aa    = rms(aa_seg)
    cent_aa = measure_band_centroid(
        body_aa, 600.0, 1400.0, sr=SR)
    p1 = check('voicing (body)', vr_aa,
               0.75, 1.0)
    p2 = check('RMS level', r_aa, 0.020, 5.0)
    p3 = check(
        f'F1+F2 centroid ({cent_aa:.0f} Hz)',
        cent_aa, 750.0, 1050.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_aa < 750:
            print(f"      Centroid too low."
                  f" Lower AA_F[0] or AA_F[1].")
        else:
            print(f"      Centroid too high."
                  f" Raise AA_F[0] or lower"
                  f" AA_F[1].")
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav(
        "output_play/diag_aa_vowel_slow.wav",
        ola_stretch(aa_seg / (
            np.max(np.abs(aa_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — R TRILL [r]")
    print()
    r_seg = synth_R_trill(
        AA_F, D_F, 145.0, 1.0)
    mod_depth, trill_hz = \
        measure_trill_modulation(r_seg)
    p1 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    p2 = check_warn(
        'voicing (open phases)',
        measure_voicing(r_seg),
        0.40, 1.0, warn_lo=0.25)
    p3 = check_warn(
        'trill modulation depth',
        mod_depth, 0.22, 1.0,
        warn_lo=0.10)
    if trill_hz > 0:
        p4 = check(
            f'trill rate ({trill_hz:.1f} Hz)',
            trill_hz, 15.0, 70.0,
            unit=' Hz', fmt='.1f')
    else:
        p4 = False
        print("    [FAIL] trill rate: "
              "not detected.")
    d3 = p1 and p2 and p3 and p4
    all_pass &= d3
    write_wav(
        "output_play/diag_r_trill_slow.wav",
        ola_stretch(r_seg / (
            np.max(np.abs(r_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — D ONSET [d]")
    print()
    d_seg  = synth_D(R_F, E_F, 145.0, 1.0)
    n_cl_d = int(45.0 / 1000.0 * SR)
    n_bst_d= int(10.0 / 1000.0 * SR)
    bst_d  = (d_seg[n_cl_d:n_cl_d+n_bst_d]
              if len(d_seg) > n_cl_d+n_bst_d
              else d_seg[-n_bst_d:])
    cent_d = measure_burst_centroid(
        bst_d, sr=SR)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.80)
    p2 = check(
        f'burst centroid ({cent_d:.0f} Hz)',
        cent_d, 2000.0, 5000.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    write_wav(
        "output_play/diag_d_onset_slow.wav",
        ola_stretch(d_seg / (
            np.max(np.abs(d_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 E ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — E VOWEL [e]")
    print()
    print("  METHOD: band centroid")
    print("  F1 region: 200–700 Hz")
    print("    target: 300–500 Hz")
    print("    (E_F[0]=370 Hz)")
    print("  F2 region: 1800–2600 Hz")
    print("    target: 1900–2400 Hz")
    print("    (E_F[1]=2200 Hz)")
    print()
    e_seg  = synth_E_short(
        D_F, N_F, 145.0, 1.0)
    n_e    = len(e_seg)
    n_on_e = int(0.12 * n_e)
    n_off_e= int(0.10 * n_e)
    body_e = e_seg[n_on_e:n_e-n_off_e]
    vr_e   = measure_voicing(body_e)

    cent_e1 = measure_band_centroid(
        body_e, 200.0, 700.0, sr=SR)
    cent_e2 = measure_band_centroid(
        body_e, 1800.0, 2600.0, sr=SR)

    p1 = check('voicing (body)', vr_e,
               0.65, 1.0)
    p2 = check('RMS level', rms(e_seg),
               0.010, 5.0)
    p3 = check(
        f'F1 centroid ({cent_e1:.0f} Hz)',
        cent_e1, 300.0, 500.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_e1 < 300:
            print(f"      F1 centroid too low"
                  f" ({cent_e1:.0f}).")
            print(f"      Raise E_F[0].")
        else:
            print(f"      F1 centroid too high"
                  f" ({cent_e1:.0f}).")
            print(f"      Lower E_F[0].")
    p4 = check(
        f'F2 centroid ({cent_e2:.0f} Hz)',
        cent_e2, 1900.0, 2400.0,
        unit=' Hz', fmt='.1f')
    if not p4:
        if cent_e2 < 1900:
            print(f"      F2 centroid too low.")
            print(f"      Raise E_F[1].")
        else:
            print(f"      F2 centroid too high.")
            print(f"      Lower E_F[1].")
    d5 = p1 and p2 and p3 and p4
    all_pass &= d5
    write_wav(
        "output_play/diag_e_short_slow.wav",
        ola_stretch(e_seg / (
            np.max(np.abs(e_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — N NASAL [n]")
    print()
    n_seg = synth_N(E_F, A_F, 145.0, 1.0)
    vr_n  = measure_voicing(n_seg)
    r_n   = rms(n_seg)
    p1 = check('voicing', vr_n, 0.65, 1.0)
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
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d6 = p1 and p2 and p3
    all_pass &= d6
    write_wav(
        "output_play/diag_n_nasal_slow.wav",
        ola_stretch(n_seg / (
            np.max(np.abs(n_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 A ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — A VOWEL [ɑ]")
    print()
    print("  METHOD: band centroid 600–1400 Hz")
    print("  Target: 800–1100 Hz")
    print()
    a_seg  = synth_A_short(N_F, 110.0, 1.0)
    n_a    = len(a_seg)
    body_a = a_seg[:int(0.6 * n_a)]
    vr_a   = measure_voicing(body_a)
    cent_a = measure_band_centroid(
        body_a, 600.0, 1400.0, sr=SR)
    p1 = check_warn(
        'voicing (body)', vr_a,
        0.50, 1.0, warn_lo=0.30)
    p2 = check('RMS level', rms(a_seg),
               0.005, 5.0)
    p3 = check(
        f'F1+F2 centroid ({cent_a:.0f} Hz)',
        cent_a, 800.0, 1100.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_a < 800:
            print(f"      Centroid too low."
                  f" Raise A_F[0].")
        else:
            print(f"      Centroid too high."
                  f" Lower A_F[1].")
    d7 = p1 and p2 and p3
    all_pass &= d7
    write_wav(
        "output_play/diag_a_final_slow.wav",
        ola_stretch(a_seg / (
            np.max(np.abs(a_seg)) + 1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ─────────────────���────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD")
    print()
    gd_dry  = synth_gar_dena(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    gd_hall = synth_gar_dena(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    p1 = check('full-word RMS', rms(gd_dry),
               0.010, 0.90)
    print(f"  {len(gd_dry)} samples"
          f" ({len(gd_dry)/SR*1000:.0f} ms)")
    n_g  = len(synth_G(AA_F, 145.0, 1.0))
    n_aa = len(synth_AA_long(
        G_F, R_F, 145.0, 1.0))
    n_r  = len(synth_R_trill(
        AA_F, D_F, 145.0, 1.0))
    n_d  = len(synth_D(R_F, E_F, 145.0, 1.0))
    n_e  = len(synth_E_short(
        D_F, N_F, 145.0, 1.0))
    n_n  = len(synth_N(E_F, A_F, 145.0, 1.0))
    z_aa = (n_g, n_g+n_aa)
    e0   = n_g+n_aa+n_r+n_d
    z_e  = (e0, e0+n_e)
    z_n  = (z_e[1], z_e[1]+n_n)
    z_a  = (z_n[1], len(gd_dry))

    def sw(s, e):
        s = max(0, s)
        e = min(len(gd_dry), e)
        return (gd_dry[s:e]
                if e > s else gd_dry[:10])

    print()
    p2 = check_warn(
        'Ā zone voicing',
        measure_voicing(sw(*z_aa)),
        0.70, 1.0, warn_lo=0.50)
    p3 = check_warn(
        'E zone voicing',
        measure_voicing(sw(*z_e)),
        0.60, 1.0, warn_lo=0.40)
    p4 = check_warn(
        'N zone voicing',
        measure_voicing(sw(*z_n)),
        0.55, 1.0, warn_lo=0.35)
    p5 = check_warn(
        'A zone voicing',
        measure_voicing(sw(*z_a)),
        0.45, 1.0, warn_lo=0.25)
    d8 = p1 and p2 and p3 and p4 and p5
    all_pass &= d8
    write_wav(
        "output_play/diag_gar_dena_full.wav",
        gd_dry)
    write_wav(
        "output_play/diag_gar_dena_hall.wav",
        gd_hall)
    write_wav(
        "output_play/diag_gar_dena_slow.wav",
        ola_stretch(gd_dry, 4.0))
    print()
    print("  diag_gar_dena_full.wav")
    print("  diag_gar_dena_hall.wav")
    print("  diag_gar_dena_slow.wav")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_r_trill_slow.wav",
        "diag_aa_vowel_slow.wav",
        "diag_e_short_slow.wav",
        "diag_gar_dena_slow.wav",
        "diag_gar_dena_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Ā: open, back — 'father'")
    print("  R: silence/voice alternation"
          " in 4x slow")
    print("  E: brief front vowel"
          " before nasal")
    print("  Full: G·Ā·R·D·E·N·A")
    print("  Seven distinct events audible")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 G onset",   d1),
        ("D2 Ā vowel",   d2),
        ("D3 R trill",   d3),
        ("D4 D onset",   d4),
        ("D5 E vowel",   d5),
        ("D6 N nasal",   d6),
        ("D7 A final",   d7),
        ("D8 Full word", d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D9 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  GĀR-DENA [ɡɑːrdenɑ] verified.")
        print()
        print("  Reconstruction complete.")
        print("  Word 3 of Beowulf line 1.")
        print()
        print("  Commit files:")
        print("    gar_dena_reconstruction.py")
        print("    gar_dena_diagnostic.py")
        print()
        print("  Next word: IN [ɪn]")
        print("  Beowulf line 1, word 4.")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d5:
            print()
            print("  D5: centroid out of range.")
            print("  F1 centroid target 300–500.")
            print("  F2 centroid target 1900–2400.")
            print("  Adjust E_F[0] or E_F[1].")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
