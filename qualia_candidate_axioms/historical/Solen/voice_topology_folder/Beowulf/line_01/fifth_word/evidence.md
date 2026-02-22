# GĒAR-DAGUM — RECONSTRUCTION EVIDENCE
**Old English:** gēar-dagum  
**IPA:** [ɡeːɑrdɑɡum]  
**Meaning:** in days of yore (dative plural of *gēar-dæg*, year-day)  
**Source:** Beowulf, line 1, word 5  
**Date verified:** February 2026  
**Diagnostic version:** v3  
**Reconstruction version:** v2  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  G1 onset      ✓ PASS
D2  Ē vowel       ✓ PASS
D3  A1 vowel      ✓ PASS
D4  R trill       ✓ PASS
D5  D onset       ✓ PASS
D6  A2 vowel      ✓ PASS
D7  G2 onset      ✓ PASS
D8  U vowel       ✓ PASS
D9  M nasal       ✓ PASS
D10 Full word     ✓ PASS
D11 Perceptual    LISTEN
```

Total duration: **804 ms** (35453 samples at 44100 Hz)

---

## PHONEME RECORD

### G1 — voiced velar stop [ɡ] before [eː]
Word-initial velar before a front vowel.
Burst centroid in the velar range (~1600 Hz).

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1336 | 0.005–0.80 | PASS |
| Burst centroid | 1620 Hz | 800–2500 Hz | PASS |

**Parameters:**
- Burst CF: 1500 Hz
- Closure: 50 ms, Burst: 12 ms
- Release trajectory: G1_F → EE_F

---

### Ē — long close-mid front vowel [eː]
Identical phoneme to WĒ (line 1, word 1).
Same formant targets, same duration.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8572 | 0.75–1.0 | PASS |
| F1 centroid (200–700 Hz) | 310 Hz | 250–480 Hz | PASS |
| F2 centroid (1800–2600 Hz) | 2081 Hz | 1800–2600 Hz | PASS |

**Parameters:** F1=390 Hz, F2=2100 Hz, duration 160 ms

---

### A1 — short open back vowel [ɑ]
First of two [ɑ] instances. Between [eː] and [r].
Same parameters as GĀR-DENA final [ɑ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.5988 | 0.50–1.0 | PASS |
| F1+F2 centroid (600–1400 Hz) | 830 Hz | 750–1050 Hz | PASS |

**Parameters:** F1=840 Hz, F2=1150 Hz, duration 65 ms

---

### R — alveolar trill [r]
Short 2-closure trill at the compound boundary
GĒAR | DAGUM. Same parameters as GĀR-DENA R.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1826 | 0.005–0.80 | PASS |
| Trill modulation depth | 0.5647 | 0.22–1.0 | PASS |
| Trill rate | 18.2 Hz | 15–70 Hz | PASS |

---

### D — voiced alveolar stop [d]
Onset of DAGUM. Same parameters as GĀR-DENA D.
Alveolar burst at ~3460 Hz, distinct from
velar G burst at ~1600 Hz.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1051 | 0.005–0.80 | PASS |
| Burst centroid | 3462 Hz | 2000–5000 Hz | PASS |

---

### A2 — short open back vowel [ɑ]
Second [ɑ] instance. Unstressed syllable of DAGUM.
Identical phoneme and parameters to A1.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.5988 | 0.50–1.0 | PASS |
| F1+F2 centroid (600–1400 Hz) | 831 Hz | 750–1050 Hz | PASS |

---

### G2 — voiced velar stop [ɡ] before [u]
Second G in the word. Before back rounded [u].
Burst CF lower than G1: back vowel context
lowers the F2 locus, pulling the burst centroid
down from ~1600 Hz to ~1200 Hz.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1454 | 0.005–0.80 | PASS |
| Burst centroid | 1237 Hz | 600–2000 Hz | PASS |

**Contrast with G1:**

| | Burst CF | Centroid | Context |
|---|---|---|---|
| G1 | 1500 Hz | 1620 Hz | before [eː] — front |
| G2 | 1200 Hz | 1237 Hz | before [u] — back rounded |

The ~400 Hz drop in burst centroid between G1 and G2
reflects the velar place shift with vowel context —
a known acoustic correlate of coarticulation in
velar stops.

---

### U — short close back rounded vowel [u]
New phoneme. The vowel of "boot" but short.
Lip rounding is the defining feature — it pulls
F2 down from ~1000 Hz (unrounded back) to ~700 Hz.
This is the lowest F2 of any vowel in the inventory.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6760 | 0.65–1.0 | PASS |
| F1 centroid (100–600 Hz) | 218 Hz | 200–380 Hz | PASS |
| F2 centroid (400–1200 Hz) | 687 Hz | 500–900 Hz | PASS |

**Formant parameters:** F1=300 Hz, F2=700 Hz

**Vowel F2 inventory comparison:**

| Vowel | F2 | Rounding |
|---|---|---|
| [iː] | 2300 Hz | none |
| [e] / [eː] | 2100–2200 Hz | none |
| [ɪ] | 1800 Hz | none |
| [ɑː] / [ɑ] | 1100–1150 Hz | none |
| [u] | 700 Hz | rounded |

[u] has the lowest F2 in the system. Rounding
contributes approximately 400 Hz of F2 lowering
relative to an unrounded back vowel.

**Duration:** 60 ms (short, unstressed)

---

### M — voiced bilabial nasal [m]
New phoneme. Bilabial closure — both lips together.
The oral cavity is longer than for alveolar [n],
shifting the antiformant lower: ~1000 Hz vs ~800 Hz.

**Antiformant measurement:** The [m] murmur has
nearly all energy below 600 Hz. The antiformant
at 1000 Hz is verified by comparing low-band energy
(200–600 Hz) to notch-band energy (850–1150 Hz).
A ratio > 2.0 confirms the notch region is
suppressed relative to the murmur body.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7888 | 0.60–1.0 | PASS |
| RMS (nasal murmur) | 0.2076 | 0.005–0.25 | PASS |
| Murmur/notch ratio | 5.87 | > 2.0 | PASS |

**Parameters:**
- Antiformant: 1000 Hz (cf. [n] at 800 Hz)
- Bandwidth: 200 Hz
- Duration: 60 ms (word-final)

**Contrast with [n]:**

| | Antiformant | Ratio check | Oral closure |
|---|---|---|---|
| [n] | 800 Hz | notch < ref above | alveolar ridge |
| [m] | 1000 Hz | low-band > notch | bilabial |

---

### Full word — D10

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2262 | 0.01–0.90 | PASS |
| Duration | 804 ms | 400–900 ms | PASS |

**Segment boundaries (samples at 44100 Hz):**

| Segment | Phoneme | Duration |
|---|---|---|
| G1 | [ɡ] | ~92 ms |
| Ē | [eː] | 160 ms |
| A1 | [ɑ] | 65 ms |
| R | [r] | ~115 ms |
| D | [d] | ~80 ms |
| A2 | [ɑ] | 65 ms |
| G2 | [ɡ] | ~92 ms |
| U | [u] | 60 ms |
| M | [m] | 60 ms |

---

## DIAGNOSTIC METHODOLOGY NOTES

### Velar burst centroid shift
The two [ɡ] onsets differ in burst centroid by
~400 Hz (G1: 1620 Hz, G2: 1237 Hz). This is not
a synthesis artefact — it reflects the well-documented
acoustic property of velar stops: the burst centroid
shifts with following vowel context because the tongue
dorsum contact point moves anterior (higher F2 locus)
before front vowels and posterior (lower F2 locus)
before back vowels. The parameters encode this
directly: G1_BURST_CF=1500, G2_BURST_CF=1200.

### [u] formant measurement
The [u] F1 at 300 Hz falls close to the 2nd harmonic
of the 145 Hz pitch (290 Hz). The same harmonic-pull
effect seen in [ɪ] and [e] diagnostics applies here.
The F1 centroid of the 100–600 Hz band reads at
218 Hz rather than 300 Hz. The floor of 200 Hz
accommodates this. The F2 centroid at 687 Hz in the
400–1200 Hz band is a clean measurement — [u] F2 at
700 Hz sits between harmonics 4 (580 Hz) and 5 (725 Hz)
and the centroid lands accurately.

### [m] antiformant measurement
The [m] nasal murmur spectrum is concentrated below
600 Hz with near-zero energy above 1200 Hz. This makes
the [n]-style ratio measurement (notch band vs reference
band above notch) impossible — there is nothing in the
reference band. The correct measurement is inverted:
low-band (200–600 Hz) vs notch-band (850–1150 Hz).
A ratio of 5.87 means the murmur body has ~6× more
energy than the notch region, confirming the
antiformant suppression is present and correct.

In v1 the second M resonator (M_GAINS[1]=2.0) was too
weak to produce energy in the 200–800 Hz murmur region.
The Rosenberg pulse produced only a fundamental spike
at ~129 Hz. Raising M_GAINS[1] to 12.0 and widening
M_B[1] from 250 to 350 Hz filled the murmur region
correctly, making the antiformant measurable.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `gear_dagum_dry.wav` | Full word, no reverb, 145 Hz |
| `gear_dagum_hall.wav` | Full word, hall reverb RT60=2.0s |
| `gear_dagum_slow.wav` | Full word, 4× time-stretched |
| `gear_dagum_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `gear_dagum_u_isolated.wav` | U vowel only, 4× slow |
| `gear_dagum_m_isolated.wav` | M nasal only, 4× slow |

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters |
| v2 | M_GAINS[1] 2.0→12.0; M_B[1] 250→350 Hz. [m] murmur was single spike at 129 Hz. Second resonator too weak to produce energy in murmur region. |

---

## LINE 1 STATUS

| Word | IPA | Status |
|---|---|---|
| HWÆT | [ʍæt] | pending |
| WĒ | [weː] | ✓ verified |
| GĀR-DENA | [ɡɑːrdenɑ] | ✓ verified |
| IN | [ɪn] | ✓ verified |
| GĒAR-DAGUM | [ɡeːɑrdɑɡum] | ✓ verified |

Four of five words verified. HWÆT remains.
HWÆT contains [ʍ] — the voiceless labio-velar
fricative — not yet in the phoneme inventory.

---

*GĒAR-DAGUM [ɡeːɑrdɑɡum] verified.*  
*Line 1 words 2–5 complete.*  
*Next: HWÆT [ʍæt] — word 1, voiceless labio-velar fricative.*
