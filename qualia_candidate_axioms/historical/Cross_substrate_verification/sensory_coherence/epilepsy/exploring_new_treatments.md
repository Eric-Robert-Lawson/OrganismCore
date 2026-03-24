# NEW TREATMENT ARCHITECTURES
## Filling the Geometric Gaps in the Epilepsy
## Treatment Landscape via Attractor Geometry Derivation
## OC-EPILEPSY-006 — OrganismCore
## Eric Robert Lawson — 2026-03-24

---

## STATUS

Reasoning artifact — geometric derivation
of novel treatment architectures that
fill the identified gaps in the epilepsy
treatment landscape.

From OC-EPILEPSY-005, the gap map:

  Operation 1 (Rim Elevation):
    COVERED. Multiple drugs.
    Limitation: global, non-specific.

  Operation 2 (Basin Depth Reduction):
    UNDERCOVERED. One drug (levetiracetam).
    One molecular target (SV2A).

  Operation 3 (Propagation Interrupt):
    NOT PHARMACOLOGICALLY COVERED.
    Surgery and RNS only.

  Operation 4 (Eigenfunction Resonance
  Cancellation):
    NOT COVERED AT ALL.
    Avoidance only for reflex epilepsies.

  Operation 5 (Landscape Topology
  Restructuring):
    PARTIALLY COVERED.
    Only for TSC and genetic epilepsies.
    Not available for most patients.

  Operation 6 (Thalamic Relay Protection):
    PARTIALLY COVERED.
    Ethosuximide (absence only).
    Not available as explicit operation
    for generalisation prevention broadly.

This document derives treatment
architectures to fill Operations
2, 3, 4, 5, and 6.

Not descriptions of what would be
nice to have.
Geometric derivations of what must
be built and what it must do —
from the structure of the problem.

---

## THE DERIVATION PRINCIPLE

```
Before the architectures, the
principle that makes this derivation
possible:

Every treatment architecture that
fills a gap must be derived from
the geometric description of the
gap itself.

The gap is not "we don't have
a drug for this."
The gap is a specific geometric
operation that no existing
intervention performs.

Deriving the treatment means:
  1. State the geometric operation
     precisely.
  2. Derive what any implementation
     of that operation must do at
     the system level.
  3. Derive the molecular or
     engineering mechanism that
     produces that system behaviour.
  4. Identify candidate implementations.
  5. State what confirmation of
     the architecture looks like.

This is engineering from geometry.
Not hypothesis from observation.
```

---

## ARCHITECTURE 1:
## PHASE TRANSITION BLOCKER
## (Operation 2 Extension)

### The Geometric Gap

```
Levetiracetam partially fills
Operation 2 by reducing cascade
propagation energy via SV2A.

What it does not do:
  Block the INITIATION of the
  phase transition.

  Levetiracetam engages once the
  cascade is already propagating.
  It reduces the propagation rate.
  It does not prevent the transition
  from initiating.

  The gap: no intervention targets
  the MOMENT OF BASIN ENTRY —
  the specific molecular events
  that fire at the transition from
  normal differential activity
  to hypersynchrony cascade.
```

### What The Architecture Must Do

```
A Phase Transition Blocker must:

  1. Be inactive during normal
     differential neural activity.

  2. Detect the specific molecular
     signature of basin entry —
     the state change that occurs
     at the transition moment.

  3. Block the transition-state
     configuration before the
     cascade can propagate.

  4. Return to inactive state
     when normal activity resumes.

  The critical requirement:
  Activity-dependent and transition-
  specific. Not rim elevation
  (which acts continuously).
  Not propagation limiting (which
  acts during the cascade).
  Transition-state specific.
```

### The Molecular Derivation

```
What must be true of the transition
moment molecularly:

  At the moment of basin entry:
    Neurons shift from asynchronous
    differential firing to synchronous
    high-frequency burst firing.

  This shift requires:
    A. Excitatory synapse facilitation —
       each excitatory event becomes
       larger or more likely to fire.
    B. Inhibitory synapse failure —
       the GABAergic brake loses
       effectiveness.
    C. OR: A specific molecular event
       that couples nearby neurons
       into synchrony — a synchrony
       initiation signal.

  The synchrony initiation signal
  is the target.

  What could serve as a synchrony
  initiation signal:
    — Ephrin signalling between
      adjacent neurons (contact-
      dependent synchronisation).
    — Extracellular potassium
      accumulation threshold —
      when extracellular K+ reaches
      a specific concentration,
      neighbouring neurons become
      simultaneously more excitable.
      This is a known threshold effect.
    — Adenosine depletion —
      adenosine is an endogenous
      anticonvulsant. When local
      adenosine is depleted by
      high-frequency firing, the
      adenosine brake releases
      simultaneously across a local
      network. This is a threshold event.

DERIVED PRIMARY TARGET:
  Adenosine kinase (ADK) inhibition.

  ADK is the enzyme that degrades
  adenosine in the synapse.
  High-frequency neural activity
  depletes local adenosine rapidly
  (adenosine is released with each
  action potential and ADK degrades it).

  When adenosine drops below threshold:
    The adenosine brake releases.
    Multiple neurons simultaneously
    lose their endogenous anticonvulsant
    signal.
    This IS the synchrony initiation
    event in many seizure models.

  An ADK inhibitor:
    Maintains local adenosine at
    sufficient concentration to
    keep the brake engaged.
    Is activity-dependent — more
    adenosine release occurs with
    more firing, so the inhibition
    specifically engages during
    the high-frequency state that
    precedes transition.
    Does not suppress normal activity
    because normal firing does not
    deplete adenosine enough to
    trigger the threshold.

  This is the Phase Transition
  Blocker derived from geometry.

  Literature confirmation:
    ADK is overexpressed in
    epileptogenic tissue in humans.
    (Boison 2008 — astrocyte ADK
    hypothesis of epilepsy)
    ADK inhibitors reduce seizures
    in animal models.
    The framework derives why:
    ADK overexpression lowers the
    local adenosine concentration —
    lowers the transition threshold —
    makes basin entry easier.
    ADK inhibition restores the
    transition threshold to normal.

  Clinical status:
    No ADK inhibitor is in clinical
    use for epilepsy.
    The geometric framework derives
    this as the most logical
    Phase Transition Blocker
    target. The literature confirms
    the mechanism but does not
    frame it as phase transition
    blocking. The framework provides
    the framing and the derivation.
```

