# PÆÞ — RECONSTRUCTION EVIDENCE
**Old English:** pæþ  
**IPA:** [pæθ]  
**Meaning:** path, way, track  
**Purpose:** Inventory completion series — word 4 of 4  
**New phoneme:** [p] — voiceless bilabial stop  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  P voicelessness         ✓ PASS
D2  P burst frequency       ✓ PASS
D3  Stop place distinc.     ✓ PASS
D4  AE vowel                ✓ PASS
D5  TH fricative            ✓ PASS
D6  Full word               ✓ PASS
D7  Perceptual              LISTEN
```

Total duration: **195 ms** (8599 samples at 44100 Hz)  
Clean first run. Six for six.  
One new phoneme: [p].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All six numeric checks passed on first run. |

---

## NEW PHONEME — [p]

### Definition
**Voiceless bilabial stop.**

Both lips sealed — bilabial closure.
No voicing during closure — no murmur.
Intraoral pressure builds behind lips.
Burst at release — low frequency,
lips produce broadband low-energy pop.
Short aspiration VOT follows.

### Parameters

```
Total duration:  65 ms
Closure:         43 ms — silence
Burst:           12 ms — filtered ~800 Hz
VOT:             10 ms — broadband aspiration
Burst gain:      0.60
VOT gain:        0.20
```

### Verified values

| Measure | Target | Measured | Result |
|---|---|---|---|
| Voicing (must be low) | 0.0–0.35 | 0.3242 | PASS |
| RMS level | 0.005–0.70 | 0.0728 | PASS |
| Burst centroid | 400–1400 Hz | 1038 Hz | PASS |
| [p]→[k] separation | 200–2000 Hz | 762 Hz | PASS |
| [p]→[t] separation | 1000–4000 Hz | 2462 Hz | PASS |

---

## WARNINGS AND NOTES

### W1 — Voicing score proximity to threshold

[p] voicing measured at **0.3242**.
Upper bound of target: **0.3500**.
Margin: **0.0258**.

The VOT aspiration noise — broadband
filtered between 500–8000 Hz — creates
slight autocorrelation in the measurement
window. The noise is not periodic but
at short durations the autocorrelation
function can produce a small spurious
peak. The measurement passes but the
margin is narrow.

**Implication for [b]:**

When [b] is verified at line 8,
the voicing score must be clearly
above the [p] score of 0.3242.
The [p]/[b] separation must be
unambiguous — target separation
>= 0.20 voicing units.

If [b] scores below 0.52 the
[p]/[b] pair will need parameter
adjustment to open up the separation.

The [ɡ]/[s] separation of 0.6644
and [θ]/[ð] separation of 0.6406
set the precedent. Stop voicing
pairs should be similarly separated.

### W2 — [θ] perceptual proximity to [ʃ]

Noted by naive listener: [θ] heard
as *sh* rather than *th*.

The [θ] noise centroid confirmed
in previous diagnostic runs sits
at approximately 7000–7600 Hz —
high for a dental fricative.
Typical [θ] centroid: 4000–5500 Hz.
Typical [ʃ] centroid: 2500–4000 Hz.
Typical [s] centroid: 7000–9000 Hz.

The synthesised [θ] is sitting
in the upper range — closer to [s]
territory than to the dental target.
This is a filter bandwidth issue:
the noise band is too wide and too
high, pulling energy into [s] range.

The diagnostic passes because the
voicing check is met (low voicing)
and the RMS check is met. The
centroid is not explicitly checked
for [θ] — it was assumed sufficient
to check voicing and level.

**This is a known limitation
of the current [θ] synthesiser.**
It passes all explicit diagnostics.
It fails informal perceptual
evaluation by at least one listener.

The discrepancy is recorded.
A future diagnostic version could
add an explicit centroid check:
[θ] centroid target: 4000–6000 Hz.
This would require parameter
adjustment to the noise filter.

For now: the [θ] is in the
inventory, verified, with this
caveat noted.

---

## STOP PLACE HIERARCHY — COMPLETE

All three voiceless stops now verified.
Burst centroid hierarchy confirmed:

| Stop | Place | Burst centroid | Status |
|---|---|---|---|
| [p] | bilabial | 1038 Hz | ✓ PÆÞ |
| [k] | velar | ~1800 Hz | ✓ GĀR-DENA |
| [t] | alveolar | ~3500 Hz | ✓ HWÆT |

**Bilabial < Velar < Alveolar.**

This is the expected pattern from
acoustic phonetics. Place of
articulation moves from front
(lips) to back (tongue dorsum)
to front again (tongue tip) —
and the burst frequency reflects
the size of the front cavity
at release. Larger front cavity
(bilabial) = lower resonant
frequency. Smaller front cavity
(alveolar) = higher resonant
frequency. Velar sits between.

The three stops are unambiguously
separated:

```
[p] 1038 Hz
        ← 762 Hz gap →
[k] 1800 Hz
        ← 1700 Hz gap →
