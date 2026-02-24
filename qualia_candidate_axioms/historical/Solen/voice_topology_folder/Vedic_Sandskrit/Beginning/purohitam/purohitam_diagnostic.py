================================================================
  PUROHITAM DIAGNOSTIC v2.0
  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
  v4 UNIFIED SOURCE ARCHITECTURE

  v1.0 → v2.0: UNIFIED SOURCE STOPS

  v1.0 measured burst-only arrays (7-8ms plucks).
  v2.0 measures unified source stops with internal
  phase extraction: silence → closure → burst → VOT.

  NEW measurements:
    - Closure RMS (subglottal floor, should be ~0.001)
    - Burst centroid on burst phase only
    - VOT late RMS (voicing emergence)
    - [p]-vs-[t] centroid separation (place contrast)

  The breath is continuous. The tongue is the envelope.
  The diagnostic measures the physics inside the stop.

  "Fix the ruler, not the instrument."
================================================================


========================================================================
PUROHITAM DIAGNOSTIC v2.0
PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v4 UNIFIED SOURCE ARCHITECTURE
========================================================================

Synthesizing word (v4 unified source)...
  Word length: 24999 samples (566.9 ms)

  Expected segment map:
    [p] UNIFIED (word-initial)        45.0 ms  ( 1984 samples)
    head + [u]                        65.0 ms  ( 2866 samples)
    [r]                               30.0 ms  ( 1323 samples)
    [oo]                             100.0 ms  ( 4410 samples)
    [h]                               65.0 ms  ( 2866 samples)
    [i] + closing tail                75.0 ms  ( 3307 samples)
    [t] UNIFIED                       37.0 ms  ( 1631 samples)
    head + [a]                        70.0 ms  ( 3087 samples)
    [m] + release                     80.0 ms  ( 3528 samples)
    TOTAL                           566.9 ms  (25002 samples)
    ACTUAL                          566.9 ms  (24999 samples)
Wrote output_play/diag_pur_word_dry.wav
Wrote output_play/diag_pur_word_slow6x.wav
Wrote output_play/diag_pur_word_slow12x.wav
Wrote output_play/diag_pur_word_hall.wav
Wrote output_play/diag_pur_perf.wav
Wrote output_play/diag_pur_perf_hall.wav
Wrote output_play/diag_pur_perf_slow6x.wav
Wrote output_play/diag_pur_p_unified.wav
Wrote output_play/diag_pur_p_unified_slow6x.wav
Wrote output_play/diag_pur_p_unified_slow12x.wav
Wrote output_play/diag_pur_t_unified.wav
Wrote output_play/diag_pur_t_unified_slow6x.wav
Wrote output_play/diag_pur_t_unified_slow12x.wav
Wrote output_play/diag_pur_PU_syllable.wav
Wrote output_play/diag_pur_PU_syllable_slow6x.wav
Wrote output_play/diag_pur_PU_syllable_slow12x.wav
Wrote output_play/diag_pur_iTAM_syllable.wav
Wrote output_play/diag_pur_iTAM_syllable_slow6x.wav
Wrote output_play/diag_pur_iTAM_syllable_slow12x.wav

------------------------------------------------------------------------
SECTION A: SIGNAL INTEGRITY
------------------------------------------------------------------------
  PASS  NaN count: 0   (expected [0 - 0] )
  PASS  Inf count: 0   (expected [0 - 0] )
  PASS  Peak amplitude: 0.7500   (expected [0.0100 - 1.0000] )
  PASS  DC offset |mean|: 0.000497   (expected [0.000000 - 0.050000] )

------------------------------------------------------------------------
SECTION B: SIGNAL CONTINUITY (SEGMENT-AWARE)
  Composite segments tested on CORE ONLY.
  Cold-start excluded. Envelope-normalized periodicity.
------------------------------------------------------------------------

  -- Tier 1: Within-segment --
  PASS    [p] UNIFIED (word-initial) max |delta| (unvoiced): 0.167669   (expected [0.000000 - 0.500000] )
  PASS  head + [u] (core only) max_ss |delta|=0.1736 (below threshold)
  PASS  [r] max_ss |delta|=0.6102 (short segment (cold-start dominant))
  PASS  [oo] max_ss |delta|=0.0372 (below threshold)
  PASS    [h] max |delta| (unvoiced): 0.057788   (expected [0.000000 - 0.500000] )
  PASS  [i] + closing tail (core only, 50ms) max_ss |delta|=0.0320 (below threshold)
  PASS    [t] UNIFIED max |delta| (unvoiced): 0.225949   (expected [0.000000 - 0.500000] )
  PASS  head + [a] (core only) max_ss |delta|=0.7445 (steady-state clean (cold-start excluded))
  PASS  [m] + release max_ss |delta|=0.0136 (below threshold)

  -- Tier 2: Segment-join continuity --
  PASS    JOIN (stop) [p] UNIFIED (word-initial) -> head + [u]: 0.000000   (expected [0.000000 - 0.850000] )
  PASS  JOIN (voiced) head + [u] -> [r]: 0.000016 (below threshold)
  PASS  JOIN (voiced) [r] -> [oo]: 0.000027 (below threshold)
  PASS  JOIN (voiced) [oo] -> [h]: 0.000859 (below threshold)
  PASS  JOIN (voiced) [h] -> [i] + closing tail: 0.000020 (below threshold)
  PASS    JOIN (stop) [i] + closing tail -> [t] UNIFIED: 0.000522   (expected [0.000000 - 0.850000] )
  PASS    JOIN (stop) [t] UNIFIED -> head + [a]: 0.000000   (expected [0.000000 - 0.850000] )
  PASS  JOIN (voiced) head + [a] -> [m] + release: 0.000069 (below threshold)
  PASS  [p] unified isolated max |delta|: 0.098174   (expected [0.000000 - 0.500000] )
  PASS  [t] unified isolated max |delta|: 0.250629   (expected [0.000000 - 0.500000] )