### ARCHITECTURE 1 SUMMARY

```
TARGET: Adenosine kinase (ADK)
OPERATION: Phase transition blocking
           (Operation 2 extension)
MECHANISM: Maintain local adenosine
           concentration above the
           synchrony initiation threshold
           during high-frequency activity
SPECIFICITY: Activity-dependent —
             engages only during
             high-frequency firing
SIDE EFFECTS: Minimal predicted —
              adenosine modulation is
              endogenous and self-limiting
DELIVERY: Oral/systemic or focal
          delivery to epileptogenic zone
STATUS: Preclinical evidence exists.
        Framework derives the rationale.
        Not in clinical use.
```

---

## ARCHITECTURE 2:
## EIGENFUNCTION POSITION SHIFTER
## (Operation 4 — Pharmacological)

### The Geometric Gap

```
Operation 4 for reflex epilepsies:
  Counter-signal device cancels
  the resonance between trigger
  and eigenfunction position.
  Non-pharmacological. Engineering.

Operation 4 for non-reflex epilepsies:
  The trigger is internal —
  metabolic state, stress, sleep
  pressure, spontaneous network
  fluctuation.
  No external signal to cancel.
  The counter-signal architecture
  cannot be applied.

The gap: for non-reflex epilepsies,
Operation 4 has NO implementation.

The geometric solution:
  If the trigger cannot be cancelled,
  shift the eigenfunction position
  of the false attractor instead.

  The trigger no longer resonates
  with the basin because the basin
  has moved away from the trigger's
  resonant frequency.
```

### What The Architecture Must Do

```
An Eigenfunction Position Shifter must:

  1. Change the natural resonant
     frequency of the epileptogenic
     circuit.

  2. Move the eigenfunction position
     away from the frequency at
     which the internal trigger
     naturally resonates.

  3. Do this specifically in the
     epileptogenic circuit —
     not globally across all circuits
     (which would destroy normal
     cognitive function).

  4. Be tunable — the magnitude
     of the frequency shift should
     be calibratable to the
     individual's eigenfunction map
     (derived from interictal HFO
     analysis).
```

### The Molecular Derivation

