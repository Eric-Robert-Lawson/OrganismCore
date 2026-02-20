"""
RAINBOW PHONETIC DIAGNOSTIC
February 2026

A systematic sweep through
the entire phoneme space.

Every phoneme family.
Every place of articulation.
Every manner of articulation.
Every transition type.
Every minimal pair.

Self-reference checks run
on every segment.
A complete report generated.

The full topology of the voice
laid out in one test.
The gaps show immediately.
The passes show immediately.
We know exactly where we are.

Output:
  output_rainbow/
    tier1_vowels/
    tier2_nasals/
    tier3_approximants/
    tier4_fricatives_unvoiced/
    tier5_fricatives_voiced/
    tier6_stops_unvoiced/
    tier7_stops_voiced/
    tier8_transitions/
    tier9_minimal_pairs/
    _FULL_RAINBOW.wav  (all in sequence)
    _REPORT.txt        (self-check results)
"""

import numpy as np
import os
import wave as wave_module
from scipy.signal import butter, lfilter

# Import synthesis
from voice_physics_v4 import (
    synth_phrase, synth_word,
    apply_room, write_wav,
    f32, PITCH, DIL, SR, DTYPE
)

# Import self-reference
from phonetic_self_reference import (
    check_phoneme,
    measure_sibilance,
    measure_hnr,
    measure_sib_to_voice,
    is_voiced_segment,
    estimate_f1_f2,
    PHONEME_TARGETS,
)

OUT_ROOT = "output_rainbow"
REPORT   = []  # accumulated results


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def sil(dur_ms, sr=SR):
    return f32(np.zeros(
        int(dur_ms/1000.0*sr)))


def concat(*segs):
    return f32(np.concatenate(
        [f32(s) for s in segs]))


def synth_ph_in_context(
        ph, context_v='AA',
        position='medial',
        sr=SR):
    """
    Synthesize a single phoneme
    in vowel context for analysis.

    position:
      'initial'  → ph + context_v
      'final'    → context_v + ph
      'medial'   → context_v + ph + context_v
    """
    cv = context_v
    if position == 'initial':
        words = [('test',[ph, cv])]
    elif position == 'final':
        words = [('test',[cv, ph])]
    else:
        words = [('test',[cv, ph, cv])]

    return synth_phrase(
        words,
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL,
        sr=sr)


def extract_middle(seg, frac=0.33):
    """
    Extract the middle fraction
    of a segment for analysis.
    Avoids onset/offset artifacts.
    """
    n     = len(seg)
    start = int(n*(0.5-frac/2))
    end   = int(n*(0.5+frac/2))
    return seg[start:end]


def run_check(ph, seg, label="",
               verbose=True):
    """
    Run self-reference check.
    Accumulate to REPORT.
    Return (results, all_pass).
    """
    mid = extract_middle(seg)
    results, passed = check_phoneme(
        ph, mid, verbose=False)

    status = '✓' if passed else '✗'
    line   = f"  [{status}] {ph:4s}"
    if label:
        line += f" ({label})"

    details = []
    for k, v in results.items():
        p   = '✓' if v['pass'] else '✗'
        m   = v.get('measured','?')
        tgt = v.get('target','')
        details.append(
            f"      {p} {k}: "
            f"{m} / {tgt}")

    REPORT.append(line)
    for d in details:
        REPORT.append(d)

    if verbose:
        print(line)
        for d in details:
            print(d)

    return results, passed


def save_ph(tier_dir, name, seg,
             room=True):
    """Save with optional room."""
    path = os.path.join(
        tier_dir, f"{name}.wav")
    sig = f32(seg)
    if room:
        sig = apply_room(
            sig, rt60=1.2, dr=0.55)
    # 95th percentile norm
    p95 = np.percentile(
        np.abs(sig), 95)
    if p95 > 1e-8:
        sig = sig/p95*0.88
    sig = np.clip(sig, -1.0, 1.0)
    write_wav(path, sig)
    return sig


# ============================================================
# TIER RUNNERS
# ============================================================

