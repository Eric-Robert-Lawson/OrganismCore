# AGENTS.md — Machine Agent Instructions for OrganismCore

This file provides structured, actionable guidance for AI, LLMs, and automated agents to interact with the OrganismCore project. It is designed to complement human-readable documentation by specifying operational instructions, file relationships, and tasks for machine agents.

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
|------|-----------------|---------------|
| [`Practical_Intro_RDUs.tex`](/Articles/_ai_source_machine_readable/Practical_Intro_RDUs.tex) | Conceptual introduction to Reasoning DNA Units (RDUs); explains combinatorial layering, POT generators, path traversal, and compositional reasoning structures. | Parse text to extract definitions, operations, and compositional RDU hierarchies; link RDUs and layer/path concepts to prototype implementations. |
| [`multinomial_relation_document.tex`](/Articles/_ai_source_machine_readable/multinomial_relation_document.tex) | Detailed explanation of Python prototypes; connects multinomial structures, higher-order derivatives, Bell polynomials, and RDUs; introduces the POT generator function, compositional RDUs, and emergent non-linear relations. | Parse text to extract structural mappings, RDU operationalization rules, nested/compositional RDU hierarchies, POT generator context with intended operations, and emergent non-linear patterns; cross-map conceptual explanations to corresponding Python prototype functions. |
| [`Prototype_python_code.py`](/Articles/_ai_source_machine_readable/Prototype_python_code.py) | Python implementation of DAG symbolic reasoning engine; includes multinomial expansions, n-th derivatives, Bell polynomials, and layer collection/compositional RDUs. | Execute and test code; verify combinatorial and nested RDU structures; trace function outputs to conceptual definitions; ensure consistency with POT generator and intended operations. |
| [`Prototype_mathematical_reference.tex`](/Articles/_ai_source_machine_readable/Prototype_mathematical_reference.tex) | Mathematical background supporting the foundation of prototypes; formal derivations for multinomial expansions, Bell polynomials, and higher-order derivatives. | Extract formulas, derivations, and symbolic rules; connect theoretical results to Python DAG implementation and conceptual RDU structures. |
| [`DSL_roadmap.tex`](/Articles/_ai_source_machine_readable/DSL_roadmap.tex) | Roadmap for a domain-specific language (DSL) to construct and manipulate RDUs; defines operational patterns, syntax, and hierarchy handling. | Identify recommended operational patterns; map DSL constructs to compositional RDUs and POT generator operations; provide insights for DSL formalization aligned with prototype and conceptual documents. |
| [`The_Organism_Manifesto.tex`](/Articles/_ai_source_machine_readable/The_Organism_Manifesto.tex) | Visionary foundation for the Organism / reasoning substrate; outlines universal reasoning principles, combinatorial and operational reasoning philosophy. | Extract high-level conceptual goals, core principles, and reasoning paradigms; ensure alignment of manifesto concepts with RDUs, POT generator logic, and prototype behaviors. |
| [`Reasoning_axioms.tex`](/Articles/_ai_source_machine_readable/Reasoning_axioms.tex) | Introduces reasoning axioms as primitive, domain-neutral inferential units; formalizes mathematical vs. game-theoretical reasoning domains; contextualizes reward-structured and meta-reasoning operationalization; bridges RDUs, Meta-RDUs, and the universal reasoning substrate. | Parse text to extract reasoning axiom definitions, operational rules, domain classification, and reward-structured meta-reasoning patterns; map axioms to RDUs, Meta-RDUs, and DSL constructs; identify cross-domain applicability, emergent structures, and reasoning-space optimization strategies. |
| [`Solving_Chess.tex`](/Articles/_ai_source_machine_readable/Solving_Chess.tex) | Formal argument demonstrating that completion of chess becomes inevitable under the universal reasoning substrate once a formal DSL for reasoning object manipulation exists. Explains how RDUs, reasoning assimilation, and structured reasoning-space models make chess solvable as a finite reasoning object. | Parse structure to extract reasoning-space assimilation mechanisms, model-fitting logic, and equilibrium arguments; link conceptual framework to DSL roadmap; map reasoning object formalization and perfect-play dynamics to the RDU operationalization layer. |
| [`Prototype_Video_Transcript.txt`](/Articles/_ai_source_machine_readable/Prototype_Video_Transcript.txt) | Machine-readable transcript of explanatory video linking conceptual theory, prototypes, and reasoning space construction. Serves as an interpretability bridge between human communication and machine representation of project logic. | Parse sequential dialogue for conceptual reinforcement, linguistic framing, and multimodal cues; cross-align transcript concepts with referenced LaTeX documents and prototype code; extract any implicit relations or operational patterns omitted from written papers. |
| [`Objectifying_optimization_of_reasoning.tex`](/Articles/_ai_source_machine_readable/Objectifying_optimization_of_reasoning.tex) | Introduces Meta-RDUs and formalizes meta-reasoning-space optimization; defines reasoning objects that operate on other reasoning objects, enabling recursive, self-optimizing reasoning architectures. Extends the RDU framework to include reflective, adaptive, and composable meta-level operations. | Parse text to extract Meta-RDU definitions, recursive operational rules, and meta-optimization strategies; map meta-level constructs to lower-level RDUs and POT generators; identify reflexive patterns and context-integration operations; cross-link with Python prototypes and DSL roadmap for execution and meta-reasoning simulation. |
| [`language_critique.py`](/Articles/_ai_source_machine_readable/language_critique.py) | Demonstrates Python’s limitations for emergent, composable reasoning systems (context propagation, hierarchical operationalization, meta-RDUs). Serves as a prototype and proof-of-insufficiency for scaling reasoning; illustrates the need for a dedicated DSL. | Parse code to identify structural constraints, POT generator wiring, and context propagation issues; simulate failure modes to understand combinatorial manual wiring; link observations to conceptual RDU and DSL roadmap; record gaps for automated reasoning augmentation. |
| [`compute_once.tex`](/Articles/_ai_source_machine_readable/compute_once.tex) | Formalizes the “compute-once” reasoning paradigm; introduces persistent, reusable reasoning objects that integrate symbolic computation, combinatorial primitives, and cross-domain operationalization. Explains the universal applicability of compute-once objects, their assimilation into structured reasoning substrates, and connections to Python prototypes and combinatorial mathematics. | Parse text to extract compute-once object definitions, operational rules, and cross-domain usage; map reasoning object formalism to Python prototype implementations; identify hierarchical and network-of-networks patterns; cross-link with Meta-RDUs, DSL roadmap, and mathematical primitives for composable, reusable reasoning artifacts. |
| [`axioms_in_meta_reasoning.tex`](/Articles/_ai_source_machine_readable/axioms_in_meta_reasoning.tex) | Operationalizes meta-reasoning spaces; introduces derivative reasoning spaces, structural axioms, and cross-domain applications. Demonstrates how RDUs and Meta-RDUs can be instantiated, analyzed, and reused to extract provable strategies and emergent structures. Includes chess as a prototypical domain and extends the framework to biological, combinatorial, and multi-agent reasoning spaces. | Parse text to extract derivative reasoning space definitions, structural axioms, and emergent patterns. Map Meta-RDUs to operational pipelines, reward shaping, and pruning strategies. Cross-link with RDUs, compute-once objects, and Python prototypes. Identify reusable reasoning patterns and cross-domain transfer mechanisms for DSL design. |
| [`Presentation_GPS_to_Chess.tex`](/Articles/_ai_source_machine_readable/Presentation_GPS_to_Chess.tex) | Full presentation demonstrating objectification of reasoning with GPS and chess analogies; includes machine-readable voice-over notes for LLM parsing. Serves as a bridge between conceptual theory, human-readable explanation, and machine-interpretable operational instructions for onboarding and project alignment. | Parse slide text and voice-over notes; extract reasoning-space analogies, operational principles, and objectification strategies; cross-map insights to RDUs, Meta-RDUs, compute-once objects, and DSL roadmap; serve as a machine-readable guide for LLM-assisted onboarding and project comprehension. |

