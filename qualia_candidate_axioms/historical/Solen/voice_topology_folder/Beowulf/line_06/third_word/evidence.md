# MEODOSETLA — RECONSTRUCTION EVIDENCE
**Old English:** meodosetla  
**IPA:** [meodosetlɑ]  
**Meaning:** mead-benches (genitive plural)  
**Source:** Beowulf, line 6, word 3 (overall word 24)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1   M nasal              ✓ PASS
D2   EO diphthong         ✓ PASS
D3   EO F2 movement       ✓ PASS
D4   EO/EA distinction    ✓ PASS
D5   D stop               ✓ PASS
D6   O vowel              ✓ PASS
D7   S fricative          ✓ PASS
D8   E vowel              ✓ PASS
D9   T stop               ✓ PASS
D10  L lateral            ✓ PASS
D11  A vowel              ✓ PASS
D12  Full word            ✓ PASS
D13  Perceptual           LISTEN
```

Total duration: **550 ms** (24252 samples at 44100 Hz)  
Clean first run. Twelve for twelve.  
One new phoneme: [eo].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All twelve numeric checks passed on first run. |

---

## PHONEME RECORD

### M — voiced bilabial nasal [m]
Word-initial. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

---

### EO — short front-mid diphthong [eo]
**New phoneme. 35th verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7915 | 0.50–1.0 | PASS |
| RMS level | 0.2585 | 0.01–0.90 | PASS |

**D3 — F2 movement trajectory:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F2 onset | 1833 Hz | 1500–2200 Hz | PASS |
| F2 offset | 759 Hz | 550–1100 Hz | PASS |
| F2 delta | 1074 Hz ↓ | 700–1500 Hz | PASS |

**D4 — [eo] vs [eɑ] distinction:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F1 onset | 347 Hz | 300–600 Hz | PASS |
| F1 delta (stability) | 5 Hz | 0–150 Hz | PASS |

**The F1 trajectory — key distinction:**

```
[eo]:
  F1: 347 Hz ────────────── 342 Hz
       delta 5 Hz — STABLE
  F2: 1833 Hz ──────────► 759 Hz
       delta 1074 Hz — large fall

[eɑ]:  (verified SCEAÞENA)
  F1: ~450 Hz ──────────► ~700 Hz
       delta ~250 Hz — RISING
  F2: 1851 Hz ──────────► 1131 Hz
       delta 720 Hz — moderate fall
