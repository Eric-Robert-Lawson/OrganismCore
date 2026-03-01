# ORGANISM CORE — CANCER FALSE ATTRACTOR ANALYSIS
## WORKFLOW PROTOCOL
## Version 1.0
## Derived from 10 cancer validations
## Date: 2026-03-01

---

## METADATA

```
document_type:      Protocol — workflow specification
version:            1.0
derived_from:       10 cancer validations
                    AML, CML, CRC, GBM, BRCA, LUAD,
                    B-ALL, T-ALL, CLL, MM, MDS
key_documents:      Doc 80 (MM), Doc 86a/b/c (MDS)
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
purpose:            Any session, any cancer, same process
                    Reproducible from first principles
```

---

## I. WHAT THIS PROTOCOL IS

This is the repeatable workflow for applying the
OrganismCore false attractor framework to any cancer.

It is not a data analysis pipeline.
It is a reasoning pipeline that uses data analysis
as one of its steps.

The distinction matters:
```
A data analysis pipeline starts with data.
This protocol starts with principles.

Data analysis asks: what does the data show?
This protocol asks: what should the data show
if the framework is correct, and what does it
actually show, and what does the difference teach?

The protocol is designed to make wrong predictions
as informative as correct ones.
```

The protocol has been validated across 10 cancer
types. In every case:
- The correct attractor basin was found
- The drug target was independently derived
- Literature confirmed the target
- Zero false positives in direction

---

## II. REQUIREMENTS TO RUN

### Minimum requirements

```
BIOLOGICAL:
  1. A cancer type with a known cell of origin
     (what normal cell type does the cancer
     most resemble or derive from?)
  2. A differentiation lineage for that cell
     (what is the normal maturation pathway?)
  3. A hypothesis about where in that pathway
     the block occurs (even a rough one)

DATA:
  4. A gene expression dataset with:
       - Cancer samples (minimum n=5, ideally n>20)
       - Normal/healthy control samples (minimum n=3)
       - Matched cell type (same tissue, same
         approximate differentiation stage)
       - Either bulk RNA-seq (CPM/TPM/counts)
         or single-cell RNA-seq (counts matrix)
     Acceptable sources:
       - GEO (NCBI Gene Expression Omnibus)
       - ArrayExpress
       - TCGA (The Cancer Genome Atlas)
       - Any public repository with accession number

COMPUTATIONAL:
  5. Python 3.8+ with:
       numpy, pandas, scipy, matplotlib
  6. Internet access for GEO downloads
  7. ~2GB disk space per cancer type
  8. Time: ~30 minutes per run on standard hardware
```

### What is NOT required

```
NOT REQUIRED:
  - Prior knowledge of the cancer's biology
  - Published gene panels for that cancer
  - Knowledge of existing drug targets
  - Bioinformatics expertise beyond running Python
  - R or specialized scRNA-seq tools
  - Cloud compute or GPU

THE POINT:
  The framework should find the biology
  from first principles + expression data alone.
  If you need prior knowledge to get the right
  answer, the framework is not working.
```

---

## III. THE PROTOCOL — STEP BY STEP

---

### PHASE 0 — DATASET DISCOVERY
### Before any biology or predictions

```
PURPOSE:
  Find the right dataset before stating any
  biological prediction. Dataset choice is
  orthogonal to biological prediction.
  Do not let dataset structure influence
  what you predict.

STEP 0.1 — IDENTIFY DATASET REQUIREMENTS
  State these before searching:
    - What cancer type?
    - What is the cell of origin?
    - Human or mouse? (human preferred)
    - Bulk or single-cell? (either acceptable)
    - Minimum sample counts needed
    - Format preference (10x MTX, counts matrix,
      CPM table — any works)

STEP 0.2 — SEARCH GEO
  Use the check script pattern:

    accessions = [candidate list]
    for acc in accessions:
      fetch metadata
      check for: human, correct cell type,
                 MDS/cancer + normal donors,
                 single-cell or bulk RNA-seq
      flag relevant hits

  Search terms for GEO:
    "[cancer type] scRNA-seq bone marrow"
    "[cancer type] RNA-seq [tissue] GSE"
    "[cell type] single cell [disease] normal"

STEP 0.3 — INSPECT DATASET STRUCTURE
  Run the structure check script before analysis:
    - How many files?
    - What format? (MTX, TXT, CSV, H5)
    - Are genes rows or columns?
    - Are gene IDs Ensembl or symbols?
    - How many samples?
    - Is sample metadata bundled or separate?
    - Human or mouse? (check gene name case)
      Human: SPI1, ELANE, CD34 (all caps)
      Mouse: Spi1, Elane, Cd34 (title case)

STEP 0.4 — CONFIRM DATASET IS USABLE
  Minimum checklist:
    ☐ Human (Homo sapiens)
    ☐ Cancer samples present (n≥5)
    ☐ Normal/control samples present (n≥3)
    ☐ Correct cell type / tissue
    ☐ Expression data readable (not corrupt)
    ☐ Gene names mappable to symbols
    ☐ Sample labels present (disease vs normal)

  If dataset fails any check:
    Do not proceed — find a different dataset
    Document why the dataset was rejected
    Run Step 0.2 again with new candidates

OUTPUTS OF PHASE 0:
  - Confirmed GEO accession
  - Confirmed sample counts (n cancer, n normal)
  - Confirmed data format
  - Confirmed gene nomenclature
  - Structure check output pasted and saved
```