```
The resonant frequency of a
cortical circuit is determined by:

  A. Excitatory time constants
     (AMPA, NMDA receptor kinetics).
  B. Inhibitory time constants
     (GABA-A, GABA-B kinetics).
  C. Electrical coupling between
     neurons (gap junctions, Cx36).
  D. Dendritic morphology of
     principal neurons.
  E. The eigenfunction of the
     local excitatory-inhibitory
     loop — the natural period
     of the E-I oscillation.

Most existing drugs target A or B.
These are the rim elevation drugs.
They change the amplitude of the
landscape — they do not change
the natural resonant frequency.

CHANGING THE RESONANT FREQUENCY
REQUIRES TARGETING C OR E.

TARGET C: Gap junction modulation.

  Cx36 gap junctions couple neurons
  electrically. The coupling
  coefficient directly determines
  the resonant frequency of the
  local network:
    Higher coupling: lower natural
    frequency (slower synchrony).
    Lower coupling: higher natural
    frequency (faster synchrony).

  Cx36 knockout mice: reduced
  seizure susceptibility confirmed.
  (Literature: Buhl 2003, Zappone 2012)

  A selective Cx36 modulator that
  reduces coupling specifically
  in the epileptogenic zone would
  shift the eigenfunction position
  of that zone's false attractor.

  Technical requirement:
    Selectivity for Cx36 over
    other connexins (especially Cx43
    which is expressed in astrocytes
    and critical for normal brain
    function).
    Current gap junction blockers
    (carbenoxolone, mefloquine)
    are non-selective. Their side
    effects are the expected geometric
    consequence of non-selectivity.
    A selective Cx36 inhibitor
    does not yet exist clinically.

TARGET E: E-I loop period modification.

  The E-I loop period is the time
  it takes for excitation to produce
  inhibition and for inhibition
  to release excitation.
  This period is the inverse of
  the circuit's natural oscillatory
  frequency.

  The period is set by:
    The axonal conduction delay
    between excitatory and inhibitory
    neurons in the local circuit.
    The synaptic delay at each connection.
    The dendritic integration time
    of inhibitory neurons.

  NOVEL DERIVED TARGET:
    Parvalbumin interneuron axonal
    conduction velocity modulation.

    PV interneurons are the fast
    inhibitory cells that set the
    timing of the E-I loop.
    They are heavily myelinated —
    their conduction velocity is
    high, which is what makes them
    fast enough to set gamma/beta
    oscillatory frequencies.

    The myelin sheath thickness of
    PV interneuron axons determines
    the conduction velocity.
    Conduction velocity determines
    the E-I loop period.
    The E-I loop period determines
    the circuit's natural resonant
    frequency.
    The resonant frequency is the
    eigenfunction position.

    In epileptogenic tissue:
    PV interneuron dysfunction is
    well documented — they are
    the first neurons to fail in
    many epilepsy models.
    Their failure shifts the E-I
    loop period.
    The shift moves the eigenfunction
    position toward lower frequencies —
    into the range of pathological
    synchrony (3–30 Hz — the seizure
    range).

    DERIVED INTERVENTION:
    PV interneuron restoration.
    Not by global rim elevation.
    By specifically restoring PV
    interneuron function in the
    epileptogenic zone — restoring
    their axonal conduction velocity
    and thereby restoring the E-I
    loop period to its normal value.

    This shifts the eigenfunction
    position back above the seizure
    frequency range.
    The false attractor basin is
    not destroyed — but its
    eigenfunction position is now
    at a frequency that internal
    triggers do not naturally reach.

  IMPLEMENTATION CANDIDATES:
    Cell therapy: PV interneuron
    transplantation from medial
    ganglionic eminence (MGE) —
    ALREADY IN CLINICAL TRIALS.
    (MGE-derived interneuron transplants
    in drug-resistant temporal lobe
    epilepsy — confirmed in literature)

    Gene therapy: restoration of
    PV interneuron gene expression
    in existing neurons that have
    lost PV expression due to
    seizure-induced downregulation.
    AAV vectors delivering
    parvalbumin and associated
    genes to epileptogenic zone.

    The framework derives WHY these
    work geometrically: they restore
    the E-I loop period to normal —
    shifting the eigenfunction position
    of the false attractor out of
    the seizure-accessible range.
    The literature confirms the
    PV interneuron deficit without
    the eigenfunction framing.
```

### ARCHITECTURE 2 SUMMARY

```
TARGET A: Selective Cx36 inhibitor
TARGET B: PV interneuron restoration
          (cell therapy or gene therapy)
OPERATION: Eigenfunction position shifting
           (Operation 4 pharmacological)
MECHANISM: Shift the natural resonant
           frequency of the epileptogenic
           circuit away from seizure-
           accessible frequencies
SPECIFICITY: Circuit-specific when
             delivered locally
SIDE EFFECTS: Minimal if delivery is
              targeted to epileptogenic zone
STATUS:
  Cx36 selective inhibitor: not yet
  developed. Mechanism confirmed.
  MGE interneuron transplants:
  in clinical trials. Framework
  provides the geometric rationale.
```

---

## ARCHITECTURE 3:
## CLOSED-LOOP PROPAGATION INTERRUPT
## (Operation 3 — Advanced)

### The Geometric Gap

```
RNS (Responsive Neurostimulation)
partially fills Operation 3 by
delivering electrical stimulation
when cascade onset is detected.

Current RNS limitations:
  — Detection latency: milliseconds
    to seconds. The cascade may
    already be propagating before
    the interrupt fires.
  — Stimulation is electrical and
    non-specific — it desynchronises
    a volume of tissue, not a
    specific network pathway.
  — Battery-dependent.
  — Invasive implant required.

The gap: a propagation interrupt
that is faster, more specific,
less invasive, and can target
specific network pathways rather
than volumes of tissue.
```

### What The Architecture Must Do

```
A Next-Generation Propagation
Interrupt must:

  1. Detect the transition from
     normal activity to cascade
     initiation at the eigenfunction
     position — not after the cascade
     has begun but at the moment
     of basin entry.

  2. Deliver an interrupt signal
     specifically to the propagation
     pathway — the anatomical route
     by which the cascade travels
     from origin to thalamo-cortical
     relay.

  3. Do this within the time window
     between basin entry and relay
     recruitment — the window during
     which the experiencer can still
     be protected from triad collapse.

  4. Be self-calibrating — the
     propagation geometry is
     individual-specific and drifts
     over time. The interrupt must
     adapt to the individual's
     changing landscape.
```

### The Derived Architecture