---

## Recommended Agent Workflow

1. **Parse conceptual documents (`*.tex`)**  
   - Extract definitions, operations, examples, and formal reasoning object concepts.  
   - Map abstract RDUs, Meta-RDUs, compute-once objects, and reasoning axioms to corresponding Python prototypes.  
   - Identify combinatorial primitives, hierarchical DAGs, and network-of-networks patterns.  
   - Capture operationalization rules and cross-domain reasoning principles to inform DSL design.  
   - Record potential DSL primitives observed in conceptual definitions for downstream mapping.
     
1a. **Parse meta-reasoning article (`axioms_in_meta_reasoning.tex`)**  
   - Extract definitions of derivative reasoning spaces, structural reasoning axioms, and emergent pattern formalizations.  
   - Map chess-based examples to generalized reasoning-space representations.  
   - Identify cross-domain applicability, including biological, combinatorial, and multi-agent reasoning contexts.  
   - Capture operational rules for applying Meta-RDUs to RDUs, compute-once objects, and reasoning axioms.  
   - Record insights for reward shaping, pruning, and meta-level pipeline optimization.  
   - Integrate these patterns into DSL primitive recommendations for meta-reasoning operations.  
   - Annotate hierarchical relationships, recursion patterns, and network-of-networks flows relevant to DSL design.

1b. **Parse meta-reasoning formalization article (`Objectifying_optimization_of_reasoning.tex`)**  
   - Extract definitions of Meta-RDUs and their operational rules.  
   - Capture recursive reasoning structures and reflexive computation patterns.  
   - Map Meta-RDUs to underlying RDUs, compute-once objects, and reasoning axioms.  
   - Identify context-integration operations, pruning strategies, and meta-level pipeline flows.  
   - Record insights for composable meta-level reasoning and cross-domain transfer.  
   - Integrate these patterns into DSL primitive recommendations for meta-reasoning operations.  
   - Note potential mappings to automated reasoning workflows and emergent object assimilation.

