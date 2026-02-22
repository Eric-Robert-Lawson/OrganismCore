# SCEAÞENA — RECONSTRUCTION EVIDENCE
**Old English:** sceaþena  
**IPA:** [ʃeɑθenɑ]  
**Meaning:** of enemies (genitive plural)  
**Source:** Beowulf, line 5, word 3 (overall word 20)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  SH fricative      ✓ PASS
D2  EA diphthong      ✓ PASS
D3  TH fricative      ✓ PASS
D4  E vowel           ✓ PASS
D5  N nasal           ✓ PASS
D6  A vowel           ✓ PASS
D7  EA F2 movement    ✓ PASS
D8  Full word         ✓ PASS
D9  Perceptual        LISTEN
```

Total duration: **410 ms** (18079 samples at 44100 Hz)  
Clean first run. Eight for eight.  
One new phoneme: [eɑ].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All eight numeric checks passed on first run. |

---

## PHONEME RECORD

### SH — voiceless postalveolar fricative [ʃ]
Third instance. SCYLD, SCEFING, SCEAÞENA.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1301 | 0.0–0.35 | PASS |
| Centroid (1000–10000 Hz) | 4525 Hz | 2500–5500 Hz | PASS |

**[ʃ] cross-instance centroid stability:**

| Word | Centroid |
|---|---|
| SCYLD | 4756 Hz |
| SCEFING | 4666 Hz |
| SCEAÞENA | 4525 Hz |

Range: 231 Hz across three instances.
Stochastic variation in noise source.
All well within 2500–5500 Hz target.
Parameter set is stable.

---

### EA — short front-back diphthong [eɑ]
**New phoneme. 32nd verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7588 | 0.50–1.0 | PASS |
| RMS level | 0.2307 | 0.01–0.90 | PASS |

**D7 — F2 movement trajectory:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F2 onset | 1851 Hz | 1500–2200 Hz | PASS |
| F2 offset | 1131 Hz | 800–1500 Hz | PASS |
| F2 delta | 720 Hz ↓ | 400–1200 Hz | PASS |

**The trajectory:**

```
F2: 1851 Hz ──────────────► 1131 Hz
               720 Hz fall
    [e] quality           [ɑ] quality
    front                 back
