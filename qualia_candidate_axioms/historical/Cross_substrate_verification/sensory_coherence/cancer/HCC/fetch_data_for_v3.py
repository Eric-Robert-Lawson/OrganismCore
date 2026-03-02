"""
TCGA-LIHC clinical + mutation data fetcher
Run this ONCE before hcc_false_attractor_v3.py

Fetches from cBioPortal public REST API
(no authentication required)

Writes three files:
  ./hcc_false_attractor/tcga_lihc/
    TCGA-LIHC.survival.tsv.gz
    TCGA-LIHC.pheno.tsv.gz
    TCGA-LIHC.mutations.tsv.gz

OrganismCore | 2026-03-02
"""

import os
import gzip
import json
import requests

# ============================================================
TCGA_DIR  = "./hcc_false_attractor/tcga_lihc/"
CBIO_BASE = "https://www.cbioportal.org/api"
STUDY_ID  = "lihc_tcga"
os.makedirs(TCGA_DIR, exist_ok=True)

SURV_FILE  = os.path.join(TCGA_DIR, "TCGA-LIHC.survival.tsv.gz")
PHENO_FILE = os.path.join(TCGA_DIR, "TCGA-LIHC.pheno.tsv.gz")
MUT_FILE   = os.path.join(TCGA_DIR, "TCGA-LIHC.mutations.tsv.gz")

HEADERS = {
    "Accept":       "application/json",
    "Content-Type": "application/json",
    "User-Agent":   "OrganismCore/1.0",
}

HCC_MUT_GENES = [
    "CTNNB1","TP53","ARID1A","AXIN1",
    "NFE2L2","RB1","PIK3CA","PTEN",
    "TSC1","TSC2","ARID2","RNF43",
    "KMT2D","SETD2","HNF1A","TERT",
    "BAP1","CDKN2A","ALB","IDH1",
    "IDH2","SMARCA4","ELF3","MET",
]

# ============================================================

def get(url, label="", timeout=60):
    print(f"  GET {label}")
    print(f"      {url}")
    try:
        r = requests.get(
            url, headers=HEADERS, timeout=timeout
        )
        print(f"      HTTP {r.status_code} "
              f"({len(r.content):,} bytes)")
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"      ERROR: {e}")
        return None

def post(url, payload, label="", timeout=120):
    print(f"  POST {label}")
    print(f"       {url}")
    try:
        r = requests.post(
            url, json=payload,
            headers=HEADERS, timeout=timeout
        )
        print(f"       HTTP {r.status_code} "
              f"({len(r.content):,} bytes)")
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"       ERROR: {e}")
        return None

def write_gz(path, lines):
    content = "\n".join(lines)
    with gzip.open(path, "wt",
                   encoding="utf-8") as f:
        f.write(content)
    sz = os.path.getsize(path)
    print(f"  Saved: {path} ({sz:,} bytes)")
    return sz

# ============================================================
# STEP 1: Get all samples for TCGA-LIHC
# ============================================================

print("=" * 60)
print("STEP 1: Fetch sample list")
print("=" * 60)

samples_data = get(
    f"{CBIO_BASE}/studies/{STUDY_ID}/samples"
    f"?pageSize=10000",
    label="TCGA-LIHC samples",
)

if not samples_data:
    print("FATAL: Cannot fetch sample list")
    print("Check internet connection and that")
    print("https://www.cbioportal.org is accessible")
    exit(1)

# Build patient→sample and sample→patient maps
sample_ids   = [s["sampleId"]  for s in samples_data]
patient_ids  = [s["patientId"] for s in samples_data]
pid_to_sids  = {}
sid_to_pid   = {}
for s in samples_data:
    sid = s["sampleId"]
    pid = s["patientId"]
    sid_to_pid[sid] = pid
    if pid not in pid_to_sids:
        pid_to_sids[pid] = []
    pid_to_sids[pid].append(sid)

print(f"  Total samples: {len(sample_ids)}")
print(f"  Total patients: {len(pid_to_sids)}")
print(f"  Sample IDs[0:3]: {sample_ids[:3]}")

# ============================================================
# STEP 2: Fetch patient clinical data
# (OS_MONTHS, OS_STATUS, STAGE, GRADE, AGE, SEX)
# ============================================================

print("")
print("=" * 60)
print("STEP 2: Fetch patient clinical data")
print("=" * 60)

