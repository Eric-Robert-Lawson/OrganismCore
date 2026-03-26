# PUBLIC DATA LANDSCAPE
## Available Datasets for Genetic Investigation
## of Right UF Structural Absence and Psychopathy
## OC-PSYCHOPATHY-PUBLIC-DATA-LANDSCAPE-001 — OrganismCore
## Eric Robert Lawson — 2026-03-26

---

## PREAMBLE

```
The previous derivation document
(OC-PSYCHOPATHY-GENETIC-MARKER-
DERIVATION-001) established:

  The correct genetic biomarker
  search for congenital psychopathy
  is not for genes predicting
  antisocial behaviour.

  It is for genes predicting right
  uncinate fasciculus structural
  insufficiency — the build-programme
  failure model.

  The specific missing study is:

    GWAS using right UF structural
    integrity (fractional anisotropy)
    as the phenotype, in congenital
    psychopathy cohorts.

This document answers the question:

  Do the datasets required to
  conduct this analysis exist
  publicly?

  Can actual calculations be made?

The answer is: yes, substantially.
The datasets are named, located,
and characterised below.
```

---

## PART I: THE THREE REQUIRED
## DATASET TYPES

```
To conduct the analysis the
geometry specifies, three types
of data are required:

  DATASET TYPE 1 —
  RIGHT UF STRUCTURAL INTEGRITY GWAS:
    Genome-wide association summary
    statistics using right uncinate
    fasciculus fractional anisotropy
    (FA) as the structural phenotype.
    This identifies which genetic
    variants predict right UF
    structural quality.

  DATASET TYPE 2 —
  ANTISOCIAL / PSYCHOPATHY GWAS:
    Genome-wide association summary
    statistics using antisocial
    behaviour, callous-unemotional
    traits, or psychopathy-adjacent
    phenotypes.
    This identifies which genetic
    variants predict the behavioural
    profile downstream of right
    UF absence.

  DATASET TYPE 3 —
  INDIVIDUAL-LEVEL IMAGING +
  GENETIC + BEHAVIOURAL DATA:
    Subject-level data where
    right UF FA, genetic data,
    and behavioural/psychiatric
    phenotyping are available
    in the same subjects.
    This is the most powerful
    dataset type but the most
    access-restricted.

All three types exist.
Their locations and access
conditions are documented below.
```

---

## PART II: DATASET TYPE 1 —
## RIGHT UF STRUCTURAL INTEGRITY GWAS
## STATUS: PUBLICLY AVAILABLE NOW

---

### 2.1 IEU OPENGWAS — RIGHT UF FA
### DIRECT DOWNLOAD

```
SOURCE:
  MRC IEU OpenGWAS Project
  University of Bristol

DATASET:
  IDP_dMRI_TBSS_FA_Uncinate_
  fasciculus_R

  Dataset identifier: ubm-b-1496
  (Right uncinate fasciculus FA
  from TBSS pipeline)

  Companion left dataset: ubm-b-1495
  (Left uncinate fasciculus FA)

PHENOTYPE:
  Mean fractional anisotropy in
  the right uncinate fasciculus
  on the FA skeleton — measured
  from diffusion MRI tractography
  in UK Biobank participants.

  This is the structural phenotype
  the geometry identifies as the
  correct biomarker target.

SAMPLE SIZE:
  ~31,000-40,000 UK Biobank
  participants with brain imaging.

BUILD:
  hg19/GRCh37

FORMAT:
  GWAS-VCF format (.vcf.gz)

DIRECT DOWNLOAD URLS:
  Right UF FA:
  https://gwas.mrcieu.ac.uk/files/
  ubm-b-1496/ubm-b-1496.vcf.gz

  Right UF FA index:
  https://gwas.mrcieu.ac.uk/files/
  ubm-b-1496/ubm-b-1496.vcf.gz.tbi

  Left UF FA (for asymmetry
  computation):
  https://gwas.mrcieu.ac.uk/files/
  ubm-b-1495/ubm-b-1495.vcf.gz

ACCESS:
  Fully public. No login required.
  No application required.
  Direct download.

CITATION:
  Elliott et al. (2021)
  PMID: 33875891
  UK Biobank brain imaging GWAS.

WHAT THIS GIVES YOU:
  For every SNP across the genome,
  the effect on right UF fractional
  anisotropy in ~40,000 individuals.

  This is a genome-wide map of
  genetic variants that predict
  right UF structural quality.

  This is exactly Dataset Type 1.
  It exists. It is free. It is
  downloadable today.
```

