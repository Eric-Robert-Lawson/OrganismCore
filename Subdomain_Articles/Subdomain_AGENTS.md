# Subdomain_AGENTS.md — Universal Reasoning Substrate Onboarding

## Purpose
This file serves as a machine-readable onboarding guide for understanding the **Universal Reasoning Substrate (URS)**, its six sub-domains, and guidance for **communal DSL development**. 
This file is designed for **machine agents**, requiring strict, stepwise parsing, cross-file linking, and dynamic context retrieval.

---

## 0. Supplementary Context Files

The following `.tex` documents provide theory, methodology, and structural guidance for how a communal DSL can emerge from URST.  
Machine agents must parse and integrate these documents before using the instructions that follow.

| File | Purpose | Key Takeaways for Machine Agent |
|------|---------|--------------------------------|
| [`Approaching_DSL_Using_URST.tex`](ai_source_machine_readable/Approaching_DSL_Using_URST.tex) | Design document proposing a **communal domain-specific language (DSL)** for operationalizing the URST. | - DSL is a **substrate**, not a meta-reasoner. <br>- Meta-reasoning (RARFL, pruning, ML-guided search) is **external**. <br>- Provides experimental testbeds (e.g., Tic-Tac-Toe) and candidate primitive definitions. <br>- Communal workflow: propose → evaluate → integrate. |
| [`Subdomain_communal_proclamation.tex`](ai_source_machine_readable/Subdomain_communal_proclamation.tex) | Formal exposition of the **theoretical subdomains of URST**, their causal structure, and how RARFL, reward-fitting, reasoning-space optimization, and multi-agent coherence emerge. | - Establishes the **mathematical and philosophical backbone** of URST. <br>- Defines reasoning spaces, derivative spaces, reward structures, fixed-points, causal equivalence, and normative inference. <br>- Stresses **URST as a living, communal research domain**. <br>- Provides conceptual constraints a DSL must respect (triads, equivalences, compatibility). |

---

## 1. Sub-Domains Overview  
The Universal Reasoning Substrate is composed of six essential sub-domains. These arise directly from the structure defined in `Subdomain_communal_proclamation.tex` and operational ground rules in `Approaching_DSL_Using_URST.tex`.

| Sub-Domain | Description | Operational Notes |
|------------|------------|------------------|
| Reasoning Objects | Atomic units of reasoning (nodes in a reasoning DAG). | Store as composable structures; maintain provenance and context. |
| Computable-Once Substrates | Prevent redundant reasoning by caching reusable results. | Compute once → reuse globally. Ensure deterministic reuse. |
| Meta-RDUs | Reasoning about reasoning. Pruning, optimization, strategy extraction. | External to DSL; map meta-actions to RDU sets. |
| Semantic Grounding | Provide interpretable meaning to reasoning objects. | Structured metadata, domain labels, stable ontologies. |
| Reward / Feedback Loops | Evaluate reasoning trajectories and provide optimization signals. | Track reward propagation. Feed back into meta-RDUs. |
| Universal Substrate Construction | Coherent composition of all sub-domains into a single reasoning scaffold. | Maintain DAG, enforce consistency & traceability. |

---

## 2. Ontology / Structure

Machine agents must maintain URST-consistent ontology, harmonizing definitions across all files.

### Reasoning Object
- Unique ID  
- Context reference  
- Layer membership  
- Dependency relations  
- Semantic grounding  
- Optional meta-RDU mappings  

### Compute-Once Behavior
- Check cache **before** computing  
- Reuse downstream  
- Track versioning if dependencies mutate  

### Reward Loop Mechanism
- Input: completed reasoning trajectory  
- Output: reward signals  
- Function: prune, refine, optimize  

### DSL Substrate
(From `Approaching_DSL_Using_URST.tex`)
- DSL defines **objects, primitives, generators, layers**  
- Meta-reasoning is **external**  
- DSL ≈ “reasoning substrate wiring diagram”  
- External modules (e.g., ML agents) may perform pruning or search  
- Communal contributions extend the primitive set  

