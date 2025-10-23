# OrganismCore

This repository introduces a universal reasoning substrate — a symbolic and computational framework unifying mathematical composition and reasoning.

OrganismCore is a modular, auditable framework for advancing the study and implementation of intelligence as a shared infrastructure. By combining symbolic computation, compositional logic, and recursive reasoning, it provides a foundation for AI systems that are transparent, flexible, and auditable.

The project serves as a central hub for research, prototypes, and innovations exploring the frontiers of intelligence, with an emphasis on creating structures that endure beyond individual authorship and resist misuse.

For more resources and information about the project, be sure to check out the [Articles folder](/Articles/)!

---

## Machine-Readable Source

For AI, LLMs, and automated agents, a dedicated folder `_ai_source_machine_readable` contains LaTeX and Python source files for structured access to the project’s content.

- [Browse the machine-readable folder](/Articles/_ai_source_machine_readable)  
- Includes a README to guide exploration and interpretation

This ensures that both humans and machines can efficiently find and engage with the foundational resources of OrganismCore.

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

## License

See [LICENSE](LICENSE) for details. 

---

## Contribution

Contributions and feedback are welcome. Please open an issue or contact directly for collaboration.
