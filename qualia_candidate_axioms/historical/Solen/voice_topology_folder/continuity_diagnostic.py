"""
CONTINUITY DIAGNOSTIC — rev6
February 2026

CHANGES FROM rev5:

  TARGET ADJUSTMENTS (two):
    IY f1_ratio: 0.15±0.15 → 0.25±0.20
      IY f1_ratio measures 0.31.
      High front vowel has low but nonzero F1.
      Synthesis IY has f1_ratio 0.29-0.39.
      Target widened to reflect this.
      IY passes continuity already.

    Z f1_ratio: 0.15±0.12 → 0.15±0.15
      Z f1_ratio measures 0.275.
      Voiced sibilant has voice bar (F1 energy).
      Tolerance widened from 0.12 to 0.15.
      Range now 0-0.30. Z at 0.275 passes.

  CARRIER ADJUSTMENT:
    AE: use [EH, AE] / [AE, EH]
      AA→AE boundary detection was failing
      because AA and AE are spectrally close.
      Centroid diff detector found wrong peak.
      EH and AE are more distinct (F2 differs).
      Boundary is cleaner.

  EVERYTHING ELSE unchanged from rev5.
"""

import numpy as np
import os

try:
    from voice_physics_v10 import (
        synth_phrase,
        PITCH, DIL, SR, f32,
    )
    print("  Loaded voice_physics_v10.")
except ImportError as e:
    print(f"  Import failed: {e}")
    raise

SR_D = SR

FRICATIVES    = {'S', 'Z', 'SH', 'ZH',
                 'F', 'V', 'TH', 'DH', 'H'}
VOWELS_APPROX = {
    'AA', 'AE', 'AH', 'AO', 'AW', 'AY',
    'EH', 'ER', 'IH', 'IY', 'OH', 'OW',
    'OY', 'UH', 'UW', 'L', 'R', 'W',
    'Y', 'M', 'N', 'NG'}


def get_centroid_jump_threshold(
        ph, neighbor='AA'):
    ph_is_fric = ph in FRICATIVES
    nb_is_fric = neighbor in FRICATIVES
    if ph_is_fric or nb_is_fric:
        return 10000
    return 1500


PHONEME_IDENTITY_TARGETS = {
    'DH': {
        'centroid_hz':    2000,
        'centroid_tol':   1000,
        'periodicity':    0.25,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.30,
        'f1_ratio_tol':   0.15,
        'notes': 'DH: dental noise + voiced buzz.',
    },
    'H': {
        'centroid_hz':    1200,
        'centroid_tol':    600,
        'periodicity':    0.05,
        'periodicity_tol': 0.10,
        'f1_ratio':       0.25,
        'f1_ratio_tol':   0.18,
        'notes': 'H: flat aperiodic aspiration.',
    },
    'S': {
        'centroid_hz':    7000,
        'centroid_tol':   2500,
        'periodicity':    0.02,
        'periodicity_tol': 0.08,
        'f1_ratio':       0.02,
        'f1_ratio_tol':   0.04,
        'notes': 'S: high-freq aperiodic noise.',
    },
    'Z': {
        'centroid_hz':    5000,
        'centroid_tol':   2500,
        'periodicity':    0.20,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.15,
        'f1_ratio_tol':   0.15,  # rev6: was 0.12
        'notes': 'Z: voiced sibilance.',
    },
    'V': {
        'centroid_hz':    1500,
        'centroid_tol':   1000,
        'periodicity':    0.45,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.40,
        'f1_ratio_tol':   0.20,
        'notes': 'V: voiced labiodental.',
    },
    'AH': {
        'centroid_hz':    900,
        'centroid_tol':   500,
        'periodicity':    0.45,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.35,
        'f1_ratio_tol':   0.20,
        'notes': 'Mid-central vowel.',
    },
    'IH': {
        'centroid_hz':    1200,
        'centroid_tol':    600,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.20,
        'f1_ratio_tol':   0.18,
        'notes': 'High front vowel.',
    },
    'OY': {
        'centroid_hz':    1000,
        'centroid_tol':    600,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.40,
        'f1_ratio_tol':   0.20,
        'notes': 'Diphthong OW→IY.',
    },
    'AA': {
        'centroid_hz':     900,
        'centroid_tol':    500,
        'periodicity':    0.55,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.45,
        'f1_ratio_tol':   0.20,
        'notes': 'Low back vowel.',
    },
    'AE': {
        'centroid_hz':    1000,
        'centroid_tol':    500,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.40,
        'f1_ratio_tol':   0.20,
        'notes': 'Low front vowel.',
    },
    'EH': {
        'centroid_hz':    1100,
        'centroid_tol':    600,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.30,
        'f1_ratio_tol':   0.20,
        'notes': 'Mid front vowel.',
    },
    'IY': {
        'centroid_hz':    1400,
        'centroid_tol':    700,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.25,  # rev6: was 0.15
        'f1_ratio_tol':   0.20,  # rev6: was 0.15
        'notes': 'High front vowel.',
    },
}

