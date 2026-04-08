"""IRCC Immigration open data constants and dataset registry.

Every (dataset_key, breakdown_key, lang) combination maps to an exact IRCC download URL.
Access: DATASET_REGISTRY["pr"]["country"]["en"] -> full URL
"""

BASE_URL = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/"
CACHE_TTL = 86400  # 24 hours — IRCC files update monthly
RATE_GROUP = "ircc"
RATE_LIMIT = 2.0  # Static file server — be conservative

# CKAN dataset IDs for provenance
CKAN_ID_PR = "f7e5498e-0ad8-4417-85c9-9b8aff9b9eda"
CKAN_ID_STUDY = "90115b00-f9b8-49e8-afa3-b4cff8facaee"
CKAN_ID_WORK = "360024f2-17e9-4558-bfc1-3616485d65b9"  # shared by IMP and TFWP
CKAN_ID_EE_ADMISSIONS = "52e4b14b-597a-4ecf-a184-23a6e69b0d57"
CKAN_ID_EE_INVITED = "593e9165-c6ce-4f9b-b519-03d315f92cd4"
CKAN_ID_TR_TO_PR = "1b026aab-edb3-4d5d-8231-270a09ed4e82"
CKAN_ID_ASYLUM = "b6cbcf4d-f763-4924-a2fb-8cc4a06e3de4"
CKAN_ID_OPS = "9b34e712-513f-44e9-babf-9df4f7256550"
CKAN_ID_AFGHAN = "53520aa7-f2a3-4593-952e-574432a4acd0"
CKAN_ID_ADHOC_PR = "ad975a26-df23-456a-8ada-756191a23695"

# CKAN IDs by dataset key for provenance lookup
CKAN_IDS: dict[str, str] = {
    "pr": CKAN_ID_PR,
    "study": CKAN_ID_STUDY,
    "work_imp": CKAN_ID_WORK,
    "work_tfwp": CKAN_ID_WORK,
    "ee_admissions": CKAN_ID_EE_ADMISSIONS,
    "ee_invited": CKAN_ID_EE_INVITED,
    "tr_to_pr": CKAN_ID_TR_TO_PR,
    "asylum": CKAN_ID_ASYLUM,
    "ops": CKAN_ID_OPS,
    "afghan": CKAN_ID_AFGHAN,
    "adhoc_pr": CKAN_ID_ADHOC_PR,
}

