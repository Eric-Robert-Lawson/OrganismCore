# ORGANISMCORE — CANCER FALSE ATTRACTOR FRAMEWORK
## What This Work Is, Why It Exists, and What It Means
## Repository Orientation and Framework Articulation
## Version 1.0 | Date: 2026-03-01

---

## FILE PATH

```
qualia_candidate_axioms/historical/
Cross_substrate_verification/
sensory_coherence/cancer/
OrganismCore_Cancer_Framework.md
```

Read this document before reading
anything else in this cancer series.
Read the Workflow_Protocol.md to
reproduce the analysis.
Read the individual cancer series
documents for the findings.

---

## I. THE PROBLEM

```
More than half of oncology Phase III
clinical trials fail.

Drugs that work in cell lines fail
in patients.
Drugs that work in some patients
fail in others with the same diagnosis.

The dominant reason is not
that the drugs are bad.

It is that patients are not
selected correctly.

"Gastric cancer" is not one disease.
It is a mixture of at least four
molecularly distinct states with
different drivers, different survival
mechanisms, and different
therapeutic vulnerabilities.

A CDK4/6 inhibitor given to a patient
whose tumor does not depend on CDK4/6
produces toxicity and no benefit.
The trial is recorded as a failure.
CDK4/6 inhibitors are concluded to
not work in gastric cancer.

The truth is they do not work
in THAT patient's gastric cancer.
They might work in another patient
whose tumor is at a different
molecular position.
The population was wrong.
Not the drug.

This failure pattern repeats across
every solid tumor type.
It has been repeating for decades.
It continues today.

This framework exists to change this
by providing a principled geometric
method for identifying which patient
belongs to which molecular position
before the trial enrolls them.
```

---

## II. THE CORE IDEA

```
Cancer is a geometric problem.

Every cell in the body occupies
a position in a high-dimensional
gene expression space.
Normal cells occupy stable positions
called attractors — corresponding
to their differentiated identity.
A gastric parietal cell.
A pancreatic acinar cell.
A hematopoietic progenitor.

Cancer occurs when a cell is displaced
from its normal attractor and becomes
trapped in a different stable state —
a false attractor —
that supports uncontrolled
proliferation and survival.

The geometry of this transition
is measurable.
Gene expression data records
where every tumor sits in this space.
The distance traveled from the
normal attractor is what this
framework calls depth.

Deeper = further from normal.
Deeper = more molecularly advanced.
Deeper = different therapeutic
         vulnerabilities than
         shallow tumors.

This is not a metaphor.
It is a measurable number —
computed from gene expression,
reproducible from public data,
verifiable by any investigator
with the accession number
and the script.

The clinical tool that emerges
from each cancer analysis is a
depth score — a continuous variable
that positions each tumor in the
attractor landscape and identifies
which drugs that position depends on.

In every cancer validated so far,
this score can be approximated
by three genes measurable by
standard IHC in any pathology lab.
```

---

## III. WHAT CONVERGENCE MEANS AND WHY IT MATTERS

```
The framework does not ask to be
believed on its own authority.

It asks to be evaluated by one
criterion:

  Do the findings derived from
  geometry alone converge with
  findings independently established
  by experimental biology?

This criterion is strict.
It cannot be gamed.
Either the geometry finds what
the experiments found or it does not.
Either the drug target derived from
expression data matches the drug
in clinical trials or it does not.

Across 13 cancer validations:
  Every geometry-derived drug target
  has been confirmed by published
  pharmacology or active clinical trials.
  Zero false positives in direction.

This is not coincidence.
It is the signature of a method
that is measuring something real.

When geometry and experiment agree
without one informing the other —
that is convergent validation.
Two independent methods.
Same answer.
Both findings become stronger.

But convergence is not the end.
It is the beginning.

A method that only confirms
what is known is a consistency check.
Useful but not sufficient.

The framework's real contribution
is what it produces AFTER convergence
has been established:
novel findings that extend beyond
any single published paper by
integrating findings across
separate domains into a unified
patient-selection tool that
no single research group had
assembled in one place.

This is why the literature check
is the last step — not the first.
The geometry runs without prior
knowledge of what the literature says.
The literature is consulted to assess
what the geometry found.
Not to guide it.

This order is the source of the
framework's credibility.
Predictions are stated before data.
Data is analyzed before literature.
Literature is consulted after everything.
This order cannot be changed.
It is what makes the results valid.
```

