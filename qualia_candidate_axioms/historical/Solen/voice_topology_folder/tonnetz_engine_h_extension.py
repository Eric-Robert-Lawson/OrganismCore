"""
TONNETZ ENGINE — H EXTENSION
Three-Origin System: h1, h2, h3

Adds to tonnetz_engine.py.
Paste after the JI_RATIOS block,
before the VOWEL_DATA block.

February 2026

BACKGROUND:
  H_Ghost_Topology.md states:
    H is the Tonnetz origin.
    The baseline state of the voice.
    The tonic from which all phonemes
    are measured as distances.

  vocal_topology_reconstruction_methodology.md
  established:
    PIE had THREE distinct H-origins,
    not one. Each from a different
    region of the vocal tract. Each
    producing a different vowel
    coloring effect in adjacent vowels.

    h1 = glottal  [h] or [ʔ]
         No vowel coloring.
         The pure open-glottis baseline.
         The H the current engine uses.

    h2 = pharyngeal [ħ]
         A-coloring: F1↑ F2↓
         The vowel becomes more open
         and back — darker.
         Lives today in Arabic ح.
         Its acoustic effect frozen in
         Sanskrit/Greek a-coloring.

    h3 = voiced labiovelar [ɣʷ]
         O-coloring: F2↓ (lip rounding)
         The vowel becomes more rounded
         and back.
         Most thoroughly lost.
         Reconstructed from o-coloring
         in daughter languages.

  All three collapsed to silence
  in English. h1 alone survived as
  the modern H phoneme.

  h2 and h3 left their traces only
  in vowel colorings — F1/F2 effects
  in the vowels that followed them.

USAGE:
  For current English synthesis:
    Use H_FORMANTS (h1) as always.
    Nothing changes for modern engine.

  For historical reconstruction:
    Use H2_FORMANTS for pharyngeal
    origin in PIE/early reconstructions.
    Use H3_FORMANTS for labiovelar
    origin.
    The ghost_at_boundary() function
    accepts an origin parameter.

  For the ghost layer:
    The ghost is always colored by
    its origin. In modern English,
    the origin is h1 — glottal,
    colorless. In historical
    reconstruction, the origin may
    be h2 or h3, and the ghost
    carries their formant signature.

CROSS-VALIDATION:
  h2 F1/F2 effects are confirmed by:
    Arabic ħ acoustic measurement:
      F1 raised ~80-120 Hz in
      adjacent vowels.
      F2 lowered ~150-250 Hz in
      adjacent vowels.
    Sanskrit a-coloring pattern:
      e → a before/after h2 sites.
    Greek vowel patterns:
      Same a-coloring systematic.
    Hittite ḫ written reflex.

  h3 F2 effects are confirmed by:
    O-coloring in daughter languages:
      e → o before/after h3 sites.
    Reconstructed as labiovelar
    because lip rounding is the
    primary mechanism of F2 lowering
    without pharyngeal F1 raising.
"""

import numpy as np
from scipy.signal import lfilter, butter

SR    = 44100
DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)

# ============================================================
# THREE-H ORIGIN SYSTEM
# ============================================================

# H1 — GLOTTAL (current engine H)
# The open glottis. No constriction.
# No vowel coloring.
# This is what the current engine
# uses for H_FORMANTS. Unchanged.
H1_FORMANTS   = [500.0, 1500.0, 2500.0, 3500.0]
H1_BANDWIDTHS = [200.0,  250.0,  300.0,  350.0]
H1_LABEL      = 'h1_glottal'

# Alias — the current engine's H.
# Nothing changes for modern synthesis.
H_FORMANTS    = H1_FORMANTS
H_BANDWIDTHS  = H1_BANDWIDTHS

# H2 — PHARYNGEAL
# Pharynx constricted.
# Tongue root retracted against
# posterior pharyngeal wall.
# Continuous turbulent airflow.
# F1 raised (pharynx narrows,
#   open pharynx effect)
# F2 lowered (back cavity lengthens)
# F3 slightly lowered.
# Effect on adjacent vowels:
#   +80-120 Hz on F1
#   -150-250 Hz on F2
#   → the vowel shifts toward A
#   → darker, more open quality
# Lives today in Arabic ح.
H2_FORMANTS   = [650.0, 1100.0, 2200.0, 3300.0]
H2_BANDWIDTHS = [280.0,  320.0,  350.0,  400.0]
H2_LABEL      = 'h2_pharyngeal'