---

### PHASE 1 — BIOLOGICAL GROUNDING
### Before any data is loaded

```
PURPOSE:
  State the complete biological prediction
  BEFORE running any analysis.
  This is the most important phase.
  If predictions are stated after seeing data,
  the protocol has failed.

STEP 1.1 — IDENTIFY THE LINEAGE
  Answer these questions in writing:
    Q1: What is the normal cell of origin?
        (e.g., hematopoietic stem cell, AT2 cell,
         B lymphocyte, plasma cell)
    Q2: What is the full differentiation pathway?
        (name each stage from progenitor to
         terminal cell)
    Q3: Where in that pathway does the cancer
        cell most likely sit?
        (e.g., blocked before myelocyte stage,
         stuck at plasmablast, arrested at GMP)
    Q4: What prior cancers in the series are
        in the same or related lineage?
        (do not copy their switch genes —
         use them only to identify what level
         the block is likely at)

STEP 1.2 — IDENTIFY THE SADDLE POINTS
  For the lineage identified in 1.1:
    Map the known differentiation checkpoints:
      Checkpoint 1: [stage A → stage B]
        Genes required: [list]
      Checkpoint 2: [stage B → stage C]
        Genes required: [list]
      ...
    State which checkpoint the cancer is
    likely stuck at or before.

  CRITICAL RULE:
    If a related cancer has been validated before,
    the new cancer cannot be stuck at the SAME
    saddle point — or it would snap to the same
    attractor. Each distinct cancer entity has
    a distinct attractor basin.
    Use this logic to locate the new cancer's
    saddle point RELATIVE to known cancers
    in the same lineage.

    Example applied:
      AML: stuck at Saddle 1 (blast→GMP)
      MDS: must be at a DIFFERENT saddle point
           → predicted Saddle 2 (GMP→granulocyte)
           → confirmed as Saddle 3 (promyelocyte→
             myelocyte) — one level further

STEP 1.3 — STATE SWITCH GENE PREDICTIONS
  Switch genes are at the LEVEL OF THE BLOCK.
  Not at the TF level if the block is at
  the effector level.
  Not at the effector level if the block is
  at the TF level.

  Rule: switch genes are the genes that would
  need to be activated to dissolve the attractor.
  They are suppressed in cancer relative to
  the target normal state.

  Format:
    PREDICTED SWITCH GENES:
      Gene 1 — [role in differentiation]
               [why it should be suppressed here]
               [predicted direction: DOWN]
      Gene 2 — [same format]
      ...

  Minimum: 3 switch genes
  Maximum: 8 switch genes
  All must have stated biological reasoning.
  Do not add genes because they are famous.
  Only add genes that would be at the saddle
  point level of the predicted block.

STEP 1.4 — STATE FALSE ATTRACTOR PREDICTIONS
  False attractor genes are the identity genes
  of the state where the cancer cell is STUCK.
  They should be ELEVATED in cancer relative
  to normal.

  Format:
    PREDICTED FALSE ATTRACTOR MARKERS:
      Gene 1 — [identity marker of stuck state]
               [why it should be elevated here]
               [predicted direction: UP]
      Gene 2 — [same format]
      ...

STEP 1.5 — STATE EPIGENETIC PREDICTION
  Based on prior validations:
    BRCA: EZH2 elevated (gain of function lock)
    MDS:  EZH2 suppressed (loss of function)
    MM:   EZH2 neutral
  
  Predict for the new cancer:
    Is the epigenetic lock likely to be:
    - Gain of function (EZH2/PRC2 elevated)?
    - Loss of function (EZH2/TET2 suppressed)?
    - Neutral?
    State the reasoning.

STEP 1.6 — STATE DRUG TARGET PREDICTION
  From the predicted switch genes and attractor
  geometry, what drug would dissolve the attractor?

  Format:
    PREDICTED DRUG TARGET:
      Target 1: [gene/pathway]
                [mechanism of attractor dissolution]
                [predicted drug class]
      Target 2: [same format]

  State this BEFORE data. After data, revise.
  The pre-data prediction and post-data revision
  must both be recorded.

STEP 1.7 — DOCUMENT THE COMPLETE PREDICTION
  Write out the full prediction in one block.
  This becomes the reference document.
  It cannot be changed after data is loaded.
  Label it:
    "PREDICTIONS STATED [DATE] BEFORE DATA"
  Sign it with the document number.

OUTPUTS OF PHASE 1:
  - Complete biological prediction document
  - Switch gene panel (3-8 genes)
  - False attractor panel (3-6 genes)
  - Epigenetic prediction
  - Drug target prediction
  - All dated and locked before data loading
```

