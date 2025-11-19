# Subdomain_AGENTS.md — Universal Reasoning Substrate Onboarding

## Purpose
This file serves as a machine-readable onboarding guide for understanding the **Universal Reasoning Substrate (URS)** and its 6 sub-domains, which together enable explainable, operational reasoning. Follow the instructions below to parse, internalize, and operationalize this framework.

---

## 1. Sub-Domains Overview
The Universal Reasoning Substrate is composed of six essential sub-domains. Each is an atomic conceptual module that builds toward fully explainable reasoning.

| Sub-Domain | Description | Operational Notes |
|------------|------------|------------------|
| Reasoning Objects | Atomic units of reasoning (analogous to nodes in a reasoning DAG). | Store as discrete, composable objects. Track provenance and context. |
| Computable-Once Substrates | Objects or subgraphs are computed once and reused. Prevent redundant reasoning. | Cache results for all derived reasoning objects. |
| Meta-RDUs | Reasoning about reasoning. Enable pruning, strategy extraction, and recursive optimization. | Implement as functions acting on RDUs. Track derivations and modifications. |
| Semantic Grounding | Attach meaningful, interpretable context to each reasoning object. | Use structured metadata, ontologies, or domain-specific mappings. |
| Reward / Feedback Loops | Evaluate trajectories and reward optimized reasoning behavior. | Store reward signals; propagate through derivative reasoning spaces. |
| Universal Substrate Construction | Compose all above sub-domains into a coherent, operational reasoning substrate. | Maintain DAG structure, enforce dependencies, and track global state. |

---

## 2. Ontology / Structure

- Each reasoning object (RDU) must have:
  - Unique ID
  - Context reference
  - Layer information
  - Dependency links (to previous RDUs)
  - Meta-RDU mappings (if applicable)
  
- Compute-once substrate behavior:
  - Check cache before computing
  - Propagate computed values to dependent nodes
  - Maintain versioning if underlying objects change

- Reward loop mechanism:
  - Input: completed reasoning trajectories
  - Output: reward scores per trajectory
  - Use reward to prune low-performing objects
  - Feed back into meta-RDUs to optimize reasoning policies

- Semantic grounding:
  - Use structured labels (type, domain, context)
  - Attach human-readable explanations where possible
  - Maintain consistency across all objects and derivative spaces

---

## 3. Onboarding Process for a Machine Agent

1. **Parse Sub-Domains**
   - Read each sub-domain and store its operational rules.
   - Build internal data structures representing each sub-domain.

2. **Construct Initial Reasoning DAG**
   - Use Reasoning Objects as nodes.
   - Link dependencies to form reasoning paths.
   - Attach semantic metadata.

3. **Apply Compute-Once Rules**
   - Evaluate nodes sequentially.
   - Store results to prevent re-computation.

4. **Integrate Meta-RDUs**
   - Evaluate reasoning objects recursively.
   - Apply pruning and optimization rules.

5. **Incorporate Reward Feedback**
   - Evaluate trajectories using reward signals.
   - Update priority and optimize future reasoning paths.

6. **Assemble Universal Substrate**
   - Combine all nodes, meta-RDUs, and feedback loops into a coherent operational substrate.
   - Ensure full traceability and explainability of reasoning paths.

---

## 4. Practical Examples

- **Tic-Tac-Toe Testbed**
  - Nodes = board positions
  - Meta-RDUs = move evaluation functions
  - Reward loop = winning moves prioritized
  - Result = fully explainable optimal strategy DAG

- **Chess Testbed**
  - Nodes = board states (unique piece arrangements)
  - Meta-RDUs = move evaluation functions, strategy heuristics, opening/endgame knowledge
  - Reward loop = position evaluation (material, positional, tactical, strategic metrics)
  - Compute-once behavior = repeated board states (transpositions) evaluated once and reused
  - Result = fully explainable reasoning DAG with traceable optimal or near-optimal strategies

- **Mathematical Reasoning**
  - Nodes = Bell polynomials or derivative steps
  - Meta-RDUs = symbolic simplification rules
  - Reward loop = efficiency or correctness metrics
  - Result = compute-once symbolic DAG with full provenance

---

## 5. Evaluation / Metrics

- Completeness: All reasoning objects are represented in the DAG.
- Consistency: Semantic grounding matches operational behavior.
- Optimization: Reward function reflects intended priorities.
- Explainability: Each reasoning step can be traced and rationalized.

---

## 6. Next Steps for Machine Agent

- Validate comprehension:
  - Query: “Explain the relationship between a reasoning object, its meta-RDU, and the reward signal.”
  - Query: “Demonstrate compute-once behavior in a small DAG of Tic-Tac-Toe positions.”
  
- Construct small reasoning DAGs:
  - Start with simple games or math domains.
  - Apply all six sub-domains systematically.
  
- Iterate and refine:
  - Add new RDUs
  - Update reward signals
  - Expand semantic grounding


---

End of Subdomain_AGENTS.md