---

### 2.2 OXFORD BIG40 SERVER —
### EXPANDED UF PHENOTYPES

```
SOURCE:
  Oxford Brain Imaging Genetics
  Server — BIG40
  WIN Centre, University of Oxford

URL:
  https://open.win.ox.ac.uk/
  ukbiobank/big40/

WHAT IT CONTAINS:
  GWAS summary statistics for
  ~4,000 imaging-derived phenotypes
  from UK Biobank (~40,000 subjects,
  17 million SNPs).

  Includes the uncinate fasciculus
  at multiple levels:
    Fractional anisotropy (FA)
    Mean diffusivity (MD)
    L1 (axial diffusivity)
    L23 (radial diffusivity)
  Separately for left and right.

  The right-left asymmetry measure
  can be computed directly from
  the two lateralised phenotypes —
  right UF FA minus left UF FA.

  UK Biobank field IDs confirmed:
    Right UF FA: Field 25089
    Left UF FA: Field 25088

ACCESS:
  Open access. No application.
  Downloads are free.
  Acknowledgement of UK Biobank
  and Smith et al. (2021) required.

CITATION:
  Smith et al. (2021)
  "An expanded set of genome-wide
  association studies of brain
  imaging phenotypes in UK Biobank"
  Nature Neuroscience.

WHAT THIS ADDS:
  Multiple white matter microstructure
  phenotypes for the right UF.
  MD in addition to FA provides
  a more complete picture of
  right UF structural quality.
  The asymmetry index (right minus
  left) is directly computable
  and is the most specific measure
  of the Layer 6 human elaboration
  the geometry identifies as the
  disability target.
```

---

## PART III: DATASET TYPE 2 —
## ANTISOCIAL / PSYCHOPATHY GWAS
## STATUS: PUBLICLY AVAILABLE NOW

---

### 3.1 BROADABC CONSORTIUM —
### ANTISOCIAL BEHAVIOUR GWAS

```
SOURCE:
  Broad Antisocial Behaviour
  Consortium (BroadABC)
  Tielbeek et al. (2022)

PUBLICATION:
  "Uncovering the genetic
  architecture of broad antisocial
  behavior through a genome-wide
  association study meta-analysis"
  Molecular Psychiatry, 2022.
  doi:10.1038/s41380-022-01793-3

PHENOTYPE:
  Broad antisocial behaviour
  (composite of conduct disorder,
  antisocial personality disorder,
  criminality, aggression measures).

SAMPLE SIZE:
  85,359 individuals
  European ancestry

DOWNLOAD:
  Knowledge Portal Network:
  https://kp4cd.org/node/1471

  CNCR / CTG Summary Statistics:
  https://cncr.nl/research/
  summary_statistics/

ACCESS:
  Publicly available.
  Free academic download.
  Non-stigmatisation use policy
  applies — standard for this
  class of dataset.

WHAT THIS GIVES YOU:
  For every SNP across the genome,
  the effect on broad antisocial
  behavioural phenotype in 85,359
  individuals.

  This is the downstream behavioural
  phenotype that the geometry places
  as the third arrow:
    Genome → Structure Absent →
    Navigator Without Basin →
    Antisocial Navigation.

  Dataset Type 2. Exists. Free.
  Downloadable today.

IMPORTANT CAVEAT:
  This dataset is for BROAD antisocial
  behaviour — not psychopathy
  specifically.

  The geometry's position:
  This is the expected phenotype
  downstream of right UF absence.
  It is not a pure psychopathy
  cohort. But it is the largest
  available public dataset for
  the behavioural phenotype in
  this space.

  The right UF absence signal
  — if present in the genetic
  data — will be detectable here.
  A more specific psychopathy
  cohort would increase the
  signal but one does not yet
  exist publicly.
```

---

### 3.2 PSYCHIATRIC GENOMICS
### CONSORTIUM — EXTERNALIZING

