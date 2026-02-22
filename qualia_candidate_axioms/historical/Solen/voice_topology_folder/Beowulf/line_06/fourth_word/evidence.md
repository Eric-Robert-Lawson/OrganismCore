# OFTEAH — RECONSTRUCTION EVIDENCE
**Old English:** ofteah  
**IPA:** [ofteɑx]  
**Meaning:** deprived, took away (past tense 3rd singular of *oftēon*)  
**Source:** Beowulf, line 6, word 4 (overall word 25)  
**Line 6 final word.**  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  O vowel               ✓ PASS
D2  F fricative           ✓ PASS
D3  T stop                ✓ PASS
D4  EA diphthong          ✓ PASS
D5  EA F2 movement        ✓ PASS
D6  X fricative           ✓ PASS
D7  X/GH distinction      ✓ PASS
D8  Full word             ✓ PASS
D9  Perceptual            LISTEN
```

Total duration: **340 ms** (14993 samples at 44100 Hz)  
Clean first run. Eight for eight.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All eight numeric checks passed on first run. |

---

## PHONEME RECORD

### O — short close-mid back rounded [o]
Word-initial. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6691 | 0.50–1.0 | PASS |
| F2 centroid (550–1100 Hz) | 748 Hz | 600–1000 Hz | PASS |

---

### F — voiceless labiodental fricative [f]
Post-vowel position. [o]→[f].
Voiceless onset — vocal folds
stop vibrating at [o] offset.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1353 | 0.0–0.35 | PASS |
| RMS level | 0.1058 | 0.001–0.50 | PASS |

---

### T — voiceless alveolar stop [t]
Post-fricative. [f]→[t] cluster.
Both voiceless — no voicing change
across the cluster boundary.
The [ft] cluster is entirely
devoiced throughout.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.2311 | 0.0–0.35 | PASS |
| RMS level | 0.0977 | 0.005–0.80 | PASS |

Voicing 0.2311 — slightly elevated
relative to word-initial [t].
Aspiration following voiced
context carries some periodicity.
Still well within voiceless target.

---

### EA — short front-back diphthong [eɑ]
Third instance. Fully stable.
Post-stop position — [t]→[eɑ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7588 | 0.50–1.0 | PASS |
| RMS level | 0.2307 | 0.01–0.90 | PASS |

**D5 — F2 movement trajectory:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F2 onset | 1851 Hz | 1500–2200 Hz | PASS |
| F2 offset | 1131 Hz | 800–1500 Hz | PASS |
| F2 delta | 720 Hz ↓ | 400–1200 Hz | PASS |

**[eɑ] cross-instance stability —
all three instances:**

| Word | F2 onset | F2 offset | Delta |
|---|---|---|---|
| SCEAÞENA | 1851 Hz | 1131 Hz | 720 Hz |
| ÞREATUM | 1851 Hz | 1131 Hz | 720 Hz |
| OFTEAH | 1851 Hz | 1131 Hz | 720 Hz |

Identical across all three instances.
The diphthong trajectory is fully
deterministic and context-independent
in the core. The [eɑ] parameters
are stable across the inventory.

---

### X — voiceless velar fricative [x]
Word-final position. [eɑ]→[x].
Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1354 | 0.0–0.35 | PASS |
| Centroid (1000–8000 Hz) | 3377 Hz | 1500–5000 Hz | PASS |
| RMS level | 0.0945 | 0.001–0.50 | PASS |

**D7 — [x] vs [ɣ] distinction:**

| Phoneme | Voicing | Separation |
|---|---|---|
| [x] — OFTEAH | 0.1354 | — |
| [ɣ] — MǢGÞUM | 0.7607 | 0.6253 units |

Separation of 0.6253 voicing units.
The velar fricative pair remains
fully separated. The voiceless/voiced
distinction is unambiguous.

**[x] post-diphthong context:**

The [eɑ] offset is back [ɑ] —
F1 ~700 Hz, F2 ~1100 Hz. The tongue
body is already raised and retracted
toward the back of the oral cavity
at the end of the diphthong. The
transition from [ɑ] to [x] is
therefore acoustically natural —
the tongue moves from near-velar
vowel position to velar fricative
constriction with minimal displacement.
The [ɑx] sequence is one of the most
physically efficient transitions in
the OE inventory.

**[x] cross-instance comparison:**

| Word | Voicing | Centroid | Context |
|---|---|---|---|
| HU | ~0.10 | ~3000 Hz | word-initial |
| OFTEAH | 0.1354 | 3377 Hz | word-final post-diphthong |

Slightly different centroid values
reflect different noise realisations
(stochastic source) and different
coarticulation contexts. Both within
the 1500–5000 Hz target. Voicing
consistent across instances.

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2106 | 0.01–0.90 | PASS |
| Duration | 340 ms | 290–500 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| O | [o] | 55 ms | short close-mid back rounded |
| F | [f] | 70 ms | voiceless labiodental fricative |
| T | [t] | 60 ms | voiceless alveolar stop |
| EA | [eɑ] | 80 ms | short front-back diphthong |
| H | [x] | 75 ms | voiceless velar fricative |

Total: 340 ms. Five segments.
The word has an unusual voicing
profile: voiced — voiceless —
voiceless — voiced — voiceless.
The [ft] cluster creates a
continuous voiceless region of
130 ms at the centre of the word.
The word opens and closes on the
same voicing profile:
voiced [o] → voiceless fricative,
voiced [eɑ] → voiceless fricative.
Symmetric voicing architecture.

---

## ETYMOLOGICAL NOTE

**oftēon — to deprive:**

*of-* (away, from) + *tēon*
(to draw, pull, lead). A compound
verb meaning to draw away from,
to deprive, to withhold.

Past tense singular: *ofteah*.
The vowel change [eː]→[eɑ] is
a strong verb ablaut — the same
phenomenon that gives ModE
*draw/drew*, *drive/drove*.

**tēon → tow:**

OE *tēon* [teːon] — to draw, pull.
ModE *tow* — to pull a boat or
vehicle. The long [eː] of *tēon*
became ME [ou] became ModE [əʊ]
spelled *ow*. The past tense
*tēah* [teɑx] used the [eɑ]
diphthong verified in this word.

Other descendants of OE *tēon*:
- *tug* — from the same Germanic root
- *tow-path* — the path from which
  boats are towed
- *team* — originally a group of
  animals drawn (towed) together

**of- prefix:**

The prefix *of-* in OE corresponds
to ModE *of* and German *ab-*.
It conveys separation, removal,
taking away. *Ofteah* — drew away,
removed. The benches were drawn
out from under the enemy warriors.

---

## LINE 6 — COMPLETE

```
mongum mǣgþum    meodosetla ofteah
[moŋɡum mæːɣθum  meodosetlɑ ofteɑx]

