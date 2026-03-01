"""
Fetch TCGA-BLCA clinical data
via cBioPortal REST API.
No login required.
No browser required.
"""

import requests
import pandas as pd
import os

OUT_DIR  = "./blca_false_attractor/"
OUT_FILE = os.path.join(
    OUT_DIR, "TCGA_BLCA_clinical_cbio.tsv"
)
os.makedirs(OUT_DIR, exist_ok=True)

BASE = "https://www.cbioportal.org/api"

# Try both study IDs
STUDY_IDS = [
    "blca_tcga_pub2017",
    "blca_tcga_pan_can_atlas_2018",
    "blca_tcga",
]

def fetch_clinical(study_id):
    print(f"Trying study: {study_id}")

    # Get all sample clinical data
    url = (
        f"{BASE}/studies/{study_id}"
        f"/clinical-data"
        f"?clinicalDataType=SAMPLE"
        f"&pageSize=100000"
    )
    print(f"  URL: {url}")
    r = requests.get(url, timeout=60)
    print(f"  Status: {r.status_code}")

    if r.status_code != 200:
        return None

    data = r.json()
    print(f"  Records: {len(data)}")
    if not data:
        return None

    # Pivot to wide format
    rows = {}
    for rec in data:
        sid = rec.get("sampleId","")
        key = rec.get("clinicalAttributeId","")
        val = rec.get("value","")
        if sid not in rows:
            rows[sid] = {"SAMPLE_ID": sid}
        rows[sid][key] = val

    df = pd.DataFrame(list(rows.values()))
    print(f"  Samples: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    return df


def fetch_clinical_patient(study_id):
    """Also get patient-level data
    (OS is usually patient-level)."""
    print(f"  Fetching patient data: {study_id}")
    url = (
        f"{BASE}/studies/{study_id}"
        f"/clinical-data"
        f"?clinicalDataType=PATIENT"
        f"&pageSize=100000"
    )
    r = requests.get(url, timeout=60)
    print(f"  Status: {r.status_code}")
    if r.status_code != 200:
        return None

    data = r.json()
    if not data:
        return None

    rows = {}
    for rec in data:
        pid = rec.get("patientId","")
        key = rec.get("clinicalAttributeId","")
        val = rec.get("value","")
        if pid not in rows:
            rows[pid] = {"PATIENT_ID": pid}
        rows[pid][key] = val

    df = pd.DataFrame(list(rows.values()))
    print(f"  Patients: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    return df


def main():
    for study_id in STUDY_IDS:
        print(f"\n{'='*50}")
        print(f"Study: {study_id}")

        # Sample data
        df_s = fetch_clinical(study_id)

        # Patient data (has OS)
        df_p = fetch_clinical_patient(study_id)

        if df_s is None and df_p is None:
            print(f"  Both failed — next study")
            continue

        # Merge if both available
        if df_p is not None and df_s is not None:
            # Add patient ID to sample df
            # via sample→patient map
            map_url = (
                f"{BASE}/studies/{study_id}"
                f"/samples?pageSize=100000"
            )
            mr = requests.get(
                map_url, timeout=60
            )
            if mr.status_code == 200:
                mdata = mr.json()
                pid_map = {
                    m["sampleId"]: m["patientId"]
                    for m in mdata
                }
                df_s["PATIENT_ID"] = df_s[
                    "SAMPLE_ID"
                ].map(pid_map)
                df_merged = df_s.merge(
                    df_p,
                    on="PATIENT_ID",
                    how="left",
                    suffixes=("","_pat"),
                )
            else:
                df_merged = df_s
        elif df_p is not None:
            df_merged = df_p
        else:
            df_merged = df_s

        # Show survival columns
        surv_cols = [
            c for c in df_merged.columns
            if any(
                x in c.upper()
                for x in [
                    "OS","SURVIVAL","VITAL",
                    "DEATH","MONTHS","DAYS",
                    "STATUS","DFS",
                ]
            )
        ]
        print(f"\n  Survival columns found:")
        for c in surv_cols:
            ex = df_merged[c].dropna(
            ).head(3).tolist()
            print(f"    {c}: {ex}")

        # Save
        df_merged.to_csv(
            OUT_FILE, sep="\t", index=False
        )
        print(f"\n  Saved: {OUT_FILE}")
        print(f"  Shape: {df_merged.shape}")
        print(f"\n  First 3 rows:")
        print(df_merged[
            ["SAMPLE_ID"] + surv_cols[:4]
        ].head(3).to_string())

        print(f"\n  SUCCESS: {study_id}")
        return

    print("\n  ALL STUDY IDs FAILED")
    print("  Try GDC portal manually:")
    print("  https://portal.gdc.cancer.gov/")
    print("  Project: TCGA-BLCA")
    print("  Files: clinical.tsv")


if __name__ == "__main__":
    main()
