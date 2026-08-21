"""Unit tests for GIS data preparation and decision matrix pipeline (Pipeline A).

Synopsis Stage: Stage 1 — GIS Processing & Candidate Site Generation.
Note: All tests use synthetic spatial geometries and mocked responses — NO live network calls are made.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, box

from src.gis.build_decision_matrix import (
    get_varanasi_boundary,
    generate_candidate_grid,
    points_to_kernel_density_raster,
    linestrings_to_proximity_raster,
    overlay_candidates,
    fetch_poi_layer,
    fetch_charging_stations,
    compute_population_idw_raster,
    compute_landuse_raster,
    compute_landcost_raster,
    compute_grid_proximity_raster,
)


@pytest.fixture
def synthetic_sample_boundary() -> gpd.GeoDataFrame:
    """Fixture providing a deterministic 1km x 1km bounding box polygon in EPSG:4326."""
    # Approximate 1km x 1km box near Varanasi (25.31 N, 83.00 E)
    poly = box(82.9900, 25.3000, 83.0000, 25.3100)
    return gpd.GeoDataFrame({"name": ["Test_Boundary"], "geometry": [poly]}, crs="EPSG:4326")


@pytest.fixture
def synthetic_points_layer() -> gpd.GeoDataFrame:
    """Fixture providing synthetic point coordinates in EPSG:4326."""
    points = [
        Point(82.9920, 25.3020),
        Point(82.9950, 25.3050),
        Point(82.9980, 25.3080),
    ]
    return gpd.GeoDataFrame(
        {"name": ["POI_1", "POI_2", "POI_3"], "geometry": points},
        crs="EPSG:4326",
    )


@pytest.fixture
def synthetic_roads_layer() -> gpd.GeoDataFrame:
    """Fixture providing synthetic road linestrings in EPSG:4326."""
    line1 = LineString([(82.9900, 25.3050), (83.0000, 25.3050)])
    line2 = LineString([(82.9950, 25.3000), (82.9950, 25.3100)])
    return gpd.GeoDataFrame(
        {"highway": ["primary", "secondary"], "geometry": [line1, line2]},
        crs="EPSG:4326",
    )


# ---------------------------------------------------------------------------
# 1. Candidate Grid & Geometry Tests
# ---------------------------------------------------------------------------

def test_generate_candidate_grid_spacing(synthetic_sample_boundary: gpd.GeoDataFrame) -> None:
    """Test that candidate grid generates points with valid IDs and correct spatial spacing."""
    spacing_m = 250.0  # 250m grid inside ~1km box
    grid_gdf = generate_candidate_grid(synthetic_sample_boundary, spacing_m=spacing_m, epsg_projected=32644)

    assert isinstance(grid_gdf, gpd.GeoDataFrame)
    assert len(grid_gdf) > 0
    assert "site_id" in grid_gdf.columns
    assert "latitude" in grid_gdf.columns
    assert "longitude" in grid_gdf.columns
    assert grid_gdf["site_id"].iloc[0] == "SITE_001"
    assert grid_gdf.crs == "EPSG:4326"

    # Verify projected distances between adjacent points are approximately spacing_m
    proj_gdf = grid_gdf.to_crs(epsg=32644)
    x_coords = np.sort(np.unique(np.round(proj_gdf.geometry.x.values, 1)))
    if len(x_coords) > 1:
        x_diffs = np.diff(x_coords)
        assert np.isclose(x_diffs[0], spacing_m, atol=2.0)


def test_get_varanasi_boundary_sample_mode() -> None:
    """Test sample mode boundary generation without external API queries."""
    sample_bbox = {"min_lat": 25.30, "min_lon": 82.99, "max_lat": 25.32, "max_lon": 83.01}
    boundary_gdf = get_varanasi_boundary(mode="sample", sample_bbox=sample_bbox)
    assert isinstance(boundary_gdf, gpd.GeoDataFrame)
    assert len(boundary_gdf) == 1
    assert boundary_gdf.geometry.iloc[0].geom_type == "Polygon"


# ---------------------------------------------------------------------------
# 2. Kernel Density & Proximity Rasterization Tests
# ---------------------------------------------------------------------------

def test_points_to_kernel_density_raster(synthetic_points_layer: gpd.GeoDataFrame) -> None:
    """Test KDE rasterization returns arrays within 1.0 to 9.0 bounds and correct shape."""
    bbox = (25.3000, 82.9900, 25.3100, 83.0000)
    raster_arr, meta = points_to_kernel_density_raster(
        synthetic_points_layer, bbox=bbox, resolution_m=50.0, bandwidth_m=200.0, epsg_projected=32644
    )

    assert isinstance(raster_arr, np.ndarray)
    assert raster_arr.ndim == 2
    assert raster_arr.shape == meta["shape"]
    assert np.all(raster_arr >= 1.0)
    assert np.all(raster_arr <= 9.0)
    assert meta["resolution_m"] == 50.0


def test_points_to_kernel_density_empty_layer() -> None:
    """Test KDE rasterization on empty point layer returns baseline 1.0."""
    empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    bbox = (25.3000, 82.9900, 25.3100, 83.0000)
    raster_arr, meta = points_to_kernel_density_raster(
        empty_gdf, bbox=bbox, resolution_m=50.0, bandwidth_m=200.0, epsg_projected=32644
    )
    assert np.all(raster_arr == 1.0)


def test_linestrings_to_proximity_raster(synthetic_roads_layer: gpd.GeoDataFrame) -> None:
    """Test road proximity rasterization returns valid 1.0-9.0 values with highest scores near roads."""
    bbox = (25.3000, 82.9900, 25.3100, 83.0000)
    raster_arr, meta = linestrings_to_proximity_raster(
        synthetic_roads_layer, bbox=bbox, resolution_m=50.0, max_dist_m=1000.0, epsg_projected=32644
    )

    assert isinstance(raster_arr, np.ndarray)
    assert np.all(raster_arr >= 1.0)
    assert np.all(raster_arr <= 9.0)


# ---------------------------------------------------------------------------
# 3. Spatial Overlay & Mocked Fetcher Tests (Zero Network)
# ---------------------------------------------------------------------------

def test_overlay_candidates(
    synthetic_sample_boundary: gpd.GeoDataFrame,
    synthetic_points_layer: gpd.GeoDataFrame,
    synthetic_roads_layer: gpd.GeoDataFrame,
) -> None:
    """Test candidate site overlay extracts values for each raster layer into the decision matrix."""
    candidates_gdf = generate_candidate_grid(synthetic_sample_boundary, spacing_m=250.0)
    bbox = (25.3000, 82.9900, 25.3100, 83.0000)

    poi_raster, poi_meta = points_to_kernel_density_raster(synthetic_points_layer, bbox=bbox, resolution_m=50.0)
    road_raster, road_meta = linestrings_to_proximity_raster(synthetic_roads_layer, bbox=bbox, resolution_m=50.0)

    raster_layers = {
        "C1_Roads": (road_raster, road_meta),
        "C6_POIs": (poi_raster, poi_meta),
    }

    matrix_df = overlay_candidates(candidates_gdf, raster_layers)

    assert isinstance(matrix_df, pd.DataFrame)
    assert len(matrix_df) == len(candidates_gdf)
    assert "site_id" in matrix_df.columns
    assert "C1_Roads" in matrix_df.columns
    assert "C6_POIs" in matrix_df.columns
    assert np.all(matrix_df["C1_Roads"] >= 1.0) and np.all(matrix_df["C1_Roads"] <= 9.0)
    assert np.all(matrix_df["C6_POIs"] >= 1.0) and np.all(matrix_df["C6_POIs"] <= 9.0)


@patch("src.gis.build_decision_matrix.requests.post")
def test_fetch_poi_layer_mocked(mock_post: MagicMock) -> None:
    """Test generic POI fetcher parses Google Places API (New) responses without live network calls."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "places": [
            {
                "displayName": {"text": "Mock High School"},
                "id": "plc_123",
                "location": {"latitude": 25.3050, "longitude": 82.9950},
            },
            {
                "displayName": {"text": "Mock Academy"},
                "id": "plc_456",
                "location": {"latitude": 25.3080, "longitude": 82.9980},
            },
        ]
    }
    mock_post.return_value = mock_resp

    bbox = (25.3000, 82.9900, 25.3100, 83.0000)
    gdf = fetch_poi_layer("schools", "fake_api_key", bbox=bbox)

    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(gdf) == 2
    assert "Mock High School" in gdf["name"].values
    assert gdf.geometry.iloc[0].x == 82.9950
    assert gdf.geometry.iloc[0].y == 25.3050