[to] many tribes  mead-benches
                  deprived/took away
```

Full line: Scyld Scefing deprived
many tribes of their mead-benches.

**Line 6 statistics:**

| Word | Phonemes | New phonemes | Duration |
|---|---|---|---|
| mongum | 6 | 0 | 365 ms |
| mǣgþum | 6 | 2 ([æː], [ɣ]) | 430 ms |
| meodosetla | 9 | 1 ([eo]) | 550 ms |
| ofteah | 5 | 0 | 340 ms |

Total new phonemes in line 6: 3
Total duration line 6: ~1685 ms

---

## OUTPUT FILES

| File | Description |
|---|---|
| `ofteah_dry.wav` | Full word, no reverb, 145 Hz |
| `ofteah_hall.wav` | Full word, hall reverb RT60=2.0s |
| `ofteah_slow.wav` | Full word, 4× time-stretched |
| `ofteah_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**35 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | New phonemes | Status |
|---|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | 18 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | 6 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | 4 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | 2 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | 3 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | 3 | ✓ complete |

**6 lines complete. 25 words. 35 phonemes.**

---

## PHONEME INVENTORY
*All verified phonemes — 35 total:*

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
| [æː] | long open front unrounded | MǢGÞUM |
| [ɣ] | voiced velar fricative | MǢGÞUM |
| [eo] | short front-mid diphthong | MEODOSETLA |

**35 verified.**  
**Remaining gaps: [p], [b], [iː], [eːɑ], [eːo].**  
**5 phonemes remaining.**

---

*OFTEAH [ofteɑx] verified.*  
*Zero new phonemes. Line 6 complete.*  
*6 lines. 25 words. 35 phonemes.*  
*Next: LINE 7 — egsode eorlas, syþðan ǣrest wearð.*  
*NEW PHONEMES: [iː] [p] [b]. Three gaps closing.*