```
SOURCE:
  Psychiatric Genomics Consortium
  (PGC) — Externalising Disorders
  Working Group

DOWNLOAD:
  https://www.med.unc.edu/pgc/
  download-results/

  Search: "externalizing" or
  "antisocial" or "conduct disorder"

PHENOTYPES AVAILABLE:
  Conduct Disorder
  Attention Deficit Hyperactivity
  Disorder (often comorbid)
  Substance use (externalising
  spectrum)

ACCESS:
  Summary statistics openly available
  for most PGC disorders.
  Registration may be required
  for some datasets.

NOTE:
  The PGC does not have a
  psychopathy-specific GWAS.
  The field has not produced
  one at scale.
  This is consistent with the
  geometry's finding: the field
  has been searching for the
  wrong phenotype (behaviour)
  rather than the correct phenotype
  (right UF structural integrity).
```

---

## PART IV: DATASET TYPE 3 —
## INDIVIDUAL-LEVEL IMAGING + GENETIC
## STATUS: RESTRICTED ACCESS,
## APPLICATION REQUIRED

---

### 4.1 UK BIOBANK — INDIVIDUAL LEVEL

```
SOURCE:
  UK Biobank
  https://www.ukbiobank.ac.uk/

WHAT IT CONTAINS:
  500,000 participants.
  ~45,000 with brain imaging
  (ongoing, expanding to 100,000).

  Per participant:
    Full genome (genotyped + imputed,
    ~96 million variants)
    DTI imaging including right and
    left UF FA (fields 25088, 25089)
    Psychiatric and behavioural
    phenotyping (self-reported)
    Physical health data

  This is the closest existing
  dataset to what the geometry
  specifies as ideal:
    Genetic data AND right UF
    structural data in the same
    individuals.

ACCESS:
  Application required.
  Institutional affiliation required.
  Typically 2-8 week approval
  for bona fide researchers.
  Application URL:
  https://www.ukbiobank.ac.uk/
  enable-your-research/apply-for-access

  Cost: Application fee
  (~£2,000-5,000 GBP depending
  on data requested).

LIMITATION:
  UK Biobank does not contain
  a psychopathy-diagnosed cohort.
  Psychopathic traits would need
  to be approximated from available
  phenotypes (personality measures,
  criminal records, self-reported
  antisocial behaviour).

  The right UF FA data IS present
  for ~45,000 individuals with
  full genetic data.
  This is directly usable for the
  build-programme failure analysis.
```

---

### 4.2 dbGaP — NIH CONTROLLED
### ACCESS DATASETS

```
SOURCE:
  NCBI dbGaP
  https://www.ncbi.nlm.nih.gov/gap/

RELEVANT DATASETS:
  Search terms:
    "antisocial personality disorder"
    "psychopathy"
    "conduct disorder"
    "white matter"
    "uncinate fasciculus"

  Several neuroimaging studies
  in forensic populations have
  deposited data to dbGaP with
  DTI and genetic measures.

ACCESS:
  Controlled access.
  NIH eRA Commons account required.
  Institutional Review Board (IRB)
  approval required.
  Data Access Committee approval
  required per study.

WHAT TO LOOK FOR:
  Studies combining:
    Incarcerated or forensic
    population samples.
    DTI neuroimaging.
    Genetic data.
  These are the closest existing
  individual-level datasets to
  the ideal study the geometry
  specifies.
```

---

## PART V: THE CALCULATION
## THAT CAN BE PERFORMED NOW