```

The 720 Hz F2 fall is the acoustic
signature of the [eɑ] diphthong.
It is unambiguous and large — nearly
an octave of movement across 80 ms.
No static vowel in the inventory
produces this trajectory.

**[eɑ] synthesis approach:**

Time-varying formant filter with
per-sample frequency interpolation.
Transition begins at 30% of duration,
completes at 90%. The early steady
portion establishes the [e] onset
clearly before the glide begins.
The late steady portion gives the
[ɑ] offset time to stabilise before
the next consonant.

```
0%    30%              90%  100%
|--[e]--|--glide [e→ɑ]--|--[ɑ]--|
F2: 1900        ↓↓↓        1100
F1:  450        ↑↑↑         700
```

Both F1 and F2 move simultaneously —
F2 falls (front→back movement) and
F1 rises (close→open movement).
This is the correct formant pattern
for a falling diphthong toward [ɑ].

**[eɑ] vs [e] vs [ɑ] — distinction:**

| Sound | F2 onset | F2 offset | Movement |
|---|---|---|---|
| [e] static | ~1875 Hz | ~1875 Hz | none |
| [ɑ] static | ~1084 Hz | ~1084 Hz | none |
| [eɑ] diphthong | ~1851 Hz | ~1131 Hz | 720 Hz ↓ |

The diphthong is not a sequence of
two separate vowels. It is a single
continuous movement. The intermediate
states — all the formant values
between onset and offset — are part
of the phoneme. A listener hears
motion, not two discrete sounds.

**[eɑ] frequency in Old English:**

The *ea* diphthong is one of the most
common vowel sequences in OE. It
appears in:

| OE word | IPA | Modern English |
|---|---|---|
| *eald* | [eɑld] | old |
| *earm* | [eɑrm] | arm |
| *heard* | [heɑrd] | hard |
| *bearn* | [beɑrn] | bairn / barn |
| *feall* | [feɑll] | fall |
| *weald* | [weɑld] | wold / weald |
| *dream* | [dreɑm] | dream |
| *eage* | [eɑɣe] | eye |
| *beadu* | [beɑdu] | battle |

Every one of these uses the [eɑ]
parameters verified here. The
diphthong covers a significant portion
of the core OE vocabulary.

**Modern English reflexes:**

OE [eɑ] had multiple outcomes in
Middle and Modern English depending
on environment:
- Before *ld*: [eɑ] → [oː] → ModE [əʊ]
  (*eald* → *old*)
- Before *r*: [eɑ] → [ɑː] → ModE [ɑː]
  (*earm* → *arm*)
- Before *rd*: [eɑ] → [ɑː] → ModE [ɑː]
  (*heard* → *hard*)
- Word-finally: various outcomes

The diphthong was always falling —
energy front-loaded, glide toward
back — but its fate in subsequent
centuries depended on the following
consonant environment.

---

### TH — voiceless dental fricative [θ]
Sixth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1561 | 0.0–0.35 | PASS |
| RMS level | 0.0871 | 0.001–0.50 | PASS |

Post-diphthong position here —
following [ɑ] offset of [eɑ].
The [θ] onset follows the voiced
glide smoothly. No coarticulation
issues — voiceless fricative after
voiced vowel is a clean transition.

---

### E — short close-mid front [e]
Sixth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | 0.50–1.0 | PASS |
| F2 centroid (1500–2500 Hz) | 1875 Hz | 1600–2300 Hz | PASS |

---

### N — voiced alveolar nasal [n]
Twelfth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7748 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2454 | 0.005–0.25 | PASS |

---

### A — short open back [ɑ]
Word-final here. Seventh instance.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6679 | 0.50–1.0 | PASS |
| F2 centroid (800–1500 Hz) | 1084 Hz | 900–1400 Hz | PASS |

F2 1084 Hz — consistent with all
previous [ɑ] instances (~1084 Hz).
The back vowel is extremely stable
across the inventory.

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2270 | 0.01–0.90 | PASS |
| Duration | 410 ms | 380–650 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| SC | [ʃ] | 80 ms | voiceless postalveolar fricative |
| EA | [eɑ] | 80 ms | short front-back diphthong |
| Þ | [θ] | 75 ms | voiceless dental fricative |
| E | [e] | 55 ms | short close-mid front vowel |
| N | [n] | 65 ms | voiced alveolar nasal |
| A | [ɑ] | 55 ms | short open back vowel |

Total: 410 ms. Six segments.
The [eɑ] diphthong at 80 ms is
the longest segment — equal to
the [ʃ] onset. The word is
vowel-heavy by OE standards:
3 of 6 segments are vowels
(including the diphthong).

---

## MORPHOLOGICAL NOTE

**sceaþena — genitive plural:**

*sceaþa* (enemy, harmer, injurer)
is a masculine a-stem noun.
Genitive plural ending: *-ena*.
Full form: *sceaþena* — of enemies.

The word *sceaþa* is related to:
- ModE *scathe* (harm, injury) —
  archaic but surviving
- ModE *unscathed* (unharmed) —
  the negative form survives where
  the positive has been lost
- ModE *scathing* (harshly critical)

The root *sceaþ-* means one who
injures, harms, destroys. In the
poem it refers to the enemies that
Scyld Scefing terrorised and subjugated.

**Line 5 context:**

```
Scyld Scefing    sceaþena þreatum
Scyld Scefing    [from] enemies' troops
```

The line describes Scyld's power —
he terrorised enemy troops, took
their mead-hall benches (*meodosetla
ofteah*, line 6). The genitive
*sceaþena* modifies *þreatum* (troops,
bands) — troops belonging to enemies.

---

## DIPHTHONG INVENTORY STATUS

| Diphthong | IPA | Status |
|---|---|---|
| *ea* short | [eɑ] | ✓ verified — SCEAÞENA |
| *ēa* long | [eːɑ] | gap remaining |
| *eo* short | [eo] | gap remaining |
| *ēo* long | [eːo] | gap remaining |

Three diphthongs remain. [eɑ] is
the first verified. The long [eːɑ]
uses the same trajectory but with
doubled duration — parameters
carry over with dil adjustment.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `sceathena_dry.wav` | Full word, no reverb, 145 Hz |
| `sceathena_hall.wav` | Full word, hall reverb RT60=2.0s |
| `sceathena_slow.wav` | Full word, 4× time-stretched |
| `sceathena_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `sceathena_ea_only.wav` | [eɑ] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameter | Iterations |
|---|---|---|---|
| [eɑ] | short front-back diphthong | F2 delta 720 Hz falling — onset 1851 Hz, offset 1131 Hz | 1 |

**32 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Status |
|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | ✓ complete |
| 4 | *þæt wæs gōd cyning* | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | Scyld ✓  Scefing ✓  Sceaþena ✓ — one word remaining |

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

*SCEAÞENA [ʃeɑθenɑ] verified.*  
*[eɑ] added. Diphthong inventory opened.*  
*Next: ÞREATUM [θreɑtum] — line 5, word 4.*  
*Zero new phonemes. Line 5 final word.*
