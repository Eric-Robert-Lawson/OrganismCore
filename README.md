# OrganismCore

🎬 **Start here:** [Automated Semantic Onboarding for AI Agents](https://youtu.be/pEGlSHxKASw)

A unified symbolic and computational framework for **objectified reasoning** that makes reasoning processes composable, auditable, reproducible, and directly executable.

OrganismCore introduces a **universal reasoning substrate** where models, agents, and humans can all interact with the same structured reasoning objects. These objects are produced through an *automated onboarding process* that works across different AI models, enabling:

- Comparable reasoning behavior  
- Fully traceable reasoning steps  
- Cross-model reproducibility  
- Interactive, agent-driven onboarding for researchers and developers  

In addition, OrganismCore provides a foundation for a **domain-specific language (DSL)** designed to operationalize the universal reasoning substrate. This DSL enables reasoning workflows, reproducible experiments, and automated construction of reasoning objects to be formally specified and executed.

This repository anchors the open research program advancing **Universal Reasoning Substrate Theory (URST)** and provides the infrastructure for reasoning-as-an-artifact.

See the [Articles folder](/Articles/) for the conceptual and formal documents supporting the project.

---

## Automated Onboarding (AGENTS.md)

> **This is the core demo of OrganismCore. Start here if you want to understand the new paradigm.**

OrganismCore includes a reproducible **automated onboarding process** that lets any AI model (or human using an LLM) traverse and internalize the structure of the entire research program.  
This process is defined in two files:

- **AGENTS.md** — top-level semantic onboarding  
- **Subdomain_AGENTS.md** — subdomain-level recursive onboarding  

### Workflow (with GitHub Copilot or any LLM)

1. Open the repo in an IDE or Codespace with an LLM assistant enabled.  
2. Open `AGENTS.md` and follow the semantic instructions.  
3. The assistant will recursively navigate LaTeX, Python prototypes, and conceptual documents.  
4. The result is a **consistent reasoning object** produced directly from the onboarding pass.

This provides a *structured and repeatable* way to onboard humans, AI models, and agents to the same reasoning substrate.  

The onboarding process also acts as a **demonstration of how the proposed DSL can be used** to specify, execute, and compare reasoning objects across models, making it the living proof of the reasoning substrate in action.
  
---
## Reproducible Reasoning Objects

OrganismCore enables generation of **reproducible, transparent reasoning objects** through the automated onboarding procedure.  
These reasoning objects are produced *consistently across multiple AI models* using the same AGENTS.md workflow. The process is designed to be compatible with the emerging **domain-specific language**, providing a medium to formalize and operationalize reasoning workflows.

Below are three independently generated reasoning objects (tic-tac-toe domain) produced by three different models after running the same onboarding process. These objects serve as an example of **cross-model, DSL-compatible reasoning artifacts**.

- 🔹 **Grok Code Fast 1 Model**: [View Reasoning Object](https://github.com/copilot/share/82541130-42a0-8cd0-b100-5e07e01360ae)
- 🔹 **Chat GPT-5 mini**: [View Reasoning Object](https://github.com/copilot/share/8a3c51a0-43a4-8cd0-8102-dc0ec4d949bc)
- 🔹 **Anthropic (Claude Sonnet 3.5)**: [View Reasoning Object](https://github.com/copilot/share/ca5d01b2-0b84-8876-9901-5c0ec41148ad)

These reasoning objects are **model-agnostic, fully reproducible, and auditable** by any researcher or developer.

---

## Why This Matters

This is a working prototype of:

- **Model-agnostic explainable reasoning**  
- **Cross-model reproducibility of reasoning behavior**  
- **Auditable chain-of-thought without leaking proprietary internals**  
- **A standardized reasoning substrate for multi-agent systems**  
- **A domain-specific language to formalize reasoning workflows**  

The onboarding process *is itself* the demo — a self-referential proof that reasoning can be objectified, serialized, executed, and compared across architectures.

---

## What the Demo Actually Demonstrates

The current demo is **not a prototype of the symbolic engine itself**.  
It demonstrates:

- The **automated onboarding process**
- Generation of **consistent reasoning objects**
- **Explainable AI behavior** across different models
- **Operationalization potential for a DSL** formalizing reasoning workflows
- A self-referential reasoning artifact that explains OrganismCore from inside the system

The onboarding procedure is both a tool and a proof-of-concept for the entire paradigm and the universal reasoning substrate.

---

## Explore OrganismCore

For hands-on experimentation and onboarding, follow these steps to engage with OrganismCore.
- Start with [AGENTS.md](AGENTS.md) and [Subdomain_AGENTS.md](Subdomain_Articles/Subdomain_AGENTS.md)  
- Watch the [Automated Semantic Onboarding tutorial](https://youtu.be/pEGlSHxKASw)  
- Interactively explore and experiment with **DSL-based reasoning workflows** via the automated onboarding process
- Audit and interact with **existing reasoning objects** to understand model-agnostic reasoning workflows  
- Join the [community](COMMUNITY.md) to collaborate on expanding reasoning spaces

---

## Academic Reference: Understanding Demo

For a formal, citable presentation of the **Automated Semantic Onboarding** methodology and cross-model reasoning demonstration, see the **Understanding Demo** PDF:

- [Understanding_demo.pdf](Understanding_demo.pdf)

This document provides:

- A reproducible, cross-model demonstration of reasoning objects
- Detailed methods and results for Tic Tac Toe reasoning objects across Grok Code Fast 1, Chat GPT-5 mini, and Claude Sonnet 3.5
- Insights on explainability, operationalization with a DSL, and cross-model reproducibility
- Discussion of broader implications for universal reasoning substrates

> **Note:** This PDF is intended as an academic contribution and formal reference. It is separate from the operational onboarding workflow in the repository. Researchers and contributors can reference it for background, methodology, and results while interacting with the practical onboarding materials (`AGENTS.md`, `Subdomain_AGENTS.md`) and reasoning objects in the repo.

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
