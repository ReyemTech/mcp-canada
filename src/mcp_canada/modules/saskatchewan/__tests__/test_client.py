"""Saskatchewan client unit tests.

Plans 02-05 fill the test bodies. Wave 0 defines placeholder classes so pytest
can collect these nodes and downstream plans reference specific node IDs.

TestSharedApiGetContract: verifies _hub_get patches at module-local level
(patches mcp_canada.modules.saskatchewan.client.api_get — BC/Alberta pattern).

NEVER patch at the shared module level for Saskatchewan client tests — use the
module-local from-import pattern (same as Phase 15 BC and Phase 17 Alberta).
"""

from __future__ import annotations

import pytest


class TestSharedApiGetContract:
    """_hub_get: verifies it calls api_get (module-local import), not CKAN envelope.

    Plan 02 fills: patches mcp_canada.modules.saskatchewan.client.api_get
    and asserts Hub JSON contract (dict with 'features' key, no .get('success')).
    """

    pass


class TestSaskSearchDatasets:
    """fetch_search_datasets: Hub Search pagination via OGC API Records startindex.

    Plan 02 fills: verify limit/startindex/q params; verify (results, total) shape.
    """

    pass


class TestSaskGetDatasetDetails:
    """fetch_dataset_details: Hub item detail by ID.

    Plan 02 fills: verify feature_server_url detection; download_urls list.
    """

    pass


class TestSaskQueryDataset:
    """fetch_query_dataset: hybrid router (FeatureServer vs parseable file vs metadata-only).

    Plan 02 fills: FeatureServer branch, CSV/GeoJSON branch, metadata-only fallback.
    """

    pass


class TestSaskListOrgs:
    """fetch_organizations: derives unique owners from Hub Search results.

    Plan 02 fills.
    """

    pass


class TestSaskListCategories:
    """fetch_categories: derives unique category strings from Hub Search results.

    Plan 02 fills.
    """

    pass


class TestSaskGetCropYields:
    """fetch_crop_yields: region dispatch to Province Summary vs Regions Only FeatureServer.

    Plan 03 fills: verify "provincial" routes to CROP_YIELDS_PROVINCE_FS_URL;
    "southeast" routes to CROP_YIELDS_REGIONS_FS_URL with WHERE Region='Southeast'.
    """

    pass


class TestSaskGetGrainElevators:
    """fetch_grain_elevators: default PR='SK' filter; optional railway= filter.

    Plan 03 fills.
    """

    pass


class TestSaskGetMineralMines:
    """fetch_mineral_mines: dispatch by mineral to MINERAL_MINES_FS_URLS dict.

    Plan 03 fills: verify "potash" routes to Potash_2024_06_13 URL;
    ValueError for unknown mineral.
    """

    pass


class TestSaskGetFireBans:
    """fetch_fire_bans: SPSA ban scope dispatch; empty list is a valid success.

    Plan 04 fills: verify "urban"→layer 0, "parks"→layer 8;
    empty features=[] does NOT raise.
    """

    pass


class TestSaskGetHistoricWildfires:
    """fetch_historic_wildfires: optional year/cause filters on STARTDATE/CAUSE1.

    Plan 04 fills.
    """

    pass


class TestSaskGetAirQuality:
    """fetch_air_quality: optional community= filter; live 15min cache TTL.

    Plan 04 fills.
    """

    pass


class TestSaskGetWSAStations:
    """fetch_wsa_stations: WSA org URL; Province='SK' default; optional basin= filter.

    Plan 05 fills.
    """

    pass


class TestSaskGetWSAReservoirs:
    """fetch_wsa_reservoirs: WSA org URL; layer 26 (NOT 0).

    Plan 05 fills: assert layer_id=WSA_RESERVOIRS_LAYER (26) passed to query_feature_service.
    """

    pass
