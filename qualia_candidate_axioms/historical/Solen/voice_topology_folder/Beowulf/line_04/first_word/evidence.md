# ÞÆT — RECONSTRUCTION EVIDENCE
**Old English:** þæt  
**IPA:** [θæt]  
**Meaning:** that (demonstrative pronoun / conjunction)  
**Source:** Beowulf, line 4, word 1 (overall word 14)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  Þ fricative    ✓ PASS
D2  Æ vowel        ✓ PASS
D3  T stop final   ✓ PASS
D4  Full word      ✓ PASS
D5  Perceptual     LISTEN
```

Total duration: **200 ms** (8819 samples at 44100 Hz)  
Clean first run. Four for four.  
Zero new phonemes. Third pure assembly
word in a row.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All four numeric checks passed on first run. |

---

## PHONEME RECORD

### Þ — voiceless dental fricative [θ]
Fifth instance. ÞĒOD-CYNINGA (×2),
ÞRYM, ÆÞELINGAS, now ÞÆET.
Fully stable across all instances.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1690 | 0.0–0.35 | PASS |
| Centroid (400–8000 Hz) | 4325 Hz | 3500–6000 Hz | PASS |

**[θ] cross-instance centroid record:**

| Word | Centroid |
|---|---|
| ÞĒOD-CYNINGA | ~4200 Hz |
| ÞRYM | ~4200 Hz |
| ÆÞELINGAS | 4344 Hz |
| ÞÆET | 4325 Hz |

Stable across all instances.
Range 4200–4344 Hz. All well within
target 3500–6000 Hz.

---

### Æ — open front unrounded [æ]
Fourth instance. HWÆT, GĒAR-DAGUM,
ÆÞELINGAS, now ÞÆET.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7244 | 0.50–1.0 | PASS |
| F1 centroid (500–900 Hz) | 647 Hz | 550–800 Hz | PASS |

Voicing and F1 centroid identical to
HWÆT and ÆÞELINGAS instances (0.7244,
647 Hz). The [æ] phoneme is the most
consistent vowel in the inventory —
zero variance across four instances
in different phonological environments.

---

### T — voiceless alveolar stop [t] word-final
Second instance of [t]. Previously
verified word-initial in HWÆT.
Here word-final — different phonological
position, same phoneme.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.0000 | 0.0–0.35 | PASS |
| RMS level | 0.0465 | 0.005–0.70 | PASS |
| Duration | 65 ms | 40–100 ms | PASS |

**Voicing 0.0000 — perfect.**
The closure is completely silent.
No voicing bleed from the preceding
vowel measurable in the autocorrelation
window. The stop is clean.

**Word-final [t] vs word-initial [t]:**

In Old English, as in most languages,
word-final stops are not aspirated.
Aspiration (the brief period of
voiceless airflow after burst release)
occurs primarily in word-initial
position before stressed vowels.

| Position | Aspiration | VOT |
|---|---|---|
| Word-initial [t] (HWÆT) | yes | ~15 ms voicing ramp |
| Word-final [t] (ÞÆET) | no | none |

The synthesis reflects this:
synth_T_final() has T_ASPIR_MS = 0
and no VOT voicing ramp after burst.
The burst decays immediately to silence.

**The [t] in Modern English *that*:**
Modern English *that* [ðæt] has the
same word-final unaspirated [t].
The pronunciation of the final
consonant has not changed in 1300
years. The [θ] word-initial has
shifted to [ð] in the Modern English
function word — but the [t] is
identical. When you say *that* you
are producing the same final stop
that the Beowulf poet produced.

---

### Full word — D4

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1914 | 0.01–0.90 | PASS |
| Duration | 200 ms | 150–350 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| Þ | [θ] | 70 ms | voiceless fricative |
| Æ | [æ] | 65 ms | short vowel |
| T | [t] | 65 ms | voiceless stop word-final |

Three segments. 200 ms total.
The shortest word reconstructed so far
by segment count. One fricative,
one vowel, one stop.
The word is symmetric in duration —
all three segments within 5 ms of
each other.

---

## HISTORICAL AND LINGUISTIC NOTE

**The word *þæt* in Old English:**

*Þæt* is one of the highest-frequency
words in Old English. It appears
hundreds of times in Beowulf alone.
It functions as:
- Demonstrative pronoun: *þæt* (that thing)
- Definite article neuter: *þæt* (the)
- Subordinating conjunction: *þæt* (that,
  so that, because)
- Result clause marker: *þæt wæs...* (that was...)

In line 4 of Beowulf it opens the
result clause: *þæt wæs gōd cyning* —
*that was a good king*. This is the
poem's first explicit evaluative
judgment. Everything in lines 1–3
has been description and subordinate
clause. Line 4 delivers the verdict.

**OE *þæt* → Modern English *that*:**

The word is directly ancestral to
Modern English *that*. The sound
changes:
- OE [θ] word-initial → ME [ð]
  in grammatical function words
  (the th-voicing of function words)
- OE [æ] → ME [a] → ModE [æ] or [ə]
  (vowel reduction in unstressed position)
- OE [t] word-final → unchanged

The word has been in continuous use
for over 1300 years with minimal
structural change. It is one of
the most durable words in the
English language.

---

## CONSECUTIVE CLEAN RUNS — NOTE

FREMEDON, ÞÆET: two consecutive words
with zero diagnostic iterations.
Combined with ÆÞELINGAS and ELLEN
(also first-run passes), four of the
last five words have passed on the
first attempt.

The calibration curve is clear:
- Words 1–5: multiple iterations
  per word as framework established
- Words 6–10: 1–2 iterations typical
- Words 11–14: zero iterations typical

The framework is fully mature.
Remaining inventory words (line 4
continuation) are expected to follow
the same zero-iteration pattern unless
a genuinely new synthesis challenge
appears — which will be the diphthong
[eo] when it first occurs.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `thaet_dry.wav` | Full word, no reverb, 145 Hz |
| `thaet_hall.wav` | Full word, hall reverb RT60=2.0s |
| `thaet_slow.wav` | Full word, 4× time-stretched |
| `thaet_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Third consecutive pure assembly word.

---

## CUMULATIVE LINE STATUS

| Line | Text | Status |
|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | ✓ complete |
| 4 | *þæt wæs gōd cyning* | þæt ✓ — in progress |

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

**28 verified. Inventory incomplete.**  
**Remaining gaps: [p], [b], [oː], [iː],**  
**[æː], [eo], [eːo], [ɣ].**

---

*ÞÆET [θæt] verified.*  
*Next: WÆS [wæs] — line 4, word 2.*  
*Zero new phonemes expected.*