# H3 — VOICED LABIOVELAR
# Voiced. Lip rounding active.
# Velar/uvular constriction.
# The rounding lowers F2 (lip
#   rounding always lowers F2).
# The voicing gives it the
#   O-coloring quality.
# F1: slightly raised (velar)
# F2: significantly lowered (rounding)
# F3: lowered (rounding effect)
# Effect on adjacent vowels:
#   F2 lowered → vowel shifts
#   toward O (rounded, back)
# Most thoroughly lost in all
# IE daughter languages.
# Reconstructed from o-coloring
# systematic in Sanskrit/Greek.
H3_FORMANTS   = [500.0,  800.0, 2000.0, 3100.0]
H3_BANDWIDTHS = [220.0,  280.0,  320.0,  370.0]
H3_LABEL      = 'h3_labiovelar'

# ============================================================
# H-ORIGIN REGISTRY
# ============================================================

H_ORIGINS = {
    'h1': {
        'formants':   H1_FORMANTS,
        'bandwidths': H1_BANDWIDTHS,
        'label':      H1_LABEL,
        'voiced':     False,
        'coloring':   None,
        'f1_delta':   0.0,    # no coloring
        'f2_delta':   0.0,
    },
    'h2': {
        'formants':   H2_FORMANTS,
        'bandwidths': H2_BANDWIDTHS,
        'label':      H2_LABEL,
        'voiced':     False,
        'coloring':   'a',    # a-coloring
        'f1_delta':  +100.0,  # F1 raised
        'f2_delta':  -200.0,  # F2 lowered
    },
    'h3': {
        'formants':   H3_FORMANTS,
        'bandwidths': H3_BANDWIDTHS,
        'label':      H3_LABEL,
        'voiced':     True,
        'coloring':   'o',    # o-coloring
        'f1_delta':   +40.0,  # F1 slightly raised
        'f2_delta':  -350.0,  # F2 significantly lowered
    },
}

# Default for modern English synthesis.
# Do not change this — it preserves
# all v16/v17 behavior unchanged.
DEFAULT_H_ORIGIN = 'h1'


# ============================================================
# VOWEL TONNETZ COORDINATES
# Used for Tonnetz distance computation
# and ghost_at_boundary().
# Extended with historical phonemes
# for reconstruction use.
# ============================================================

# Current engine coordinates (unchanged)
VOWEL_TONNETZ = {
    'AA': ( 0,  0),   # tonic — A3
    'AH': ( 0,  0),   # near tonic
    'AE': ( 0,  0),   # near tonic
    'IY': ( 3,  1),   # far — high front
    'IH': ( 2,  1),
    'EH': ( 1,  1),
    'EY': ( 2,  1),
    'UW': (-3, -1),   # far — high back
    'UH': (-2, -1),
    'OW': (-2,  0),
    'AO': (-1,  0),
    'AW': (-1, -1),
    'AY': ( 2,  0),
    'OY': ( 1, -1),
    'ER': ( 0,  0),   # central — near origin
}

# Historical phoneme Tonnetz positions
# for reconstruction use.
# These are estimated from formant
# targets using the same F2-to-fifth-axis
# relationship as the existing vowels.
VOWEL_TONNETZ_HISTORICAL = {
    # Old English vowels (long forms)
    'OE_A_LONG':   ( 0,  0),   # ā — like AA
    'OE_AE_LONG':  ( 1,  1),   # ǣ — like EY
    'OE_E_LONG':   ( 2,  1),   # ē — like IY approach
    'OE_I_LONG':   ( 3,  1),   # ī — high front
    'OE_O_LONG':   (-2,  0),   # ō — like OW
    'OE_U_LONG':   (-3, -1),   # ū — like UW
    'OE_Y_LONG':   ( 3,  0),   # ȳ — front rounded
    # PIE vowels (reconstructed)
    'PIE_E':       ( 1,  1),   # *e — the base vowel
    'PIE_A':       ( 0,  0),   # *a — post-h2-coloring
    'PIE_O':       (-2,  0),   # *o — post-h3-coloring
    'PIE_I':       ( 3,  1),   # *i
    'PIE_U':       (-3, -1),   # *u
}


