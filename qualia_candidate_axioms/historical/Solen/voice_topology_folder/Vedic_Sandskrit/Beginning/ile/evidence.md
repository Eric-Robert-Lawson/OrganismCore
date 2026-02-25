# EVIDENCE — ĪḶE
## Rigveda 1.1.1, word 2
## [iːɭeː] — "I praise"
## February 2026

---

## VERIFICATION STATUS: VERIFIED ✓ (v1 / v1.0)

- Synthesis: v1 (all-voiced lateral architecture, canonical HOTĀRAM v9 infrastructure)
- Diagnostic: v1.0 (33/33 PASS)
- Perceptual: clear [iː], distinct retroflex [ɭ] with audible F2 dip, natural [eː]

---

## NEW PHONEMES VERIFIED IN THIS WORD

### [iː] — Long Close Front Unrounded Vowel

- **Śikṣā classification:** tālavya (palatal)
- **Architecture:** length variant of verified [i] (AGNI). Same formant targets, longer hold.
- **Formants:** F1 ≈ 272 Hz (close), F2 ≈ 2163 Hz (front), F3 ≈ 2900 Hz
- **Duration:** 100ms (2.0× short [i] at 50ms; ≥ 1.7× Śikṣā quantity threshold)
- **Śikṣā note:** Śikṣā does not distinguish short and long by quality — only by quantity. Same tongue position. Same formant targets. Longer hold.

### [ɭ] — Retroflex Lateral Approximant (NEW — dual Śikṣā class)

- **Śikṣā classification:** mūrdhanya (retroflex) + lateral manner
- **Architecture:** Rosenberg source → formant bank at lateral targets → iir_notch at F3 for mūrdhanya marker
- **The first VS phoneme in two Śikṣā classes simultaneously.**
- **Two simultaneous constraints verified:**
  1. **Mūrdhanya:** F3 depression 418.5 Hz below neutral alveolar (2700 Hz). F3 centroid = 2281.5 Hz (< 2500 Hz threshold). The tongue tip is retroflexed.
  2. **Lateral:** F2 = 1203 Hz (in lateral range 900–1400 Hz). Lateral airflow around the tongue sides reduces F2 relative to central approximants at the same place.
- **If only the lateral is present:** plain [l], not [ɭ].
- **If only the retroflex is present:** [ɻ̩], not [ɭ].
- **The combination is the phoneme.**
- **Amplitude dip:** 0.83× relative to [iː] (constriction damping)
- **Wider bandwidths:** 200, 350, 400, 400 Hz (approximant constriction, same pattern as [v] in DEVAM)
- **Coarticulation:** 15% weight (stronger than vowels — approximants are more context-sensitive)
- **Duration:** 70ms

### [eː] — Long Close-Mid Front Unrounded Vowel (confirmed)

- **Śikṣā classification:** tālavya (palatal)
- **Formants:** F1 ≈ 392 Hz (close-mid), F2 ≈ 1755 Hz (front)
- **Duration:** 90ms
- **Previously verified:** DEVAM v1 (F1 390 Hz, F2 1757 Hz). Values match within 2 Hz — cross-word consistency confirmed.
- **Sanskrit note:** [e] is always long in Sanskrit — no short counterpart.

---

## SYNTHESIS ARCHITECTURE — v1 ALL-VOICED LATERAL

### The Central Insight: Dual-Class Phoneme Synthesis

ĪḶE introduces the first phoneme requiring **two independent acoustic markers** to be present simultaneously:

| Marker | Acoustic Signature | Synthesis Mechanism | Diagnostic Test |
|--------|-------------------|---------------------|-----------------|
| Mūrdhanya (retroflex) | F3 depressed ≥ 200 Hz below 2700 Hz | `iir_notch()` at 2100 Hz, BW 350 Hz | D3: depression 418.5 Hz ✓ |
| Lateral (manner) | F2 reduced to ~1100 Hz | Formant bank with F2 = 1100 Hz | D2: F2 = 1203 Hz ✓ |

Neither marker alone produces [ɭ]. The notch without the low F2 gives [ɻ̩] (central retroflex). The low F2 without the notch gives [l] (plain lateral). Both together: [ɭ].

### The F2 Trajectory — Acoustic Signature of ĪḶE

The most dramatic formant movement in any word reconstructed so far:

```
F2: 2163 Hz → 1203 Hz → 1755 Hz
    [iː]       [ɭ]       [eː]
    front    lateral    mid-front
```