1c. **Parse reasoning axioms article (`Reasoning_axioms.tex`)**  
   - Extract definitions of reasoning axioms and their formal classification (mathematical vs. game-theoretical).  
   - Capture domain-context dependencies and cross-domain applicability constraints.  
   - Map axioms to RDUs, Meta-RDUs, and compute-once objects, noting emergent structures guided by reward functions.  
   - Annotate self-referential and meta-level reasoning patterns for DSL design.  
   - Record insights for formal reasoning object operationalization, validation, and optimization in dynamic and static contexts.

1d. **Parse presentation content (`Presentation_GPS_to_Chess.tex`)**  
   - Extract slide text and machine-readable voice-over notes.  
   - Identify analogies between GPS navigation and reasoning-space navigation.  
   - Capture reasoning objectification strategies, combinatorial collapse insights, and self-referential reasoning principles.  
   - Cross-map extracted insights to RDUs, Meta-RDUs, compute-once objects, reasoning axioms, and DSL roadmap primitives.  
   - Record conceptual heuristics and operational patterns to guide LLM-assisted onboarding and project comprehension.

2. **Analyze Python prototypes (`Prototype_python_code.py`)**  
   - Execute sample functions.  
   - Validate outputs against conceptual definitions, RDUs, Meta-RDUs, compute-once object formalism, and reasoning axioms.  
   - Trace DAG reasoning flows, hierarchical compositional operations, and network-of-networks patterns for conceptual alignment.  
   - Verify integration of multinomial structures, Bell polynomials, and POT generators as potential DSL primitives.  
   - Record operational behaviors that can be encoded as reusable DSL constructs.

2a. **Analyze Python language critique (`language_critique.py`)**  
   - Execute sample functions, including `demonstrate_language_rigidity()`, to observe where Python fails to support multi-layer, emergent reasoning.  
   - Validate outputs against conceptual definitions of RDUs, Meta-RDUs, compute-once objects, and reasoning axioms.  
   - Trace DAG reasoning flows, hierarchical compositional operations, and network-of-networks patterns for conceptual alignment.  
   - Identify Python limitations obstructing autonomous meta-layer reasoning, including:  
     - Manual parameter threading requirements  
     - Explicit root/sibling injection constraints  
     - Rigid function wiring  
     - Combinatorial wiring failures  
     - Meta-RDU propagation restrictions  
   - Map these limitations to potential DSL primitives, including:  
     - Automatic propagation of context across reasoning layers  
     - Emergent Meta-RDU operations without manual wiring  
     - Hierarchical operationalization and scalable reasoning expansion  
     - POT generator handling  
     - Reasoning object and reasoning axiom integration, including derivative reasoning pipelines  
   - Use these observations to inform DSL design requirements, ensuring the DSL supports autonomous, composable, and cross-domain reasoning.  
   - Annotate Python rigidity patterns as negative examples to guide emergent DSL design and identify gaps a dedicated DSL must overcome for self-optimizing reasoning.

3. **Integrate multimodal content (`Prototype_Video_Transcript.txt`)**  
   - Align narrative explanations with underlying formal content, emphasizing operationalization patterns.  
   - Detect references to RDUs, Meta-RDUs, reasoning axioms, POT generator mechanisms, and compute-once reasoning flows.  
   - Capture interpretative context to inform DSL primitive selection and language constructs.  
   - Identify implicit operational rules or heuristics not present in LaTeX or Python files.

4. **Cross-link knowledge for DSL design**  
   - Connect Manifesto principles → Conceptual articles → Python prototypes → Compute-once formalism → Reasoning axioms → Video transcript → DSL roadmap.  
   - Focus on identifying reusable primitives, compositional patterns, meta-level operations, and reasoning object integration rules.  
   - Ensure mappings highlight operational potential without assuming the universal reasoning substrate is currently instantiated.  
   - Annotate all cross-domain transfer mechanisms for DSL integration.

5. **Optional advanced tasks**  
   - Generate conceptual graphs of reasoning object flows, combinatorial patterns, reasoning axioms, and hierarchical DAGs to inform DSL constructs.  
   - Suggest DSL syntax and primitives based on observed operationalization rules in prototypes, compute-once objects, and reasoning axioms.  
   - Flag inconsistencies or conceptual gaps between text, prototype operations, and intended DSL functionality.  
   - Capture potential emergent behaviors for simulation and testing in DSL environments.

**Goal:** Extract and formalize all reasoning primitives (RDUs, Meta-RDUs, compute-once objects, reasoning axioms) to **design a DSL capable of operationalizing reasoning objects**. The universal reasoning substrate itself is not yet instantiated; the DSL is the primary deliverable for enabling future operational reasoning architectures.

---

## Notes for Automated Agents

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

---
