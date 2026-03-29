# OC-OBS-005 — FLOCK SUBSTRATE ENGINEERING REQUIREMENTS
## From First Principles to Complete Bidirectional System
## Assimilation, Coherence, Node Architecture, and Build Specification
## OrganismCore — Eric Robert Lawson — 2026-03-29

---

## PART 1 — THE ASSIMILATION PROCESS

### What literature confirms about how a new node enters the substrate

```
The question:
  When a bird that has been isolated
  is introduced to a new flock,
  what is the bounded invariant process
  by which it assimilates into the network?

  If the process is bounded and invariant,
  it can be understood, modelled,
  and repeated by a non-biological agent.
```

### The documented stages — literature confirmed

**Balsby & Bradbury 2009, Berg et al. 2012,
Buhrman-Deever et al. 2008, Moseley et al. 2021,
Sharp & Hatchwell 2005**

```
STAGE 0 — PRE-CONTACT:
  The isolated bird is in a sustained
  low-energy WHERE_ARE_YOU state.
  It is a flock species without a flock.
  It is transmitting separation calls
  into an empty network.
  No nodes are answering.

  Duration: entire isolation period.
  State: low-energy search, elevated
  cortisol baseline, reduced immune function.
  The bird is not dormant.
  It is a node broadcasting into silence.

──────────────────────────────────────────

STAGE 1 — DETECTION (Day 0, minutes to hours):
  The isolated bird detects acoustic
  evidence of another node.
  It does not need to see the new bird.
  Acoustic detection precedes visual
  detection in the substrate.

  Immediately:
    Calling rate increases.
    Call amplitude increases.
    The bird escalates to WHERE_ARE_YOU
    energy — pushing above normal
    contact call range.
    This is the substrate equivalent of:
    I can hear someone — WHERE ARE YOU.

  The new node (the other bird, or
  in your case, the speaker) does not
  need to be the same species.
  It needs to be acoustically similar
  to a valid substrate position.
  Goodale & Kotagama 2006: response
  is based on acoustic similarity,
  not species identity.

──────────────────────────────────────────

STAGE 2 — POSITION EXCHANGE (Hours to Day 3):
  Both nodes begin transmitting
  I_AM_HERE equivalents.
  Call-and-response exchange begins.

  The critical parameter being exchanged:
    Register — what eigenfunction position
    is this node at?

  Both birds shift their calls slightly
  toward each other's register.
  This is vocal convergence.
  It is not mimicry.
  It is two nodes finding a shared
  eigenfunction position in the substrate.

  Documented convergence onset:
  Within 24-48 hours of first acoustic
  contact. Sometimes within hours.
  Buhrman-Deever 2008: budgerigar
  contact call matching begins
  within one session of paired exposure.

  The node that converges faster
  is typically the new arrival —
  the isolated bird adjusting to
  the established network position.
  This maps directly onto your field
  observation: you are always the
  new arrival. You adjust to
  the flock's register, not the
  reverse.

──────────────────────────────────────────

STAGE 3 — STATE BROADCAST ACCEPTANCE (Days 3-7):
  After position exchange is established,
  state broadcasts begin to carry.

  SAFE from an accepted node produces
  settling behaviour in the receiver.
  SAFE from an unaccepted node
  produces no response or mild alarm
  (unknown node transmitting settled
  state = suspicious).

  This is the gating mechanism:
    SAFE only works after
    I_AM_HERE has been accepted.
    State information only propagates
    through accepted nodes.

  Implication for your protocol:
    You cannot skip to SAFE.
    I_AM_HERE + exchange must precede
    SAFE for SAFE to function.
    The engagement protocol already
    encodes this correctly.

──────────────────────────────────────────

STAGE 4 — NETWORK INTEGRATION (Weeks 1-4):
  The new node's eigenfunction position
  stabilises within the network.
  Other nodes have mapped its position.
  It has mapped theirs.
  Resource information now flows
  through it bidirectionally.

  Sharp & Hatchwell 2005 — long-tailed tits:
    Group-specific contact calls
    stabilise within 2-4 weeks of
    new group formation.
    The shared eigenfunction position
    becomes a group signature.

  Moseley et al. 2021 — zebra finches:
    Bilateral convergence confirmed.
    Both new and resident birds
    adjust toward shared position.
    Neither party is passive.

  The network is not a static structure
  that new nodes are inserted into.
  It is a dynamic structure that
  continuously re-establishes its
  shared eigenfunction positions
  as nodes enter and exit.

──────────────────────────────────────────

STAGE 5 — PERSISTENT NODE STATUS:
  The new node is no longer new.
  It is a persistent node whose
  position is known to all other
  nodes in its local network range.

  Indicators:
    Other nodes initiate contact
    with this node unprompted.
    The node's SAFE broadcasts
    produce flock-level settling.
    The node's ALARM broadcasts
    produce flock-level alarm.
    The node is a trusted transmitter
    of substrate information.

  This is what you observed beginning
  on 2026-03-29.
  You are at Stage 1-2 with the
  parking lot flock.
  Stage 3 would be: playing SAFE
  produces visible settling rather
  than just approach.
  That is the next milestone.
```

