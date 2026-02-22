# ÞĒOD — RECONSTRUCTION EVIDENCE
**Old English:** þēod  
**IPA:** [θeːod]  
**Meaning:** people, nation, tribe  
**Purpose:** Inventory completion series — word 3 of 4  
**New phoneme:** [eːo] — long front-mid diphthong  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  EYO basic               ✓ PASS
D2  EYO duration            ✓ PASS
D3  EYO F2 movement         ✓ PASS
D4  EYO F1 stability        ✓ PASS
D5  EYO vs short EO         ✓ PASS
D6  EYO vs EYA F1           ✓ PASS
D7  TH fricative            ✓ PASS
D8  D stop                  ✓ PASS
D9  Full word               ✓ PASS
D10 Perceptual              LISTEN
```

Total duration: **280 ms** (12348 samples at 44100 Hz)  
Clean first run. Nine for nine.  
One new phoneme: [eːo].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All nine numeric checks passed on first run. |

---

## NEW PHONEME — [eːo]

### Definition
**Long front-mid diphthong.**

Long counterpart of short [eo].
Same trajectory. Double duration.
Onset: close-mid front [eː].
Offset: close-mid back rounded [o].
F1 stable throughout — jaw does not open.
F2 falls steeply — tongue retracts far.

### Parameters

```
Onset:  F1 450 Hz, F2 1900 Hz, F3 2600 Hz, F4 3300 Hz
Offset: F1 450 Hz, F2  800 Hz, F3 2400 Hz, F4 3000 Hz
Transition onset:  25% of duration
Transition offset: 85% of duration
Duration: 150 ms
```

### Verified values

| Measure | Target | Measured | Result |
|---|---|---|---|
| Voicing | 0.50–1.0 | 0.8955 | PASS |
| Duration | 120–180 ms | 150 ms | PASS |
| Long/short ratio | 1.5–2.5x | 2.00x | PASS |
| F2 onset | 1400–2200 Hz | 1851 Hz | PASS |
| F2 offset | 500–1100 Hz | 758 Hz | PASS |
| F2 delta | 800–1500 Hz | 1093 Hz ↓ | PASS |
| F1 onset | 300–600 Hz | 336 Hz | PASS |
| F1 delta (must be small) | 0–100 Hz | 1 Hz | PASS |

---

## THE FOUR-WAY DIPHTHONG MATRIX
*Now complete.*

```
         SHORT           LONG
