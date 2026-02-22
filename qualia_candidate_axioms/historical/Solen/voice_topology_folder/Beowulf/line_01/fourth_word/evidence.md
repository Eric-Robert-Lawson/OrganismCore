# IN — RECONSTRUCTION EVIDENCE
**Old English:** in  
**IPA:** [ɪn]  
**Meaning:** in  
**Source:** Beowulf, line 1, word 4  
**Date verified:** February 2026  
**Diagnostic version:** v2  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1 I vowel        ✓ PASS
D2 N nasal        ✓ PASS
D3 Full word      ✓ PASS
D4 Perceptual     LISTEN
```

Total duration: **120 ms** (5291 samples at 44100 Hz)

---

## PHONEME RECORD

### I — short near-close near-front vowel [ɪ]
The lax high front vowel. Modern English "bit", "sit".
Not [iː] (tense, higher, F2 ~2300 Hz).
Not [e] (more open, F2 ~2200 Hz).
The laxness of [ɪ] is audible in the lower F2.

**Verification method:** Band centroid (two bands).
Sub-F1 harmonics at 290 Hz (2nd harmonic of 145 Hz pitch)
pull the 200–700 Hz centroid below the actual F1 at 400 Hz.
Centroid floor set to 280 Hz to account for this.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (body) | 0.6699 | 0.65–1.0 | PASS |
| RMS level | 0.3041 | 0.01–5.0 | PASS |
| F1 centroid (200–700 Hz) | 307 Hz | 280–480 Hz | PASS |
| F2 centroid (1400–2200 Hz) | 1774 Hz | 1600–2000 Hz | PASS |

**Formant parameters:**
- F1 = 400 Hz — near-close height
- F2 = 1800 Hz — front, lax

**Vowel contrasts:**

| Vowel | F1 | F2 | Quality |
|---|---|---|---|
| [iː] | 300 Hz | 2300 Hz | tense, high |
| [ɪ] | 400 Hz | 1800 Hz | lax, near-close |
| [e] | 370 Hz | 2200 Hz | close-mid front |
| [ɛ] | 550 Hz | 1900 Hz | open-mid front |

[ɪ] is distinguished from [e] primarily by F2 (1800 vs 2200 Hz).
Both are front vowels of similar F1 height but [ɪ] is laxer
and more central, pulling F2 down by ~400 Hz.

**Duration:** 65 ms (short — unstressed function word)

---

### N — voiced alveolar nasal [n] (word-final)
Word-final position. Shorter than the medial N of DENA (55 ms
vs 70 ms). Releases into silence rather than into a following
vowel. Amplitude decays to zero at the end.

Same antiformant structure as medial [n]: IIR notch at 800 Hz,
bandwidth 200 Hz. The oral cavity anti-resonance is present
regardless of word position.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7666 | 0.60–1.0 | PASS |
| RMS (nasal murmur) | 0.1935 | 0.005–0.25 | PASS |
| Antiformant ratio (800/1200 Hz) | 0.0996 | 0.0–1.0 | PASS |

**Notes:** Antiformant ratio 0.10 — energy at 800 Hz is one
tenth of energy at 1200 Hz. Consistent with the medial N of
DENA (0.0991). The nasal anti-resonance is stable across
word positions.

**Duration:** 55 ms (word-final, shorter than medial 70 ms)

---

### Full word — D3

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2778 | 0.01–0.90 | PASS |
| Duration | 120 ms | 80–180 ms | PASS |
| I zone voicing | 0.7812 | 0.65–1.0 | PASS |
| N zone voicing | 0.7666 | 0.55–1.0 | PASS |

**Segment boundaries (samples at 44100 Hz):**

| Segment | Start | End | Duration |
|---|---|---|---|
| I | 0 | 2866 | 65 ms |
| N | 2866 | 5291 | 55 ms |

---

## DIAGNOSTIC METHODOLOGY NOTES

### F1 centroid floor for [ɪ]
The 200–700 Hz band centroid is pulled below the actual F1
by strong sub-F1 harmonic energy. At pitch 145 Hz, the 2nd
harmonic falls at 290 Hz — just below F1 at 400 Hz. This
harmonic has substantial energy and shifts the centroid
downward to ~307 Hz. The floor is set to 280 Hz rather than
the naive expectation of ~350 Hz.

This is the same pattern seen in the E vowel diagnostic
(GĀR-DENA v1: F1 measured at 366 Hz vs floor of 380 Hz).
The centroid method consistently reads below the actual
formant frequency when pitch harmonics are present near F1.
The ceiling (480 Hz) is unchanged and correctly bounds the
upper limit.

### Word-final nasal
The word-final [n] releases into silence. The amplitude
envelope decays to zero over the final 40 ms (vs a formant
transition into a following vowel in medial position). This
is phonetically correct — a final nasal in Old English has
no following schwa or release vowel in this reconstruction.
The murmur quality and antiformant structure are identical
to the medial nasal.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `in_dry.wav` | Full word, no reverb, 145 Hz pitch |
| `in_hall.wav` | Full word, hall reverb (RT60=2.0s) |
| `in_slow.wav` | Full word, 4× time-stretched |
| `in_performance.wav` | 110 Hz pitch, dil=2.5, hall reverb |
| `in_i_isolated.wav` | I vowel only, 4× slow |

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. First pass. |

---

*IN [ɪn] verified. Proceed to word 5: GĒAR-DAGUM [ɡeːɑrdɑɡum]*