@patch("src.gis.build_decision_matrix.requests.get")
def test_fetch_charging_stations_mocked(mock_get: MagicMock) -> None:
    """Test OpenChargeMap fetcher parses response correctly without live network calls."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"ID": 9991, "AddressInfo": {"Latitude": 25.3060, "Longitude": 82.9970}}
    ]
    mock_get.return_value = mock_resp

    bbox = (25.3000, 82.9900, 25.3100, 83.0000)
    gdf = fetch_charging_stations("fake_ocm_key", bbox=bbox)

    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(gdf) == 1
    assert gdf["station_id"].iloc[0] == 9991


# ---------------------------------------------------------------------------
# 4. Out-of-Scope Stubs NotImplementedError Tests
# ---------------------------------------------------------------------------

def test_unconfirmed_criteria_raise_not_implemented() -> None:
    """Test that all pending/unconfirmed criteria functions cleanly raise NotImplementedError."""
    dummy_gdf = gpd.GeoDataFrame(geometry=[Point(83.0, 25.3)], crs="EPSG:4326")
    dummy_path = Path("non_existent_data.tif")

    with pytest.raises(NotImplementedError, match="Population density data source pending"):
        compute_population_idw_raster(dummy_path, dummy_gdf)

    with pytest.raises(NotImplementedError, match="Land use / land cover data source pending"):
        compute_landuse_raster(dummy_path, dummy_gdf)

    with pytest.raises(NotImplementedError, match="Land cost data source pending"):
        compute_landcost_raster(dummy_path, dummy_gdf)

    with pytest.raises(NotImplementedError, match="Grid substation data source pending"):
        compute_grid_proximity_raster(dummy_path, dummy_gdf)


# ---------------------------------------------------------------------------
# 5. Milestone 7 Equal-Scrutiny Multi-Zone Validation Tests
# ---------------------------------------------------------------------------

def test_comparison_zone_containment_in_boundary() -> None:
    """Verify that all 4 commercial comparison zone centroids lie within the municipal polygon."""
    boundary_gdf = get_varanasi_boundary(mode="full")
    poly = boundary_gdf.geometry.iloc[0]

    # Key commercial zone centroids (Sigra, Lanka, Cantt, Godowlia)
    zone_centroids = [
        ("Godowlia", 25.3100, 83.0050),
        ("Sigra", 25.31126, 82.98521),
        ("Lanka", 25.28109, 82.99884),
        ("Cantonment", 25.32757, 82.98624),
    ]

    for name, lat, lon in zone_centroids:
        pt = Point(lon, lat)
        assert poly.contains(pt), f"Zone centroid for '{name}' ({lat}, {lon}) is outside the municipal polygon."

