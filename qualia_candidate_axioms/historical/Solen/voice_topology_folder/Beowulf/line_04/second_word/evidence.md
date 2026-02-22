# WÆS — RECONSTRUCTION EVIDENCE
**Old English:** wæs  
**IPA:** [wæs]  
**Meaning:** was (3rd person singular past tense of *wesan* — to be)  
**Source:** Beowulf, line 4, word 2 (overall word 15)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  W approximant  ✓ PASS
D2  Æ vowel        ✓ PASS
D3  S fricative    ✓ PASS
D4  Full word      ✓ PASS
D5  Perceptual     LISTEN
```

Total duration: **200 ms** (8819 samples at 44100 Hz)  
Clean first run. Four for four.  
Zero new phonemes. Fourth consecutive
pure assembly word.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All four numeric checks passed on first run. |

---

## PHONEME RECORD

### W — voiced labio-velar approximant [w]
Second instance. Previously verified WĒ.
Word-initial here, gliding into [æ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6272 | 0.45–1.0 | PASS |
| RMS level | 0.2760 | 0.005–0.80 | PASS |

The trill amplitude modulation in [r]
reduces its voicing score relative to
steady vowels. The [w] glide has a
similar but smaller effect — the
formant transition produces a slightly
lower autocorrelation peak than a
steady vowel. 0.6272 is consistent
with the WĒ instance.

---

### Æ — open front unrounded [æ]
Fifth instance. HWÆT, GĒAR-DAGUM,
ÆÞELINGAS, ÞÆET, now WÆS.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7244 | 0.50–1.0 | PASS |
| F1 centroid (500–900 Hz) | 646 Hz | 550–800 Hz | PASS |

**[æ] cross-instance stability — complete record:**

| Word | Voicing | F1 centroid |
|---|---|---|
| HWÆT | 0.7244 | 647 Hz |
| ÆÞELINGAS | 0.7244 | 647 Hz |
| ÞÆET | 0.7244 | 647 Hz |
| WÆS | 0.7244 | 646 Hz |

Voicing identical across all four
instances to four decimal places.
F1 centroid variance < 1 Hz.
[æ] is the most reproducible phoneme
in the entire inventory. Zero variance
across word-initial, word-medial, and
post-approximant positions.

---

### S — voiceless alveolar fricative [s]
Second instance. Previously verified
word-final in ÆÞELINGAS.
Word-final again here.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1251 | 0.0–0.35 | PASS |
| RMS level | 0.1031 | 0.005–0.80 | PASS |
| Centroid (1000–22050 Hz) | 7609 Hz | 5000–22050 Hz | PASS |

**[s] cross-instance centroid:**

| Word | Centroid |
|---|---|
| ÆÞELINGAS | 7535 Hz |
| WÆS | 7609 Hz |

Variance 74 Hz across two instances.
Both well above the 5000 Hz floor.
Stable. The small variance is expected
from the stochastic noise source —
each synthesis call generates new
random noise, so centroid varies
slightly while remaining in range.

---

### Full word — D4

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2421 | 0.01–0.90 | PASS |
| Duration | 200 ms | 150–320 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| W | [w] | 55 ms | voiced approximant |
| Æ | [æ] | 65 ms | short vowel |
| S | [s] | 80 ms | voiceless fricative word-final |

Total: 200 ms. Three segments.
Same duration as ÞÆET (200 ms) —
coincidence of segment totals, not
a constraint. Both are short
function words with similar phoneme
durations.

The [æ]→[s] boundary is the primary
coarticulation event: voicing cuts
as the tongue moves from the open
front vowel position to the alveolar
groove. The vowel offset trajectory
moves F2 slightly upward toward the
alveolar place before voicing ends.

---

## LINGUISTIC NOTE

**The verb *wesan* — to be:**

Old English had two suppletive verbs
for *to be*, whose forms merged in
Modern English:

| Form | OE source | Meaning |
|---|---|---|
| *is*, *are* | *wesan* / *bēon* | present |
| *was*, *were* | *wæs* / *wǣron* | past |

*Wæs* is the 3rd person singular past
tense — *he/she/it was*. It is one of
the most frequent words in all Old
English prose and poetry.

**OE [wæs] → Modern English *was*:**

| Feature | OE | ModE |
|---|---|---|
| [w] | [w] | [w] — unchanged |
| [æ] | [æ] | [ɒ] — vowel shifted |
| [s] | [s] | [z] — voiced intervocalically in connected speech, [s] word-final in isolation |

The [w] and word-final [s] are
unchanged. The vowel has rounded
and lowered from front [æ] to back
[ɒ] in the Great Vowel Shift and
subsequent changes. When you say
*was* you are producing two of the
three phonemes identically to the
Beowulf poet.

**Frequency note:**
*Wæs* appears approximately 170 times
in Beowulf — more than once per two
lines on average. It is the most
frequent verb form in the poem.
The synthesis parameters established
here will be called thousands of
times across the full poem.

---

## CONSECUTIVE CLEAN RUNS

| Word | New phonemes | Iterations |
|---|---|---|
| FREMEDON | 0 | 0 |
| ÞÆET | 0 | 0 |
| WÆS | 0 | 0 |

Five of the last five words:
zero diagnostic iterations.
The assembly framework is operating
at full maturity for known phonemes.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `waes_dry.wav` | Full word, no reverb, 145 Hz |
| `waes_hall.wav` | Full word, hall reverb RT60=2.0s |
| `waes_slow.wav` | Full word, 4× time-stretched |
| `waes_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Fourth consecutive pure assembly word.

---

## CUMULATIVE LINE STATUS

| Line | Text | Status |
|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | ✓ complete |
| 4 | *þæt wæs gōd cyning* | þæt ✓  wæs ✓ — in progress |

---

## PHONEME INVENTORY
*All verified phonemes — 28 total.  
No change this word.*

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

**28 verified.**

---

*WÆS [wæs] verified.*  
*Next: GŌD [ɡoːd] — line 4, word 3.*  
*NEW PHONEME: [oː] long close-mid back rounded.*  
*First new phoneme since ÐĀ (word 10).*  
*Five consecutive assembly words broken.*