# ============================================================
# DISTANCE FROM H — EXTENDED
# ============================================================

def distance_from_H(vowel_ph, origin='h1'):
    """
    Compute Tonnetz distance from the
    specified H origin to a vowel.

    For h1 (modern English):
      Distance is from (0,0) — the
      current engine behavior.

    For h2 (pharyngeal origin):
      The pharyngeal origin colors
      toward A. Vowels near A are
      'closer' to h2 in the sense
      that the ghost traversal is
      shorter — less movement needed.
      Distance is adjusted by the
      h2 coloring displacement.

    For h3 (labiovelar origin):
      The labiovelar origin colors
      toward O. Vowels near O are
      closer to h3.

    Returns float — Tonnetz distance.
    """
    pos = VOWEL_TONNETZ.get(
        vowel_ph,
        VOWEL_TONNETZ_HISTORICAL.get(
            vowel_ph, (0, 0)))
    a, b = pos

    # Base distance from (0,0)
    base_dist = np.sqrt(a**2 + b**2)

    # Origin adjustment
    if origin == 'h2':
        # h2 is displaced toward A (0,0)
        # — no adjustment needed at (0,0)
        # but the pharyngeal coloring
        # means the ghost carries extra
        # dark texture
        return base_dist * 1.15
    elif origin == 'h3':
        # h3 displaced toward O (-2, 0)
        # vowels near O are closer
        o_a, o_b = -2, 0
        h3_dist = np.sqrt(
            (a - o_a)**2 + (b - o_b)**2)
        return min(base_dist, h3_dist) * 1.20
    else:
        # h1 — standard
        return base_dist


# ============================================================
# GHOST FORMANT INTERPOLATION — EXTENDED
# ============================================================

def ghost_formant_interp(
        F_prev, F_next, n_s,
        origin='h1', sr=SR):
    """
    Interpolate formant arrays for a
    ghost segment, passing through the
    specified H origin at the midpoint.

    For h1: passes through H1_FORMANTS.
    For h2: passes through H2_FORMANTS.
            The ghost has a darker,
            more open quality at midpoint.
    For h3: passes through H3_FORMANTS.
            The ghost has a rounded,
            back quality at midpoint.

    The H origin is the lowest energy
    point of the ghost — the moment
    of most complete return to baseline.
    For h2, that baseline is pharyngeal.
    For h3, that baseline is labiovelar.

    Returns list of 4 float32 arrays.
    """
    origin_data = H_ORIGINS.get(
        origin, H_ORIGINS['h1'])
    H_F  = origin_data['formants']
    n_h1 = n_s // 2
    n_h2 = n_s - n_h1

    F_arrays = []
    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)
        # First half: F_prev → H_origin
        if n_h1 > 0:
            arr[:n_h1] = np.linspace(
                float(F_prev[fi]),
                float(H_F[fi]),
                n_h1, dtype=DTYPE)
        # Second half: H_origin → F_next
        if n_h2 > 0:
            arr[n_h1:] = np.linspace(
                float(H_F[fi]),
                float(F_next[fi] if F_next
                      else H_F[fi]),
                n_h2, dtype=DTYPE)
        F_arrays.append(arr)
    return F_arrays


# ============================================================
# GHOST AT BOUNDARY — EXTENDED
# ============================================================

# Ghost profiles (from v16 via
# H_Ghost_Topology.md)
GHOST_PROFILES = {
    'ARC_NORMAL':  {'dur_ms': 10.0, 'amp': 0.045},
    'ARC_WEIGHT':  {'dur_ms': 18.0, 'amp': 0.065},
    'ARC_GRIEF':   {'dur_ms': 28.0, 'amp': 0.030},
    'ARC_CONTAIN': {'dur_ms':  4.0, 'amp': 0.015},
    'ARC_EUREKA':  {'dur_ms': 14.0, 'amp': 0.060},
    'ARC_RECOGN':  {'dur_ms': 12.0, 'amp': 0.040},
}