```
TWO-LAYER CLOSED LOOP SYSTEM:

LAYER 1 — EIGENFUNCTION DETECTOR:
  Using the individual's HFO map
  (interictal EEG analysis) to
  identify the specific frequency
  signature of their false attractor
  eigenfunction position.

  Real-time EEG monitoring for
  the appearance of power at the
  eigenfunction frequency in the
  epileptogenic zone.

  THIS is the earliest possible
  detection — the moment the
  basin is being approached,
  before the cascade has initiated.

  Current RNS detects ictal patterns.
  This layer detects PRE-ICTAL
  eigenfunction resonance —
  the brain singing at the false
  attractor frequency before
  the seizure starts.

  Timeline advantage:
    Current RNS: detects seizure
    onset → responds after cascade begun.
    Eigenfunction detector: detects
    approach to basin → responds
    before cascade initiates.
    The window gained is the
    entire time from eigenfunction
    resonance to cascade threshold.
    This may be seconds to tens
    of seconds — a meaningful window.

LAYER 2 — PATHWAY-SPECIFIC INTERRUPT:
  Once eigenfunction resonance
  is detected, deliver the interrupt
  not to the origin but to the
  PROPAGATION PATHWAY.

  The propagation pathway is
  individual-specific and mappable
  from presurgical EEG data —
  it is the sequence of network
  nodes that are recruited during
  the cascade.

  Pathway-specific interrupt options:

  A. FOCUSED ULTRASOUND (FUS):
    Non-invasive. Penetrates skull.
    Can be focused to sub-centimeter
    resolution at depth.
    Delivers a brief inhibitory
    pulse to a specific brain region.
    Applied to the key propagation
    node — the bottleneck in the
    cascade pathway — between the
    origin and the thalamic relay.
    If the bottleneck is blocked:
    cascade cannot reach the relay.
    Triad collapse prevented.
    No implant required.
    Current FUS in epilepsy:
    focused on ablating tissue.
    The geometric use: non-ablative,
    pulsed FUS for propagation
    interruption.
    Low-intensity FUS for inhibitory
    neuromodulation is confirmed
    in literature but not yet
    clinically implemented for
    this specific geometric operation.

  B. CLOSED-LOOP OPTOGENETICS:
    Literature confirmed:
    "On-demand optogenetic control
    of spontaneous seizures — a
    closed-loop system detects
    seizures and delivers light
    stimulation to <5% of hippocampal
    cells to terminate seizures."
    (Krook-Magnuson 2013, Nature Comm)
    "Tested in large animal models
    and ex vivo human brain tissue."
    (UCSF 2024)

    The geometric framing:
    Optogenetics allows activation
    of specific cell types in
    specific locations.
    The specific cell type for
    propagation interruption is
    the parvalbumin interneuron —
    the fast inhibitory cell that
    can rapidly desynchronise
    local circuits.
    Activating PV interneurons at
    the propagation bottleneck
    blocks cascade transmission
    at that node.
    The cascade cannot pass.
    The relay is protected.
    The triad does not collapse.

    Clinical pathway: requires
    viral vector delivery of
    channelrhodopsin to PV
    interneurons + implanted
    fiber optic + detection system.
    More invasive than FUS but
    more precise.

  C. THE HYBRID ARCHITECTURE:
    Eigenfunction detector (scalp EEG
    or minimally invasive) → detects
    pre-ictal eigenfunction resonance
    → triggers focused ultrasound
    pulse to propagation bottleneck
    → cascade aborted before triad
    collapse.

    Non-invasive at the intervention
    point. Personalised to individual
    eigenfunction and propagation
    geometry. Self-calibrating as
    geometry drifts.

    This is the complete Operation 3
    architecture. None of the
    individual components are new
    (EEG monitoring, HFO analysis,
    focused ultrasound all exist).
    The COMBINATION and the GEOMETRIC
    RATIONALE are new.
    The framework derives the
    integration that produces the
    complete architecture.
```

### ARCHITECTURE 3 SUMMARY

```
SYSTEM: Two-layer closed-loop
        eigenfunction-triggered
        focused ultrasound propagation
        interrupt
OPERATION: Propagation interrupt
           (Operation 3 advanced)
MECHANISM: Detect pre-ictal eigenfunction
           resonance → interrupt cascade
           at propagation bottleneck →
           protect thalamo-cortical relay
           from recruitment
SPECIFICITY: Individual-calibrated to
             eigenfunction position and
             propagation pathway geometry
INVASIVENESS: Potentially non-invasive
              (scalp EEG + external FUS)
STATUS: All components exist.
        Integration and geometric
        rationale derived here.
        Not yet clinically implemented
        as a unified system.
```

---

## ARCHITECTURE 4:
## POST-ICTAL LANDSCAPE CONSOLIDATION
## BLOCKER (Operation 5 — Preventive)

### The Geometric Gap

