# ÞRYM — RECONSTRUCTION EVIDENCE
**Old English:** þrym  
**IPA:** [θrym]  
**Meaning:** glory, might, greatness  
**Source:** Beowulf, line 2, word 2 (overall word 7)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  Þ fricative   ✓ PASS
D2  R trill       ✓ PASS
D3  Y vowel       ✓ PASS
D4  M nasal       ✓ PASS
D5  Full word     ✓ PASS
D6  Perceptual    LISTEN
```

Total duration: **340 ms** (14992 samples at 44100 Hz)  
Clean first pass. Zero new phonemes. All four previously
verified in earlier reconstructions.

---

## PHONEME RECORD

### Þ — voiceless dental fricative [θ]
Third instance. Parameters consistent with
ÞĒOD-CYNINGA D1. Slightly shorter duration
(75 ms vs 80 ms) — word-initial before trill
rather than before a long vowel.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1187 | 0.0–0.35 | PASS |
| RMS level | 0.1097 | 0.005–0.80 | PASS |
| Frication centroid (1–8 kHz) | 4164 Hz | 2500–5000 Hz | PASS |

**Cross-instance consistency:**

| Word | Context | Centroid |
|---|---|---|
| ÞĒOD-CYNINGA | before [eː] | 4341 Hz |
| ÞRYM | before [r] | 4164 Hz |

~180 Hz variation between instances.
Both within the 2500–5000 Hz target band.
The dental fricative centroid is stable
across phonological contexts — expected,
since frication is generated at the dental
constriction regardless of following segment.

---

### R — alveolar trill [r]
Fourth instance across the reconstruction.
Consistent parameters throughout.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1978 | 0.005–0.80 | PASS |
| Trill modulation depth | 0.5810 | 0.22–1.0 | PASS |
| Trill rate | 18.2 Hz | 15–70 Hz | PASS |

**Trill rate 18.2 Hz** — at the low end of the
natural range (15–30 Hz typical for citation
form). Two closures at this rate produce a
perceptually borderline trill/flap quality.
This is a known property of the OLA-based
trill synthesizer. The modulation depth of
0.58 confirms periodic amplitude variation
is present and measurable.

**Cross-instance trill rate:**

| Word | Rate |
|---|---|
| GĀR-DENA | 18.2 Hz |
| GĒAR-DAGUM | 18.2 Hz |
| ÞRYM | 18.2 Hz |

Rate is determined by R_CLOSURE_MS (35 ms)
and R_OPEN_MS (20 ms) — fixed parameters.
Consistent across all instances. To raise
the trill rate toward 25 Hz, reduce
R_CLOSURE_MS to ~25 ms.

---

### Y — short close front rounded [y]
Second instance. Previously verified in
ÞĒOD-CYNINGA D6. Parameters identical.

Here [y] is the sole vowel of a stressed
heavy syllable — the nucleus of the word.
Duration raised slightly to 70 ms (from
65 ms) to reflect the syllable weight.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6852 | 0.65–1.0 | PASS |
| F1 centroid (150–700 Hz) | 211 Hz | 200–420 Hz | PASS |
| F2 centroid (1000–2200 Hz) | 1428 Hz | 1200–1800 Hz | PASS |

**Cross-instance [y] consistency:**

| Word | F1 centroid | F2 centroid |
|---|---|---|
| ÞĒOD-CYNINGA | 219 Hz | 1429 Hz |
| ÞRYM | 211 Hz | 1428 Hz |

8 Hz F1 variation, 1 Hz F2 variation.
Effectively identical. The [y] phoneme
is stable and reproducible across
different phonological contexts
(post-[k] vs post-[r]).

---

### M — voiced bilabial nasal [m]
Second instance. Previously verified in
GĒAR-DAGUM D9. Parameters identical.
Duration raised to 65 ms (from 60 ms) —
word-final nasal in a stressed syllable
carries slightly longer duration than
in an unstressed syllable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7980 | 0.60–1.0 | PASS |
| RMS (nasal murmur) | 0.2095 | 0.005–0.25 | PASS |
| Murmur/notch ratio (200–600 / 850–1150 Hz) | 5.87 | > 2.0 | PASS |

**Cross-instance [m] consistency:**

| Word | RMS | Murmur/notch |
|---|---|---|
| GĒAR-DAGUM | 0.2076 | 5.87 |
| ÞRYM | 0.2095 | 5.87 |

Near-identical values. The bilabial nasal
antiformant at 1000 Hz is stable and
reproducible. Murmur/notch ratio of 5.87
in both instances — the synthesis is
deterministic for this phoneme.

---

### Full word — D5

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2315 | 0.01–0.90 | PASS |
| Duration | 340 ms | 150–450 ms | PASS |

**Segment boundaries (estimated):**

| Segment | Phoneme | Duration |
|---|---|---|
| Þ | [θ] | 75 ms |
| R | [r] | ~130 ms |
| Y | [y] | 70 ms |
| M | [m] | 65 ms |

ÞRYM is the shortest word reconstructed
so far (340 ms vs IN at 120 ms for the
monosyllable, but ÞRYM has more consonants).

---

## PHONETIC NOTES

### [θr] onset cluster
Old English allows word-initial [θr].
The fricative releases directly into the
trill onset — no vowel or sonorant transition
between them. The trill begins voicing
immediately after the frication noise ends.
This is typologically uncommon — most
languages do not permit voiceless fricative
+ trill clusters word-initially. Old English
does, and this cluster survives in Modern
English "three", "throw", "through" (where
[θr] is preserved, though the [r] has
shifted from trill to approximant).

### [ym] coda
The [y] vowel is followed immediately by
the bilabial nasal [m]. The lip rounding
of [y] anticipates and smoothly coarticulates
with the bilabial closure of [m]. In the
synthesis the F_next parameter of synth_Y_short
is set to M_F, encoding the formant transition
toward the nasal murmur formant structure.

### Alliterative stress
In Beowulf's alliterative meter, line 2
alliterates on [θ]:
- **þ**ēod-cyninga (word 6)
- **þ**rym (word 7)
- ge**fr**ūnon (word 8) — secondary alliteration

ÞRYM carries the second alliterating stress
of the line. In performance (dil=2.5,
pitch=110 Hz) the word is expanded to
~850 ms — the [θ] onset and [y] nucleus
are the perceptually prominent events.

---

## SYNTHESIS QUALITY NOTE

This reconstruction uses a Rosenberg pulse
formant synthesizer — a cascade/parallel
architecture equivalent to Klatt (1980).
The output is recognizably synthetic.

**What the synthesis correctly captures:**
- Formant frequencies and bandwidths
- Voicing/voicelessness contrast
- Stop burst place (spectral centroid)
- Nasal antiformant positions
- Fricative spectral shape
- Trill amplitude modulation rate

**What the synthesis does not capture:**
- Natural pitch perturbation (jitter/shimmer)
- Subglottal resonances
- Microprosodic F0 variation
- Coarticulation beyond linear F-interpolation
- Source-filter nonlinearities

The synthesis is a phonetic scaffold —
acoustically verifiable, reproducible,
and correctable. It is not a perceptual
reconstruction of natural speech.

---

## CROSS-WORD PHONEME INVENTORY
*All phonemes verified as of this word:*

| Phoneme | First verified | Instances |
|---|---|---|
| [ʍ] | HWÆT | 1 |
| [æ] | HWÆT | 1 |
| [t] | HWÆT | 1 |
| [w] | WĒ | 1 |
| [eː] | WĒ | 3 |
| [ɡ] | GĀR-DENA | 4 |
| [ɑː] | GĀR-DENA | 1 |
| [r] | GĀR-DENA | 4 |
| [d] | GĀR-DENA | 3 |
| [e] | GĀR-DENA | 1 |
| [n] | GĀR-DENA | 3 |
| [ɑ] | GĀR-DENA | 5 |
| [ɪ] | IN | 2 |
| [ɑ] | IN | — |
| [u] | GĒAR-DAGUM | 1 |
| [m] | GĒAR-DAGUM | 2 |
| [θ] | ÞĒOD-CYNINGA | 2 |
| [o] | ÞĒOD-CYNINGA | 1 |
| [k] | ÞĒOD-CYNINGA | 1 |
| [y] | ÞĒOD-CYNINGA | 2 |
| [ŋ] | ÞĒOD-CYNINGA | 1 |

21 distinct phonemes verified across 7 words.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `thrym_dry.wav` | Full word, no reverb, 145 Hz |
| `thrym_hall.wav` | Full word, hall reverb RT60=2.0s |
| `thrym_slow.wav` | Full word, 4× time-stretched |
| `thrym_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. Clean first pass. |

---

## LINE STATUS

| Line | Word | IPA | Status |
|---|---|---|---|
| 1 | HWÆT | [ʍæt] | ✓ verified |
| 1 | WĒ | [weː] | ✓ verified |
| 1 | GĀR-DENA | [ɡɑːrdenɑ] | ✓ verified |
| 1 | IN | [ɪn] | ✓ verified |
| 1 | GĒAR-DAGUM | [ɡeːɑrdɑɡum] | ✓ verified |
| 2 | ÞĒOD-CYNINGA | [θeːodkyniŋɡɑ] | ✓ verified |
| 2 | ÞRYM | [θrym] | ✓ verified |
| 2 | GEFRŪNON | [jefrуːnon] | pending |

---

*ÞRYM [θrym] verified.*  
*Next: GEFRŪNON [jefrуːnon] — line 2, word 3.*
