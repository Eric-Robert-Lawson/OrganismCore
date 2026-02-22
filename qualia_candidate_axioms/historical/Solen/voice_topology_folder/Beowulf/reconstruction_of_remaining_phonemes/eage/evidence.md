# ĒAGE — RECONSTRUCTION EVIDENCE
**Old English:** ēage  
**IPA:** [eːɑɣe]  
**Meaning:** eye  
**Purpose:** Inventory completion series — word 2 of 4  
**New phoneme:** [eːɑ] — long front-back diphthong  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  EYA basic               ✓ PASS
D2  EYA duration            ✓ PASS
D3  EYA F2 movement         ✓ PASS
D4  EYA F1 movement         ✓ PASS
D5  EYA vs short EA         ✓ PASS
D6  EYA vs EYO contrast     ✓ PASS
D7  GH fricative            ✓ PASS
D8  E vowel final           ✓ PASS
D9  Full word               ✓ PASS
D10 Perceptual              LISTEN
```

Total duration: **270 ms** (11906 samples at 44100 Hz)  
Clean first run. Nine for nine.  
One new phoneme: [eːɑ].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All nine numeric checks passed on first run. |

---

## NEW PHONEME — [eːɑ]

### Definition
**Long front-back diphthong.**

Long counterpart of short [eɑ].
Same trajectory. Double duration.
Onset: close-mid front [eː].
Offset: open back [ɑ].
F1 rises — jaw opens throughout.
F2 falls — tongue retracts.

### Parameters

```
Onset:  F1 450 Hz, F2 1900 Hz, F3 2600 Hz, F4 3300 Hz
Offset: F1 700 Hz, F2 1100 Hz, F3 2400 Hz, F4 3000 Hz
Transition onset:  30% of duration
Transition offset: 90% of duration
Duration: 150 ms
```

### Verified values

| Measure | Target | Measured | Result |
|---|---|---|---|
| Voicing | 0.50–1.0 | 0.8854 | PASS |
| Duration | 120–180 ms | 150 ms | PASS |
| Long/short ratio | 1.5–2.5x | 1.88x | PASS |
| F2 onset | 1500–2200 Hz | 1851 Hz | PASS |
| F2 offset | 800–1400 Hz | 1115 Hz | PASS |
| F2 delta | 400–1000 Hz | 737 Hz ↓ | PASS |
| F1 onset | 300–600 Hz | 341 Hz | PASS |
| F1 delta | 100–400 Hz | 281 Hz ↑ | PASS |

---

## THE LONG/SHORT DIPHTHONG PAIRS
*Both now complete and measured.*

### [eɑ] / [eːɑ] — front-back pair

| Feature | [eɑ] short | [eːɑ] long |
|---|---|---|
| Duration | 80 ms | 150 ms |
| Ratio | 1.0x | 1.88x |
| F2 onset | 1851 Hz | 1851 Hz |
| F2 offset | 1131 Hz | 1115 Hz |
| F2 delta | 720 Hz ↓ | 737 Hz ↓ |
| F1 onset | ~450 Hz | 341 Hz |
| F1 delta | ~250 Hz ↑ | 281 Hz ↑ |

**Trajectory virtually identical.**
F2 onset 1851 Hz in both instances —
deterministic synthesis confirmed.
F2 offset slightly different
(1131 vs 1115 Hz) — within
measurement variance.
F1 delta comparable (250 vs 281 Hz).

**Duration is the primary distinction.**
1.88x ratio — clearly perceptible.
In OE phonology, the long/short
distinction was phonemic — it
changed meaning. *Ēare* (ear) vs
*earu* (ready) — duration alone
distinguishes pairs like these.

### [eo] / [eːo] — front-mid pair

| Feature | [eo] short | [eːo] long |
|---|---|---|
| Duration | 75 ms | pending — ÞĒOD |
| F2 delta | 1074 Hz ↓ | pending |
| F1 delta | 5 Hz stable | pending |

[eːo] is the next word in the
inventory completion series.
Based on the [eɑ]/[eːɑ] pattern,
[eːo] will have the same trajectory
as [eo] at approximately double
duration.

---

## THE FOUR-WAY DIPHTHONG DISTINCTION
*Status after this word:*

```
         SHORT          LONG
