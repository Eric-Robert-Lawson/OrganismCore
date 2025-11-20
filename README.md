# OrganismCore

🎬 **Start here:** [Automated Semantic Onboarding for AI Agents](https://youtu.be/pEGlSHxKASw)


A unified symbolic and computational framework for **objectified reasoning** — treating reasoning processes as composable, auditable, and operational structures. OrganismCore builds the foundations for a **universal reasoning substrate**, integrating symbolic computation, compositional logic, and recursive reasoning into a transparent, interpretable system.

This repository serves as the hub for research, prototypes, and documents advancing **Universal Reasoning Substrate Theory (URST)** — with the goal of making general reasoning and intelligence a shared public commons.

See the [Articles folder](/Articles/) for the conceptual documents that anchor the project.


---

## Using AGENTS.md for Machine-Assisted Onboarding

> **Recommended starting point for anyone new to OrganismCore.**

### Workflow with GitHub Copilot

1. Open the repository in an IDE or Codespace with Copilot enabled.  
2. Read `AGENTS.md` and 'Subdomain_AGENTS.md' to understand how agents should traverse LaTeX, Python prototypes, and conceptual documents.  
3. Explore how the AGENTS.md and Subdomain_AGENTS.md files reference project files and concepts; follow the structure shown in the tutorial to understand the automated onboarding process.


### Automated Onboarding Tutorial

[▶ Automated Semantic Onboarding for AI Agents](https://youtu.be/pEGlSHxKASw)

> For now we only have [AGENTS.md](AGENTS.md) in top layer and the [Subdomain_AGENTS.md](Subdomain_Articles/Subdomain_AGENTS.md) in the lower layer.

### Benefits

- **Collaborators and reviewers** can interrogate and onboard to the repo interactively.  
- Provides structured context to LLMs, improving reproducibility.  
- Enables agents to reason across the full research program.
  
---

## Prototype Overview Video

> **Start here for a high-level conceptual grounding before diving into code.**

[▶ OrganismCore Prototype Walkthrough](https://youtu.be/S5XGJ9JgHsU)

**This video covers:**

- The **Reasoning DNA Unit (RDU)** framework  
- Operationalization via Python DAG prototypes  
- Combinatorial layering and POT generator functions  
- Bell polynomial operations  
- How these components support a future DSL for objectified reasoning  

This serves as a conceptual anchor for both the Articles folder and the code prototypes.


---

## Prototype: DAG-Based Reasoning DNA Unit

The repository includes a Python prototype implementing a Directed Acyclic Graph (DAG) system for:

- Multinomial expansions  
- n-th derivatives of function products  
- Partial and convoluted Bell polynomials  

The DAG structure enables **auditable, composable symbolic reasoning**, demonstrating how reasoning operations can be objectified and operationalized even without a dedicated DSL.

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