patient_clin = get(
    f"{CBIO_BASE}/studies/{STUDY_ID}"
    f"/clinical-data?clinicalDataType=PATIENT"
    f"&pageSize=100000",
    label="patient clinical",
    timeout=120,
)

# Pivot: patientId → {attributeId: value}
pat_data = {}
if patient_clin:
    print(f"  Records: {len(patient_clin)}")
    for row in patient_clin:
        pid  = row.get("patientId","")
        attr = row.get("clinicalAttributeId","")
        val  = row.get("value","")
        if pid not in pat_data:
            pat_data[pid] = {}
        pat_data[pid][attr] = val
    print(f"  Patients with data: {len(pat_data)}")
    # Show available attributes
    attrs_seen = set()
    for d in pat_data.values():
        attrs_seen.update(d.keys())
    print(f"  Attributes: {sorted(attrs_seen)}")
else:
    print("  WARNING: No patient clinical data")

# ============================================================
# STEP 3: Write survival TSV
# Format: sample  OS  OS.time
# ============================================================

print("")
print("=" * 60)
print("STEP 3: Write survival file")
print("=" * 60)

if not os.path.exists(SURV_FILE):
    surv_lines = ["sample\tOS\tOS.time"]
    n_with_surv = 0

    for sid in sample_ids:
        pid  = sid_to_pid.get(sid, "")
        pd_  = pat_data.get(pid, {})

        # OS status
        os_s = pd_.get("OS_STATUS","")
        if "DECEASED" in os_s.upper():
            ev = "1"
        elif "LIVING" in os_s.upper():
            ev = "0"
        elif os_s in ["0","1"]:
            ev = os_s
        else:
            ev = ""

        # OS time (months)
        os_t = pd_.get("OS_MONTHS","")
        # Some studies use different keys
        if not os_t:
            os_t = pd_.get("SURVIVAL_TIME","")
        if not os_t:
            os_t = pd_.get("OS","")

        surv_lines.append(
            f"{sid}\t{ev}\t{os_t}"
        )
        if ev and os_t:
            n_with_surv += 1

    print(f"  Samples with OS data: {n_with_surv}")
    write_gz(SURV_FILE, surv_lines)
else:
    sz = os.path.getsize(SURV_FILE)
    print(f"  Already present: {SURV_FILE} ({sz:,} bytes)")

# ============================================================
# STEP 4: Write full phenotype TSV
# ============================================================

print("")
print("=" * 60)
print("STEP 4: Write phenotype file")
print("=" * 60)

if not os.path.exists(PHENO_FILE):
    # Collect all attribute names
    all_attrs = set()
    for d in pat_data.values():
        all_attrs.update(d.keys())
    all_attrs = sorted(all_attrs)

    hdr = ["sample","patientId"] + all_attrs
    pheno_lines = ["\t".join(hdr)]

    for sid in sample_ids:
        pid = sid_to_pid.get(sid,"")
        pd_ = pat_data.get(pid,{})
        row = (
            [sid, pid]
            + [pd_.get(a,"") for a in all_attrs]
        )
        pheno_lines.append("\t".join(row))

    write_gz(PHENO_FILE, pheno_lines)
else:
    sz = os.path.getsize(PHENO_FILE)
    print(f"  Already present: {PHENO_FILE} ({sz:,} bytes)")

# ============================================================
# STEP 5: Fetch mutations
# POST to mutations/fetch endpoint
# ============================================================

print("")
print("=" * 60)
print("STEP 5: Fetch somatic mutations")
print("=" * 60)