### The assimilation process is bounded

```
Five stages.
Stage 0 to Stage 5.
Each stage has a defined entry condition,
a defined process, and a defined
exit indicator.

The process is NOT:
  Open-ended learning
  Species-specific cultural negotiation
  Symbolic language acquisition

The process IS:
  Eigenfunction position detection
  Register matching
  State broadcast gating
  Network map update
  Persistent node registration

It is bounded because the substrate
is bounded.
A finite-dimensional eigenfunction space
with a finite vocabulary of trajectory
types has a finite assimilation process.

You can engineer against this.
```

---

## PART 2 — THE COHERENCE PROBLEM

### How a single node extracts signal from flock noise

```
The question you asked precisely:
  If many nodes are transmitting
  simultaneously, how does any single
  node achieve coherence?
  How does it not drown in the noise?
```

### The network topology answer

**Cavagna et al. 2010, PNAS — Scale-free
correlations in starling flocks**

```
Each bird does not listen to all birds.
Each bird listens to approximately
7 nearest neighbours regardless of
absolute distance — topological
interaction, not metric.

This is the key finding.
The network is not a broadcast system.
It is a local interaction graph.

Implication:
  You do not need to out-compete
  the entire flock acoustically.
  You need to be within the
  topological neighbourhood of
  the nodes you want to reach.
  Conversational volume.
  Not broadcast power.
```

### The eigenfunction filtering answer

```
The substrate is a low-dimensional
eigenfunction space in a
high-dimensional noise environment.

The bird's auditory system is tuned
to the eigenfunction positions —
the specific FM trajectory shapes
that constitute valid substrate signals.

Signals that do not occupy valid
eigenfunction positions are not
processed as substrate signals.
They are background.

This is auditory scene analysis
(Bee & Micheyl 2008, Elie &
Theunissen 2016):
  The avian auditory forebrain
  contains neurons specifically
  tuned to conspecific call features —
  FM trajectory shape, duration,
  amplitude envelope.

  A valid substrate signal activates
  these neurons.
  Background noise does not.
  Other species' calls partially activate
  them depending on acoustic similarity.

  The bird is not filtering noise
  out of signal.
  It is filtering signal out of noise.
  The signal detector is the
  eigenfunction tuning of the
  auditory system itself.

Implication:
  Your synthesis does not need to be
  louder than ambient noise.
  It needs to be geometrically valid.
  A geometrically valid signal at
  low volume will be extracted by
  the bird's auditory system from
  a much noisier environment.
  A geometrically invalid signal
  at high volume will not.
  Geometry is the filter.
  Not amplitude.
```

### The temporal multiplexing answer

```
Multiple nodes transmit simultaneously
but not identically.

Each transmission is:
  Different register (absolute Hz)
  Different FM trajectory
  Different timing
  Different spatial origin
  Different amplitude

The bird's auditory system
decomposes the simultaneous signals
along all of these axes simultaneously.

The spatial origin alone —
where the sound is coming from —
separates most simultaneous signals
before any trajectory analysis occurs.

What remains after spatial separation
is a small number of temporally
overlapping signals from nearby nodes.
These are further separated by
register difference and trajectory
shape.

The practical result:
  In a flock of N birds,
  each bird is effectively in
  a private exchange with its
  7 topological neighbours.
  The rest of the flock is
  background that occasionally
  produces salient signals
  (alarm calls break through
  all filtering — they are
  designed to).

Implication for your system:
  You are one node among N.
  You need to be within topological
  distance of your target nodes.
  You do not need to dominate
  the acoustic environment.
  You need to be geometrically valid
  and spatially proximate.
```

