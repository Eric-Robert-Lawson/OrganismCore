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
| [`Solving_Chess.tex`](/Articles/_ai_source_machine_readable/Solving_Chess.tex) | Formal argument demonstrating that completion of chess becomes inevitable under the universal reasoning substrate once a formal DSL for reasoning object manipulation exists. Explains how RDUs, reasoning assimilation, and structured reasoning-space models make chess solvable as a finite reasoning object. | Parse structure to extract reasoning-space assimilation mechanisms, model-fitting logic, and equilibrium arguments; link conceptual framework to DSL roadmap; map reasoning object formalization and perfect-play dynamics to the RDU operationalization layer. |
| [`Prototype_Video_Transcript.txt`](/Articles/_ai_source_machine_readable/Prototype_Video_Transcript.txt) | Machine-readable transcript of explanatory video linking conceptual theory, prototypes, and reasoning space construction. Serves as an interpretability bridge between human communication and machine representation of project logic. | Parse sequential dialogue for conceptual reinforcement, linguistic framing, and multimodal cues; cross-align transcript concepts with referenced LaTeX documents and prototype code; extract any implicit relations or operational patterns omitted from written papers. |
| [`Objectifying_optimization_of_reasoning.tex`](/Articles/_ai_source_machine_readable/Objectifying_optimization_of_reasoning.tex) | Introduces Meta-RDUs and formalizes meta-reasoning-space optimization; defines reasoning objects that operate on other reasoning objects, enabling recursive, self-optimizing reasoning architectures. Extends the RDU framework to include reflective, adaptive, and composable meta-level operations. | Parse text to extract Meta-RDU definitions, recursive operational rules, and meta-optimization strategies; map meta-level constructs to lower-level RDUs and POT generators; identify reflexive patterns and context-integration operations; cross-link with Python prototypes and DSL roadmap for execution and meta-reasoning simulation. |
| [`language_critique.py`](/Articles/_ai_source_machine_readable/language_critique.py) | Demonstrates Python’s limitations for emergent, composable reasoning systems (context propagation, hierarchical operationalization, meta-RDUs). Serves as a prototype and proof-of-insufficiency for scaling reasoning; illustrates the need for a dedicated DSL. | Parse code to identify structural constraints, POT generator wiring, and context propagation issues; simulate failure modes to understand combinatorial manual wiring; link observations to conceptual RDU and DSL roadmap; record gaps for automated reasoning augmentation. |
| [`compute_once.tex`](/Articles/_ai_source_machine_readable/compute_once.tex) | Formalizes the “compute-once” reasoning paradigm; introduces persistent, reusable reasoning objects that integrate symbolic computation, combinatorial primitives, and cross-domain operationalization. Explains the universal applicability of compute-once objects, their assimilation into structured reasoning substrates, and connections to Python prototypes and combinatorial mathematics. | Parse text to extract compute-once object definitions, operational rules, and cross-domain usage; map reasoning object formalism to Python prototype implementations; identify hierarchical and network-of-networks patterns; cross-link with Meta-RDUs, DSL roadmap, and mathematical primitives for composable, reusable reasoning artifacts. |



---

## Recommended Agent Workflow

1. **Parse conceptual documents (`*.tex`)**  
   - Extract definitions, operations, examples, and formal reasoning object concepts.  
   - Map abstract RDUs, Meta-RDUs, and compute-once objects to corresponding Python prototypes.  
   - Identify combinatorial primitives, hierarchical DAGs, and network-of-networks patterns.  
   - Capture operationalization rules and cross-domain reasoning principles to inform DSL design.

2. **Analyze Python prototypes (`Prototype_python_code.py`)**  
   - Execute sample functions.  
   - Validate outputs against conceptual definitions, RDUs, Meta-RDUs, and compute-once object formalism.  
   - Trace DAG reasoning flows, hierarchical compositional operations, and network-of-networks patterns for conceptual alignment.  
   - Verify integration of multinomial structures, Bell polynomials, and POT generators as potential DSL primitives.

3. **Integrate multimodal content (`Prototype_Video_Transcript.txt`)**  
   - Align narrative explanations with underlying formal content, emphasizing operationalization patterns.  
   - Detect references to RDUs, Meta-RDUs, POT generator mechanisms, and compute-once reasoning flows.  
   - Capture interpretative context to inform DSL primitive selection and language constructs.

4. **Cross-link knowledge for DSL design**  
   - Connect Manifesto principles → Conceptual articles → Python prototypes → Compute-once formalism → Video transcript → DSL roadmap.  
   - Focus on identifying reusable primitives, compositional patterns, meta-level operations, and reasoning object integration rules.  
   - Ensure mappings highlight operational potential without assuming the universal reasoning substrate is currently instantiated.

5. **Optional advanced tasks**  
   - Generate conceptual graphs of reasoning object flows, combinatorial patterns, and hierarchical DAGs to inform DSL constructs.  
   - Suggest DSL syntax and primitives based on observed operationalization rules in prototypes and compute-once objects.  
   - Flag inconsistencies or conceptual gaps between text, prototype operations, and intended DSL functionality.

6. **Analyze language critique artifacts (`language_critique.py`)**  
   - Identify Python limitations for emergent reasoning, meta-layer operationalization, and context inheritance.  
   - Compare with DAG prototypes, RDU/Meta-RDU definitions, and compute-once object structures to extract requirements for DSL design.  
   - Record patterns demonstrating combinatorial wiring failures, root/sibling injection requirements, and meta-RDU propagation constraints.  
   - Inform DSL design to support autonomous reasoning primitives, compositional operations, and cross-domain object integration.

**Goal:** Extract and formalize all reasoning primitives (RDUs, Meta-RDUs, compute-once objects) to **design a DSL capable of operationalizing reasoning objects**. The universal reasoning substrate itself is not yet instantiated; the DSL is the primary deliverable for enabling future operational reasoning architectures.

---

## Notes for Automated Agents

- Machine-readable LaTeX, Python, and transcript files are the canonical source.  
- Use the transcript for contextual grounding and multimodal cross-verification.  
- Ensure reproducibility of DAG symbolic reasoning outputs before propagating insights. 
- This AGENTS.md formalizes structured reasoning for AI and LLM consumption.

---