------------------------------------------------------------------------
SECTION C: [p] UNIFIED SOURCE — BILABIAL BURST
  Siksa: osthya aghosa alpaprana.
  Word-initial: 10ms silence + unified source.
  Internal phases: closure → burst → VOT.
------------------------------------------------------------------------
  PASS  [p] closure RMS (subglottal): 0.023346   (expected [0.000000 - 0.050000] )
  PASS  [p] burst centroid: 1891.8 Hz  (expected [800.0 - 2500.0] Hz)
  PASS  [p] burst RMS: 0.157855   (expected [0.001000 - 1.000000] )
  PASS  [p] closure voicing (aghosa): -0.0183   (expected [-1.0000 - 0.3000] )
  PASS  [p] VOT late RMS (voicing emerging): 0.018586   (expected [0.000500 - 1.000000] )
  PASS  [p] total duration: 45.0 ms  (expected [30.0 - 60.0] ms)

------------------------------------------------------------------------
SECTION D: [t] UNIFIED SOURCE — DENTAL BURST
  Siksa: dantya aghosa alpaprana.
  Internal phases: closure → burst → VOT.
  The breath is continuous. The tongue is the envelope.
------------------------------------------------------------------------
  PASS  [t] closure RMS (subglottal): 0.009177   (expected [0.000000 - 0.050000] )
  PASS  [t] burst centroid: 3127.4 Hz  (expected [2500.0 - 5500.0] Hz)
  PASS  [t] burst RMS: 0.160694   (expected [0.001000 - 1.000000] )
  PASS  [t] closure voicing (aghosa): -0.0140   (expected [-1.0000 - 0.3000] )
  PASS  [t] VOT late RMS (voicing emerging): 0.016884   (expected [0.000500 - 1.000000] )
  PASS  [t] total duration: 37.0 ms  (expected [25.0 - 55.0] ms)

------------------------------------------------------------------------
SECTION E: [p]-vs-[t] PLACE CONTRAST
  Bilabial (LOW-BURST) vs Dental (HIGH-BURST).
  Centroid separation proves two distinct places.
------------------------------------------------------------------------
  PASS  [t]-[p] centroid separation: 1235.5 Hz  (expected [500.0 - 5000.0] Hz)
  INFO  [p] burst centroid: 1891.8 Hz (bilabial)
  INFO  [t] burst centroid: 3127.4 Hz (dental)
  INFO  Separation: 1235.5 Hz

------------------------------------------------------------------------
SECTION F: CLOSING TAIL — [i] OWNS THE CLOSURE
  Core voicing + RMS fade = the tongue rises to dental,
  the cords were vibrating, the amplitude decreases.
------------------------------------------------------------------------

  -- [i] closing tail --
  PASS  [i] core voicing: 0.7556   (expected [0.5000 - 1.0000] )
  PASS  [i] tail/core RMS ratio: 0.4630   (expected [0.0000 - 0.9000] )

------------------------------------------------------------------------
SECTION G: OPENING HEADS
------------------------------------------------------------------------

  -- [u] after [p] --
  PASS  [u] after [p] core voicing: 0.7505   (expected [0.5000 - 1.0000] )
  PASS  [u] after [p] head rising: 0.045333 -> 0.271646

  -- [a] after [t] --
  PASS  [a] after [t] core voicing: 0.7886   (expected [0.5000 - 1.0000] )
  PASS  [a] after [t] head rising: 0.041917 -> 0.277682