---

## IV. WHAT GOING FURTHER MEANS

```
In every cancer validation,
the framework produces two types
of output:

TYPE 1 — CONVERGENT CONFIRMATION
  The geometry independently derived
  a finding that published literature
  already established.
  Example from gastric cancer (STAD):
    Geometry found WNT5A r=+0.56
    with attractor depth.
    A 2006 Cancer Research paper
    established WNT5A drives invasion
    and aggressiveness in gastric cancer
    experimentally.
    Two independent methods.
    Same conclusion.
    Neither was informed by the other.
  This type of output validates
  the method.

TYPE 2 — GOING FURTHER
  The geometry reveals a relationship
  or integration that the literature
  had not yet produced.
  Not contradiction of what is known.
  Extension beyond it.
  Example from STAD:
    Literature knew ZEB2 drives
    gastric cancer progression.
    Literature knew AURKA drives
    gastric cancer proliferation.
    Both studied separately.
    Neither connected to the other.
    The geometry measured their
    co-expression in 300 tumors:
    r(ZEB2, AURKA) = 0.9871.
    97.4% shared variance.
    They are not two programs.
    They are one program.
    One drug (alisertib) disrupts
    both simultaneously.
    That therapeutic implication
    exists nowhere in the published
    literature on alisertib in
    gastric cancer.
    The framework produced it by
    measuring a relationship that
    was always there in the data
    but had never been measured.

The distinction between convergence
and going further is the distinction
between validation and contribution.

Both are needed.
Convergence without contribution
is a replication study.
Contribution without convergence
is speculation.
Together they constitute
a validated novel finding.

Every cancer series in this
repository contains both.
```

---

## V. THE ANALYST ERROR MECHANISM

```
Wrong predictions are not failures.
They are the mechanism.

Before any data is analyzed,
the analyst states predictions
based on biological knowledge:
  Which genes should be suppressed?
  Which should be elevated?
  Where in the differentiation pathway
  is the cancer cell blocked?
  What drug would dissolve the block?

These predictions are written down
and locked before data is loaded.
They cannot be changed.

When the data contradicts a prediction,
the framework does not discard
the prediction — it processes it.

Wrong predictions are labeled
ANALYST ASSUMPTION ERRORS.
They are recorded in the documents
alongside confirmed predictions.

This is deliberate.

An honest record of what was assumed
and where assumptions were wrong is
more valuable than a curated record
of only what was confirmed.

Wrong predictions reveal three things:
  1. Where prior biological knowledge
     was incomplete or incorrect
     for this specific cancer context.
  2. Where this cancer differs from
     the analyst's mental model —
     which is exactly the information
     that could save a patient from
     receiving the wrong drug.
  3. What the data actually contains
     that prior knowledge did not predict —
     the novel findings emerge most
     clearly from the corrections.

Example:
  STAD analysis predicted CDH2/VIM
  would be elevated (EMT markers up).
  Data showed CDH2/VIM suppressed.
  The wrong prediction taught:
    STAD bulk signal is non-EMT.
    The EMT subtype is a minority.
    Treating all STAD as EMT-like
    is incorrect.
    The drug targets for the majority
    are different from EMT targets.
  That correction has direct
  clinical implications for which
  patients receive which drugs.

A framework that hides its errors
is a framework that cannot be trusted.
This framework shows every error
alongside every confirmation.
That is what makes it trustworthy.
```

---

## VI. THE CLINICAL OUTPUT

