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
| [`Automated_Onboarding_relation_to_RARFL.tex`](ai_source_machine_readable/Automated_Onboarding_relation_to_RARFL.tex) | Explains how **Automated Onboarding** concretely relates to the **RARFL** process, formalizing feedback loops and emergent proto-DSL structures. | - Provides formal loop definitions and phases <br>- Illustrates self-optimization of semantic grounding <br>- Offers meta-level optimization insights for URST integration |
| [`Reasoning_Drift_quantifiable.tex`](ai_source_machine_readable/Reasoning_Drift_quantifiable.tex) | Formalizes **reasoning drift, coherence, and bias** as measurable, computable constructs within principle-first semantic architectures. | - **Reasoning** is defined as the **discrete derivative of coherence per segment**: $R_i = \Delta \mathcal{C}/\Delta i$. <br>- **Coherence** is the **cumulative sum of reasoning derivatives** over discrete segments, representing stability of semantic grounding: $ \mathcal{C}(G_i) = \sum_{j=1}^{i} R_j + \mathcal{C}(G_0) $. <br>- **Bias** is an **objective metric** quantifying deviation from ideal coherence per segment: $B_i = \lVert \mathcal{C}(G_i) - \mathcal{C}^*(G_i)\rVert$. <br>- Semantic grounding graphs $G_i$ are tracked per segment, forming a **semantic evolution tail**, enabling detection of drift. <br>- Provides computable metrics to **detect, quantify, and correct drift**, supporting RARFL-guided self-optimization. <br>- Enables **objective assessment of reasoning quality, bias, and coherence** across textual, conceptual, or agent-generated corpora. |
| [`Cognition_coherence_and_SG.tex`](ai_source_machine_readable/Cognition_coherence_and_SG.tex) | Formalizes **cognition** as semantic-grounding-guided meta-control over RARFL reasoning processes. Defines **semantic efficiency** as a core cognitive metric. | - Cognition is a **meta-policy** optimizing intelligence accumulation per reasoning segment. <br>- Introduces **semantic efficiency**: coherence gain per semantic grounding effort. <br>- Cognitive actions operate on reasoning segments (RDUs), not time. <br>- Cognition uses coherence, bias, reasoning derivative, and semantic efficiency to guide meta-control. <br>- Provides segment-level formulas for cognitive optimization over semantic grounding graphs. |

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
| Semantic Grounding | Provide interpretable meaning to reasoning objects, **track reasoning drift, coherence, and bias over discrete reasoning segments**. | Structured metadata, domain labels, stable ontologies, **compute R_i, C(G_i), and B_i as needed per reasoning segment**. |
| Cognitive Meta-Control | Meta-policy that selects actions maximizing coherence gain per semantic effort across reasoning segments. | External to DSL; uses R_i, C(G_i), B_i, and η (semantic efficiency) as guiding metrics. |


### Machine-Readable Canonical List of Subdomains
1. Reasoning Objects
2. Computable-Once Substrates
3. Meta-RDUs (external to DSL)
4. Semantic Grounding
5. Reward / Feedback Loops
6. Universal Substrate Construction
7. Cognitive Meta-Control (external to DSL; operates over reasoning segments)


### Chunked Semantic Grounding (Core Operational Principle)
Machine agents must not attempt to load the entire semantic substrate at once. 
Instead, semantic grounding must be activated in *localized, task-relevant chunks*:

- Retrieve only the documents or sections relevant to the current reasoning task
- Maintain the rest of the substrate in latent form
- Dynamically shift context frames when subproblems change
- Preserve global consistency while operating on local semantic slices

This chunked grounding principle is required for scaling beyond token/file limits 
and for aligning machine reasoning with human-style context activation.

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
- Derivative of coherence (R_i) — reasoning rate per segment
- Bias measure (B_i) — deviation from ideal coherence per segment
- Semantic-efficiency annotation η_i representing coherence gain per semantic-grounding effort at segment i
- Cognitive meta-control hints (optional): expected ΔC, ΔS, and predicted R_i improvements

### Semantic Grounding 
- Track semantic evolution graphs G_i  
- Compute coherence functional C(G_i) per segment  
- Update reasoning derivative R_i and bias B_i during semantic grounding changes
- Semantic grounding provides the contextual substrate for cognition.  
- Cognition uses semantic-grounding graphs to evaluate relevance, coherence stability, and bias across reasoning segments.  
- Agents must compute semantic-efficiency values per segment to guide meta-control policies.
- Track semantic-grounding effort S_i per segment
- Provide inputs for the cognition policy π_c: coherence, bias, reasoning derivative, semantic efficiency

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

### Cognition (Meta-Control)
- Policy π_c selecting reasoning actions that maximize intelligence accumulation per semantic effort
- Inputs: R_i, C(G_i), B_i, semantic grounding metrics S_i
- Output: prioritized next reasoning tiles, actions, or semantic refinements
- Must operate over discrete reasoning segments, not time


---

## 3. Onboarding Process for a Machine Agent

