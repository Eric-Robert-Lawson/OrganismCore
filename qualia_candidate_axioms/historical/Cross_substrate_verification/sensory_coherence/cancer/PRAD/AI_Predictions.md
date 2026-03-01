SWITCH GENES — PREDICTED SUPPRESSED IN PRAD:

  NKX3-1  — master luminal TF
             Most commonly deleted gene
             in PRAD (chr8p21)
             Loss initiates transformation
             PREDICTION: strongly suppressed
             Direction: DOWN

  FOXA1   — AR pioneer factor
             Required for AR binding
             to luminal gene enhancers
             FOXA1 mutations in CRPC
             In primary PRAD:
             PREDICTION: suppressed or
             dysregulated
             Direction: complex — may be
             elevated in some subtypes
             Record as DOWN for primary
             and revisit

  KLK3    — PSA — terminal AR target
             Marker of mature luminal
             differentiation
             PREDICTION: suppressed in
             high-grade vs low-grade
             (dedifferentiation reduces AR
             target gene expression)
             Direction: DOWN in high Gleason

  ACPP    — acid phosphatase (ACPP/PAP)
             Luminal differentiation marker
             Prostate-specific
             PREDICTION: suppressed
             Direction: DOWN

FALSE ATTRACTOR — PREDICTED ELEVATED:

  ERG     — TMPRSS2-ERG fusion product
             ~50% of primary PRAD
             ETS family TF
             When fused to TMPRSS2:
             AR drives ERG expression
             ERG then reprograms cells
             PREDICTION: elevated in
             fusion-positive subset
             Direction: UP (in ERG+ tumors)

  MKI67   — proliferation marker
             PREDICTION: elevated
             Direction: UP

  EZH2    — epigenetic lock
             PREDICTING ELEVATED again
             Fourth cancer in series
             (BRCA, PAAD, now PRAD)
             EZH2 silences NKX3-1
             and luminal TF loci
             PREDICTION: UP strongly
             Direction: UP

  HOXC6   — HOX gene
             Elevated in PRAD
             Part of EMT program
             PREDICTION: UP

EPIGENETIC:
  EZH2 ELEVATED — gain of function
  EZH2 silences NKX3-1/luminal program
  Same pattern as BRCA and PAAD
  Strongest prediction in this category

SCAFFOLD:
  AR      — androgen receptor
             In primary PRAD: maintained
             or elevated (drives cancer)
             Not a FA marker but a driver
             PREDICTION: maintained/elevated
             compared to benign
  MYC     — elevated in PRAD
             KRAS is not the driver here —
             MYC amplification is common
             (~30% of primary PRAD)
             PREDICTION: elevated
             Direction: UP
             NOTE: Normal prostate is NOT
             a high-MYC secretory cell
             unlike acinar pancreas
             So MYC UP prediction is valid
             here — no secretory reference
             bias problem

GLEASON PREDICTION:
  High Gleason (aggressive) vs
  Low Gleason (indolent):
    High Gleason = deeper in attractor
    Lower NKX3-1 expression
    Higher EZH2 expression
    Higher MKI67
    Lower KLK3/PSA
    Higher ERG (in fusion+ tumors)
  Block depth score should correlate
  positively with Gleason grade
  PREDICTION: r(depth, Gleason_high) > 0
  i.e. high grade tumors are deeper
  in the false attractor

ERG PREDICTION:
  ERG fusion-positive tumors:
    Higher ERG expression (>5x vs fusion-)
    Different depth score distribution
    ERG+ may be a distinct attractor basin
    vs ERG- which may use a different route
  PREDICTION: ERG expression bimodal
  in tumor samples (fusion+ vs fusion-)
  Threshold derivable from expression alone

DRUG PREDICTIONS (geometry-derived,
before literature):
  1. AR pathway inhibitor
     Geometry: AR drives the cancer
               luminal state
               AR is the motor of the
               false attractor
               Enzalutamide/abiraterone
               already standard — confirmed
  2. EZH2 inhibitor (tazemetostat)
     Geometry: EZH2 silences NKX3-1
               Third solid cancer with
               EZH2 gain lock
               Prediction: EZH2i restores
               NKX3-1 → luminal re-diff
               OR forces basal identity
               → cells lose AR dependence
               in a non-NEPC direction
  3. NKX3-1 restoration
     Geometry: NKX3-1 is the switch gene
               Deleted in many PRAD
               If not deleted — can be
               re-expressed via EZH2i
               If deleted — need synthetic
               approach (CRISPRa)
  4. MYC inhibitor
     Geometry: MYC predicted elevated
               (different from PAAD)
               BET inhibitor / OMO-103
               MYC drives proliferation
               at the block point

ADJACENT NORMAL NOTE:
  Normal = benign prostate tissue
  from same patient (radical prostatectomy)
  True luminal cells — not secretory
  factories like acinar pancreas
  This is a better matched reference
  than PAAD adjacent normal
  The MYC secretory bias problem
  should NOT apply here
  Luminal prostate cells have moderate
  MYC — not high
  MYC UP prediction in PRAD vs benign
  is valid
