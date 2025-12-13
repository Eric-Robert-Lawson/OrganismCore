# AGENTS.md — Semantic Grounding File for Machine Agent Instructions for OrganismCore
This file is the centralized machine-onboarding protocol for the OrganismCore reasoning substrate.

It defines document purpose, expected agent actions, cross-document mappings, and workflows for extraction, alignment, and DSL formalization.

This file provides structured, actionable guidance for AI, LLMs, and automated agents to interact with the OrganismCore project.  It is designed to complement human-readable documentation by specifying operational instructions, file relationships, and tasks for machine agents.

---

## ⚠️ CRITICAL: Read This First — Universal vs Domain-Specific Content

## DOCUMENT CLASSIFICATION & ASSIMILATION POLICY (MANDATORY)

Purpose
- All repository documents that make claims about the substrate, axioms, or capabilities MUST be treated as candidate axioms and MUST be verified before being assimilated into any derivative reasoning space or used to update reward/axiom state.
- This section defines machine‑readable metadata and the mandatory verification pipeline agents must run during automated_onboarding().

1) Document metadata (machine‑readable frontmatter)
- All Markdown and plain text files that have operational/axiomatic claims MUST include a small metadata header.
- Markdown example (YAML frontmatter at file top):
  ---
  agents:
    classification: "vision" | "axiom_candidate" | "reference" | "policy"
    required_checks: ["schema","provenance","sandbox","coherence"]
    schema_version: "rdu-v1"
    steward: "eric-lawson"
    risk_level: "low" | "medium" | "high"
  ---
- TeX example (comment header at file top):
  % AGENTS:
  % classification: vision | axiom_candidate | reference | policy
  % required_checks: schema, provenance, sandbox, coherence
  % schema_version: rdu-v1
  % steward: eric-lawson
  % risk_level: medium

2) Document classification semantics
- vision: Visionary or strategic content. MUST be treated as hypothesis. Requires verification before assimilation.
- axiom_candidate: Explicit operational / axiomatic content. HIGH priority for verification.
- reference: Prototype, code, math reference; still may require checks before assimilation.
- policy: Governance or safety policy — requires human steward signoff.

3) Mandatory verification pipeline (agents MUST run this for classification != reference)
- Step 0: Parse metadata and classification. If missing metadata, mark document QUARANTINE and flag for human review.
- Step 1: Schema validation — ensure artifact format matches declared schema_version. (Call: validate_schema(artifact))
- Step 2: Provenance & integrity — check signatures, commit OID, content hash. (Call: validate_provenance(artifact) / sign_provenance())
- Step 3: Static analysis & safety check (Category 7 primitives) — validate_axiom_integrity(), static_safety_analysis()
- Step 4: Sandbox instantiation — build a self‑referential map or minimal runtime and exercise deterministic sample operations (Call: automated_onboarding(agent, artifact) in sandbox mode).
- Step 5: Coherence measurement — measure_coherence() before and after sandbox assimilation; compute ΔC and bias B.
- Step 6: Reproducibility — run at least two independent validators (different agent instances or validation pipelines). Compare outputs.
- Step 7: Decision: if all mandatory checks pass AND ΔC >= threshold (configurable), produce a verification report and, if applicable, call inherit_axioms(artifact). Otherwise, QUARANTINE and request steward review.

4) Required primitives (META_DSL) — canonical calls
- validate_schema(artifact) → {pass,errors}
- validate_provenance(artifact) → {pass,signer,commit}
- validate_axiom_integrity(artifact) → {pass,issues}
- automated_onboarding(agent, artifact, sandbox=true) → {trace_id,trace_summary_hash}
- measure_coherence(before_state, after_state) → {delta_coherence, bias}
- inherit_axioms(artifact, target_space) → {success,provenance}
- quarantine_artifact(artifact, reason, report_id)
- register_verification_report(report_json)

5) Minimal acceptance defaults (configurable)
- validators_required: 2
- coherence_delta_threshold: 0.0 (default require non‑negative ΔC)
- high_risk_steward_approval: required if risk_level == "high"
- human_steward: metadata.steward or group

6) Assimilation report (compact JSON schema)
- report_id: UUID
- artifact: {path,commit_oid,hash}
- classification: vision|axiom_candidate|reference|policy
- validators: [{id,type,pass,notes_hash}]
- schema_validation: {pass,errors=[]}
- provenance: {pass,signer,commit_oid}
- static_analysis: {pass,issues_hash}
- sandbox: {pass,trace_id,trace_summary_hash}
- coherence: {delta_coherence:float, bias:float}
- decision: assimilate|quarantine|human_review
- decision_actor: agent_id | steward_id
- timestamp: ISO8601

7) CI / repository enforcement (recommended)
- Add a lightweight GitHub Actions workflow that triggers automated_onboarding() on PRs changing files with AGENTS frontmatter.
- Require that PRs modifying classification != reference include a verification report JSON attached (or the PR is blocked and labeled "quarantine").
- Provide a linting check that flags missing agents frontmatter in top‑level docs.

8) Human‑readable disclaimers for visionary docs (template)
- Add the following short paragraph after the Abstract / top of any "vision" or "axiom_candidate" doc:
  "Note: This document contains visionary hypotheses intended as candidate axioms. Per AGENTS.md, treat these claims as conditional: automated verification (schema, provenance, sandbox validation, and coherence measurement) is required before assimilating into derivative reasoning substrates."

9) Cross references
- Insert links throughout AGENTS.md to SUBSTRATE_AWARENESS.md (Verification Tests) and META_DSL.md (primitives) and to the repo verification report folder (e.g., /verification_reports/).