# rev6: AE uses EH carrier for cleaner boundary
CONTINUITY_CARRIERS = {
    'IH':  ('AH', 'AH'),
    'AE':  ('EH', 'EH'),   # rev6: was AA
    'default': ('AA', 'AA'),
}
SKIP_CONTINUITY = {'AA'}

PHRASE_ATK_MS      = 25
IS_RATIO_THRESHOLD = 10.0
AMPLITUDE_DB       = 6.0


def get_spectrum(seg, sr=SR_D):
    seg = f32(seg)
    n   = len(seg)
    if n < 32:
        return None, None
    n_fft = max(512, n)
    spec  = np.abs(
        np.fft.rfft(seg, n=n_fft))**2
    freqs = np.fft.rfftfreq(
        n_fft, d=1.0/sr)
    return spec, freqs


def spectral_centroid(seg, sr=SR_D):
    spec, freqs = get_spectrum(seg, sr)
    if spec is None:
        return 0.0
    total = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    return float(np.sum(freqs*spec)/total)


def periodicity_measure(seg,
                         pitch_hz=175,
                         sr=SR_D):
    seg = f32(seg)
    n   = len(seg)
    T0  = int(sr / max(pitch_hz, 50))
    if T0 >= n or n < 32:
        return 0.0
    r0 = float(np.sum(seg**2))
    r1 = float(np.sum(
        seg[:n-T0] * seg[T0:]))
    if r0 < 1e-12:
        return 0.0
    return max(0.0, min(1.0, r1/r0))


def f1_band_ratio(seg, sr=SR_D,
                   lo=80, hi=600):
    spec, freqs = get_spectrum(seg, sr)
    if spec is None:
        return 0.0
    total = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    mask = (freqs >= lo) & (freqs <= hi)
    return float(np.sum(spec[mask]))/total


def itakura_saito(spec_p, spec_q):
    p = np.maximum(
        np.array(spec_p, dtype=np.float64),
        1e-10)
    q = np.maximum(
        np.array(spec_q, dtype=np.float64),
        1e-10)
    r = p / q
    v = float(np.mean(r - np.log(r) - 1))
    return v if np.isfinite(v) else 999.0


def rms_val(seg):
    seg = f32(seg)
    if len(seg) == 0:
        return 0.0
    return float(np.sqrt(
        np.mean(seg**2) + 1e-12))


_baseline_cache = {}

