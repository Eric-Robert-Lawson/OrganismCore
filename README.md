# OrganismCore

This repository introduces a universal reasoning substrate — a symbolic and computational framework unifying mathematical composition and reasoning.

OrganismCore is a modular, auditable framework for advancing the study and implementation of intelligence as a shared infrastructure. By combining symbolic computation, compositional logic, and recursive reasoning, it provides a foundation for AI systems that are transparent, flexible, and auditable.

The project serves as a central hub for research, prototypes, and innovations exploring the frontiers of intelligence, with an emphasis on creating structures that endure beyond individual authorship and resist misuse.

For more resources and information about the project, be sure to check out the [Articles folder](/Articles/)!

---

## Project Overview Video

> **Start here if you want a conceptual overview before diving into code.**

To help understand the OrganismCore prototypes, reasoning substrate, and conceptual framework, check out this walkthrough video:

[![OrganismCore Prototype Walkthrough](https://img.youtube.com/vi/S5XGJ9JgHsU/0.jpg)](https://youtu.be/S5XGJ9JgHsU)

**About this video:**

- Explains the **Reasoning DNA Unit (RDU) framework** and its operationalization.
- Demonstrates the **Python DAG prototypes**, combinatorial layering, POT generator functions, and Bell polynomial operations.
- Connects the **theoretical concepts** in the Articles folder to practical, auditable code.
- Provides context for understanding how a **DSL for objectified reasoning** could be constructed.
- Meant to be a resource that anchors documents, something that can be returned to as you read the documents.
- Serves as a guided entry point for recruiters, collaborators, and AI/LLM agents exploring the project.

Click the image above to watch the full video on YouTube.

---

## Machine-Readable Source

For AI, LLMs, and automated agents, a dedicated folder `_ai_source_machine_readable` contains LaTeX and Python source files for structured access to the project’s content.

- [Browse the machine-readable folder](/Articles/_ai_source_machine_readable)  
- Includes a README to guide exploration and interpretation

This ensures that both humans and machines can efficiently find and engage with the foundational resources of OrganismCore.

---
## Using AGENTS.md with GitHub Copilot

OrganismCore includes an **AGENTS.md** file located in the top level of the project. This file is designed to **guide AI, LLMs, and automated agents** in interpreting the project’s conceptual and prototype content.

### How it works with GitHub Copilot

1. **Open the repository** in an IDE or GitHub Codespace with Copilot enabled.  
2. **Explore `AGENTS.md`** to understand the structured workflow for parsing LaTeX and Python source files.  
3. **Use Copilot Chat or inline suggestions** to query and analyze:  
   - Conceptual definitions (Reasoning DNA Units, combinatorial layering, POT generators, path traversal)  
   - Python prototypes (DAG symbolic reasoning engine, Bell polynomials, n-th derivatives)  
   - Connections between manifesto principles, conceptual documents, and executable code
4. **Ensure you include references to the /Articles/_ai_source_machine_readable folder** to ensure the folder content's context is understood with AGENTS.md

### Benefits

- **Recruiters, collaborators, and reviewers** can interactively explore the repository with AI assistance.  
- AGENTS.md makes the **project machine-accessible**, improving discoverability, reproducibility, and structured comprehension.  
- Copilot references files **directly in the repo**, providing a guided, context-aware experience of your symbolic reasoning framework.  

> Note: This workflow currently works best with GitHub Copilot or Copilot Chat. Without Copilot, AGENTS.md serves as a structured human-readable guide.

---
## Prototype: DAG Symbolic Reasoning Engine

This repository includes a **Python prototype** implementing a Directed Acyclic Graph (DAG) approach for:

- **Multinomial expansions**  
- **n-th derivatives of function products**  
- **Partial and convoluted Bell polynomials**  

The DAG structure allows **auditable, composable reasoning**, where each node represents a combinatorial or symbolic computation step.

---

## Getting Started

### Prerequisites

- Python 3.10+  
- [SymEngine](https://github.com/symengine/symengine.py)

Install dependencies via pip:

```bash
pip install symengine
```

### Setup

1. Save the prototype file as `DAG.py` in your working directory.  
2. Open Python from the command line:

```bash
$ python
```

3. Import the prototype:

```python
>>> import DAG
```

---

### Examples

**Multinomial expansion:**  

```python
>>> k4 = DAG.multinomial_DAG(3, 2, 0, DAG.unordered_combinations)
>>> k4[0]
3*f0(x)*f1(x)**2 + 3*f0(x)**2*f1(x) + f0(x)**3 + f1(x)**3
```

**n-th derivative of function products:**  

```python
>>> k4 = DAG.multinomial_DAG(3, 2, 1, DAG.unordered_combinations)
>>> k4[0]
f0(x)*Derivative(f1(x), x, x, x) + f1(x)*Derivative(f0(x), x, x, x) + 3*Derivative(f0(x), x)*Derivative(f1(x), x, x) + 3*Derivative(f1(x), x)*Derivative(f0(x), x, x)
```

**Partial Bell polynomial example:**  

```python
>>> k4 = DAG.predefined_bell_polynomial_DAG(0, 3, 2)
>>> k4[0]
3.0*Derivative(f0(x), x)*Derivative(f0(x), x, x)
```

**Convoluted partial Bell polynomial example:**  

```python
>>> k4 = DAG.convoluted_partial_bell_polynomial(3, 2, 2)
>>> k4[0]
3.0*Derivative(f0(x), x)*Derivative(f0(x), x, x) + 3.0*Derivative(f0(x), x)*Derivative(f1(x), x, x) + 3.0*Derivative(f1(x), x)*Derivative(f0(x), x, x) + 3.0*Derivative(f1(x), x)*Derivative(f1(x), x, x)
```

---

## Demo Walkthrough

To make experimentation even easier, a fully runnable Jupyter Notebook `demo.ipynb` is included in this repository.

### Contents of `demo.ipynb`:

1. **Multinomial expansion**  
2. **n-th derivative of function products**  
3. **Partial Bell polynomial**  
4. **Convoluted partial Bell polynomial**

Each example replicates the Python code above, but in an interactive format where you can:

- Modify function orders or numbers of functions.
- Experiment with different DAG compositions.
- Trace symbolic outputs and see how the combinatorial reasoning unfolds.

### Running the Demo:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/OrganismCore.git
cd OrganismCore
cd OrganismDemo
```

2. Ensure dependencies are installed:

```bash
pip install -r requirements.txt
```

3. Launch the notebook:
```bash
jupyter notebook demo.ipynb

```
This interactive demo provides a guided experience of the DAG symbolic reasoning engine and demonstrates the key combinatorial and symbolic reasoning patterns in action.

---

## Community & Participation

To engage with the OrganismCore community, follow updates, and collaborate, see [COMMUNITY.md](COMMUNITY.md).

The community welcomes discussion, feedback, and collaboration.

---

## Support & Donations

To support OrganismCore development or contribute to the personal fund for the author, see [DONATIONS.md](DONATIONS.md).

- **Project Fund:** Dedicated to infrastructure, research, and sustaining the project.  
- **Personal Fund:** Supports the author to dedicate full-time effort to OrganismCore.


---

## Notes

- This is an **early prototype**. APIs and outputs may change.  
- Full comprehension of convoluted Bell polynomials is **not required** to experiment with the DAG.  
- Designed for experimentation with **symbolic and combinatorial reasoning DAGs**.  

---

## License and project intent

License: GNU Affero General Public License v3 (AGPLv3) — SPDX: AGPL-3.0-only. See [LICENSE](LICENSE) for the full text.

We use AGPLv3 to ensure improvements and hosted derivatives remain available to the community. OrganismCore is intended to be a shared research substrate, and the AGPL helps prevent proprietary or centralized service forks that would hide improvements from the commons.

Commercial licensing (optional)
- AGPLv3 permits commercial use provided the license obligations are satisfied (including source disclosure for networked services).
- If your organization cannot comply with AGPLv3 for operational or legal reasons (for example, closed SaaS, embedded proprietary products, or restrictive procurement rules), a negotiated commercial license is available. See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for the request process and typical timelines.

Contributor / relicensing note
- The public repository remains AGPLv3 for all users. If third‑party contributors have added code, relicensing those contributions may require their consent. To keep future governance and licensing options clear, please see [CONTRIBUTING.md](CONTRIBUTING.md) for contributor sign‑off guidance (DCO/CLA).

Citation
- If you use OrganismCore in research, please cite the repository or the project DOI/CITATION.cff (see [CITATION.cff](CITATION.cff) or the Zenodo badge in the repo).

See [LICENSE](LICENSE) for details.
---

## Contribution

Contributions and feedback are welcome. Please open an issue or contact directly for collaboration.
