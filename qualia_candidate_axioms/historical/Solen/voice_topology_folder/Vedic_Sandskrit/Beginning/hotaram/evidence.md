# HOTĀRAM Evidence File

**Word:** hotāram (होतारम्)  
**Translation:** "invoker" (accusative singular)  
**Source:** Rigveda 1.1.1, word 8  
**IPA:** [hoːtaːrɑm]  
**Date verified:** February 2026  

---

## VERIFICATION STATUS: VERIFIED

**New phoneme:** [aː] long open central unrounded vowel  
**Status:** PARTIAL → VERIFIED  
**Method:** Perceptual + numeric (principles-first)  
**Synthesis version:** v6 (AGNI parameters restored)  
**Diagnostic version:** v4 (fixed measurement methodology)  

---

## PHONEME INVENTORY

| Phoneme | Status | Notes |
|---------|--------|-------|
| [h] | VERIFIED | voiceless glottal fricative (PUROHITAM) |
| [oː] | VERIFIED | long close-mid back rounded (PUROHITAM) |
| [t] | VERIFIED | voiceless dental stop (PUROHITAM) |
| **[aː]** | **VERIFIED** | **long open central unrounded (THIS WORD)** |
| [ɾ] | VERIFIED | alveolar tap (PUROHITAM) |
| [ɑ] | VERIFIED | short open central unrounded (AGNI) |
| [m] | VERIFIED | bilabial nasal (PUROHITAM) |

**VS phonemes verified: 24 → 25**

---

## NEW PHONEME: [aː]

### Articulation

**Place:** Open central  
**Manner:** Unrounded vowel  
**Duration:** Long (2× short counterpart [ɑ])  
**Voicing:** Continuous (modal phonation)  

### Acoustic Targets

**Formants (identical to [ɑ]):**
- F1: 700 Hz (open articulation)
- F2: 1100 Hz (central position)
- F3: 2550 Hz
- F4: 3400 Hz

**Duration:**
- [aː]: 110 ms
- [ɑ]: 55 ms
- Ratio: 2.00× (minimum 1.7× for long distinction)

**Key principle:** [aː] is phonologically distinct from [ɑ] by DURATION ALONE, not formant quality.

### Synthesis Parameters

```python
VS_AA_F      = [700.0, 1100.0, 2550.0, 3400.0]  # Hz (AGNI values)
VS_AA_B      = [130.0,  160.0,  220.0,  280.0]  # Hz (bandwidths)
VS_AA_GAINS  = [ 16.0,    6.0,    1.5,    0.5]  # relative amplitudes
VS_AA_DUR_MS = 110.0  # 2× [ɑ] duration (55ms)
VS_AA_COART_ON  = 0.10  # 10% onset coarticulation
VS_AA_COART_OFF = 0.10  # 10% offset coarticulation
```

**Coarticulation:**
- Onset: Blend 10% with preceding consonant locus frequencies
- Offset: Blend 10% with following phoneme targets
- Same architecture as all VS vowels (AGNI pattern)

---

## DIAGNOSTIC RESULTS (v4)

### D0: [oː] Voicing Sanity Check
**Result:** 0.7545 ✓ PASS  
**Purpose:** Verify voicing measurement works on verified phoneme  
**Status:** Measurement reliable  

### D1: [aː] F1 Centroid
**Measured:** 636.0 Hz  
**Target:** 620-800 Hz  
**AGNI reference:** 631.0 Hz  
**Difference:** 5.0 Hz  
**Status:** ✓ PASS  

### D2: [aː] F2 Centroid (KEY)
**Measured:** 1174.3 Hz  
**Target:** 900-1300 Hz  
**AGNI reference:** 1106.0 Hz  
**Difference:** 68.3 Hz  
**Status:** ✓ PASS  

**Critical fix:** Measurement band changed from 700-1800 Hz (v1) to 850-1400 Hz (v2+). Lower band included F1 tail energy, pulling centroid down. AGNI bands exclude F1 tail.

### D3: [aː] Absolute Duration
**Measured:** 110.0 ms  
**Target:** ≥ 93.5 ms  
**Status:** ✓ PASS  

### D4: [aː]/[ɑ] Duration Ratio (KEY)
**Measured:** 2.00×  
**Target:** ≥ 1.7×  
**Status:** ✓ PASS  

**This is the PRIMARY phonological distinction.** [aː] and [ɑ] have identical formant targets but differ in duration by 2:1 ratio.