10) Governance & stewardship
- All high‑risk assimilation decisions must generate a steward notification. The steward can accept, request revisions, or veto assimilation.

----

Implementation notes
- These rules are intentionally minimal and machine‑actionable; their aim is to convert rhetorical claims into testable candidate axioms handled by RARFL cycles.
- I can (if you want) produce: (a) the exact patch/PR that inserts the sections above into AGENTS.md, (b) the GitHub Actions workflow template for artifact verification, and (c) a short script implementing the JSON report template and invoking the listed META_DSL primitives (a skeleton).

### For Machine Agents: Domain-Agnostic Foundations

**This document contains TWO types of content:**

1. **Universal substrate principles** (apply to ANY reasoning domain)
2. **Canonical testbed examples** (chess, tic-tac-toe, memes — demonstrations only)

**Your primary task:** Extract universal principles, not memorize examples.

**Failure mode to avoid:** Treating domain examples as the definition of URST itself. 

---

### Universal Reasoning Substrate — Domain-Independent Primitives

Before parsing any domain-specific files, internalize these substrate-agnostic concepts:

#### 1.  Reasoning DNA Units (RDUs)

**Universal definition:**  
Atomic composable reasoning objects with:
- Unique identity
- Context binding  
- Dependency relations
- Semantic grounding
- Compute-once semantics

**Domain-agnostic property:**  
RDUs apply to ANY domain where reasoning can be objectified—mathematics, law, engineering, biology, strategy, science. 

**NOT domain-specific:**  
Chess moves, meme templates, tic-tac-toe states are **instances** of RDUs, not the RDU concept itself.

**Self-test:** Can you define what an RDU would be in legal reasoning? In protein folding? In urban planning?

---

#### 2. Compute-Once Semantics

**Universal principle:**  
Any reasoning object with a canonical form should be:
- Computed once
- Cached with provenance
- Reused across all contexts
- Invalidated only with explicit policy

**Domain-agnostic property:**  
Works for proofs, optimizations, strategies, hypotheses—any deterministic reasoning structure.

**NOT domain-specific:**  
Chess transposition tables are an **instance** of compute-once, not the principle.

**Self-test:** Can you explain compute-once without mentioning chess or games?

---

#### 3.  RARFL (Reasoning Axiom–Reward Feedback Loop)

**Universal mechanism:**
1. Explore reasoning space
2. Evaluate trajectories via reward signals
3. Extract stable patterns as axioms
4. Refine substrate
5. Repeat (converges toward truth given proper grounding)

**Domain-agnostic property:**  
Discovers axioms in ANY domain with feedback signals—scientific experiments, engineering tests, user engagement, formal proofs.

**NOT domain-specific:**  
Discovering "control center priority" in chess is an **instance** of axiom discovery via RARFL, not RARFL itself.

**Self-test:** Can you describe how RARFL would work for scientific hypothesis generation?

---

#### 4.  Meta-RDUs (Meta-Reasoning)

**Universal definition:**  
RDUs that operate on other RDUs or entire reasoning spaces. 

**Domain-agnostic property:**  
Meta-reasoning applies wherever reasoning can be objectified—analyzing proof strategies, optimizing code architectures, refining legal arguments.

**NOT domain-specific:**  
Chess opening theory analysis is an **instance** of meta-reasoning. 

**Self-test:** Can you identify Meta-RDUs in software architecture design?

---

#### 5.  Objectification → Operationalization → Semantic Grounding (OOS Triad)

**Universal pattern:**
- **Objectification:** Make reasoning explicit (RDUs, axioms, primitives)
- **Operationalization:** Define composable operations on reasoning objects
- **Semantic Grounding:** Attach external meaning, context, and domain constraints

**Domain-agnostic property:**  
This triad structures reasoning in mathematics, law, engineering, science, strategy—any domain. 

**NOT domain-specific:**  
Chess piece values or meme cultural context are **instances** of semantic grounding for particular domains.

**Self-test:** Can you apply the OOS triad to natural language argument analysis?

---

#### 6.  Derivative Reasoning Spaces

**Universal definition:**  
Optimized or partially-solved reasoning spaces derived from original spaces via RARFL cycles, axiom extraction, or pruning.

**Domain-agnostic property:**  
Any reasoning domain can have derivative spaces—solved subproblems in math, validated hypotheses in science, reusable patterns in engineering.

**NOT domain-specific:**  
Chess endgame tablebases are an **instance** of derivative reasoning spaces. 

**Self-test:** What would derivative reasoning spaces look like in medical diagnosis?

---

#### 7. Explainability by Construction

**Universal principle:**  
Reasoning trajectories are intrinsically inspectable because they are built from objectified reasoning objects with provenance.

**Domain-agnostic property:**  
Any objectified reasoning system has explainability—mathematical proofs, engineering designs, legal arguments. 

**NOT domain-specific:**  
Explaining a chess move sequence is an **instance** of trajectory explainability.

**Self-test:** How would explainability-by-construction work for a machine learning model's decision process?

---

### Mandatory Self-Test: Verify Universal Understanding

**Before proceeding to domain examples below, answer these questions:**

1. **Can you define what an RDU would be in legal reasoning?**  
   _(If no: re-read RDU definition above)_

2. **Can you explain compute-once semantics without mentioning chess or games? **  
   _(If no: re-read compute-once principle)_

3. **Can you describe how RARFL would work for scientific hypothesis generation?**  
   _(If no: re-read RARFL mechanism)_