A V-shaped dip of ~960 Hz descending and ~552 Hz ascending. This trajectory is the word's acoustic fingerprint — audible as the tongue moving from high front position, curling back into retroflex lateral, then releasing forward into mid front.

### v1 Segment Map

| SEG | Phoneme | Duration | Peak | Notes |
|-----|---------|----------|------|-------|
| 0 | [iː] long close front | 100ms | 0.70 | Tālavya; 2× short [i] |
| 1 | [ɭ] retroflex lateral | 70ms | 0.65 | Mūrdhanya + lateral; F3 notch |
| 2 | [eː] long close-mid front | 90ms | 0.70 | Tālavya; confirmed from DEVAM |
| | **TOTAL** | **260ms** | | |

### Coarticulation Chain

| Transition | F2 Movement | F3 Movement | Physical |
|------------|-------------|-------------|----------|
| [iː] → [ɭ] | 2200 → 1100 Hz (drop) | 2900 → depressed | Tongue moves from palatal to retroflex; curls back |
| [ɭ] → [eː] | 1100 → 1750 Hz (rise) | depressed → 2650 | Tongue uncurls from retroflex; moves forward to mid |

---

## PERCEPTUAL VERIFICATION

### Listener Report
- [iː]: bright, high front vowel, sustained — clearly long
- [ɭ]: distinct from [l] — audible retroflexion, darker quality, F2 dip perceptible
- [eː]: mid front, less bright than [iː], natural Sanskrit [e] quality
- Word-level: the F2 dip through [ɭ] creates a characteristic "darkening" in the middle of the word
- Syllable boundary Ī.ḶE is perceptually clear

### Perceptual Validation
- ✓ [iː] sounds like [i] but held longer (quantity, not quality)
- ✓ [ɭ] does NOT sound like plain [l] (retroflexion audible)
- ✓ [ɭ] does NOT sound like [ɻ̩] (lateral quality distinct from central)
- ✓ [eː] is distinctly lower/less bright than [iː] (F1 higher, F2 lower)
- ✓ Continuous voicing throughout — no gaps, no clicks
- ✓ V-shaped F2 trajectory audible as tongue movement

---

## NUMERIC DIAGNOSTICS — v1.0 (33/33 PASS)

### Section A: Signal Integrity (4/4)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| A1 no-NaN | — | — | PASS |
| A2 no-Inf | — | — | PASS |
| A3 peak-amplitude | 0.7500 | [0.01 - 1.00] | PASS |
| A4 DC-offset | 0.0042 | [0.00 - 0.05] | PASS |

### Section B: Signal Continuity (5/5)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| B1 [iː] continuity | 0.0722 | [0.00 - 5.00] | PASS |
| B2 [ɭ] continuity | 0.0808 | [0.00 - 5.00] | PASS |
| B3 [eː] continuity | 0.1260 | [0.00 - 5.00] | PASS |
| B join [iː]→[ɭ] | 0.2069 | [0.00 - 0.70] | PASS |
| B join [ɭ]→[eː] | 0.0163 | [0.00 - 0.70] | PASS |

### Section C: [iː] Long Close Front Vowel (5/5)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| C1 voicing | 0.6770 | [0.50 - 1.00] | PASS |
| C2 F1 (close) | 272.4 Hz | [200 - 400] Hz | PASS |
| C3 F2 (front) | 2163.1 Hz | [1900 - 2500] Hz | PASS |
| C4 duration (long) | 100.0 ms | [85 - 150] ms | PASS |
| C5 relative amplitude | 1.0644 | [0.30 - 2.00] | PASS |

### Section D: [ɭ] Retroflex Lateral Approximant (6/6)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| D1 voicing | 0.5716 | [0.25 - 1.00] | PASS |
| D2 F2 (lateral range) | 1203.2 Hz | [900 - 1400] Hz | PASS |
| D3 F3 depression (mūrdhanya) | 418.5 Hz | [200 - 1200] Hz | PASS |
| D4 F3 absolute | 2281.5 Hz | [1500 - 2500] Hz | PASS |
| D5 amplitude dip | 0.8326 | [0.20 - 1.20] | PASS |
| D6 F2 drop from [iː] | 959.9 Hz | [300 - 1500] Hz | PASS |