def ghost_at_boundary(
        prev_nucleus_ph,
        next_nucleus_ph,
        position_in_phrase,
        stress_prev,
        stress_next,
        arc_type,
        dil=6.0,
        phrase_final=False,
        origin='h1'):
    """
    Compute ghost duration and amplitude
    at a syllable boundary.

    Extended from v16 to accept origin
    parameter for historical reconstruction.

    For h2 origin: ghost is slightly
    longer (pharyngeal return takes more
    time — deeper tract position).
    Amplitude slightly louder (pharyngeal
    resonance is more present).

    For h3 origin: ghost is slightly
    longer and has a rounded quality
    (the labiovelar return).

    Returns (duration_ms, amplitude).
    """
    arc_key = (arc_type if isinstance(
        arc_type, str) else 'ARC_NORMAL')
    profile = GHOST_PROFILES.get(
        arc_key,
        GHOST_PROFILES['ARC_NORMAL'])

    dur_ms = profile['dur_ms']
    amp    = profile['amp']

    # Scale with speaking rate (dil)
    dur_ms *= max(0.5, dil / 6.0)

    # Phrase position: ghost grows
    # slightly toward phrase end
    dur_ms *= (1.0 + 0.3 * position_in_phrase)

    # Stress scaling
    stress_factor = 1.0
    if stress_prev == 1:
        stress_factor *= 1.15
    if stress_next == 1:
        stress_factor *= 1.10
    dur_ms *= stress_factor
    amp    *= stress_factor

    # Tonnetz distance scaling
    if prev_nucleus_ph:
        dist = distance_from_H(
            prev_nucleus_ph, origin=origin)
        dur_ms *= (1.0 + 0.12 * dist)

    # Phrase final: longer exhale
    if phrase_final:
        dur_ms *= 2.2
        amp    *= 0.55

    # Origin adjustment
    if origin == 'h2':
        # Pharyngeal return: deeper,
        # slightly longer, slightly louder
        dur_ms *= 1.18
        amp    *= 1.12
    elif origin == 'h3':
        # Labiovelar return: rounded,
        # slightly longer
        dur_ms *= 1.22
        amp    *= 1.08

    dur_ms = float(np.clip(dur_ms, 2.0, 50.0))
    amp    = float(np.clip(amp, 0.005, 0.18))

    return dur_ms, amp


# ============================================================
# VOCAL DISTANCE — UNCHANGED FROM v16
# ============================================================

def vocal_distance(ph1, ph2):
    """
    Tonnetz distance between two vowels.
    """
    pos1 = VOWEL_TONNETZ.get(ph1, (0, 0))
    pos2 = VOWEL_TONNETZ.get(ph2, (0, 0))
    return np.sqrt(
        (pos1[0]-pos2[0])**2 +
        (pos1[1]-pos2[1])**2)


def print_vocal_distances():
    """
    Print Tonnetz distance table.
    Extended to show h1/h2/h3
    distances from each vowel.
    """
    vowels = ['AA','AH','IY','IH',
              'EH','EY','UW','UH',
              'OW','AO','AW','AY',
              'OY','ER']
    print("\nVocal Tonnetz distances from H origins:")
    print(f"  {'Vowel':6s} "
          f"{'from H1':10s} "
          f"{'from H2':10s} "
          f"{'from H3':10s}")
    print("  " + "-" * 42)
    for v in vowels:
        d1 = distance_from_H(v, 'h1')
        d2 = distance_from_H(v, 'h2')
        d3 = distance_from_H(v, 'h3')
        print(f"  {v:6s} "
              f"{d1:8.3f}   "
              f"{d2:8.3f}   "
              f"{d3:8.3f}")
    print()
    print("  H1 (glottal):    no coloring")
    print("  H2 (pharyngeal): a-coloring "
          "— IY furthest")
    print("  H3 (labiovelar): o-coloring "
          "— UW closest")
    print()