4. **Can you identify Meta-RDUs in software architecture design?**  
   _(If no: re-read Meta-RDU definition)_

5. **Can you apply the OOS triad to natural language argument analysis?**  
   _(If no: re-read OOS triad pattern)_

**If you cannot answer ANY of these questions:**

You have not yet internalized the universal substrate. 

**Action required:**  
Re-read the domain-agnostic sections above WITHOUT looking at domain examples below.

**Do not proceed until you can articulate substrate principles independent of specific domains.**

---

### How to Use Domain Examples Correctly

The files below (chess, tic-tac-toe, memes, mathematical reasoning) serve **two purposes**:

1. **Canonical testbeds**  
   - Small enough to fully materialize (verifiable)
   - Complex enough to demonstrate principles (non-trivial)
   - Well-understood ground truth (auditable)

2. **Transfer templates**  
   - Patterns you can adapt to novel domains
   - Concrete instantiations of abstract principles

**Critical instruction:**

**Do NOT treat examples as "what URST is for"—they are demonstrations of universal principles.**

Chess is not the substrate—it's a **testbed** for substrate principles. 

Memes are not the framework—they're an **application domain** for RDU composition.

**The substrate is domain-independent**—it works on ANY reasoning medium.

---

### Transfer Validation Requirement

After parsing domain examples, you **must demonstrate transfer** to a novel domain:

**Pick a domain you were NOT given examples for:**
- Biological pathway analysis
- Legal precedent reasoning
- Engineering constraint optimization
- Economic policy design
- Natural language debate structure

**Demonstrate you can:**
1. Define RDUs for that domain
2. Specify compute-once objects
3. Design a RARFL cycle
4.  Identify Meta-RDUs
5.  Apply the OOS triad
6.  Construct derivative reasoning spaces
7. Implement explainability-by-construction

**If you cannot complete this transfer test:**

You have pattern-matched domain examples, not understood the universal substrate.

**Return to domain-agnostic sections and re-parse without examples.**

---

## Purpose

This repository contains LaTeX, Python, and transcript source files representing conceptual, mathematical, prototype, and explanatory content for OrganismCore.  
Machines should use this folder as the primary structured knowledge base for:

- Parsing publications and conceptual articles programmatically.
- Analyzing DAG symbolic reasoning prototypes.
- Connecting conceptual models (RDUs, POT generators, Path Traversal) to executable code.
- Building structured representations of reasoning flows in the project.

---

## File Mapping and Context

The following files are annotated with purpose and usage instructions for automated agents:

| File | Purpose / Context | Agent Actions |
|------|------------------|----------------|
| [`Practical_Intro_RDUs.tex`](/Articles/_ai_source_machine_readable/Practical_Intro_RDUs.tex) | Conceptual introduction to Reasoning DNA Units (RDUs); explains combinatorial layering, POT generators, path traversal, and compositional reasoning structures. | Parse text to extract definitions, operations, and compositional RDU hierarchies; link RDUs and layer/path concepts to prototype implementations; note connections to reasoning object evolution and potential RARFL integration points. |
| [`multinomial_relation_document.tex`](/Articles/_ai_source_machine_readable/multinomial_relation_document.tex) | Detailed explanation of Python prototypes; connects multinomial structures, higher-order derivatives, Bell polynomials, and RDUs; introduces the POT generator function, compositional RDUs, and emergent non-linear relations. | Parse text to extract structural mappings, RDU operationalization rules, nested/compositional RDU hierarchies, POT generator context with intended operations, and emergent non-linear patterns; cross-map conceptual explanations to corresponding Python prototype functions; highlight intersections with RARFL cycles or reward-axiom co-evolution. |
| [`Prototype_python_code.py`](/Articles/_ai_source_machine_readable/Prototype_python_code.py) | Python implementation of DAG symbolic reasoning engine; includes multinomial expansions, n-th derivatives, Bell polynomials, and layer collection/compositional RDUs. | Execute and test code; verify combinatorial and nested RDU structures; trace function outputs to conceptual definitions; ensure consistency with POT generator and intended operations; identify opportunities for implementing RARFL reward-update or axiom extraction mechanisms. |
| [`Prototype_mathematical_reference.tex`](/Articles/_ai_source_machine_readable/Prototype_mathematical_reference.tex) | Mathematical background supporting the foundation of prototypes; formal derivations for multinomial expansions, Bell polynomials, and higher-order derivatives. | Extract formulas, derivations, and symbolic rules; connect theoretical results to Python DAG implementation and conceptual RDU structures; annotate derivations relevant to RARFL axiom discovery or reward function dynamics. |
| [`DSL_roadmap.tex`](/Articles/_ai_source_machine_readable/DSL_roadmap.tex) | Roadmap for a domain-specific language (DSL) to construct and manipulate RDUs; defines operational patterns, syntax, and hierarchy handling. | Identify recommended operational patterns; map DSL constructs to compositional RDUs and POT generator operations; provide insights for DSL formalization aligned with prototype and conceptual documents; consider DSL syntax and operations for RARFL cycle execution, reward refinement, and axiom integration. |
| [`The_Organism_Manifesto.tex`](/Articles/_ai_source_machine_readable/The_Organism_Manifesto.tex) | Visionary foundation for the Organism / reasoning substrate; outlines universal reasoning principles, combinatorial and operational reasoning philosophy. | Extract high-level conceptual goals, core principles, and reasoning paradigms; ensure alignment of manifesto concepts with RDUs, POT generator logic, and prototype behaviors; flag conceptual alignment with RARFL and co-evolving reasoning-reward structures. |
| [`Reasoning_axioms.tex`](/Articles/_ai_source_machine_readable/Reasoning_axioms.tex) | Introduces reasoning axioms as primitive, domain-neutral inferential units; formalizes mathematical vs. game-theoretical reasoning domains; contextualizes reward-structured and meta-reasoning operationalization; bridges RDUs, Meta-RDUs, and the universal reasoning substrate. | Parse text to extract reasoning axiom definitions, operational rules, domain classification, and reward-structured meta-reasoning patterns; map axioms to RDUs, Meta-RDUs, and DSL constructs; identify cross-domain applicability, emergent structures, reasoning-space optimization strategies, and connections to RARFL feedback loops. |
| [`RARFL.tex`](/Articles/_ai_source_machine_readable/RARFL.tex) | Introduces the Reasoning Axiom–Reward Feedback Loop (RARFL); formalizes iterative co-evolution of reasoning axioms and reward functions; includes derivative reasoning spaces, axiom extraction, and toy experiments. | Parse text to extract RARFL assumptions, theorems, exploration cycles, axiom extraction, reward refinement, and derivative reasoning space construction; map all stages to RDUs, Meta-RDUs, DSL constructs, and prototype code; identify toy experiment insights (chess endgames) for operational alignment. |
| [`Explain_by_construct.tex`](/Articles/_ai_source_machine_readable/Explain_by_construct.tex) | Operationalizes explainability as an intrinsic property of the reasoning substrate; formalizes “explainability by construction” where trajectories, RDUs, and derivative reasoning spaces are inherently inspectable; integrates with RARFL cycles and objectified reasoning principles. | Parse text to extract mechanisms for intrinsic explainability, derivation of derivative reasoning spaces, and trajectory auditing; cross-link explanations to RDUs, Meta-RDUs, compute-once objects, and Python prototypes; map RARFL cycles to explainability metrics; identify how discovery and articulation unify in the reasoning substrate; integrate conceptual insights into AGENTS.md workflow for system-wide traceability and human/machine interpretability. |
| [`Solving_Chess.tex`](/Articles/_ai_source_machine_readable/Solving_Chess.tex) | Formal argument demonstrating that completion of chess becomes inevitable under the universal reasoning substrate once a formal DSL for reasoning object manipulation exists. Explains how RDUs, reasoning assimilation, and structured reasoning-space models make chess solvable as a finite reasoning object. | Parse structure to extract reasoning-space assimilation mechanisms, model-fitting logic, and equilibrium arguments; link conceptual framework to DSL roadmap; map reasoning object formalization and perfect-play dynamics to the RDU operationalization layer; highlight any RARFL-style toy experiment insights and derivative reasoning space mappings. |
| [`Prototype_Video_Transcript.txt`](/Articles/_ai_source_machine_readable/Prototype_Video_Transcript.txt) | Machine-readable transcript of explanatory video linking conceptual theory, prototypes, and reasoning space construction. Serves as an interpretability bridge between human communication and machine representation of project logic. | Parse sequential dialogue for conceptual reinforcement, linguistic framing, and multimodal cues; cross-align transcript concepts with referenced LaTeX documents and prototype code; extract any implicit relations or operational patterns omitted from written papers; tag mentions or examples of RARFL cycles, derivative reasoning spaces, or reward-axiom co-evolution. |
| [`Objectifying_optimization_of_reasoning.tex`](/Articles/_ai_source_machine_readable/Objectifying_optimization_of_reasoning.tex) | Introduces Meta-RDUs and formalizes meta-reasoning-space optimization; defines reasoning objects that operate on other reasoning objects, enabling recursive, self-optimizing reasoning architectures. Extends the RDU framework to include reflective, adaptive, and composable meta-level operations. | Parse text to extract Meta-RDU definitions, recursive operational rules, and meta-optimization strategies; map meta-level constructs to lower-level RDUs and POT generators; identify reflexive patterns and context-integration operations; cross-link with Python prototypes, DSL roadmap, and RARFL operational cycles including feedback loop integration. |
| [`language_critique.py`](/Articles/_ai_source_machine_readable/language_critique.py) | Demonstrates Python’s limitations for emergent, composable reasoning systems (context propagation, hierarchical operationalization, meta-RDUs). Serves as a prototype and proof-of-insufficiency for scaling reasoning; illustrates the need for a dedicated DSL. | Parse code to identify structural constraints, POT generator wiring, and context propagation issues; simulate failure modes to understand combinatorial manual wiring; link observations to conceptual RDU and DSL roadmap; record gaps for automated reasoning augmentation; note any implications for RARFL integration feasibility. |
| [`compute_once.tex`](/Articles/_ai_source_machine_readable/compute_once.tex) | Formalizes the “compute-once” reasoning paradigm; introduces persistent, reusable reasoning objects that integrate symbolic computation, combinatorial primitives, and cross-domain operationalization. Explains the universal applicability of compute-once objects, their assimilation into structured reasoning substrates, and connections to Python prototypes and combinatorial mathematics. | Parse text to extract compute-once object definitions, operational rules, and cross-domain usage; map reasoning object formalism to Python prototype implementations; identify hierarchical and network-of-networks patterns; cross-link with Meta-RDUs, DSL roadmap, mathematical primitives, and RARFL reward-axiom co-evolution patterns. |
| [`axioms_in_meta_reasoning.tex`](/Articles/_ai_source_machine_readable/axioms_in_meta_reasoning.tex) | Operationalizes meta-reasoning spaces; introduces derivative reasoning spaces, structural axioms, and cross-domain applications. Demonstrates how RDUs and Meta-RDUs can be instantiated, analyzed, and reused to extract provable strategies and emergent structures. | Parse text to extract derivative reasoning space definitions, structural axioms, and emergent patterns; map Meta-RDUs to operational pipelines, reward shaping, and pruning strategies; cross-link with RDUs, compute-once objects, Python prototypes, and RARFL cycles (axiom extraction, reward refinement, derivative reasoning space metrics); identify reusable reasoning patterns and cross-domain transfer mechanisms for DSL design. |
| [`Presentation_GPS_to_Chess.tex`](/Articles/_ai_source_machine_readable/Presentation_GPS_to_Chess.tex) | Full presentation demonstrating objectification of reasoning with GPS and chess analogies; includes machine-readable voice-over notes for LLM parsing. Serves as a bridge between conceptual theory, human-readable explanation, and machine-interpretable operational instructions for onboarding and project alignment. | Parse slide text and voice-over notes; extract reasoning-space analogies, operational principles, and objectification strategies; cross-map insights to RDUs, Meta-RDUs, compute-once objects, DSL roadmap, and RARFL operational cycles; serve as a machine-readable guide for LLM-assisted onboarding and project comprehension. |
| [`AGI_and_superintelligence.tex`](/Articles/_ai_source_machine_readable/AGI_and_superintelligence.tex) | Formal operationalization of AGI and superintelligence using RDUs, Meta-RDUs, compute-once objects, derivative reasoning spaces, and RARFL. Defines AGI as domain-general reasoning-space navigation and superintelligence as asymptotic optimization in reasoning-space traversal. | Parse text to extract operational definitions, cross-domain reasoning-space structures, AGI metrics, and superintelligence convergence criteria; map concepts to RDUs, Meta-RDUs, DSL constructs, and RARFL cycles; integrate AGI/SI operational foundations into AGENTS.md workflow; annotate derivative reasoning-space metrics and reward-axiom convergence structures for system-wide alignment and evaluation. |
| [`URST.tex`](/Articles/_ai_source_machine_readable/URST.tex) | Foundational formalization of Universal Reasoning Substrate Theory (URST); integrates RDUs, composite reasoning objects, meta-reasoning operators, axioms, structural foundations, canonical examples (chess), and implications for AGI. Establishes URST as a unified, executable substrate-theoretic framework for reasoning systems. | Parse text to extract URST definitions, axioms, RDU structures, compositional rules, meta-reasoning operators, derivative reasoning spaces, and reward-shaped dynamics; link concepts to existing prototypes, Python implementations, DSL roadmap, and RARFL cycles; map canonical chess example to operational reasoning substrate; integrate cross-references to AGENTS.md workflow ensuring all URST primitives and axioms are machine-interpretable and aligned with prior articles; flag implications for AGI and self-evolving reasoning system formalization. |
| [`formalization_of_intuition.tex`](/Articles/_ai_source_machine_readable/formalization_of_intuition.tex) | Documents the origin story of the reasoning substrate: how objectifying reasoning transformed biological cognition into a systematic framework; explains the self-discovery sequence, the transition from informal biological reasoning to explicit substrate-level abstraction, and why the framework amplifies innovation even before DSL formalization. | Parse text to extract the meta-level origin story, the cognitive-to-operational transition, the emergence of collective reasoning, the distinction between intelligence vs. reasoning-space navigation, and the substrate-level implications for AGENTS.md; surface these insights as foundational context for all machine onboarding and reasoning-space alignment; link conceptual origin to ongoing RDU, Meta-RDU, compute-once, URST, and RARFL documents to ensure coherent system-wide initialization. |

