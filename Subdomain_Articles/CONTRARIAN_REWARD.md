# Contrarian Reward Primitive — Spec & Process (v0.1)

Purpose
-------
This document defines a first‑class artifact for the URST substrate: the "Contrarian Reward" primitive. Its purpose is to surface, canonize, instrument, and reward rigorously validated challenges to existing high‑coherence axioms, beliefs, or Meta‑RDUs. The primitive operationalizes the social value of productive contradiction: if a coherent contrarian claim is validated and reduces unjustified certainty, the substrate treats that as epistemic progress and records, publishes, and optionally rewards the outcome.

Design principles
-----------------
- Tests-first: every contrarian proposal must include a suggested (or machine-generated) test plan.
- Provenance-first: every step (proposal → canonicalization → tests → validators → steward decisions) is recorded as an immutable provenance package.
- Diversity-first: validation requires independent validators (model families, institutions, human experts) per governance thresholds.
- Sandbox-first: changes to canonical axioms are advisory/contained until steward quorum and canary passes.
- Auditability: every proposal, test result, validator report, and steward decision is publicly queryable and hash-anchored.

Artifact schema (human summary)
-------------------------------
Field (name) — Type — Description
- proposal_id — string — unique id (UUID) for the contrarian proposal
- proposer_id — string — contributor identifier
- target_axiom_ids — [string] — list of RDU / Meta‑RDU ids being challenged
- provenance_package_uri — string — URI to the canonical provenance bundle for the proposal
- canonical_form — object — canonical primitives produced by the canonicalizer
- coherence_score_before — number — coherence(C_target) prior to challenge
- coherence_score_proposal — number — coherence(proposal)
- suggested_tests — [object] — machine/human tests (type, runner, dataset requirements)
- required_validator_diversity — object — minimal validator mix (e.g., 2 models, 1 human; min independent data sources)
- reward_budget — object — optional budget and distribution rules (if project funds rewards)
- risk_flags — [string] — privacy/legal/safety flags
- acceptance_criteria — object — thresholds for validation_index to count as validated
- lifecycle_state — enum — {draft, queued, running, validated, rejected, steward_review, canary, promoted, archived}
- validation_records_uri — string — pointer to aggregated test/validator reports
- steward_votes — [object] — steward decisions and signatures
- activation_metadata — object — canary scope, time windows, rollback triggers

High‑level process
------------------
1. Submit contrarian proposal (proposer includes suggested tests and provenance).
2. Canonicalizer reduces freeform claim to canonical_form; triage checks required provenance completeness and risk flags.
3. If triage passes, proposal is queued and automated tests are generated and run (CI jobs / model probes).
4. Coordinator assigns validators per required_validator_diversity and starts validation window.
5. Validators run tests, add independent evidence, and produce structured validation records (signed).
6. System computes validation_index (weighted function of reproduction, cross‑model agreement, adversarial resistance, validator independence).
7. If validation_index ≥ acceptance_criteria → mark as validated and publish validation_records. ContrarianReward computed and (optionally) distributed.
8. Steward review: for changes affecting canonical axioms, steward(s) review and determine sandbox/canary/promotion flow.
9. If promoted, update substrate: reduce coherence of invalidated axioms, create/activate Meta‑RDUs for new invariants, announce changes and anchor provenance.

ContrarianReward (formula sketch)
---------------------------------
Let:
- V ∈ [0,1] = validation_index
- ΔC = C_old − C_post (change in coherence of target after results)
- D = diversity_score ∈ [0,1] (higher when validators are independent)
Define:
ContrarianReward = base_scale * V * ΔC * (1 + α * D)
Where base_scale and α are project parameters set by steward policy and reward_budget. The formula is intentionally simple for v0.1; implementers may refine with more domain weighting.

Governance & safety controls
---------------------------
- Minimum validator diversity required for any promotion that materially changes canonical axioms.
- Sandbox → canary → full promotion with explicit steward multi‑sig for high‑impact changes.
- Rate limits: throttle contrarian campaigns that target the same axiom across short windows.
- Public audit logs and immutable anchors for all promotion decisions.
- Appeal & rebuttal channel: original proponents and community may submit counter‑evidence; all versions are preserved.

Badge & UX signals
------------------
- "Contrarian Pending" — proposal queued and tests running
- "Validated Contrarian" — validation_index passed; published with provenance
- "Promoted (Canary)" — steward approved canary activation
- "Promoted (Enforced)" — fully active Meta‑RDU / rule

Example minimal use case
------------------------
- Target: a project Meta‑RDU "All file writes must be atomic via method X".
- Contrarian proposal: demonstrable case where X imposes unacceptable latency under Y workload and method Z is provably safe and faster.
- Tests: benchmark harness + formal proof for atomicity conditions + adversarial workload generator.
- Validators: two independent performance models + one human infra engineer.
- Outcome: validation_index passes; steward canaries rule change on specific service, monitors metrics, then promotes.

Next actionable items (repo‑level)
---------------------------------
- Add a machine‑readable Contrarian Reward schema (JSON Schema) and code templates for generating suggested_tests.
- Add a `contrarian_runbook.md` for contributors and validators describing minimal content and test templates.
- Add a GitHub issue template `contrarian-proposal.md` to collect canonical fields on submission.
- Implement a small serverless endpoint to accept proposals and return triage status and provenance checklist.

Versioning & evolution
----------------------
This is v0.1. The artifact is intentionally conservative on enforcement. Over time we will refine:
- validation_index composition,
- reward math and incentivization,
- domain‑specific test templates,
- policy for steward quorums and diversity constraints.

Steward note
------------
Propose a stewarded initial configuration (validator mix, base_scale, α) and a trial budget if rewards are to be distributed. If no budget is attached, the system still uses the artifact to prioritize validation and publication without financial reward.

–––––
This file is intended as a canonical project artifact to be committed to the repository so contrarian proposals and their lifecycle are first‑class citizens of the URST substrate.