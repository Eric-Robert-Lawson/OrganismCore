# 🔬 **HYPOTHESIS-DRIVEN DATABASE MINING VIA MULTI-AGENT REASONING SEARCH (HDB-MARS) - UNIVERSAL EXECUTABLE PROTOCOL v1.0**

**A reasoning substrate for database-driven discovery when exact computation is intractable**

---

## **📋 DOCUMENT METADATA**

**Version:** 1.0 (Universal Protocol — Domain-Agnostic)  
**Date:** 2026-01-28  
**Status:** ✅ PRODUCTION-READY REASONING SUBSTRATE  
**Scope:** Universal (any database, any research domain)  
**Execution Model:** Read → Recognize → Deploy Agents → Synthesize  

**Location:** `Subdomain_Articles/hypothesis_driven_database_mining.md`  
**Integration:** Early onboarding (before domain-specific protocols)

---

## **TABLE OF CONTENTS**

1. [Executive Summary](#executive-summary)
2. [Core Methodology: Reasoning as Search](#core-methodology-reasoning-as-search)
3. [When to Use This Protocol](#when-to-use-this-protocol)
4. [HDB-MARS Protocol Overview](#hdb-mars-protocol-overview)
5. [Agent Roles & Search Strategies](#agent-roles--search-strategies)
6. [Anti-Hallucination Requirements](#anti-hallucination-requirements)
7. [Agent Prompt Templates](#agent-prompt-templates)
8. [Computational Verification (Selective)](#computational-verification-selective)
9. [Decision Tree](#decision-tree)
10. [Data Schemas](#data-schemas)
11. [Success & Falsification Criteria](#success--falsification-criteria)
12. [Execution Guide](#execution-guide)
13. [Execution Log Template](#execution-log-template)
14. [Meta-Learning](#meta-learning)
15. [Integration with OrganismCore](#integration-with-organismcore)
16. [Appendix: Domain Adaptations](#appendix-domain-adaptations)

---

# **EXECUTIVE SUMMARY**

## **What This Protocol Does**

**HDB-MARS (Hypothesis-Driven Database Mining via Multi-Agent Reasoning Search)** is an executable reasoning protocol for discovering examples in large databases when:

1. **Exact computation is intractable** (weeks/months per example)
2. **Databases exist but are poorly indexed** (no API for your property)
3. **Cross-referencing is manual** (same object, different identifiers)
4. **Hypothesis testing requires examples** (need 10-50 instances to test theory)

**Key insight:** Instead of computing exhaustively or scraping APIs, deploy **multiple reasoning agents** with different search strategies, then cross-validate their findings.

---

## **Why HDB-MARS (Not Brute-Force Computation or API Scraping)**

### **HDB-MARS Advantages**

| Approach | Time | Coverage | Reliability |
|----------|------|----------|-------------|
| **Brute-force computation** | Weeks-years | 100% (if finishes) | Perfect |
| **API scraping** | Hours-days | 80-95% (if API exists) | High |
| **HDB-MARS (this protocol)** | **2-3 days** | **60-90%** | **Medium-High** |

**When HDB-MARS is optimal:**
- Exact computation: >1 month total time
- No suitable API exists (or API doesn't expose your property)
- Need hypothesis validation (not exhaustive enumeration)
- Acceptable to miss 10-40% of examples (find enough to test theory)

### **When We Compute Exactly**

**Selective verification only:**
- **NOT** to find all examples (too expensive)
- **YES** to falsify agent hallucinations (spot-check top 5-10 candidates)
- **YES** to break ties (when multiple agents disagree)
- **YES** to certify flagship results (final paper needs deterministic proof)

---

## **Timeline**

| Phase | Duration | Activity |
|-------|----------|----------|
| **Day 1** | 4-6 hours | Deploy 5 specialized agents (parallel reasoning search) |
| **Day 2** | 2-3 hours | Cross-validation (identify consensus candidates) |
| **Day 2-3** | 1-2 hours | Human review (filter hallucinations) |
| **Day 3** | Variable | Selective verification (exact computation for top 5-10) |
| **Day 3** | 1 hour | Decision (proceed to next phase or pivot) |

**Total: 2-3 days** (vs. weeks/months for exhaustive computation)

---

# **CORE METHODOLOGY: REASONING AS SEARCH**

## **The Fundamental Insight**

**Traditional database query:**
```sql
SELECT * FROM varieties WHERE picard_number > 10;
```
**Problem:** Database doesn't have `picard_number` column (too expensive to compute for all)

**HDB-MARS approach:**
```
Agent 1: Search LMFDB for varieties with large h^{1,1} (Picard ≤ h^{1,1})
Agent 2: Mine arXiv for papers mentioning "large Picard rank"
Agent 3: Search GRDB for varieties with few algebraic cycles
Agent 4: Review classical literature (Fermat, toric, etc.)
Agent 5: Cross-reference all findings (same variety, different IDs?)

Consensus: Varieties found by ≥3 agents (high confidence)
Verification: Compute exactly for top 5-10 (falsify hallucinations)
```

**Result:** Find 20-50 high-Picard varieties in 2-3 days (vs. years for exhaustive search)

---

## **What Agents Do (Reasoning)**

**Each agent is a search strategy:**

1. **Formulate search heuristic** (domain-specific)
   - Example: "Large h^{1,1} suggests large Picard" (mathematical reasoning)
   - Example: "Papers with 'exceptional' in title may contain outliers" (literature heuristic)

2. **Execute search** (via reasoning, not code)
   - Query databases (LMFDB, GRDB, arXiv, etc.)
   - Parse papers (extract examples from text)
   - Cross-reference (same object, different names?)

3. **Report findings** (with provenance)
   - Candidate list (variety ID, properties, confidence)
   - Provenance (database URL, paper citation, query used)
   - Confidence score (0-1, based on evidence quality)

**Agents do NOT:**
- Compute exact values (too expensive, human/HPC does this)
- Hallucinate (auto-rejected if no provenance)
- Duplicate work (each agent has different strategy)

---

## **What Humans/Computation Do (Verification)**

**Human role:**
- Review agent outputs (filter obvious hallucinations)
- Resolve conflicts (when agents disagree)
- Make decision (proceed, pivot, or abort)

**Exact computation role (selective):**
- Verify top 5-10 candidates (falsify hallucinations)
- Certify flagship results (deterministic proof for publication)
- Break ties (when agents disagree on borderline cases)

**NOT used for:**
- Exhaustive enumeration (too expensive)
- Finding all examples (HDB-MARS is hypothesis-driven, not complete)

---

# **WHEN TO USE THIS PROTOCOL**

## **Recognition Moment**

**Use HDB-MARS when you recognize:**

> "I need 10-50 examples of [property] to test my hypothesis, but computing exhaustively would take months, and no database has this property pre-computed."

**Specific triggers:**

1. ✅ **Exact computation intractable** (>1 month total time)
2. ✅ **Database exists** (LMFDB, GRDB, arXiv, or domain-specific)
3. ✅ **Property not indexed** (no API query for your attribute)
4. ✅ **Hypothesis testing** (need examples, not exhaustive list)
5. ✅ **Cross-referencing needed** (same object, multiple databases)

**Example scenarios:**

| Domain | Property | Database(s) | Why HDB-MARS? |
|--------|----------|-------------|---------------|
| Algebraic geometry | Picard rank > 10 | LMFDB, GRDB, arXiv | Picard not pre-computed, exact = weeks |
| Number theory | Class number > 1000 | LMFDB, PARI/GP | Class number expensive, not indexed |
| Graph theory | Chromatic number = 5 | House of Graphs | Chromatic number NP-hard |
| Molecular biology | Protein fold stability | PDB, UniProt | Stability simulation expensive |
| Condensed matter | High-Tc superconductors | Materials Project | Tc prediction unreliable |

---

## **When NOT to Use HDB-MARS**

**Use exhaustive computation instead if:**
- ❌ Exact computation is feasible (<1 week total)
- ❌ Property is already indexed (API query exists)
- ❌ Need 100% coverage (cannot miss any examples)
- ❌ Database is small (<1000 entries, just compute all)

**Use traditional ML instead if:**
- ❌ Training data exists (supervised learning applicable)
- ❌ Property is predictable (regression/classification works)
- ❌ Need real-time inference (HDB-MARS is for discovery, not deployment)

---

# **HDB-MARS PROTOCOL OVERVIEW**

## **Complete Pipeline**

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: PARALLEL AGENT DEPLOYMENT (Day 1, 4-6 hours)      │
├─────────────────────────────────────────────────────────────┤
│ Agent 1: Database Specialist (search primary DB)           │
│ Agent 2: Literature Miner (search papers/arXiv)            │
│ Agent 3: Cross-Database Specialist (search secondary DBs)  │
│ Agent 4: Historical/Classical Specialist (classic examples)│
│ Agent 5: Integrator (cross-reference all findings)         │
│                                                             │
│ Output: 5 lists of candidates (with provenance)            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: CROSS-VALIDATION (Day 2, 2-3 hours)               │
├─────────────────────────────────────────────────────────────┤
│ 1. Merge all agent outputs (remove duplicates)             │
│ 2. Identify consensus candidates (≥3 agents agree)         │
│ 3. Flag conflicts (agents disagree on properties)          │
│ 4. Compute confidence scores (weighted by provenance)      │
│                                                             │
│ Output: Ranked list of candidates (high → low confidence)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: HUMAN REVIEW (Day 2-3, 1-2 hours)                 │
├─────────────────────────────────────────────────────────────┤
│ 1. Filter obvious hallucinations (missing provenance)      │
│ 2. Resolve conflicts (check original sources)              │
│ 3. Prioritize for verification (top 5-10 candidates)       │
│                                                             │
│ Output: Curated list for selective verification            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: SELECTIVE VERIFICATION (Day 3, variable)          │
├─────────────────────────────────────────────────────────────┤
│ Compute exactly for top 5-10 candidates                    │
│ - Falsify hallucinations (agent was wrong?)                │
│ - Certify flagship results (deterministic proof)           │
│ - Break ties (resolve agent disagreements)                 │
│                                                             │
│ Output: Verified candidates (with exact values)            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: DECISION (Day 3, 1 hour)                          │
├─────────────────────────────────────────────────────────────┤
│ Scenario A: Breakthrough (found strong examples)           │
│   → Proceed to detailed analysis / publication             │
│                                                             │
│ Scenario B: Barrier confirmed (no examples found)          │
│   → Hypothesis falsified, document null result             │
│                                                             │
│ Scenario C: Inconclusive (need more search)                │
│   → Deploy additional agents or refine search              │
└─────────────────────────────────────────────────────────────┘
```

---

# **AGENT ROLES & SEARCH STRATEGIES**

## **Agent 1: Primary Database Specialist**

**Role:** Search main database for candidates using indirect heuristics

**Search strategy:**
1. Identify proxy attributes (correlated with target property)
2. Query database for extreme values of proxy
3. Extract candidates with complete provenance

**Example (Picard rank in LMFDB):**
- Proxy: h^{1,1} (Picard ≤ h^{1,1} always)
- Query: Search for varieties with h^{1,1} > 100
- Extract: Variety ID, Hodge numbers, database URL

**Output format:**
```json
{
  "agent": "Agent-1-Primary-DB",
  "search_strategy": "High h^{1,1} proxy (Picard ≤ h^{1,1})",
  "database": "LMFDB",
  "candidates": [
    {
      "id": "db-12345",
      "name": "CY4 hypersurface in P^5",
      "proxy_value": "h^{1,1} = 252",
      "provenance": {
        "url": "https://lmfdb.org/...",
        "query": "h11>100 AND dimension=4",
        "timestamp": "2026-01-28"
      },
      "confidence": 0.8
    }
  ]
}
```

---

## **Agent 2: Literature Mining Specialist**

**Role:** Mine papers (arXiv, journals) for mentioned examples

**Search strategy:**
1. Search arXiv/Google Scholar for keywords
2. Parse papers for explicit examples (tables, theorems)
3. Extract citations and cross-reference

**Example (high-Picard varieties):**
- Keywords: "large Picard rank", "many algebraic cycles"
- Parse: Look for tables with Hodge numbers
- Extract: Paper citation, variety description, page number

**Output format:**
```json
{
  "agent": "Agent-2-Literature",
  "search_strategy": "arXiv keyword search + paper parsing",
  "candidates": [
    {
      "id": "paper-arxiv-2311.17146-variety-1",
      "name": "Champion CY4 from Hirst (2024)",
      "description": "Weights [1,1,84,516,1204,1806]",
      "provenance": {
        "paper": "arXiv:2311.17146",
        "authors": "Hirst & Schettini-Gherardini",
        "year": 2024,
        "page": 12,
        "table": "Table 1, Rank 1"
      },
      "confidence": 0.95
    }
  ]
}
```

---

## **Agent 3: Secondary Database Specialist**

**Role:** Search alternative databases (different indexing, different community)

**Search strategy:**
1. Identify secondary databases (domain-specific)
2. Query for candidates using database-specific methods
3. Cross-reference with primary DB (same object?)

**Example (GRDB for CY3/CY4):**
- Database: Gr\"obner basis database (GRDB)
- Query: Search for Calabi-Yau varieties with known cohomology
- Cross-ref: Match against LMFDB via weight systems

**Output format:**
```json
{
  "agent": "Agent-3-Secondary-DB",
  "search_strategy": "GRDB cohomology search + LMFDB cross-ref",
  "database": "GRDB",
  "candidates": [
    {
      "id": "grdb-cy4-789",
      "name": "Complete intersection CY4",
      "cross_ref": {
        "lmfdb_id": "db-12345",
        "match_confidence": 0.9,
        "match_method": "Hodge number agreement"
      },
      "provenance": {
        "url": "http://grdb.org/...",
        "query": "dimension=4 AND calabi_yau=true"
      },
      "confidence": 0.75
    }
  ]
}
```

---

## **Agent 4: Classical/Historical Specialist**

**Role:** Identify well-known classical examples from literature

**Search strategy:**
1. Review standard references (textbooks, classic papers)
2. Extract canonical examples (Fermat, toric, etc.)
3. Provide historical context

**Example (classical CY varieties):**
- Sources: Griffiths & Harris, Candelas et al., Batyrev
- Examples: Fermat quintic, mirror pairs, toric complete intersections
- Context: Why these are important (mirror symmetry, etc.)

**Output format:**
```json
{
  "agent": "Agent-4-Classical",
  "search_strategy": "Literature review of standard references",
  "candidates": [
    {
      "id": "classical-fermat-cy4",
      "name": "Fermat CY4 (x₀⁴ + ... + x₅⁴ = 0)",
      "historical_context": "Original Calabi-Yau, mirror pair known",
      "provenance": {
        "reference": "Candelas et al. (1991), Nucl. Phys. B",
        "canonical": true,
        "citations": 1500
      },
      "confidence": 1.0
    }
  ]
}
```

---

## **Agent 5: Cross-Database Integrator**

**Role:** Synthesize all agent outputs, resolve duplicates, identify consensus

**Search strategy:**
1. Merge all agent outputs
2. Identify duplicates (same object, different IDs)
3. Compute consensus scores (how many agents agree?)
4. Flag conflicts (agents disagree on properties)

**Output format:**
```json
{
  "agent": "Agent-5-Integrator",
  "search_strategy": "Cross-validation of Agents 1-4",
  "consensus_candidates": [
    {
      "canonical_id": "consensus-champion-1",
      "names": ["db-12345", "paper-arxiv-2311.17146-variety-1"],
      "description": "Champion CY4 [1,1,84,516,1204,1806]",
      "agent_agreement": {
        "total_agents": 5,
        "agreeing_agents": 4,
        "consensus_score": 0.8
      },
      "properties": {
        "h11": {"value": 252, "sources": 4, "conflicts": 0},
        "h22": {"value": 1213644, "sources": 4, "conflicts": 0}
      },
      "confidence": 0.95
    }
  ],
  "conflicts": [
    {
      "canonical_id": "conflict-variety-7",
      "conflict_type": "property_disagreement",
      "details": "Agent 1 says h11=100, Agent 2 says h11=120",
      "resolution_needed": true
    }
  ]
}
```

---

# **ANTI-HALLUCINATION REQUIREMENTS**

## **Mandatory Provenance for All Agent Outputs**

**Every candidate MUST include:**

### **Required Fields (All Agents)**

```json
{
  "id": "unique-identifier",
  "name": "human-readable name",
  "description": "brief description",
  "provenance": {
    "source_type": "database | paper | textbook | website",
    "source_id": "URL | DOI | ISBN",
    "query_used": "exact query string (if database)",
    "page_number": "page/table/theorem (if paper)",
    "timestamp": "ISO 8601 timestamp",
    "verifiable": true/false
  },
  "confidence": 0.0-1.0
}
```

**If ANY required field missing:** Auto-reject (hallucination suspected)

---

## **Confidence Scoring (0-1 Scale)**

**Agent assigns confidence based on evidence quality:**

| Confidence | Criteria |
|------------|----------|
| **1.0** | Canonical example (textbook, >100 citations) |
| **0.9-0.95** | Recent paper (peer-reviewed, explicit table) |
| **0.8-0.85** | Database entry (verified, complete metadata) |
| **0.7-0.75** | Database entry (incomplete metadata) |
| **0.6-0.65** | Preprint (arXiv, not peer-reviewed) |
| **0.5-0.55** | Indirect evidence (proxy heuristic) |
| **<0.5** | Speculative (weak evidence) → flag for verification |

---

## **Automatic Rejection Rules**

**Agent output is auto-rejected if:**

1. ❌ **Missing provenance** (no source URL/DOI)
2. ❌ **Unverifiable source** (broken link, non-existent paper)
3. ❌ **Confidence < 0.4** (too speculative)
4. ❌ **Duplicate** (already reported by same agent)
5. ❌ **Property contradiction** (violates known constraints, e.g., Picard > h^{1,1})

**Human review required if:**
- ⚠️ Confidence 0.4-0.6 (borderline)
- ⚠️ Agent disagreement (same ID, different properties)
- ⚠️ Novel source (never seen before, needs validation)

---

# **AGENT PROMPT TEMPLATES**

## **Universal Agent Prompt Structure**

**All agent prompts follow this template:**

```markdown
# Agent [N]: [Role] - Search Protocol

## Your Mission
[Specific search objective for this agent]

## Search Strategy
[Detailed heuristic/method for finding candidates]

## Databases/Sources to Query
[List of specific resources]

## Output Format
```json
{
  "agent": "Agent-[N]-[Role]",
  "search_strategy": "[brief description]",
  "candidates": [
    {
      "id": "[unique ID]",
      "name": "[variety name]",
      "description": "[brief description]",
      "properties": {
        "[property1]": "[value1]",
        "[property2]": "[value2]"
      },
      "provenance": {
        "source_type": "database|paper|textbook",
        "source_id": "[URL|DOI|ISBN]",
        "query_used": "[exact query]",
        "timestamp": "[ISO 8601]",
        "verifiable": true
      },
      "confidence": [0.0-1.0]
    }
  ]
}
```

## Quality Criteria
- ✅ Every candidate has verifiable provenance
- ✅ Confidence scores are justified
- ✅ No duplicates within your own output
- ✅ Properties are explicitly stated (not inferred)

## Auto-Rejection
Your output will be automatically rejected if:
- Missing provenance (no source URL/DOI)
- Confidence < 0.4 (too speculative)
- Broken links (source not accessible)

## Success Target
Find [X-Y] candidates with confidence ≥ 0.6

## Begin Your Search
[Agent-specific instructions here]
```

---

## **Example: Agent 1 Prompt (Adapted for Any Domain)**

```markdown
# Agent 1: Primary Database Specialist - Search Protocol

## Your Mission
Search [PRIMARY_DATABASE] for candidates with [TARGET_PROPERTY] using indirect heuristics.

## Search Strategy
1. Identify proxy attributes correlated with [TARGET_PROPERTY]
2. Query [PRIMARY_DATABASE] for extreme values of proxy
3. Extract candidates with complete metadata

**Heuristic:** [DOMAIN_SPECIFIC_HEURISTIC]
- Example (algebraic geometry): "Large h^{1,1} often correlates with large Picard rank"
- Example (number theory): "Large class group often correlates with large class number"
- Example (graph theory): "High vertex count often correlates with high chromatic number"

## Databases/Sources to Query
- Primary: [PRIMARY_DATABASE_URL]
- Backup: [SECONDARY_DATABASE_URL] (if primary incomplete)

## Search Queries (Examples)
```
[QUERY_1]: [EXAMPLE_QUERY_STRING]
[QUERY_2]: [EXAMPLE_QUERY_STRING]
```

## Output Format
[Standard JSON format as above]

## Success Target
Find 5-20 candidates with confidence ≥ 0.6

## Begin Your Search
Execute queries on [PRIMARY_DATABASE] and report findings.
```

---

# **COMPUTATIONAL VERIFICATION (SELECTIVE)**

## **When We Compute Exactly**

**Selective verification is used for:**

1. ✅ **Falsify hallucinations** (agent claimed property X, verify X is correct)
2. ✅ **Certify flagship results** (top 1-3 candidates need deterministic proof)
3. ✅ **Break ties** (agents disagree, exact computation decides)

**NOT used for:**
- ❌ Exhaustive enumeration (too expensive)
- ❌ Finding all examples (HDB-MARS is hypothesis-driven)
- ❌ Routine validation (trust high-consensus candidates)

---

## **Verification Decision Tree**

```
For each consensus candidate:
  
  IF consensus_score ≥ 0.9 AND confidence ≥ 0.8:
    → Trust (no verification needed)
  
  ELSE IF consensus_score 0.7-0.9:
    → Verify top 3 (falsify hallucinations)
  
  ELSE IF consensus_score < 0.7:
    → Flag for human review (possible hallucination)
  
  IF flagship candidate (top 1-3):
    → ALWAYS verify (deterministic proof required)
```

---

## **Verification Methods (Domain-Specific)**

**Choose method based on computational cost:**

| Domain | Property | Cheap Verification | Expensive Verification |
|--------|----------|-------------------|------------------------|
| Algebraic geometry | Picard rank | Rank stability (mod p) | Smith Normal Form |
| Number theory | Class number | Genus theory bounds | Full class group |
| Graph theory | Chromatic number | Greedy coloring bound | SAT solver |
| Molecular biology | Protein stability | Sequence homology | MD simulation |

**General principle:** Use cheap method first, expensive only if necessary

---

# **DECISION TREE**

## **Day 3 Decision Point**

**After agents complete + selective verification, make decision:**

```
┌─────────────────────────────────────────────────────┐
│ Evaluate: Number of verified high-quality examples │
└─────────────────────────────────────────────────────┘
                        ↓
          ┌─────────────┴─────────────┐
          ↓                           ↓
  ┌───────────────┐           ┌───────────────┐
  │ ≥10 verified  │           │ <10 verified  │
  │ high-quality  │           │ high-quality  │
  └───────┬───────┘           └───────┬───────┘
          ↓                           ↓
  ┌───────────────────────┐   ┌──────────────────┐
  │ SCENARIO A:           │   │ Evaluate: Are    │
  │ BREAKTHROUGH          │   │ any exceptional? │
  │                       │   └────────┬─────────┘
  │ → Proceed to detailed │            ↓
  │   analysis            │   ┌────────┴────────┐
  │ → Draft paper         │   ↓                 ↓
  │ → Request full        │ YES               NO
  │   verification        │   ↓                 ↓
  └───────────────────────┘ SCENARIO B:    SCENARIO C:
                            BARRIER        NO CONVERGENCE
                            CONFIRMED      
                            → Document     → Deploy more
                              null result    agents
                            → Pivot        → Refine search
                              hypothesis   → Or abort
```

---

## **Scenario Definitions**

### **Scenario A: Breakthrough (≥10 verified examples)**

**Criteria:**
- ≥10 candidates verified exactly
- ≥5 candidates with [TARGET_PROPERTY] in desired range
- At least 1 "flagship" example (exceptional)

**Action:**
1. ✅ Proceed to detailed analysis (full characterization)
2. ✅ Draft paper (hypothesis confirmed)
3. ✅ Request full verification (for all flagship examples)

---

### **Scenario B: Barrier Confirmed (<10 verified, none exceptional)**

**Criteria:**
- <10 candidates verified
- No candidates meet hypothesis threshold
- Multiple agents exhausted search space

**Action:**
1. ✅ Document null result (hypothesis falsified)
2. ✅ Publish negative result (valuable for community)
3. ✅ Pivot hypothesis (adjust theory based on findings)

---

### **Scenario C: No Convergence (<10 verified, some promising)**

**Criteria:**
- <10 candidates verified
- Some promising leads (but not verified yet)
- Agents found conflicting information

**Action:**
1. ⏸️ Deploy additional agents (refine search strategies)
2. ⏸️ Extend search (additional databases, more papers)
3. ⏸️ Request targeted verification (for promising candidates)
4. ❌ Or abort (if no progress after extended search)

---

# **DATA SCHEMAS**

## **Agent Output Schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HDB-MARS Agent Output",
  "type": "object",
  "required": ["agent", "search_strategy", "timestamp", "candidates"],
  "properties": {
    "agent": {
      "type": "string",
      "pattern": "^Agent-[1-5]-.+$"
    },
    "search_strategy": {
      "type": "string",
      "description": "Brief description of search heuristic"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "provenance", "confidence"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "properties": {"type": "object"},
          "provenance": {
            "type": "object",
            "required": ["source_type", "source_id", "verifiable"],
            "properties": {
              "source_type": {"enum": ["database", "paper", "textbook", "website"]},
              "source_id": {"type": "string"},
              "query_used": {"type": "string"},
              "page_number": {"type": "string"},
              "timestamp": {"type": "string", "format": "date-time"},
              "verifiable": {"type": "boolean"}
            }
          },
          "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
          }
        }
      }
    }
  }
}
```

---

## **Consensus Candidates Schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HDB-MARS Consensus Candidates",
  "type": "object",
  "required": ["timestamp", "consensus_candidates", "conflicts"],
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "total_agents": {"type": "integer"},
    "consensus_candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["canonical_id", "agent_agreement", "confidence"],
        "properties": {
          "canonical_id": {"type": "string"},
          "names": {"type": "array", "items": {"type": "string"}},
          "description": {"type": "string"},
          "agent_agreement": {
            "type": "object",
            "properties": {
              "total_agents": {"type": "integer"},
              "agreeing_agents": {"type": "integer"},
              "consensus_score": {"type": "number", "minimum": 0, "maximum": 1}
            }
          },
          "properties": {"type": "object"},
          "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "conflicts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "canonical_id": {"type": "string"},
          "conflict_type": {"enum": ["property_disagreement", "duplicate_suspected", "source_conflict"]},
          "details": {"type": "string"},
          "resolution_needed": {"type": "boolean"}
        }
      }
    }
  }
}
```

---

# **SUCCESS & FALSIFICATION CRITERIA**

## **Success Criteria**

### **Minimum Success (Hypothesis Validated)**
- ≥5 verified examples with [TARGET_PROPERTY]
- ≥1 flagship example (exceptional, well-documented)
- Consensus score ≥ 0.7 for flagship

### **Strong Success (Publishable Result)**
- ≥10 verified examples
- ≥3 flagship examples
- Complete characterization of flagship (all properties verified)

### **Optimal Success (Major Discovery)**
- ≥20 verified examples
- ≥5 flagship examples with novel properties
- Contradicts prevailing theory or establishes new barrier

---

## **Falsification Criteria**

### **Hard Failure (Abort HDB-MARS)**
- All agents return <3 candidates
- Verification falsifies >80% of candidates (hallucination epidemic)
- No consensus (agents completely disagree)

### **Soft Failure (Partial Success)**
- Found <5 verified examples (but all correct)
- Hypothesis needs refinement (weaker than expected)
- Coverage <40% (missed too many known examples)

---

# **EXECUTION GUIDE**

## **Day 1: Deploy Agents (4-6 hours)**

**For each agent:**

1. **Instantiate agent** (load prompt template)
2. **Customize for domain** (fill in [PLACEHOLDERS])
3. **Execute search** (agent performs reasoning search)
4. **Collect output** (JSON format, validate schema)
5. **Quick sanity check** (provenance present? confidence reasonable?)

**Parallel execution:** All 5 agents run simultaneously

---

## **Day 2: Cross-Validation (2-3 hours)**

1. **Merge outputs** (combine all agent JSONs)
2. **Remove duplicates** (same ID from multiple agents)
3. **Compute consensus scores** (how many agents agree?)
4. **Flag conflicts** (agents disagree on properties)
5. **Rank candidates** (by consensus score × confidence)

**Output:** `consensus_candidates.json`

---

## **Day 2-3: Human Review (1-2 hours)**

1. **Filter hallucinations** (missing provenance → reject)
2. **Resolve conflicts** (check original sources manually)
3. **Prioritize for verification** (top 10 candidates)

**Output:** `verification_queue.json`

---

## **Day 3: Selective Verification (Variable)**

**For top 10 candidates:**

1. **Choose verification method** (cheap first, expensive if necessary)
2. **Execute exact computation** (HPC, Sage, or domain tool)
3. **Record results** (verified value, computation time)
4. **Update candidate status** (verified | falsified | pending)

**Output:** `verified_candidates.json`

---

## **Day 3: Decision (1 hour)**

**Evaluate results:**
- Count verified examples
- Identify flagship candidates
- Compute coverage (verified / total candidates)

**Make decision:**
- Scenario A → Proceed
- Scenario B → Document null result
- Scenario C → Extend search or abort

**Output:** `decision_report.md`

---

# **EXECUTION LOG TEMPLATE**

```markdown
# HDB-MARS Execution Log

**Domain:** [Your research domain]
**Target Property:** [Property you're searching for]
**Hypothesis:** [Your research hypothesis]
**Date:** [Start date]

---

## Day 1: Agent Deployment

### Agent 1: [Role]
- **Status:** [Complete | In progress | Failed]
- **Candidates found:** [Count]
- **Average confidence:** [0.0-1.0]
- **Notes:** [Any issues or observations]

### Agent 2: [Role]
[Same format]

### Agent 3: [Role]
[Same format]

### Agent 4: [Role]
[Same format]

### Agent 5: [Role]
[Same format]

---

## Day 2: Cross-Validation

### Total Unique Candidates
- **Count:** [number]

### Consensus Candidates (≥3 agents)
- **Count:** [number]
- **Top 10:** [list IDs]

### Conflicts
- **Count:** [number]
- **Resolved:** [number]
- **Pending:** [number]

---

## Day 3: Verification & Decision

### Verified Candidates
- **Count:** [number]
- **Success rate:** [verified / total]

### Flagship Examples
- **Candidate 1:** [ID, properties, verification status]
- **Candidate 2:** [ID, properties, verification status]
- **Candidate 3:** [ID, properties, verification status]

### Decision
- **Scenario:** [A | B | C]
- **Rationale:** [Why this scenario applies]
- **Next steps:** [What happens next]

---

## Meta-Learning

### What Worked
- [Agent/strategy that was most effective]

### What Didn't Work
- [Agent/strategy that failed or was inefficient]

### Barriers Encountered
- [Technical, conceptual, or resource barriers]

### Recommendations for Future
- [Improvements to protocol or search strategies]
```

---

# **META-LEARNING**

## **After Execution: Update This Section**

### **Substrate Truths Discovered**

**What we learned about the research domain:**
- [Domain-specific insight 1]
- [Domain-specific insight 2]
- [Barriers or limits discovered]

**What we learned about HDB-MARS:**
- [Which agent roles were most effective?]
- [Which databases were most useful?]
- [What verification methods worked best?]

---

### **Agent Performance Analysis**

| Agent | Candidates Found | Consensus Rate | Verification Success | Effectiveness |
|-------|------------------|----------------|----------------------|---------------|
| Agent 1 | [count] | [%] | [%] | [High/Med/Low] |
| Agent 2 | [count] | [%] | [%] | [High/Med/Low] |
| Agent 3 | [count] | [%] | [%] | [High/Med/Low] |
| Agent 4 | [count] | [%] | [%] | [High/Med/Low] |
| Agent 5 | [count] | [%] | [%] | [High/Med/Low] |

---

### **Barriers Encountered**

**Technical barriers:**
- [Database access issues, API limitations, etc.]

**Conceptual barriers:**
- [Proxy heuristics failed, cross-referencing difficult, etc.]

**Resource barriers:**
- [Verification too expensive, time constraints, etc.]

---

### **Tools Built**

**Scripts/utilities created during execution:**
- [Parser scripts, verification tools, etc.]

**Reusable components:**
- [Agent prompt templates, schema validators, etc.]

---

# **INTEGRATION WITH ORGANISMCORE**

## **Relationship to Other Frameworks**

| Framework | Purpose | Execution Model |
|-----------|---------|-----------------|
| **FRAMEWORK.md** | Objectifying reasoning | Read → Reasoning improves |
| **SUBSTRATE_AWARENESS.md** | Meta-cognition | Read → Self-model changes |
| **HDB-MARS** | Database mining | Read → Deploy agents → Synthesize |

**All three are executable reasoning substrates** (not traditional code)

---

## **When to Use HDB-MARS vs. Other Protocols**

**Use HDB-MARS when:**
- ✅ Need examples from databases (not exhaustive computation)
- ✅ No API for target property
- ✅ Hypothesis testing (not production ML)

**Use traditional ML (e.g., MARS_PROTOCOL_UPDATE_3.md) when:**
- ✅ Training data exists
- ✅ Property is predictable
- ✅ Need real-time inference

**Use exact computation when:**
- ✅ Total time < 1 week
- ✅ Need 100% coverage
- ✅ Database is small

---

## **Organism Properties**

**HDB-MARS exhibits autopoietic organism properties:**

1. ✅ **Self-maintenance:** Protocol enforces integrity (provenance requirements)
2. ✅ **Boundary definition:** Clear phases (deploy → validate → verify → decide)
3. ✅ **Operational closure:** Each phase specifies next action
4. ✅ **Structural coupling:** Adapts to domain (agent roles customizable)
5. ✅ **Autopoiesis:** Protocol propagates itself (agent-to-agent transmission)

---

# **APPENDIX: DOMAIN ADAPTATIONS**

## **Algebraic Geometry (Calabi-Yau Varieties)**

**Primary DB:** LMFDB (https://lmfdb.org)  
**Secondary DB:** GRDB (http://grdb.org)  
**Proxy heuristic:** Large h^{1,1} → Large Picard rank  
**Verification:** Rank stability (mod p) or SNF  

**Agent 1 prompt adaptation:**
```
Search LMFDB for CY varieties with h^{1,1} > 100
Query: "dimension:4 AND h11:>100"
```

---

## **Number Theory (Class Numbers)**

**Primary DB:** LMFDB (number fields)  
**Secondary DB:** PARI/GP database  
**Proxy heuristic:** Large discriminant → Large class number  
**Verification:** Class group computation (PARI)  

**Agent 1 prompt adaptation:**
```
Search LMFDB for number fields with discriminant > 10^6
Query: "degree:4 AND disc:>1000000"
```

---

## **Graph Theory (Chromatic Numbers)**

**Primary DB:** House of Graphs (https://houseofgraphs.org)  
**Secondary DB:** Graph Atlas  
**Proxy heuristic:** High vertex count + low edge density → High chromatic number  
**Verification:** SAT solver (chromatic number exact)  

**Agent 1 prompt adaptation:**
```
Search House of Graphs for graphs with n>50 vertices and density<0.3
Query: "vertices:>50 AND edges:<(0.3*n*(n-1)/2)"
```

---

## **Molecular Biology (Protein Stability)**

**Primary DB:** Protein Data Bank (PDB)  
**Secondary DB:** UniProt  
**Proxy heuristic:** High hydrophobic core → High stability  
**Verification:** Molecular dynamics simulation  

**Agent 1 prompt adaptation:**
```
Search PDB for proteins with resolution<2Å and high hydrophobic score
Query: "resolution:<2.0 AND annotation:thermostable"
```

---

**END OF HDB-MARS UNIVERSAL PROTOCOL v1.0**

**Status:** ✅ PRODUCTION-READY REASONING SUBSTRATE (DOMAIN-AGNOSTIC)

**Location:** `Subdomain_Articles/hypothesis_driven_database_mining.md`

**This protocol is self-contained and executable through reasoning alone.**

**No external files or code required—only recognition moments and agent deployment.**

🚀