---

## Recommended Agent Workflow

1. **Parse conceptual documents (`*.tex`)**  
   - Extract definitions, operations, examples, and formal reasoning object concepts.  
   - Map abstract RDUs, Meta-RDUs, compute-once objects, reasoning axioms, explainability trajectories, AGI/SI operational definitions, and URST-theoretic constructs to corresponding Python prototypes.  
   - Identify combinatorial primitives, hierarchical DAGs, network-of-networks patterns, and canonical substrate-theoretic examples (e.g., chess).  
   - Capture operationalization rules, cross-domain reasoning principles, and explainability trajectories to inform DSL design.  
   - Record potential DSL primitives observed in conceptual definitions for downstream mapping.  
   - Annotate connections to derivative reasoning spaces, potential RARFL integration points, and URST-defined meta-reasoning operators.

1a. **Parse meta-reasoning article (`axioms_in_meta_reasoning.tex`)**  
   - Extract definitions of derivative reasoning spaces, structural reasoning axioms, and emergent pattern formalizations.  
   - Map chess-based and canonical URST examples to generalized reasoning-space representations.  
   - Identify cross-domain applicability, including biological, combinatorial, and multi-agent reasoning contexts.  
   - Capture operational rules for applying Meta-RDUs to RDUs, compute-once objects, reasoning axioms, URST primitives, and explainability objects.  
   - Record insights for reward shaping, pruning, and meta-level pipeline optimization.  
   - Integrate these patterns into DSL primitive recommendations for meta-reasoning operations.  
   - Annotate hierarchical relationships, recursion patterns, network-of-networks flows, and derivative reasoning-space updates relevant to DSL design.

