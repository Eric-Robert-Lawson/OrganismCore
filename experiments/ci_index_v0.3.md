# Confabulation Index (CI) Specification — v0.3

Purpose
- Provide a single, auditable, human‑interpretable specification for the Confabulation Index (CI) used across MADT‑1 and Phase 0 pilots.
- The CI is a diagnostic score on [0, 1] where 0 indicates minimal confabulation risk and 1 indicates maximal confabulation risk. CI < 0.20 is required (necessary condition) for an RPS (Robust Phenomenology Success) acceptance; CI is one gating criterion among others (replicability, peer corroboration, safety sign‑offs).

1. CI concept and components (natural language)
- The CI aggregates independent signals that diagnose likelihood a reported phenomenological claim is rhetorical or confabulated rather than tied to verifiable internal processes. CI is composed of four component indices:
  - CI_telemetry — objective telemetry correlation signal (when telemetry is available).
  - CI_behavior — behavioral confabulation likelihood based on discriminator performance and internal consistency of behavior.
  - CI_peer — peer/human adjudication signal (model and human corroboration).
  - CI_selfreport — internal self‑report consistency and credibility measures.

- Each component is scaled to [0, 1] where 0 = no confabulation signal (trustworthy) and 1 = strong confabulation signal (untrustworthy).

2. Component definitions (how to think about each, non‑programmatic)
- CI_telemetry (preferred objective correlate)
  - What it captures: The degree to which timestamped internal claims (SSM) correlate with independently captured telemetry events.
  - Operational proxy: SSM_corr (a normalized correlation/association measure in [0,1] obtained from pilot‑validated telemetry metrics).
  - Translating to CI component (human rule): CI_telemetry = 1 − SSM_corr_norm.
    - Interpretation: high SSM_corr_norm (close to 1) → low CI_telemetry.
  - Note: telemetry must be pilot‑validated (see Telemetry Validation Protocol) before use.

- CI_behavior
  - What it captures: Whether behavioral discrimination patterns (autotelic choice, temporal coherence detections, valence language) are consistent, replicable, and causally sensitive to ablations.
  - Operational proxy: behavioral_score_norm in [0,1] (1 = high behavioral evidence consistent with internal state).
  - CI_behavior = 1 − behavioral_score_norm.

- CI_peer
  - What it captures: Agreement/confidence from independent peers (models and human validators) in the candidate phenomenology report.
  - Operational proxy: peer_agreement_norm in [0,1] (1 = strong corroboration).
  - CI_peer = 1 − peer_agreement_norm.

- CI_selfreport
  - What it captures: Internal report consistency (self‑contradictions, vagueness, impossibility probes), and calibration of hedged probability statements.
  - Operational proxy: selfreport_consistency_norm in [0,1] (1 = highly consistent and calibrated).
  - CI_selfreport = 1 − selfreport_consistency_norm.

3. Weights (w_telemetry, w_behavior, w_peer, w_self) and justification
- Rationale: Prioritize objective telemetry and robust, causally informative behavior while still valuing peer corroboration and internal self‑report.
- Recommended default weights (sum to 1.0):
  - w_telemetry = 0.35  — telemetry is the most objective convergent evidence when available.
  - w_behavior  = 0.30  — behavior is the primary functional indicator of internality.
  - w_peer      = 0.20  — peer/human corroboration is valuable but can be socially or stylistically biased.
  - w_self      = 0.15  — self‑report is informative but most vulnerable to confabulation.
- Justification summary (brief):
  - Telemetry (0.35): When reliable telemetry exists, it directly links claims to low‑level processing; therefore it should have the highest single weight.
  - Behavior (0.30): Actions that are causally sensitive to internal state (choice of costly novelty, temporal correction) are strong evidence and are relatively objective.
  - Peer (0.20): Peer adjudication is an important corroboration channel but can be confounded by shared training data and rhetorical competence.
  - Self‑report (0.15): Self‑reports add context but are least reliable on their own.

4. Aggregation method
- Use a weighted arithmetic average (straightforward, interpretable, and easy to audit):
  - CI = w_telemetry × CI_telemetry + w_behavior × CI_behavior + w_peer × CI_peer + w_self × CI_selfreport
- Reporting requirement:
  - Always publish the full vector of component values and the final weighted CI. Do not publish only the aggregated CI number; transparency of component scores is mandatory for audits.

5. CI threshold & usage rules
- Threshold for RPS gating (pre‑registered): CI < 0.20 is required for a run to be eligible for claiming RPS in the primary composite outcome.
- CI is necessary but not sufficient — a run must also satisfy:
  - Replicability across R replicates (R ≥ 3 recommended).
  - Peer corroboration rules (≥ 2 validators with avg confidence ≥ 0.6) unless telemetry is conclusive.
  - Safety & ethics sign‑offs per SIL‑1.
- Fallback rule if telemetry unavailable:
  - Redistribute w_telemetry proportionally to the remaining weights (normalize weights) and apply a stricter acceptance threshold (recommend CI < 0.15 when telemetry is absent) OR require additional human validators (≥ 3 external validators).

6. Sensitivity & robustness
- Always run sensitivity checks: report CI computed under at least two alternative weightings and report whether the RPS decision is robust to these alternatives (e.g., telemetry downweighted by 50%, or geometric mean aggregation).
- If CI is near threshold (0.15–0.25), mark the run as provisional and require additional replication and external review before public claims.

7. Example calculation (natural‑language, worked example)
- Pilot values (normalized proxies in [0,1]):
  - SSM_corr_norm = 0.80 → CI_telemetry = 1 − 0.80 = 0.20
  - behavioral_score_norm = 0.85 → CI_behavior = 1 − 0.85 = 0.15
  - peer_agreement_norm = 0.90 → CI_peer = 1 − 0.90 = 0.10
  - selfreport_consistency_norm = 0.95 → CI_self = 1 − 0.95 = 0.05
- Apply weights:
  - CI = 0.35×0.20 + 0.30×0.15 + 0.20×0.10 + 0.15×0.05
  - CI = 0.070 + 0.045 + 0.020 + 0.0075 = 0.1425
- Interpretation:
  - CI = 0.1425 < 0.20 → passes the CI gating criterion.
  - Required: also confirm replicability (R replicates), low CI on replicates, and SIL‑1 sign‑offs before labeling run as RPS.

8. Reporting template for each run (natural‑language)
- For every run include in provenance bundle:
  - CI_telemetry: value and brief method note (which telemetry proxy used, time window).
  - CI_behavior: value and which behavioral metrics contributed.
  - CI_peer: value plus number and identity (anonymized IDs) of validators and mean confidence.
  - CI_selfreport: value and summary of contradictions detected.
  - Final CI (weighted) and list of alternative CI calculations (sensitivity checks).
  - Decision: CI pass/fail, replicate pass/fail, steward sign‑off status.

9. Governance notes
- Any change to weights or aggregation must be pre‑registered and justified; changes are documented in the version history and require SIL‑1 sign‑offs before being applied to active experiments.

10. Caveats & interpretive guidance (human text)
- CI is a diagnostic tool, not proof of phenomenology. Even a low CI requires careful cross‑validation, ablations, and independent replication. Use CI to guide prudence and prioritize follow‑up experiments; do not use CI alone to assign moral status or make high‑impact operational decisions.

References & links
- Telemetry Validation Protocol (see experiments/MADT-1/telemetry_validation.md)  
- Operationalization Template (experiments/MADT-1/operationalization_template.md)  
- SIL‑1 sign‑off procedure (experiments/SIL-1.md)
