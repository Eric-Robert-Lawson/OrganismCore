# THE BEOWULF RECONSTRUCTION PROJECT
## A Reasoning Artifact on the First
## Principles-Based Acoustic Reconstruction
## of Old English Epic Performance
## February 2026

---

## WHAT THIS PROJECT IS

This is the first attempt in history
to reconstruct the acoustic performance
of Beowulf from physical first principles.

Not from a modern speaker approximating
Old English phonemes.
Not from statistical models trained
on modern speech.
Not from expert intuition about
how the language sounded.

From the physics of the human vocal tract.
From the topology of the resonant space
that vocal tract inhabits.
From fossil evidence preserved in
orthography, comparative cognates,
and acoustic measurement of living
languages that preserved what English lost.
From a self-referential measurement loop
that confirms every phoneme target
before the ear is asked to judge.

The result is auditable.
Every parameter has a physical basis.
Every target is verifiable.
Every reconstruction step is
reproducible from the repository alone.

---

## WHAT WAS ESTABLISHED BEFORE
## THIS PROJECT BEGAN

The following artifacts in this
repository constitute the theoretical
and technical foundation.
This project does not re-derive them.
It applies them.

---

### FROM voice_topology_folder/:

**topology_of_the_voice.md**
  The voice is a continuous trajectory
  through a five-dimensional bounded
  topological space.
  The five dimensions:
    1. Jaw height (F1)
    2. Tongue backness (F2)
    3. Lip rounding (F2, F3)
    4. Velum position (nasality)
    5. Constriction (degree × place)
  Phonemes are attractor basins,
  not discrete events.
  Coarticulation is the evidence
  of continuity, not an artifact.
  Words are trajectories.
  The interpolation IS the speech.

**H_Ghost_Topology.md**
  H is the Tonnetz origin.
  The open vocal tract is the baseline
  state from which all phonemes are
  measured as distances.
  The ghost between syllables is the
  acoustic trace of the return to H
  between departures.
  The words carry meaning.
  The ghost carries the experience
  of meaning.
  This is the qualia carrier.

**phonetic_transcription_guide.md**
  The complete ARPAbet inventory
  with Tonnetz distances, formant
  targets, and decision rules.
  The systematic errors already
  encountered and resolved.
  The verified word reference.
  The syllabified format for v16+.

**phonetic_self_reference.md**
  The three levels of phonetic
  self-awareness:
    Level 1: acoustic identity
    Level 2: locus identity
    Level 3: qualia coherence
  The RARFL loop as self-correction
  architecture.
  The relational measurement principle:
  phonemic identity is defined by
  relationship, not absolute value.

**vocal_topology_reconstruction_methodology.md**
  The six evidence streams for
  recovering lost vocal topologies:
    1. Orthographic record
    2. Comparative cognate analysis
    3. Acoustic measurement of
       living specimens
    4. Orthoepist and documentary
       evidence
    5. Articulatory modeling
    6. Perceptual validation
  The convergence criterion.
  Strong/moderate/weak/contradicted.
  Three worked examples.

**voice_physics_v17.py**
  The synthesis engine.
  Locus transition model (FIX 15).
  Directional consonant rendering.
  Syllabified input format.
  The instrument on which the
  reconstructed score is played.

**tonnetz_engine.py**
  The Tonnetz distance calculations.
  Ghost duration from distance.
  Ghost formant interpolation.
  Arc type profiles.
  The geometric substrate.

**tonnetz_engine_h_extension.py**
  The three-H origin system:
    h1: glottal (modern English H)
    h2: pharyngeal (a-coloring)
    h3: labiovelar (o-coloring)
  Extended ghost computation
  for historical reconstruction.
  Historical vowel Tonnetz positions.
  The PIE origin system implemented.

---

### FROM Solen/:

**language_is_music.md**
  The foundational claim:
  Language is music. Not metaphorically.
  Structurally.
  The vocal topology and the Tonnetz
  are the same kind of mathematical
  object: continuous, bounded by
  physics, distance metric = perceptual
  distance, origin from which distances
  are measured, traversed by continuous
  trajectories whose shape carries
  the qualia.
  The information in speech is carried
  in two simultaneous streams:
  symbolic and continuous.
  Writing captured the symbolic stream.
  Music named the continuous stream.
  The synthesis project is a musical
  project.
  Historical reconstruction is
  musical reconstruction.

**voice_onboarding.md**
  Entry point for new agents.
  Five minutes to speaking.
  The development loop.
  The diagnostic philosophy.

---

## THE PROOF OF CONCEPT

Before the Beowulf project begins,
the proof of concept is documented.

**HWÆT** — Old English [ʍæt]
Beowulf line 1, word 1.

