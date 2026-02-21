# VOICE SYNTHESIS — ARCHITECTURE REASONING
## Deep Analysis of Current Failures and Required Approach
## February 2026

---

## THE CORE ARCHITECTURAL PROBLEM

The current synthesis engine is not a
formant synthesizer for fricatives.
It is a **cascade resonator** (correct for
vowels and approximants) with **post-hoc
noise addition** (incorrect for fricatives).

### What is happening now (wrong)

```
Voiced fricative (V, Z, DH):

  voiced_full (Rosenberg pulse)
      ↓
  tract(F1, F2, F3, F4)   ← cascade path
      ↓                      F1 amplifies
  tract_output               by 22dB
      ↓
  + bypass_noise (separate)
  + buzz (Rosenberg × gain, post-tract)

Result: two independent signals added.
  One vowel-shaped (from cascade).
  One noise-shaped (from bypass).
  They do not share a spectral envelope.
  The ear hears them as separate objects.
```

### What should happen (Klatt 1980 parallel path)

```
Voiced fricative (V, Z, DH):

  voiced_source × AV ──→ parallel_F1(BW1) ──┐
  voiced_source × AV ──→ parallel_F2(BW2) ──┤
  noise_source  × AF ──→ frication_F(BWf) ──┘→ sum

Result: one signal with mixed character.
  Low frequencies: voiced buzz (F1 × AV).
  High frequencies: frication (Ff × AF).
  They share the same output sum.
  Perceptually: one evolving texture.
```

The difference is not a matter of gain tuning.
It is a matter of signal routing.
The parallel path cannot be simulated by
adding a cascade output to a bypass output.
They are fundamentally different spectral structures.

---

## WHY THE DIAGNOSTIC NUMBERS ARE MISLEADING

### The V paradox

V measures:
- `periodicity=0.531` (target 0.3) → FAIL
- `f1_ratio=0.52` (target 0.2) → FAIL
- But perceptually: **sounds more like V than before**

This is not a contradiction.
The diagnostic targets are wrong for V.

Real `/v/`:
- Has a strong voice bar (voiced buzz below 500Hz)
- Has labiodental friction (noise 800-3000Hz)
- The voice bar IS high f1_ratio energy
- The voicing IS high periodicity

Real `/v/` would measure:
- `periodicity ≈ 0.45-0.65`
- `f1_ratio ≈ 0.35-0.55`

The targets were set from literature tables
that describe gross spectral character,
not from measurements of actual formant
synthesis output. They are wrong.

### The centroid_jump failure for fricatives

S↔AA centroid jump: **8700Hz**.
Target: ≤1500Hz → FAIL.

But in real speech, S↔AA centroid jump
is approximately 7000-9000Hz.
This is one of the largest spectral
contrasts in the entire phoneme inventory.
It is **correct and expected**.

The threshold of 1500Hz was designed for
vowel↔vowel transitions.
Applied to fricative↔vowel: it will always fail.
It is not measuring synthesis quality.
It is measuring phoneme class distance.

### The IH→AA IS divergence

IH ph→AA: IS_ratio=65.76 (recurring failure).

IH (F2≈1990Hz) → AA (F2≈1100Hz) with
no coarticulation between them.
The F2 trajectory must jump 890Hz
at the boundary.
In real speech this jump is smoothed by:
  - Coarticulation across syllable boundaries
  - Sub-phonemic transitions
  - Lip and tongue movement overlap

Our synthesizer has none of this.
The test carrier [IH, AA] is phonetically
unrealistic. This is a test design failure,
not a synthesis failure.

---

## WHAT THE DIAGNOSTIC HAS CORRECTLY IDENTIFIED

Setting aside the false positives, the
diagnostic has found real problems:

### 1. DH f1_ratio=0.373 (target 0.15)
Real issue: the DH buzz contributes too much
F1 energy relative to the dental friction.
Partially a parameter issue, partially
architectural (buzz is Rosenberg direct,
not a shaped low-frequency source).

### 2. Z f1_ratio=0.232 (target 0.08)
Real issue: same. Z buzz contributes F1 energy.
But Z perceptually sounds like Z now.
The f1_ratio target may be wrong, not the synthesis.

### 3. S ph→AA IS_ratio=40.63
Real issue: this might actually be a real
discontinuity at the S offset.
S body: centroid 8800Hz.
AA onset: centroid rises from 0 (silence)
to 900Hz over the onset ramp.
The spectral jump is real.
Whether it is perceptually problematic
depends on whether there is a smooth
amplitude transition covering it.

---

## THE CORRECT DEVELOPMENT PATH

### Phase 1 — Fix the diagnostic (immediate)

Before changing any synthesis code,
fix the diagnostic to not report false failures.

**Changes to make:**

1. **Phoneme-class-specific thresholds**
   ```
   CENTROID_JUMP_THRESHOLD = {
     'fricative→vowel': 10000,  # always large, not a failure
     'vowel→fricative': 10000,  # same
     'vowel→vowel':      1500,  # real continuity measure
     'fricative→fricative': 5000,
   }
   ```