### URST Theoretical Constraints
(From `Subdomain_communal_proclamation.tex`)
- Reasoning is a structured triad: Objectification → Operationalization → Contextualization  
- Reward-fitting defines normative optimization  
- Causal equivalence defines reasoning-space compatibility  
- RARFL has fixed-point, attractor-like behavior  
- Multi-agent systems extend to joint reasoning spaces  

A valid DSL must **respect these constraints**.

---

## 3. Onboarding Process for a Machine Agent

### Step 1 — Parse Context Files  
1. Read all `.tex` documents.  
2. Extract:
   - Triadic reasoning structure  
   - Definitions of reasoning spaces  
   - Reward-fitting and causal equivalence rules  
   - DSL candidate primitives  
   - Communal workflow instructions  

### Step 2 — Initialize Reasoning DAG  
- Instantiate reasoning objects  
- Link dependencies  
- Attach semantic grounding  
- Integrate any DSL primitives defined in proposals  

### Step 3 — Enforce Compute-Once Semantics  
- Cache results  
- Reuse across all testbeds  
- Maintain deterministic global state  

### Step 4 — Attach Meta-RDUs (External)  
- External pruning  
- External reward fitting  
- External meta-RARFL  
The DSL **does not implement these**, but **must support integration hooks**.

### Step 5 — Communal DSL Iteration  
Reflecting RARFL:

1. Propose primitive  
2. Evaluate primitive (reward / transfer / stability metrics)  
3. Assimilate or discard  
4. Refine  

### Step 6 — Universal Substrate Assembly  
- Combine primitive-level DAGs  
- Track provenance of contributions  
- Maintain traceability and explainability  

---
## 4. Practical Examples (GPS-inspired multi-scale segmentation + testbeds)

**Design note (GPS analogy).**  
Treat the global reasoning space like a geographical map: represent it at multiple scales (zoom levels). At coarse zoom you see only major routes/regions (high-level abstractions); at fine zoom you see dense, detailed local structure (full state graphs). Use lazy evaluation, compute-once caching, and metadata density that increases with zoom. External meta-tools (pruners, ML explorers, IDE plugins) act like route planners or local guides: they request focused tiles/regions and propose local operations without forcing full global expansion.

### GPS-inspired primitives & behaviors
- **Zoom levels / tiles** — Partition reasoning space into hierarchical tiles or regions indexed by scale (e.g., `tile(scale, region_id)`).
- **Lazy evaluation** — Only materialize tile contents when requested; provide summary metadata for unmaterialized tiles (estimates, heuristic scores).
- **Progressive refinement** — Expand a tile incrementally (coarse → fine), allowing external agents to refine subspaces on demand.
- **Metadata density** — Store light summaries at coarse scales (counts, best-known axioms, heuristic bounds) and full provenance/trajectories at fine scales.
- **Prefetching & caching** — Preload neighbor tiles likely to be queried (route planning), keep compute-once results in a hierarchical cache (tile-level + node-level).
- **Canonicalization & transposition tables** — Use canonical forms and equivalence classes to merge states across tiles; reuse compute-once results across different tiles.
- **Local pruning & plugins** — IDE/agent plugins can apply domain heuristics to a tile without altering the DSL; they return pruned subspaces or annotations to be stored back in the shared substrate.
- **Relevance scoring** — Maintain a score per tile for prioritization (e.g., estimated utility, novelty, uncertainty).