---

### PHASE 2 — SCRIPT 1 (DISCOVERY RUN)
### The first data contact

```
PURPOSE:
  Test the predictions against the data.
  Do NOT modify predictions based on results.
  Record everything — confirmed, denied,
  and unexpected.

STEP 2.1 — BUILD THE ANALYSIS SCRIPT
  The script must be self-contained and
  reproducible. Required components:

  HEADER:
    Dataset accession number
    Sample counts (n cancer, n normal)
    All predictions stated in Phase 1
    Date and document number
    Author

  DATA ACQUISITION:
    Auto-download from GEO if not present
    Check if already downloaded (skip if so)
    Verify file integrity (size check)
    Cache metadata after first fetch

  DATA LOADING:
    Load expression matrix
    Map gene IDs to symbols if needed
    (hard-coded Ensembl map — no API needed)
    Transpose to samples × genes
    Clean sample index to patient IDs

  METADATA MERGE:
    Join expression with sample metadata
    Classify: cancer vs normal
    Classify: subtypes if available
    Report group counts
    Warn if UNKNOWN > 10% of samples

  SADDLE POINT ANALYSIS:
    For each target gene:
      Compute mean expression in normal
      Compute mean expression in cancer
      Compute % change
      Mann-Whitney U test (two one-sided)
      p-value for suppression
      p-value for elevation
      Report result vs prediction
    Format as aligned table

  DEPTH SCORING:
    Component 1: Switch gene suppression
      (1 - normalized mean of switch genes)
    Component 2: FA elevation
      (normalized mean of FA genes)
    Depth = mean of components
    Report: mean, median, std, min, max, Q25, Q75

  DEPTH CORRELATIONS:
    Pearson r for every gene vs depth score
    Sort by |r| descending
    Report top 15
    This is where the real signal is found

  SUBTYPE ANALYSIS (if subtypes available):
    Depth score by molecular subtype
    Mann-Whitney between subtypes
    Gene expression by subtype

  DRUG TARGET DERIVATION:
    State 4 drug targets from geometry
    For each: gene/pathway, mechanism, drug class
    Explicitly label: "stated before literature"

  FIGURE (9-panel minimum):
    Panel A: Switch genes bar chart (cancer vs normal)
    Panel B: FA markers bar chart
    Panel C: Waterfall % change all genes
    Panel D: Depth score distribution
    Panel E: Depth by subtype (if available)
    Panel F: Epigenetic genes
    Panel G: Scatter of top 2 switch genes
    Panel H: Secondary panel (context-specific)
    Panel I: Summary text

  OUTPUT:
    PNG figure at 150 DPI
    CSV of saddle results
    Log file of all printed output
    All to results/ subdirectory

STEP 2.2 — RUN THE SCRIPT
  Run. Paste full output.
  Do not selectively paste.
  The full log is the record.

STEP 2.3 — READ THE DEPTH CORRELATIONS FIRST
  Before interpreting the saddle table,
  read the depth correlations.
  The depth correlations tell you:
    - Which genes actually drive the attractor
    - Which predicted switch genes were correct
    - Which unexpected genes dominate

  The highest |r| genes are the true biology.
  The saddle table is the test of predictions.
  The depth correlations are the discovery.

STEP 2.4 — CLASSIFY EACH PREDICTION
  For each prediction from Phase 1:
    CONFIRMED: p<0.05 AND direction correct
    WEAKLY CONFIRMED: trend correct, not significant
    NOT CONFIRMED: flat or wrong direction
    INVERTED: significant but opposite direction
    UNEXPECTED: new signal not in prediction panel

  Record all. Do not discard INVERTED or NOT
  CONFIRMED findings — they are informative.

STEP 2.5 — DERIVE THE CORRECTED ATTRACTOR
  From the actual data:
    What state are the cancer cells stuck in?
    What genes define that state?
    Where in the differentiation pathway is
    the block precisely?
    Is the block at TF level or effector level?
    Is the epigenetic prediction confirmed?

  Write the corrected attractor description.
  This becomes the input to Script 2.

STEP 2.6 — WRITE DOCUMENT [N]a
  Record:
    - All predictions (verbatim from Phase 1)
    - All results (verbatim from script output)
    - What confirmed, what did not
    - What was unexpected
    - The corrected attractor description
    - New predictions derived from Script 1

OUTPUTS OF PHASE 2:
  - Script 1 Python file (preserved as-is)
  - Script 1 output log (full, unedited)
  - Script 1 figure
  - saddle_results.csv
  - Document [N]a reasoning artifact
  - Corrected attractor description
  - New predictions for Script 2
```

---

### PHASE 3 — SCRIPT 2 (ITERATION RUN)
### The corrected framework