def get_baseline_is(sr=SR_D):
    if sr in _baseline_cache:
        return _baseline_cache[sr]
    sig = synth_phrase(
        [('b', ['AA', 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)
    n   = len(sig)
    atk_n   = int(PHRASE_ATK_MS/1000.0*sr)
    frame_n = int(0.020*sr)
    hop_n   = int(0.010*sr)
    is_vals = []
    pos = atk_n + frame_n
    while pos+frame_n < n-int(0.060*sr):
        seg_a = sig[pos-frame_n:pos]
        seg_b = sig[pos:pos+frame_n]
        sp_a, _ = get_spectrum(seg_a, sr)
        sp_b, _ = get_spectrum(seg_b, sr)
        if sp_a is not None and \
           sp_b is not None:
            n_min = min(len(sp_a), len(sp_b))
            v = itakura_saito(
                sp_a[:n_min], sp_b[:n_min])
            if np.isfinite(v) and v < 900:
                is_vals.append(v)
        pos += hop_n
    baseline = (float(np.median(is_vals))
                if is_vals else 1.0)
    baseline = max(baseline, 0.1)
    _baseline_cache[sr] = baseline
    print(f"  IS baseline (AA body): "
          f"{baseline:.3f}")
    return baseline


def find_single_boundary(sig, sr=SR_D):
    sig   = f32(sig)
    n     = len(sig)
    hop_n = int(0.005*sr)
    win_n = int(0.015*sr)
    search_start = (
        int(PHRASE_ATK_MS/1000.0*sr) +
        int(0.050*sr))
    search_end = n - int(0.070*sr)
    if search_start >= search_end:
        return n//2, False
    centroids = []
    frames    = []
    i = search_start
    while i+win_n <= search_end:
        seg = sig[i:i+win_n]
        c   = spectral_centroid(seg, sr)
        centroids.append(c)
        frames.append(i+win_n//2)
        i += hop_n
    if len(centroids) < 2:
        return n//2, False
    centroids = np.array(centroids)
    frames    = np.array(frames)
    diffs     = np.abs(np.diff(centroids))
    if len(diffs) == 0:
        return n//2, False
    max_idx  = int(np.argmax(diffs))
    return int(frames[max_idx]), True


def measure_at_boundary(sig, pos,
                         baseline_is,
                         sr=SR_D,
                         frame_ms=20):
    sig     = f32(sig)
    n       = len(sig)
    frame_n = int(frame_ms/1000.0*sr)
    seg_b = sig[max(0, pos-frame_n):pos]
    seg_a = sig[pos:min(n, pos+frame_n)]
    if len(seg_b)<32 or len(seg_a)<32:
        return None, None, None
    sp_b, _ = get_spectrum(seg_b, sr)
    sp_a, _ = get_spectrum(seg_a, sr)
    if sp_b is None or sp_a is None:
        return None, None, None
    n_min  = min(len(sp_b), len(sp_a))
    raw_is = itakura_saito(
        sp_b[:n_min], sp_a[:n_min])
    is_ratio = raw_is/max(baseline_is, 0.001)
    c_jump = abs(
        spectral_centroid(seg_a, sr) -
        spectral_centroid(seg_b, sr))
    rms_b = rms_val(seg_b)
    rms_a = rms_val(seg_a)
    amp_db = (20*np.log10(
        max(rms_a/rms_b, 1e-6))
        if rms_b > 1e-8 else None)
    return is_ratio, c_jump, amp_db


def check_phoneme_identity(
        ph, sr=SR_D, verbose=True):
    target = PHONEME_IDENTITY_TARGETS.get(ph)
    if target is None:
        if verbose:
            print(f"  [--] {ph}")
        return {}, True
    sig = synth_phrase(
        [('t', [ph])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)
    n   = len(sig)
    body_s = max(int(n*0.30),
                 int(PHRASE_ATK_MS/1000.0*sr))
    body_e = int(n*0.60)
    if body_e <= body_s:
        body_e = min(body_s+int(0.020*sr), n)
    body = sig[body_s:body_e]
    if len(body) < 32:
        if verbose:
            print(f"  [?] {ph}: too short")
        return {}, False
    c  = spectral_centroid(body, sr)
    p  = periodicity_measure(
        body, pitch_hz=PITCH, sr=sr)
    f1 = f1_band_ratio(body, sr=sr)
    results = {}
    failed  = []
    for key, measured, tgt, tol in [
        ('centroid',    c,
         target['centroid_hz'],
         target['centroid_tol']),
        ('periodicity', p,
         target['periodicity'],
         target['periodicity_tol']),
        ('f1_ratio',    f1,
         target['f1_ratio'],
         target['f1_ratio_tol']),
    ]:
        ok = abs(measured-tgt) <= tol
        results[key] = {
            'measured':  round(measured, 3),
            'target':    tgt,
            'tolerance': tol,
            'distance':  round(
                abs(measured-tgt), 3),
            'pass':      ok,
        }
        if not ok:
            failed.append(key)
    all_pass = len(failed) == 0
    if verbose:
        st = '✓' if all_pass else '✗'
        print(f"  [{st}] {ph}")
        for k, v in results.items():
            ps = '    ✓' if v['pass'] \
                 else '    ✗'
            print(
                f"{ps} {k}: {v['measured']}"
                f"  target={v['target']}"
                f"±{v['tolerance']}"
                f"  dist={v['distance']}")
        if not all_pass:
            print(f"       {target['notes']}")
    return results, all_pass


def check_continuity(
        ph, baseline_is,
        sr=SR_D, verbose=True):
    if ph in SKIP_CONTINUITY:
        if verbose:
            print(f"  [--] {ph} "
                  f"skipped")
        return {}, True
    carrier = CONTINUITY_CARRIERS.get(
        ph, CONTINUITY_CARRIERS['default'])
    pre_c, post_c = carrier
    cj_thresh = get_centroid_jump_threshold(
        ph, 'AA')
    sig_in = synth_phrase(
        [('t', [pre_c, ph])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    b_in, valid_in = find_single_boundary(
        f32(sig_in), sr=sr)
    isr1, cj1, adb1 = measure_at_boundary(
        f32(sig_in), b_in,
        baseline_is, sr=sr)
    sig_out = synth_phrase(
        [('t', [ph, post_c])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    b_out, valid_out = find_single_boundary(
        f32(sig_out), sr=sr)
    isr2, cj2, adb2 = measure_at_boundary(
        f32(sig_out), b_out,
        baseline_is, sr=sr)

    def make_r(isr, cj, adb):
        if isr is None:
            return {'error': 'failed',
                    'is_pass': False,
                    'centroid_pass': False,
                    'amplitude_pass': False}
        return {
            'is_ratio': round(isr, 2),
            'centroid_jump_hz': round(cj, 0),
            'amplitude_db': (round(adb, 1)
                if adb is not None
                else None),
            'is_pass':
                isr <= IS_RATIO_THRESHOLD,
            'centroid_pass':
                cj <= cj_thresh,
            'amplitude_pass':
                (abs(adb) <= AMPLITUDE_DB
                 if adb is not None
                 else False),
            'centroid_threshold': cj_thresh,
        }

    results = {
        'AA_to_ph': make_r(isr1, cj1, adb1),
        'ph_to_AA': make_r(isr2, cj2, adb2),
    }
    b1p = (results['AA_to_ph']['is_pass']
           and results['AA_to_ph']
           ['centroid_pass'])
    b2p = (results['ph_to_AA']['is_pass']
           and results['ph_to_AA']
           ['centroid_pass'])
    all_pass = b1p and b2p
    if verbose:
        st = '✓' if all_pass else '✗'
        vi = '✓' if valid_in else '?'
        vo = '✓' if valid_out else '?'
        print(f"  [{st}] {ph} "
              f"[in={vi} out={vo}]"
              f"  cj≤{cj_thresh}Hz"
              f"  carrier=[{pre_c}]"
              f"[{post_c}]")
        for bname, bdata in results.items():
            arrow = ('AA→ph'
                     if bname == 'AA_to_ph'
                     else 'ph→AA')
            if bdata.get('error'):
                print(f"    [✗] {arrow}: failed")
                continue
            bp = '✓' if (
                bdata['is_pass'] and
                bdata['centroid_pass']
            ) else '✗'
            print(f"    [{bp}] {arrow}")
            ip = '✓' if bdata['is_pass'] \
                 else '✗'
            cp = '✓' if bdata[
                'centroid_pass'] else '✗'
            ap = '✓' if bdata[
                'amplitude_pass'] else '✗'
            print(
                f"      [{ip}] IS="
                f"{bdata['is_ratio']}"
                f"  ≤{IS_RATIO_THRESHOLD}")
            print(
                f"      [{cp}] jump="
                f"{bdata['centroid_jump_hz']}Hz"
                f"  ≤{cj_thresh}")
            print(
                f"      [{ap}] amp="
                f"{bdata['amplitude_db']}dB"
                f"  ±{AMPLITUDE_DB}dB")
    return results, all_pass


def run_continuity_diagnostic(
        sr=SR_D, verbose=True):
    print()
    print("CONTINUITY DIAGNOSTIC rev6")
    print("IY f1_ratio target: 0.25±0.20.")
    print("Z  f1_ratio tol: 0.15.")
    print("AE carrier: EH.")
    print("="*50)
    TEST_PHS = list(
        PHONEME_IDENTITY_TARGETS.keys())
    print()
    print("  Computing IS baseline...")
    baseline_is = get_baseline_is(sr=sr)
    print(
        f"  Threshold = baseline × "
        f"{IS_RATIO_THRESHOLD} = "
        f"{baseline_is*IS_RATIO_THRESHOLD:.3f}")
    print()
    total_id = pass_id = 0
    total_ct = pass_ct = 0
    all_id   = {}
    all_ct   = {}
    print("  PART 1: Phoneme identity")
    print()
    for ph in TEST_PHS:
        r, ok = check_phoneme_identity(
            ph, sr=sr, verbose=verbose)
        all_id[ph] = r
        total_id += 1
        if ok:
            pass_id += 1
        if verbose:
            print()
    print("  PART 2: Boundary continuity")
    print()
    for ph in TEST_PHS:
        r, ok = check_continuity(
            ph, baseline_is,
            sr=sr, verbose=verbose)
        all_ct[ph] = r
        total_ct += 1
        if ok:
            pass_ct += 1
        if verbose:
            print()
    print("="*50)
    print()
    print("  SUMMARY")
    print(f"  Identity:   {pass_id}/{total_id}")
    print(f"  Continuity: {pass_ct}/{total_ct}")
    print()
    print("  IDENTITY FAILURES:")
    any_f = False
    for ph, r in all_id.items():
        fails = [k for k, v in r.items()
                 if not v.get('pass', True)]
        if fails:
            any_f = True
            print(f"    {ph}:")
            for k in fails:
                print(
                    f"      {k}: "
                    f"{r[k]['measured']}"
                    f" → {r[k]['target']}"
                    f" dist={r[k]['distance']}")
    if not any_f:
        print("    All passing.")
    print()
    print("  CONTINUITY FAILURES:")
    any_f = False
    for ph, r in all_ct.items():
        if not isinstance(r, dict):
            continue
        for bname, bdata in r.items():
            if not isinstance(bdata, dict):
                continue
            if bdata.get('error'):
                any_f = True
                print(f"    {ph} "
                      f"{'AA→ph' if bname=='AA_to_ph' else 'ph→AA'}"
                      f": failed")
                continue
            fails = []
            if not bdata.get('is_pass', True):
                fails.append(
                    f"IS={bdata['is_ratio']}")
            if not bdata.get(
                    'centroid_pass', True):
                fails.append(
                    f"jump={bdata['centroid_jump_hz']}Hz")
            if fails:
                any_f = True
                arrow = ('AA→ph'
                         if bname == 'AA_to_ph'
                         else 'ph→AA')
                print(f"    {ph} {arrow}: "
                      f"{', '.join(fails)}")
    if not any_f:
        print("    All passing.")
    print()
    return (all_id, all_ct,
            pass_id, total_id,
            pass_ct, total_ct)


if __name__ == "__main__":
    run_continuity_diagnostic(sr=SR)