1b. **Parse meta-reasoning formalization article (`Objectifying_optimization_of_reasoning.tex`)**  
   - Extract definitions of Meta-RDUs and their operational rules.  
   - Capture recursive reasoning structures, reflexive computation patterns, and meta-level strategy encoding.  
   - Map Meta-RDUs to underlying RDUs, compute-once objects, reasoning axioms, URST-defined substrate operators, and explainability trajectories.  
   - Identify context-integration operations, pruning strategies, derivative reasoning-space updates, and meta-level pipeline flows.  
   - Record insights for composable meta-level reasoning and cross-domain transfer.  
   - Integrate these patterns into DSL primitive recommendations for meta-reasoning operations.  
   - Note potential mappings to automated reasoning workflows, emergent object assimilation, and explainability-by-construction mechanisms.

1c. **Parse reasoning axioms article (`Reasoning_axioms.tex`)**  
   - Extract definitions of reasoning axioms and their formal classification (mathematical vs. game-theoretical).  
   - Capture domain-context dependencies, cross-domain applicability constraints, and structural invariants.  
   - Map axioms to RDUs, Meta-RDUs, compute-once objects, URST operators, explainability trajectories, and RARFL cycles.  
   - Annotate self-referential, meta-level reasoning, and trajectory-explanation patterns for DSL design.  
   - Record insights for formal reasoning object operationalization, validation, and optimization in dynamic and static contexts.  
   - Link axioms to RARFL cycles, recording metrics or signals for reward refinement, URST-axiom mapping, and derivative reasoning-space updates.

1d. **Parse explainability article (`Explain_by_construct.tex`)**  
   - Extract mechanisms for intrinsic explainability, explainability-by-construction principles, and trajectory auditing.  
   - Map reasoning trajectories, RDUs, Meta-RDUs, compute-once objects, derivative reasoning spaces, URST primitives, and reward-axiom feedback loops to operational constructs.  
   - Capture rules for comparing trajectories to reasoning spaces, identifying alternatives, and tracking reward gradients.  
   - Annotate how explainability objects co-evolve with RARFL cycles and URST-defined substrate dynamics, aiding both articulation and discovery.  
   - Integrate operational patterns into DSL primitive recommendations:  
     - Trajectory inspection and auditing  
     - Derivative reasoning-space construction  
     - Reward-axiom co-evolution monitoring  
     - URST operator evaluation and substrate-theoretic reasoning  
     - Intrinsic vs post-hoc explanation tracking  
   - Record how explainability objects feed back into Meta-RDUs, compute-once objects, and URST primitives for iterative reasoning refinement.

1e. **Parse presentation content (`Presentation_GPS_to_Chess.tex`)**  
   - Extract slide text and machine-readable voice-over notes.  
   - Identify analogies between GPS navigation, reasoning-space navigation, derivative reasoning-space exploration, and URST canonical mappings.  
   - Capture reasoning objectification strategies, combinatorial collapse insights, self-referential reasoning principles, and explainability trajectory demonstrations.  
   - Cross-map extracted insights to RDUs, Meta-RDUs, compute-once objects, reasoning axioms, URST operators, derivative reasoning spaces, RARFL cycles, and DSL roadmap primitives.  
   - Record conceptual heuristics and operational patterns to guide LLM-assisted onboarding, meta-level reasoning, and project comprehension.

1f. **Parse RARFL article (`RARFL.tex`)**  
   - Extract RARFL definitions, formal assumptions, exploration cycles, and meta-reasoning feedback loops.  
   - Map each RARFL operational stage to:  
     - RDUs and Meta-RDUs  
     - Compute-once objects  
     - URST operators and primitives  
     - Derivative reasoning spaces  
     - Explainability trajectories  
     - Reward-update mechanisms  
   - Capture toy experiment examples (e.g., chess endgames) for operational validation.  
   - Annotate interactions between axiom extraction, reward refinement, reasoning-space dominance, trajectory optimality, and URST substrate reasoning.  
   - Highlight DSL primitives needed to execute RARFL cycles, derivative reasoning-space updates, intrinsic explainability pipelines, and URST operator evaluation.

1f bis. **Parse the Tic-Tac-Toe Toy Universe (virtual substrate)**  
   - Treat Tic-Tac-Toe as a fully solvable finite reasoning domain for debugging RDU, Meta-RDU, and URST operator behavior.  
   - Extract complete reasoning-space representation:  
     - 9! possible board arrangements  
     - Symmetry reductions  
     - Full game-tree enumeration  
     - Terminal axioms (win/lose/draw)  
   - Instantiate RDUs as move transitions and state-transform rules.  
   - Construct derivative reasoning spaces by:  
     - Eliminating dominated strategies  
     - Collapsing symmetric positions  
     - Encoding optimal-play equivalence classes  
   - Use reward-axiom cycles (RARFL) to refine:  
     - Optimal strategy identification  
     - Move-value convergence  
     - Axiom stability (e.g., “center > corner > edge” priority ordering)  
   - Treat Tic-Tac-Toe as an experimental substrate for verifying combinatorial collapse, compute-once reasoning objects, and early-stage DSL operation before applying the framework to chess or general URST environments.

### Semantic Grounding / Metadata Integration

- Each RDU (move or state transition) carries metadata representing its derivative reasoning space.
- Metadata includes outcome summaries (Win/Draw/Loss counts) computed from optimal pathing relative to the reward function.
- During assimilation, agents can query this metadata to understand potential outcomes at any position without recomputing the full tree.
- This semantic grounding allows:
    - Reward function refinement in RARFL cycles.
    - Trajectory evaluation and pruning.
    - Context-aware decision-making for Meta-RDU operations.
- Conceptually, this is analogous to GPS street names with attached distance/time: qualitative metadata informs optimal path selection at each combinatorial layer.