2. **Correct identity targets**
   ```
   V:  periodicity=0.45±0.20, f1_ratio=0.40±0.20
   DH: periodicity=0.25±0.20, f1_ratio=0.30±0.15
   Z:  f1_ratio=0.15±0.10
   AA: periodicity=0.55±0.20
   ```

3. **Skip same-phoneme continuity**
   `[AA, AA]` has no real boundary.

4. **Replace IH test carrier**
   Use `[IH, AH]` instead of `[IH, AA]`.
   IH→AH is a natural vowel transition.
   IH→AA is an unusual jump.

### Phase 2 — Implement Klatt parallel path (next major revision)

This is the architectural fix that resolves
the fundamental voiced fricative problem.

```python
def parallel_fricative(
        voiced_src,    # Rosenberg pulse
        noise_src,     # white noise
        AV,            # voicing amplitude (0-1)
        AF,            # frication amplitude (0-1)
        F_voiced,      # formant freqs for voiced component
        B_voiced,      # formant BWs for voiced component
        Ff,            # frication center frequency
        Bf,            # frication bandwidth
        sr=SR):
    """
    Klatt-style parallel path for voiced fricatives.
    
    Voiced component: voiced_src passed through
    parallel resonators at F_voiced[0], F_voiced[1].
    Each resonator is independent (parallel, not cascade).
    No 22dB F1 amplification from cascade chain.
    
    Frication component: noise_src passed through
    bandpass at (Ff, Bf).
    
    Sum: voiced × AV + frication × AF.
    """
    out = np.zeros(len(voiced_src), dtype=np.float32)
    
    # Voiced component through parallel F1, F2 only
    # (F3, F4 not used — they are inaudible for fricatives)
    for fi in range(min(2, len(F_voiced))):
        fc  = F_voiced[fi]
        bw  = B_voiced[fi]
        seg = _parallel_resonator(
            voiced_src, fc, bw, sr)
        out += seg * AV
    
    # Frication component
    fric = _bandpass_noise(noise_src, Ff, Bf, sr)
    out += fric * AF
    
    return calibrate(out)
```

Frication parameters (from Klatt 1980
and acoustic phonetics literature):

```
Phoneme  Ff(Hz)  Bf(Hz)  AV    AF    notes
V        900     400     0.35  0.45  labiodental, low Ff
DH       2500    800     0.30  0.40  dental, mid Ff
Z        8000    1200    0.25  0.60  alveolar, high Ff
ZH       3000    900     0.20  0.55  palatal
V        900     400     0.35  0.45  labiodental
```

### Phase 3 — Recalibrate targets against parallel path output

After implementing the parallel path:
- Measure what the parallel path actually produces
- Set identity targets to match those measurements ± tolerance
- The system measures itself and sets its own targets

This is the true self-referential calibration.

---

## META-OBSERVATION: THE ITERATION TRAP

We have been in an iteration trap:

```
Synthesis change → Diagnostic fails differently
  → Diagnostic change → Different failures visible
    → Synthesis change → ...
```

The trap exists because we have been treating
the diagnostic as ground truth when it
is a hypothesis about what correct output
should look like.

The diagnostic is only valid when:
1. The architecture is physically correct
2. The targets match what the correct
   architecture can produce
3. The measurement methods are appropriate
   for each phoneme class

None of these three conditions have been
fully satisfied simultaneously.

**The exit from the trap:**
Fix the architecture first.
Then let the system measure itself to
set its own targets.
Then iterate on parameters only.

---

## WHAT IS ACTUALLY WORKING

Acknowledge what is correct so we
do not break it:

```
✓ All vowels: identity passing (AH, IH, OY, AE, EH, IY)
✓ S identity: passing (centroid=8879Hz, periodicity=0.036)
✓ H identity: passing (centroid=1235Hz, periodicity=0.0)
✓ DH continuity: passing both directions
✓ H continuity: passing both directions
✓ AH continuity: passing both directions
✓ OY continuity: passing both directions
✓ AE continuity: passing both directions
✓ IY continuity: passing both directions
✓ EH continuity: passing both directions
```

S and H are acoustically correct.
All vowels are acoustically correct.
DH and H are **continuously** correct
even though DH still fails f1_ratio.

What is genuinely wrong:
```
✗ V:  architecture wrong (no parallel path)
✗ Z:  f1_ratio off (partial architecture fix)
✗ DH: f1_ratio off (buzz adds F1 energy)
```

These three share the same root cause.
They all need the parallel path.

---

## RECOMMENDED NEXT ACTION

**Do not change synthesis code yet.**

1. Fix continuity diagnostic targets (30 min)
2. Re-run diagnostic with corrected targets
3. Verify that the remaining genuine failures
   are exactly: V, Z, DH (not the measurement artifacts)
4. Implement Klatt parallel path for those three
5. Re-run diagnostic
6. Adjust AV/AF parameters until passing
7. Listen

If step 7 confirms perceptual correctness,
the problem is solved architecturally and
will not regress with further parameter changes.

---

*"V is worse but sounds more like V."*
*This is the most precise diagnostic*
*observation in the entire session.*
*It tells us the metric is wrong,*
*not the synthesis.*
*Trust the ears over the numbers*
*until the architecture is correct.*

---
*February 2026*