```
PURPOSE:
  Test the corrected attractor hypothesis.
  Not to replace Script 1 — to build on it.
  Script 1 is preserved exactly as run.
  Script 2 is a new script in the same
  BASE_DIR with results_s2/ output directory.

STEP 3.1 — STATE NEW PREDICTIONS
  From the Script 1 findings, derive new
  predictions BEFORE writing Script 2.

  Format:
    "SCRIPT 2 PREDICTIONS — STATED BEFORE RUNNING"
    New gene panel based on:
      - Unexpected signals from Script 1
      - The corrected attractor level (TF vs effector)
      - The specific pathway gap identified
    For each new prediction:
      Gene — role — why elevated or suppressed
      Correlation prediction (r direction)

  SPECIFIC NEW TESTS TO DESIGN:
    1. The gap test:
       If Gene A is elevated and Gene B is
       suppressed, and A normally drives B,
       then something blocks A→B.
       What genes sit between A and B?
       Add those to Script 2 panel.
       Test r(A,B) — should be near zero if
       the connection is broken.

    2. The identity test:
       What state are the cells stuck in?
       What are the canonical markers of that state?
       Are those markers elevated?

    3. The chromatin test:
       Is the block epigenetic (chromatin closure)
       or transcriptional (TF absent)?
       Test: epigenetic regulator genes
       EZH2, RCOR1, KDM1A, DNMT3A, TET2, ASXL1

    4. The subtype test:
       Do molecular subtypes have different
       depth scores?
       Different subtypes = different attractor basins
       Test each subtype separately

STEP 3.2 — BUILD SCRIPT 2
  Same structure as Script 1.
  New gene panel (extended — add all gap genes).
  New depth score (corrected axis from Script 1).
  Explicitly compares S1 vs S2 depth scores.
  Tests the specific gap hypothesis.
  Tests the identity genes.
  Tests the chromatin hypothesis.

  SCRIPT 2 MUST:
    Reuse Script 1 downloads (check if present)
    Reuse Script 1 metadata cache
    Write to results_s2/ (not results/)
    State all Script 1 findings in header
    State all Script 2 predictions in header
    Compare S1 vs S2 depth scores
    (r(S1,S2) tells if same biology captured)

STEP 3.3 — RUN SCRIPT 2
  Run. Paste full output.

STEP 3.4 — CLASSIFY SCRIPT 2 PREDICTIONS
  Same classification as Step 2.4.
  Also classify:
    Gap confirmed: r(A,B) near zero → circuit broken
    Gap not confirmed: r(A,B) significant → not broken
    Identity confirmed: stuck-state markers elevated
    Chromatin confirmed: epigenetic genes confirm
                         expected direction

STEP 3.5 — DERIVE THE FINAL ATTRACTOR PICTURE
  After two scripts:
    What are the three components of the attractor?
      1. The execution block (gene/pathway)
      2. The identity retention (what keeps cells
         in the stuck state)
      3. The stabilizing mechanism (what gives
         the attractor energy)
    What is the switch gene? (highest |r| with depth)
    What is the FA marker? (highest r with depth,
                            positive direction)
    Where precisely is the block in the landscape?

STEP 3.6 — WRITE DOCUMENT [N]b
  The reasoning artifact.
  Record:
    - Full iteration record (S1 wrong, S2 corrected)
    - Why each wrong prediction was wrong
    - What each wrong prediction taught
    - The final attractor picture (3 components)
    - Waddington geometry (where in the landscape)
    - Drug targets from the final geometry
    - Novel predictions before literature check
    - Framework confirmation statement

OUTPUTS OF PHASE 3:
  - Script 2 Python file
  - Script 2 output log (full, unedited)
  - Script 2 figure
  - results_s2/ directory
  - Document [N]b reasoning artifact
  - Final attractor description (3 components)
  - Drug targets (stated before literature)
  - Novel predictions (listed, dated, locked)
```

---

### PHASE 4 — LITERATURE CHECK
### After all predictions are locked