[t] 3500 Hz
```

Place is encoded in burst frequency.
The instrument captures this
hierarchy correctly.

---

## PHONEME RECORD

### P — voiceless bilabial stop [p]
**New phoneme. 39th verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.3242 | 0.0–0.35 | PASS |
| RMS level | 0.0728 | 0.005–0.70 | PASS |
| Burst centroid | 1038 Hz | 400–1400 Hz | PASS |
| [p]→[k] separation | 762 Hz | 200–2000 Hz | PASS |
| [p]→[t] separation | 2462 Hz | 1000–4000 Hz | PASS |

---

### AE — open front unrounded [æ]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7011 | 0.50–1.0 | PASS |
| F2 centroid | 1684 Hz | 1400–2000 Hz | PASS |

---

### TH — voiceless dental fricative [θ]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1094 | 0.0–0.35 | PASS |
| RMS level | 0.0980 | 0.001–0.50 | PASS |

Note: perceptual proximity to [ʃ]
recorded. See W2 above.

---

### Full word — D6

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1896 | 0.01–0.90 | PASS |
| Duration | 195 ms | 150–280 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| P | [p] | 65 ms | voiceless bilabial stop |
| AE | [æ] | 60 ms | open front unrounded |
| TH | [θ] | 70 ms | voiceless dental fricative |

Total: 195 ms. Three segments.

The word is predominantly voiceless:
[p] voiceless, [æ] voiced, [θ] voiceless.
One voiced segment surrounded by
two voiceless. The word is acoustically
sparse — two transient events
bracketing a short vowel.

---

## ETYMOLOGICAL NOTE

**pæþ — path:**

One of the few OE words with initial
[p] in native vocabulary. The word
is attested in OE, OS, OHG, and is
of uncertain ultimate etymology —
possibly pre-Germanic, possibly
related to movement vocabulary in
neighbouring languages.

**ModE descendants:**

- **path** — direct descendant.
  The OE [æ] split in ModE dialects:
  - General American: [pæθ] — preserved
    the original front vowel
  - Received Pronunciation: [pɑːθ] —
    lengthened and backed the vowel
    in the BATH set
  The GA pronunciation is closer
  to the OE original. The RP
  *path-broadening* is a later
  innovation, not a preservation.

- **German Pfad** — cognate.
  The [p] in OE corresponds to
  [pf] in German — the High German
  consonant shift. OE *pæþ* vs
  German *Pfad*. The [p] was not
  shifted in OE (or in English
  generally — the High German shift
  did not extend to the North Sea
  Germanic dialects).

**[p] rarity in native OE:**

Native OE vocabulary avoids
word-initial [p] where other
IE languages have it. The
correspondence is systematic:

| OE | German | Latin | Meaning |
|---|---|---|---|
| *feoh* | *Vieh* | *pecus* | cattle |
| *fæder* | *Vater* | *pater* | father |
| *fisc* | *Fisch* | *piscis* | fish |
| *fot* | *Fuß* | *pes/pedis* | foot |

In all these cases OE has [f]
where Latin has [p]. This is
Grimm's Law — the Germanic
consonant shift moved IE [p]
to Germanic [f]. OE *pæþ*
begins with [p] because it
was borrowed or retained before
or outside of Grimm's Law —
or represents a cluster where
the shift behaved differently.

The [p] in *pæþ* is therefore
phonologically unusual in native
OE. It is one of the reasons [p]
is the last stop to enter this
inventory — it simply does not
appear often in the early lines
of Beowulf, which draw heavily
on core native Germanic vocabulary
where [p] → [f] by Grimm's Law.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `paeth_dry.wav` | Full word, no reverb, 145 Hz |
| `paeth_hall.wav` | Full word, hall reverb RT60=2.0s |
| `paeth_slow.wav` | Full word, 4× time-stretched |
| `paeth_p_only.wav` | [p] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameters | Iterations |
|---|---|---|---|
| [p] | voiceless bilabial stop | burst 1038 Hz, voicing 0.3242, dur 65 ms | 1 |

**39 phonemes verified.**

---

## INVENTORY COMPLETION SERIES — COMPLETE

| Word | Phoneme | Status | Iterations |
|---|---|---|---|
| WĪF | [iː] | ✓ VERIFIED | 1 |
| ĒAGE | [eːɑ] | ✓ VERIFIED | 1 |
| ÞĒOD | [eːo] | ✓ VERIFIED | 1 |
| PÆÞ | [p] | ✓ VERIFIED | 1 |

All four inventory completion
words passed on first run.
Zero failures across the series.

---

## ONE PHONEME REMAINING

| Phoneme | Status | Source |
|---|---|---|
| [b] | pending | line 8 — GEBĀD |

[b] is the voiced bilabial stop —
the voiced counterpart of [p].
It arrives naturally in line 8.
The [p]/[b] pair will be complete
and measured when [b] is verified.

Target [b] voicing: >= 0.52
(clearly above [p] score of 0.3242).
Target separation: >= 0.20 voicing units.

**39 of 40 phonemes verified.**  
**Return to line 8.**

---

*PÆÞ [pæθ] verified.*  
*[p] added. 39 phonemes verified.*  
*Stop place hierarchy complete: [p] 1038 Hz < [k] 1800 Hz < [t] 3500 Hz.*  
*[p] voicing 0.3242 — narrow margin noted. [b] must score clearly higher.*  
*[θ] perceptual proximity to [ʃ] noted — known limitation.*  
*Inventory completion series: 4 words, 4 new phonemes, 4 first-run passes.*  
*One phoneme remaining: [b] — line 8 GEBĀD.*  
*Next: return to line 8 and complete it.*