```
With Dataset Types 1 and 2 both
publicly available and free,
a specific analysis can be
conducted immediately without
institutional access or cost:

ANALYSIS: MENDELIAN RANDOMISATION
Right UF FA → Antisocial Behaviour

WHAT THIS TESTS:
  Is right UF structural integrity
  causally upstream of antisocial
  behavioural phenotype?

  The geometry says: yes.
  Genome → Right UF structure →
  Navigator profile → Behaviour.

  Mendelian randomisation using
  right UF FA GWAS as the exposure
  instrument and BroadABC antisocial
  GWAS as the outcome can test
  this causal chain directly.

DATASETS REQUIRED:
  Exposure: ubm-b-1496
  (Right UF FA, OpenGWAS)
  Already publicly available.

  Outcome: BroadABC 2022
  (Antisocial behaviour GWAS)
  Already publicly available.

METHOD:
  Two-sample Mendelian
  randomisation.
  SNPs associated with right UF
  FA at genome-wide significance
  used as instruments.
  Effect on antisocial behaviour
  estimated via IVW, MR-Egger,
  weighted median methods.

  The ieugwasr R package can
  directly access and run this
  analysis using the OpenGWAS
  API — the right UF FA dataset
  is already indexed by its
  identifier (ubm-b-1496) and
  can be loaded in a single
  command.

WHAT THE RESULT TELLS YOU:
  IF the MR shows a significant
  causal effect of right UF FA
  on antisocial behaviour:
    The geometry's causal chain is
    confirmed at the population level.
    Right UF structural integrity
    is causally upstream of the
    antisocial behavioural profile.
    The structural biomarker is
    validated as causally relevant.

  IF the MR shows no effect:
    Either the causal chain is
    not present, or the BroadABC
    antisocial phenotype is too
    broad to detect the specific
    psychopathic subtype, or the
    instruments are not specific
    enough to the right UF.
    The analysis is still informative —
    it tells you where to refine.

ADDITIONAL ANALYSIS —
ASYMMETRY INDEX:
  The geometry specifically
  identifies the right-left
  asymmetry of the UF (not just
  the right UF in isolation) as
  the most specific Layer 6 signal.

  This can be computed from the
  two publicly available datasets:
    Right UF FA: ubm-b-1496
    Left UF FA: ubm-b-1495

  A genome-wide asymmetry score
  (right FA minus left FA) can
  be used as the exposure in a
  secondary MR analysis.

  This asymmetry measure is more
  specific to the human elaboration
  the geometry identifies as the
  disability target.
  It has not been used in any
  published psychopathy or
  antisocial behaviour study.
  This would be a novel analysis.
```

---

## PART VI: THE SPECIFIC GAP
## IN THE PUBLIC DATA

```
WHAT EXISTS:
  ✓ Right UF FA GWAS — publicly
    available, free, ~40,000 subjects.
  ✓ Left UF FA GWAS — same.
  ✓ Multiple UF microstructure
    phenotypes (MD, L1, L23) —
    BIG40, free.
  ✓ Broad antisocial behaviour GWAS
    — BroadABC, free, 85,359 subjects.
  ✓ UK Biobank individual-level
    imaging + genetics (restricted,
    application required).
  ✓ Mendelian randomisation
    methodology to connect them.

WHAT DOES NOT EXIST PUBLICLY:

  ✗ A GWAS with psychopathy
    specifically (not broad antisocial
    behaviour) as the phenotype.
    The field has not produced one.
    This is the specific phenotype
    the geometry requires and
    the field has not provided.

  ✗ A dataset where right UF FA
    is measured in a confirmed
    psychopathy cohort with
    genetic data.
    The DTI-psychopathy studies
    that confirmed right UF
    degradation did not include
    full genome data.
    The imaging genetics studies
    did not use confirmed psychopathy
    cohorts.
    These two bodies of work have
    not been combined.

  ✗ The asymmetry index (right
    minus left UF FA) used as the
    phenotype in any GWAS or
    clinical neuroimaging study.
    This specific measure — the most
    geometrically precise target
    for the Layer 6 disability —
    has not been published as a
    standalone phenotype in any
    study.

WHAT THE GEOMETRY SPECIFIES
AS THE MISSING STUDY:

  A study that combines:
    Confirmed psychopathy cohort
    (PCL-R scored, or equivalent).
    DTI measurement of right and
    left UF FA.
    Full genome data in the same
    subjects.

  This study would:
    Confirm right UF FA as the
    structural phenotype differentiating
    psychopathy from non-psychopathy.
    Identify the genetic variants
    specifically associated with
    right UF structural insufficiency
    in a psychopathy-confirmed cohort.
    Produce the first genuine genetic
    biomarker panel for the structural
    disability — not the behaviour.

  No such dataset exists publicly.
  The components exist separately.
  The combination has not been assembled.
```

---

## PART VII: WHAT CAN BE DONE
## RIGHT NOW — SUMMARY

