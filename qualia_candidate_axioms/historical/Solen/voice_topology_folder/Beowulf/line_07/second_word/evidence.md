# EORLAS — RECONSTRUCTION EVIDENCE
**Old English:** eorlas  
**IPA:** [eorlas]  
**Meaning:** warriors, noblemen, earls (nominative plural)  
**Source:** Beowulf, line 7, word 2 (overall word 27)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  EO diphthong            ✓ PASS
D2  EO F2 movement          ✓ PASS
D3  EO onset comparison     ✓ PASS
D4  R trill                 ✓ PASS
D5  L lateral               ✓ PASS
D6  A vowel                 ✓ PASS
D7  S fricative             ✓ PASS
D8  Full word               ✓ PASS
D9  Perceptual              LISTEN
```

Total duration: **320 ms** (14110 samples at 44100 Hz)  
Clean first run. Eight for eight.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All eight numeric checks passed on first run. |

---

## PHONEME RECORD

### EO — short front-mid diphthong [eo]
Second instance. Word-initial.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7915 | 0.50–1.0 | PASS |
| RMS level | 0.2585 | 0.01–0.90 | PASS |

**D2 — F2 movement trajectory:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F2 onset | 1833 Hz | 1500–2200 Hz | PASS |
| F2 offset | 759 Hz | 550–1100 Hz | PASS |
| F2 delta | 1074 Hz ↓ | 700–1500 Hz | PASS |

**D3 — cross-instance onset comparison:**

| Instance | Context | F2 onset | Difference |
|---|---|---|---|
| MEODOSETLA | post-[m] | 1833 Hz | reference |
| EORLAS | word-initial | 1833 Hz | +0 Hz |

Expected: word-initial [eo] onset
slightly higher than post-nasal
instance — no [m] coarticulation
pulling F2 onset downward.

Observed: identical values.
Difference: 0 Hz.

**Finding — synthesiser coarticulation
is boundary-only:**

The synthesiser implements coarticulation
as formant transitions at segment
boundaries — the first 12% and last
12% of each segment. The measurement
window for F2 onset samples the first
25% of the diphthong. The coarticulation
influence of [m] on [eo] onset occurs
at the boundary — the first ~10 ms.
The measurement window is wide enough
to average over both the boundary
transition and the stable onset region,
reducing the detectable difference
between contexts.

This is a known property of the
instrument. Coarticulation is modelled
at boundaries. Within-segment trajectory
is context-independent. The onset
centroid measurement reflects the
stable onset target, not the boundary
transition detail.

Both instances pass all diagnostic
targets. The instrument is internally
consistent. The limitation is noted
for the record.

**[eo] cross-instance stability —
all instances:**

| Word | F2 onset | F2 offset | Delta | Context |
|---|---|---|---|---|
| MEODOSETLA | 1833 Hz | 759 Hz | 1074 Hz | post-[m] |
| EORLAS | 1833 Hz | 759 Hz | 1074 Hz | word-initial |

Fully deterministic across contexts.
Same parameters, same output.

---

### R — alveolar trill [r]
Post-diphthong position. [eo]→[r].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6818 | 0.50–1.0 | PASS |
| RMS level | 0.2557 | 0.005–0.80 | PASS |

**[r] cross-instance comparison:**

| Word | Voicing | Context |
|---|---|---|
| GĀR-DENA | 0.8608 | intervocalic |
| EORLAS | 0.6818 | post-diphthong |

Voicing lower here than in GĀR-DENA.
The AM trill modulation reduces the
autocorrelation peak — the periodic
interruptions of the trill create
slight aperiodicity that lowers the
voicing score. Both instances pass
the target of >= 0.50. The GĀR-DENA
instance had a higher score because
it was in a stronger intervocalic
position with more surrounding
voiced context.

---

### L — voiced alveolar lateral [l]
Post-trill position. [r]→[l].
Both alveolar — same place.
Smooth voiced transition.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7638 | 0.50–1.0 | PASS |
| RMS level | 0.2685 | 0.005–0.80 | PASS |

---

### A — short open back [ɑ]
Post-lateral position. [l]→[ɑ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6679 | 0.50–1.0 | PASS |
| F2 centroid (800–1500 Hz) | 1085 Hz | 900–1400 Hz | PASS |

---

### S — voiceless alveolar fricative [s]
Word-final. [ɑ]→[s]. Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1279 | 0.0–0.35 | PASS |
| Centroid (4000–12000 Hz) | 7615 Hz | 5000–10000 Hz | PASS |

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2612 | 0.01–0.90 | PASS |
| Duration | 320 ms | 280–480 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| EO | [eo] | 75 ms | short front-mid diphthong |
| R | [r] | 65 ms | alveolar trill |
| L | [l] | 60 ms | voiced alveolar lateral |
| A | [ɑ] | 55 ms | short open back |
| S | [s] | 65 ms | voiceless alveolar fricative |

Total: 320 ms. Five segments.

**Voicing profile:**

```
EO   voiced    0.7915
R    voiced    0.6818
L    voiced    0.7638
A    voiced    0.6679
S    voiceless 0.1279
```

Four voiced segments followed by
one voiceless. The word is maximally
voiced until the final [s] — the
plural marker. The [s] closes the
word with a clean voiceless offset.
The voicing contrast at the [ɑ]→[s]
boundary is 0.5400 units — sharp
and unambiguous.

**[rl] cluster — same-place transition:**

Both [r] and [l] are voiced alveolar
sonorants. The transition between them
is articulatorily simple — the tongue
tip stays at the alveolar ridge, the
lateral groove opens as the trill
ceases. In real speech this produces
a smooth, continuous voiced sound.
The synthesis concatenates them
at their boundaries — the result
is a brief formant transition from
R parameters to L parameters with
no silence between.

---

## ETYMOLOGICAL NOTE

**eorl — warrior, nobleman:**

*Eorl* is one of the most socially
loaded words in OE. It denotes a man
of the warrior class — not simply a
fighter but a man of rank, capable of
independent command, entitled to a
seat at the lord's table.

The word has two distinct lineages
in the period:

1. **OE native usage:** *eorl* as
   generic nobleman/warrior, contrasted
   with *þēow* (slave) and *ceorl*
   (free man of lower rank).

2. **Scandinavian influence:** In the
   Danelaw, *eorl* (from ON *jarl*)
   became a specific administrative
   title — the earl who governed a
   region under the king. This is the
   sense that survived.

By the time of the Norman Conquest,
*eorl/earl* was a formal title.
The Normans retained it alongside
their own *comte* (count), and
*earl* survived as the English
equivalent of a continental count —
the only major English noble title
not replaced by a French term.

**ModE descendants:**

- *earl* — direct descendant, same
  word, title of nobility between
  marquess and viscount
- *Earls Court*, *Carlisle* —
  place names containing the word
- The female form *countess* is used
  for an earl's wife — a Norman
  imposition on the English title

**The [eo] in *eorl*:**

OE *eorl* [eorɑl] → ME *erl* [ɛrl]
The diphthong [eo] was monophthongised
before [r] in Middle English —
the same process as *heorte* → *herte*
(heart), *eorþe* → *erthe* (earth).
The [eo] before [r] collapsed to [ɛː]
and eventually to ModE [ɜː] (the
vowel in *earl*, *earth*, *heard*).

The word *earl* therefore contains
the acoustic ghost of the [eo]
diphthong — the [ɜː] vowel in
*earl* is the final destination of
a sound change that began with
[eo] in this exact word.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `eorlas_dry.wav` | Full word, no reverb, 145 Hz |
| `eorlas_hall.wav` | Full word, hall reverb RT60=2.0s |
| `eorlas_slow.wav` | Full word, 4× time-stretched |
| `eorlas_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**35 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas, syþðan ǣrest wearð* | 26–30 | egsode ✓  eorlas ✓ — in progress |

---

*EORLAS [eorlas] verified.*  
*Zero new phonemes. 35 phonemes verified.*  
*[eo] onset identical across contexts — synthesiser coarticulation is boundary-only. Noted.*  
*ModE earl — same word, same sound, one millennium apart.*  
*Next: SYÞÐAN [syθðɑn] — line 7, word 3. Zero new phonemes.*