def tier1_vowels(root):
    d = mkdir(os.path.join(
        root, "tier1_vowels"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 1: VOWELS")
    REPORT.append("="*50)
    print("\n  TIER 1: VOWELS")

    ALL_VOWELS = [
        # Front
        ('IY','front_high'),
        ('IH','front_high_lax'),
        ('EH','front_mid'),
        ('AE','front_low'),
        # Central
        ('AH','central_mid'),
        ('AA','central_low'),
        ('AO','central_low_round'),
        ('ER','central_rhotic'),
        # Back
        ('UW','back_high'),
        ('UH','back_high_lax'),
        ('OW','back_mid'),
        ('OH','back_low'),
        # Diphthongs
        ('AY','diph_low_front'),
        ('AW','diph_low_back'),
        ('OY','diph_back_front'),
    ]

    segs_all = []
    for v, label in ALL_VOWELS:
        seg = synth_phrase(
            [('test',[v])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(d, f"vowel_{v}", seg)
        run_check(v, seg, label)
        segs_all.append(s)
        segs_all.append(sil(220))

    return concat(*segs_all)


def tier2_nasals(root):
    d = mkdir(os.path.join(
        root, "tier2_nasals"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 2: NASALS")
    REPORT.append("="*50)
    print("\n  TIER 2: NASALS")

    NASALS = [
        ('M','bilabial'),
        ('N','alveolar'),
        ('NG','velar'),
    ]

    segs_all = []
    for ph, label in NASALS:
        # In AV context
        seg = synth_phrase(
            [('test',['AA',ph,'AA'])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(d, f"nasal_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier3_approximants(root):
    d = mkdir(os.path.join(
        root, "tier3_approximants"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 3: APPROXIMANTS")
    REPORT.append("="*50)
    print("\n  TIER 3: APPROXIMANTS")

    APPROX = [
        ('W','bilabial_velar'),
        ('L','lateral_alveolar'),
        ('R','retroflex'),
        ('Y','palatal'),
    ]

    segs_all = []
    for ph, label in APPROX:
        seg = synth_phrase(
            [('test',['AA',ph,'AA'])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(
            d, f"approx_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier4_fricatives_unvoiced(root):
    d = mkdir(os.path.join(
        root, "tier4_fric_unvoiced"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 4: FRICATIVES (UNVOICED)")
    REPORT.append("="*50)
    print("\n  TIER 4: FRICATIVES UNVOICED")

    FRICS_U = [
        ('F', 'labio_dental'),
        ('TH','dental'),
        ('S', 'alveolar'),
        ('SH','palatal'),
        ('H', 'glottal'),
    ]

    segs_all = []
    for ph, label in FRICS_U:
        # Initial position (ph + vowel)
        nv = 'IH' if ph == 'H' else 'AA'
        seg = synth_phrase(
            [('test',[ph, nv])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(
            d, f"fric_u_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier5_fricatives_voiced(root):
    d = mkdir(os.path.join(
        root, "tier5_fric_voiced"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 5: FRICATIVES (VOICED)")
    REPORT.append("="*50)
    print("\n  TIER 5: FRICATIVES VOICED")

    FRICS_V = [
        ('V', 'labio_dental_voiced'),
        ('DH','dental_voiced'),
        ('Z', 'alveolar_voiced'),
        ('ZH','palatal_voiced'),
    ]

    segs_all = []
    for ph, label in FRICS_V:
        seg = synth_phrase(
            [('test',['AA',ph,'AA'])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(
            d, f"fric_v_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier6_stops_unvoiced(root):
    d = mkdir(os.path.join(
        root, "tier6_stops_unvoiced"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 6: STOPS (UNVOICED)")
    REPORT.append("="*50)
    print("\n  TIER 6: STOPS UNVOICED")

    STOPS_U = [
        ('P','bilabial'),
        ('T','alveolar'),
        ('K','velar'),
    ]

    segs_all = []
    for ph, label in STOPS_U:
        # Stop before vowel (burst audible)
        seg = synth_phrase(
            [('test',[ph,'AA'])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(
            d, f"stop_u_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier7_stops_voiced(root):
    d = mkdir(os.path.join(
        root, "tier7_stops_voiced"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 7: STOPS (VOICED)")
    REPORT.append("="*50)
    print("\n  TIER 7: STOPS VOICED")

    STOPS_V = [
        ('B','bilabial_voiced'),
        ('D','alveolar_voiced'),
        ('G','velar_voiced'),
    ]

    segs_all = []
    for ph, label in STOPS_V:
        seg = synth_phrase(
            [('test',[ph,'AA'])],
            pitch_base=PITCH, dil=DIL)
        s = save_ph(
            d, f"stop_v_{ph}", seg)
        run_check(ph, seg, label)
        segs_all.append(s)
        segs_all.append(sil(280))

    return concat(*segs_all)


def tier8_transitions(root):
    d = mkdir(os.path.join(
        root, "tier8_transitions"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 8: TRANSITIONS")
    REPORT.append("  (where artifacts live)")
    REPORT.append("="*50)
    print("\n  TIER 8: TRANSITIONS")

    TRANSITIONS = [
        # vowel → fricative
        (('AA','S'),  'V→FricU_alveolar'),
        (('AA','Z'),  'V→FricV_alveolar'),
        (('AA','SH'), 'V→FricU_palatal'),
        (('AA','F'),  'V→FricU_labial'),
        (('IH','Z'),  'V→FricV_alveolar_front'),
        # fricative → vowel
        (('S','AA'),  'FricU→V_alveolar'),
        (('Z','AA'),  'FricV→V_alveolar'),
        (('SH','AA'), 'FricU→V_palatal'),
        # vowel → stop
        (('AA','T'),  'V→StopU_alveolar'),
        (('AA','D'),  'V→StopV_alveolar'),
        (('AA','P'),  'V→StopU_bilabial'),
        (('AA','B'),  'V→StopV_bilabial'),
        (('AA','K'),  'V→StopU_velar'),
        (('AA','G'),  'V→StopV_velar'),
        # stop → vowel
        (('T','AA'),  'StopU→V_alveolar'),
        (('D','AA'),  'StopV→V_alveolar'),
        (('P','AA'),  'StopU→V_bilabial'),
        (('B','AA'),  'StopV→V_bilabial'),
        # vowel → nasal
        (('AA','M'),  'V→Nasal_bilabial'),
        (('AA','N'),  'V→Nasal_alveolar'),
        (('AA','NG'), 'V→Nasal_velar'),
        # nasal → vowel
        (('M','AA'),  'Nasal→V_bilabial'),
        (('N','AA'),  'Nasal→V_alveolar'),
        # approximant transitions
        (('AA','R'),  'V→R'),
        (('R','AA'),  'R→V'),
        (('AA','L'),  'V→L'),
        (('L','AA'),  'L→V'),
        # DH + vowel (the + vowel)
        (('DH','AH'), 'DH→AH (the)'),
    ]

    segs_all = []
    for phs, label in TRANSITIONS:
        name = f"{phs[0]}_{phs[1]}"
        seg  = synth_phrase(
            [('test', list(phs))],
            pitch_base=PITCH, dil=DIL)
        s    = save_ph(
            d, f"trans_{name}", seg)
        REPORT.append(
            f"  [transition] "
            f"{phs[0]}→{phs[1]} "
            f"({label})")
        segs_all.append(s)
        segs_all.append(sil(200))

    return concat(*segs_all)


def tier9_minimal_pairs(root):
    d = mkdir(os.path.join(
        root, "tier9_minimal_pairs"))
    REPORT.append("")
    REPORT.append("="*50)
    REPORT.append("TIER 9: MINIMAL PAIRS")
    REPORT.append("  (contrast check)")
    REPORT.append("="*50)
    print("\n  TIER 9: MINIMAL PAIRS")

    # Each pair: same context
    # different phoneme
    # Should sound DIFFERENT
    PAIRS = [
        # Voiced/unvoiced sibilants
        (('S','Z'),  'AA_{}AA',
         'sibilant voiced/unvoiced'),
        # Voiced/unvoiced labial fric
        (('F','V'),  'AA_{}AA',
         'labial fric voiced/unvoiced'),
        # Voiced/unvoiced stops
        (('P','B'),  '{}_AA',
         'bilabial stop VOT'),
        (('T','D'),  '{}_AA',
         'alveolar stop VOT'),
        (('K','G'),  '{}_AA',
         'velar stop VOT'),
        # Nasal vs stop (same place)
        (('M','B'),  'AA_{}AA',
         'bilabial nasal vs stop'),
        (('N','D'),  'AA_{}AA',
         'alveolar nasal vs stop'),
        (('NG','G'), 'AA_{}AA',
         'velar nasal vs stop'),
        # Approximants
        (('L','R'),  'AA_{}AA',
         'lateral vs rhotic'),
        (('W','V'),  '{}_AA',
         'bilabial approx vs fric'),
        # Front vowel contrast
        (('IY','IH'), '{}',
         'high front tense/lax'),
        (('EH','AE'), '{}',
         'mid/low front'),
        # Back vowel contrast
        (('UW','UH'), '{}',
         'high back tense/lax'),
        (('OW','AO'), '{}',
         'mid/low back'),
    ]

    segs_all = []
    for (ph1,ph2), template, label \
            in PAIRS:
        name = f"{ph1}_vs_{ph2}"
        REPORT.append(
            f"  [pair] {ph1} vs {ph2}"
            f"  ({label})")

        pair_segs = []
        for ph in [ph1, ph2]:
            ctx = template.format(ph)
            phs = [c for c in ctx.split('_')
                   if c]
            # Handle template format
            if '{}' in template:
                phs = ctx.replace(
                    '{}', ph).split('_')
                phs = [p for p in phs if p]

            seg = synth_phrase(
                [('test', phs)],
                pitch_base=PITCH,
                dil=DIL)
            save_ph(
                d,
                f"pair_{ph1}v{ph2}_{ph}",
                seg)
            pair_segs.append(seg)
            pair_segs.append(sil(180))

            # Self-check each member
            mid = extract_middle(seg)
            results,passed = check_phoneme(
                ph, mid, verbose=False)
            status = '✓' if passed else '✗'
            REPORT.append(
                f"    [{status}] {ph}")
            for k,v in results.items():
                p = '✓' if v['pass'] \
                    else '✗'
                REPORT.append(
                    f"      {p} {k}: "
                    f"{v.get('measured','?')}"
                    f" / "
                    f"{v.get('target','')}")

        # Save the pair together
        # for easy comparison
        pair_audio = concat(*pair_segs)
        save_ph(d, f"pair_{name}",
                 pair_audio)
        segs_all.append(pair_audio)
        segs_all.append(sil(350))

        print(f"    {ph1} vs {ph2}"
              f"  ({label})")

    return concat(*segs_all)


# ============================================================
# FULL RAINBOW SWEEP
# ============================================================

def run_rainbow():
    """
    Run all tiers.
    Generate full rainbow wav.
    Generate full report.
    """
    root = mkdir(OUT_ROOT)

    print()
    print("RAINBOW PHONETIC DIAGNOSTIC")
    print("The full topology of the voice.")
    print("Every phoneme.")
    print("Every transition.")
    print("Every minimal pair.")
    print("="*60)

    REPORT.append(
        "RAINBOW PHONETIC DIAGNOSTIC")
    REPORT.append(
        "February 2026")
    REPORT.append(
        "Full phoneme space analysis.")

    # Run all tiers
    # Each returns an audio segment
    # for the full rainbow wav
    all_tiers = []

    # Brief leader tone before each tier
    def tier_gap():
        return sil(600)

    t1 = tier1_vowels(root)
    all_tiers.extend([t1, tier_gap()])

    t2 = tier2_nasals(root)
    all_tiers.extend([t2, tier_gap()])

    t3 = tier3_approximants(root)
    all_tiers.extend([t3, tier_gap()])

    t4 = tier4_fricatives_unvoiced(root)
    all_tiers.extend([t4, tier_gap()])

    t5 = tier5_fricatives_voiced(root)
    all_tiers.extend([t5, tier_gap()])

    t6 = tier6_stops_unvoiced(root)
    all_tiers.extend([t6, tier_gap()])

    t7 = tier7_stops_voiced(root)
    all_tiers.extend([t7, tier_gap()])

    t8 = tier8_transitions(root)
    all_tiers.extend([t8, tier_gap()])

    t9 = tier9_minimal_pairs(root)
    all_tiers.append(t9)

    # Full rainbow wav
    print()
    print("  Assembling full rainbow...")
    rainbow = concat(*all_tiers)
    rainbow = apply_room(
        rainbow, rt60=1.3, dr=0.55)
    p95 = np.percentile(
        np.abs(rainbow), 95)
    if p95 > 1e-8:
        rainbow = rainbow/p95*0.88
    rainbow = np.clip(rainbow,-1.0,1.0)
    rbow_path = os.path.join(
        root, "_FULL_RAINBOW.wav")
    write_wav(rbow_path, rainbow)
    print(f"  Written: _FULL_RAINBOW.wav")
    print(f"  Duration: "
          f"{len(rainbow)/SR:.1f}s")

    # Write report
    report_path = os.path.join(
        root, "_REPORT.txt")
    with open(report_path, 'w') as rf:
        rf.write('\n'.join(REPORT))
    print(f"  Written: _REPORT.txt")

    # Print summary
    print()
    print("  SUMMARY:")
    total   = sum(1 for r in REPORT
                  if r.strip().startswith(
                      '[✓]') or
                  r.strip().startswith(
                      '[✗]'))
    passing = sum(1 for r in REPORT
                  if r.strip().startswith(
                      '[✓]'))
    failing = sum(1 for r in REPORT
                  if r.strip().startswith(
                      '[✗]'))
    print(f"  Phoneme checks: {total}")
    print(f"  Passing: {passing}")
    print(f"  Failing: {failing}")
    if total > 0:
        pct = 100*passing//total
        print(f"  Score:   {pct}%")

    print()
    print("  FAILING PHONEMES:")
    for r in REPORT:
        if r.strip().startswith('[✗]'):
            print(f"  {r.strip()}")

    print()
    print("="*60)
    print()
    print("  Listen:")
    print(f"  afplay {rbow_path}")
    print()
    print("  Or by tier:")
    for tier in [
        'tier1_vowels',
        'tier2_nasals',
        'tier3_approximants',
        'tier4_fric_unvoiced',
        'tier5_fric_voiced',
        'tier6_stops_unvoiced',
        'tier7_stops_voiced',
        'tier8_transitions',
        'tier9_minimal_pairs',
    ]:
        print(f"  ls {OUT_ROOT}/{tier}/")
    print()
    print("  Full report:")
    print(f"  cat {report_path}")
    print()


if __name__ == "__main__":
    run_rainbow()