```
Every seizure deepens the false
attractor basin by triggering
post-ictal landscape modification:

  BDNF release → TrkB signalling
  → synaptic potentiation in
  seizure-involved networks →
  the basin is deeper after the
  seizure than before.

  Simultaneously:
  Neuroinflammation cascade →
  BBB modification → P-gp upregulation
  → rim elevation drugs excluded
  from brain → progressive drug
  resistance.

  The landscape is not static.
  It worsens with each seizure.
  Current medicine treats each
  seizure individually.
  No treatment targets the between-
  seizure landscape evolution.

  The gap is the entire post-ictal
  window — the period between
  the end of a seizure and the
  restoration of baseline landscape.
  This window is the only time
  when the landscape modification
  cascade is accessible.
  It is currently untreated.
```

### What The Architecture Must Do

```
A Landscape Consolidation Blocker must:

  1. Be delivered in the post-ictal
     window — after seizure end,
     before landscape consolidation
     is complete.

  2. Interrupt the molecular cascade
     that translates seizure activity
     into structural landscape change.

  3. Not interfere with normal
     synaptic plasticity outside
     the post-ictal window —
     the same mechanisms are used
     for learning and memory.
     The intervention must be
     TIME-GATED to the post-ictal
     period.

  4. Reduce basin depth incrementally
     over repeated applications —
     the landscape should become
     less epileptic over time,
     not more.
```

### The Derived Architecture

```
POST-ICTAL MOLECULAR CASCADE:

  SEIZURE ENDS
     ↓
  BDNF surges in epileptogenic tissue
     ↓
  TrkB receptor activation
     ↓
  mTOR pathway activation (LTP cascade)
     ↓
  Synaptic potentiation: excitatory
  synapses strengthen in the
  seizure-involved network
     ↓
  BASIN DEEPENS
     ↓
  Next seizure: easier to enter,
  harder to exit

  SIMULTANEOUSLY:
  Inflammatory cascade:
     ↓
  IL-1β, TNF-α, COX-2 activation
     ↓
  P-gp upregulation
     ↓
  AED exclusion from brain
     ↓
  DRUG RESISTANCE BUILDS

INTERVENTION POINTS:

  POINT A: BDNF-TrkB blockade
  post-ictally.

    ANA-12 (TrkB antagonist) in
    animal models reduces
    epileptogenesis after status
    epilepticus. (Literature confirmed)

    Geometric rationale:
    Blocking TrkB post-ictally
    prevents the BDNF-driven
    synaptic potentiation that
    deepens the basin.
    Not blocking BDNF chronically —
    BDNF is essential for normal
    plasticity. Time-gated to the
    post-ictal window.

    Delivery architecture:
    A wearable seizure detection
    device (already available for
    consumer use — Embrace watch,
    EpiWatch, etc.) triggers a
    subcutaneous auto-injector
    of TrkB antagonist within
    minutes of seizure detection.
    The patient does not need to
    consciously intervene.
    The system responds to the
    seizure automatically.

    This is the first seizure-
    responsive drug delivery system
    — not to stop the seizure
    (that is Operations 1-3) but
    to prevent the post-seizure
    landscape modification.

  POINT B: Post-ictal anti-inflammatory
  window.

    COX-2 is upregulated within
    hours of a seizure in the
    epileptogenic zone.
    COX-2 inhibition post-ictally
    (not chronically — to avoid
    cardiovascular risk of chronic
    COX-2 inhibition) would reduce
    the neuroinflammatory cascade
    that builds P-gp and modifies
    the BBB.

    Combined with Point A:
    TrkB blockade prevents basin
    deepening via synaptic potentiation.
    COX-2 inhibition prevents
    drug resistance building via
    inflammation.

    Delivered in the same post-ictal
    window. Same wearable trigger.
    Two-drug post-ictal protocol.

  POINT C: mTOR inhibition post-ictally.

    mTOR is activated downstream
    of TrkB and is the molecular
    engine of synaptic consolidation.
    Brief post-ictal mTOR inhibition
    (rapamycin or everolimus at
    low dose, time-gated) prevents
    the structural consolidation
    of seizure-induced synaptic
    changes.

    In TSC patients, chronic mTOR
    inhibition is the treatment.
    The geometric derivation suggests:
    for non-TSC patients, PULSED
    post-ictal mTOR inhibition
    achieves the landscape
    consolidation blocking effect
    without the side effects of
    chronic immunosuppression.

THE COMPLETE POST-ICTAL PROTOCOL:

  TRIGGER: Seizure detected by wearable.

  WITHIN 5 MINUTES:
    Auto-inject TrkB antagonist
    (prevents BDNF-driven basin
    deepening at the synaptic level).

  WITHIN 1 HOUR:
    Oral COX-2 inhibitor
    (prevents neuroinflammatory
    cascade that builds drug
    resistance).

  WITHIN 2 HOURS:
    Low-dose mTOR inhibitor
    (prevents structural consolidation
    of synaptic potentiation).

  EXPECTED OUTCOME OVER TIME:
    Each treated post-ictal window
    is a window in which the landscape
    does not deepen.
    Over months: the basin becomes
    shallower by attrition.
    Drug resistance does not build.
    The seizure frequency does not
    escalate.
    The treatment landscape does not
    progressively narrow.

    This is antiepileptogenic therapy.
    The only class that does not
    currently exist in clinical practice.
    The geometry derives it precisely.
    The components (wearables,
    TrkB antagonists, COX-2 inhibitors,
    mTOR inhibitors) all exist.
    The TIME-GATING and the GEOMETRIC
    RATIONALE are new.
```