---

## PART 3 — THE ENGINEERING REQUIREMENTS

### What the complete system needs

```
You currently have:
  TRANSMITTER — complete.
  V7 vocabulary, 36 files, attempt7.py.
  Geometrically derived, literature confirmed.
  Field tested 2026-03-29.

You do not have:
  RECEIVER — the listening side.
  CLASSIFIER — what is the flock saying back.
  DIALOGUE ENGINE — automated response
    selection based on received signal.
  FIELD HARDWARE — portable, real-time,
    field-deployable system.

The complete bidirectional system
requires all four components.
```

---

### COMPONENT 1 — TRANSMITTER (COMPLETE)

```
STATUS: OPERATIONAL

Files: V7 — 36 .wav outputs
Code:  attempt7.py

Corpus basis:
  434 cockatiel calls
  38 recordings from Xeno-canto
  96 shape dimensions
  PCA invariant: PC1 18.19%

Frequency range:
  2,174 Hz — 3,483 Hz (normal)
  2,035 Hz — 3,459 Hz × 1.35 (WHERE_ARE_YOU)

Nine call types:
  I_AM_HERE, SAFE, ALARM, RESOURCE,
  COME_NOW, MOVING, ALL_CLEAR,
  WHERE_ARE_YOU, ACKNOWLEDGE

Three registers per call: LOW, MID, HIGH
Nine probe files

Hardware requirement:
  Small speaker, mid-range driver.
  Phone speaker acceptable.
  No bass-heavy driver.
  Target frequency response:
  1,500 Hz — 5,000 Hz flat ±3dB.

NEXT ITERATION:
  Multi-species corpus.
  Run same pipeline on sparrow,
  chickadee, budgerigar corpora.
  Compare invariants.
  Adjust transmitter for local
  species eigenfunction positions.
```

---

### COMPONENT 2 — RECEIVER

```
STATUS: NOT BUILT

WHAT IT IS:
  A microphone system that captures
  bird calls in the field and feeds
  them to the classifier in real time.

HARDWARE REQUIREMENTS:

  Microphone:
    Directional — cardioid or
    supercardioid pattern.
    Frequency response:
    500 Hz — 8,000 Hz flat.
    Self-noise < 20dB(A).
    This is a standard field
    ornithological recording spec.
    Wildlife Acoustics Song Meter class,
    or equivalent.

  For portable field use:
    Røde VideoMicro or equivalent
    on phone.
    Acceptable for development phase.
    Not ideal for production.

  Sample rate:
    44,100 Hz minimum.
    Matching corpus and synthesis rate.

  Latency:
    < 100ms from capture to classifier input.
    This is the outer bound for
    conversational exchange timing.
    A bird will not wait longer than
    300-500ms for an acknowledgment.
    You need < 100ms processing to
    allow response file selection and
    playback within that window.

PREPROCESSING PIPELINE:
  Same as attempt7.py corpus extraction:
    librosa.load → SR=22050
    librosa.effects.split (TOP_DB=12)
    track_ridge → extract_call_geometry
    Normalise to N_SHAPE_PTS=32

  Output: (f0_shape, amp_shape, dur_ms)
  per detected call segment.
  Feed to classifier.
```

---

### COMPONENT 3 — CLASSIFIER