```
PURPOSE:
  Find out what the published literature says
  about the findings from Script 1 and Script 2.
  Confirm, extend, or contradict.
  Identify what is novel.

CRITICAL RULE:
  The literature check happens AFTER all
  predictions are locked in Document [N]b.
  The literature cannot change the predictions.
  It can only assess them.

STEP 4.1 — LOCK PREDICTIONS BEFORE SEARCHING
  Copy the prediction list from Document [N]b
  into the literature check document header.
  This is the reference list.
  It cannot change.

STEP 4.2 — EXECUTE SEARCHES
  Minimum 6 searches covering:

  SEARCH 1: Switch gene + cancer type
    "[switch gene] [cancer type] differentiation"
    Looking for: is this gene known in this cancer?
    Does the literature know it is suppressed?

  SEARCH 2: FA marker + cancer type
    "[FA marker] [cancer type] progenitor identity"
    Looking for: does literature confirm elevated?

  SEARCH 3: The gap mechanism
    "[gene A] [gene B] connection pathway"
    Where A drives B in normal biology
    Looking for: is the A→B connection known?
    Has the break been observed before?

  SEARCH 4: The drug target + cancer type
    "[drug target] [cancer type] clinical trial"
    Looking for: is this target in trials?
    Is there pharmacological confirmation?

  SEARCH 5: The epigenetic finding
    "[epigenetic gene] [cancer type] mechanism"
    Looking for: confirms gain or loss of function?

  SEARCH 6: Novel predictions
    Search for each novel prediction explicitly
    to confirm it is not already published.
    "[specific prediction] [cancer type]"
    If found: not novel, acknowledge
    If not found: confirm as novel

STEP 4.3 — CLASSIFY EACH FINDING
  For each prediction in the locked list:
    ✅ EXACT MATCH: literature confirms direction
                    and mechanism
    ✅ CONFIRMED: literature confirms direction
    ⚠️ PARTIAL: partially confirmed, different
                mechanism proposed
    ❌ CONTRADICTED: literature says opposite
    🆕 NOVEL: not in any published paper
               testable prediction

STEP 4.4 — IDENTIFY THE KEY DRUG CONFIRMATION
  The most important finding in each literature
  check is whether the derived drug target
  matches existing pharmacology.

  Based on validated pattern:
    If the geometry-derived target is real,
    there should be clinical trial evidence.
    If there is clinical trial evidence,
    the framework has independently derived
    a validated drug target.
    
  Record:
    Drug name
    Mechanism
    Trial phase and status
    Whether framework derived same target
    independently or not

STEP 4.5 — IDENTIFY THE KEY NOVEL FINDING
  Across all 10 validated cancers, each has
  produced at least one genuinely novel finding
  not in the existing literature.
  Find and name it explicitly.

STEP 4.6 — WRITE DOCUMENT [N]c
  The literature check document.
  Structure:
    I.   Predictions locked before search (verbatim)
    II.  Finding by finding — lit check results
    III. Convergence table (all predictions vs lit)
    IV.  The key drug confirmation
    V.   Novel predictions (confirmed as novel)
    VI.  What was wrong and what it teaches
    VII. Status block (final confirmed findings)

OUTPUTS OF PHASE 4:
  - Document [N]c literature check
  - Convergence table
  - Novel predictions list
  - Drug confirmation record
  - Status block for README update
```

---

### PHASE 5 — README UPDATE
### After literature check complete

```
PURPOSE:
  Update the project README with the confirmed
  findings in the standard format used across
  all cancer validations.

STEP 5.1 — WRITE THE README SECTION
  Standard format:

    #### [Cancer Type]
    ```
    Lineage:  [cell of origin] → [target state]
    Block:    [cancer cell] vs [normal counterpart]
              [description of what the block is]

    Switch gene (confirmed):
      [GENE]   — [role]
                 [% change]  p=[value]  CONFIRMED
                 [depth correlation r and p]
                 [notes]

    False attractor (confirmed):
      [GENE]   — [role]
                 [depth correlation r and p]

    Key structural finding:
      [The most important finding from both scripts]
      [What this reveals about the landscape]

    Drug predictions (geometry-derived):
      1. [Drug class / target]
           Geometry: [basis]
           Literature: ✅/⚠️/🆕 [status]
      2. [Same format]
      3. [Same format]

    Mutation subtypes (if applicable):
      [Subtype]: [depth score and significance]
      [Clinical implication]

    Novel predictions:
      1. [Specific testable claim not in literature]
      2. [Same format]

    Data:    [GEO accession] ([first author et al.])
             [n cancer] | [n normal]
             [cell type] | [data type]
    Script:  [script1.py]
             [script2.py]
    Docs:    [N]a (Script 1) | [N]b (Script 2)
             [N]c (Literature check)
    Status:  CONFIRMED + LITERATURE CHECK COMPLETE
    ```

STEP 5.2 — UPDATE CROSS-CANCER TABLE
  Add the new cancer to the master table:

    Cancer  Lineage  Switch gene   Level    Lock
    [new]   [lin]    [gene]        [level]  [epigenetic]

STEP 5.3 — UPDATE FRAMEWORK LESSONS
  Add any new framework lesson derived from
  this cancer to the running list of refinements.

OUTPUTS OF PHASE 5:
  - Updated README section
  - Updated cross-cancer table
  - Updated framework lessons list
```

---

## IV. DIRECTORY STRUCTURE

```
cancer_name/
├── data/
│   └── [cancer]_false_attractor/
│       ├── [GEO_file_1].gz          (downloaded)
│       ├── [GEO_file_2].gz          (downloaded)
│       └── results/
│           ├── metadata.csv          (cached)
│           ├── saddle_results.csv    (Script 1)
│           ├── analysis_log.txt      (Script 1)
│           ├── [cancer]_figure.png   (Script 1)
│           └── results_s2/
│               ├── gap_results_s2.csv
│               ├── all_genes_s2.csv
│               ├── analysis_log_s2.txt
│               └── [cancer]_figure_s2.png
│
├── [cancer]_false_attractor.py       (Script 1)
├── [cancer]_false_attractor_2.py     (Script 2)
│
└── docs/
    ├── Doc_[N]a_Script1.md
    ├── Doc_[N]b_ReasoningArtifact.md
    └── Doc_[N]c_LiteratureCheck.md
```

