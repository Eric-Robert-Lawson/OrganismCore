# GĀR-DENA — RECONSTRUCTION EVIDENCE
**Old English:** Gār-Dena  
**IPA:** [ɡɑːrdenɑ]  
**Meaning:** of the Spear-Danes (genitive plural)  
**Source:** Beowulf, line 1, word 3  
**Date verified:** February 2026  
**Diagnostic version:** v6  
**Reconstruction version:** v4  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1 G onset        ✓ PASS
D2 Ā vowel        ✓ PASS
D3 R trill        ✓ PASS
D4 D onset        ✓ PASS
D5 E vowel        ✓ PASS
D6 N nasal        ✓ PASS
D7 A final        ✓ PASS
D8 Full word      ✓ PASS
D9 Perceptual     LISTEN
```

Total duration: **702 ms** (30956 samples at 44100 Hz)

---

## PHONEME RECORD

### G — voiced velar stop [ɡ]
Plain velar before back vowel Ā. No palatalization.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1080 | 0.005–0.80 | PASS |
| Closure RMS (voicing bar) | 0.0028 | 0.001–0.05 | PASS |
| Burst RMS | 0.2252 | 0.010–1.0 | PASS |
| Burst centroid | 1627 Hz | 800–2500 Hz | PASS |

**Notes:** Voicing bar present throughout closure. Voiced stop —
no aspiration. Burst centroid at velar position (~1500–1700 Hz),
distinct from alveolar D at ~3500 Hz.

---

### Ā — long open back vowel [ɑː]
Pre-Great-Vowel-Shift. Not [æ], not [eɪ]. The vowel of
Latin *pater*, German *Bahn*.

**Verification method:** Band centroid 600–1400 Hz.  
LPC peak separation is not possible for [ɑː] at 110 Hz
analysis pitch — F1 (750 Hz) and F2 (1100 Hz) are only 350 Hz
apart and merge into a single hill in the LPC envelope,
peaking at ~603 Hz due to harmonic interaction. The band
centroid method is the correct measurement for this vowel
class at low pitch.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (body) | 0.8794 | 0.75–1.0 | PASS |
| RMS level | 0.2554 | 0.02–5.0 | PASS |
| F1+F2 centroid (600–1400 Hz) | 847 Hz | 750–1050 Hz | PASS |

**Formant parameters:**
- F1 = 750 Hz (high — open jaw)
- F2 = 1100 Hz (low — back tongue)
- Contrast: [æ] has F1=668 F2=1873; [eː] has F1=409 F2=2132
- [ɑː] inverts both axes relative to front vowels

**Duration:** 180 ms (long vowel, dil=1.0)

---

### R — short trill [r]
Germanic alveolar trill. Not the English approximant [ɹ].
Two tongue-tip closures against the alveolar ridge.
F3 suppressed throughout (~1690 Hz) — rhoticity carried
in the formant structure even during open phases.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1758 | 0.005–0.80 | PASS |
| Voicing (open phases) | 0.6546 | 0.40–1.0 | PASS |
| Trill modulation depth | 0.5606 | 0.22–1.0 | PASS |
| Trill rate | 18.2 Hz | 15–70 Hz | PASS |

**Notes:** 2-closure short trill. Modulation depth 0.56 — the
closures produce clear amplitude silences. Rate 18.2 Hz =
period 55 ms per cycle (35 ms closure + 20 ms open). Trill
sits at the compound boundary GĀR | DENA. The D closure
follows immediately after the final trill open phase.

---

### D — voiced alveolar stop [d]
Onset of second element DENA. Voiced throughout — no
aspiration, no prevoicing gap.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.0988 | 0.005–0.80 | PASS |
| Burst centroid | 3486 Hz | 2000–5000 Hz | PASS |

**Notes:** Alveolar burst centroid at ~3500 Hz, clearly
distinct from velar G burst at ~1600 Hz. Place contrast
is acoustically auditable in the 4x slow isolated files.

---

### E — short close-mid front vowel [e]
The E of DENA. Not the long [eː] of WĒ (line 1, word 1).
Same formant target, shorter duration.

**Verification method:** Band centroid (two bands).  
LPC cannot isolate F1 at 370 Hz — F2 at 2200 Hz dominates
the LPC spectrum at all pre-emphasis settings. Band centroid
is the correct method for this vowel.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (body) | 0.7895 | 0.65–1.0 | PASS |
| RMS level | 0.3164 | 0.01–5.0 | PASS |
| F1 centroid (200–700 Hz) | 301 Hz | 300–500 Hz | PASS |
| F2 centroid (1800–2600 Hz) | 2167 Hz | 1900–2400 Hz | PASS |

**Formant parameters:**
- F1 = 370 Hz (close-mid height)
- F2 = 2200 Hz (front tongue position)

**Duration:** 80 ms (short — unstressed syllable)

---

### N — voiced alveolar nasal [n]
Velum lowered. Oral cavity occluded at alveolar ridge.
Air flows through nasal passage. Antiformant at 800 Hz
from oral cavity anti-resonance.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7992 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2439 | 0.005–0.25 | PASS |
| Antiformant ratio (800/1200 Hz) | 0.0991 | 0.0–1.0 | PASS |

**Notes:** Antiformant ratio 0.099 — energy at 800 Hz is
one tenth of energy at 1200 Hz. IIR notch filter (200 Hz
bandwidth) confirmed working. This is the correct acoustic
signature of the nasal anti-resonance.

---

### A — short open back vowel [ɑ]
Genitive ending. Unstressed. Word-final decay.
Same phoneme as Ā, shorter duration, lower amplitude.

**Verification method:** Band centroid 600–1400 Hz.
Same LPC limitation as Ā — back vowel F1/F2 merge at
low pitch.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (body) | 0.5346 | 0.50–1.0 | PASS |
| RMS level | 0.1847 | 0.005–5.0 | PASS |
| F1+F2 centroid (600–1400 Hz) | 832 Hz | 800–1100 Hz | PASS |

**Formant parameters:**
- F1 = 840 Hz (open jaw — higher than Ā)
- F2 = 1150 Hz (back tongue)

**Duration:** 70 ms (short, unstressed, word-final)

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| Full-word RMS | 0.2225 | 0.01–0.90 | PASS |
| Ā zone voicing | 0.9230 | 0.70–1.0 | PASS |
| E zone voicing | 0.8188 | 0.60–1.0 | PASS |
| N zone voicing | 0.7992 | 0.55–1.0 | PASS |
| A zone voicing | 0.8066 | 0.45–1.0 | PASS |

**Segment boundaries (samples at 44100 Hz, dil=1.0):**

| Segment | Start | End | Duration |
|---|---|---|---|
| G | 0 | 4057 | 92 ms |
| Ā | 4057 | 11995 | 180 ms |
| R | 11995 | 17065 | 115 ms |
| D | 17065 | 20592 | 80 ms |
| E | 20592 | 24120 | 80 ms |
| N | 24120 | 27207 | 70 ms |
| A | 27207 | 30956 | 85 ms |

---

## DIAGNOSTIC METHODOLOGY NOTES

### LPC limitations at low pitch
The Rosenberg pulse source at 110–145 Hz produces harmonics
spaced 110–145 Hz apart. The LPC spectral envelope is fit
across this harmonic structure. For vowels with closely-spaced
formants (F2 − F1 < 400 Hz), the LPC cannot resolve separate
peaks — they merge into a single hill. This is a fundamental
property of LPC on low-pitched speech, not a synthesis failure.

**Vowels affected:** [ɑː] (F1=750, F2=1100, spacing=350 Hz)
and [ɑ] (F1=840, F2=1150, spacing=310 Hz).

**Solution used:** Spectral band centroid. The centroid of
the 600–1400 Hz band falls between F1 and F2, weighted by
gain. For [ɑː] the centroid is 847 Hz. For [ɑ] it is 832 Hz.
Both are in the correct range for open back vowels.

**Vowels unaffected:** [e] (F1=370, F2=2200, spacing=1830 Hz)
and [eː] in WĒ. These have wide enough separation that LPC
could in principle separate them, but F2 at 2200 Hz dominates
the LPC spectrum because its gain per Hz is higher. Band
centroid used for [e] as well.

### Trill modulation measurement
The trill modulation is measured by extracting the amplitude
envelope of the trill segment via short-window RMS, then
computing the autocorrelation of that envelope. The peak
autocorrelation value in the 15–60 Hz range gives the
modulation depth and rate.

For a 2-closure trill: 0.56 modulation depth, 18.2 Hz rate.
This is a physically correct short trill. A 3-closure trill
would show higher depth (~0.7) and more distinct periodicity.

### Antiformant measurement
The nasal antiformant is verified by comparing band energy
at 700–900 Hz (at the notch) versus 1000–1400 Hz (above the
notch). Ratio 0.099 confirms the IIR notch is suppressing
the 800 Hz region by approximately 10 dB.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `gar_dena_dry.wav` | Full word, no reverb, 145 Hz pitch |
| `gar_dena_hall.wav` | Full word, hall reverb (RT60=2.0s) |
| `gar_dena_slow.wav` | Full word, 4× time-stretched |
| `gar_dena_performance.wav` | 110 Hz pitch, dil=2.5, hall reverb |
| `gar_dena_r_isolated.wav` | R trill only, 4× slow |
| `gar_dena_aa_isolated.wav` | Ā vowel only, 4× slow |

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters |
| v2 | AA_GAINS[1] 6→14; R_CLOSURE_MS 20→35; E_F[0] 430→370; N antiformant subtraction→IIR notch; A_F[0] 720→780 |
| v3 | A_F[0] 780→840; A_B[0] 160→180 |
| v4 | AA_F[1] 1000→1100; AA_GAINS[1] 14→8; A_F[1] 1050→1150; E_GAINS[0] 18→28; N_ANTI_BW 80→200 Hz |

---

## WHAT THIS IS NOT

This reconstruction does not claim to be the only correct
pronunciation of Old English Gār-Dena. It claims:

1. The formant targets are consistent with reconstructed
   Old English phonology as documented in scholarship.
2. The acoustic output passes objective numeric verification
   of voicing, spectral centroid, stop burst place, nasal
   antiformant, and trill modulation.
3. The synthesis engine (Rosenberg pulse + parallel formant
   resonators + IIR notch) is physically motivated.
4. The parameters are documented and reproducible.

Dialectal variation, individual speaker variation, and
scholarly disagreement about pre-shift vowel phonetics
are not resolved here. The reconstruction represents one
phonologically defensible realization.

---

*GĀR-DENA verified. Proceed to word 4: IN [ɪn]*
