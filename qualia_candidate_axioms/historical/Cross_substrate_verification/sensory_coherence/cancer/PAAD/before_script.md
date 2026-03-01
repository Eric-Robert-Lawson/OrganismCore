SWITCH GENES — PREDICTED SUPPRESSED IN PAAD:

  PTF1A  — pancreatic acinar master TF
           Required for acinar identity
           PTF1A loss is the initiating event
           in ADM — when PTF1A falls, acinar
           cells become ductal-like
           PREDICTION: strongly suppressed
           Direction: DOWN
           Expected: -50% to -90%

  NR5A2  — nuclear receptor, acinar TF
           Co-regulates acinar gene program
           with PTF1A
           NR5A2 germline variants are PAAD
           risk factors (published)
           PREDICTION: suppressed
           Direction: DOWN

  RBPJL  — acinar-specific transcription factor
           Notch pathway transcriptional target
           expressed only in mature acinar cells
           Loss during ADM is documented
           PREDICTION: suppressed
           Direction: DOWN

  MIST1  — (BHLHA15) acinar differentiation TF
           Master regulator of acinar secretory
           identity — lost during ADM
           PREDICTION: suppressed
           Direction: DOWN

  CPA1   — carboxypeptidase A1
           Acinar digestive enzyme
           Terminal acinar effector gene
           Same logic as ELANE in MDS:
           effector gene marks the
           completed differentiation state
           PREDICTION: suppressed
           Direction: DOWN

  PRSS1  — trypsinogen 1
           Acinar digestive enzyme
           Another terminal acinar effector
           PREDICTION: suppressed
           Direction: DOWN

FALSE ATTRACTOR MARKERS — PREDICTED ELEVATED:

  KRT19  — cytokeratin 19
           Ductal epithelial marker
           Elevated in PAAD vs normal acinar
           PAAD cells express ductal identity
           PREDICTION: elevated
           Direction: UP

  SOX9   — ductal/progenitor TF
           Marks ductal cells and early
           pancreatic progenitors
           Elevated in PAAD — re-expression
           of progenitor TF in cancer
           PREDICTION: elevated
           Direction: UP

  MUC1   — mucin 1
           Ductal surface marker
           Elevated in PAAD
           PREDICTION: elevated
           Direction: UP

  EPCAM  — epithelial cell adhesion molecule
           Progenitor/ductal surface marker
           PREDICTION: elevated
           Direction: UP

EPIGENETIC PREDICTION:
  EZH2:  ELEVATED — gain of function
         PAAD has high EZH2 expression
         EZH2 silences acinar identity genes
         PTF1A locus may be EZH2-methylated
         Same direction as BRCA — gain of lock
         PREDICTION: UP, significant

  Direction reasoning:
    MDS: epigenetic LOSS (EZH2 suppressed)
    BRCA: epigenetic GAIN (EZH2 elevated)
    PAAD: epigenetic GAIN — EZH2 silences
          the acinar program
          This is a different cancer from MDS
          Gain-of-function lock predicted

SCAFFOLD:
  MYC:   ELEVATED — KRAS drives MYC
         KRAS → RAS/MAPK → MYC
         PREDICTION: UP strongly

SURVIVAL PREDICTION:
  Block depth score should stratify survival
  Higher block depth (lower acinar gene
  expression + higher ductal markers)
  = more dedifferentiated = worse prognosis
  Depth correlates negatively with survival
  PREDICTION: r(depth, survival_months) < 0
              p < 0.05
  This would be the first survival validation
  of the depth score across any cancer in
  the series

DRUG TARGET PREDICTION (from geometry):
  Target 1: EZH2 inhibitor
    Geometry: EZH2 elevated locks acinar program
    Restoring acinar TFs (PTF1A/NR5A2) via
    EZH2 inhibition may dissolve the attractor
    Drug: tazemetostat (FDA approved in other
          cancers — already in our validation
          series from BRCA)
    PAAD-specific: EZH2 inhibitor + gemcitabine

  Target 2: PTF1A restoration
    Geometry: PTF1A is the master switch gene
    Forced PTF1A expression → acinar identity
    → cells cannot maintain PAAD phenotype
    Drug: indirect — demethylation of PTF1A
    locus via HMA (azacitidine/decitabine)
    Or: BET inhibitor (JQ1) — MYC/BRD4 axis
    to reduce the dedifferentiation signal

  Target 3: KRAS→MYC axis
    Geometry: MYC elevated by KRAS
    MYC maintains dedifferentiated state
    MYC inhibitor (OMO-103 in trials) or
    BET inhibitor (targets MYC transcription)
    reduces proliferative drive at the
    block point

SUBTYPE PREDICTION:
  Classical PAAD (high GATA6, epithelial):
    Higher acinar gene retention
    Shallower block depth
    Better survival
  Basal-like PAAD (low GATA6, mesenchymal):
    Lower acinar gene expression
    Deeper block depth
    Worse survival
  PREDICTION: depth score stratifies
  Classical vs Basal-like
  GATA6 will be the stratifier

ADJACENT NORMAL CAVEAT:
  Normal samples are adjacent non-tumor tissue
  not truly healthy pancreas
  Field effects may shift normal toward tumor
  Changes found will be UNDERSTATED
  Real acinar→PAAD differences are larger
  than measured
  Note this in all results