------------------------------------------------------------------------
SECTION H: VOWELS — THE SUSTAINED NOTES
------------------------------------------------------------------------

  -- [u] --
  PASS  [u] voicing: 0.7505   (expected [0.5000 - 1.0000] )
  PASS  [u] F1: 272.2 Hz  (expected [200.0 - 450.0] Hz)
  PASS  [u] F2: 878.9 Hz  (expected [600.0 - 1100.0] Hz)

  -- [oo] --
  PASS  [oo] voicing: 0.7871   (expected [0.5000 - 1.0000] )
  PASS  [oo] F1: 420.5 Hz  (expected [300.0 - 600.0] Hz)
  PASS  [oo] F2: 866.3 Hz  (expected [600.0 - 1100.0] Hz)

  -- [i] --
  PASS  [i] voicing: 0.7556   (expected [0.5000 - 1.0000] )
  PASS  [i] F1: 302.4 Hz  (expected [200.0 - 450.0] Hz)
  PASS  [i] F2: 2135.4 Hz  (expected [1800.0 - 2600.0] Hz)

  -- [a] --
  PASS  [a] voicing: 0.7886   (expected [0.5000 - 1.0000] )
  PASS  [a] F1: 658.6 Hz  (expected [550.0 - 900.0] Hz)
  PASS  [a] F2: 1083.9 Hz  (expected [850.0 - 1400.0] Hz)

------------------------------------------------------------------------
SECTION I: FRICATIVE [h]
  Siksa: kanthya aghosa mahaprana.
  Voiceless glottal fricative. Noise source.
------------------------------------------------------------------------
  PASS  [h] voicing (aghosa): -0.2057   (expected [-1.0000 - 0.3000] )
  PASS  [h] RMS (audible): 0.055037   (expected [0.001000 - 0.500000] )

------------------------------------------------------------------------
SECTION J: TAP [r] AND NASAL [m]
------------------------------------------------------------------------

  -- [r] alveolar tap --
  PASS  [r] voicing: 0.5265   (expected [0.2500 - 1.0000] )
  PASS  [r] dip ratio (mid/edge): 0.8777   (expected [0.0000 - 0.9500] )

  -- [m] bilabial nasal --
  PASS  [m] voicing: 0.7955   (expected [0.5000 - 1.0000] )
  PASS  [m] LF ratio: 0.9961   (expected [0.2000 - 1.0000] )

------------------------------------------------------------------------
SECTION K: SYLLABLE-LEVEL COHERENCE
  PU.RŌ.HI.TAM
------------------------------------------------------------------------
  PASS  [p] trough: 0.0365 < 0.2944
  PASS  [t] trough: 0.0341 < min(0.2705, 0.2912)
  PASS  [oo] relative amplitude: 1.0000   (expected [0.6000 - 1.0000] )
  PASS  Word duration: 566.9 ms  (expected [350.0 - 750.0] ms)

========================================================================
ALL 64 DIAGNOSTICS PASSED

PUROHITAM v4 UNIFIED SOURCE — VERIFIED.

Ruler calibration history:
  v1.0: Initial (v3 pluck, burst-only segments)
  v2.0: Unified source (v4, internal phase extraction)
        Stops now contain closure+burst+VOT internally.
        Burst centroid measured on burst phase only.
        Closure RMS confirms subglottal floor.
        VOT RMS confirms voicing emergence.

Section structure:
  A: Signal integrity (NaN, Inf, peak, DC)
  B: Signal continuity (glottal periodicity)
  C: [p] unified (closure, centroid, voicelessness)
  D: [t] unified (closure, centroid, voicelessness)
  E: [p]-vs-[t] place contrast (centroid separation)
  F: Closing tail ([i] core voicing + RMS fade)
  G: Opening heads ([u] after [p], [a] after [t])
  H: Vowels ([u], [oo], [i], [a] — voicing, F1, F2)
  I: Fricative [h] (voicelessness, RMS)
  J: Tap [r] + Nasal [m] (voicing, dip, LF)
  K: Syllable cadence (troughs, prominence, duration)

Phonemes verified in this word:
  [p]  voiceless bilabial stop (UNIFIED, word-initial)
  [u]  short close back rounded
  [ɾ]  alveolar tap
  [oː] long close-mid back rounded
  [h]  voiceless glottal fricative
  [i]  short close front unrounded
  [t]  voiceless dental stop (UNIFIED)
  [ɑ]  short open central unrounded
  [m]  bilabial nasal (word-final)

Śikṣā alignment:
  [p] = oṣṭhya aghoṣa alpaprāṇa ✓
  [t] = dantya aghoṣa alpaprāṇa ✓
  [h] = kaṇṭhya aghoṣa mahāprāṇa ✓

Architecture:
  PLUCK + UNIFIED SOURCE compose:
    Vowels own transitions (closing tails, opening heads)
    Stops own their physics (one breath, one envelope)
    No boundary anywhere is born from different sources

PERCEPTUAL VERIFICATION:
  afplay output_play/diag_pur_p_unified_slow12x.wav
  afplay output_play/diag_pur_t_unified_slow12x.wav
  afplay output_play/diag_pur_PU_syllable_slow12x.wav
  afplay output_play/diag_pur_iTAM_syllable_slow12x.wav
  afplay output_play/diag_pur_word_slow6x.wav
  afplay output_play/diag_pur_perf_hall.wav

The ear is the FINAL arbiter.

"The sounds were always there.
  The language is being found, not invented."
========================================================================
