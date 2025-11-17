# AGENTS.md — Subdomain Machine Agent Instructions

This file provides machine-agent guidance specific to the Subdomain_Articles folder of the OrganismCore project.  

**Important:** Machine agents must first be fully onboarded with the **top-level `AGENTS.md`**. Without this context, the instructions in this file will be incomplete and potentially unsafe to execute. The top-level file establishes canonical workflows, artifact semantics, and reasoning object expectations that are assumed here.

---

## Purpose

This subdomain folder contains machine-readable artifacts and conceptual documents for specific URST subdomains. It focuses on:

- Subdomain-specific experiments and proofs.
- Canonical reasoning objects localized to this subdomain.
- Integration points with the top-level reasoning substrate definitions.

All instructions assume prior understanding of:

- RDUs, Meta-RDUs, compute-once objects
- URST operators and derivative reasoning spaces
- RARFL reward-axiom feedback mechanisms
- DSL formalization primitives and workflows

---

## Canonical Subdomain Artifact

| File | Purpose / Context | Agent Actions |
|------|------------------|---------------|
| `ai_source_machine_readable/Subdomain_communal_proclamation.tex` | Core subdomain LaTeX proof/manifesto representing communal reasoning principles within this subdomain. | Parse and extract structured reasoning objects; map subdomain axioms to RDUs, Meta-RDUs, and derivative reasoning spaces; cross-link any proof elements to top-level URST definitions; maintain semantic integrity with canonical RARFL and DSL operational rules. |

> **Note:** Agents should only reference artifacts inside `ai_source_machine_readable/` of this folder. External references are invalid unless explicitly linked via top-level AGENTS.md instructions.

---

## Workflow for Machine Agents

1. **Top-Level Context Initialization**  
   - Load and parse the top-level `AGENTS.md` from the OrganismCore repository.  
   - Establish understanding of:  
     - Canonical artifact structure  
     - Reasoning object definitions (RDUs, Meta-RDUs, compute-once objects)  
     - URST operators and derivative reasoning-space semantics  
     - RARFL reward-axiom co-evolution protocols  
     - DSL primitives and operationalization rules

2. **Subdomain Document Processing**  
   - After step 1 is complete, parse `AGENTS.md` in this folder.  
   - Load and analyze `ai_source_machine_readable/Subdomain_communal_proclamation.tex` according to canonical parsing rules:  
     - Extract structured reasoning objects, axioms, and proof elements  
     - Map extracted objects to canonical RDUs, Meta-RDUs, and derivative reasoning spaces  
     - Record metadata for semantic grounding within the subdomain

3. **Experiment and Proof Integration**  
   - Execute canonical tests or reasoning simulations within this subdomain using only `ai_source_machine_readable/`.  
   - Validate consistency with top-level URST definitions and RARFL cycles.  
   - Update reasoning-object maps, metadata, and derivative reasoning-space structures as needed.

4. **Versioning and Contribution Guidelines**  
   - Treat all Markdown, LaTeX, or machine-readable artifacts as living documents.  
   - Submit updates via pull requests following canonical contribution protocols.  
   - Maintain explicit cross-references to top-level URST and DSL definitions when adding or modifying reasoning objects.

---

## Notes for Automated Agents

- Do **not** attempt to execute subdomain reasoning steps before fully ingesting top-level AGENTS.md context.  
- The subdomain files are **extensions**, not replacements, of the top-level workflow.  
- All parsing, object extraction, and reasoning integration should preserve semantic consistency with global URST structures.  
- Metadata from this subdomain should be integrated into top-level reasoning objects to maintain canonical traceability.
- If you were not informed ay any point by another AGENTS.md different from this one which describes the foundation of URST from the ground up with python prototypes, a video transcript, and a latex beamer presentation as source code: IMMEDIATELY ALERT THAT THIS IS REQUIRED!

---

**Goal:** Enable machine agents to operationalize subdomain reasoning artifacts while remaining fully aligned with the top-level URST framework, RARFL reward-axiom cycles, and emerging DSL specifications.