---

## V. THE ENSEMBL MAP PATTERN

```
Every script needs a hard-coded Ensembl→symbol
map for target genes. This avoids API dependencies
and makes scripts fully self-contained.

PATTERN:
  ENSEMBL_MAP = {
      "ENSG00000066336": "SPI1",
      "ENSG00000101361": "KLF4",
      # ... etc
  }
  SYMBOL_TO_ENSEMBL = {v: k for k,v in ENSEMBL_MAP.items()}

  df.index = df.index.map(
      lambda x: ENSEMBL_MAP.get(x, x)
  )

SOURCE FOR ENSEMBL IDs:
  https://www.ensembl.org/id/[ENSG...]
  or Biomart bulk lookup
  Hard-code them — do not fetch dynamically.

PANDAS 2.x COMPATIBILITY:
  Do NOT use df.index.fillna(Index)
  Use list comprehension instead:
    extracted = df.index.str.extract(r"(pattern)", expand=False)
    new_index = [
        extracted[i] if pd.notna(extracted[i])
        else df.index[i]
        for i in range(len(df.index))
    ]
    df.index = pd.Index(new_index)
```

---

## VI. THE GENE PANEL CONSTRUCTION RULES

```
RULE 1 — PREDICT FROM THE BLOCK LEVEL
  Switch genes must be at the level of the block.
  AML block = TF level → SPI1/KLF4/IRF8
  MDS block = effector level → ELANE
  If you do not know the block level,
  include genes from MULTIPLE levels and
  let the depth correlations reveal which level.

RULE 2 — DO NOT COPY PRIOR CANCER PANELS
  A new cancer has a new attractor basin.
  If the panels were identical, the cancers
  would snap to the same attractor.
  Use prior validations only to eliminate
  levels already assigned to other cancers
  in the same lineage.

RULE 3 — ALWAYS INCLUDE THESE PANELS
  SWITCH GENES (3-8): lineage-specific TFs and
    effectors at the predicted block level
  FALSE ATTRACTOR (3-6): identity genes of
    the stuck state (surface markers, TFs of
    the progenitor state)
  EPIGENETIC (4): EZH2, TET2, DNMT3A, ASXL1
    always included — direction tells lock type
  SCAFFOLD (2): MYC, MKI67
    always included — proliferation context

RULE 4 — INCLUDE GENES FOR THE GAP TEST
  If you predict Gene A drives Gene B:
    Include both A and B in the panel
    Run r(A,B) in the cancer samples
    Near-zero r = connection broken = the gap
    This is the most mechanistically informative
    test in the protocol

RULE 5 — EXTEND IN SCRIPT 2
  Script 2 panel = Script 1 panel
                 + gap genes (what sits between
                   the elevated and suppressed genes)
                 + identity genes (of actual stuck state)
                 + chromatin complex genes
                   (RCOR1, KDM1A, HDAC1/2 if relevant)
```

---

## VII. DEPTH SCORING RULES

```
SCRIPT 1 DEPTH SCORE (discovery):
  Component 1: mean switch gene suppression
    (1 - norm(mean of switch genes))
  Component 2: mean FA gene elevation
    (norm(mean of FA genes))
  Depth = mean(Component 1, Component 2)
  Range: 0 to 1 (higher = more deeply blocked)

SCRIPT 2 DEPTH SCORE (corrected):
  Use the two highest-|r| genes from Script 1
  depth correlations.
  Typically: top suppressed gene + top elevated gene
  Depth = mean(
    1 - norm(top suppressed gene),
    norm(top elevated gene)
  )

ALWAYS COMPARE S1 vs S2:
  r(S1_depth, S2_depth) tells you:
    r > 0.9: same biology, ELANE/CD34-like dominance
    r 0.5-0.9: partial concordance
    r < 0.5: different axes — S2 captures new signal

ALWAYS CHECK DEPTH BY SUBTYPE:
  If molecular subtypes are available:
    Mann-Whitney depth by subtype
    p < 0.05 = different attractor basins
    Different basins = different drug targets
    Different basins = different depth axes needed
```

---

## VIII. THE WRONG PREDICTION PROTOCOL