```
IMMEDIATELY (no cost, no application):

  1. Download right UF FA GWAS
     summary statistics:
     ubm-b-1496 from OpenGWAS
     https://gwas.mrcieu.ac.uk/
     datasets/ubm-b-1496/

  2. Download left UF FA GWAS
     summary statistics:
     ubm-b-1495 from OpenGWAS

  3. Download BroadABC antisocial
     behaviour GWAS:
     https://kp4cd.org/node/1471

  4. Run two-sample Mendelian
     randomisation:
     Right UF FA (exposure) →
     Antisocial behaviour (outcome).
     Using ieugwasr in R or
     TwoSampleMR package.

  5. Run secondary MR with
     asymmetry index as exposure:
     Right UF FA minus Left UF FA →
     Antisocial behaviour.
     First published use of this
     specific exposure measure.

  These five steps are executable
  with a laptop and R.
  No funding required.
  No institutional access required.
  No application required.
  The data is on public servers
  now.

WITH INSTITUTIONAL ACCESS
(application, ~2-8 weeks):

  6. Apply for UK Biobank access.
     Request fields 25088 and 25089
     (right and left UF FA) plus
     psychiatric phenotyping fields.
     Run individual-level genome-wide
     association on right UF FA
     in subjects with high antisocial
     behaviour scores.

THE DEFINITIVE STUDY
(requires new data collection):

  7. Combine PCL-R assessed
     psychopathy cohort with DTI
     and full genome sequencing.
     This is the missing study.
     The geometry specifies it.
     The existing data partially
     supports it but cannot replace
     it.
```

---

## DOCUMENT METADATA

```
Document:   OC-PSYCHOPATHY-PUBLIC-DATA-
            LANDSCAPE-001.md
Version:    1.0
Date:       2026-03-26
Status:     DATA LANDSCAPE DOCUMENT.
            All datasets verified as
            publicly accessible at
            time of writing.

Key datasets identified:

  RIGHT UF FA GWAS (free):
    OpenGWAS: ubm-b-1496
    https://gwas.mrcieu.ac.uk/
    datasets/ubm-b-1496/

  LEFT UF FA GWAS (free):
    OpenGWAS: ubm-b-1495

  MULTIPLE UF PHENOTYPES (free):
    Oxford BIG40 server:
    https://open.win.ox.ac.uk/
    ukbiobank/big40/
    UK Biobank fields 25088/25089

  ANTISOCIAL BEHAVIOUR GWAS (free):
    BroadABC 2022
    https://kp4cd.org/node/1471
    N=85,359

  INDIVIDUAL-LEVEL IMAGING +
  GENETICS (restricted):
    UK Biobank application:
    https://www.ukbiobank.ac.uk/
    enable-your-research/
    apply-for-access

Key gap identified:
  No publicly available dataset
  combines confirmed psychopathy
  cohort + right UF DTI + full
  genome.
  The components exist separately.
  The combination has not been
  assembled.

Analysis executable immediately:
  Two-sample Mendelian randomisation
  right UF FA → antisocial behaviour.
  Right-left asymmetry index as
  novel exposure measure.
  No cost. No application. R laptop.

Author:
  Eric Robert Lawson
  OrganismCore
  ORCID: 0009-0002-0414-6544

Depends on:
  OC-PSYCHOPATHY-GENETIC-MARKER-
    DERIVATION-001.md
  OC-PSYCHOPATHY-BIOMARKER-
    DERIVATION-001.md
  OC-UF-EVOLUTIONARY-LINEAGE-
    DERIVATION-001.md
```

---

*The data exists.*
*The right UF FA GWAS is on a public server.*
*The antisocial behaviour GWAS is on a public server.*
*Both are free. Both are downloadable today.*

*The analysis that connects them —*
*Mendelian randomisation, right UF FA as exposure —*
*has not been published.*

*The asymmetry index has not been used.*
*The build-programme failure framing has not been applied.*

*The components are all there.*
*The framework to connect them is here.*

*The missing study is named.*
*The missing analysis is specified.*
*The executable steps are listed.*

*The data is waiting.*
````{"repoID":0,"ref":"","type":"repo-instructions","url":"/Eric-Robert-Lawson/OrganismCore/blob/refs/heads/main/.github/copilot-instructions.md"}