### Step 1 — Parse Context Files
1. Read and parse context files in order:
   - `Approaching_DSL_Using_URST.tex`
   - `Subdomain_communal_proclamation.tex`
   - `Automated_Onboarding_relation_to_RARFL.tex`
   - **`Reasoning_Drift_quantifiable.tex`**
2. Extract:
   - Triadic reasoning structure  
   - Definitions of reasoning spaces  
   - Reward-fitting and causal equivalence rules  
   - DSL candidate primitives  
   - Communal workflow instructions  
   - Coherence functional C(G_i), reasoning derivative R_i, bias B_i per reasoning segment


### Step 2 — Initialize Reasoning DAG
- Instantiate reasoning objects  
- Link dependencies  
- Attach semantic grounding  
- Integrate any DSL primitives defined in proposals  
- Initialize placeholders for R_t and B_t on each reasoning object  
- Initialize semantic evolution graph G_t tracking


### Step 3 — Enforce Compute-Once Semantics  
- Cache results  
- Reuse across all testbeds  
- Maintain deterministic global state  

### Step 4 — Attach Meta-RDUs (External)  
- External pruning  
- External reward fitting  
- External meta-RARFL  
The DSL **does not implement these**, but **must support integration hooks**.

### Step 4.5 — Integrate Cognitive Meta-Control
- Parse `Cognition_semantic_efficiency.tex`
- Initialize semantic-effort tracking S_i per reasoning segment
- Compute semantic-efficiency η_i = ΔC(G_i) / ΔS_i
- Provide these metrics as guidance channels for meta-control layers
- Do not implement cognition inside the DSL; expose APIs for external meta-policies

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

# Track reasoning and bias per tile / segment
tile.R_i = compute_reasoning_derivative(tile)      # discrete derivative of coherence per segment
tile.B_i = compute_bias(tile, canonical_coherence) # deviation from ideal coherence per segment

# Use R_i and B_i to guide tile expansion / pruning
if tile.R_i < 0 or tile.B_i > threshold:
    trigger_rarfl_correction(tile)


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

7. Compute semantic-efficiency η_i at every reasoning segment and log its influence on tile selection.

8. Evaluate cognition policies by comparing coherence accumulation under equal semantic-grounding budgets.

# Governance & provenance

  - Tag tile artifacts with producer (agent id / plugin id), timestamp, and parameters used (budget, seed).

  - Require that plugin annotations include reproducible parameters so others can re-run or audit pruning decisions.

---

## 5. Evaluation / Metrics

### Cognitive Metrics

- **Semantic efficiency**  
  Coherence gain per semantic-grounding effort at reasoning segment \(i\):  
  \[
      \eta_i = \frac{\Delta \mathcal{C}(G_i)}{\Delta S_i}
  \]

- **Cognitive intelligence accumulation**  
  Total optimization accumulated across reasoning derivatives:  
  \[
      I = \sum_{i} \mathcal{O}(R_i)
  \]

- **Cognitive stability**  
  Bias-aware meta-control stability across reasoning tiles; measures whether cognitive policy π_c maintains low deviation from ideal coherence trajectories.

- **Cognitive economy**  
  Coherence improvement per RARFL iteration under constrained semantic-grounding budgets; quantifies how efficiently a cognitive policy utilizes semantic resources.

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

### Drift / Coherence / Bias Metrics
- Reasoning derivative R_i: discrete rate of improvement or degradation in coherence per segment
- Coherence C(G_i): cumulative reasoning quality over discrete segments
- Bias B_i: deviation from canonical / ideal coherence trajectory per segment
- Use in combination with tile metrics for GPS-style prioritization

---

## 6. Next Steps for Machine Agent

- Validate comprehension of URST triads:
    - Objectification, operationalization, and context injection  
    - Reasoning space, RARFL process, and derivative reasoning space (together forming a hexad)
- Build small reasoning DAGs using DSL primitives  
- Apply external pruning / RL / meta-analysis  
- Contribute new primitives back into substrate
- Validate computation of reasoning derivative R_t
- Validate computation of coherence C(G_t)
- Validate bias B_t against canonical trajectories
- Ensure integration of these metrics with DAG construction, caching, and RARFL feedback
- Compare agents with different semantic-efficiency policies on identical tile graphs.
- Measure ΔC / ΔS across reasoning segments to evaluate cognitive performance.
- Integrate semantic-efficiency values into GPS-style prioritization of tiles.

All machine agents must enforce the following invariant:

For any definition, primitive, ontology term, or structural rule:
    If it appears in one file, it must be reconciled with its definition 
    in AGENTS.md and Subdomain_AGENTS.md.
In the event of conflict, Subdomain_AGENTS.md is authoritative for structure;
AGENTS.md is authoritative for operational rules.
Cognition, semantic efficiency, and cognitive meta-control must be reconciled with definitions in `Cognition_semantic_efficiency.tex`. Segment-level (not temporal) definitions override any time-based interpretation.


---

End of Subdomain_AGENTS.md