### D5: [aː] Continuous Voicing
**Measured:** Min 0.5786, Avg 0.5851  
**Target:** ≥ 0.50  
**[oː] reference:** 0.7545  
**Status:** ✓ PASS  

**Critical fixes:**
1. **v3:** Apply body() trim (15% edges) to exclude VOT transition from [t]
2. **v4:** Increase frame window from 20ms to 40ms (autocorrelation needs ≥2 pitch periods)

### D6: [ɑ] Sanity Check
**[ɑ] F1:** 613.5 Hz (AGNI: 631.0 Hz, diff 17.5 Hz)  
**[ɑ] F2:** 1108.7 Hz (AGNI: 1106.0 Hz, diff 2.7 Hz)  
**Status:** ✓ PASS  

Verifies measurement bands are correct. [ɑ] measured in HOTĀRAM matches AGNI reference.

### D7: Full Word
**RMS:** 0.3215 ✓  
**Duration:** 466.9 ms ✓  
**Status:** ✓ PASS  

---

## PERCEPTUAL VERIFICATION

### Listener Report

**Transcription:** "hoh tah rahm"

**Analysis:**
- "hoh" = [hoː] ✓ (correct)
- "tah" = [taː] ✓ (listener perceives [aː])
- "rahm" = [rɑm] ✓ (listener perceives [ɑ])

**Duration distinction:**
> "the middle tah one is longer than ram"

**Key finding:** Listener correctly perceives duration difference between [aː] and [ɑ]. Same vowel quality, clear length distinction.

### Perceptual Validation
✓ Word is pronounceable  
✓ Phonemes are distinguishable  
✓ [aː] perceived as long variant of [ɑ]  
✓ Duration contrast clear (2:1 ratio)  

---

## ITERATION HISTORY

### Synthesis Iterations

**v1 (initial):**
- No coarticulation implementation
- Phonemes synthesized in isolation
- F1/F2 measured low (579/840 Hz)
- [h] too noisy (no context blending)
- Duration ratio correct (2.00×) ✓

**v2 (attempted fix):**
- Reduced coarticulation parameters in constants
- No actual code implementation
- Same results as v1
- Identified missing coarticulation architecture

**v3 (coarticulation added):**
- Implemented F_prev/F_next parameters
- Formant blending at onset/offset
- Context passing in word synthesis
- [h] perceptual: "sounds so much better" ✓
- F1/F2 still measuring low (579/840 Hz)
- **Root cause:** Not synthesis, but diagnostic measurement bands

**v4 (unnecessary adjustment):**
- Increased F1/F2 targets: 700→750 Hz, 1100→1250 Hz
- Attempted to compensate for formant interaction
- F1 improved (+41 Hz), F2 worsened (-35 Hz)
- **Diagnosis:** Wrong approach, measurement bands were the issue

**v5 (unnecessary adjustment):**
- Reduced bandwidths: F1 130→100 Hz, F2 160→120 Hz
- Attempted to sharpen formant peaks
- Minimal improvement
- **Diagnosis:** Still wrong approach

**v6 (FINAL - revert to AGNI):**
- **Restored AGNI verified parameters:**
  - VS_AA_F = VS_A_F = [700, 1100, 2550, 3400] Hz
  - VS_AA_B = VS_A_B = [130, 160, 220, 280] Hz
- No synthesis changes needed
- **Synthesis was correct from v3 onward**
- Problem was diagnostic measurement bands

### Diagnostic Iterations

**v1 (initial):**
- F2 measurement band: 700-1800 Hz
- **Problem:** Band starts at 700 Hz, includes F1 peak
- F1 energy (gain 16.0) dominates centroid calculation
- F2 measured at ~805 Hz (pulled down by F1 tail)

**v2 (measurement bands fixed):**
- F2 measurement band: 850-1400 Hz (AGNI values)
- F1 measurement band: 550-900 Hz (AGNI values)
- **Band now starts ABOVE F1 peak (~700 Hz)**
- F2 measured at ~1127 Hz ✓ PASS
- Added [oː] voicing sanity check (D0)
- D5 still failing (voicing 0.111)

**v3 (VOT edge exclusion):**
- Applied body() trim (15% edges) before D5 measurement
- Consistent with D1/D2 methodology
- Excludes VOT transition from [t] (first ~16ms)
- **Problem:** D5 still failing (voicing 0.121)
- **Root cause:** Frame window too short for autocorrelation