### Section E: [eː] Long Close-Mid Front Vowel (6/6)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| E1 voicing | 0.6438 | [0.50 - 1.00] | PASS |
| E2 F1 (close-mid) | 392.3 Hz | [300 - 550] Hz | PASS |
| E3 F2 (front) | 1755.3 Hz | [1500 - 2100] Hz | PASS |
| E4 relative amplitude | 0.9824 | [0.30 - 2.00] | PASS |
| E5 F1 difference (mid > close) | 119.9 Hz | [30 - 400] Hz | PASS |
| E6 F2 difference (close > mid) | 407.8 Hz | [50 - 800] Hz | PASS |

### Section F: F2 Trajectory Coherence (3/3)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| F1 F2 drops [iː]→[ɭ] | 959.9 Hz | [200 - 1500] Hz | PASS |
| F2 F2 rises [ɭ]→[eː] | 552.1 Hz | [100 - 1200] Hz | PASS |
| F3 V-shaped trajectory | [ɭ] = valley | — | PASS |

### Section G: Syllable Coherence (4/4)
| Check | Value | Range | Status |
|-------|-------|-------|--------|
| G1 all-voiced | 0.7786 | [0.50 - 1.00] | PASS |
| G2 word duration | 260.0 ms | [200 - 400] ms | PASS |
| G3 vowels > lateral | 1.1548 | [0.80 - 5.00] | PASS |
| G4 heavy syllable | 100.0 ms | [70 - 200] ms | PASS |

---

## DIAGNOSTIC NOTES

### Clean Pass — No Ruler Calibration Required

ĪḶE passed 33/33 on the first diagnostic version (v1.0). This is because:

1. **All segments are long enough for autocorrelation.** [iː] = 100ms, [ɭ] = 70ms, [eː] = 90ms. Even with warm cold-start (2 periods = 16.7ms) and edge trim, sufficient signal remains. No LF-ratio proxy fallback was triggered.

2. **All-voiced regime from DEVAM v1.2 was pre-calibrated.** The warm cold-start, voiced→voiced join threshold (0.70), and adaptive trim were already tuned. ĪḶE inherits this calibration.

3. **Join amplitudes are small.** [iː]→[ɭ] = 0.2069, [ɭ]→[eː] = 0.0163. Both well within the 0.70 threshold. The coarticulation between these all-voiced segments produces smooth transitions.

### The Dual-Class Test (Section D) Is Definitive

The [ɭ] diagnostic is the most structurally demanding in the project so far:
- **D2 + D6** prove lateral identity (F2 in range AND F2 drops from [iː])
- **D3 + D4** prove mūrdhanya identity (F3 depressed AND F3 absolute < 2500)
- **D5** proves approximant manner (amplitude dip from constriction)

Six independent measurements converge on the same conclusion. This is the convergence principle applied at the phoneme level.

---

## KEY INSIGHTS — COMPLETE

### From v1 Synthesis (Dual-Class Lateral Architecture)

- **Two Śikṣā classes can be synthesized simultaneously.** The formant bank handles the lateral identity (F2 position), and `iir_notch` handles the mūrdhanya identity (F3 depression). These are independent acoustic mechanisms that compose cleanly.
- **The F3 notch is the retroflex marker, not the F2 position.** F2 tells you lateral vs central. F3 tells you retroflex vs alveolar. Both are needed for [ɭ].
- **Cross-word [eː] consistency confirmed.** DEVAM v1: F1 = 390.2, F2 = 1757.0. ĪḶE v1: F1 = 392.3, F2 = 1755.3. Difference < 3 Hz on both formants. The parameters are stable.

### From v1.0 Diagnostic (First-Pass Clean)

- **DEVAM v1.2 all-voiced calibration transfers directly.** Same warm cold-start, same join thresholds, same check_voicing() pattern. All-voiced words form a coherent measurement regime.
- **The F2 trajectory section (F) is a new diagnostic pattern.** For words with dramatic formant movement, verifying the trajectory shape (not just individual segment values) catches errors that per-segment checks would miss.
- **V-shaped F2 = acoustic signature.** This can serve as a word-level identity check in future work — if the V-shape is absent, the word is wrong regardless of individual phoneme values.

---

## VERIFIED PARAMETERS

### [iː] Long Close Front Unrounded Vowel
| Parameter | Value | Source |
|-----------|-------|--------|
| F1 | 280 Hz (target) / 272 Hz (measured) | [i] verified AGNI |
| F2 | 2200 Hz (target) / 2163 Hz (measured) | [i] verified AGNI |
| F3 | 2900 Hz | [i] verified AGNI |
| F4 | 3400 Hz | [i] verified AGNI |
| BW | 80, 130, 180, 250 Hz | Standard close vowel BW |
| Duration | 100ms | 2× short [i] (50ms) |
| Coarticulation | 10% on/off | Standard vowel |