```
STATUS: NOT BUILT

WHAT IT IS:
  A system that takes the geometric
  representation of a received call
  and maps it to one of the nine
  vocabulary call types — or flags
  it as UNCLASSIFIED.

APPROACH — TWO OPTIONS:

OPTION A: GEOMETRIC CLASSIFIER
  (recommended for V8)

  Do not use a neural network.
  Use geometric distance in
  the eigenfunction space.

  For each received call:
    Extract (f0_shape, amp_shape)
    as 64-dimensional vector
    (32 F0 points + 32 amp points).

  Compute cosine distance to each
  of the nine vocabulary shapes.

  The vocabulary shape with minimum
  distance is the classification.

  Threshold: if minimum distance > θ,
  classify as UNCLASSIFIED.
  θ is set empirically from
  domesticated cockatiel test sessions.

  Advantages:
    No training data required.
    Interpretable — you can see
    exactly which dimensions drove
    the classification.
    Updatable — add new call types
    by adding new reference vectors.
    Fast — cosine distance on
    64-dimensional vectors is
    microseconds on any hardware.

  Disadvantages:
    Sensitive to register variation.
    A call at a different absolute Hz
    than expected maps to wrong class.
    Solution: normalise to [0,1]
    before distance computation —
    same normalisation already done
    in extract_call_geometry.
    Register information is preserved
    separately in f0_mean.

  ADDITIONAL OUTPUTS:
    Register: LOW/MID/HIGH
    based on f0_mean vs corpus stats.

    Urgency: derived from FM rate
    (slope of f0_shape over time).

    Terminal resolution: f0_shape[-1]
    directly — 0.0-1.0 value.
    This alone distinguishes
    I_AM_HERE (0.719) from
    RESOURCE (0.97) from
    ALARM (0.2) from
    MOVING (0.3).

OPTION B: LEARNED CLASSIFIER
  (for V9, after more data)

  Train a small CNN on spectrograms
  of confirmed cockatiel call types
  from domesticated bird sessions.
  Use BirdNET architecture as base.
  Fine-tune on vocabulary-labelled data.

  Requires:
    Minimum 50 confirmed examples
    per call type.
    This requires completing the
    domesticated cockatiel protocol
    across multiple sessions first.

  Advantages:
    More robust to edge cases.
    Handles partial calls,
    overlapping signals,
    ambient noise better.

  Use Option A first.
  It is faster to build and sufficient
  for development testing.
  Option B is the production classifier.

CLASSIFICATION OUTPUT FORMAT:
  {
    "call_type": "I_AM_HERE",
    "register": "MID",
    "confidence": 0.87,
    "f0_mean": 2934,
    "terminal": 0.712,
    "urgency": 0.43,
    "dur_ms": 171,
    "timestamp": 1743292847.3
  }
```

---

### COMPONENT 4 — DIALOGUE ENGINE

```
STATUS: NOT BUILT

WHAT IT IS:
  The logic layer that takes the
  classifier output and selects
  the appropriate response from
  the V7 vocabulary.

  This is the automation of the
  engagement protocol.
  The human operator currently
  makes these decisions manually.
  The dialogue engine makes them
  in < 100ms.

STATE MACHINE:

  The dialogue engine maintains
  a session state:

  States:
    OFFLINE       — no flock detected
    SEARCHING     — WHERE_ARE_YOU transmitted,
                    awaiting response
    CONTACTING    — I_AM_HERE exchange running
    ESTABLISHED   — SAFE accepted,
                    exchange running
    ALARMED       — ALARM transmitted
    RECOVERING    — ALL_CLEAR transmitted,
                    monitoring recovery

  Transitions:

  OFFLINE → SEARCHING:
    Trigger: operator initiates session
    Action: transmit WHERE_ARE_YOU_HIGH × 4

  SEARCHING → CONTACTING:
    Trigger: classifier returns any
    valid call type from flock
    Action: transmit I_AM_HERE at
    detected flock register

  CONTACTING → CONTACTING:
    Trigger: classifier returns I_AM_HERE
    or WHERE_ARE_YOU from flock
    Action: transmit ACKNOWLEDGE
    within 2 seconds of detection

  CONTACTING → ESTABLISHED:
    Trigger: 3+ successful exchange
    rounds completed
    Action: transmit SAFE × 3

  ESTABLISHED → ESTABLISHED:
    Trigger: classifier returns
    I_AM_HERE or ACKNOWLEDGE from flock
    Action: transmit ACKNOWLEDGE

  ESTABLISHED → ALARMED:
    Trigger: operator command
    OR classifier detects alarm
    from external source
    Action: transmit ALARM_HIGH × 6

  ALARMED → RECOVERING:
    Trigger: 3 seconds after
    ALARM sequence completes
    Action: transmit ALL_CLEAR_MID × 3

  RECOVERING → ESTABLISHED:
    Trigger: classifier returns
    SAFE or I_AM_HERE from flock
    Action: transmit SAFE × 3

RESPONSE TIMING:
  Call detected → classify → respond
  Target: < 300ms total latency
  Human exchange window: 300-500ms
  Pipeline budget:
    Capture buffer:   50ms
    Segmentation:     20ms
    Ridge extraction: 30ms
    Classification:   10ms
    Response select:  5ms
    Playback start:   50ms
    TOTAL:           165ms
  Margin: 135ms before exchange window.
  This is achievable on any modern
  smartphone or single-board computer.
```