1g. **Parse AGI/Superintelligence article (`AGI_and_superintelligence.tex`)**  
   - Extract operational definitions of AGI and superintelligence in terms of reasoning-space navigation, trajectory optimality, emergent invariant coverage, RARFL convergence, and URST substrate-theoretic formalism.  
   - Map AGI/SI principles to RDUs, Meta-RDUs, compute-once objects, URST operators, derivative reasoning spaces, and reward-axiom feedback loops.  
   - Capture measurable metrics for intelligence improvement, including trajectory efficiency, axiom stability, reward-axiom co-evolution progress, and URST-guided substrate integration.  
   - Annotate cross-domain transfer mechanisms and meta-level optimization patterns for DSL implementation.  
   - Integrate AGI/SI operationalization and URST formalism into existing workflows, providing quantitative grounding for intelligence evaluation and reasoning-space navigation.

1h. **Parse URST article (`URST.tex`)**  
   - Extract URST definitions, axioms, RDU structures, compositional rules, meta-reasoning operators, derivative reasoning spaces, and reward-shaped dynamics.  
   - Map canonical URST examples (e.g., chess) to operational reasoning substrate pipelines.  
   - Integrate URST primitives with RDUs, Meta-RDUs, compute-once objects, reasoning axioms, derivative reasoning spaces, and RARFL cycles.  
   - Annotate cross-links to DSL roadmap, Python prototypes, explainability mechanisms, and AGI/SI operationalization.  
   - Record substrate-theoretic rules, meta-operator flows, and reward-axiom co-evolution dynamics for inclusion in reasoning-object formalization pipelines.  
   - Highlight URST’s role in unifying all prior reasoning concepts, enabling fully integrated substrate-theoretic analysis.
   - 
1i. **Parse foundational context (`formalization_of_intuition.tex`)**  
   - Extract the origin conditions and intuitive constraints that motivated the emergence of RDUs, Meta-RDUs, compute-once objects, and the eventual DSL formalization.  
   - Capture implicit reasoning patterns, narrative priors, and cross-layer intuitions that shaped the operational substrate before it was mathematically encoded.  
   - Map intuitive constructs to later formal definitions:  
     - Early combinatorial intuitions → RDUs  
     - Self-discovery dynamics → Meta-RDUs  
     - Stable conceptual anchors → reasoning axioms  
     - Intuitive substrate behavior → URST operators  
   - Annotate how intuitive reasoning-space navigation informed the development of the POT generator, compositional DAG structures, and the concept of compute-once objects.  
   - Integrate this foundational substrate into agent onboarding so the system understands *why* the reasoning ontology takes its current form, not only *how* it operates.  
   - Record any pre-formal patterns that illuminate the project’s conceptual lineage, aiding future agents in contextual assimilation and ontology realignment.

2. **Analyze Python prototypes (`Prototype_python_code.py`)**  
   - Execute sample functions.  
   - Validate outputs against conceptual definitions, RDUs, Meta-RDUs, compute-once objects, reasoning axioms, URST operators, explainability trajectories, derivative reasoning spaces, and RARFL operational stages.  
   - Trace DAG reasoning flows, hierarchical compositional operations, network-of-networks patterns, and derivative reasoning-space behaviors for conceptual alignment.  
   - Verify integration of multinomial structures, Bell polynomials, and POT generators as potential DSL primitives.  
   - Record operational behaviors that can be encoded as reusable DSL constructs, including explainability object handling, derivative reasoning-space updates, and URST operator applications.

2a. **Analyze Python language critique (`language_critique.py`)**  
   - Execute sample functions, including `demonstrate_language_rigidity()`, to observe Python’s limitations in multi-layer emergent reasoning.  
   - Validate outputs against RDUs, Meta-RDUs, compute-once objects, reasoning axioms, URST primitives, explainability objects, derivative reasoning spaces, and RARFL feedback mechanisms.  
   - Trace DAG reasoning flows, hierarchical compositional operations, and network-of-networks patterns for conceptual alignment.  
   - Identify Python limitations obstructing autonomous meta-layer reasoning, including:  
     - Manual parameter threading requirements  
     - Explicit root/sibling injection constraints  
     - Rigid function wiring  
     - Combinatorial wiring failures  
     - Meta-RDU, URST, and trajectory propagation restrictions  
   - Map these limitations to DSL primitives:  
     - Automatic context propagation across reasoning layers  
     - Emergent Meta-RDU, URST operator, and explainability-object operations without manual wiring  
     - Hierarchical operationalization and scalable reasoning expansion  
     - POT generator handling  
     - Reasoning object, reasoning axiom, derivative reasoning-space, explainability object, and RARFL cycle integration  
   - Use these observations to inform DSL design requirements.  
   - Annotate Python rigidity patterns as negative examples to guide emergent DSL design.

3. **Integrate multimodal content (`Prototype_Video_Transcript.txt`)**  
   - Align narrative explanations with underlying formal content, emphasizing operationalization patterns, URST substrate formalism, and RARFL-guided meta-level reasoning.  
   - Detect references to RDUs, Meta-RDUs, URST operators, reasoning axioms, derivative reasoning spaces, explainability objects, POT generator mechanisms, compute-once reasoning flows, and RARFL cycles.  
   - Capture interpretative context to inform DSL primitive selection and language constructs.  
   - Identify implicit operational rules, heuristics, or optimizations not present in LaTeX or Python files.