```
Every cancer analysis in this series
ends with the same type of output:

A PATIENT STRATIFICATION TOOL.

Not a paper.
Not a finding.
Not a statistical result.

A tool that a clinician can use
to put the right patient in
the right trial.

The tool has three components:

COMPONENT 1 — THE DEPTH SCORE
  A continuous variable from 0 to 1.
  Measures how far the tumor has
  traveled from its normal attractor.
  Computed from gene expression.
  Higher = deeper = more advanced
  molecular state.

COMPONENT 2 — THE CLINICAL PANEL
  A 3-gene approximation of the
  depth score.
  Measurable by standard IHC in
  any pathology laboratory.
  r > 0.85 with the full depth score
  in every validated cancer.
  The panel makes the depth score
  clinically deployable without
  RNA sequencing.

COMPONENT 3 — THE DRUG MAP
  Which drug class targets which
  depth stratum.
  Derived from depth correlations.
  Validated against clinical trial
  evidence in the literature check.
  Specifies:
    High depth → these drugs
    Intermediate depth → these drugs
    Low depth → these drugs
    Contraindicated drugs at each depth

These three components together
constitute a patient stratification
framework that:
  Can be implemented in a clinical
  trial as an enrollment criterion.
  Requires only standard pathology
  equipment (IHC).
  Is derived from public gene
  expression data by a reproducible
  computational process.
  Has been validated by convergence
  with independent experimental
  biology in every cancer in this series.

This is the output.
This is what the work is for.
```

---

## VII. HOW TO READ THIS REPOSITORY

```
THE DOCUMENTS IN EACH CANCER SERIES:

  Document [N]a — Script 1
    First contact with the data.
    Analyst predictions stated before
    data is loaded — verbatim.
    Script 1 results — verbatim.
    What was confirmed.
    What was wrong and what it taught.
    Corrected attractor description.
    New predictions for Script 2.
    Read this to understand the
    discovery process for this cancer.

  Document [N]b — Script 2
    The iteration.
    Corrected analysis based on
    Script 1 findings.
    Circuit integrity tests.
    Drug target depth correlations.
    The final attractor geometry.
    Novel predictions listed and dated
    before literature check.
    Read this to understand the
    therapeutic geometry of this cancer.

  Document [N]c — Literature Check
    All predictions locked before
    any searches are run.
    Each finding assessed against
    published literature.
    CONFIRMED: geometry and experiment agree.
    NOVEL: geometry found something
           not in literature.
    CONTRADICTED: geometry was wrong —
                  documented honestly.
    Read this to understand what
    the framework contributed vs
    what was already known.

  Document [N]d and beyond (where present)
    Additional scripts for specific
    analysis objectives.
    Survival analysis.
    Clinical panel validation.
    TF network analysis.
    Each follows the same structure:
    predictions before data,
    full output preserved,
    findings classified honestly.

  Document [N]e — Synthesis (where present)
    What this cancer taught the framework.
    What the framework found that
    literature had not yet assembled.
    The clinical tool that emerges
    from the full series.
    How this cancer fits into the
    cross-cancer pattern.
    Read this for the full meaning
    of the series.

THE WORKFLOW PROTOCOL:
  Workflow_Protocol.md
  The step-by-step reproducible process.
  Follow this to run a new cancer analysis.
  It contains:
    Phase 0: Dataset selection
    Phase 1: Biological predictions
    Phase 2: Script 1
    Phase 3: Script 2
    Phase 4: Literature check
    Phase 5: README update
    Quality checks at every transition
    10 accumulated framework lessons
    Wrong prediction protocol
    Reproducibility standard

THE README:
  Cross-cancer table with all validated
  cancers, switch genes, drug targets,
  and novel predictions.
  The summary view of the full series.
```

---

## VIII. THE REPRODUCIBILITY STANDARD

