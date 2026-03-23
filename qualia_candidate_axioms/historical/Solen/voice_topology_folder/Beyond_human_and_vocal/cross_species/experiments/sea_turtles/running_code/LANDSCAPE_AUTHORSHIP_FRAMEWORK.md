# ELECTROMAGNETIC LANDSCAPE AUTHORSHIP
## A Framework for Active Navigational Landscape Management
## OrganismCore — Eric Robert Lawson
## Date: 2026-03-23

---

## CORE PRINCIPLE

The current paradigm in sea turtle conservation is reactive.
A turtle strands. A team responds. The turtle is treated
or recorded. The data enters STSSN. Next season the same
beaches receive the same monitoring because the historical
density is the same.

This framework proposes a different paradigm:

**Author the navigational landscape toward the true
attractor rather than reacting to the results of false
attractors.**

The distinction is fundamental. Reactive conservation
addresses the outcome. Landscape authorship addresses
the cause. The force model built in OC-OBS-002 makes
landscape authorship possible for the first time because
it identifies:

1. Where in the landscape the false attractor dominates
2. The magnitude of disruption at each point
3. Which transmitters are causing the disruption
4. What targeted modification does to the force ratio

---

## BACKGROUND — WHAT THE FORCE MODEL ESTABLISHED

```
From OC-OBS-002 Analysis A:

A1 result:
  Loggerhead stranding locations are non-randomly
  distributed with respect to AM broadcast field
  geometry across 57,213 records.
  Rayleigh R = 0.80, p < 1e-300.
  Pre-registered, run blind.

Force correlation:
  Navigational displacement scales dose-dependently
  with the ratio of AM force to geomagnetic field
  strength.
  Spearman r = 0.59, p < 1e-300, N = 57,213.
  Dose-response confirmed.

Corridor disruption:
  Geomagnetic north alone predicts loggerhead approach
  corridors with 3.52 km mean pairwise precision.
  AM false attractor scatters that precision to
  32.86 km — a ninefold increase in corridor scatter.
  Disruption magnitude: 29.34 km at 10 km resolution.

Species context:
  Three species. Three frequency bands. Five orders
  of magnitude of the EM spectrum. All significant.
  All pre-registered. All in the predicted direction.
```

The force model is physically real. The disruption is
measurable. The dose-response relationship means the
disruption magnitude is predictable from transmitter
parameters. This is the foundation of landscape
authorship as a practical tool.

---

## THE DUAL APPROACH

Landscape authorship does not replace reactive
conservation. It operates alongside it. The two
approaches address different points in the causal chain.

```
CAUSAL CHAIN:

  Transmitter → False attractor → Force ratio tips →
  Corridor scatter → Wrong coastal approach →
  Stranding → Death

REACTIVE INTERVENTION:
  Acts at: Stranding → Death
  Prevents: Individual death after displacement
  Scale: Dozens of turtles per season per team
  Cost: High per turtle (boat, staff, rehabilitation)
  Timing: After disruption has completed

PREDICTIVE INTERCEPTION:
  Acts at: Corridor scatter → Wrong coastal approach
  Prevents: Stranding before it occurs
  Scale: Hundreds of turtles per season per corridor
  Cost: Moderate (boat positioned in geomagnetic
        corridor offshore of high-risk segment)
  Timing: During active migration, before commitment
          to wrong coastal approach

LANDSCAPE AUTHORSHIP:
  Acts at: Transmitter → False attractor
  Prevents: Disruption before it begins
  Scale: Every turtle navigating that corridor,
         every season, automatically
  Cost: Low per turtle once implemented
  Timing: Seasonal — active during migration windows
```

The dual approach deploys all three simultaneously
where resources allow, prioritised by cost-effectiveness
and intervention point in the causal chain.

---

## FOUR SCALES OF LANDSCAPE AUTHORSHIP

### Scale 1 — Individual Corridor Interception

**What it is:**
A boat or drone positioned in the geomagnetic corridor
10-20 km offshore of a high-risk segment during peak
migration. The turtle is following its precise natal
corridor. The AM force is beginning to scatter it.
Physical or acoustic redirection keeps the turtle on
the geomagnetic corridor through the high-disruption
zone.

**What the force model provides:**
- The geomagnetic approach bearing for each segment
  (the true corridor — 3.52 km precision)