F1 rises  [eɑ] ✓       [eːɑ] ✓
F1 stable [eo] ✓       [eːo] pending
```

Three of four verified.
The fourth — [eːo] — follows next.

**The acoustic matrix:**

| | F1 rises (→ɑ) | F1 stable (→o) |
|---|---|---|
| Short | [eɑ]: delta 250 Hz | [eo]: delta 5 Hz |
| Long | [eːɑ]: delta 281 Hz | [eːo]: ~5 Hz predicted |

F1 trajectory encodes the quality
distinction (eɑ vs eo).
Duration encodes the quantity
distinction (short vs long).
Two independent dimensions.
Four distinct phonemes from
two binary features.

---

## PHONEME RECORD

### EYA — long front-back diphthong [eːɑ]
**New phoneme. 37th verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8854 | 0.50–1.0 | PASS |
| Duration | 150 ms | 120–180 ms | PASS |
| Long/short ratio | 1.88x | 1.5–2.5x | PASS |
| F2 onset | 1851 Hz | 1500–2200 Hz | PASS |
| F2 offset | 1115 Hz | 800–1400 Hz | PASS |
| F2 delta | 737 Hz ↓ | 400–1000 Hz | PASS |
| F1 onset | 341 Hz | 300–600 Hz | PASS |
| F1 delta | 281 Hz ↑ | 100–400 Hz | PASS |

Voicing 0.8854 — highest voicing
score in the entire inventory.
Long duration means more periods
sampled in the autocorrelation
window — the periodicity measure
is more accurate for long vowels
and diphthongs. The long phonemes
consistently score higher than
their short counterparts.

---

### GH — voiced velar fricative [ɣ]
Intervocalic position. [eːɑ]→[ɣ]→[e].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7230 | 0.50–1.0 | PASS |
| RMS level | 0.2548 | 0.005–0.80 | PASS |

[ɣ] voicing 0.7230 here vs 0.7607
in MǢGÞUM. Slight variation —
different coarticulation context.
Intervocalic [ɣ] between [ɑ] and
[e] vs post-nasal [ɣ] in MǢGÞUM.
Both within target. The voiced
velar fricative is stable across
contexts.

---

### E ��� short close-mid front [e]
Word-final. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | 0.50–1.0 | PASS |
| F2 centroid | 1876 Hz | 1600–2300 Hz | PASS |

---

### Full word — D9

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2749 | 0.01–0.90 | PASS |
| Duration | 270 ms | 220–360 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| EYA | [eːɑ] | 150 ms | long front-back diphthong |
| GH | [ɣ] | 65 ms | voiced velar fricative |
| E | [e] | 55 ms | short close-mid front |

Total: 270 ms. Three segments.

The [eːɑ] accounts for 56% of
the word duration. The long
diphthong dominates completely.
This is phonologically correct —
*ēage* is a long-vowel word and
its length is its most prominent
acoustic feature.

---

## ETYMOLOGICAL NOTE

**ēage — eye:**

Direct ancestor of ModE *eye*.
One of the most stable words
in the Indo-European languages —
cognates in virtually every
branch: Latin *oculus*, Greek
*ὄμμα*, Sanskrit *akṣi*,
German *Auge*, Dutch *oog*,
Norse *auga*.

**Sound change chain:**

```
OE  ēage   [eːɑɣe]
ME  ēye    [eːje]     — [ɣ] → [j] intervocalic
ME  eye    [eːe]      — [j] lost
ME  eye    [ɛːe]      — vowel lowering
ModE eye   [aɪ]       — Great Vowel Shift
```

The [ɣ] between the two vowels
weakened to [j] in Middle English
then was lost entirely, leaving
the two vowel sounds in hiatus.
The long [eːɑ] monophthongised
then underwent the Great Vowel
Shift: [eː] → [ɛː] → [æː] → [aɪ].

The OE word [eːɑɣe] and ModE
*eye* [aɪ] share only the
consonant-zero correspondence
where [ɣ] once stood. The vowel
quality has been completely
transformed. The word is
recognisable only through
the written record and
comparative reconstruction.

**The [eːɑ] in the Germanic
eye-word family:**

| Language | Word | Vowel |
|---|---|---|
| OE | *ēage* | [eːɑ] |
| OHG | *ouga* | [ou] |
| Gothic | *augō* | [au] |
| ON | *auga* | [au] |

The OE [eːɑ] corresponds to
[au] in the other Germanic
languages. This is a regular
OE sound change: PGmc *[au]*
→ OE *[eːɑ]* — the *ea*-
diphthong is the OE reflex of
Proto-Germanic *au* in most
environments. The [eːɑ] verified
here is the OE endpoint of
a vowel that started as [au]
in Proto-Germanic.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `eage_dry.wav` | Full word, no reverb, 145 Hz |
| `eage_hall.wav` | Full word, hall reverb RT60=2.0s |
| `eage_slow.wav` | Full word, 4× time-stretched |
| `eage_eya_only.wav` | [eːɑ] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameters | Iterations |
|---|---|---|---|
| [eːɑ] | long front-back diphthong | dur 150 ms, F1 delta 281 Hz ↑, F2 delta 737 Hz ↓ | 1 |

**37 phonemes verified.**

---

## INVENTORY COMPLETION STATUS

| Phoneme | Status | Word |
|---|---|---|
| [iː] | ✓ VERIFIED | WĪF |
| [eːɑ] | ✓ VERIFIED | ĒAGE |
| [eːo] | pending | ÞĒOD — next |
| [p] | pending | PÆÞ |
| [b] | pending | line 8 GEBĀD |

**3 phonemes remaining.**

---

*ĒAGE [eːɑɣe] verified.*  
*[eːɑ] added. 37 phonemes verified.*  
*Long/short [eɑ]/[eːɑ] pair complete. Ratio 1.88x.*  
*F1 delta 281 Hz rising — jaw opens — confirmed distinct from [eːo].*  
*PGmc [au] → OE [eːɑ] — the diphthong is a Proto-Germanic vowel preserved.*  
*Next: ÞĒOD [θeːod] — closes [eːo]. Inventory completion word 3 of 4.*