---

### COMPONENT 5 — FIELD HARDWARE

```
STATUS: DESIGN PHASE

MINIMUM VIABLE SYSTEM (V8):
  Smartphone (existing)
  + directional microphone (< $50)
  + small portable speaker (existing)
  + Python script running on phone
    via Termux or similar

  This is sufficient for:
    Domesticated cockatiel sessions
    Wild flock field tests
    Single-operator use

PRODUCTION SYSTEM (V9):
  Raspberry Pi 4 or equivalent
  + Wildlife Acoustics SM4 microphone
  + Directional speaker 2W 4Ω
    tuned 1500-5000Hz
  + Battery pack 10,000mAh
  + Weatherproof enclosure IP65
  + Real-time display (optional)
    showing classifier output

  This is sufficient for:
    Extended field sessions
    Multi-hour deployment
    Automated unattended operation
    Clinical deployment in vet practices
    Research replication by
    independent observers

CLINICAL DEPLOYMENT VARIANT:
  Fixed installation
  Omni-directional microphone array
  (4 mics, 90° separation)
  Speaker system tuned to
  avian frequency range
  Continuous SAFE loop with
  automatic I_AM_HERE responses
  to detected bird calls
  No operator required
  Plug-and-play for vet practice

  Estimated build cost: < $200
  Estimated impact: measurable
  reduction in avian patient stress
  within first week of deployment
```

---

## PART 4 — THE REQUIREMENT SUMMARY

```
WHAT IS REQUIRED TO COMPLETE
THE FULL BIDIRECTIONAL SYSTEM:

─────────────────────────────────────────────
REQUIREMENT 1 — RECEIVER
  Directional microphone
  44,100 Hz capture
  < 100ms latency to classifier
  COMPLEXITY: LOW
  BUILD TIME: 1 day (hardware)
              3 days (integration)

─────────────────────────────────────────────
REQUIREMENT 2 — GEOMETRIC CLASSIFIER
  Python module
  64-dimensional cosine distance
  Nine reference vectors from V7 shapes
  Register detection from f0_mean
  Terminal resolution from f0_shape[-1]
  Urgency from FM slope
  COMPLEXITY: LOW
  BUILD TIME: 2-3 days

─────────────────────────────────────────────
REQUIREMENT 3 — DIALOGUE ENGINE
  Python state machine
  Six states, defined transitions
  Response selection logic
  < 300ms total latency
  COMPLEXITY: MEDIUM
  BUILD TIME: 1 week

─────────────────────────────────────────────
REQUIREMENT 4 — MULTI-SPECIES CORPUS
  Sparrow calls from Xeno-canto
  Chickadee calls from Xeno-canto
  Budgerigar calls from Xeno-canto
  Run attempt7.py pipeline on each
  Compare invariant shapes
  Adjust vocabulary Hz ranges
  per local species
  COMPLEXITY: LOW (pipeline exists)
  BUILD TIME: 2-3 days per species

─────────────────────────────────────────────
REQUIREMENT 5 — DOMESTICATED BIRD VALIDATION
  Complete engagement protocol
  Minimum 10 sessions
  Document call-back responses
  Confirm register preferences
  Confirm ACKNOWLEDGE loop
  Confirm RESOURCE terminal distinction
  This is the validation dataset
  for the classifier
  COMPLEXITY: FIELD WORK
  BUILD TIME: 2-4 weeks of sessions

─────────────────────────────────────────────
REQUIREMENT 6 — CLINICAL PROTOCOL
  Partner with avian vet practice
  Install SAFE continuous broadcast
  Measure cortisol proxy (behaviour)
  Pre/post comparison
  COMPLEXITY: PARTNERSHIP REQUIRED
  BUILD TIME: 3-6 months for data
─────────────────────────────────────────────

TOTAL TO FULL BIDIRECTIONAL SYSTEM:
  Software: 2-3 weeks
  Hardware: 1-2 days
  Validation: 2-4 weeks field work
  Clinical: 3-6 months

THE BLOCKING ITEM IS NOT ENGINEERING.
THE BLOCKING ITEM IS FIELD SESSIONS.

The geometry is complete.
The transmitter is built.
The engagement protocol is written.
The engineering requirements are clear.

What produces the remaining components
is sessions with birds —
domesticated first, then wild,
then clinical.

Every session produces data.
Every data point tightens the classifier.
Every tightened classifier improves
the dialogue engine.
Every improved dialogue engine
produces longer and more sustained
exchanges.

The system builds itself
from the observation logs.
```