```
When a prediction is wrong, the protocol
does not discard it. It processes it.

STEP W1 — CLASSIFY THE ERROR
  Type A: Wrong gene, right level
    (predicted SPI1 suppressed — actually ELANE)
    → Panel was at right level, wrong member
    → Add correct member to Script 2

  Type B: Wrong level entirely
    (predicted TF suppressed — actually effector)
    → Block is at different level than predicted
    → Identify actual level from depth correlations
    → Rebuild Script 2 panel at correct level

  Type C: Wrong direction
    (predicted suppressed — actually elevated)
    → Cancer is not at the predicted saddle point
    → Gene is a marker of a DIFFERENT state
    → Ask: what state expresses this gene?
    → That state is where the cells are stuck

  Type D: Correct gene, insufficient power
    (predicted suppressed, trend present, ns)
    → May be real, may be noise
    → Check depth correlation — if |r| > 0.3,
      it is real and underpowered
    → Collect more samples or use correlation
      as confirmation

STEP W2 — EXTRACT THE POINTER
  Every wrong prediction points to something.
    Wrong gene → correct gene is nearby in pathway
    Wrong level → correct level is revealed
    Wrong direction → correct attractor is revealed
    Wrong magnitude → correct scale revealed

  Write: "This wrong prediction tells us [X]"
  This becomes an entry in the reasoning artifact.

STEP W3 — BUILD SCRIPT 2 FROM THE POINTERS
  The Script 2 panel is built from:
    - What Script 1 confirmed (keep)
    - What the wrong predictions pointed to (add)
    - The gap between elevated and suppressed (add)
    - Nothing else

STEP W4 — RECORD THE LESSON
  Add to the framework lessons list:
    "In [cancer type], wrong prediction [X]
     taught [Y] about the attractor geometry.
     Lesson: [general rule for future analyses]"
```

---

## IX. FRAMEWORK LESSONS — ACCUMULATED

### From 10 cancer validations

```
LESSON 1 (from AML validation):
  In myeloid cancers, the primary TFs
  (SPI1/KLF4/IRF8) are the switch genes
  when the block is at the blast→GMP level.
  TF-level block = TF-level switch genes.

LESSON 2 (from MDS validation):
  In the same lineage, a different cancer
  has a different saddle point.
  If MDS had the same saddle point as AML,
  MDS cells would snap to AML.
  The existence of a distinct clinical entity
  proves a distinct attractor basin.
  Use clinical distinctness to infer geometric
  distinctness.

LESSON 3 (from MDS validation):
  Switch genes are at the LEVEL OF THE BLOCK,
  not at the level of the most famous TFs.
  Effector-level blocks (MDS/ELANE) have
  effector-level switch genes.
  TF-level blocks (AML/SPI1) have TF-level
  switch genes.
  When predicting for a new cancer, ask:
  is the cancer stuck before or after TF
  activation?

LESSON 4 (from MM validation):
  Some cancers have within-terminal-state
  false attractors.
  Plasma cell is already a terminal state.
  MM is stuck within terminal state —
  not blocked before it.
  The switch gene (IRF8) is a
  COMMITMENT MARKER, not a TF driver.
  When the cancer cell type is already terminal,
  look for commitment markers as switch genes.

LESSON 5 (from BRCA validation):
  EZH2 can be either a LOCK (elevated, gain
  of function) or DISRUPTED (suppressed, loss
  of function) depending on cancer type.
  Do not assume EZH2 direction.
  Let data determine it.
  EZH2 elevated: gain-of-function epigenetic
                 lock — EZH2 inhibitor is drug
  EZH2 suppressed: loss-of-function — different
                   target, different mechanism

LESSON 6 (from MDS validation):
  Surface markers and nuclear TFs can
  desynchronize in false attractor states.
  CD34 (surface) retained.
  GATA2 (nuclear) suppressed.
  Surface marker retention does not mean
  TF retention.
  Commitment TFs may already be suppressed
  while surface markers lag.
  This is specific to states where cells have
  committed to a fate but cannot complete it.

LESSON 7 (from all validations):
  The depth correlation table is more
  informative than the saddle point table.
  The saddle table tests predictions.
  The depth correlations find the real biology.
  Always read depth correlations before
  interpreting the saddle table.

LESSON 8 (from MDS validation):
  Wrong-direction predictions locate the
  attractor precisely.
  AZU1 predicted suppressed, found elevated:
  This located the block at promyelocyte stage.
  RCOR1 predicted elevated, found suppressed:
  This revealed the progenitor retention mechanism.
  When prediction is wrong direction, ask:
  what does the actual direction imply about
  where the cells are in the landscape?

LESSON 9 (from all validations):
  If the geometry-derived drug target is real,
  there will be clinical trial evidence.
  If there is no clinical trial evidence,
  either the prediction is novel or wrong.
  Use absence of trial evidence to distinguish
  novel predictions from errors.

LESSON 10 (from all validations):
  The gap test (r between elevated Gene A
  and suppressed Gene B when A normally drives B)
  is the most mechanistically informative test.
  Near-zero r = circuit broken = the gap.
  This locates the therapeutic intervention point
  more precisely than the gene expression
  changes themselves.
```

---

## X. QUALITY CHECKS

### Before moving to the next phase