# Per-dataset XLSX parse configuration for multi-row merged headers.
# Used by _fetch_dataset to pass the correct skip_rows, header_rows, label_cols
# to _parse_ircc_xlsx via fetch_and_parse(ircc_parse_config=...).
#
# Layout A — Standard quarterly (1 label col, 3 header rows: year/quarter/month):
#   pr, study, work_imp, work_tfwp, afghan
# Layout B — Two-label quarterly (2 label cols, 3 header rows):
#   ee_admissions, ee_invited, tr_to_pr
# Layout B-monthly — Two-label, no quarter row (2 label cols, 2 header rows):
#   asylum
# Layout C — Operational (6 skip rows, 2 header rows: year/month):
#   ops
# Layout D — Legacy annual (simple 1 header row, already works):
#   adhoc_pr (header_rows=1 routes through _parse_ircc_xlsx but produces same result)
DATASET_PARSE_CONFIG: dict[str, dict[str, int]] = {
    "pr":           {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
    "study":        {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
    "work_imp":     {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
    "work_tfwp":    {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
    "ee_admissions": {"skip_rows": 2, "header_rows": 3, "label_cols": 2},
    "ee_invited":   {"skip_rows": 2, "header_rows": 3, "label_cols": 2},
    "tr_to_pr":     {"skip_rows": 2, "header_rows": 3, "label_cols": 2},
    "asylum":       {"skip_rows": 2, "header_rows": 2, "label_cols": 2},
    "ops":          {"skip_rows": 6, "header_rows": 2, "label_cols": 1},
    "afghan":       {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
    "adhoc_pr":     {"skip_rows": 2, "header_rows": 1, "label_cols": 1},
}

# Registry: DATASET_REGISTRY[dataset_key][breakdown_key][lang] = full URL
# Note: Operational Processing filenames contain literal spaces — stored as-is, do NOT percent-encode.
# Note: Ad-hoc PR files are English-only — only "en" key, no "fr" key.
DATASET_REGISTRY: dict[str, dict[str, dict[str, str]]] = {
    # -------------------------------------------------------------------------
    # Permanent Residents (CKAN: f7e5498e-0ad8-4417-85c9-9b8aff9b9eda)
    # -------------------------------------------------------------------------
    "pr": {
        "country": {
            "en": BASE_URL + "EN_ODP-PR-Citz.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-Citz.xlsx",
        },
        "province": {
            "en": BASE_URL + "EN_ODP-PR-ProvImmCat.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-ProvImmCat.xlsx",
        },
        "gender": {
            "en": BASE_URL + "EN_ODP-PR-Gender.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-Gender.xlsx",
        },
        "age": {
            "en": BASE_URL + "EN_ODP-PR-AgeGroup.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-AgeGroup.xlsx",
        },
        "cma": {
            "en": BASE_URL + "EN_ODP-PR-CMA.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-CMA.xlsx",
        },
        "noc": {
            "en": BASE_URL + "EN_ODP-PR-ProvNOC4.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-ProvNOC4.xlsx",
        },
        "country_category": {
            "en": BASE_URL + "EN_ODP-PR-CitzImmCat.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-CitzImmCat.xlsx",
        },
        "csd": {
            "en": BASE_URL + "EN_ODP-PR-CSD.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-CSD.xlsx",
        },
        "adoptions": {
            "en": BASE_URL + "EN_ODP-PR-AdoptionsCOBGender.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-AdoptionsCOBGender.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Study Permits (CKAN: 90115b00-f9b8-49e8-afa3-b4cff8facaee)
    # -------------------------------------------------------------------------
    "study": {
        "country": {
            "en": BASE_URL + "EN_ODP-TR-Study-IS_CITZ_sign_date.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Study-IS_CITZ_sign_date.xlsx",
        },
        "province_level": {
            "en": BASE_URL + "EN_ODP-TR-Study-IS_PT_study_level_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Study-IS_PT_study_level_sign.xlsx",
        },
        "gender": {
            "en": BASE_URL + "EN_ODP-TR-Study-IS_PT_gender_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Study-IS_PT_gender_sign.xlsx",
        },
        "annual_country": {
            "en": BASE_URL + "EN_ODP_annual-TR-Study-IS_CITZ_year_end.xlsx",
            "fr": BASE_URL + "FR_ODP_annual-TR-Study-IS_CITZ_year_end.xlsx",
        },
        "annual_province": {
            "en": BASE_URL + "EN_ODP_annual-TR-Study-IS_PT_study_level_year_end.xlsx",
            "fr": BASE_URL + "FR_ODP_annual-TR-Study-IS_PT_study_level_year_end.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Work Permits — IMP (CKAN: 360024f2-17e9-4558-bfc1-3616485d65b9)
    # Note: "EN_ODP-TR-Work-IMP CITZ.xlsx" contains a literal space in filename
    # -------------------------------------------------------------------------
    "work_imp": {
        "province_program": {
            "en": BASE_URL + "EN_ODP-TR-Work-IMP_PT_program_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-IMP_PT_program_sign.xlsx",
        },
        "gender_skill": {
            "en": BASE_URL + "EN_ODP-TR-Work-IMP_gender_skill.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-IMP_gender_skill.xlsx",
        },
        "country": {
            "en": BASE_URL + "EN_ODP-TR-Work-IMP CITZ.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-IMP CITZ.xlsx",
        },
        "noc": {
            "en": BASE_URL + "EN_ODP-TR-Work-IMP_PT_NOC4.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-IMP_PT_NOC4.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Work Permits — TFWP (CKAN: 360024f2-17e9-4558-bfc1-3616485d65b9)
    # Note: "EN_ODP-TR-Work-TFWP CITZ.xlsx" contains a literal space in filename
    # -------------------------------------------------------------------------
    "work_tfwp": {
        "province_program": {
            "en": BASE_URL + "EN_ODP-TR-Work-TFWP_PT_program_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-TFWP_PT_program_sign.xlsx",
        },
        "country": {
            "en": BASE_URL + "EN_ODP-TR-Work-TFWP CITZ.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-TFWP CITZ.xlsx",
        },
        "gender_skill": {
            "en": BASE_URL + "EN_ODP-TR-Work-TFWP_gender_skill_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-TFWP_gender_skill_sign.xlsx",
        },
        "noc": {
            "en": BASE_URL + "EN_ODP-TR-Work-TFWP_PT_NOC4_sign.xlsx",
            "fr": BASE_URL + "FR_ODP-TR-Work-TFWP_PT_NOC4_sign.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Express Entry — Admissions (CKAN: 52e4b14b-597a-4ecf-a184-23a6e69b0d57)
    # -------------------------------------------------------------------------
    "ee_admissions": {
        "gender": {
            "en": BASE_URL + "EN_ODP-EE_Admissions-Gender.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Admissions-Gender.xlsx",
        },
        "category": {
            "en": BASE_URL + "EN_ODP-EE_Admissions-ImmCat.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Admissions-ImmCat.xlsx",
        },
        "country": {
            "en": BASE_URL + "EN_ODP-EE_Admissions-CITZ.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Admissions-CITZ.xlsx",
        },
        "age": {
            "en": BASE_URL + "EN_ODP-EE_Admissions-AgeGroup.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Admissions-AgeGroup.xlsx",
        },
        "occupation": {
            "en": BASE_URL + "EN_ODP-EE_Admissions-Occ.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Admissions-Occ.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Express Entry — Invited Candidates (CKAN: 593e9165-c6ce-4f9b-b519-03d315f92cd4)
    # -------------------------------------------------------------------------
    "ee_invited": {
        "destination": {
            "en": BASE_URL + "EN_ODP-EE_Candidates-IntDest.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Candidates-IntDest.xlsx",
        },
        "score": {
            "en": BASE_URL + "EN_ODP-EE_Candidates-ITAScore.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Candidates-ITAScore.xlsx",
        },
        "country": {
            "en": BASE_URL + "EN_ODP-EE_Candidates-CITZ.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Candidates-CITZ.xlsx",
        },
        "age": {
            "en": BASE_URL + "EN_ODP-EE_Candidates-AgeGroup.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Candidates-AgeGroup.xlsx",
        },
        "education": {
            "en": BASE_URL + "EN_ODP-EE_Candidates-FrnEduLevel.xlsx",
            "fr": BASE_URL + "FR_ODP-EE_Candidates-FrnEduLevel.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # TR-to-PR Transitions (CKAN: 1b026aab-edb3-4d5d-8231-270a09ed4e82)
    # -------------------------------------------------------------------------
    "tr_to_pr": {
        "study_permit": {
            "en": BASE_URL + "EN_ODP-TR_to_PR-IS_PT_immcat.xlsx",
            "fr": BASE_URL + "FR_ODP-TR_to_PR-IS_PT_immcat.xlsx",
        },
        "imp": {
            "en": BASE_URL + "EN_ODP-TR_to_PR-IMP_PT_immcat.xlsx",
            "fr": BASE_URL + "FR_ODP-TR_to_PR-IMP_PT_immcat.xlsx",
        },
        "tfwp": {
            "en": BASE_URL + "EN_ODP-TR_to_PR-TFWP_PT_immcat.xlsx",
            "fr": BASE_URL + "FR_ODP-TR_to_PR-TFWP_PT_immcat.xlsx",
        },
        "pgwp": {
            "en": BASE_URL + "EN_ODP-TR_to_PR-PGWP_PT_immcat.xlsx",
            "fr": BASE_URL + "FR_ODP-TR_to_PR-PGWP_PT_immcat.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Asylum Claimants (CKAN: b6cbcf4d-f763-4924-a2fb-8cc4a06e3de4)
    # -------------------------------------------------------------------------
    "asylum": {
        "province_office": {
            "en": BASE_URL + "EN_ODP-Asylum-OfficeType_Prov.xlsx",
            "fr": BASE_URL + "FR_ODP-Asylum-OfficeType_Prov.xlsx",
        },
        "province_age": {
            "en": BASE_URL + "EN_ODP-Asylum-PT_Age.xlsx",
            "fr": BASE_URL + "FR_ODP-Asylum-PT_Age.xlsx",
        },
        "province_gender": {
            "en": BASE_URL + "EN_ODP-Asylum-PT_Gender.xlsx",
            "fr": BASE_URL + "FR_ODP-Asylum-PT_Gender.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Operational Processing (CKAN: 9b34e712-513f-44e9-babf-9df4f7256550)
    # IMPORTANT: Filenames contain literal spaces. httpx handles encoding correctly.
    # Do NOT percent-encode these URLs — that would double-encode the spaces.
    # -------------------------------------------------------------------------
    "ops": {
        "pr_intake": {
            "en": BASE_URL + "Open Data - OPS PR Intake en.xlsx",
            "fr": BASE_URL + "Open Data - OPS PR Intake fr.xlsx",
        },
        "copr_issued": {
            "en": BASE_URL + "Open Data - OPS COPR Issued en.xlsx",
            "fr": BASE_URL + "Open Data - OPS COPR Issued fr.xlsx",
        },
        "study_processed": {
            "en": BASE_URL + "Open Data - OPS SP Processed en.xlsx",
            "fr": BASE_URL + "Open Data - OPS SP Processed fr.xlsx",
        },
        "tr_processed": {
            "en": BASE_URL + "Open Data - OPS TR Processed en.xlsx",
            "fr": BASE_URL + "Open Data - OPS TR Processed fr.xlsx",
        },
        "trv_intake": {
            "en": BASE_URL + "Open Data - OPS TRV Intake en.xlsx",
            "fr": BASE_URL + "Open Data - OPS TRV Intake fr.xlsx",
        },
        "tr_approved": {
            "en": BASE_URL + "Open Data - OPS TR Approved en.xlsx",
            "fr": BASE_URL + "Open Data - OPS TR Approved fr.xlsx",
        },
        "trv_v1_approved": {
            "en": BASE_URL + "Open Data - OPS TRV V-1 Approved en.xlsx",
            "fr": BASE_URL + "Open Data - OPS TRV V-1 Approved fr.xlsx",
        },
        "new_citizens": {
            "en": BASE_URL + "Open Data - New Citizens by COB en.xlsx",
            "fr": BASE_URL + "Open Data - New Citizens by COB fr.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Afghan Refugees (CKAN: 53520aa7-f2a3-4593-952e-574432a4acd0)
    # -------------------------------------------------------------------------
    "afghan": {
        "gender": {
            "en": BASE_URL + "EN_ODP-Afghan-Gender.xlsx",
            "fr": BASE_URL + "FR_ODP-Afghan-Gender.xlsx",
        },
        "age": {
            "en": BASE_URL + "EN_ODP-Afghan-AgeGroup.xlsx",
            "fr": BASE_URL + "FR_ODP-Afghan-AgeGroup.xlsx",
        },
        "education": {
            "en": BASE_URL + "EN_ODP-Afghan-Edu.xlsx",
            "fr": BASE_URL + "FR_ODP-Afghan-Edu.xlsx",
        },
        "language": {
            "en": BASE_URL + "EN_ODP-Afghan-OL.xlsx",
            "fr": BASE_URL + "FR_ODP-Afghan-OL.xlsx",
        },
    },

    # -------------------------------------------------------------------------
    # Ad-hoc PR (CKAN: ad975a26-df23-456a-8ada-756191a23695)
    # Historical 1980-2023. XLS format (legacy). English-only — no "fr" key.
    # Requires xlrd (optional): pip install mcp-canada[ircc]
    # -------------------------------------------------------------------------
    "adhoc_pr": {
        "category_1980": {
            "en": BASE_URL + "IRCC_PRadmiss_0002_E.xls",
        },
        "country_1980": {
            "en": BASE_URL + "IRCC_PRadmiss_0004_E.xls",
        },
        "province_cat_2000": {
            "en": BASE_URL + "IRCC_PRadmiss_0007_E.xls",
        },
        "province_citz_2000": {
            "en": BASE_URL + "IRCC_PRadmiss_0008_E.xls",
        },
    },
}
