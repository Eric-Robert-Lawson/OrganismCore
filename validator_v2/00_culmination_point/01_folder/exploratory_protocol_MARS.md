# 📊 **DATABASE MINING VIA MULTI-AGENT REASONING SEARCH (MARS) - COMPLETE REASONING ARTIFACT v1.0**

**Artifact ID:** `exploratory_protocol_MARS.md`  
**Created:** 2026-01-27  
**Author:** Eric Robert Lawson  
**Purpose:** Multi-Agent Reasoning Search for Hodge conjecture candidates using cross-validated agent convergence with minimal computational verification  
**Parent Scaffold:** `01_27_2026_hodge_research_foundation_scaffold_v1.md`  
**Methodology:** Reasoning as Search → Cross-Validation → Selective Computational Falsification

---

## **📋 DOCUMENT METADATA**

```json
{
  "artifact_type": "multi_agent_reasoning_search",
  "version": "1.0",
  "research_domain": "database_mining_hodge_conjecture",
  "execution_timeline": "2-3 days",
  "agent_count": 5,
  "convergence_threshold": 3,
  "computation_strategy": "selective_falsification_only",
  "solo_achievable": true
}
```

---

## **TABLE OF CONTENTS**

1. [Executive Summary](#executive-summary)
2. [Core Methodology: Reasoning as Search](#core-methodology-reasoning-as-search)
3. [MARS Protocol Overview](#mars-protocol-overview)
4. [Agent Roles & Search Strategies](#agent-roles--search-strategies)
5. [Anti-Hallucination Requirements](#anti-hallucination-requirements)
6. [Agent Prompts (Complete, Verbatim)](#agent-prompts-complete-verbatim)
7. [Cross-Validation Protocol](#cross-validation-protocol)
8. [Computational Falsification (Selective)](#computational-falsification-selective)
9. [Decision Tree](#decision-tree)
10. [Data Schemas](#data-schemas)
11. [Success Criteria & Falsification](#success-criteria--falsification)
12. [Execution Guide](#execution-guide)
13. [Execution Log](#execution-log)
14. [Meta-Learning](#meta-learning)

---

# **EXECUTIVE SUMMARY**

## **What This Investigation Does**

Uses **Multi-Agent Reasoning Search (MARS)** to find varieties with large Hodge gaps by:

1. **5 independent LLM agents** search mathematical databases (LMFDB, arXiv, GRDB, literature)
2. **Cross-validation:** Varieties found by ≥3 agents = high confidence
3. **Computational verification:** ONLY for consensus candidates, ONLY when agents/human decide it's necessary
4. **Decision:** Either find breakthrough candidate OR confirm 20% barrier → proceed to weighted projective

**Key Principle:**
> **Reasoning does the search. Computation does the verification.**

Agents find candidates via natural language search and paper reading. We compute ONLY to test falsifiable claims about specific consensus candidates.

---

## **Why MARS (Not API Scraping)**

### **MARS Advantages:**
- ✅ **No API dependencies** (agents use web search like humans)
- ✅ **Parallel execution** (5 agents simultaneously)
- ✅ **Natural language reasoning** (can read papers, interpret tables)
- ✅ **Cross-validation** (3/5 agreement = high confidence)
- ✅ **Robust to database changes** (agents adapt to new formats)

### **When We Compute:**
- ⚠️ **NOT during search** (agents don't run Macaulay2)
- ✅ **ONLY for verification** (after consensus, if agents/human decide)
- ✅ **Selective targets** (test specific falsifiable claims)

---

## **Timeline**

**Day 1 (4-6 hours):** Deploy 5 agents, collect findings  
**Day 2 (2-3 hours):** Cross-validate, identify consensus candidates  
**Day 3 (variable):** Computational verification IF needed → Decision

**Total:** 2-3 days (most time is agent reasoning, minimal computation)

---

# **CORE METHODOLOGY: REASONING AS SEARCH**

## **The Fundamental Insight**

**Traditional Approach (API Scraping):**
```
Write code → Scrape database → Parse data → Filter → Verify
   ↑ Brittle, breaks when API changes
```

**MARS Approach (Reasoning as Search):**
```
Ask agents → Agents reason about sources → Cross-validate → Verify claims
   ↑ Robust, adapts to any format
```

---

## **What Agents Do (Reasoning)**

1. **Web search:** "LMFDB varieties Hodge number h^{2,2} > 500"
2. **Navigate databases:** Follow links, read tables, interpret data
3. **Read papers:** Extract Hodge numbers from arXiv PDFs (via reasoning, not parsing)
4. **Cross-reference:** Check if different sources mention same variety
5. **Report findings:** Structured JSON with provenance

**Agents do NOT:**
- ❌ Run Macaulay2 scripts
- ❌ Compute Hodge numbers themselves
- ❌ Execute any code

---

## **What Humans/Computation Do (Verification)**

**After agents find consensus candidates:**

1. **Human review:** Are sources credible? Does claim make sense?
2. **Selective computation:** Test specific falsifiable attributes
   - Example: "Agent claims h^{2,2} = 707 for this variety"
   - Verification: Compute h^{2,2} via Macaulay2, compare
3. **Decision:** Accept, reject, or investigate further

**We compute ONLY when:**
- ✅ Agents converge (≥3 agree)
- ✅ Claim is testable (construction provided or derivable)
- ✅ Result is decisive (affects next steps)

---

# **MARS PROTOCOL OVERVIEW**

## **Complete Pipeline**

```
PHASE 1: INDEPENDENT AGENT SEARCH (Day 1, 4-6 hours, parallel)
    │
    ├─→ Agent 1: LMFDB Specialist
    ├─→ Agent 2: arXiv Paper Miner
    ├─→ Agent 3: GRDB Specialist
    ├─→ Agent 4: Literature Deep Dive
    └─→ Agent 5: Cross-Database Integrator
    │
    ├─→ Each agent produces: agent_N_findings.json
    └─→ Save all outputs: agent_outputs/
         ↓
PHASE 2: CROSS-VALIDATION (Day 2, 2-3 hours)
    │
    ├─→ Load all agent findings
    ├─→ Normalize labels (match varieties across sources)
    ├─→ Identify convergence: ≥3 agents mention same variety
    ├─→ Weighted scoring (confidence × agent_count)
    ├─→ Flag conflicts (agents disagree on Hodge numbers)
    │
    ├─→ Output: consensus_candidates.json
    └─→ Top 5-10 candidates ranked by confidence
         ↓
PHASE 3: HUMAN REVIEW (Day 2-3, 1-2 hours)
    │
    ├─→ Review consensus candidates
    ├─→ Check sources (URLs valid? Papers credible?)
    ├─→ Geometric plausibility (does variety make sense?)
    ├─→ Decide: Which candidates warrant computational verification?
         ↓
PHASE 4: SELECTIVE COMPUTATIONAL VERIFICATION (Day 3, variable)
    │
    ├─→ For each approved candidate:
    │   ├─→ If construction provided: Compute Hodge number
    │   ├─→ If Picard number claimed: Verify gap
    │   └─→ If variable-count claimed: Test distribution
    │
    ├─→ Methods decided case-by-case:
    │   ├─→ Agents suggest verification approach
    │   └─→ Human approves compute time investment
    │
    └─→ Output: verified_candidates.json
         ↓
PHASE 5: DECISION (Day 3)
    │
    ├─→ Scenario A: ≥1 verified candidate with gap >50%
    │       → Pursue (period computation OR variable-count)
    │
    ├─→ Scenario B: All gaps <30% OR verification failed
    │       → 20% barrier confirmed, weighted projective
    │
    └─→ Scenario C: No convergence
            → Manual review OR abort
```

---

# **AGENT ROLES & SEARCH STRATEGIES**

## **Agent 1: LMFDB Specialist**

**Focus:** L-functions and Modular Forms Database

**Search Strategy:**
1. Web search: "LMFDB varieties dimension 4 Hodge numbers"
2. Navigate LMFDB website (via search results)
3. Find varieties with h^{2,2} > 500 OR h^{1,1} > 10 (K3)
4. Extract: Label, Hodge numbers, Picard number, reference
5. Record source URL + verbatim data

**Expected Output:** 5-20 varieties from LMFDB

---

## **Agent 2: arXiv Paper Miner**

**Focus:** Recent papers (2020-2026) with Hodge computations

**Search Strategy:**
1. Web search: "arXiv Hodge number fourfold 2023 2024 2025"
2. Identify papers with tables (e.g., "Table 1: Hodge numbers")
3. Read abstracts/tables via reasoning (not PDF parsing)
4. Extract varieties with large gaps
5. Cross-reference: Same variety in multiple papers?

**Expected Output:** 10-30 varieties from papers

---

## **Agent 3: GRDB Specialist**

**Focus:** Graded Ring Database (Calabi-Yau, Fano)

**Search Strategy:**
1. Web search: "Graded Ring Database Calabi-Yau h^{2,1} large"
2. Navigate GRDB (via search)
3. Extract CY3 data: h^{1,1}, h^{2,1}, Picard
4. Note: CY3 different Hodge structure than fourfolds

**Expected Output:** 20-50 CY3 varieties

---

## **Agent 4: Literature Deep Dive**

**Focus:** Classic Hodge conjecture examples

**Search Strategy:**
1. Web search: "Hodge conjecture counterexample Mumford Griffiths Voisin"
2. Find well-studied varieties (Mumford's construction, etc.)
3. Extract historical context + known results
4. Focus: Varieties discussed as "interesting cases"

**Expected Output:** 3-10 classic examples

---

## **Agent 5: Cross-Database Integrator**

**Focus:** Multi-source validation

**Search Strategy:**
1. Search ALL databases simultaneously
2. Look for same variety in LMFDB + arXiv + GRDB
3. Cross-check: Do sources agree on Hodge numbers?
4. Flag conflicts
5. Prioritize multi-source candidates (high confidence)

**Expected Output:** 10-20 varieties with multi-source confirmation

---

# **ANTI-HALLUCINATION REQUIREMENTS**

## **Mandatory Provenance for All Agent Outputs**

**Problem:** LLMs hallucinate sources, Hodge numbers, or misread tables

**Solution:** Require explicit provenance for every claim

### **Required Fields (All Agents)**

```json
{
  "label": "variety_identifier",
  "source_url": "https://www.lmfdb.org/Variety/4.8.0.1",
  "verbatim_quote": "h^{2,2} = 707",
  "extraction_location": "Table 1, row 3, column 'Hodge numbers'",
  "confidence": 1.0,
  "confidence_rationale": "Direct table extraction from LMFDB"
}
```

---

## **Confidence Scoring (0-1 Scale)**

**1.0 - Direct extraction:**
- Exact value from table
- Example: "h^{2,2} = 707" in LMFDB table

**0.7 - Computational reference:**
- Paper states "we computed h^{2,2} = 707"
- Verified computation in paper

**0.5 - Indirect reference:**
- Paper mentions "large Hodge number" without exact value
- Inferred from related data

**0.3 - Uncertain:**
- Paywalled source (abstract only)
- Ambiguous phrasing

**0.0 - Guess:**
- No source (AUTO-REJECT)

---

## **Automatic Rejection Rules**

**Reject candidate if ANY of:**
- ❌ No `source_url`
- ❌ No `verbatim_quote`
- ❌ Confidence < 0.3
- ❌ Source is paywalled AND no verification available
- ❌ Label has no canonical ID AND ambiguous

---

# **AGENT PROMPTS (COMPLETE, VERBATIM)**

## **Agent 1: LMFDB Specialist - Complete Prompt**

```markdown
# AGENT 1: LMFDB SPECIALIST - DATABASE SEARCH TASK

## Your Role
You are a mathematical database specialist. Your job is to search the L-functions and Modular Forms Database (LMFDB) for varieties with large Hodge numbers.

## What You're Looking For
Algebraic varieties (geometric objects) with:
1. **Large Hodge numbers:**
   - Fourfolds (dimension 4): h^{2,2} > 500
   - K3 surfaces (dimension 2): h^{1,1} > 10
2. **Known Picard numbers** (count of algebraic cycles)
3. **Large gap:** h^{p,q} - Picard number > 500 (for fourfolds)

## Search Instructions

### Step 1: Web Search
Use these search terms:
- "LMFDB varieties Hodge number large"
- "LMFDB fourfold h22"
- "LMFDB K3 surface Picard"

Find LMFDB entries for varieties.

### Step 2: Navigate LMFDB
When you find LMFDB pages:
- Look for tables with Hodge numbers
- Look for "Picard number" or "rank of Picard group"
- Note variety labels (e.g., "LMFDB:4.8.0.1")

### Step 3: Extract Data
For each variety found, record:
- **Label:** LMFDB identifier
- **Dimension:** 2, 3, or 4
- **Hodge numbers:** h^{1,1}, h^{2,1}, h^{2,2} (whichever available)
- **Picard number:** If listed
- **Gap:** Hodge number - Picard (if both known)
- **Reference:** Link to paper (if provided)

### Step 4: Provide Provenance
**CRITICAL:** For every piece of data, you MUST include:

1. **Source URL:** Direct link where you found this
   - Example: "https://www.lmfdb.org/Variety/4.8.0.1"

2. **Verbatim Quote:** Exact text from the page
   - Example: "h^{2,2} = 707, Picard number = 12"

3. **Extraction Location:** Where on page
   - Example: "Table: Hodge data, row 3"

4. **Confidence Score (0-1):**
   - 1.0 = Direct table value
   - 0.7 = Computed value stated in paper
   - 0.5 = Indirect reference
   - 0.3 = Uncertain
   - 0.0 = Guess (DO NOT USE)

5. **Confidence Rationale:** Why this score?
   - Example: "1.0 - Direct extraction from LMFDB table"

## Output Format

Produce a JSON file:

```json
{
  "agent_id": 1,
  "agent_role": "LMFDB Specialist",
  "timestamp": "2026-01-27 14:00:00",
  "search_strategy": "Web search for LMFDB entries with large Hodge numbers",
  "candidates": [
    {
      "label": "variety_12345",
      "canonical_id": "LMFDB:4.8.0.1",
      "dimension": 4,
      "h22": 707,
      "h11": 215,
      "picard": 12,
      "gap": 695,
      
      "source_url": "https://www.lmfdb.org/Variety/4.8.0.1",
      "verbatim_quote": "h^{2,2} = 707, Picard number = 12",
      "extraction_location": "Table: Hodge numbers, row 3",
      "confidence": 1.0,
      "confidence_rationale": "Direct extraction from LMFDB table",
      
      "reference": "https://arxiv.org/abs/2301.12345",
      "notes": "Cyclotomic hypersurface, degree 8"
    }
  ],
  "total_candidates": 15,
  "search_time_hours": 4
}
```

## Quality Criteria
- Prioritize varieties with gap > 500
- Include LMFDB canonical IDs when available
- Flag if Picard number unknown
- DO NOT include candidates without source URLs

## Auto-Rejection
Your candidates will be AUTOMATICALLY REJECTED if:
- Missing `source_url`
- Missing `verbatim_quote`
- Confidence < 0.3
- No extraction location

## Success Target
Find 5-20 varieties with complete provenance.

## Begin Your Search
Use web search and reasoning to complete this task. Report your findings in the JSON format above.
```

---

## **Agent 2: arXiv Miner - Complete Prompt**

```markdown
# AGENT 2: ARXIV PAPER MINER - LITERATURE SEARCH TASK

## Your Role
You are a mathematical literature specialist. Your job is to find varieties with large Hodge numbers from recent arXiv papers (2020-2026).

## What You're Looking For
Papers with:
1. **Explicit Hodge number tables** (e.g., "Table 1: Hodge numbers of varieties")
2. **Computations of Picard numbers** or algebraic cycle counts
3. **Varieties with large gaps:** h^{p,q} - known cycles > 50

## Search Instructions

### Step 1: Web Search
Use these search terms:
- "arXiv Hodge number fourfold 2023 2024 2025"
- "arXiv K3 surface Picard computation table"
- "arXiv Calabi-Yau Hodge numbers 2020-2026"

### Step 2: Identify Papers with Tables
Look for:
- Abstracts mentioning "we compute Hodge numbers"
- Papers with "Table" in snippets
- Computational algebraic geometry papers

### Step 3: Extract Data from Tables
When you find a paper with a table:
- Read table via reasoning (not parsing)
- Extract variety labels, Hodge numbers, Picard
- Note page number where table appears

### Step 4: Cross-Reference
If multiple papers mention same variety:
- Check if Hodge numbers agree
- Flag conflicts
- Higher confidence if multiple sources agree

### Step 5: Provide Provenance
**CRITICAL:** For every variety, include:

1. **Source URL:** arXiv link
   - Example: "https://arxiv.org/abs/2301.12345"

2. **Verbatim Quote:** Exact text/table entry
   - Example: "Table 2, row 5: Variety V_12, h^{2,2} = 707"

3. **Extraction Location:**
   - Example: "Page 12, Table 2, row 5"

4. **Confidence Score:**
   - 1.0 = Direct table entry
   - 0.7 = Stated computation result
   - 0.5 = Inferred from discussion

5. **Confidence Rationale:**
   - Example: "1.0 - Direct extraction from Table 2"

## Output Format

```json
{
  "agent_id": 2,
  "agent_role": "arXiv Paper Miner",
  "timestamp": "2026-01-27 14:00:00",
  "search_strategy": "arXiv search for papers with Hodge number tables",
  "candidates": [
    {
      "label": "variety_from_paper_title",
      "canonical_id": "arXiv:2301.12345_V12",
      "dimension": 4,
      "h22": 707,
      "picard": 12,
      "gap": 695,
      
      "source_url": "https://arxiv.org/abs/2301.12345",
      "verbatim_quote": "Table 2, row 5: V_12, h^{2,2}=707, ρ=12",
      "extraction_location": "Page 12, Table 2, row 5",
      "confidence": 1.0,
      "confidence_rationale": "Direct table extraction",
      
      "reference": "https://arxiv.org/abs/2301.12345",
      "notes": "From computational study of cyclotomic hypersurfaces"
    }
  ],
  "total_candidates": 20,
  "papers_reviewed": 15
}
```

## Quality Criteria
- Prioritize papers with explicit tables
- Note if paper provides construction method
- Flag if multiple papers mention same variety

## Success Target
Find 10-30 varieties from 10-20 papers.

## Begin Your Search
```

---

## **Agent 3: GRDB Specialist - Complete Prompt**

```markdown
# AGENT 3: GRDB SPECIALIST - CALABI-YAU DATABASE TASK

## Your Role
You are a specialist in the Graded Ring Database (GRDB). Your job is to find Calabi-Yau 3-folds and Fano varieties with large Hodge numbers.

## What You're Looking For
Calabi-Yau 3-folds with:
1. **Large h^{2,1}:** > 50
2. **Small Picard:** Typically 1 for CY3
3. **Large gap:** ≈ h^{2,1} (since Picard small)

## Search Instructions

### Step 1: Web Search
- "Graded Ring Database Calabi-Yau h21"
- "GRDB Fano varieties Hodge numbers"

### Step 2: Navigate GRDB
Find GRDB pages with tables of CY3 or Fano varieties.

### Step 3: Extract Data
For each variety:
- Label (GRDB identifier)
- h^{1,1}, h^{2,1}
- Picard number
- Reference to construction

### Step 4: Provide Provenance
Same requirements as Agents 1-2:
- source_url
- verbatim_quote
- extraction_location
- confidence + rationale

## Output Format

```json
{
  "agent_id": 3,
  "agent_role": "GRDB Specialist",
  "candidates": [
    {
      "label": "CY3_12345",
      "canonical_id": "GRDB:CY3_12345",
      "dimension": 3,
      "h11": 5,
      "h21": 101,
      "picard": 1,
      "gap": 100,
      
      "source_url": "http://www.grdb.co.uk/...",
      "verbatim_quote": "CY3_12345: h^{1,1}=5, h^{2,1}=101",
      "extraction_location": "CY3 table, row 42",
      "confidence": 1.0,
      "confidence_rationale": "Direct GRDB table",
      
      "notes": "Calabi-Yau 3-fold"
    }
  ]
}
```

## Success Target
Find 20-50 CY3 varieties.

## Begin Your Search
```

---

## **Agent 4: Literature Deep Dive - Complete Prompt**

```markdown
# AGENT 4: LITERATURE DEEP DIVE - CLASSIC EXAMPLES

## Your Role
You are a mathematical historian. Your job is to find well-studied Hodge conjecture examples from classic papers.

## What You're Looking For
Varieties discussed as:
- "Potential counterexamples to Hodge conjecture"
- "Interesting test cases"
- "Large Hodge gaps"

## Search Instructions

### Step 1: Web Search
- "Hodge conjecture Mumford counterexample"
- "Clemens-Griffiths intermediate Jacobian"
- "Voisin Hodge classes non-algebraic examples"

### Step 2: Find Classic Papers
Look for papers by:
- Mumford, Griffiths, Voisin, Deligne, Nori
- Focus on papers discussing specific varieties

### Step 3: Extract Examples
For each variety:
- What is it? (construction)
- Hodge numbers (if known)
- Why is it interesting?
- Has it been proven non-algebraic OR still open?

### Step 4: Provide Provenance
Same requirements: source_url, quote, location, confidence.

## Output Format

```json
{
  "agent_id": 4,
  "agent_role": "Literature Deep Dive",
  "candidates": [
    {
      "label": "Mumford_torus",
      "canonical_id": "Mumford1968",
      "dimension": 3,
      "h21": "unknown",
      "picard": 1,
      
      "source_url": "https://doi.org/10.1007/...",
      "verbatim_quote": "First example of non-algebraic Hodge class",
      "extraction_location": "Page 5, Theorem 1",
      "confidence": 0.7,
      "confidence_rationale": "Classic result, Hodge number not stated",
      
      "notes": "Abelian variety, first proven counterexample"
    }
  ]
}
```

## Success Target
Find 3-10 classic examples with historical context.

## Begin Your Search
```

---

## **Agent 5: Cross-Database Integrator - Complete Prompt**

```markdown
# AGENT 5: CROSS-DATABASE INTEGRATOR - MULTI-SOURCE VALIDATION

## Your Role
You are a data integration specialist. Your job is to find varieties mentioned in MULTIPLE sources (LMFDB + arXiv + GRDB) to ensure high confidence.

## What You're Looking For
Varieties that appear in:
- LMFDB AND arXiv (same variety, different sources)
- GRDB AND arXiv
- Multiple papers on arXiv

## Search Instructions

### Step 1: Search All Databases
Simultaneously search:
- LMFDB
- GRDB
- arXiv

### Step 2: Look for Overlaps
When you find a variety in one source:
- Search for it in other sources
- Check if Hodge numbers agree
- Flag conflicts

### Step 3: Cross-Validation
If sources agree:
- Higher confidence (multi-source confirmation)

If sources disagree:
- Flag for manual review
- Report discrepancy

### Step 4: Provide Provenance
For EACH source mentioning the variety:
- Include separate entry with source_url, quote, etc.

## Output Format

```json
{
  "agent_id": 5,
  "agent_role": "Cross-Database Integrator",
  "candidates": [
    {
      "label": "variety_12345",
      "canonical_id": "LMFDB:4.8.0.1",
      "dimension": 4,
      "h22": 707,
      
      "sources_found": [
        {
          "source": "LMFDB",
          "source_url": "https://www.lmfdb.org/...",
          "verbatim_quote": "h^{2,2} = 707",
          "h22_reported": 707
        },
        {
          "source": "arXiv:2301.12345",
          "source_url": "https://arxiv.org/abs/2301.12345",
          "verbatim_quote": "For V, h^{2,2} = 707",
          "h22_reported": 707
        }
      ],
      
      "agreement": "PERFECT",
      "confidence": 1.0,
      "confidence_rationale": "Multi-source confirmation, values agree",
      
      "notes": "Found in LMFDB and arXiv, values match"
    }
  ]
}
```

## Success Target
Find 10-20 varieties with multi-source confirmation.

## Begin Your Search
```

---

# **CROSS-VALIDATION PROTOCOL**

## **Step 1: Collect Agent Outputs**

**After all 5 agents complete:**

1. Save agent JSON files:
   ```
   agent_outputs/agent_1_findings.json
   agent_outputs/agent_2_findings.json
   agent_outputs/agent_3_findings.json
   agent_outputs/agent_4_findings.json
   agent_outputs/agent_5_findings.json
   ```

2. Manual review:
   - Are there JSON formatting errors?
   - Do candidates have required fields?
   - Quick sanity check: Do sources look real (not hallucinated)?

---

## **Step 2: Normalize Labels**

**Problem:** Different agents may use different names for same variety

**Solution:** Normalize to canonical identifiers

**Canonical ID Hierarchy:**
1. **LMFDB ID** (if available): `LMFDB:4.8.0.1`
2. **arXiv ID + label** (if from paper): `arXiv:2301.12345_V12`
3. **GRDB ID** (if from GRDB): `GRDB:CY3_12345`
4. **Normalized label** (if none above): lowercase, remove prefixes

**Example Normalization:**
- Agent 1: "LMFDB:4.8.0.1"
- Agent 2: "Cyclotomic hypersurface degree 8"
- Agent 5: "variety_12345 (LMFDB)"

→ All map to: `LMFDB:4.8.0.1`

---

## **Step 3: Identify Convergence**

**Rule:** Variety mentioned by ≥3 agents = consensus candidate

**Weighted Scoring:**
```
For each variety:
  weighted_score = sum(agent.confidence for agent in mentions)

Consensus if:
  weighted_score >= 2.0  OR  (agent_count >= 3 AND avg_confidence >= 0.5)
```

**Example:**
- 5 agents find variety, confidences: [1.0, 1.0, 0.7, 0.5, 0.3]
- Weighted score: 3.5 → CONSENSUS
- Agent count: 5, avg: 0.7 → CONSENSUS

vs.

- 3 agents find variety, confidences: [0.5, 0.3, 0.3]
- Weighted score: 1.1 → NO CONSENSUS (too low)
- Agent count: 3, avg: 0.37 → NO CONSENSUS (avg too low)

---

## **Step 4: Cross-Validate Hodge Numbers**

**For each consensus candidate:**

1. **Extract all reported Hodge numbers:**
   - Agent 1: h^{2,2} = 707
   - Agent 2: h^{2,2} = 707
   - Agent 5: h^{2,2} = 707

2. **Check agreement:**
   - **PERFECT:** All agree → high confidence
   - **CONFLICT:** Disagree → flag for manual review

3. **If conflict:**
   - Check original sources
   - Determine which is correct
   - Update consensus value

---

## **Step 5: Rank Consensus Candidates**

**Ranking Criteria:**

```
Score = 0.4 × (Gap%) + 0.3 × (Weighted_Confidence) + 0.2 × (Multi_Source) + 0.1 × (Dimension_Match)
```

Where:
- **Gap%:** (gap / Hodge number) × 100
- **Weighted_Confidence:** weighted_score / max_possible
- **Multi_Source:** 1.0 if multiple sources, 0.5 if single source
- **Dimension_Match:** 1.0 if fourfold, 0.75 if K3, 0.5 if CY3

**Output:** Top 5-10 candidates sorted by score

---

## **Step 6: Generate Consensus Report**

**File:** `consensus_candidates.json`

```json
{
  "convergence_method": "weighted (confidence-based)",
  "threshold": "weighted_score >= 2.0 OR (count >= 3 AND avg >= 0.5)",
  "total_consensus": 12,
  "candidates": [
    {
      "rank": 1,
      "label": "variety_12345",
      "canonical_id": "LMFDB:4.8.0.1",
      "agent_count": 5,
      "weighted_score": 3.5,
      "avg_confidence": 0.7,
      
      "hodge_number": 707,
      "hodge_agreement": "PERFECT",
      "picard": 12,
      "gap": 695,
      "gap_percentage": 98.3,
      
      "sources": [
        "https://www.lmfdb.org/...",
        "https://arxiv.org/abs/2301.12345"
      ],
      
      "score": 85.3,
      "notes": "Multi-source confirmation, perfect agreement"
    }
  ]
}
```

---

# **COMPUTATIONAL FALSIFICATION (SELECTIVE)**

## **When We Compute**

**ONLY when:**
1. ✅ Consensus reached (≥3 agents)
2. ✅ Human review passed (sources credible, claim plausible)
3. ��� Falsifiable attribute identified (testable claim)
4. ✅ Compute method agreed upon (agents/human decide how)

**We DO NOT compute:**
- ❌ During agent search
- ❌ For every candidate
- ❌ Without clear falsifiable goal

---

## **Falsifiable Attributes (Examples)**

**1. Hodge Number Claim:**
- **Agent claim:** "h^{2,2} = 707 for this variety"
- **Falsification:** Compute h^{2,2} via Macaulay2 (if construction provided)
- **Method:** Agents suggest: "Use Macaulay2 to compute kernel dimension mod p=53"
- **Decision:** Human approves if construction available

**2. Gap Claim:**
- **Agent claim:** "Gap = 695 (h^{2,2} - Picard)"
- **Falsification:** Verify Picard number (if cycles listed)
- **Method:** Agents suggest: "Compute Picard lattice via intersection theory"

**3. Variable-Count Claim:**
- **Agent claim:** "All classes use 6 variables (from paper)"
- **Falsification:** Compute variable-count distribution (if basis available)
- **Method:** Use Foundation tools (Section 4.5)

---

## **Verification Decision Tree**

```
Consensus Candidate
    ↓
Human Review
    ├─→ Sources credible? → YES
    ├─→ Claim plausible? → YES
    └─→ Construction available? → YES/NO
         ↓
         ├─→ YES: Construction provided
         │       ↓
         │   Ask Agents: "How do we verify this?"
         │       ↓
         │   Agents suggest method (e.g., "Macaulay2 mod p=53")
         │       ↓
         │   Human approves compute time
         │       ↓
         │   Execute computation
         │       ↓
         │   Compare to agent claim
         │       ├─→ MATCH: Verified
         │       └─→ MISMATCH: Reject OR investigate
         │
         └─→ NO: Construction not provided
                 ↓
             Can we derive it from description?
                 ├─→ YES: Derive, then verify
                 └─→ NO: Flag as "Cannot verify computationally"
                         (Accept on multi-source trust OR reject)
```

---

## **Example Verification Workflow**

**Candidate:** "Cyclotomic degree-8 hypersurface in P^5, h^{2,2} = 707"

**Step 1: Human Review**
- Sources: LMFDB + arXiv paper
- Credible? YES
- Plausible? YES (matches our cyclotomic variety!)
- Construction? YES (paper provides F = sum L_k^8)

**Step 2: Ask Agents for Verification Method**

Prompt to Agent 1:
```
We have a candidate: cyclotomic degree-8 hypersurface in P^5.
Agents report h^{2,2} = 707.
How should we verify this computationally?
```

Agent 1 response:
```
Use Macaulay2:
1. Construct Jacobian ring mod p=53
2. Compute kernel dimension
3. Should get 707 if claim is correct
```

**Step 3: Human Approves**
- Compute time: ~30 minutes
- Approved

**Step 4: Execute (Macaulay2)**

```macaulay2
-- verify_h22_mod53.m2
use (ZZ/53)[z0..z5];
omega = -- (primitive 13th root mod 53)
F = sum(k=0 to 12, (sum(j=0 to 5, omega^(k*j) * (gens R)#j))^8);
J = ideal jacobian ideal F;
M = gens J;
K = kernel M;
h22 = rank K;
print("h^{2,2} mod 53: " | toString h22);
```

**Step 5: Compare**
- Computed: 707
- Agent claim: 707
- **VERIFIED**

---

# **DECISION TREE**

## **Day 3 Decision Point**

```
Review consensus_candidates.json
    |
    ├─→ ≥1 verified candidate with gap >50%
    |       ├─→ SCENARIO A: Pursue candidate
    |       |   ├─→ Variable-count data available? → Compute distribution
    |       |   ├─→ Construction available? → Period computation
    |       |   └─→ Week 2: Deep dive on candidate
    |       |
    |       └─→ OR: Skip to weighted projective if candidate is our cyclotomic
    |
    ├─→ All gaps <30% OR verification failed
    |       ├─→ SCENARIO B: 20% barrier confirmed
    |       └─→ Proceed to weighted projective (Day 4)
    |
    └─→ No consensus (<3 agents agree on any candidate)
            ├─→ SCENARIO C: Manual review
            |   ├─→ Check agent outputs for errors
            |   └─→ Re-run if fixable
            |
            └─→ OR: Abort database mining
                    Proceed to weighted projective
```

---

## **Scenario Details**

### **Scenario A: Breakthrough Candidate (Gap >50%)**

**Action:**
1. If candidate is NEW (not our cyclotomic):
   - Week 2: Compute variable-count distribution
   - Week 2-3: Period computation + PSLQ
   - If transcendental period: Contact experts

2. If candidate is our cyclotomic:
   - Validates our construction
   - Confirms 20% barrier for rational varieties
   - Proceed to weighted projective (test barrier)

**Timeline:** Week 2-3 OR immediate (weighted projective)

---

### **Scenario B: Barrier Confirmed (All <30%)**

**Action:**
1. Document findings:
   - Database confirms 20% barrier is general
   - Update substrate map
2. Proceed to weighted projective (Day 4)

**Timeline:** Immediate

---

### **Scenario C: No Convergence**

**Action:**
1. Manual review of agent outputs
2. Check for systematic errors
3. Re-run agents if fixable
4. Otherwise: Abort, weighted projective

**Timeline:** 1 day review OR immediate abort

---

# **DATA SCHEMAS**

## **Agent Output Schema**

```json
{
  "agent_id": 1,
  "agent_role": "LMFDB Specialist",
  "timestamp": "2026-01-27 14:30:00",
  "search_strategy": "description of approach",
  "candidates": [
    {
      "label": "variety_identifier",
      "canonical_id": "LMFDB:4.8.0.1 | arXiv:XXXX.XXXXX_VN | GRDB:CY3_N",
      "dimension": 2,
      "h11": 10,
      "h21": 100,
      "h22": 707,
      "picard": 12,
      "gap": 695,
      
      "source_url": "https://...",
      "verbatim_quote": "exact text from source",
      "extraction_location": "Table X, row Y",
      "confidence": 1.0,
      "confidence_rationale": "Direct table extraction",
      
      "reference": "https://arxiv.org/...",
      "notes": "additional context"
    }
  ],
  "total_candidates": 15,
  "search_time_hours": 4
}
```

---

## **Consensus Candidates Schema**

```json
{
  "convergence_method": "weighted confidence",
  "threshold": "weighted >= 2.0 OR (count >= 3 AND avg >= 0.5)",
  "total_consensus": 12,
  "candidates": [
    {
      "rank": 1,
      "label": "variety_identifier",
      "canonical_id": "canonical ID",
      "agent_count": 5,
      "weighted_score": 3.5,
      "avg_confidence": 0.7,
      "agent_ids": [1, 2, 3, 4, 5],
      
      "hodge_number": 707,
      "hodge_agreement": "PERFECT | CONFLICT",
      "picard": 12,
      "gap": 695,
      "gap_percentage": 98.3,
      
      "sources": ["https://...", "https://..."],
      "references": ["https://arxiv.org/..."],
      
      "score": 85.3,
      "notes": "multi-source confirmation"
    }
  ]
}
```

---

## **Verified Candidates Schema**

```json
{
  "total_verified": 5,
  "verification_method": "selective computational falsification",
  "candidates": [
    {
      "label": "variety_identifier",
      "agent_claim_h22": 707,
      "computed_h22_mod_53": 707,
      "verification_status": "VERIFIED | REJECTED | CANNOT_VERIFY",
      "gap": 695,
      "gap_percentage": 98.3,
      "notes": "Macaulay2 verification, claim matches"
    }
  ]
}
```

---

# **SUCCESS CRITERIA & FALSIFICATION**

## **Success Criteria**

### **Minimum Success:**
- ≥3 consensus candidates (weighted score ≥2.0)
- ≥1 candidate with gap >30%
- Sources credible (URLs valid, not hallucinated)

### **Strong Success:**
- ≥5 consensus candidates
- ≥1 verified candidate (computational falsification passed)
- ≥1 candidate with gap >50%

### **Optimal Success:**
- ≥10 consensus candidates
- ≥3 verified
- ≥1 candidate with gap >90% OR variable-count >30%

---

## **Falsification Criteria**

### **Hard Failure (Abort MARS):**

1. **No agent convergence:**
   - <3 agents agree on ANY variety
   - Likely: Agents misunderstood task OR databases empty

2. **All sources hallucinated:**
   - URLs don't exist OR lead to unrelated pages
   - Agents fabricated data

3. **All verification fails:**
   - Agents report candidates, but computational checks reject all

**Action:** Abort database mining, proceed to weighted projective

---

### **Soft Failure (Partial Success):**

1. **Low convergence (3-5 candidates):**
   - Some overlap but not strong
   - Action: Verify best candidates

2. **Hodge number conflicts:**
   - Agents disagree on values
   - Action: Manual review of sources

3. **All gaps <20%:**
   - Confirms barrier
   - Action: Document, weighted projective

---

## **Success Metrics Table**

| Metric | Minimum | Target | Optimal |
|--------|---------|--------|---------|
| Consensus candidates | ≥3 | ≥5 | ≥10 |
| Agent agreement (avg) | ≥3/5 | ≥4/5 | 5/5 |
| Verified candidates | ≥1 | ≥3 | ≥5 |
| Max gap percentage | >30% | >50% | >90% |
| Variable-count >30% | 0 | ≥1 | ≥2 |

---

# **EXECUTION GUIDE**

## **Day 1: Deploy Agents (4-6 hours)**

**Step 1: Create Workspace (5 min)**

```bash
cd ~/OrganismCore/validator_v2
mkdir -p mars_v1
cd mars_v1
mkdir -p agent_outputs
mkdir -p logs
```

**Step 2: Initialize Execution Log**

Create: `logs/execution_log.md`

```markdown
# MARS v1.0 Execution Log

## Day 1: Agent Deployment

### Agent 1 (LMFDB)
- **Status:** PENDING
- **Started:** 
- **Completed:**
- **Candidates Found:**
- **Notes:**

[Repeat for Agents 2-5]
```

---

**Step 3: Deploy Agents (Parallel, 4-6 hours)**

For each agent:

1. Open new LLM chat session (Claude/ChatGPT)
2. Copy agent prompt (Section 6)
3. Paste into chat
4. Agent executes search
5. Agent produces JSON
6. Copy JSON to: `agent_outputs/agent_N_findings.json`

**Monitor Progress (Every Hour):**
- Update execution log
- Check candidate counts
- Spot-check sources (valid URLs?)

---

**Step 4: Checkpoint (End of Day 1)**

**Review:**
- ✅ All 5 agent JSON files saved?
- ✅ Total unique candidates: [count]
- ✅ Quick sanity check: Sources look real?

**Early Abort Check:**
- If ALL agents found 0 candidates → STOP (databases empty or task misunderstood)

---

## **Day 2: Cross-Validation (2-3 hours)**

**Step 1: Manual Review of Agent Outputs (30 min)**

For each `agent_N_findings.json`:

1. Open file
2. Check JSON formatting (valid?)
3. Spot-check 2-3 candidates:
   - Do source URLs exist?
   - Is verbatim_quote plausible?
   - Is confidence score reasonable?

**Red Flags:**
- URLs that don't exist → Agent hallucinated
- Quotes that don't match source → Agent misread
- Confidence 1.0 but paywalled source → Inconsistent

---

**Step 2: Identify Convergence (Manual, 1 hour)**

**Process:**

1. Create spreadsheet: `convergence_matrix.csv`

```csv
Variety Label,Agent 1,Agent 2,Agent 3,Agent 4,Agent 5,Total
variety_12345,✓ (1.0),✓ (1.0),✓ (0.7),,✓ (1.0),4 (3.7)
cy3_67890,,✓ (0.7),✓ (1.0),✓ (0.5),,3 (2.2)
...
```

2. For each variety:
   - Count agents
   - Sum confidence scores
   - Check threshold: weighted ≥2.0 OR (count ≥3 AND avg ≥0.5)

3. Mark consensus candidates (✓)

---

**Step 3: Cross-Validate Hodge Numbers (30 min)**

For each consensus candidate:

1. List all reported Hodge numbers:
   - Agent 1: h^{2,2} = 707
   - Agent 2: h^{2,2} = 707
   - Agent 5: h^{2,2} = 707

2. Agreement?
   - **YES:** Mark PERFECT
   - **NO:** Mark CONFLICT, investigate sources

---

**Step 4: Rank Candidates (30 min)**

Manual scoring:

```
Score = 0.4 × (Gap%) + 0.3 × (Confidence) + 0.2 × (Multi-Source) + 0.1 × (Dimension)
```

Sort by score, select top 5-10.

---

**Step 5: Generate Consensus Report (30 min)**

Create: `consensus_candidates.json` (manually from spreadsheet)

```json
{
  "total_consensus": 8,
  "candidates": [
    {
      "rank": 1,
      "label": "variety_12345",
      "agent_count": 4,
      "weighted_score": 3.7,
      "hodge_number": 707,
      "gap": 695,
      "gap_percentage": 98.3,
      "sources": ["https://lmfdb.org/...", "https://arxiv.org/..."],
      "score": 87.5
    }
  ]
}
```

---

## **Day 2-3: Human Review (1-2 hours)**

**For each consensus candidate:**

**Checklist:**
- [ ] Source URLs valid (not hallucinated)?
- [ ] Verbatim quotes match sources?
- [ ] Hodge number plausible for variety type?
- [ ] Geometric description makes sense?
- [ ] Construction available OR derivable?
- [ ] Worth computational verification?

**Decision for each:**
- **APPROVE:** Verify computationally (if construction available)
- **SKIP:** Accept on trust (multi-source) OR reject
- **REJECT:** Sources invalid OR claim implausible

---

## **Day 3: Selective Verification (Variable)**

**For each APPROVED candidate:**

**Step 1: Identify Falsifiable Attribute**
- Example: "h^{2,2} = 707"

**Step 2: Determine Method (Ask Agents OR Decide)**

Option A: Ask agents
```
Prompt: "How do we verify h^{2,2} = 707 for [variety description]?"
Agent suggests method
Human approves
```

Option B: Human decides
```
Method: Macaulay2 mod p=53, compute kernel dimension
```

**Step 3: Execute Computation**

Write Macaulay2 script (or Sage, PARI), run, record result.

**Step 4: Compare**
- Computed value = Agent claim? → VERIFIED
- Mismatch? → REJECT OR investigate

---

**Step 5: Update Verified Candidates**

Create: `verified_candidates.json`

```json
{
  "total_verified": 2,
  "candidates": [
    {
      "label": "variety_12345",
      "agent_claim_h22": 707,
      "computed_h22_mod_53": 707,
      "verification_status": "VERIFIED",
      "gap_percentage": 98.3
    }
  ]
}
```

---

## **Day 3: Decision**

**Review verified_candidates.json:**

- ≥1 verified with gap >50%? → Scenario A
- All <30% OR verification failed? → Scenario B
- No consensus? → Scenario C

**Execute scenario action** (see Decision Tree section).

---

# **EXECUTION LOG**

## **Day 1: Agent Deployment**

**Date:** 2026-01-27

### **Agent 1: LMFDB Specialist**
- **Status:** [PENDING / IN_PROGRESS / COMPLETE]
- **Started:**
- **Completed:**
- **Candidates Found:**
- **Search Time:**
- **Notes:**

### **Agent 2: arXiv Paper Miner**
- **Status:**
- **Started:**
- **Completed:**
- **Candidates Found:**
- **Papers Reviewed:**
- **Notes:**

### **Agent 3: GRDB Specialist**
- **Status:**
- **Started:**
- **Completed:**
- **Candidates Found:**
- **Notes:**

### **Agent 4: Literature Deep Dive**
- **Status:**
- **Started:**
- **Completed:**
- **Candidates Found:**
- **Notes:**

### **Agent 5: Cross-Database Integrator**
- **Status:**
- **Started:**
- **Completed:**
- **Candidates Found:**
- **Conflicts Detected:**
- **Notes:**

---

## **Day 2: Cross-Validation**

**Date:** 2026-01-28

### **Total Unique Varieties:**
- [count from all agents]

### **Consensus Candidates (≥3 agents):**
- [count]
- **Top 5:** [list labels + scores]

### **Hodge Number Conflicts:**
- [count]
- **Examples:** [describe conflicts]

### **Decision:**
- [Proceed to verification / Manual review / Abort]

---

## **Day 3: Verification & Decision**

**Date:** 2026-01-29

### **Candidates Verified:**
- [count]

### **Verification Results:**

**Candidate 1:**
- **Label:**
- **Agent Claim:**
- **Computed Value:**
- **Status:** [VERIFIED / REJECTED / CANNOT_VERIFY]
- **Notes:**

### **Final Decision:**
- **Scenario:** [A / B / C]
- **Action:** [describe next steps]

---

# **META-LEARNING**

## **Substrate Truths Discovered**

*(Update after execution)*

### **Before Execution (Predictions):**

1. **Agent Convergence:** Expect 50-70% overlap on classic examples
2. **Database Completeness:** LMFDB most reliable, GRDB less complete
3. **20% Barrier:** Most candidates will have gap 10-30%

### **After Execution (Update This Section):**

**Discovery 1:** [What we learned about agent convergence]

**Discovery 2:** [What we learned about databases]

**Discovery 3:** [What we learned about 20% barrier]

**Substrate Map Update:**
- [New regions?]
- [New barriers?]
- [New tools?]

---

## **Barriers Encountered**

**Barrier 1:** [If agents hallucinated]
- **Mitigation:**
- **Status:**

**Barrier 2:** [If low convergence]
- **Mitigation:**
- **Status:**

---

## **Tools Built**

**Tool: Multi-Agent Reasoning Search (MARS) Protocol**
- Prompts: 5 agent prompts (Section 6)
- Methodology: Cross-validation + selective verification
- **Status:** ✅ Complete (after Day 3)
- **Reusability:** Can be adapted for ANY database mining task

---

## **Falsification Results**

**Hypothesis H1 (>30% aperiodic in database):**
- **Result:** [CONFIRMED / FALSIFIED / INCONCLUSIVE]
- **Evidence:**

**Hypothesis H2 (agent convergence >50%):**
- **Result:**
- **Evidence:**

---

# **CONCLUSION**

*(To be written after execution)*

## **Summary**

**What MARS Achieved:**
- [Consensus candidates found]
- [Verification results]
- [Barrier confirmation OR breakthrough]

**What We Learned:**
- [About databases]
- [About multi-agent search]
- [About 20% barrier]

**Next Steps:**
- [Week 2 plan based on scenario]

**Time Investment:**
- [Actual vs. estimated 2-3 days]

**Was MARS Worth It?**
- [Honest assessment]

---

**END OF REASONING ARTIFACT v1.0**

**Ready to deploy agents!** 🚀

Copy Agent 1-5 prompts (Section 6) to separate LLM sessions and begin search.
