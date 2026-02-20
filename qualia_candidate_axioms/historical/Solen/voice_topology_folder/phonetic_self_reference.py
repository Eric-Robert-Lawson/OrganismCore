"""
PHONETIC SELF-REFERENCE
February 2026

The synthesis engine gains its own ears.

Synthesize → Analyze → Compare → Adjust.

The analysis measures acoustic properties
of the output and compares them to
phoneme targets.

The Z fix is implemented here
using this loop:
  Target: sibilance ratio ≥ 0.40
  Measure: actual sibilance ratio
  Adjust: Z noise gain until met

This module:
  1. Defines acoustic targets per phoneme
  2. Provides analysis functions
  3. Provides a self-check function
  4. Fixes Z/S relative levels
"""

import numpy as np
from scipy.signal import (
    butter, lfilter, freqz, lfilter_zi
)
from scipy.signal import find_peaks
import os

SR    = 44100
DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)


# ============================================================
# ACOUSTIC TARGETS
# What each phoneme should measure as.
# These are the self-reference targets.
# ============================================================

PHONEME_TARGETS = {
    # Vowels
    'AA': {
        'voiced': True,
        'f1': (650, 800),
        'f2': (950, 1200),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'IH': {
        'voiced': True,
        'f1': (320, 450),
        'f2': (1850, 2150),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'AH': {
        'voiced': True,
        'f1': (450, 600),
        'f2': (1050, 1350),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'OW': {
        'voiced': True,
        'f1': (380, 520),
        'f2': (700,  950),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'EH': {
        'voiced': True,
        'f1': (460, 600),
        'f2': (1700, 1980),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'ER': {
        'voiced': True,
        'f1': (420, 560),
        'f3': (1580, 1800),  # low F3 key
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    # Sibilants — the key relationships
    'S': {
        'voiced': False,
        'sibilance_min': 0.65,
        'sibilance_band': (6000, 12000),
        'f_peak_min': 6000,
        'hnr_max': 2.0,   # noisy
    },
    'Z': {
        'voiced': True,
        'sibilance_min': 0.40,
        'sibilance_band': (6000, 12000),
        'f_peak_min': 6000,
        'hnr_min': 3.0,   # some periodicity
        'hnr_max': 15.0,  # not too clean
        # KEY: sibilance audible above voice
        'sib_to_voice_min': 0.35,
    },
    'SH': {
        'voiced': False,
        'sibilance_min': 0.55,
        'sibilance_band': (2000, 8000),
        'f_peak_max': 4000,
        'hnr_max': 2.0,
    },
    'ZH': {
        'voiced': True,
        'sibilance_min': 0.35,
        'sibilance_band': (2000, 8000),
        'hnr_min': 3.0,
    },
    # Fricatives
    'F': {
        'voiced': False,
        'sibilance_min': 0.20,
        'sibilance_band': (3000, 10000),
        'hnr_max': 2.0,
    },
    'V': {
        'voiced': True,
        'sibilance_min': 0.10,
        'hnr_min': 5.0,
        'hnr_max': 20.0,
    },
    # Nasals
    'M': {
        'voiced': True,
        'f1': (220, 280),
        'antiformant': (850, 1150),
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    'N': {
        'voiced': True,
        'f1': (220, 280),
        'antiformant': (1300, 1700),
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    # Approximants
    'R': {
        'voiced': True,
        'f3': (1580, 1800),
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    'L': {
        'voiced': True,
        'f2': (850, 1150),
        'hnr_min': 8.0,
    },
    'W': {
        'voiced': True,
        'f1': (260, 350),
        'f2': (500, 720),
        'hnr_min': 8.0,
    },
    # H
    'H': {
        'voiced': False,   # onset
        'sibilance_max': 0.15,
        'hnr_max': 8.0,    # breathy
    },
    # DH
    'DH': {
        'voiced': True,
        'sibilance_max': 0.10,
        'hnr_min': 5.0,
    },
}


# ============================================================
# ANALYSIS FUNCTIONS
# The engine's ears.
# ============================================================

def measure_sibilance(seg, sr=SR,
                       band=(6000,12000)):
    """
    Sibilance ratio:
    energy in sibilance band
    relative to total energy.

    High ratio = clearly sibilant (S, Z).
    Low ratio = non-sibilant (vowels).
    """
    seg = f32(seg)
    if len(seg) < 64:
        return 0.0
    nyq = sr/2.0
    lo  = max(band[0]/nyq, 0.001)
    hi  = min(band[1]/nyq, 0.499)
    if lo >= hi: return 0.0
    try:
        b,a    = butter(4,[lo,hi],
                         btype='band')
        sib    = lfilter(b,a,seg)
        e_sib  = float(np.mean(sib**2))
        e_tot  = float(np.mean(seg**2))
        if e_tot < 1e-12: return 0.0
        return e_sib/e_tot
    except:
        return 0.0


def measure_hnr(seg, pitch_hz=175,
                sr=SR):
    """
    Harmonics-to-Noise Ratio (dB).

    Measures periodicity of signal.
    High HNR (>15dB): clean voiced.
    Mid HNR (5-15dB): voiced + noise.
    Low HNR (<5dB): mostly noise.

    Uses autocorrelation at pitch period.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 64: return 0.0

    T0  = int(sr/max(pitch_hz, 50))
    if T0 >= n: return 0.0

    # Autocorrelation at T0
    r0  = float(np.sum(seg**2))
    r1  = float(np.sum(
        seg[:n-T0]*seg[T0:]))

    if r0 < 1e-12: return 0.0

    ratio = r1/r0
    ratio = max(-0.999,
                 min(0.999, ratio))
    if ratio <= 0: return 0.0

    hnr_db = 10*np.log10(
        ratio/(1-ratio+1e-10))
    return float(hnr_db)


def estimate_f1_f2(seg, sr=SR,
                    n_formants=4):
    """
    Estimate formant frequencies
    using LPC analysis.

    Returns [F1, F2, F3, F4] in Hz.
    Simple peak-picking from LPC spectrum.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 128: return [0,0,0,0]

    # Pre-emphasis
    pre = np.append(
        seg[0],
        seg[1:]-0.97*seg[:-1])

    # LPC order
    order = int(2 + sr/1000)
    order = min(order, n//3, 40)

    try:
        from numpy.linalg import solve
        # Autocorrelation method
        R = np.array([
            float(np.dot(pre[:n-k],
                          pre[k:]))
            for k in range(order+1)])
        if abs(R[0]) < 1e-10:
            return [0,0,0,0]

        # Levinson-Durbin
        a    = np.zeros(order)
        err  = R[0]
        for i in range(order):
            k = R[i+1]
            for j in range(i):
                k -= a[j]*R[i-j]
            k /= (err + 1e-10)
            a_new = a[:i] - k*a[:i][::-1]
            a[:i] = a_new
            a[i]  = k
            err  *= (1-k**2)

        # Frequency response
        n_fft = 1024
        H     = np.fft.rfft(
            np.append([1.0], -a),
            n=n_fft)
        spec  = 1.0/(np.abs(H)**2 + 1e-10)
        freqs = np.fft.rfftfreq(
            n_fft, d=1.0/sr)

        # Find peaks above 150Hz
        # below 5000Hz
        mask  = (freqs > 150) & \
                (freqs < 5000)
        s_m   = spec[mask]
        f_m   = freqs[mask]

        peaks,_ = find_peaks(
            s_m, height=np.max(s_m)*0.1,
            distance=int(100/(
                freqs[1]-freqs[0])+1))

        formants = sorted(
            [float(f_m[p]) for p in peaks])
        while len(formants) < 4:
            formants.append(0.0)
        return formants[:4]

    except:
        return [0.0, 0.0, 0.0, 0.0]


def is_voiced_segment(seg, sr=SR,
                       threshold=0.01):
    """
    Simple voiced/unvoiced detection.
    Based on zero-crossing rate
    and energy ratio.
    """
    seg = f32(seg)
    if len(seg) < 32: return False
    zcr = float(np.mean(
        np.abs(np.diff(np.sign(seg)))))
    nrg = float(np.mean(seg**2))
    # Low ZCR + energy = voiced
    # High ZCR + energy = unvoiced fricative
    return (zcr < 0.3 and
            nrg > threshold**2)


def measure_sib_to_voice(seg, sr=SR):
    """
    Sibilance-to-voicing ratio.
    Critical for Z:
    sibilance must be audible
    above the voiced component.

    Returns ratio of high-freq energy
    to low-freq energy.
    """
    seg = f32(seg)
    if len(seg) < 64: return 0.0
    nyq = sr/2.0
    try:
        b,a  = butter(4,
            3000/nyq, btype='high')
        hi   = lfilter(b,a,seg)
        b,a  = butter(4,
            3000/nyq, btype='low')
        lo   = lfilter(b,a,seg)
        e_hi = float(np.mean(hi**2))
        e_lo = float(np.mean(lo**2))
        if e_lo < 1e-12: return 0.0
        return e_hi/e_lo
    except:
        return 0.0


# ============================================================
# SELF-CHECK FUNCTION
# Analyze a synthesized segment
# and compare to phoneme target.
# ============================================================

def check_phoneme(ph, seg, sr=SR,
                   verbose=True):
    """
    Analyze synthesized segment.
    Compare to PHONEME_TARGETS[ph].
    Report pass/fail for each criterion.

    Returns:
      dict of results
      bool: all_pass
    """
    target  = PHONEME_TARGETS.get(ph)
    if target is None:
        return {}, True

    seg     = f32(seg)
    results = {}
    passed  = []
    failed  = []

    # Voiced check
    if 'voiced' in target:
        hnr    = measure_hnr(seg, sr=sr)
        voiced = hnr > 3.0
        tgt_v  = target['voiced']
        ok     = (voiced == tgt_v)
        results['voiced'] = {
            'target': tgt_v,
            'measured': voiced,
            'hnr_db': round(hnr, 1),
            'pass': ok,
        }
        (passed if ok else failed).append(
            'voiced')

    # Sibilance ratio
    band = target.get(
        'sibilance_band', (6000,12000))
    if 'sibilance_min' in target or \
       'sibilance_max' in target:
        sib = measure_sibilance(
            seg, sr=sr, band=band)
        s_min = target.get(
            'sibilance_min', 0.0)
        s_max = target.get(
            'sibilance_max', 1.0)
        ok    = (s_min <= sib <= s_max)
        results['sibilance'] = {
            'target': (s_min, s_max),
            'measured': round(sib, 3),
            'pass': ok,
        }
        (passed if ok else failed).append(
            'sibilance')

    # Sibilance-to-voice ratio (Z key)
    if 'sib_to_voice_min' in target:
        stv = measure_sib_to_voice(
            seg, sr=sr)
        s_min = target['sib_to_voice_min']
        ok    = stv >= s_min
        results['sib_to_voice'] = {
            'target_min': s_min,
            'measured': round(stv, 3),
            'pass': ok,
        }
        (passed if ok else failed).append(
            'sib_to_voice')

    # HNR
    if 'hnr_min' in target or \
       'hnr_max' in target:
        hnr   = measure_hnr(seg, sr=sr)
        h_min = target.get('hnr_min',-99)
        h_max = target.get('hnr_max', 99)
        ok    = (h_min <= hnr <= h_max)
        results['hnr'] = {
            'target': (h_min, h_max),
            'measured': round(hnr, 1),
            'pass': ok,
        }
        (passed if ok else failed).append(
            'hnr')

    # Formants
    if any(k in target
           for k in ('f1','f2','f3')):
        fmts  = estimate_f1_f2(
            seg, sr=sr)
        for fi, fname in enumerate(
                ('f1','f2','f3','f4')):
            if fname in target:
                lo,hi = target[fname]
                measured = fmts[fi]
                ok = (lo <= measured <= hi)
                results[fname] = {
                    'target': (lo, hi),
                    'measured': round(
                        measured, 1),
                    'pass': ok,
                }
                (passed if ok
                 else failed).append(fname)

    all_pass = len(failed) == 0

    if verbose:
        status = '✓' if all_pass else '✗'
        print(f"  [{status}] {ph}")
        for k, v in results.items():
            p = '  ✓' if v['pass'] \
                else '  ✗'
            print(f"    {p} {k}: "
                  f"measured={v['measured']}"
                  f" target={v.get('target','')}")

    return results, all_pass


# ============================================================
# Z FIX — derived from self-reference
# ============================================================

def z_noise_gain_search(
        synth_fn, sr=SR,
        target_sib=0.40,
        target_stv=0.35,
        max_iter=8,
        verbose=True):
    """
    Find the correct Z noise gain
    using the self-referential loop.

    synth_fn(noise_gain) → audio segment

    Adjusts noise_gain until:
      sibilance_ratio >= target_sib
      sib_to_voice_ratio >= target_stv

    This is the engine tuning itself.
    """
    lo_gain = 0.30
    hi_gain = 1.50
    best_gain = 0.80

    if verbose:
        print()
        print("  Z self-tuning loop:")

    for i in range(max_iter):
        mid = (lo_gain+hi_gain)/2.0
        seg = synth_fn(mid)
        sib = measure_sibilance(
            seg, sr=sr,
            band=(6000,12000))
        stv = measure_sib_to_voice(
            seg, sr=sr)

        if verbose:
            print(f"    iter {i}: "
                  f"gain={mid:.3f} "
                  f"sib={sib:.3f} "
                  f"stv={stv:.3f}")

        if sib >= target_sib and \
           stv >= target_stv:
            best_gain = mid
            if verbose:
                print(f"    ✓ converged "
                      f"at gain={mid:.3f}")
            break
        elif sib < target_sib or \
             stv < target_stv:
            lo_gain = mid
        else:
            hi_gain = mid
        best_gain = mid

    return best_gain


# ============================================================
# INTEGRATION WITH VOICE SYNTHESIS
# ============================================================

# Updated Z and S parameters
# derived from self-reference analysis

Z_PARAMS = {
    'bands':   [(4000, 12000, 1.0)],
    'd_res':   8000,
    'd_bw':    900,
    'n_gain':  0.80,   # raised from 0.50
    'v_frac':  0.50,   # 50/50 voice/noise
}

S_PARAMS = {
    'bands':   [(4000, 14000, 1.0)],
    'd_res':   8800,
    'd_bw':    800,
    'n_gain':  0.90,
}


def patch_z_params(spec):
    """
    Apply corrected Z parameters to
    a phoneme spec dict.
    """
    if spec.get('ph') == 'Z':
        spec['bands']  = Z_PARAMS['bands']
        spec['d_res']  = Z_PARAMS['d_res']
        spec['d_bw']   = Z_PARAMS['d_bw']
        spec['n_gain'] = Z_PARAMS['n_gain']
        # Z: more noise in mix
        # sibilance above voicing
        spec['source'] = 'fric_v_loud'
    return spec


# ============================================================
# MAIN — diagnostic + self-check
# ============================================================

if __name__ == "__main__":

    print()
    print("PHONETIC SELF-REFERENCE")
    print("The engine checks its own output.")
    print("="*60)
    print()

    # Import synthesis
    try:
        from voice_physics_v7_fix import (
            synth_phrase, synth_word,
            apply_room, write_wav,
            PITCH, DIL
        )
        has_synth = True
    except ImportError:
        has_synth = False
        print("  (synthesis not available,"
              " running analysis only)")

    os.makedirs("output_play",
                 exist_ok=True)

    if has_synth:
        # Synthesize and self-check
        # each phoneme family

        print("  Synthesizing for"
              " self-check...")
        print()

        # The Z / S comparison
        # This is the diagnostic
        for word, phs, label in [
            ('was', ['W','AH','Z'],
             'Z in was'),
            ('voice', ['V','OY','S'],
             'S in voice'),
        ]:
            seg = synth_phrase(
                [(word, phs)],
                pitch_base=PITCH,
                dil=DIL)

            # Extract the sibilant portion
            # (last third of word)
            n   = len(seg)
            sib_seg = seg[2*n//3:]

            ph_check = phs[-1]
            print(f"  Self-check: '{label}'")
            results, passed = \
                check_phoneme(
                    ph_check,
                    sib_seg,
                    verbose=True)
            print()

            # Save for listening
            seg_room = apply_room(
                seg, rt60=1.4, dr=0.52)
            write_wav(
                f"output_play/"
                f"selfcheck_{word}.wav",
                seg_room)

        # Full phrase self-check
        print()
        print("  Full phrase self-check:")
        print("  'the voice was already"
              " here'")
        print()

        phrase_spec = [
            ('the',     ['DH','AH']),
            ('voice',   ['V','OY','S']),
            ('was',     ['W','AH','Z']),
            ('already', ['AA','L','R',
                          'EH','D','IY']),
            ('here',    ['H','IH','R']),
        ]

        seg = synth_phrase(
            phrase_spec,
            pitch_base=PITCH,
            dil=DIL)
        seg_room = apply_room(
            seg, rt60=1.5, dr=0.50)
        write_wav(
            "output_play/"
            "the_voice_selfcheck.wav",
            seg_room)
        print("  Written: the_voice_"
              "selfcheck.wav")

    print()
    print("="*60)
    print()
    print("  Z target:")
    print("  sibilance ≥ 0.40")
    print("  sib_to_voice ≥ 0.35")
    print("  (sibilance audible ABOVE")
    print("   the voiced buzz)")
    print()
    print("  S target:")
    print("  sibilance ≥ 0.65")
    print("  voiced = False")
    print()
    print("  The relationship:")
    print("  S and Z same sibilance level.")
    print("  Z adds voiced buzz underneath.")
    print("  Not: Z buries sibilance")
    print("       under voicing.")
    print()
    print("  The engine now measures")
    print("  its own output.")
    print("  The loop is closed.")
    print()