**v4 (FINAL - frame size fix):**
- Increased D5 frame window: 20ms → 40ms
- **Reasoning:** Autocorrelation needs ≥2 pitch periods
  - At 120 Hz: period = 8.3ms, need ≥16.6ms
  - measure_voicing() takes middle 50% of input
  - 20ms frame → 10ms core (only 1.2 periods) ✗
  - 40ms frame → 20ms core (2.4 periods) ✓
- D5 voicing: 0.579 ✓ PASS
- **ALL DIAGNOSTICS PASS**

---

## KEY INSIGHTS

### 1. RATNADHĀTAMAM Pattern: Fix the Ruler

**The synthesis was correct. The diagnostic was wrong.**

From ancestor:
> "The isolated vowel test is measuring F2 at 762–803 Hz when the target is 1100 Hz. That is a 300 Hz gap. But the AGNI diagnostic verified [a] at F2 = 1106 Hz using the same IIR resonator bank and the same formant parameters. The resonator worked in AGNI. It cannot have stopped working. The problem is not in the synthesis. The problem is in the measurement."

**Evidence:**
- AGNI measured [ɑ] F2 = 1106 Hz with parameters [700, 1100, 2550, 3400]
- HOTĀRAM v1 measured [ɑ] F2 = 810 Hz with SAME parameters
- **Difference: Measurement bands, not synthesis**

**Fix:**
- AGNI F2 band: 850-1400 Hz (excludes F1 tail)
- HOTĀRAM v1 F2 band: 700-1800 Hz (includes F1 tail)
- Changed HOTĀRAM to AGNI bands → F2 measured correctly

### 2. Formant Interaction and Measurement Artifacts

**F1 and F2 close together (400 Hz separation):**
- F1: 700 Hz, gain 16.0, bandwidth 130 Hz
- F2: 1100 Hz, gain 6.0, bandwidth 160 Hz
- F1 energy extends ~570-830 Hz
- F2 energy extends ~940-1260 Hz

**If F2 measurement band starts below 850 Hz:**
- Captures F1 tail energy (570-850 Hz)
- F1 dominates (gain 16.0 vs F2 gain 6.0)
- Centroid pulled down toward F1

**Solution:** Start F2 band ABOVE F1 peak (≥850 Hz)

### 3. VOT Edge Effects in Phoneme Boundaries

**[t] consists of:**
- Closure: 25ms (silent)
- Burst: 7ms (noise)
- VOT: 15ms (voice onset transition)

**Segment boundary at 212ms (end of VOT):**
- VOT is a TRANSITION from voiceless to voiced
- Voicing ramps up gradually over ~11-15ms
- First ~15ms of [aː] segment still in transition zone

**Fix:** Skip first 15% of segment edges before measurement (body() trim)

### 4. Autocorrelation Window Requirements

**measure_voicing() implementation:**
```python
core = seg[n // 4: 3 * n // 4]  # Takes middle 50%
acorr = np.correlate(core, core, mode='full')
```

**For reliable autocorrelation:**
- Need at least 2 complete pitch periods
- At 120 Hz: period = 8.3ms, need ≥16.6ms
- measure_voicing() takes middle 50%, so input needs ≥33ms

**Frame sizes:**
- 20ms frame → 10ms core → 1.2 periods ✗
- 40ms frame → 20ms core → 2.4 periods ✓

### 5. Principles-First Methodology Validation

**The ancestor was right at every step:**
1. "Fix the ruler, not the instrument" (v6 revert)
2. "Test the edge hypothesis" (VOT edge test)
3. "Do not accept 7/8" (complete the diagnostic)

**The iteration count (v1→v6) was necessary:**
- v1-v2: Identified missing coarticulation
- v3: Implemented coarticulation (correct)
- v4-v5: Explored wrong hypotheses (eliminated)
- v6: Returned to verified parameters (correct)

**This is principles-first in action:**
- Start from physics (formant targets)
- Iterate when measurements don't match
- Test hypotheses systematically
- Return to verified foundations when lost

---

## SYNTHESIS ARCHITECTURE

### Coarticulation Implementation

**All vowel synthesis functions accept F_prev and F_next:**

```python
def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_AA_F)
    
    # Onset coarticulation
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_AA_F))):
            f_mean[k] = F_prev[k] * VS_AA_COART_ON + VS_AA_F[k] * (1.0 - VS_AA_COART_ON)
    
    # Offset coarticulation
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_AA_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_AA_COART_OFF) + F_next[k] * VS_AA_COART_OFF
    
    out = apply_formants(src, f_mean, VS_AA_B, VS_AA_GAINS)
    return normalize(out, 0.72)
```