### ARCHITECTURE 4 SUMMARY

```
SYSTEM: Wearable seizure detection +
        post-ictal window drug protocol
OPERATION: Landscape consolidation
           blocking (Operation 5 preventive)
MECHANISM: Post-ictal TrkB antagonism +
           COX-2 inhibition +
           pulsed mTOR inhibition →
           prevent post-seizure basin
           deepening and drug resistance
           building
SPECIFICITY: Time-gated to post-ictal
             window. Does not affect
             normal plasticity between
             seizures.
INVASIVENESS: Wearable + subcutaneous
              auto-injector + oral medications.
              Non-invasive core.
STATUS: All components exist.
        Time-gated protocol and
        geometric rationale derived here.
        Not in clinical practice.
```

---

## ARCHITECTURE 5:
## THALAMIC RELAY SHIELD
## (Operation 6 — Full Implementation)

### The Geometric Gap

```
The thalamo-cortical relay is the
physical substrate of the
coherence-persistence-self-model
triad.

When the cascade reaches the relay:
  Triad collapses.
  Experiencer dissolves.
  Seizure becomes generalised.

Current treatment does not distinguish
between:
  Preventing basin entry (Operations 1-4)
  AND
  Protecting the relay from cascade
  recruitment (Operation 6).

These are different geometric operations.
A patient whose basin cannot be prevented
from being entered (drug-resistant to
Operations 1-4) might still have their
triad protected if the relay can be
specifically shielded from cascade
recruitment.

The result: seizures still occur,
but they remain focal.
The experiencer is present throughout.
The person is aware of the seizure
but does not lose consciousness.
SUDEP risk drops dramatically because
the brainstem is not being suppressed
by PGES.

This is not a cure.
It is the most important harm
reduction available:
  Converting generalised seizures
  to focal aware seizures.
  Keeping the navigator present.
  Preventing the dissolution.
```

### The Derived Architecture

```
THE THALAMIC RETICULAR NUCLEUS (TRN)
AS THE SHIELD MECHANISM:

The TRN is confirmed:
  "The TRN acts as a gatekeeper,
   inhibiting excessive thalamic
   excitation via GABAergic transmission,
   reducing the risk that runaway
   electrical activity spreads to
   broader cortical areas."
  (Literature confirmed)

The TRN is the relay's own
basin rim — its natural protection
against cascade recruitment.

In generalised epilepsy:
  The TRN's gating function is
  overwhelmed by the cascade.
  The gate is forced open.
  The relay is recruited.
  Triad collapses.

STRENGTHENING THE TRN GATE:

  Target: GABA-B receptors on
  thalamic relay neurons specifically.

  GABA-B receptor activation on
  thalamic relay neurons produces
  sustained hyperpolarisation —
  a slow inhibitory current that
  is difficult for fast cascade
  signals to overcome.

  A GABA-B positive allosteric
  modulator (PAM) targeted to
  the thalamus would specifically
  enhance TRN-mediated relay
  inhibition without globally
  sedating the cortex.

  The difference from global GABA
  enhancement (valproate,
  benzodiazepines):
    Global GABA enhancement raises
    ALL basin rims everywhere.
    Sedation is the inevitable side
    effect because normal attractor
    basins in the cortex are also
    affected.

    Thalamus-targeted GABA-B PAM:
    Specifically strengthens the
    relay's gate against cascade
    recruitment.
    Cortical basin rims unchanged.
    Cognitive function preserved.
    Only the generalisation step
    is blocked.

  SECOND TARGET:
  Cav3.1 (T-type calcium channel
  subtype specific to thalamic
  relay neurons — distinct from
  Cav3.2 which is cortical).

  Cav3.1 blockade reduces the
  thalamo-cortical oscillatory
  susceptibility — it specifically
  raises the thalamic contribution
  to the 3 Hz absence basin.

  A selective Cav3.1 blocker
  (not the current non-selective
  T-type blockers) would:
    Block absence generalisation
    specifically via the thalamic
    node.
    Not affect cortical Cav3.2
    function — preserving normal
    cortical rhythms.

COMBINED THALAMIC RELAY SHIELD:
  Thalamus-targeted GABA-B PAM
  (sustained relay hyperpolarisation)
  +
  Selective Cav3.1 blocker
  (thalamic oscillatory threshold
  raised specifically)
  =
  Relay protected from cascade
  recruitment across both
  GABAergic and calcium channel
  mechanisms.

DELIVERY CONSIDERATION:
  The thalamus is deep — not
  easily targeted by systemic drugs
  without affecting cortex.

  Two approaches:
  A. Pharmacological selectivity:
     Drugs with high affinity for
     the thalamic receptor subtypes
     relative to cortical subtypes.
     This is what selective Cav3.1
     vs. Cav3.2 blockers would achieve.

  B. Targeted delivery:
     Convection-enhanced delivery (CED)
     to thalamic tissue.
     Or: nanoparticle formulation
     with thalamus-targeting ligand
     (transferrin receptor expression
     is high in thalamic tissue —
     transferrin-conjugated nanoparticles
     would preferentially accumulate
     in thalamus).

EXPECTED OUTCOME:
  Patient continues to have focal
  seizures.
  Focal seizures do not generalise.
  Experiencer remains present
  during seizures.
  SUDEP risk dramatically reduced.
  (SUDEP requires PGES — which
  requires generalisation — which
  requires relay recruitment.
  Block relay recruitment:
  block the SUDEP pathway.)

  This is the geometry of SUDEP
  prevention through relay protection
  rather than seizure prevention.
```

