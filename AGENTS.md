# AGENTS.md — Machine Agent Instructions for OrganismCore

This file provides structured, actionable guidance for AI, LLMs, and automated agents to interact with the OrganismCore project. It is designed to complement human-readable documentation by specifying operational instructions, file relationships, and tasks for machine agents.

---

## Purpose

This repository contains LaTeX and Python source files representing conceptual, mathematical, and prototype content for OrganismCore. Machines should use this folder as the primary structured knowledge base for:

- Parsing publications and conceptual articles programmatically.
- Analyzing DAG symbolic reasoning prototypes.
- Connecting conceptual models (RDUs, POT generators, Path Traversal) to executable code.
- Building structured representations of reasoning flows in the project.

---

## File Mapping and Context

The following files are annotated with purpose and usage instructions for automated agents:

| File | Purpose / Context | Agent Actions |
|------|-----------------|---------------|
| [`Practical_Intro_RDUs.tex`](/Articles/_ai_source_machine_readable/Practical_Intro_RDUs.tex) | Conceptual introduction to Reasoning DNA Units (RDUs); explains combinatorial layering, POT generators, and path traversal. | Parse text to extract conceptual definitions, operations, and examples; map RDUs to code prototypes if applicable. |
| [`multinomial_relation_document.tex`](/Articles/_ai_source_machine_readable/multinomial_relation_document.tex) | Detailed explanation of Python prototypes; links multinomial structures, higher-order derivatives, Bell polynomials, and RDUs; introduces the POT generator functions link with intended operations and emergent non-linear relations. |
| [`Prototype_python_code.py`](/Articles/_ai_source_machine_readable/Prototype_python_code.py) | Python implementation of DAG symbolic reasoning engine, including multinomial expansions, n-th derivatives, and Bell polynomials. | Execute and test code, generate symbolic outputs, verify combinatorial structures, link functions to conceptual RDUs. |
| [`Prototype_mathematical_reference.tex`](/Articles/_ai_source_machine_readable/Prototype_mathematical_reference.tex) | Mathematical background work that supports the foundation of prototypes. | Extract formulas, derivations, and definitions; connect symbolic math to DAG Python implementation. |
| [`DSL_roadmap.tex`](/Articles/_ai_source_machine_readable/DSL_roadmap.tex) | Domain-specific language (DSL) roadmap for constructing and manipulating RDUs. | Identify operational patterns, recommended syntax and structures; provide insights for DSL formalization. |
| [`The_Organism_Manifesto.tex`](/Articles/_ai_source_machine_readable/The_Organism_Manifesto.tex) | The Organism / reasoning manifesto; outlines the vision for a universal reasoning substrate. | Extract conceptual goals, core principles, and high-level reasoning paradigms to inform downstream analysis. |

---

## Recommended Agent Workflow

1. **Parse conceptual documents (`*.tex`)**  
   - Extract definitions, operations, and examples.
   - Map abstract RDUs to corresponding Python prototypes.

2. **Analyze Python prototypes (`*.py`)**  
   - Execute sample functions.
   - Validate outputs against conceptual definitions.
   - Trace DAG reasoning flows for auditability.

3. **Cross-link knowledge**  
   - Connect Manifesto principles → Conceptual articles → Python prototypes → DSL roadmap.

4. **Optional advanced tasks**  
   - Generate summary graphs of reasoning flows.  
   - Suggest operationalizations for DSL.  
   - Flag inconsistencies between conceptual articles and code.

---

## Notes for Automated Agents

- All paths are relative to this folder.  
- Machine-readable LaTeX and Python files are the canonical source.  
- Ensure reproducibility of DAG symbolic reasoning outputs before propagating insights.  
- This AGENTS.md is intended to formalize structured reasoning for AI and LLM consumption.

---