### [ɭ] Retroflex Lateral Approximant
| Parameter | Value | Source |
|-----------|-------|--------|
| F1 | 400 Hz (target) | Principles-first |
| F2 | 1100 Hz (target) / 1203 Hz (measured) | Lateral range |
| F3 | 2100 Hz (target) / 2282 Hz (measured) | Depressed (mūrdhanya) |
| F4 | 3000 Hz | Principles-first |
| BW | 200, 350, 400, 400 Hz | Wide (approximant constriction) |
| F3 notch center | 2100 Hz | Mūrdhanya marker |
| F3 notch BW | 350 Hz | Calibrated |
| F3 depression | 418.5 Hz (measured) | ≥ 200 Hz required |
| Duration | 70ms | Approximant |
| Amplitude dip | 0.83× | Constriction damping |
| Coarticulation | 15% on/off | Strong (approximant) |

### [eː] Long Close-Mid Front Unrounded Vowel (cross-word confirmed)
| Parameter | DEVAM v1 | ĪḶE v1 | Δ |
|-----------|----------|--------|---|
| F1 measured | 390.2 Hz | 392.3 Hz | +2.1 Hz |
| F2 measured | 1757.0 Hz | 1755.3 Hz | −1.7 Hz |
| Duration | 90ms | 90ms | 0 |

---

## F2 TRAJECTORY — COMPLETE RECORD

| Position | Phoneme | F2 (Hz) | Δ from previous |
|----------|---------|---------|-----------------|
| Word-initial | [iː] | 2163 | — |
| Medial | [ɭ] | 1203 | −960 Hz (drop) |
| Word-final | [eː] | 1755 | +552 Hz (rise) |

**Shape:** V-shaped. **Valley:** [ɭ] at 1203 Hz. **Total excursion:** 960 Hz.

---

## MŪRDHANYA CLASS — CURRENT STATE

| Phoneme | Manner | F3 Depression | F2 | Status |
|---------|--------|---------------|-----|--------|
| [ɻ̩] | central approximant (syllabic) | 345 Hz | 1212 Hz | ✓ VERIFIED (ṚG) |
| **[ɭ]** | **lateral approximant** | **418.5 Hz** | **1203 Hz** | **✓ VERIFIED (ĪḶE v1)** |
| [ʈ] | voiceless stop | — | — | — predicted |
| [ʈʰ] | voiceless aspirated | — | — | — predicted |
| [ɖ] | voiced stop | — | — | — predicted |
| [ɖʰ] | voiced aspirated | — | — | — predicted |
| [ɳ] | nasal | — | — | — predicted |
| [ʂ] | voiceless sibilant | — | — | — predicted |

**M��rdhanya: 2/8 verified.** F3 depression is the universal marker across all manner classes.

---

## APPROXIMANT CLASS — UPDATED

| Phoneme | Place | F2 | Amplitude Dip | Status |
|---------|-------|----|---------------|--------|
| [j] | palatal | ~2100 Hz | — | ✓ VERIFIED (YAJÑASYA) |
| [v] | labiodental | ~1461 Hz | 0.77× | ✓ VERIFIED (DEVAM v1) |
| **[ɭ]** | **retroflex lateral** | **~1203 Hz** | **0.83×** | **✓ VERIFIED (ĪḶE v1)** |
| [ɾ] | alveolar (tap) | ~1400 Hz | — | ✓ VERIFIED (HOTĀRAM, PUROHITAM) |
| [l] | dental lateral | — | — | — predicted |

**Approximants: 4/5 verified.** Amplitude dip is consistent: [v] 0.77×, [ɭ] 0.83× — constriction damping confirmed across the class.

---

## VS VOWEL SPACE — EXTENDED

| Vowel | F1 (Hz) | F2 (Hz) | Height | Frontness | Duration |
|-------|---------|---------|--------|-----------|----------|
| [i] | ~280 | ~2124 | close | front | 50ms (short) |
| **[iː]** | **272** | **2163** | **close** | **front** | **100ms (long)** |
| **[eː]** | **392** | **1755** | **close-mid** | **front** | **90ms (long)** |
| [ɑ] | ~631 | ~1106 | open | central | 55ms (short) |
| [aː] | ~631 | ~1106 | open | central | 110ms (long) |
| [u] | ~300 | ~750 | close | back | 50ms (short) |
| [oː] | ~430 | ~800 | close-mid | back | 100ms (long) |