F1 rises  [eɑ]  ✓       [eːɑ] ✓
F1 stable [eo]  ✓       [eːo] ✓
```

All four verified. The matrix is closed.

### Full measurement table

| Phoneme | Duration | F1 delta | F2 delta | Status |
|---|---|---|---|---|
| [eɑ] | 80 ms | 250 Hz ↑ | 720 Hz ↓ | ✓ SCEAÞENA |
| [eːɑ] | 150 ms | 281 Hz ↑ | 737 Hz ↓ | ✓ ĒAGE |
| [eo] | 75 ms | ~5 Hz stable | 1074 Hz ↓ | ✓ MEODOSETLA |
| [eːo] | 150 ms | 1 Hz stable | 1093 Hz ↓ | ✓ ÞĒOD |

### The two binary dimensions

**Dimension 1 — Quantity (duration):**

| | Short | Long |
|---|---|---|
| Duration | ~75–80 ms | ~150 ms |
| Ratio | 1.0x | ~1.9–2.0x |

**Dimension 2 — Quality (F1 trajectory):**

| | F1 rises (→ɑ) | F1 stable (→o) |
|---|---|---|
| F1 delta | 250–281 Hz | 1–5 Hz |
| Jaw | opens | stays |
| Target | open back | mid back |

Two binary features.
Four distinct phonemes.
The system is complete and measured.

### F2 delta comparison

| Phoneme | F2 delta | Steepness |
|---|---|---|
| [eɑ] | 720 Hz | — |
| [eːɑ] | 737 Hz | similar to short |
| [eo] | 1074 Hz | steeper — [o] more back |
| [eːo] | 1093 Hz | similar to short |

The F2 delta is consistent within
each quality pair — [eɑ]/[eːɑ]
both ~720–737 Hz, [eo]/[eːo] both
~1074–1093 Hz. Duration scaling
does not change the F2 trajectory
depth. The short and long versions
of each diphthong reach the same
formant targets — they just take
longer to get there.

---

## THE KEY DIAGNOSTIC — F1 STABILITY

D4 measured F1 delta = **1 Hz**.

This is the most precise measurement
in the entire inventory. The F1 onset
was 336 Hz and the F1 offset was
337 Hz — a difference of 1 Hz over
150 ms of speech. The jaw did not
move. The formant filter held the
F1 parameter constant throughout
the diphthong trajectory.

Separation from [eːɑ] F1 delta
(281 Hz): **280 Hz**.

This is unambiguous. The two long
diphthongs are distinguished by
280 Hz of F1 movement difference.
One moves. One does not.
The instrument captures this
distinction cleanly and without
any parameter tuning — the
difference is structural, built
into the EYO_F_ON and EYO_F_OFF
parameter sets where F1 on = F1 off.

---

## LONG VOWEL VOICING SCORES

The long vowels consistently score
the highest voicing values in the
inventory. The pattern is now clear:

| Phoneme | Voicing | Duration |
|---|---|---|
| [eːo] | 0.8955 | 150 ms |
| [eːɑ] | 0.8854 | 150 ms |
| [iː] | 0.8482 | 110 ms |
| [eɑ] | 0.7588 | 80 ms |
| [eo] | 0.7915 | 75 ms |
| [e] | 0.6695 | 55 ms |
| [o] | 0.6691 | 55 ms |

**Longer duration → higher voicing score.**

More pitch periods in the
autocorrelation window. More periods
means the periodic peak is sharper
relative to the noise floor. The
autocorrelation measure improves
with duration. Long vowels are not
more voiced than short vowels in
any phonological sense — but the
measurement is more accurate for
them because there is more signal
to measure.

This is an instrument property.
It is consistent and predictable.
It does not affect the validity
of the voicing distinctions —
all values remain above 0.50
for voiced segments.

---

## PHONEME RECORD

### EYO — long front-mid diphthong [eːo]
**New phoneme. 38th verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8955 | 0.50–1.0 | PASS |
| Duration | 150 ms | 120–180 ms | PASS |
| Long/short ratio | 2.00x | 1.5–2.5x | PASS |
| F2 onset | 1851 Hz | 1400–2200 Hz | PASS |
| F2 offset | 758 Hz | 500–1100 Hz | PASS |
| F2 delta | 1093 Hz ↓ | 800–1500 Hz | PASS |
| F1 onset | 336 Hz | 300–600 Hz | PASS |
| F1 delta | 1 Hz | 0–100 Hz | PASS |
| F1 separation vs [eːɑ] | 280 Hz | 150–400 Hz | PASS |

---

### TH — voiceless dental fricative [θ]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1438 | 0.0–0.35 | PASS |
| RMS level | 0.0769 | 0.001–0.50 | PASS |

---

### D — voiced alveolar stop [d]

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.0946 | 0.005–0.70 | PASS |
| Duration | 60 ms | 30–90 ms | PASS |

---

### Full word — D9

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2197 | 0.01–0.90 | PASS |
| Duration | 280 ms | 230–380 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| TH | [θ] | 70 ms | voiceless dental fricative |
| EYO | [eːo] | 150 ms | long front-mid diphthong |
| D | [d] | 60 ms | voiced alveolar stop |

Total: 280 ms. Three segments.

The [eːo] accounts for 54% of
the word duration. As in ĒAGE,
the long diphthong dominates.

---

## ETYMOLOGICAL NOTE

**þēod — people, nation:**

One of the most culturally significant
words in OE. *Þēod* is the word
for *the people* — the community
defined by shared language, law
and kinship. It appears in compounds
throughout OE literature:

- *þēod-cyning* — king of the people
  (line 2 of Beowulf — this exact word)
- *þēod-land* — homeland
- *þēod-scaða* — enemy of the people

**The Germanic family:**

| Language | Word | Meaning |
|---|---|---|
| OE | *þēod* | people, nation |
| OHG | *diot* | people |
| Gothic | *þiuda* | people |
| PGmc | *\*þeudō* | the people |

**ModE descendants:**

- **Dutch** — from MDu *Duits*,
  from OHG *diutisc* — of the people,
  vernacular. The English word *Dutch*
  originally meant *German* (the
  language of the *þēod*) and was
  narrowed to mean specifically
  the people of the Netherlands.

- **Deutsch** — the German
  self-designation. Same word,
  never narrowed. Still means
  simply *of the people*, vernacular,
  German.

- **Theodore** — from Greek
  *Theodoros* — but the first
  element *theo-* in Germanic
  names like *Theodoric* (*Þēodric*)
  is this same word — king of
  the people.

- **Teutonic** — from Latin
  *Teutonicus*, from PGmc *\*þeudō*.
  The academic/archaic term for
  Germanic.

The [eːo] in *þēod* is the OE
reflex of PGmc *\*eu* — the same
sound change that produced [eo]
in *þēod-cyninga* (line 2).
The long diphthong here is the
stressed, long-syllable version
of the same vowel. The quantity
distinction (short [eo] vs long
[eːo]) was phonemic in OE and
changed word meaning.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `theod_dry.wav` | Full word, no reverb, 145 Hz |
| `theod_hall.wav` | Full word, hall reverb RT60=2.0s |
| `theod_slow.wav` | Full word, 4× time-stretched |
| `theod_eyo_only.wav` | [eːo] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameters | Iterations |
|---|---|---|---|
| [eːo] | long front-mid diphthong | dur 150 ms, F1 delta 1 Hz stable, F2 delta 1093 Hz ↓ | 1 |

**38 phonemes verified.**

---

## INVENTORY COMPLETION STATUS

| Phoneme | Status | Word |
|---|---|---|
| [iː] | ✓ VERIFIED | WĪF |
| [eːɑ] | ✓ VERIFIED | ĒAGE |
| [eːo] | ✓ VERIFIED | ÞĒOD |
| [p] | pending | PÆÞ — next |
| [b] | pending | line 8 GEBĀD |

**2 phonemes remaining.**

---

## THE DIPHTHONG SYSTEM — COMPLETE

*All four diphthongs verified.  
All long/short pairs measured.  
The system is closed.*

```
         SHORT    LONG
→ [ɑ]    [eɑ] ✓  [eːɑ] ✓   F1 rises
→ [o]    [eo] ✓  [eːo] ✓   F1 stable
```

*F1 trajectory encodes quality.*  
*Duration encodes quantity.*  
*Four phonemes. Two dimensions. Complete.*

---

*ÞĒOD [θeːod] verified.*  
*[eːo] added. 38 phonemes verified.*  
*F1 delta 1 Hz — jaw does not move. Confirmed.*  
*Separation from [eːɑ]: 280 Hz. Unambiguous.*  
*Four-way diphthong matrix complete and closed.*  
*Next: PÆÞ [pæθ] — closes [p]. Inventory completion word 4 of 4.*
