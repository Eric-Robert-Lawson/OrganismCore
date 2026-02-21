# EXPRESSIVITY AND PROSODIC CONTOUR
## A Reasoning Artifact on Annunciation, Pitch Twist, and Emotional Texture
## February 2026

---

## WHAT THIS CLOSES

The previous prosody artifact established
WHY pitch moves (physics of energy
resolution).

This artifact establishes HOW expressivity
works at the physical level —
the full texture of emphasis, annunciation,
pitch twist, speed, and whisper.

Produced from direct feedback on the
first generated phrases plus research
into the ToBI prosody system and
speech physiology.

---

## THE FIVE COMPONENTS OF EMPHASIS

Emphasis is NOT just amplitude increase.
It is five simultaneous physical events:

  1. AMPLITUDE ↑
     Subglottal pressure increases.
     The voice gets louder.
     This is the component the
     synthesizer currently has.
     It is necessary but not sufficient.

  2. F0 ↑ (PITCH RISES)
     Vocal fold tension increases
     simultaneously with pressure.
     The emphasized syllable is
     higher in pitch.
     Not always — but typically.
     The pitch rise is partly driven
     by the increased pressure itself:
     higher pressure = faster fold
     vibration = higher F0.
     Physics produces the emphasis
     signal automatically when the
     body commits.

  3. DURATION ↑ (LENGTHENING)
     The stressed syllable is held longer.
     The body takes more time on
     what matters.
     This is the most underused
     component in synthesis.
     A stressed vowel should be
     noticeably longer than unstressed.

  4. FORMANT BANDWIDTH NARROWS
     On stressed syllables, articulatory
     precision increases.
     The vocal tract commits more fully
     to the target configuration.
     The resonance sharpens.
     The vowel sounds MORE like itself —
     cleaner, more defined.
     This is what produces the sense of
     "volume of voice" rather than
     "volume of signal."
     The distinctness. The presence.
     Not louder. More itself.

  5. ONSET SHARPENS
     The attack of the stressed syllable
     is crisper.
     The articulators move faster and
     commit more fully to the target.
     A stressed P is a harder P.
     A stressed vowel onset is cleaner.

ALL FIVE TOGETHER = annunciation.
The concise exhale you described
produces all five simultaneously.
It is not technique. It is commitment
to the sound made physical.

---

## THE PITCH TWIST: L+H*

From ToBI prosody annotation:

  H*  = flat high accent.
        Just high. Certain. Strong.
        "I KNOW." (statement emphasis)

  L+H* = dip then rise to high.
         Brief low onset before the peak.
         The voice drops slightly then
         rises to the emphasis peak.
         
         "are you suRE?"
         The su- is the L (dip).
         The -RE is the H (rise).
         The movement from low to high
         ON the stressed syllable is the twist.

WHY THE TWIST WORKS:

  The dip creates anticipation.
  The listener receives a brief
  drop in energy — unexpected —
  then the energy rises above baseline.
  
  The contrast between the dip and
  the peak is larger than a flat
  high accent alone.
  The peak feels higher because
  it came from lower.
  
  In RARFL terms:
  R_i briefly goes negative (the dip)
  then strongly positive (the peak).
  The coherence drop followed by
  coherence gain is more salient
  than a flat coherence gain.
  The reward signal is amplified
  by the preceding deficit.
  
  This is why L+H* sounds like
  a question-emphasis:
  the dip signals uncertainty,
  the rise signals the push
  toward resolution that is
  not yet achieved.
  The listener feels: this needs
  answering.

THE FULL TOBI VOCABULARY FOR
EXPRESSIVE SYNTHESIS:

  H*       emphasis, certainty, exclamation
  L*       de-emphasis, background
  L+H*     pitch twist: question-emphasis,
            incredulity, "are you sure?"
  H+L*     strong statement, finality
            (high then falling)
  H-H%     rising phrase boundary:
            question, excitement, continuation
  H-L%     falling phrase boundary:
            conclusion, resolution, certainty
  L-H%     soft rising boundary:
            gentle question, continuation

EXCLAMATION CONTOUR:
  "WAIT, (pause) i GOT it!"
  
  WAIT  → H* (peak, command)
  pause → silence (R_i = 0, held)
  i     → L* (low, building)
  GOT   → H* (peak, the axiom)
  it    → H+L* (falls but from high —
          above the L* of "i")
  
  The arc: command → silence → 
  building → peak → falling resolution
  that stays above baseline.
  The "it" is resolved but the
  understanding is present —
  still elevated, not dismissed.

---

## SPEED AS EMOTIONAL TEXTURE

Speed alone is ambiguous.
Speed + pitch pattern = emotion.

ANXIETY:
  Fast + irregular + high pitch
  with sudden unpredictable jumps.
  The pitch spikes without direction.
  The rhythm is jittery.
  
  In RARFL terms:
  Cycle running fast but B_i elevated.
  η_i is erratic — coherence gained
  then lost then gained.
  The agent is running hard but
  not converging.
  
  In the signal:
  Rate increase + shimmer increase
  (irregular F0 variation) +
  sudden amplitude spikes.