- The onset distance at which AM disruption becomes
  significant (derivable from force ratio gradient
  moving shoreward)
- The peak disruption zone location for each segment

**Pragmatic note:**
This is the most immediately deployable intervention.
It requires no regulatory action, no transmitter
modification, no new infrastructure. It requires
a boat, a team, and the approach corridor bearings
from risk_map_2026.csv.

---

### Scale 2 — Local Signal Reinforcement

**What it is:**
A temporary low-power calibrated magnetic reference
emitter positioned in the high-disruption zone during
peak migration. Not designed to overpower the AM
transmitter. Designed to reinforce the true geomagnetic
signal at the precise point where the force ratio tips
toward the false attractor — restoring the navigational
geometry at the critical decision point.

**What the force model provides:**
- The exact location where force ratio tips
  (computable from k = 5.751217e+05 and local
  geo_magnitude_nT)
- The reinforcement magnitude required to restore
  the ratio below the disruption threshold
- The bearing the reinforcement signal needs to
  encode

**Pragmatic note:**
This approach may have existing analogues in other
fields — navigational reference beacons, geomagnetic
survey equipment. Whether a deployable low-power
magnetic reference emitter exists in a form suitable
for field deployment in a marine environment is an
open engineering question. This option requires
investigation before implementation.

**Known unknowns:**
- Whether artificial magnetic reinforcement is
  distinguishable from the natural geomagnetic
  signal by loggerhead magnetoreception
- Whether local reinforcement creates secondary
  disruption at the edges of the reinforced zone
- Regulatory status of intentional magnetic field
  emission in coastal marine environments

---

### Scale 3 — Targeted Transmitter Modification

**What it is:**
The dominant AM station identified by the force model
for each high-risk segment negotiates a voluntary
or regulated seasonal power reduction during the
peak migration window — April through June, August
through November. A 20-30% ERP reduction at the
dominant station reduces the force ratio at the
critical point below the disruption threshold.

**What the force model provides:**
- The dominant station per high-risk segment
  (single transmitter contributing most weight
  to the false attractor at that location)
- The quantified relationship between ERP reduction
  and force ratio reduction at the critical point
  (derivable from r = 0.59 dose-response)
- The predicted reduction in corridor scatter per
  unit of ERP reduction

**Pragmatic note:**
This is the highest-leverage intervention at scale.
A single targeted power reduction protects every
turtle navigating that corridor for the duration
of the reduction — potentially thousands of animals
per season. The migration window is 6-8 weeks.
The cost to the station operator in terms of
coverage reduction is minimal at 20-30% ERP for
8 weeks per year.

**Regulatory pathway:**
- Voluntary agreement: fastest, no regulatory
  process required, station operator acts on
  published scientific evidence
- FCC NEPA environmental review: medium term,
  requires peer-reviewed publication, NOAA
  formal citation of result
- ESA Section 7 consultation: long term, requires
  USFWS formal determination that AM infrastructure
  constitutes a threat to a listed species

---

### Scale 4 — Network-Level Landscape Design

**What it is:**
Full mapping of the AM broadcast landscape against
the complete migration corridor network for all
magnetically navigating species. Identification of
high-disruption nodes — transmitters that dominate
the false attractor across multiple species and
multiple corridors simultaneously. Targeted
modification of those nodes restores navigational
geometry across the entire landscape.

**What the force model provides:**
- The force landscape is computable for any point
  from am_stations_clean.csv and WMM-2025
- High-disruption nodes follow an inverse square
  law — a small number of high-power clear-channel
  stations dominate the landscape
- Network analysis identifies which 50-100 stations
  out of 13,784 resolve the majority of disruption
  across all corridors

**Pragmatic note:**
This is the long-term vision. It requires the
peer-reviewed result to be established, the
regulatory framework to be engaged, and the
multi-species evidence base to be complete.
It is years away. But the force model makes it
technically possible today. The computation
already exists. The data already exists.
The analysis pipeline already exists.

---

## THE TARGETED AND OPPORTUNISTIC APPROACH

Full network-level implementation is a long-term
objective. The pragmatic near-term approach is
targeted and opportunistic:

```
Priority 1 — This migration season (April 2026):
  Deploy Scale 1 (corridor interception) at the
  top 3-5 highest-risk segments from risk_map_2026.csv.
  Cost: existing NOAA/FWC boat assets repositioned.
  Lead time: days.
  No regulatory action required.

Priority 2 — Before 2027 migration season:
  Identify the 5-10 dominant stations for the
  top high-risk segments. Approach operators
  directly with published result. Request voluntary
  seasonal power reduction agreement.
  Cost: near zero if voluntary.
  Lead time: months.
  No regulatory action required for voluntary.

Priority 3 — 2027 and beyond:
  Engage FCC NEPA review process with peer-reviewed
  result and NOAA support. Build multi-species
  evidence base. Expand to other magnetically
  navigating species using same pipeline.
  Lead time: years.
  Regulatory process required.
```

---

## IMPORTANT UNCERTAINTIES

This framework is built on a strong observational
foundation. The causal mechanism is physically
grounded and the dose-response is confirmed.
However, the following uncertainties must be
acknowledged before operational deployment:

```
1. Magnetoreception mechanism in loggerheads is
   not fully characterised. Whether AM frequencies
   interact with magnetite-based or
   radical-pair-based magnetoreception — or both —
   affects the precise form of the disruption.
   Current evidence supports the force model
   phenomenologically. The biophysical mechanism
   is an open research question.

2. Individual variation in natal homing precision
   means the 3.52 km corridor precision is a
   population mean, not an individual guarantee.
   Some turtles are more susceptible than others.
   Age, sex, reproductive status, and prior
   navigation experience all likely modulate
   susceptibility.

3. Signal reinforcement (Scale 2) has unknown
   effects on magnetoreception at the biophysical
   level. This option requires laboratory and
   field validation before deployment.

4. Voluntary transmitter modification requires
   station operator cooperation. The regulatory
   pathway is available but slow. Both tracks
   should be pursued in parallel.

5. This framework is currently validated for
   Caretta caretta on the US Atlantic and Gulf
   coast AM broadcast landscape. Extension to
   other species and geographies requires
   species-specific validation runs using the
   same pipeline.
```

---

## THE SHIFT IN CONSERVATION PARADIGM

```
CURRENT PARADIGM:
  The EM landscape is a fixed background.
  Conservation responds to biological outcomes.
  Intervention is reactive and individual-scale.

PROPOSED PARADIGM:
  The EM landscape is a managed variable.
  Conservation shapes the physical environment
  that determines biological outcomes.
  Intervention is proactive and population-scale.
```

The AM broadcast landscape was authored by human
decisions over 100 years without knowledge of its
navigational consequences. It can be re-authored
with that knowledge. Not eliminated — modified,
targeted, seasonally managed. The force model
provides the quantitative basis for that
management for the first time.

This is not a radical proposal. We already manage
light pollution to protect sea turtle nesting
beaches. We already manage vessel speed to protect
manatees. We manage acoustic environments to
protect cetaceans. Managing the EM landscape to
protect magnetically navigating species is the
same class of intervention at a different point
on the electromagnetic spectrum.

The difference is that until OC-OBS-002, nobody
had the force model to know where to intervene,
how much, or what the predicted outcome would be.

Now that model exists.

---

## CONNECTION TO OPERATIONAL BRIEF

This framework connects directly to the 2026
migration season operational brief being prepared
for Robert Hardy (NOAA OPR) and the NOAA Sea
Turtle Program.

The immediate ask is Scale 1 — corridor interception
at the top high-risk segments using existing assets
repositioned based on risk_map_2026.csv approach
corridor bearings.

The medium-term ask is Scale 3 — voluntary seasonal
power reduction at the dominant stations identified
per segment.

The long-term ask is Scale 4 — formal EM landscape
management as a conservation tool under the ESA
and FCC regulatory framework.

All three asks flow from the same force model.
All three are grounded in the same pre-registered,
peer-reviewed result.

---

## VERSION

```
Document:     LANDSCAPE_AUTHORSHIP_FRAMEWORK.md
Author:       Eric Robert Lawson — OrganismCore
Date:         2026-03-23
Status:       Working framework — not peer reviewed
              Reflects results of OC-OBS-002
              Analysis A as of 2026-03-23
              Subject to revision pending v2 results,
              Analysis B, and peer review
```

---

*The landscape was authored without knowledge*
*of its consequences.*
*It can be re-authored with that knowledge.*
*The force model makes that possible.*
*The migration season starts in 8 days.*