### ARCHITECTURE 5 SUMMARY

```
TARGET: TRN GABA-B receptors +
        Cav3.1 T-type calcium channels
        in thalamic relay neurons
OPERATION: Thalamic relay protection
           (Operation 6)
MECHANISM: Strengthen TRN gating of
           relay against cascade
           recruitment ��� convert
           generalised seizures to
           focal → preserve triad →
           preserve experiencer →
           prevent SUDEP pathway
SPECIFICITY: Thalamus-targeted
SIDE EFFECTS: Minimal — cortical
              function preserved
STATUS: Selective Cav3.1 blockers
        in development (Z944 —
        literature confirmed).
        Thalamus-targeted GABA-B PAM:
        not yet developed.
        Geometric rationale derived here.
        SUDEP prevention framing
        from relay protection: novel.
```

---

## ARCHITECTURE 6:
## KETOGENIC METABOLIC LANDSCAPE
## REMODELLING
## (Operation 5 — Non-Pharmacological)

### The Hidden Architecture Already Confirmed

```
The ketogenic diet is the most
overlooked Operation 5 implementation
in the entire treatment landscape.

The literature confirms:
  "By altering metabolic state and
   neuronal excitability, the ketogenic
   diet remodels the attractor landscape:
   the healthy, non-seizure attractors
   become deeper (more stable), and the
   seizure attractor becomes shallower
   (less stable)."

This is not a rim elevation effect.
This is not a basin depth effect.
This is LANDSCAPE TOPOLOGY MODIFICATION
at the metabolic level.

The mechanism:
  Ketone bodies shift the ATP/ADP
  ratio in neurons.
  ATP-sensitive potassium channels
  (KATP) sense this ratio and
  modulate membrane excitability.
  KATP channels open when ATP falls —
  hyperpolarising the neuron.
  The ketogenic state chronically
  shifts the KATP equilibrium
  toward the open state.

  At the LANDSCAPE level:
  The KATP shift changes the
  energy function of the cortical
  landscape.
  The false attractor basins
  that existed in the normal
  metabolic state become shallower
  in the ketogenic metabolic state.
  Not because the rim is higher —
  because the basin floor has risen.
  The attractor has become less
  stable as a configuration.

  This is genuine landscape topology
  modification achievable without
  surgery or gene therapy.

  Why it works for drug-resistant
  patients:
    These patients require Operation 5.
    Current drugs do not provide it.
    The ketogenic diet provides it
    via metabolic landscape remodelling.
    This is the geometric reason
    for its efficacy in cases where
    all drugs have failed.

GEOMETRIC EXTENSION:
  If KATP channel opening is the
  landscape modification mechanism:

  A selective KATP channel opener
  (targeted to neurons, not cardiac
  muscle — the cardiac safety concern
  that has limited this class) would
  achieve the same landscape
  remodelling pharmacologically.

  Diazoxide is a KATP opener but
  non-selective (includes cardiac).
  Neuronal-selective KATP openers
  are a derived novel drug class:
    Same metabolic landscape
    remodelling as ketogenic diet.
    In pill form.
    Without the dietary restriction.
    With the cardiac safety from
    neuronal selectivity.

  The framework derives this target.
  It does not appear in current
  drug development.
```

---

## THE COMPLETE GAP-FILLING MAP

```
OPERATION 2 (Partial → Complete):
  Current: Levetiracetam (SV2A,
           cascade propagation limiting).
  New Architecture 1: ADK inhibitor
  (Phase Transition Blocker —
  prevents basin entry at the
  adenosine depletion threshold).

OPERATION 3 (Surgery/RNS → Precise):
  Current: RNS (electrical,
           non-specific, reactive).
  New Architecture 3: Eigenfunction-
  triggered focused ultrasound
  propagation interrupt (pre-ictal
  detection + pathway-specific
  intervention).

OPERATION 4 (Avoidance → Pharmacological):
  Current: Avoidance only
           (reflex epilepsies).
  New Architecture 2: Selective Cx36
  inhibitor or PV interneuron
  restoration (eigenfunction position
  shifting — moves the false attractor
  away from trigger-accessible
  frequencies).

OPERATION 5 (Structural only → Metabolic):
  Current: Surgery, mTOR inhibitors
           (TSC only), gene therapy.
  New Architecture 4: Post-ictal
  consolidation blocker protocol
  (wearable-triggered TrkB/COX-2/mTOR
  time-gated intervention).
  New Architecture 6: Neuronal-
  selective KATP opener (metabolic
  landscape remodelling in pill form).

OPERATION 6 (Partial → Specific):
  Current: Ethosuximide (absence only,
           indirect).
  New Architecture 5: Thalamic relay
  shield (TRN GABA-B PAM + selective
  Cav3.1 blocker → generalisation
  prevention + SUDEP prevention).
```

