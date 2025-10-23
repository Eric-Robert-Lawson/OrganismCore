# Exploratory Directions (OrganismCore)

This document collects ideas in the Organism project currently marked as *exploratory*. These items are important and strategic, but they are not production-ready technical claims. Each entry includes current maturity, brief rationale, risks, and suggested next steps.

---

## Important Orientation (Core Priority)

- **Core priority:** RDUs + DSL (Reasoning Derivative Units and their Domain-Specific Language) — this is the pragmatic, testable core of OrganismCore. Everything else in this document is exploratory and should be evaluated or prototyped only after the DSL primitives and baseline RDUs are stable enough to express them.  
- The **manifesto** and broader Organism vision remain the exploratory umbrella. For adoption and review, emphasize the **DSL** and **prototype artifacts** first; treat the items listed below as research directions.

---

## Purpose

- Clearly separate speculative, social, or governance ideas from the technical core (RDUs + DSL).  
- Help reviewers focus on proven results while giving contributors a map of research directions.

---

## Labeling Conventions

- **[MATURE]** — core technical claims supported by math and/or a working prototype (cite Zenodo, tests).  
- **[PROTOTYPE]** — implemented in the repository; reproducible artifacts exist (see examples/demo.ipynb).  
- **[EXPLORATORY]** — conceptual or speculative items intended to spark research and debate, not production requirements.

---

## Exploratory Items

### Blockchain-Based Contribution & Royalty System
- **Maturity:** [EXPLORATORY]  
- **Rationale:** incentive alignment for contribution attribution and provenance  
- **Risks:** legal, security, ease-of-adoption, centralization incentives  
- **Next Steps:** produce a threat model; prototype only an off-chain, non-financial proof-of-contribution flow; solicit cryptoeconomic review.

### Post-Quantum Traversal / Key-Generation Ideas
- **Maturity:** [EXPLORATORY]  
- **Rationale:** speculative alignment between traversal proofs and cryptographic constructs  
- **Risks:** high cryptographic burden; easy to overclaim without cryptographer review  
- **Next Steps:** frame as a research question, solicit cryptographers, avoid product framing until vetted.

### Distributed Reasoning Economy (Economic Design)
- **Maturity:** [EXPLORATORY / Concept Sketch]  
- **Rationale:** align compute, validation, and human contribution incentives  
- **Risks:** attack vectors, economic failure modes, perverse incentives  
- **Next Steps:** simulate small economies; explore reputation-only incentive models before monetary integration.

### Constitutional Layer & Governance
- **Maturity:** [EXPLORATORY]  
- **Rationale:** ethical guardrails and mechanisms for contestability  
- **Risks:** political, legal, and operational complexity  
- **Next Steps:** maintain as a policy research track; produce a concise governance design note separate from the core technical documentation.

### Incentive and Royalty Mechanics
- **Maturity:** [EXPLORATORY]  
- **Rationale:** fund and reward contributors  
- **Risks:** monetization-vs-commons tension; regulatory complexity  
- **Next Steps:** document non-monetary, governance-first alternatives (curation, reputation, badges).

---

## How to Use This File

- **Reviewers:** focus first on sections of the manifesto labeled [MATURE] or [PROTOTYPE] for technical claims.  
- **Contributors:** pick exploratory items you'd like to move toward prototype; open an issue with a 2–4 line plan and clear success metrics.  
- **Maintainers:** as an exploratory item gains evidence (tests, prototype, or paper), update its maturity label and migrate details back into the main documentation.

> Maintainers may also convert manifesto paragraphs marked speculative into entries here and link back to their original manifesto locations.