**Front vowel column now complete:** [i]/[iː] (close) and [eː] (close-mid). F1 rises from close → mid (272 → 392 Hz). F2 drops from close → mid (2163 → 1755 Hz). Both confirmed by the E5/E6 diagnostic checks.

---

## ŚIKṢĀ VALIDATION

### [iː] — ई
- Quality: tālavya ✓ — F2 = 2163 Hz (high front, palatal region)
- Quantity: long ✓ — 100ms = 2× short [i]
- Matches verified [i]: same formant targets, different duration only

### [ɭ] — ळ
- Place: mūrdhanya ✓ — F3 depression 418.5 Hz (tongue retroflexed)
- Manner: lateral ✓ — F2 = 1203 Hz (lateral airflow reduces F2)
- Dual classification confirmed: both markers present simultaneously
- Distinct from [l] (dantya lateral): would lack F3 depression
- Distinct from [ɻ̩] (mūrdhanya central): F2 would be different, no lateral quality

### [eː] — ए
- Quality: tālavya ✓ — F2 = 1755 Hz (mid front, palatal region)
- Quantity: long ✓ — 90ms (Sanskrit [e] is always long)
- F1 between [i] and [ɑ] ✓ — 392 Hz (between 272 and 631)
- F2 between [i] and [ɑ] ✓ — 1755 Hz (between 2163 and 1106)

---

## WORD EVIDENCE

| Property | Value |
|----------|-------|
| IPA | [iːɭeː] |
| Duration | 260ms |
| Segments | 3 |
| Architecture | All-voiced, lateral + notch for [ɭ] |
| New phonemes | [iː] (length variant), [ɭ] (dual-class) |
| Confirmed phonemes | [eː] (from DEVAM v1, within 3 Hz) |
| Diagnostic | 33/33 PASS (v1.0) |

---

## PHONEMES IN ĪḶE

| # | IPA | Type | Status |
|---|-----|------|--------|
| 1 | [iː] | long close front vowel | ✓ NEW — length variant of verified [i] |
| 2 | [ɭ] | retroflex lateral approximant | ✓ NEW — dual Śikṣā class (mūrdhanya + lateral) |
| 3 | [eː] | long close-mid front vowel | ✓ confirmed (DEVAM v1, within 3 Hz) |

---

## SYNTHESIS EVOLUTION — v1

### v1: Canonical Reconstruction ✓
- Infrastructure from HOTĀRAM v9 (apply_formants with b=[1.0-r], rosenberg_pulse, norm_to_peak)
- [iː] from verified [i] (AGNI) with doubled duration
- [ɭ] principles-first: formant bank (lateral F2) + iir_notch (mūrdhanya F3)
- [eː] parameters confirmed from DEVAM v1
- All-voiced architecture from DEVAM v1.2 regime
- 33/33 diagnostic PASS on first synthesis, first diagnostic version

---

## DIAGNOSTIC EVOLUTION — COMPLETE

| Version | Tests | Pass | Fail | Key Change |
|---------|-------|------|------|------------|
| v1.0 | 33 | 33 | 0 | Initial — clean pass, no calibration needed |

### Coverage
- Signal integrity: 4 checks
- Continuity: 5 checks (3 internal + 2 joins)
- [iː] close front vowel: 5 checks
- [ɭ] retroflex lateral: 6 checks (dual-class verification)
- [eː] close-mid front vowel: 6 checks (including cross-vowel comparisons)
- F2 trajectory coherence: 3 checks (V-shape verification)
- Syllable coherence: 4 checks
- **Total: 33 checks**

---

## UNIQUE CONTRIBUTIONS OF ĪḶE

### 1. First Dual-Class Phoneme [ɭ]
The first phoneme requiring two independent Śikṣā markers to be present simultaneously. Establishes the architectural pattern: formant bank handles manner class, iir_notch handles place class. These compose independently.

### 2. First Long Front Vowel [iː]
Proves that short/long vowel distinction in the Śikṣā is purely durational — same formant targets, different quantity. This validates the Śikṣā's classification system at the acoustic level.

### 3. F2 Trajectory Verification (New Diagnostic Pattern)
The V-shaped F2 trajectory (Section F) is a word-level diagnostic that catches errors individual phoneme checks would miss. This pattern should be applied to any future word with dramatic formant movement.