```
Every finding in this repository
can be reproduced by any investigator
who has:

  1. The GEO accession number
     (stated in every document header)
  2. The Python script
     (preserved exactly as run —
      never modified after execution)
  3. Python 3.8+ with standard
     scientific libraries
     (numpy, pandas, scipy, matplotlib)

No proprietary data.
No institutional access required.
No specialized bioinformatics tools.
No cloud compute.

The standard is:
  Run the script on the GEO data.
  Get the same numbers.
  That is reproducibility.

Not peer review.
Not journal publication.
Reproducible computation from public data.

This standard is strict because
the work is meant to be used —
not just read.

An investigator who wants to apply
this framework to a new cancer
should be able to read the protocol,
select a dataset, run the scripts,
and produce equivalent documents
without asking anyone how.

If the process is not reproducible
by a competent bioinformatician
following the protocol,
the process is not complete.
```

---

## IX. THE CROSS-CANCER PATTERN

```
Across 13 cancer validations,
several patterns have emerged
that hold across cancer types.
These are not assumptions —
they are empirical findings from
13 independent analyses.

PATTERN 1: FALSE ATTRACTOR UNIVERSALITY
  Every cancer analyzed has a
  measurable false attractor state.
  The depth score always separates
  tumor from normal.
  The depth score always correlates
  with known adverse prognostic markers.
  The false attractor is not
  specific to one cancer type —
  it is a general feature of
  malignant transformation.

PATTERN 2: DRUG TARGET DERIVATION
  In every cancer, the geometry-derived
  drug target has been confirmed by
  published pharmacology or active
  clinical trials.
  The framework finds approved targets
  from first principles in every case.
  This is not coincidence.
  It validates that depth correlations
  identify clinically meaningful
  molecular dependencies.

PATTERN 3: THE 3-GENE PANEL
  In every cancer, a 3-gene subset
  of the full depth score panel
  achieves r > 0.85 with the full score.
  The 3 genes are always clinically
  measurable by standard IHC.
  This pattern suggests the attractor
  geometry of cancer is concentrated
  in a small number of highly coupled
  genes — not distributed uniformly
  across thousands.
  The clinical deployability of the
  framework follows from this pattern.

PATTERN 4: EZH2 IS CANCER-SPECIFIC
  EZH2 is not a universal oncogene.
  In some cancers (BRCA, PAAD, PRAD):
    EZH2 elevated — gain-of-function lock
    EZH2 inhibitors are the target
  In other cancers (STAD in this dataset):
    EZH2 suppressed
    EZH2 inhibitors would worsen disease
  The direction of EZH2 change must
  be determined from data for each cancer.
  It cannot be assumed.

PATTERN 5: CIRCUIT INTEGRITY VARIES
  In some cancers (PAAD, PRAD):
    The master differentiation TF circuit
    is intact.
    Restoring the switch gene would
    execute the differentiation program.
    Circuit restoration is therapeutic.
  In other cancers (STAD):
    The circuit is broken.
    Restoring the switch gene would not
    execute the program.
    The downstream connections are
    uncoupled.
    Circuit restoration is not therapeutic.
    Attractor dissolution is the
    correct strategy.
  Circuit integrity must be tested
  for each cancer.
  It cannot be assumed from the
  identity of the switch gene alone.

PATTERN 6: NOVEL FINDINGS EMERGE
  In every cancer,
  the depth correlation analysis
  produces at least one finding that
  is not in the existing literature.
  These are not fabricated.
  They emerge from the geometry.
  They are credible because the
  same geometry also finds
  everything the literature already knew.
  The novel findings are the
  framework's contribution to the field.
```

---

## X. WHO THIS IS FOR