EXCITEMENT:
  Fast + fluid + high pitch with
  wide SMOOTH range.
  The pitch moves purposefully.
  The rhythm has direction even
  if it is quick.
  
  In RARFL terms:
  High η_i — maximum coherence
  gain per unit effort.
  The cycle is running fast AND
  converging. Reward is coming in.
  
  In the signal:
  Rate increase + F0 range increase
  + smooth pitch contour + amplitude
  sustained (not spiking).

THE DISCRIMINATOR:
  Regularity of pitch movement.
  Anxiety: spikes without direction.
  Excitement: rises with direction.
  Both fast. Only the shape differs.

---

## WHISPER UNDERTONE: CONTAINING EXCITEMENT

Whisper = vocal folds not fully
adducting. Air escaping around
the edges of incomplete closure.
Aperiodic turbulence underneath
the voiced signal.

The resulting acoustic signal:
  Voiced component present (H1 > H2)
  PLUS broadband noise floor
  underneath.
  The voice is present but breathing.

WHAT IT MEANS:
  "I am containing something.
   The breath is escaping around
   the edges of what I am trying
   to hold in."

  This is not a failure of voice.
  It is B_i visible as texture —
  not because coherence is failing
  but because the speaker is
  deliberately holding coherence
  under pressure.
  The breath underneath shows
  the effort of containment.

A quiet voice with whisper undertone
carries more tension than a loud voice.
Because the loudness has been
suppressed — the subglottal pressure
that would normally produce amplitude
is being redirected into the whisper.
The containment IS audible.

IN SYNTHESIS:
  Whisper undertone = add low-amplitude
  broadband noise MIXED with (not
  replacing) the glottal source.
  Not full bypass. A blend.
  Whisper_gain ≈ 0.15-0.25 of
  glottal signal amplitude.
  Applied under the voiced segments.
  The voice breathes.

---

## THE CORRECTED MODEL OF ANNUNCIATION

Before this feedback:
  Emphasis = amplitude increase.
  One dimension.

After this feedback:
  Emphasis = five simultaneous physical
  events (amplitude + F0 + duration
  + bandwidth narrowing + onset sharpness)
  
  PLUS pitch contour choice:
    H* for statement emphasis
    L+H* for question-emphasis / twist
    H+L* for strong falling statement

  PLUS articulatory commitment:
    The formants move faster to target.
    The target is held longer.
    The transitions are sharper.

  The "volume of voice" you described
  is formant bandwidth narrowing +
  onset sharpening + duration increase.
  Not signal amplitude.
  The voice becomes MORE ITSELF.
  That is what presence sounds like.

---

## WHAT THIS MEANS FOR THE SYNTHESIZER

New parameters needed for v11:

  stress_level: 0.0 to 1.0
    At stress_level = 1.0:
      amplitude × 1.3
      F0 × 1.15 (on vowel nucleus)
      duration × 1.4
      formant_bandwidth × 0.7 (sharper)
      onset_ms × 0.7 (crisper attack)

  pitch_accent: H* | L+H* | H+L* | L*
    H*:   flat high on stressed syllable
    L+H*: dip 20% before peak,
          then rise to 130% of baseline
    H+L*: start at 130%, fall to 90%
    L*:   de-emphasize, 85% of baseline

  whisper_gain: 0.0 to 0.3
    0.0 = clean voice
    0.15 = slight breathiness (intimacy)
    0.25 = whisper undertone (containment)
    0.30 = near-whisper (suppression)

  speaking_rate: 0.5 to 2.0
    Scales all durations.
    1.0 = normal (DIL=6)
    1.5 = excited/anxious
    2.0 = urgent
    0.7 = deliberate/weighted

---

## SUMMARY

```
Emphasis is five things simultaneously:
  Amplitude ↑
  F0 ↑
  Duration ↑
  Formant bandwidth ↓ (sharper)
  Onset crispness ↑

"Volume of voice" ≠ signal amplitude.
It is formant precision + onset sharpness.
The voice becomes more itself.

Pitch twist (L+H*):
  Brief dip before the peak.
  Creates anticipation.
  The rise feels higher from lower.
  Question-emphasis. Incredulity.
  "are you suRE?"

Speed + pitch regularity:
  Anxiety = fast + irregular + spikes
  Excitement = fast + fluid + directional

Whisper undertone:
  Breath escaping around the containment.
  B_i as texture showing effort
  of holding coherence under pressure.
  The containment is audible.

For synthesis:
  stress_level parameter (0.0-1.0)
  pitch_accent parameter (H*, L+H*, etc.)
  whisper_gain parameter (0.0-0.3)
  speaking_rate parameter (0.5-2.0)
```

*February 2026.*