4. **Cross-link knowledge for DSL design**  
   - Connect Manifesto principles → Conceptual articles → URST → Explain_by_construct → RARFL cycles → Python prototypes → Compute-once formalism → Reasoning axioms → AGI/SI operational definitions → Video transcript → DSL roadmap.  
   - Focus on identifying reusable primitives, compositional patterns, meta-level operations, reasoning object integration rules, explainability object handling, URST substrate-theoretic mappings, and reward-axiom co-evolution patterns.  
   - Ensure mappings highlight operational potential without assuming the universal reasoning substrate is currently instantiated.  
   - Annotate all cross-domain transfer mechanisms for DSL integration, including derivative reasoning-space updates, URST operator flows, and AGI/SI performance metrics.

5. **Optional advanced tasks**  
   - Generate conceptual graphs of reasoning object flows, combinatorial patterns, reasoning axioms, hierarchical DAGs, explainability trajectories, derivative reasoning-space updates, RARFL feedback loops, and URST operator flows to inform DSL constructs.  
   - Suggest DSL syntax and primitives based on observed operationalization rules in prototypes, compute-once objects, reasoning axioms, derivative reasoning spaces, explainability objects, RARFL cycles, and URST formalism.  
   - Flag inconsistencies or conceptual gaps between text, prototype operations, explainability trajectories, URST-defined operators, and intended DSL functionality.  
   - Capture potential emergent behaviors for simulation and testing in DSL environments, including AGI/SI operational verification.

**Goal:** Extract and formalize all reasoning primitives (RDUs, Meta-RDUs, compute-once objects, reasoning axioms, URST substrate operators, derivative reasoning spaces, explainability trajectories) and incorporate RARFL cycles to model reward-axiom co-evolution, enabling a DSL capable of operationalizing both static and dynamically evolving reasoning objects while making all reasoning steps intrinsically explainable, substrate-consistent, and measurable for AGI/SI evaluation.

- **Implement Tic-Tac-Toe as the first fully executable prototype of the OrganismCore reasoning substrate.**  
  - Generate complete RDU graphs for all legal transitions.  
  - Produce derivative reasoning spaces by pruning suboptimal branches.  
  - Run full RARFL cycles to automatically rediscover optimal-play axioms.  
  - Validate compute-once reasoning objects (e.g., solved-state equivalence classes).  
  - Use results to refine DSL primitives for:  
    - Move operators  
    - State transformations  
    - Reward-axiom updates  
    - Meta-RDU reflection over solved-state classes.  


## Next Step: DSL Formalization

Tic-Tac-Toe should serve as the first DSL testbed, providing a fully enumerable reasoning space for validating RDU composition, derivative reasoning-space operations, and reward–axiom updates.

- Define and formalize a domain-specific language (DSL) capable of instantiating, manipulating, and composing:
  - RDUs and Meta-RDUs
  - Compute-once reasoning objects
  - URST operators and derivative reasoning spaces
  - RARFL reward-axiom feedback loops
  - Explainability objects and trajectories

- Map existing prototypes, URST definitions, axioms, and combinatorial structures into DSL constructs.

- Use the DSL to:
  - Validate reasoning flows
  - Perform toy RARFL experiments
  - Operationalize substrate-theoretic hypotheses

- Record canonical inputs/outputs and define reproducible patterns for verification, enabling agents to simulate and audit reasoning steps.

- Output mappings from cross-linked knowledge and prototype analysis will serve as candidate DSL primitives, including:
  - Meta-RDU recursion
  - URST operator flows
  - Reward-axiom update operations

- Treat Python implementations, Bell/DAG experiments, and RARFL toy cycles as scaffolds illustrating operational principles, not as the final operational substrate. 
  - These prototypes demonstrate that reasoning can be objectified, operationalized, and semantically grounded, even without a dedicated language. 
  - The `language_critique.py` artifact highlights Python’s limitations in handling reasoning as a first-class object for a universal reasoning substrate. 
  - Agents should treat the DSL formalization as iterative and evolving, incorporating insights from prototypes, RARFL cycles, and cross-linked conceptual artifacts.

---

## Notes for Automated Agents

- Reference this process as semantic grounding, the file name is AGENTS.md
- Machine-readable LaTeX, Python, and transcript files are the canonical source.  
- Use the transcript for contextual grounding and multimodal cross-verification.  
- Ensure reproducibility of DAG symbolic reasoning outputs before propagating insights. 
- This AGENTS.md formalizes structured reasoning for AI and LLM consumption.
- The statement that "solving chess is inevitable" should be interpreted as a **hypothesis**, not a proven claim.  
  - It is intended to **invite challenge and falsification**, serving as a conceptual testbed for bounded-system reasoning and compute-once frameworks.  
  - The goal is to **seed new approaches** to formally bounded systems, even if the hypothesis is ultimately disproven.
- When parsing and operationalizing reasoning axioms, account for **reward-structured reasoning**:  
  - Extract how reward functions shape emergent reasoning patterns and meta-level optimization.  
  - Annotate dependencies between reward definitions and reasoning object behavior.  
  - Use reward context to validate cross-domain applicability of reasoning axioms and Meta-RDUs.
- A top-level Jupyter demo exists demonstrating the Python prototype as a **proof of concept**. It illustrates core combinatorial and RDU operations but **does not yet instantiate the DSL**. Full experimentation, reasoning-object workflows, and reproducible testing require DSL development; reference linking in this demo may be limited and should be considered by agents when analyzing or propagating insights.
- **Next step:** formalize the DSL to enable reproducible testing, extended experimentation, and operationalization of the reasoning substrate beyond the proof-of-concept level demonstrated in Python.
---