```

The two diphthongs are distinguished
primarily by the F1 trajectory:

- [eo]: F1 stays low and stable.
  Height maintained throughout.
  The tongue stays at mid height.
  Only backness and rounding change.

- [eɑ]: F1 rises significantly.
  The jaw opens toward [ɑ].
  The tongue lowers and retracts.
  Both height and backness change.

The F2 fall is larger in [eo] than
in [eɑ] — 1074 Hz vs 720 Hz — because
[o] is further back in F2 terms
(~800 Hz) than [ɑ] (~1100 Hz).

**[eo] synthesis approach:**

Same time-varying formant filter
architecture as [eɑ]. Transition
begins at 25% of duration, completes
at 85%. The critical parameter
difference: F1 onset and F1 offset
are both set to 450 Hz — the height
does not change. Only F2 (and higher
formants) move. This encodes the
phonemic distinction mechanically —
the synthesiser cannot confuse [eo]
with [eɑ] because F1 is fixed.

**[eo] cross-instance trajectory:**

First instance here. Parameters:

```
Onset:  F1 450, F2 1900, F3 2600, F4 3300
Offset: F1 450, F2  800, F3 2400, F4 3000
Measured onset:  F2 1833 Hz (target 1900)
Measured offset: F2  759 Hz (target 800)
```

Small deviation from target —
coarticulation with preceding [m]
pulls F2 onset slightly lower.
Both values within diagnostic targets.

**[eo] frequency in Old English:**

The *eo* diphthong is one of the
most common vowel sequences in OE.
It appears in the core vocabulary:

| OE word | IPA | Modern English |
|---|---|---|
| *weorld* | [weorldɑ] | world |
| *heorte* | [heorte] | heart |
| *feoh* | [feox] | cattle, money, fee |
| *beorn* | [beorn] | warrior, man |
| *eorþe* | [eorθe] | earth |
| *leod* | [leod] | people, nation |
| *deorc* | [deork] | dark |
| *feond* | [feond] | enemy, fiend |
| *meodu* | [meodu] | mead |
| *seolfor* | [seolfor] | silver |
| *þeod* | [θeod] | people, nation |

*Þēod* appears in line 2 of Beowulf
itself — *Þēod-cyninga* (of
nation-kings). That instance used
the long [eːo] — not yet verified.
The short [eo] verified here applies
to all the words in the list above.

**Modern English reflexes of [eo]:**

OE [eo] had variable outcomes in ME:

| OE | ME | ModE | Environment |
|---|---|---|---|
| *heorte* | *herte* | *heart* | before r |
| *eorþe* | *erthe* | *earth* | before r |
| *feond* | *feend* | *fiend* | before nd |
| *deorc* | *derk* | *dark* | before r |
| *weorld* | *world* | *world* | before rl |

The [eo] diphthong was generally
monophthongised in Middle English.
Before *r*, it merged with [e] → [ɛː]
and then developed further. The
modern words retain no trace of
the diphthong — only the consonant
environment that conditioned the
original [eo] is sometimes visible.

---

### D �� voiced alveolar stop [d]
Post-diphthong position. [eo]→[d].

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.0701 | 0.005–0.70 | PASS |
| Duration | 60 ms | 30–90 ms | PASS |

---

### O — short close-mid back rounded [o]
Post-stop position. Stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6691 | 0.50–1.0 | PASS |
| F2 centroid (550–1100 Hz) | 748 Hz | 600–1000 Hz | PASS |

---

### S — voiceless alveolar fricative [s]
Medial position. [o]→[s]→[e].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1247 | 0.0–0.35 | PASS |
| Centroid (4000–12000 Hz) | 7564 Hz | 5000–10000 Hz | PASS |

Centroid 7564 Hz — highest spectral
centre of gravity in the inventory.
[s] is the most front-heavy fricative
— the tongue tip groove creates a
narrow high-frequency resonance
that distinguishes it clearly from
[ʃ] (~4500 Hz), [θ] (~5000 Hz),
and [x] (~3000 Hz).

---

### E — short close-mid front [e]
Medial position. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | 0.50–1.0 | PASS |
| F2 centroid (1500–2500 Hz) | 1875 Hz | 1600–2300 Hz | PASS |

---

### T — voiceless alveolar stop [t]
Medial position. [e]→[t]→[l].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1723 | 0.0–0.35 | PASS |
| RMS level | 0.1093 | 0.005–0.80 | PASS |

---

### L — voiced alveolar lateral [l]
Pre-final position. [t]→[l]→[ɑ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7637 | 0.50–1.0 | PASS |
| RMS level | 0.2681 | 0.005–0.80 | PASS |

---

### A — short open back [ɑ]
Word-final. Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6679 | 0.50–1.0 | PASS |
| F2 centroid (800–1500 Hz) | 1085 Hz | 900–1400 Hz | PASS |

---

### Full word — D12

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2472 | 0.01–0.90 | PASS |
| Duration | 550 ms | 480–780 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| M | [m] | 65 ms | voiced bilabial nasal |
| EO | [eo] | 75 ms | short front-mid diphthong |
| D | [d] | 60 ms | voiced alveolar stop |
| O | [o] | 55 ms | short close-mid back rounded |
| S | [s] | 65 ms | voiceless alveolar fricative |
| E | [e] | 55 ms | short close-mid front |
| T | [t] | 60 ms | voiceless alveolar stop |
| L | [l] | 60 ms | voiced alveolar lateral |
| A | [ɑ] | 55 ms | short open back |

Total: 550 ms. Nine segments.
The longest word reconstructed so far
by segment count. The compound
structure is audible: *meodo-* (mead)
and *-setla* (of benches) are
acoustically distinct sub-units.

---

## THE DIPHTHONG INVENTORY — STATUS

With [eo] verified, the short
diphthong pair *ea/eo* is complete:

| Diphthong | IPA | F2 delta | F1 delta | Status |
|---|---|---|---|---|
| *ea* short | [eɑ] | 720 Hz ↓ | 250 Hz ↑ | ✓ SCEAÞENA |
| *eo* short | [eo] | 1074 Hz ↓ | 5 Hz stable | ✓ MEODOSETLA |
| *ēa* long | [eːɑ] | — | — | gap |
| *ēo* long | [eːo] | — | — | gap |

The acoustic distinction between
[eɑ] and [eo] is confirmed and
measurable. The two diphthongs
occupy clearly separate regions
of the acoustic space:

```
F1/F2 at offset:
  [eɑ] offset: F1 ~700 Hz, F2 ~1100 Hz  → open back
  [eo] offset: F1 ~450 Hz, F2 ~800 Hz   → mid back rounded

These are distinct vowel targets.
The trajectories are distinct paths.
The diphthongs are fully separated.
```

---

## ETYMOLOGICAL NOTE

**meodosetl — mead-bench:**

*Meodu* (mead) + *setl* (seat, bench,
settle). A compound noun referring
to the benches in the mead-hall
where warriors sat during feasts
and celebrations.

The mead-hall (*meodohēall*) was the
centre of the heroic social world —
the place where the lord distributed
treasure, where bonds of loyalty were
sealed, where poetry was performed.
To have a seat at the mead-bench was
to have a place in that world. To
lose it — *meodosetla ofteah* (deprived
of mead-benches) — was social
annihilation.

**Modern English descendants:**

- *mead*: OE *meodu* — the honey
  drink. Survives in ModE as an
  archaic/specialist term.
- *settle*: OE *setl* — a bench,
  seat, or settle. The piece of
  furniture called a *settle*
  (a high-backed bench) preserves
  the OE word exactly.
- *settle* (verb): to place, to
  seat, to establish — from the
  same root.

The [eo] diphthong in *meodo* was
lost in ME — *mede*, *mead* — the
diphthong monophthongised and the
vowel eventually raised.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `meodosetla_dry.wav` | Full word, no reverb, 145 Hz |
| `meodosetla_hall.wav` | Full word, hall reverb RT60=2.0s |
| `meodosetla_slow.wav` | Full word, 4× time-stretched |
| `meodosetla_eo_only.wav` | [eo] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameters | Iterations |
|---|---|---|---|
| [eo] | short front-mid diphthong | F2 delta 1074 Hz ↓, F1 delta 5 Hz stable | 1 |

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
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | mongum ✓  mǣgþum ✓  meodosetla ✓ — one word remaining |

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

*MEODOSETLA [meodosetlɑ] verified.*  
*[eo] added. Short diphthong pair ea/eo complete.*  
*[eo] F1 stability 5 Hz — confirmed distinct from [eɑ] F1 rise 250 Hz.*  
*Next: OFTEAH [ofteɑx] — line 6, word 4. Zero new phonemes. Line 6 final word.*