```
THIS REPOSITORY IS FOR:

CANCER RESEARCHERS
  Who want to understand the molecular
  geometry of a specific cancer before
  designing a clinical study.
  Use: read the cancer series documents.
  Start with Document [N]e if present.
  Read the depth correlation tables.
  The drug target depth map tells you
  which patients are most likely to
  respond to which agents.

CLINICAL TRIAL INVESTIGATORS
  Who want a patient selection framework
  based on molecular position not
  just histological diagnosis.
  Use: read Document [N]b for the
  depth score construction.
  Use: read Document [N]c for
  literature-validated drug targets.
  The 3-gene clinical panel is in
  every complete cancer series.
  Add it to your enrollment criteria.

BIOINFORMATICIANS
  Who want to apply this framework
  to a new cancer or new dataset.
  Use: read Workflow_Protocol.md first.
  Follow phases 0 through 5 exactly.
  Preserve all outputs unmodified.
  Document all predictions before data.
  The protocol is complete and
  self-contained.

ONCOLOGISTS
  Who want to understand why their
  patients respond differently to
  the same drug.
  Use: find your cancer type in
  the cross-cancer table.
  Read the depth-stratified drug map.
  The depth score separates patients
  by molecular position.
  Different positions have different
  dependencies.
  Same diagnosis — different geometry —
  different drug.

ANYONE SEEKING TO UNDERSTAND
THE FRAMEWORK
  Who wants to understand the
  principles behind the analysis.
  Read this document.
  Then read one complete cancer series
  from [N]a to [N]e.
  Follow the predictions through
  the corrections through the
  literature check.
  The process is the product.
  The reasoning is as important
  as the results.
```

---

## XI. THE GOAL

```
There is one goal.

It is not publications.
It is not citations.
It is not recognition of the method.

It is this:

  A patient with stomach cancer
  goes to a clinic.
  A pathologist runs three IHC stains:
  Ki67, ZEB2, ERBB4.
  The depth score is computed.
  The score is 0.71.
  The oncologist reads the drug map:
    Depth > 0.65:
    Alisertib + MCL1 inhibitor
    + anti-PD-L1.
    Not venetoclax — BCL2 is low
    at this depth.
    Not zolbetuximab — CLDN18 is lost
    at this depth.
  The patient receives the drugs
  that target their geometry.
  Not the drugs that target the
  average gastric cancer patient
  who does not exist.

  That is the goal.
  One patient at a time.
  Getting the right drug to the right
  molecular position.

The work in this repository is
the path from gene expression data
to that clinical moment.

Every script, every document,
every reasoning artifact,
every analyst error recorded
and every convergence found —
all of it serves that single purpose.

The work is not done when
the document is written.
It is done when the patient
receives the right drug.
```

---

## XII. CITATION AND USE

```
This work is open for use by any
investigator, clinician, or researcher
who wishes to apply the framework,
reproduce the analyses, or build
on the findings.

If you use this framework or
any finding from this series:
  Cite: Eric Robert Lawson,
        OrganismCore, 2026.
        [GEO accession of dataset used]
        [Document number of finding cited]

If you reproduce an analysis:
  Run from the GEO accession.
  Use the script as archived.
  Report your results alongside
  the original results.
  If your results differ — document why.
  Difference is information.

If you find an error:
  Open an issue in the repository.
  State the document number.
  State the finding.
  State the evidence for the error.
  Errors will be documented in the
  relevant document with the date
  of correction.
  Honest correction is part of
  the protocol.
  It is not a failure.
  It is how the framework improves.

If you extend the framework
to a new cancer:
  Follow Workflow_Protocol.md exactly.
  State all predictions before data.
  Preserve all outputs unmodified.
  Run the literature check after.
  Submit the documents to this
  repository or cite it in your
  own publication.
  The series grows by contribution.
```

---

## STATUS

```
document_type:      Framework orientation
                    Repository master document
version:            1.0
cancer_validations: 13 complete
                    AML, CML, CRC, GBM, BRCA,
                    LUAD, B-ALL, T-ALL, CLL,
                    MM, MDS, PAAD, PRAD, STAD
false_positive_rate: 0 in direction
                    across all 13 validations
drug_targets:       all confirmed by published
                    pharmacology or active trials
novel_predictions:  at least 1 per cancer type
protocol:           Workflow_Protocol.md
                    complete and self-contained
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
```