if not os.path.exists(MUT_FILE):
    # Identify the mutation molecular profile
    profiles_data = get(
        f"{CBIO_BASE}/studies/{STUDY_ID}"
        f"/molecular-profiles",
        label="molecular profiles",
    )

    mut_profile = None
    if profiles_data:
        for p in profiles_data:
            pid_  = p.get(
                "molecularProfileId",""
            )
            ptype = p.get(
                "molecularAlterationType",""
            )
            if "MUTATION" in ptype.upper():
                mut_profile = pid_
                print(f"  Mutation profile: "
                      f"{mut_profile}")
                break

    if mut_profile is None:
        # Common fallback name
        mut_profile = f"{STUDY_ID}_mutations"
        print(f"  Using default profile: "
              f"{mut_profile}")

    # Fetch mutations for HCC genes
    # cBioPortal accepts up to ~500 samples
    # per request; batch if needed
    BATCH = 500
    all_muts = []

    for i in range(0, len(sample_ids), BATCH):
        batch = sample_ids[i:i+BATCH]
        payload = {
            "sampleIds":       batch,
            "hugoGeneSymbols": HCC_MUT_GENES,
        }
        url_m = (
            f"{CBIO_BASE}/molecular-profiles"
            f"/{mut_profile}/mutations/fetch"
            f"?projection=SUMMARY"
        )
        result = post(
            url_m, payload,
            label=f"mutations batch "
                  f"{i//BATCH+1}/"
                  f"{(len(sample_ids)-1)//BATCH+1}",
        )
        if result:
            all_muts.extend(result)
            print(f"  Batch {i//BATCH+1}: "
                  f"n={len(result)} mutations")

    print(f"  Total mutations: {len(all_muts)}")

    if all_muts:
        # Write MAF-like TSV
        mut_lines = [
            "Hugo_Symbol\t"
            "Tumor_Sample_Barcode\t"
            "Variant_Classification\t"
            "Protein_Change\t"
            "Chromosome\t"
            "Start_Position\t"
            "Reference_Allele\t"
            "Tumor_Seq_Allele2"
        ]
        for m in all_muts:
            gene   = (
                m.get("gene",{})
                 .get("hugoGeneSymbol","")
                if isinstance(
                    m.get("gene"), dict
                )
                else m.get("hugoGeneSymbol",
                           m.get("gene",""))
            )
            sid_m  = m.get("sampleId","")
            vclass = m.get(
                "mutationType",
                m.get("variantClassification","")
            )
            pchng  = m.get(
                "proteinChange",
                m.get("aminoAcidChange","")
            )
            chrom  = m.get(
                "chr",
                m.get("chromosome","")
            )
            start  = str(m.get(
                "startPosition",
                m.get("startPos","")
            ))
            ref    = m.get(
                "referenceAllele","")
            alt    = m.get(
                "variantAllele",
                m.get("tumorSeqAllele2","")
            )
            mut_lines.append(
                f"{gene}\t{sid_m}\t"
                f"{vclass}\t{pchng}\t"
                f"{chrom}\t{start}\t"
                f"{ref}\t{alt}"
            )
        write_gz(MUT_FILE, mut_lines)
    else:
        print("  No mutations returned — "
              "writing empty placeholder")
        write_gz(MUT_FILE, [
            "Hugo_Symbol\t"
            "Tumor_Sample_Barcode\t"
            "Variant_Classification"
        ])
else:
    sz = os.path.getsize(MUT_FILE)
    print(f"  Already present: {MUT_FILE} "
          f"({sz:,} bytes)")

# ============================================================
# STEP 6: Verify all three files
# ============================================================

print("")
print("=" * 60)
print("STEP 6: Verification")
print("=" * 60)

all_ok = True
for label, path in [
    ("Survival",  SURV_FILE),
    ("Phenotype", PHENO_FILE),
    ("Mutations", MUT_FILE),
]:
    if os.path.exists(path):
        sz = os.path.getsize(path)
        # Quick content check
        try:
            with gzip.open(
                path, "rt", encoding="utf-8"
            ) as f:
                first_line = f.readline()
                n_lines    = (
                    sum(1 for _ in f) + 1
                )
            print(f"  {label}: ✓ "
                  f"{sz:,} bytes "
                  f"{n_lines} lines")
            print(f"    Header: "
                  f"{first_line.strip()[:80]}")
        except Exception as e:
            print(f"  {label}: ✓ present "
                  f"but read error: {e}")
    else:
        print(f"  {label}: ✗ NOT FOUND")
        all_ok = False

print("")
if all_ok:
    print("All files present.")
    print("Run hcc_false_attractor_v3.py now.")
else:
    print("Some files missing.")
    print("If cBioPortal is unreachable,")
    print("manual download instructions:")
    print("")
    print("  1. Go to https://www.cbioportal.org")
    print("  2. Search: Liver Hepatocellular")
    print("     Carcinoma (TCGA, PanCancer Atlas)")
    print("  3. Download → Clinical Data")
    print(f"     Save to: {PHENO_FILE}")
    print("  4. Download → Mutations")
    print(f"     Save to: {MUT_FILE}")
    print("  5. Survival is inside the clinical")
    print("     data file — the parser will")
    print("     extract it automatically.")
