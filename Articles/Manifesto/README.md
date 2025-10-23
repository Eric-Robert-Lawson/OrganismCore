# Exploratory Directions (OrganismCore)

This document collects ideas in the Organism project currently marked as exploratory. These items are important and strategic, but they are not production‑ready technical claims. Each entry includes current maturity, brief rationale, risks, and suggested next steps.

Important orientation (core priority)
- Core priority: RDUs + DSL (Reasoning DNA Units and their Domain‑Specific Language) — this is the pragmatic, testable core of OrganismCore. Everything else in this document is exploratory and should be evaluated or prototyped only after the DSL primitives and baseline RDUs are stable enough to express them.
- The manifesto and broader Organism vision remain the exploratory umbrella. For adoption and review, emphasize the DSL and prototype artifacts first; treat the items listed below as research directions.

Purpose
- Clearly separate speculative/social/governance ideas from the technical core (RDUs + DSL).
- Help reviewers focus on proven results while giving contributors a map of research directions.

Labeling conventions
- [MATURE] — core technical claims supported by math and/or a working prototype (cite Zenodo, tests).
- [PROTOTYPE] — implemented in the repository; reproducible artifacts exist (see examples/demo.ipynb).
- [EXPLORATORY] — conceptual/speculative items; intended to spark research and debate, not production requirements.

Exploratory items
- Blockchain-based contribution & royalty system
  - Maturity: [EXPLORATORY]
  - Rationale: incentive alignment for contribution attribution and provenance
  - Risks: legal, security, ease-of-adoption, centralization incentives
  - Suggested next steps: produce a threat model; prototype only an off‑chain, non‑financial proof‑of‑contribution flow; solicit cryptoeconomic review.

- Post‑quantum traversal / key‑generation ideas
  - Maturity: [EXPLORATORY]
  - Rationale: speculative alignment between traversal proofs and cryptographic constructs
  - Risks: high cryptographic burden; easy to be overclaiming without cryptographer review
  - Suggested next steps: frame as a research question, solicit cryptographers, avoid product framing until vetted.

- Distributed reasoning economy (economic design)
  - Maturity: [EXPLORATORY / concept sketch]
  - Rationale: align compute, validation, and human contribution incentives
  - Risks: attack vectors, economic failure modes, perverse incentives
  - Suggested next steps: simulate small economies, explore reputation-only incentive models before monetary integration.

- Constitutional layer & governance
  - Maturity: [EXPLORATORY]
  - Rationale: ethical guardrails and mechanisms for contestability
  - Risks: political, legal, and operational complexity
  - Suggested next steps: maintain as a policy research track, produce a concise governance design note separate from core technical doc.

- Incentive and royalty mechanics
  - Maturity: [EXPLORATORY]
  - Rationale: fund and reward contributors
  - Risks: monetization vs. commons tension, regulatory complexity
  - Suggested next steps: document non‑monetary governance-first alternatives (curation, reputation, badges).

How to use this file
- Reviewers: focus first on sections of the manifesto labeled [MATURE] or [PROTOTYPE] for technical claims.
- Contributors: pick exploratory items you'd like to move toward prototype; open an issue with a 2–4 line plan + metrics for success.
- Maintainers: as an exploratory item gains evidence (tests, prototype, paper), update the maturity label and migrate details back into the main docs.

If desired, maintainers can convert manifesto paragraphs marked speculative into entries here and link back to exact manifesto locations.
