# MONGUM — RECONSTRUCTION EVIDENCE
**Old English:** mongum  
**IPA:** [moŋɡum]  
**Meaning:** many (dative plural adjective)  
**Source:** Beowulf, line 6, word 1 (overall word 22)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  M nasal initial   ✓ PASS
D2  O vowel           ✓ PASS
D3  NG nasal          ✓ PASS
D4  G stop medial     ✓ PASS
D5  U vowel           ✓ PASS
D6  M nasal final     ✓ PASS
D7  Full word         ✓ PASS
D8  Perceptual        LISTEN
```

Total duration: **365 ms** (16094 samples at 44100 Hz)  
Clean first run. Seven for seven.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All seven numeric checks passed on first run. |

---

## PHONEME RECORD

### M — voiced bilabial nasal [m] initial
Word-initial. Onset from silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

---

### O — short close-mid back rounded [o]
Post-nasal position. [m]→[o].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6692 | 0.50–1.0 | PASS |
| F2 centroid (550–1100 Hz) | 747 Hz | 600–1000 Hz | PASS |

F2 747 Hz — back rounded vowel.
Consistent with previous [o] instances.

---

### NG — voiced velar nasal [ŋ]
Post-vowel position. [o]→[ŋ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7797 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2340 | 0.005–0.25 | PASS |

---

### G — voiced velar stop [ɡ] medial
Post-nasal position. [ŋ]→[ɡ].
The [ŋɡ] cluster — nasal + stop —
both fully realised. The nasal
murmur of [ŋ] carries into the
closure of [ɡ], then the burst
releases into [u].

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1087 | 0.005–0.70 | PASS |
| Duration | 65 ms | 40–100 ms | PASS |

---

### U — short close back rounded [u]
Post-stop position. [ɡ]→[u].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6675 | 0.50–1.0 | PASS |
| F2 centroid (500–1200 Hz) | 738 Hz | 550–1100 Hz | PASS |

---

### M — voiced bilabial nasal [m] final
Word-final. Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

Initial and final [m] instances
produce identical measurements —
the synthesiser is deterministic
for voiced nasals. Both instances
use the same parameters and produce
the same output. Expected behaviour.

---

### Full word — D7

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2822 | 0.01–0.90 | PASS |
| Duration | 365 ms | 330–560 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| M | [m] | 65 ms | voiced bilabial nasal |
| O | [o] | 55 ms | short close-mid back rounded |
| NG | [ŋ] | 60 ms | voiced velar nasal |
| G | [ɡ] | 65 ms | voiced velar stop medial |
| U | [u] | 55 ms | short close back rounded |
| M | [m] | 65 ms | voiced bilabial nasal |

Total: 365 ms. Six segments.
The word is entirely voiced —
no voiceless segments. Every
phoneme carries vocal fold vibration
throughout. The voicing measure
stays above 0.65 for all segments.
This is the most uniformly voiced
word reconstructed so far.

---

## MORPHOLOGICAL NOTE

**mongum — dative plural:**

*monig* (adjective: many, much)
inflects as a strong adjective.
Dative plural: *mongum*.

Agrees with *mǣgþum* (tribes,
kinship groups) — dative plural
noun. The adjective and noun agree
in case, number, and gender.

*mongum mǣgþum* — to/from many
tribes. The dative marks the
semantic relationship: Scyld's
terror was directed at and exacted
tribute from many peoples, not
just one enemy nation.

**monig → many:**

| Stage | Form | Change |
|---|---|---|
| OE | *monig* | [monɪɣ] |
| ME | *mani* | [manɪ] |
| ModE | *many* | [mɛni] |

The [ɣ] (voiced velar fricative)
in OE *monig* was lost in Middle
English — the word simplified.
The [ɣ] that will be verified in
MǢGÞUM is the same phoneme that
existed at the end of *monig*
in its uninflected form.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `mongum_dry.wav` | Full word, no reverb, 145 Hz |
| `mongum_hall.wav` | Full word, hall reverb RT60=2.0s |
| `mongum_slow.wav` | Full word, 4× time-stretched |
| `mongum_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**32 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | mongum ✓ — in progress |

---

## PHONEME INVENTORY
*All verified phonemes — 32 total:*

| Phoneme | Description | First word |
|---|---|---|
| [ʍ] | voiceless labio-velar fricative | HWÆT |
| [æ] | open front unrounded | HWÆT |
| [t] | voiceless alveolar stop | HWÆT |
| [w] | voiced labio-velar approximant | WĒ |
| [eː] | long close-mid front | WĒ |
| [ɡ] | voiced velar stop | GĀR-DENA |
| [ɑː] | long open back | GĀR-DENA |
| [r] | alveolar trill | GĀR-DENA |
| [d] | voiced alveolar stop | GĀR-DENA |
| [e] | short close-mid front | GĀR-DENA |
| [n] | voiced alveolar nasal | GĀR-DENA |
| [ɑ] | short open back | GĀR-DENA |
| [ɪ] | short near-close front | IN |
| [u] | short close back rounded | GĒAR-DAGUM |
| [m] | voiced bilabial nasal | GĒAR-DAGUM |
| [θ] | voiceless dental fricative | ÞĒOD-CYNINGA |
| [o] | short close-mid back rounded | ÞĒOD-CYNINGA |
| [k] | voiceless velar stop | ÞĒOD-CYNINGA |
| [y] | short close front rounded | ÞĒOD-CYNINGA |
| [ŋ] | voiced velar nasal | ÞĒOD-CYNINGA |
| [j] | palatal approximant | GEFRŪNON |
| [f] | voiceless labiodental fricative | GEFRŪNON |
| [uː] | long close back rounded | GEFRŪNON |
| [x] | voiceless velar fricative | HU |
| [ð] | voiced dental fricative | ÐĀ |
| [l] | voiced alveolar lateral | ÆÞELINGAS |
| [s] | voiceless alveolar fricative | ÆÞELINGAS |
| [lː] | geminate lateral | ELLEN |
| [oː] | long close-mid back rounded | GŌD |
| [ʃ] | voiceless postalveolar fricative | SCYLD |
| [v] | voiced labiodental fricative | SCEFING |
| [eɑ] | short front-back diphthong | SCEAÞENA |

**32 verified.**  
**Remaining gaps: [p], [b], [iː],**  
**[æː], [eːɑ], [eo], [eːo], [ɣ].**  
**8 phonemes remaining.**

---

*MONGUM [moŋɡum] verified.*  
*Zero new phonemes. Pure assembly holds.*  
*Next: MǢGÞUM [mæːɣθum] — line 6, word 2.*  
*NEW PHONEMES: [æː] long open front unrounded,*  
*[ɣ] voiced velar fricative.*