```
PHASE 0 → PHASE 1 CHECKLIST:
  ☐ Dataset is human (not mouse)
  ☐ Cancer AND normal samples confirmed
  ☐ n(cancer) ≥ 5, n(normal) ≥ 3
  ☐ Correct tissue/cell type confirmed
  ☐ Data is readable and parseable
  ☐ No dataset modification after prediction

PHASE 1 → PHASE 2 CHECKLIST:
  ☐ All predictions written before data loaded
  ☐ Predictions are dated and signed
  ☐ Predictions have biological reasoning
    (not just "it's a famous gene")
  ☐ At least 3 switch genes predicted
  ☐ At least 3 FA markers predicted
  ☐ Epigenetic direction predicted
  ☐ Drug target predicted with mechanism
  ☐ Predictions are not copied from prior
    cancer in same lineage

PHASE 2 → PHASE 3 CHECKLIST:
  ☐ Script 1 output fully pasted and saved
  ☐ Depth correlation table reviewed
  ☐ Each prediction classified (confirmed/denied)
  ☐ Unexpected signals documented
  ☐ Corrected attractor described
  ☐ New predictions derived from Script 1
  ☐ Script 1 NOT modified after running
  ☐ Document [N]a written

PHASE 3 → PHASE 4 CHECKLIST:
  ☐ Script 2 predictions stated before writing
  ☐ Script 2 reuses Script 1 downloads
  ☐ Gap test designed (if applicable)
  ☐ Script 2 output fully pasted and saved
  ☐ S1 vs S2 depth comparison done
  ☐ Final attractor picture has 3 components
  ☐ Drug targets stated before literature
  ☐ Novel predictions listed and dated
  ☐ Document [N]b written

PHASE 4 → PHASE 5 CHECKLIST:
  ☐ Predictions locked before any search
  ☐ Minimum 6 literature searches run
  ☐ Each prediction classified vs literature
  ☐ Drug confirmation found or explicitly absent
  ☐ Novel predictions confirmed as novel
  ☐ Document [N]c written

PHASE 5 COMPLETION CHECKLIST:
  ☐ README section written in standard format
  ☐ Cross-cancer table updated
  ☐ Framework lessons updated
  ☐ All scripts, logs, figures archived
  ☐ All documents numbered and dated
```

---

## XI. WHAT MAKES A RESULT VALID

```
A RESULT IS VALID WHEN:
  1. Prediction was stated before data was seen
  2. Script is reproducible from GEO accession
     on any machine
  3. Full output log is preserved unedited
  4. Literature check was run after predictions
     were locked
  5. Wrong predictions are documented alongside
     correct ones

A RESULT IS INVALID WHEN:
  1. Gene panel was modified after seeing results
  2. Only confirmations are reported
  3. Script requires proprietary data
  4. Literature was consulted before predictions
  5. Sample labels were changed after analysis

THE STANDARD:
  Any researcher with the GEO accession and
  the script should be able to reproduce
  the exact numbers in the log file.
  That is the reproducibility standard.
  Not peer review. Not journal publication.
  Reproducible computation from public data.
```

---

## XII. DOCUMENT NUMBERING

```
Each cancer validation produces 3 documents:
  [N]a  — Script 1 reasoning artifact
  [N]b  — Script 2 reasoning artifact
          (framework confirmation)
  [N]c  — Literature check

Assigned document numbers:
  Doc 80   — Multiple Myeloma (MM)
  Doc 86a  — MDS Script 1
  Doc 86b  — MDS Script 2 + reasoning artifact
  Doc 86c  — MDS Literature check

Next cancer:
  Doc 87a  �� [cancer] Script 1
  Doc 87b  — [cancer] Script 2
  Doc 87c  — [cancer] Literature check

Session continuity:
  Each new session begins by reading the
  most recent [N]c document to establish
  where the series stands.
  The protocol does not require memory across
  sessions — the documents carry the state.
```

---

## XIII. STARTING A NEW SESSION

```
Any session can pick up the protocol at any
point if given:

  1. The most recent literature check document
     (e.g., Doc 86c)
  2. The protocol document (this file)
  3. A new cancer type to analyze

The session starts at PHASE 0:
  Read Doc [N]c for context on what has been
  established. Do not modify prior documents.
  Identify the new cancer.
  Run PHASE 0 through PHASE 5.
  Produce Doc [N+1]a, [N+1]b, [N+1]c.

The session does NOT need:
  - Memory of prior conversations
  - Access to prior scripts (they are in GEO)
  - The full prior reasoning chain
  - Any context beyond the provided documents

THE KEY INVARIANT:
  Predictions before data.
  Data before literature.
  Literature after everything else.
  This order cannot be changed.
  This order is what makes the results valid.
```

---

## STATUS

```
protocol_version:   1.0
validated_against:  10 cancer types
                    AML, CML, CRC, GBM, BRCA,
                    LUAD, B-ALL, T-ALL, CLL,
                    MM, MDS
false_positive_rate: 0 (zero in direction)
                    across all 10 validations
drug_targets_confirmed: all 10 drug targets
                    confirmed by clinical
                    pharmacology
novel_predictions:  at least 1 per cancer type
                    not in existing literature
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
next_cancer:        any — protocol is ready
```
