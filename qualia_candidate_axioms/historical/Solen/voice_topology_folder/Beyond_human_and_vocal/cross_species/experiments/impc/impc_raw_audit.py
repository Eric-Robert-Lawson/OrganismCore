============================================================
IMPC RAW DATA AUDIT
============================================================

Rows: 851,255

============================================================
Q1: ACTUAL RAW VALUES — THIGMOTAXIS
Parameter: IMPC_OFD_010_001
============================================================

Showing percentiles per center
to determine true units:

Center                       N      Min       P5      P25   Median      P75      P95        Max  Units_guess
─────────────────────────────────────────────────────────────────────────────────────────────────────────
BCM                     15,523     75.7   1259.9   1699.5   2056.4   2468.2   3161.2    14342.0 MS_OR_LONG_TEST
CCP-IMG                 10,538     22.6   1170.2   1769.8   2250.8   2805.5   3758.5     8093.2 MS_OR_LONG_TEST
HMGU                    15,267   2138.1  12160.7  15996.1  18526.9  21068.5  24533.0    51577.6 MS_OR_LONG_TEST
ICS                      5,780    323.5   5158.3   6177.6   6797.6   7426.5   8430.1    25179.8 MS_OR_LONG_TEST
MARC                     4,323    961.0   2895.2   3636.8   4155.6   4751.6   5746.8     9877.8 MS_OR_LONG_TEST
MRC Harwell             17,988    235.5   1654.8   3620.5   4162.6   4700.6   5642.1    16830.0 MS_OR_LONG_TEST
RBRC                     3,048    374.3   2438.7   3318.6   3928.4   4498.5   5525.5    14772.8 MS_OR_LONG_TEST
TCP                     11,461    411.4   3176.0   4220.0   4971.8   5795.7   7162.2    27215.5 MS_OR_LONG_TEST
UC Davis                27,889     43.2   3345.0   4260.6   4919.0   5619.4   6768.2    21002.4 MS_OR_LONG_TEST

Unit interpretation key:
  SECONDS_OK:       median 100-1800
                    consistent with
                    seconds in a
                    20-30 min test
  SECONDS_SHORT_WIN: median 1-100
                    short time window
                    parameter (5 min)
  MS_OR_LONG_TEST:  median 1800-20000
                    ambiguous — could
                    be long test or ms
  MILLISECONDS:     median >20000
                    almost certainly ms

============================================================
Q2: DISTRIBUTION COMPARISON
HMGU vs all other centers
============================================================

Thigmotaxis:
  HMGU median:   18526.9
  Others median: 4186.9
  Ratio HMGU/others: 4.42x
  Mann-Whitney U: 1472290930, p = 0.00e+00

Time in center:
  HMGU median:   23.2
  Others median: 5.2
  Ratio HMGU/others: 4.43x
  Mann-Whitney U: 1524003442, p = 0.00e+00

Rearing count:
  HMGU median:   22.0
  Others median: 4.8
  Ratio HMGU/others: 4.63x
  Mann-Whitney U: 1472344632, p = 0.00e+00

============================================================
Q3: WILDTYPE-ONLY BEHAVIORAL
SUMMARY BY CENTER
============================================================

Wildtype records: 140,785 / 851,255 (16.5%)

All zygosity values in data:
  'homozygote': 489,752
  'heterozygote': 212,472
  'wildtype': 140,785
  'hemizygote': 8,246

Parameter: Thigmotaxis (IMPC_OFD_010_001)
  Center                    N_wt     Median       Mean         SD     ELF
  ────────────────────────────────────────────────────────────────────────
  BCM                      2,417       2.10       2.14       0.58      94
  CCP-IMG                  3,926       2.26       2.33       0.81      74
  ICS                      2,418       6.79       6.78       0.99      36
  MARC                     1,706       4.21       4.30       0.87      65
  RBRC                     1,292       3.91       3.91       0.91      55
  TCP                      1,844       4.93       5.00       1.13      74
  UC Davis                 4,402       4.97       5.02       1.08      31

  Wildtype Spearman ELF vs Thigmotaxis: r=-0.775, p=0.0408 *
  (N=7 centers with wildtype data and ELF score)

Parameter: Time_in_center (IMPC_OFD_009_001)
  Center                    N_wt     Median       Mean         SD     ELF
  ────────────────────────────────────────────────────────────────────────
  BCM                      2,417       0.01       0.01       0.00      94
  CCP-IMG                  3,926       0.00       0.00       0.00      74
  ICS                      2,418       0.01       0.01       0.00      36
  KMPC                     1,741       5.80       5.96       1.66      67
  MARC                     1,706       0.00       0.00       0.00      65
  RBRC                     1,292       0.01       0.01       0.00      55
  TCP                      1,844       0.01       0.01       0.00      74
  UC Davis                 4,402       0.00       0.00       0.00      31

  Wildtype Spearman ELF vs Time_in_center: r=+0.120, p=0.7776 ns
  (N=8 centers with wildtype data and ELF score)

Parameter: Rearing (IMPC_OFD_013_001)
  Center                    N_wt     Median       Mean         SD     ELF
  ────────────────────────────────────────────────────────────────────────
  BCM                      2,417       0.01       0.01       0.00      94
  CCP-IMG                  3,926       0.00       0.00       0.00      74
  ICS                      2,418       0.01       0.01       0.00      36
  MARC                     1,706       0.00       0.00       0.00      65
  RBRC                     1,292       0.00       0.00       0.00      55
  TCP                      1,844       0.01       0.01       0.00      74
  UC Davis                 4,402       0.00       0.00       0.00      31

  Wildtype Spearman ELF vs Rearing: r=+0.072, p=0.8780 ns
  (N=7 centers with wildtype data and ELF score)

Parameter: Ctr_entries (IMPC_OFD_008_001)
  Center                    N_wt     Median       Mean         SD     ELF
  ────────────────────────────────────────────────────────────────────────
  BCM                      2,417       1.20       1.20       0.00      94
  CCP-IMG                  3,926       1.20       1.20       0.00      74
  ICS                      2,418       1.20       1.20       0.00      36
  KMPC                     1,741    1200.00    1200.00       0.00      67
  MARC                     1,706       1.20       1.20       0.00      65
  RBRC                     1,292       1.20       1.20       0.00      55
  TCP                      1,844       1.20       1.20       0.00      74
  UC Davis                 4,402       1.20       1.20       0.01      31

  Wildtype Spearman ELF vs Ctr_entries: r=+0.290, p=0.4858 ns
  (N=8 centers with wildtype data and ELF score)

Saved → impc_wildtype_summary.csv

Building distribution figures...
Saved → impc_raw_distributions.png

Saved → impc_raw_audit.txt

============================================================
KEY OUTPUT TO READ:
  Q1 table — true units per center
  Q3 wildtype Spearman results
  impc_raw_distributions.png
    — shows whether HMGU is
      genuinely anomalous or
      just a different unit
============================================================