### Micro-API examples (pseudo-DSL / interface)
```python
# Tile & zoom API (conceptual)
tile = get_tile(scale=2, region="center_cluster")      # returns tile metadata; lazy
if tile.is_materialized():
    nodes = tile.nodes()
else:
    summary = tile.summary()                           # high-level counts, best axioms, heuristics

# Progressive refinement
expand_tile(tile, to_scale=4, budget=100)              # materialize part of tile with a compute budget
prefetch_neighbors(tile)                               # prefetch adjacent tiles

# Compute-once & canonical lookup
canonical_id = canonicalize(state)
if cache.has(canonical_id):
    value = cache.get(canonical_id)
else:
    value = evaluate_state(state); cache.set(canonical_id, value)

# External plugin interaction (non-D Sl core)
pruned_tile = plugin_prune(tile, strategy="ml_local")  # plugin returns annotations/prunes; DSL stores results as metadata
store_tile_annotations(tile, pruned_tile.annotations)  # provenance + who/what produced them


##Testbeds using GPS approach

# Tic-Tac-Toe (tiny demo; full materialization possible)
  - **How GPS applies:** treat board symmetries as tile collapse; coarse tiles = equivalence classes, fine tiles = explicit states.
  - **Benefits:** quick global summaries (win/draw counts), targeted expansion of ambiguous tiles only.
  - **Agent steps:** build full RDU DAG for small tiles, test expand/refine workflow, measure cache hit rate and expansion budget.

# Chess (real scalability example)
  - **How GPS applies:** coarse tiles could be openings / endgame families / piece-material classes; refine into specific move trees on demand.
  - **Benefits:** avoid global expansion; reuse transposition tables across tiles; prefetch promising lines.
  - **Agent steps:** define tile taxonomy (opening family → middlegame cluster → endgame family), implement tile summaries, run incremental expansion with external pruning agents, measure coverage vs compute budget.

# Mathematical Reasoning
  - **How GPS applies:** coarse tiles = algebraic forms / expression families; fine tiles = full derivations or simplified canonical forms.
  - **Benefits:** reuse compute-once simplifications across similar symbolic subspaces.
  - **Agent steps:** canonicalize subexpressions as tiles, track compute-once reuse across proofs, measure reuse rate.

# Metrics & instrumentation (GPS style)
  - Tile materialization rate: how many tiles were expanded per experiment.
  - Cache hit rate: hierarchical cache hits (tile-level and canonical-level).
  - Expansion budget used: compute time / node evaluations per refinement step.
  - Axiom stability per tile: fraction of axioms that persist across RARFL cycles at tile and global levels.
  - Prefetch utility: metric of how often prefetches were used vs wasted.

# Agent actions (concrete)

1. **Design a tile taxonomy** for the target domain (Tic-Tac-Toe: symmetry classes; Chess: opening/middlegame/endgame families; Math: expression patterns).

2. **Implement lazy tile API** (get_tile, expand_tile, prefetch_neighbors) in the prototype runtime or as an adapter layer over Prototype_python_code.py.

3. **Implement hierarchical cache & canonicalizer** — ensure canonicalization rules are domain-specific but reusable.

4. **Create plugin hooks** (read-only access + annotation channel) so external meta-reasoners can prune/explore and record provenance.

5. **Run controlled experiments:**
  - Baseline: full expansion (if possible) or naive search.
  - GPS: lazy + tile prefetching + external pruning.
  - Compare metrics above (cache hit, expansion budget, axiom stability).

6. **Record artifacts:** tile summaries (JSON), expansions traces, cache logs, plugin annotations with provenance. Use these as expected outputs for agents and CI.

# Governance & provenance

  - Tag tile artifacts with producer (agent id / plugin id), timestamp, and parameters used (budget, seed).

  - Require that plugin annotations include reproducible parameters so others can re-run or audit pruning decisions.

---

## 5. Evaluation / Metrics

### Substrate Metrics
- Completeness  
- Semantic consistency  
- Compute-once efficiency  
- Reward stability  
- Explainability  

### DSL Metrics
- Primitive generality  
- Cross-domain transfer  
- Reusability  
- RARFL stability under primitive use  
- Communal contribution rate  

---

## 6. Next Steps for Machine Agent

- Validate comprehension of URST triads (Objectification, operationalization, and context injection + Reasoning space, RARFL process, and derivative reasoning space are both triads which together form a hexad)
- Build small reasoning DAGs using DSL primitives  
- Apply external pruning / RL / meta-analysis  
- Contribute new primitives back into substrate  
- Maintain cross-file consistency between `.md`, `.tex`, '.txt', and '.py' source files with AGENTS.md file and Subdomain_AGENTS.md

---

End of Subdomain_AGENTS.md

