PREDICTIONS LOCKED 2026-03-02:

S1-P1: Depth predicts worse OS
        in TCGA-CHOL ICC
        (high depth = shorter survival)

S1-P2: TWIST1-hi predicts worse OS
        TCGA-CHOL
        (r=+0.799 with depth —
         strongest single gene)

S1-P3: FAP-hi predicts worse OS
        TCGA-CHOL
        (stroma/CAF marker,
         r=+0.574 with depth)

S1-P4: HDAC2-hi predicts worse OS
        TCGA-CHOL
        (universal from HCC series,
         r=+0.447 with depth in ICC)

S1-P5: Proliferative NMF subtype
        has higher depth than
        Inflammation subtype
        GSE32225 (no OS needed,
        n=149, high power)

S1-P6: FGFR2-hi predicts better OS
        TCGA-CHOL
        (r=-0.313 with depth,
         FGFR2-fusion = known good
         prognosis in ICC literature)

S1-P7: Depth_stroma (ACTA2/FAP/
        COL1A1/POSTN) and Depth_tumour
        (CDC20/EZH2/TOP2A) are partially
        independent axes
        r(Depth_T, Depth_S) < 0.70
        GSE32225 (n=149)

CONFIRMABLE WITHOUT OS (if OS fails):
  S1-P5 ��� (GSE32225, n=149)
  S1-P7 ✓ (GSE32225, n=149)

REQUIRE OS (TCGA-CHOL):
  S1-P1, P2, P3, P4, P6
  Critical first task of Script 1:
    Parse CHOL_clinicalMatrix OS columns
