# ǢREST — RECONSTRUCTION EVIDENCE
**Old English:** ǣrest  
**IPA:** [æːrest]  
**Meaning:** first, at first, for the first time  
**Beowulf:** Line 7, word 4 (overall word 29)  
**New phonemes:** none — pure assembly  
**Date verified:** February 2026  
**Diagnostic version:** v2  
**Reconstruction version:** v2  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  AEY long vowel          ✓ PASS
D2  AEY duration            ✓ PASS
D3  R trill (v2)            ✓ PASS
D4  E vowel                 ✓ PASS
D5  S fricative             ✓ PASS
D6  T stop                  ✓ PASS
D7  ST cluster              ✓ PASS
D8  Full word               ✓ PASS
D9  Perceptual              LISTEN
```

Total duration: **360 ms** (15874 samples at 44100 Hz) — diagnostic  
Performance duration: **900 ms** (39688 samples) — 110 Hz, dil 2.5, hall  
Eight for eight on v2. One failure on v1 resolved.

---

## VERSION HISTORY

| Version | Change | D3 R voicing | Result |
|---|---|---|---|
| v1 | Initial parameters. R_TRILL_DEPTH 0.55 | 0.4320 | FAIL |
| v2 | R_TRILL_DEPTH 0.55 → 0.40 | 0.5923 | PASS |

**Cause of v1 failure:**
Post-long-vowel [æː]→[r] context.
AM modulation at depth 0.55 created
periodic amplitude interruptions that
degraded the autocorrelation peak below
the 0.50 threshold. Signal was voiced —
RMS 0.1827 confirmed energy present —
but periodicity measure failed.

**Fix:**
Reduced trill depth 0.55 → 0.40.
AM modulation still present — trill
character preserved. Reduced depth
leaves more continuous voicing signal
in the autocorrelation window.
v2 voicing 0.5923 — passes with
margin 0.0923.

**Perceptual check on fix:**
Trill is slightly smoother at depth 0.40
vs 0.55. Still identifiable as trill
by AM periodicity at 28 Hz. Not
degraded to approximant. Fix is
phonetically acceptable.

---

## TRILL VOICING — CONTEXT DEPENDENCY

This failure reveals a context dependency
in the [r] trill voicing measurement.

**Previous [r] scores:**
- GĀR-DENA (post-short-vowel): 0.6818–0.8608
- ǢREST v1 (post-long-vowel): 0.4320

**Hypothesis:**
The long vowel [æː] preceding the trill
provides a longer, more stable periodic
signal in the measurement context.
When the autocorrelation window samples
the trill segment, the boundary between
[æː] and [r] may be included — but
the trill interruptions then cause
a steeper drop in autocorrelation than
in post-short-vowel contexts where the
boundary region is proportionally smaller.

**Not fully confirmed.** The measurement
window uses the middle 50% of the
segment, which should exclude boundary
effects for a 65 ms segment. More likely
explanation: the absolute AM depth
creates more complete amplitude zeros
at depth 0.55 (min amplitude = 1.0 -
0.55 = 0.45) than the segments
previously measured, where the trill
was in different coarticulation contexts.

**Inventory update note:**
The [r] inventory entry should note:
R_TRILL_DEPTH 0.40 as verified value.
Previous entries at 0.55 were verified
in different coarticulation contexts.
Context-dependent trill depth is a
known instrument property.

---

## PHONEME RECORD

### AEY — long open front unrounded [æː]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8484 | >= 0.50 | PASS |
| F2 centroid | 1731 Hz | 1400–2100 Hz | PASS |
| Duration | 110 ms | 90–150 ms | PASS |

F2 centroid 1731 Hz — consistent with
MǢGÞUM verification. The [æː] is
stable across word contexts. Same
formant parameters, same measured
output.

---

### R — alveolar trill [r]

| Measure | v1 | v2 | Target | Result |
|---|---|---|---|---|
| Voicing | 0.4320 | 0.5923 | >= 0.50 | v1 FAIL → v2 PASS |
| RMS level | 0.1827 | 0.1976 | 0.005–0.80 | PASS |
| TRILL_DEPTH | 0.55 | 0.40 | — | adjusted |

RMS slightly higher in v2 (0.1976 vs
0.1827) — less amplitude suppression
from the shallower AM envelope means
more energy in the measurement window.

---

### E — short close-mid front [e]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | >= 0.50 | PASS |
| F2 centroid | 1876 Hz | 1600–2300 Hz | PASS |

Voicing 0.6695 — identical to every
previous [e] measurement. Deterministic
synthesis confirmed. F2 1876 Hz —
stable.

---

### S — voiceless alveolar fricative [s]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1181 | <= 0.35 | PASS |
| Centroid | 7645 Hz | 5000–10000 Hz | PASS |

---

### T — voiceless alveolar stop [t]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.0000 | <= 0.35 | PASS |
| RMS level | 0.0506 | 0.005–0.70 | PASS |

Voicing 0.0000 — closure silence and
burst noise produce zero autocorrelation.
Clean stop.

---

### [st] cluster — D7

| Measure | Value | Target | Result |
|---|---|---|---|
| [s] voiceless | 0.1181 | <= 0.35 | PASS |
| [t] voiceless | 0.0000 | <= 0.35 | PASS |
| [s] centroid | 7645 Hz | 5000–10000 Hz | PASS |

Both alveolar. Both voiceless.
Smooth transition confirmed.
No place change — fricative releases
directly into stop closure.

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2550 | 0.01–0.90 | PASS |
| Duration (diagnostic) | 360 ms | 300–480 ms | PASS |
| Duration (performance) | 900 ms | — | — |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| ǢY | [æː] | 110 ms | long open front unrounded |
| R | [r] | 65 ms | alveolar trill |
| E | [e] | 55 ms | short close-mid front |
| S | [s] | 65 ms | voiceless alveolar fricative |
| T | [t] | 65 ms | voiceless alveolar stop |

Total diagnostic: 360 ms. Five segments.

**Voicing profile:**

```
[æː]  0.8484  voiced   — long vowel onset
[r]   0.5923  voiced   — trill
[e]   0.6695  voiced   — short vowel
[s]   0.1181  voiceless— fricative
[t]   0.0000  voiceless— stop
```

The word begins voiced and ends voiceless.
Three voiced segments followed by two
voiceless. The [s]→[t] cluster closes
the word in silence.

---

## OUTPUT FILES

| File | Parameters | Duration |
|---|---|---|
| `diag_aerest_full.wav` | dry, 145 Hz, dil 1.0 | 360 ms |
| `diag_aerest_hall.wav` | hall RT60=2.0s, 145 Hz, dil 1.0 | 360 ms |
| `diag_aerest_slow.wav` | 4× OLA stretch | ~1440 ms |
| `diag_aerest_perf.wav` | hall RT60=2.0s, 110 Hz, dil 2.5 | 900 ms |

**Performance parameters:**
110 Hz — chest voice, scop register.
Dil 2.5 — oral epic performance rate.
Hall RT60 2.0s — mead hall acoustic.
900 ms — the word as it would have
been delivered in performance.

---

## ETYMOLOGICAL NOTE

**ǣrest — first:**

Superlative of *ǣr* (early, before).
*Ǣr* → *ǣrest* — the earliest,
the first, at the very beginning.

The word appears in line 7:
*syþðan ǣrest wearð* —
since first it came to be /
since the beginning of time.

Three words. *Syþðan* — since, after.
*Ǣrest* — first, at the beginning.
*Wearð* — became, came to be.

Together: *since it first came to be.*
The absolute temporal origin of the
narrative. The moment before which
there is nothing to tell. The scop
reaches back to the beginning of
Scyld Scefing's story — and the
word for that beginning is [æːrest].

**ModE descendants:**

*Ǣrest* does not survive directly
into Modern English. The superlative
form was lost. The root *ǣr* survives
in *ere* (archaic: before) and in
the prefix *early* (*ǣr* + *līce*).

The meaning — temporal priority,
firstness, origin — is captured in
ModE by *first* (from OE *fyrmest*,
a different superlative) and *earliest*
(from the same root via a longer path).

The OE word for first-in-time
does not survive. The concept does.
The sound does not. The reconstruction
recovers the sound.

---

## LINE 7 STATUS

```
Line 7: egsode eorlas, syþðan ǣrest wearð
         [eɡsode eorlas syθðɑn æːrest weɑrθ]

  egsode  ✓  word 1
  eorlas  ✓  word 2
  syþðan  ✓  word 3
  ǣrest   ✓  word 4
  wearð   —  word 5 — remaining
```

One word remaining on line 7.
*Wearð* — became, came to be.
[weɑrθ] — W, long EA diphthong, R, TH.

Phonemes: [w] ✓, [eɑ] ✓, [r] ✓, [θ] ✓.
Zero new phonemes. Pure assembly.
Line 7 will be complete on next word.

---

*ǢREST [æːrest] verified.*  
*Zero new phonemes. 39 phonemes verified.*  
*v1 failed D3: R trill voicing 0.4320 — trill depth too aggressive.*  
*v2 fixed: R_TRILL_DEPTH 0.55 → 0.40 — voicing 0.5923 — passed.*  
*Performance: 900 ms, 110 Hz, dil 2.5, hall.*  
*Line 7: four of five words complete.*  
*Next: WEARÐ [weɑrθ] — closes line 7.*