**Context passing in word synthesis:**

```python
synth_AA(F_prev=VS_T_LOCUS_F, F_next=VS_R_F, pitch_hz=pitch_hz, dil=dil)
```

**This matches AGNI architecture exactly.**

### IIR Formant Synthesis

**Second-order resonator (per formant):**

```python
r = np.exp(-np.pi * bw / sr)
cosf = 2.0 * np.cos(2.0 * np.pi * f0 / sr)
a = [1.0, -r * cosf, r * r]
b = [1.0 - r]
res = lfilter(b, a, src)
```

**Summed across all formants with gains:**

```python
out = sum(res[k] * gain[k] for k in range(4))
```

**This is standard formant synthesis. Same method used for all VS vowels.**

---

## PHYSICAL EXPLANATION

### Why [aː] and [ɑ] Have Identical Formants

**Formants are determined by vocal tract shape:**
- F1 correlates with jaw height (open → high F1)
- F2 correlates with tongue position (back/central/front)

**[aː] and [ɑ] are:**
- Same place: Open central
- Same manner: Unrounded
- Different duration only

**Physics prediction:** Identical formant frequencies, different duration.

**Measurement confirms:**
- [aː] F1: 636 Hz, [ɑ] F1: 614 Hz (22 Hz difference, <4%)
- [aː] F2: 1174 Hz, [ɑ] F2: 1109 Hz (65 Hz difference, <6%)
- [aː] duration: 110 ms, [ɑ] duration: 55 ms (2.00× ratio)

**The vowel quality is identical. Duration is the sole distinguishing feature.**

---

## COMPARISON WITH AGNI

| Parameter | AGNI [ɑ] | HOTĀRAM [aː] | HOTĀRAM [ɑ] |
|-----------|----------|--------------|-------------|
| F1 measured | 631 Hz | 636 Hz | 614 Hz |
| F2 measured | 1106 Hz | 1174 Hz | 1109 Hz |
| Duration | 55 ms | 110 ms | 55 ms |
| Voicing | (not measured) | 0.585 | (not measured) |
| Context | word-initial | post-[t] | post-[ɾ] |

**[aː] and [ɑ] in HOTĀRAM match AGNI [ɑ] within measurement tolerance.**

**Small differences (<70 Hz) attributable to:**
- Post-consonantal context (HOTĀRAM) vs word-initial (AGNI)
- Different coarticulation environments
- Measurement variance

---

## FILES

### Synthesis
- `hotaram_reconstruction.py` (v6 - AGNI parameters)
- Phoneme functions: synth_H(), synth_OO(), synth_T(), synth_AA(), synth_R(), synth_A(), synth_M()
- Word function: synth_hotaram()

### Diagnostic
- `hotaram_diagnostic.py` (v4 - fixed measurement bands + frame size)
- Tests: D0-D7 (8 diagnostics, all pass)

### Audio Output
- `hotaram_dry.wav` (normal speed, 467ms)
- `hotaram_performance.wav` (slowed 2.5×)
- `hotaram_slow.wav` (slowed 6× for analysis)
- `diag_hotaram_aa_iso.wav` (isolated [aː])
- `diag_hotaram_aa_iso_slow.wav` (isolated [aː] 6× slow)
- `diag_hotaram_a_iso.wav` (isolated [ɑ])
- `diag_hotaram_a_iso_slow.wav` (isolated [ɑ] 6× slow)

### Test Scripts
- `hotaram_vowel_test.py` (isolated vowel F1/F2 test)
- `hotaram_vot_edge_test.py` (VOT contamination test)

---

## NEXT STEPS

**[aː] is now VERIFIED.**

**VS phoneme inventory: 25 phonemes verified.**

**Next word:** Continue Rigveda 1.1.1 sequence.

**Lessons for future work:**
1. Always check measurement bands against AGNI reference
2. Test edge effects with verified phoneme sanity checks
3. Verify autocorrelation window size (≥2 pitch periods)
4. Trust AGNI parameters until proven wrong
5. The ruler can be wrong; fix measurement before synthesis

---

## ANCESTOR WISDOM

> "The synthesis is correct. Fix the ruler."

> "Do not accept 7/8."

> "This is fifteen minutes of work. Do it."

**All three were right. The process is complete.**

---

*End of evidence file.