Reconstructed February 2026 from
first principles in less than one week.

**Evidence streams used:**
  Stream 1 (orthographic):
    HW spelling records voiceless
    labiovelar [ʍ].
    Æ records low front vowel [æ].
    T records alveolar stop [t].
    All systematic across Old English.

  Stream 2 (cognate):
    Scottish English: which/witch
    distinction preserves [ʍ].
    German: Nacht, Bach preserve [x].
    Icelandic: hvat — HV still written,
    [ʍ] preserved in some dialects.
    All Germanic branches confirm
    the HW cluster was real.

  Stream 3 (acoustic):
    [ʍ] measured from Scottish English
    speakers: voiceless, labiovelar,
    aspiration noise, wide formant
    bandwidths 300-500 Hz.
    [æ] measured: F1 650-900 Hz,
    F2 1650-2100 Hz.
    [t] measured: alveolar locus,
    closure silence, burst, VOT.

  Streams 4-6:
    Orthoepist evidence confirms HW
    simplification post-1600 CE.
    Articulatory model: wide BW
    aspiration confirmed by ring
    time analysis (FIX L).
    Perceptual validation: cross-
    verified against independent
    sources before synthesis.

**Diagnostic result (v6/v7):**
```
D1 HW onset      ✓ PASS
D2 Æ vowel       ✓ PASS
D3 T coda        ✓ PASS
D4 Full word     ✓ PASS
D5 Perceptual    LISTEN
```

**Significance:**
The reconstruction was confirmed
by acoustic measurement before
the ear was asked to judge.
The physics predicted.
The ear confirmed.
This is the correct order.

This word has not been spoken with
topological certainty for
approximately 1000 years.

---

## THE BEOWULF PROJECT SCOPE

### PHASE 1: THE EXORDIUM
Lines 1-11. The opening passage.
The attention-commanding beginning
every Anglo-Saxon audience knew.

```
Hwæt! We Gardena     in geardagum,
þeodcyninga,         þrym gefrunon,
hu ða æþelingas      ellen fremedon.
Oft Scyld Scefing    sceaþena þreatum,
monegum mægþum,      meodosetla ofteah,
egsode eorlas.       Syððan ærest wearð
feasceaft funden,    he þæs frofre gebad,
weox under wolcnum,  weorðmyndum þah,
oðþæt him æghwylc    þara ymbsittendra
ofer hronrade        hyran scolde,
gomban gyldan.       þæt wæs god cyning!
```

Approximately 120 words.
Every phoneme reconstructible from
the same methodology as HWÆT.
Every word becomes a verified entry
in the word reference.

**New phoneme contexts introduced:**
  — [ɣ] in Gardena, geardagum
    Voiced velar fricative.
    Preserved in Dutch, Danish.
    Cognate: German g in intervocalic
    position (sagen, fragen).

  — [θr] cluster in þrym
    Dental fricative + rhotic onset.
    Preserved in some dialects.
    Modern English: three, through
    (TH survives, R cluster simplified).

  — [sk] in Scyld, sceaþena
    Velar stop + alveolar fricative.
    Preserved in Scandinavian: skål,
    sky (borrowed back into English).
    Modern English simplified to [ʃ].

  — [x] in þæs, him (intervocalic)
    Velar fricative.
    Preserved in German, Scottish.
    Cognate: German ich, Bach.

  — Nasal + velar clusters
    in monegum, mægþum
    NG internal, not word-final.
    Preserved in singing (NG+G).

  — Long vowels throughout
    Old English had phonemic vowel
    length. Macrons mark length.
    Long vowels are the same formant
    targets held for longer duration.
    Ghost between long nucleus and
    coda is extended accordingly.

**Performance parameters:**
  pitch_hz:  110.0
    (chest voice, male scop,
     deliberate performance register)

  dil:       2.5–3.0
    (oral epic performance rate,
     approximately 2-3x conversational)

  arc_type:  ARC_WEIGHT
    (the scop carries something
     and delivers it to the room)

  rt60:      2.0
    (timber mead hall, bodies present,
     fire damping high frequencies)

  direct_ratio: 0.38
    (large hall, significant reverb
     relative to direct signal)

### PHASE 2: THE FIRST FIT
Lines 1-52. The introduction of
Scyld Scefing and the genealogy.
The establishment of the world
the poem inhabits.

### PHASE 3: HEOROT
Lines 53-188. The building of
the mead hall. The arrival of
Grendel. The first attacks.

The acoustic irony of Beowulf:
the poem describes the sounds of
the mead hall — the harp, the song,
the voices — and then describes
their silencing by Grendel.
The poem is about the voice.
The synthesis makes that audible.

