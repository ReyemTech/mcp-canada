"""Unit tests for IRCC client functions.

All tests mock fetch_and_parse to verify:
- The correct URL is passed from DATASET_REGISTRY
- The (data, was_cached) tuple is returned correctly
- ValueError is raised for invalid breakdown keys
"""

import pytest

from mcp_canada.modules.ircc.constants import DATASET_PARSE_CONFIG, DATASET_REGISTRY


class TestFetchPermanentResidents:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_permanent_residents

        rows, cached = await fetch_permanent_residents(breakdown="country")

        expected_url = DATASET_REGISTRY["pr"]["country"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["pr"]
        )
        assert rows == [{"year": 2024, "value": 100}]
        assert cached is False

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_permanent_residents

        with pytest.raises(ValueError, match="invalid_key"):
            await fetch_permanent_residents(breakdown="invalid_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_permanent_residents

        await fetch_permanent_residents(breakdown="country", lang="fr")

        expected_url = DATASET_REGISTRY["pr"]["country"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["pr"]
        )


class TestFetchStudyPermits:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_study_permits

        rows, cached = await fetch_study_permits(breakdown="country")

        expected_url = DATASET_REGISTRY["study"]["country"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["study"]
        )
        assert rows == [{"year": 2024, "value": 100}]
        assert cached is False

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_study_permits

        with pytest.raises(ValueError, match="not_a_breakdown"):
            await fetch_study_permits(breakdown="not_a_breakdown")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_study_permits

        await fetch_study_permits(breakdown="province_level", lang="fr")

        expected_url = DATASET_REGISTRY["study"]["province_level"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["study"]
        )


class TestFetchWorkPermitsImp:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_imp

        await fetch_work_permits_imp(breakdown="country")

        expected_url = DATASET_REGISTRY["work_imp"]["country"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["work_imp"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_imp

        with pytest.raises(ValueError):
            await fetch_work_permits_imp(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_imp

        await fetch_work_permits_imp(breakdown="noc", lang="fr")

        expected_url = DATASET_REGISTRY["work_imp"]["noc"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["work_imp"]
        )


class TestFetchWorkPermitsTfwp:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_tfwp

        await fetch_work_permits_tfwp(breakdown="country")

        expected_url = DATASET_REGISTRY["work_tfwp"]["country"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["work_tfwp"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_tfwp

        with pytest.raises(ValueError):
            await fetch_work_permits_tfwp(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_work_permits_tfwp

        await fetch_work_permits_tfwp(breakdown="gender_skill", lang="fr")

        expected_url = DATASET_REGISTRY["work_tfwp"]["gender_skill"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["work_tfwp"]
        )


class TestFetchEeAdmissions:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_admissions

        await fetch_ee_admissions(breakdown="gender")

        expected_url = DATASET_REGISTRY["ee_admissions"]["gender"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ee_admissions"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_admissions

        with pytest.raises(ValueError):
            await fetch_ee_admissions(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_admissions

        await fetch_ee_admissions(breakdown="category", lang="fr")

        expected_url = DATASET_REGISTRY["ee_admissions"]["category"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ee_admissions"]
        )


class TestFetchEeInvited:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_invited

        await fetch_ee_invited(breakdown="destination")

        expected_url = DATASET_REGISTRY["ee_invited"]["destination"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ee_invited"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_invited

        with pytest.raises(ValueError):
            await fetch_ee_invited(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ee_invited

        await fetch_ee_invited(breakdown="score", lang="fr")

        expected_url = DATASET_REGISTRY["ee_invited"]["score"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ee_invited"]
        )


class TestFetchTrToPr:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_tr_to_pr

        await fetch_tr_to_pr(breakdown="study_permit")

        expected_url = DATASET_REGISTRY["tr_to_pr"]["study_permit"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["tr_to_pr"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_tr_to_pr

        with pytest.raises(ValueError):
            await fetch_tr_to_pr(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_tr_to_pr

        await fetch_tr_to_pr(breakdown="pgwp", lang="fr")

        expected_url = DATASET_REGISTRY["tr_to_pr"]["pgwp"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["tr_to_pr"]
        )


class TestFetchAsylum:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_asylum

        await fetch_asylum(breakdown="province_office")

        expected_url = DATASET_REGISTRY["asylum"]["province_office"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["asylum"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_asylum

        with pytest.raises(ValueError):
            await fetch_asylum(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_asylum

        await fetch_asylum(breakdown="province_gender", lang="fr")

        expected_url = DATASET_REGISTRY["asylum"]["province_gender"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["asylum"]
        )


class TestFetchOps:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ops

        await fetch_ops(breakdown="pr_intake")

        expected_url = DATASET_REGISTRY["ops"]["pr_intake"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ops"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ops

        with pytest.raises(ValueError):
            await fetch_ops(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_ops

        await fetch_ops(breakdown="copr_issued", lang="fr")

        expected_url = DATASET_REGISTRY["ops"]["copr_issued"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["ops"]
        )


class TestFetchAfghan:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_afghan

        await fetch_afghan(breakdown="gender")

        expected_url = DATASET_REGISTRY["afghan"]["gender"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["afghan"]
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_afghan

        with pytest.raises(ValueError):
            await fetch_afghan(breakdown="bad_key")

    async def test_french_url_variant(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_afghan

        await fetch_afghan(breakdown="education", lang="fr")

        expected_url = DATASET_REGISTRY["afghan"]["education"]["fr"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url, ircc_parse_config=DATASET_PARSE_CONFIG["afghan"]
        )


class TestFetchAdhocPr:
    async def test_calls_fetch_and_parse_with_correct_url(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_adhoc_pr

        await fetch_adhoc_pr(breakdown="category_1980")

        expected_url = DATASET_REGISTRY["adhoc_pr"]["category_1980"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url,
            ircc_parse_config={"skip_rows": 2, "header_rows": 1, "label_cols": 1},
        )

    async def test_raises_value_error_for_invalid_breakdown(self, mock_fetch_and_parse):
        from mcp_canada.modules.ircc.client import fetch_adhoc_pr

        with pytest.raises(ValueError):
            await fetch_adhoc_pr(breakdown="bad_key")

    async def test_raises_value_error_for_french_lang(self, mock_fetch_and_parse):
        """Ad-hoc PR files are English-only — no fr key."""
        from mcp_canada.modules.ircc.client import fetch_adhoc_pr

        with pytest.raises(ValueError, match="fr"):
            await fetch_adhoc_pr(breakdown="category_1980", lang="fr")


# ---------------------------------------------------------------------------
# Tests for ircc_parse_config pass-through in _fetch_dataset
# ---------------------------------------------------------------------------


class TestFetchDatasetParseConfigPassthrough:
    """Verify _fetch_dataset passes the correct ircc_parse_config to fetch_and_parse."""

    async def test_pr_passes_layout_a_config(self, mock_fetch_and_parse):
        """pr dataset passes Layout A config (skip_rows=2, header_rows=3, label_cols=1)."""
        from mcp_canada.modules.ircc.client import fetch_permanent_residents

        await fetch_permanent_residents(breakdown="country")

        expected_url = DATASET_REGISTRY["pr"]["country"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url,
            ircc_parse_config={"skip_rows": 2, "header_rows": 3, "label_cols": 1},
        )

    async def test_asylum_passes_layout_b_monthly_config(self, mock_fetch_and_parse):
        """asylum dataset passes Layout B-monthly config (skip_rows=2, header_rows=2, label_cols=2)."""
        from mcp_canada.modules.ircc.client import fetch_asylum

        await fetch_asylum(breakdown="province_office")

        expected_url = DATASET_REGISTRY["asylum"]["province_office"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url,
            ircc_parse_config={"skip_rows": 2, "header_rows": 2, "label_cols": 2},
        )

    async def test_ops_passes_layout_c_config(self, mock_fetch_and_parse):
        """ops dataset passes Layout C config (skip_rows=6, header_rows=2, label_cols=1)."""
        from mcp_canada.modules.ircc.client import fetch_ops

        await fetch_ops(breakdown="pr_intake")

        expected_url = DATASET_REGISTRY["ops"]["pr_intake"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url,
            ircc_parse_config={"skip_rows": 6, "header_rows": 2, "label_cols": 1},
        )

    async def test_adhoc_pr_passes_layout_d_config(self, mock_fetch_and_parse):
        """adhoc_pr dataset passes Layout D config (skip_rows=2, header_rows=1, label_cols=1)."""
        from mcp_canada.modules.ircc.client import fetch_adhoc_pr

        await fetch_adhoc_pr(breakdown="category_1980")

        expected_url = DATASET_REGISTRY["adhoc_pr"]["category_1980"]["en"]
        mock_fetch_and_parse.assert_called_once_with(
            expected_url,
            ircc_parse_config={"skip_rows": 2, "header_rows": 1, "label_cols": 1},
        )