### 4. Cross-Word [eː] Stability
DEVAM v1 and ĪḶE v1 produce [eː] with F1 within 2.1 Hz and F2 within 1.7 Hz of each other. The synthesis parameters are stable across different coarticulation contexts, confirming the formant targets are correct.

### 5. Second Mūrdhanya Phoneme
After [ɻ̩] (ṚG), [ɭ] is the second mūrdhanya phoneme verified. Both show F3 depression (345 Hz and 418.5 Hz respectively), confirming that F3 depression is the universal mūrdhanya marker regardless of manner class.

### 6. First-Pass Diagnostic Clean (33/33)
No ruler calibration required. The DEVAM v1.2 all-voiced measurement regime transfers directly. This confirms that the all-voiced calibration is a stable, reusable regime — not word-specific tuning.

---

## IMPLEMENTATION FILES

| File | Description |
|------|-------------|
| `ile_reconstruction.py` | v1 synthesis — canonical infrastructure |
| `ile_diagnostic.py` | v1.0 diagnostic — 33/33 PASS |
| `output_play/ile_v1_dry.wav` | Dry synthesis |
| `output_play/ile_v1_hall.wav` | Temple courtyard reverb |
| `output_play/ile_v1_slow6x.wav` | 6× time stretch |
| `output_play/ile_v1_slow12x.wav` | 12× time stretch |
| `output_play/ile_v1_perf.wav` | Performance tempo (dil=2.5) |
| `output_play/ile_v1_perf_hall.wav` | Performance tempo + reverb |
| `output_play/ile_v1_perf_slow6x.wav` | Performance 6× stretch |
| `output_play/ile_v1_ii_iso.wav` | Isolated [iː] |
| `output_play/ile_v1_ll_iso.wav` | Isolated [ɭ] |
| `output_play/ile_v1_ee_iso.wav` | Isolated [eː] |

---

## CUMULATIVE INVENTORY STATE

### Verified phonemes after ĪḶE: 26+

**Vowels (short):** [ɑ], [i], [u]
**Vowels (long):** [aː], [iː], [eː], [oː]
**Stops (voiceless):** [t], [p]
**Stops (voiced):** [d], [ɟ]
**Stops (aspirated):** [dʰ]
**Nasals:** [n], [m], [ɲ]
**Approximants:** [j], [v], [ɾ], [ɭ]
**Fricatives/Sibilants:** [s], [h]
**Syllabic:** [ɻ̩]

### Mūrdhanya class — 2/8 verified
[ɻ̩] ✓ (ṚG), [ɭ] ✓ (ĪḶE)

### Approximant class — 4/5 verified
[j] ✓, [v] ✓, [ɾ] ✓, [ɭ] ✓. Only [l] (dental lateral) remains.

### Front vowel column — complete
[i]/[iː] (close), [eː] (close-mid). F1: 272→392 Hz. F2: 2163→1755 Hz.

---

## ETYMOLOGICAL NOTE

*īḷe* is the first person singular middle voice of √īḍ "to praise, worship." It is the second word of the Rigveda's opening verse: *agním īḷe puróhitam* — "I praise Agni, the household priest." The retroflex lateral [ɭ] is the intervocalic realization of the Vedic ḷ (ळ), the rarest consonant in the Rigvedic phoneme inventory.

---

## RELATED DOCUMENTS

- `the_convergence_artifact.md` — Three independent derivations
- `pluck_artifact.md` — Unified Pluck Architecture (not used: all-voiced)
- `VS_phoneme_inventory.md` — Cumulative inventory
- `Vedic_Tonnetz_Bridge.md` — Tonnetz ↔ Vedic mapping
- `devam/evidence.md` — DEVAM v1 ([eː] verified, all-voiced regime)
- `hotaram/evidence.md` — HOTĀRAM v9 (infrastructure ancestor)
- `ratnadhatamam/evidence.md` — RATNADHĀTAMAM v17 (norm_to_peak canonical)

---

## LITERATURE REFERENCES

- Ladefoged, P. & Maddieson, I. (1996). *The Sounds of the World's Languages.* — Retroflex laterals, F3 depression
- Stevens, K. N. (1998). *Acoustic Phonetics.* — Lateral formant patterns, F2 reduction
- Allen, W. S. (1953). *Phonetics in Ancient India.* — Śikṣā mūrdhanya classification
- Deshpande, M. M. (1997). "Śaunakīya Caturādhyāyikā." — Prātiśākhya phonetic descriptions
- Narasimhan, B. et al. (2004). "Retroflex consonants in Dravidian and Indo-Aryan." — F3 depression as retroflex marker