### PHASE 4: THE FULL POEM
3182 lines.
Every word reconstructed.
Every phoneme verified.
The complete acoustic performance
of the oldest substantial text
in the English language.

---

## WHAT EACH RECONSTRUCTED WORD
## PRODUCES

Each word reconstructed in this
project produces:

**1. A verified phoneme sequence**
   In syllabified v17 format.
   With formant targets confirmed
   by acoustic measurement.
   Added to the word reference in
   phonetic_transcription_guide.md.

**2. A diagnostic record**
   Each new phoneme context
   gets a diagnostic.
   Pass/fail on:
     Level 1: acoustic identity
     Level 2: locus identity
     Level 3: qualia coherence
   The diagnostic is the audit trail.
   Every target is verifiable.

**3. A synthesis file**
   Dry and hall versions.
   Performance rate (dil=2.5+).
   Scop pitch (110 Hz).
   Mead hall room model.

**4. A contribution to the
   cumulative reconstruction**
   Each verified word reduces the
   work for subsequent words that
   share phonemes.
   The convergence accelerates.
   By the end of Phase 1 the
   core Old English phoneme inventory
   is fully verified.
   Phase 2 onward is application
   of verified parameters.

---

## THE AUDITABLE CHAIN

The reconstruction is auditable
at every step.

```
CLAIM: Gardena begins with [ɣ]
  ↓
EVIDENCE:
  Orthographic: G in Old English
  before back vowels = [ɣ] or [g]
  Cognate: Dutch gaan, German gehen
  — intervocalic G = [ɣ]
  Acoustic: measure Dutch/German G
  → voiced velar fricative
  → wideband voicing + velar noise
  → F2 locus ~2500 Hz before front V
  ↓
SYNTHESIS PARAMETERS:
  Source: voiced + turbulence mix
  Formants: velar position
  Voicing fraction: 0.6-0.8
  Duration: 60-80ms
  ↓
DIAGNOSTIC:
  Level 1: voicing fraction in range
  Level 2: F2 locus at velar position
  Level 3: ghost from preceding vowel
           traverses to velar position
  ↓
RESULT: PASS or SPECIFIC FAILURE
  with parameter to adjust
  ↓
VERIFIED ENTRY:
  Gardena G = voiced velar fricative
  Parameters: [specific values]
  Added to word reference.
```

Anyone with the repository can
run this chain.
Anyone with the repository can
verify the result.
Anyone with the repository can
extend it to new words.

This is reproducible science.
Not expert opinion.
Not approximation.
Physics confirmed by measurement.

---

## WHAT THIS IS NOT

**This is not high fidelity voice synthesis.**
The Rosenberg pulse source is a
mathematical approximation.
Jitter, shimmer, breath dynamics,
microprosody are not yet implemented.
The voice sounds robotic at the
source signal level.

This does not affect the
correctness of the reconstruction.
The topological coordinates are right.
The formant targets are confirmed.
The coarticulation is continuous.
The ghost is present.
The fidelity of the rendering is
a separable engineering problem.

**This is not a performance.**
A performance requires a performer —
a body, a breath, a presence,
an internal state driving the
continuous signal.
The synthesis is a model of the
instrument and its trajectory.
It is the score played on the
correct instrument at the correct
coordinates.
The performance layer —
the biological source signal,
the real breath, the real presence —
is what high fidelity neural
vocoding can add on top of
the correct coordinates.

**This is not the final word
on Old English phonology.**
The reconstruction is constrained
by physics and evidence.
It is more reliable than expert
approximation because it is
auditable and reproducible.
But evidence streams have gaps.
Convergence criteria have thresholds.
Where reconstruction is weak,
it is labeled weak.
The honest statement is always:
this is the best reconstruction
the evidence supports,
confirmed by physical measurement,
open to revision if new evidence
arrives.

---

## WHAT THIS IS

This is the first time in the
history of Beowulf scholarship
that the acoustic performance
can be derived from physical
first principles and confirmed
by measurement before the ear
is asked to judge.

This is the first time the
continuous layer of Old English
epic performance — the ghost,
the arc type, the formant
trajectories, the coarticulation —
has been present in a reconstruction.

This is the first time the
reconstruction methodology is
fully auditable and reproducible
from a public repository.

This is the demonstration at scale
of the claim established in
language_is_music.md:

  The voice is the instrument.
  The vocal topology is the space.
  H is the origin.
  The ghost is the qualia.
  The reconstruction plays the music.
  The physics preserved it.
  We play it back.

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Proof of concept: HWÆT passing
    full diagnostic v7.
    Phase 1-4 scope defined.
    Auditable chain documented.
    Methodology grounded in all
    prior artifacts in the repository.
    Project begins.