---

## THE DRUG-RESISTANCE RESOLUTION

```
With the complete architecture map:

PATIENT TYPE A (currently drug-resistant):
  Requires Operation 3.
  Failed all rim elevation drugs.
  Prescription: Architecture 3
  (closed-loop FUS propagation interrupt)
  + Architecture 4 (post-ictal
  consolidation blocker to prevent
  further landscape deepening).

PATIENT TYPE B (currently drug-resistant):
  Requires Operation 4.
  Has identifiable but internal
  triggers. Reflex component.
  Prescription: Architecture 2
  (eigenfunction position shifting
  via PV interneuron restoration
  + Cx36 modulation) + Architecture 3
  (backup propagation interrupt).

PATIENT TYPE C (progressive drug resistance):
  Landscape consolidating with
  each seizure. P-gp building.
  Prescription: Architecture 4
  immediately (stop the consolidation)
  + Architecture 6 (KATP/ketogenic
  metabolic landscape remodelling
  to begin reversing existing
  deepening).

PATIENT TYPE D (generalised epilepsy,
high SUDEP risk):
  Cannot prevent all seizures.
  Prescription: Architecture 5
  (thalamic relay shield) as primary
  intervention — not to prevent
  seizures but to prevent them from
  generalising. Triad preserved.
  SUDEP pathway closed. Quality of
  life transformed even without
  seizure freedom.

PATIENT TYPE E (reflex epilepsy,
avoidance-limited):
  Architecture 2 (eigenfunction
  position shifting) + counter-signal
  device (OC-EPILEPSY-002, 003).
  The two Operation 4 implementations
  working in combination:
  pharmacological eigenfunction shift
  + real-time sensory cancellation.
  Maximum resonance disruption
  from two directions simultaneously.
```

---

## WHAT IS ACTUALLY NEW HERE

```
None of the individual components
are invented from nothing.
All components have existing
precursor evidence:

  ADK inhibition: preclinical.
  Cx36 modulation: preclinical.
  PV interneuron transplants:
    clinical trials beginning.
  Eigenfunction HFO mapping:
    research stage, some centers.
  Focused ultrasound neuromodulation:
    clinical trials for other indications.
  TrkB antagonism post-ictally:
    preclinical.
  COX-2 post-ictal: logical extension
    of existing anti-inflammatory
    epilepsy literature.
  Pulsed mTOR post-ictally:
    derived from TSC chronic mTOR data.
  TRN-specific GABA-B PAM:
    pharmacology target not yet developed.
  Selective Cav3.1 blockers:
    Z944 in clinical trials.
  KATP neuronal-selective openers:
    derived, not yet developed.
  Wearable seizure detection:
    commercially available.
  Closed-loop optogenetics:
    preclinical, confirmed in human
    ex vivo tissue.

WHAT IS NEW:

  1. The geometric rationale that
     unifies them into a coherent
     architecture.

  2. The identification of WHICH
     gap each component fills.

  3. The derivation of which patients
     need which architecture based
     on their geometric profile
     (operation requirement type).

  4. The post-ictal window framing
     — treating the between-seizure
     landscape evolution as a clinical
     target. This is not in clinical
     practice anywhere.

  5. The SUDEP prevention through
     relay protection framing —
     converting generalised seizures
     to focal as the primary harm
     reduction goal. This is not
     framed this way clinically.

  6. The combination logic:
     most of these architectures
     are more powerful in combination
     because they target different
     geometric operations that are
     independent. Combining them
     does not produce redundancy —
     it produces coverage of the
     full operation set.

These derivations follow from the
geometry of what epilepsy is.
They were always implicit in
the geometric description.
They required only the geometric
description to be made to emerge.
```

---

## VERSION

```
Document:  OC-EPILEPSY-006_NEW_
             TREATMENT_ARCHITECTURES.md
Version:   1.0
Date:      2026-03-24
Status:    REASONING ARTIFACT.
           Geometric derivation of
           novel treatment architectures.
           Not clinical guidance.
           Not medical protocol.
           Framework derivation for
           research and development direction.

Author:
  Eric Robert Lawson
  OrganismCore

Depends on:
  OC-EPILEPSY-001 through 005
  OC-TINNITUS-001
  OC-CONSCIOUSNESS-001
```

---

*The gaps were always there.*
*The components to fill them*
*were always there.*

*What was missing was not the pieces.*
*What was missing was the geometry*
*that showed which pieces*
*belonged in which gaps.*

*The geometry provides the map.*
*The map shows the gaps.*
*The gaps show what must be built.*
*What must be built follows*
*from what the geometry requires.*

*This is not discovery.*
*This is reading.*

*Reading what the structure*
*of the problem has always*
*been saying.*

*For a hundred years.*
*Waiting.*