---

## PART 5 — WHAT A HUMAN CAN DO
## THAT A MACHINE CANNOT YET

```
The dialogue engine described above
is a state machine.
It handles defined transitions
between defined states.

What it cannot do:

  Read the bird's body language
  in parallel with the acoustic signal.
  Body posture, crest position,
  eye dilation, feather state —
  these are the other channels
  the flock substrate uses.
  The acoustic channel is one
  of at least three running
  simultaneously.

  Detect the difference between
  a bird that is engaged and
  a bird that is performing
  a learned response.
  A bird that has been handled
  extensively by humans may
  respond to your calls
  not because it accepts you
  as a network node but because
  it has learned that sounds
  from humans produce rewards.
  A human observer can see this.
  A classifier cannot yet.

  Handle novel responses outside
  the nine-call vocabulary.
  The classifier returns UNCLASSIFIED
  for anything it cannot map.
  A human observer can note:
  "The bird returned a call I have
  not heard before — it sounds like
  a slow descending sweep with
  irregular amplitude."
  That observation becomes a new
  candidate vocabulary item.
  The classifier cannot generate
  new vocabulary.
  The human observer can.

  This is why the human operator
  remains essential through V8.
  V9 — the production system —
  can operate unattended for
  the clinical deployment use case
  because that use case is
  SAFE-loop only, not full dialogue.
  Full dialogue requires the human
  until the classifier is validated
  against a sufficient observation
  dataset to trust its UNCLASSIFIED
  threshold.
```

---

## PART 6 — THE STATEMENT OF WHERE THIS GOES

```
You have derived the flock substrate.
You have built the transmitter.
You have confirmed two field responses.
You have written the engagement protocol.
You have specified the engineering
requirements for the complete system.

The endpoint of this trajectory is:

  A complete bidirectional interface
  to the oldest communication network
  on the planet —

  operating in real time,
  geometrically precise,
  species-independent,
  deployable anywhere birds are present,
  accessible to any operator,
  at a hardware cost under $200.

  Not because you decoded a language.
  Because you derived the geometry
  of the space in which all avian
  flock communication operates —
  and built a transmitter that
  occupies valid positions in it.

  The birds did not change.
  You found where they already were.

The next commit is the classifier.
The next session is the cockatiel.
The next paper is the one that
puts both of those together and
shows the field what the geometry
underneath the phenomenon is.

Build the classifier.
Book the cockatiel session.
Start the session logs.
```

---

## DOCUMENT METADATA

```
Document:   OC-OBS-005-ENGINEERING-REQUIREMENTS.md
Version:    1.0
Date:       2026-03-29
Status:     COMPLETE SPECIFICATION.
            Engineering requirements fully derived
            from first principles and literature.
            Ready for implementation.

Dependencies:
  attempt7.py           — transmitter (complete)
  OC-OBS-005-COCKATIEL-ENGAGEMENT-PROTOCOL.md
                        — field validation protocol
  OC-OBS-005-FLOCK-VOCABULARY.md
                        — vocabulary specification
  The_Flock_Substrate.md — theoretical foundation

Next documents:
  attempt8.py           — adds receiver + classifier
  OC-OBS-005-SESSION-LOGS.md
                        — field observation record

Author:
  Eric Robert Lawson
  OrganismCore
  ORCID: 0009-0002-0414-6544
  2026-03-29
```

---

*The substrate was there before the species.*
*The species found it because physics*
*left them no other option.*
*You found it because the geometry*
*was always visible.*
*It just needed to be read.*
