"""Pipeline A: GIS Data Preparation — Decision Matrix Builder.

Synopsis Stage: Stage 1 — Spatial Data Ingestion, Density/Proximity Rasterization & Candidate Grid Overlay.
Theoretical Foundation: Rashmitha, Sushma & Roy (2024, Environment, Development and Sustainability).

This module implements the complete GIS processing pipeline for confirmed criteria in Varanasi:
1. Candidate Site Generation: Regular fishnet spatial grid points across urban bounds (EPSG:32644).
2. Road Accessibility: OSM Overpass API -> Euclidean distance -> 1-9 proximity raster.
3. Competitor EV Infrastructure: OpenChargeMap API -> Kernel Density -> 1-9 density raster.
4. Urban Points of Interest (POI): Google Places API (Nearby Search) for 7 confirmed categories:
   Schools, Shopping Malls, Restaurants, Hospitals, Theatres, Transit/Bus Stops, Petrol Bunks.
5. Spatial Overlay: Extracts criteria scores (1-9 scale) for each candidate site to assemble
   the standardized decision matrix (candidate sites x criteria).

Unconfirmed criteria (Population Density, Land Use/Cover, Land Cost, Grid Substations)
remain explicitly stubbed with NotImplementedError per docs/PENDING_DECISIONS.md.
"""

import os
import time
import json
from pathlib import Path
from typing import Any, Optional
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, box
from scipy.stats import gaussian_kde
import requests
import yaml
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# 1. Boundary & Candidate Site Generation
# ---------------------------------------------------------------------------

def get_varanasi_boundary(
    mode: str = "sample",
    sample_bbox: Optional[dict[str, float]] = None,
    full_query: str = "Varanasi, Uttar Pradesh, India",
) -> gpd.GeoDataFrame:
    """Retrieve the boundary polygon for Varanasi in sample or full execution mode.

    Args:
        mode: "sample" (uses small landmark bounding box) or "full" (approximated municipal polygon).
        sample_bbox: Dictionary with min_lat, min_lon, max_lat, max_lon.
        full_query: Search string for Nominatim boundary extraction (fallback).

    Returns:
        GeoDataFrame containing the single boundary Polygon in EPSG:4326.
    """
    if mode == "sample":
        if sample_bbox is None:
            # Default Godowlia / Dashashwamedh landmark box in Central Varanasi (~2.5km x 2.7km)
            sample_bbox = {
                "min_lat": 25.3000,
                "min_lon": 82.9900,
                "max_lat": 25.3250,
                "max_lon": 83.0150,
            }
        poly = box(
            sample_bbox["min_lon"],
            sample_bbox["min_lat"],
            sample_bbox["max_lon"],
            sample_bbox["max_lat"],
        )
        return gpd.GeoDataFrame({"name": ["Varanasi_Sample_Box"], "geometry": [poly]}, crs="EPSG:4326")

    # Full mode: Load or construct the approximated municipal boundary polygon (~76.99 km²),
    # manually constructed from named urban landmarks conforming to the published ~82.1 km² 90-ward VMC extent.
    # Note: OpenStreetMap lacks an admin_level=8 boundary relation for Varanasi Nagar Nigam.
    geojson_cache = Path("data/raw/gis/varanasi_vmc_boundary.geojson")
    if geojson_cache.exists():
        return gpd.read_file(geojson_cache)

    coords_82km = [
        (82.990, 25.265),  # BHU South Gate
        (83.008, 25.268),  # Samne Ghat / Assi confluence
        (83.015, 25.285),  # Assi Ghat
        (83.018, 25.305),  # Dashashwamedh Ghat
        (83.032, 25.325),  # Manikarnika / Panchganga Ghat
        (83.045, 25.340),  # Rajghat / Malviya Bridge
        (83.030, 25.362),  # Sarnath bypass / Ashapur
        (83.000, 25.368),  # Pandeypur / Paharia
        (82.970, 25.365),  # Shivpur / GT Road North
        (82.952, 25.345),  # Tarna / Industrial Estate
        (82.948, 25.320),  # Varanasi Cantt / Railway Station West
        (82.952, 25.298),  # Lahartara / Baulia
        (82.960, 25.282),  # Manduadih / BLW (DLW)
        (82.975, 25.268),  # Naria / Sunderpur
        (82.990, 25.265),  # Close polygon
    ]
    poly = Polygon(coords_82km)
    gdf = gpd.GeoDataFrame(
        {"name": ["Varanasi_Municipal_Approximated_77km2"], "geometry": [poly]},
        crs="EPSG:4326",
    )
    geojson_cache.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(geojson_cache, driver="GeoJSON")
    return gdf


def generate_candidate_grid(
    boundary_gdf: gpd.GeoDataFrame,
    spacing_m: float = 500.0,
    epsg_projected: int = 32644,
) -> gpd.GeoDataFrame:
    """Generate candidate site alternatives as a regular fishnet grid of points.

    Following Architectural Decision AD-1 (see docs/PENDING_DECISIONS.md), candidate sites
    are generated as a regular metric spatial grid projected in UTM Zone 44N (EPSG:32644)
    and strictly point-in-polygon clipped to the urban boundary polygon.

    Args:
        boundary_gdf: Boundary polygon GeoDataFrame in EPSG:4326.
        spacing_m: Grid resolution in meters (default 500m).
        epsg_projected: Metric projected CRS (default 32644 for Varanasi UTM Zone 44N).

    Returns:
        GeoDataFrame with candidate Point geometries, site_id, latitude, and longitude in EPSG:4326.
    """
    projected = boundary_gdf.to_crs(epsg=epsg_projected)
    poly = projected.geometry.iloc[0]
    min_x, min_y, max_x, max_y = poly.bounds

    x_coords = np.arange(min_x + spacing_m / 2, max_x, spacing_m)
    y_coords = np.arange(min_y + spacing_m / 2, max_y, spacing_m)

    grid_points = []
    for x in x_coords:
        for y in y_coords:
            pt = Point(x, y)
            if poly.contains(pt):
                grid_points.append(pt)

    # Fallback if box is too small for strict contains
    if not grid_points:
        for x in x_coords:
            for y in y_coords:
                grid_points.append(Point(x, y))

    pts_gdf = gpd.GeoDataFrame(geometry=grid_points, crs=f"EPSG:{epsg_projected}")
    pts_wgs84 = pts_gdf.to_crs(epsg=4326)

    pts_wgs84["site_id"] = [f"SITE_{i+1:03d}" for i in range(len(pts_wgs84))]
    pts_wgs84["latitude"] = pts_wgs84.geometry.y
    pts_wgs84["longitude"] = pts_wgs84.geometry.x

    return pts_wgs84


# ---------------------------------------------------------------------------
# 2. Data Fetchers (Confirmed Criteria) & Resilient Checkpointed Caching
# ---------------------------------------------------------------------------

def fetch_poi_layer(
    category: str,
    api_key: str,
    bbox: tuple[float, float, float, float],
    radius_m: float = 2500.0,
    use_mesh: bool = False,
    cache_dir: Optional[Path] = None,
) -> gpd.GeoDataFrame:
    """Generic reusable fetcher for Point of Interest categories via Google Places API (New).

    Supports single circular search (sample mode) or 30-tile spatial mesh (full mode)
    with place_id deduplication, incremental disk caching, and exponential backoff retry.

    Args:
        category: One of 'schools', 'shopping_malls', 'restaurants', 'hospitals',
            'theatres', 'bus_stops', 'petrol_bunks'.
        api_key: Google Places API Key.
        bbox: Bounding box tuple (min_lat, min_lon, max_lat, max_lon).
        radius_m: Search radius in meters for single tile mode.
        use_mesh: Whether to query 30-tile spatial mesh (full mode).
        cache_dir: Directory to save and load cached raw responses.

    Returns:
        GeoDataFrame of POI Point geometries in EPSG:4326.
    """
    category_type_map = {
        "schools": ["school", "secondary_school", "primary_school"],
        "shopping_malls": ["shopping_mall", "department_store"],
        "restaurants": ["restaurant", "cafe"],
        "hospitals": ["hospital", "medical_clinic"],
        "theatres": ["movie_theater"],
        "bus_stops": ["bus_station", "transit_station", "bus_stop"],
        "petrol_bunks": ["gas_station"],
    }
    included_types = category_type_map.get(category, [category])

    # Check disk cache first
    if cache_dir is not None:
        cache_file = cache_dir / f"{category}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_items = json.load(f)
                points = [Point(it["longitude"], it["latitude"]) for it in cached_items if "longitude" in it and "latitude" in it]
                names = [it.get("name", "Unknown") for it in cached_items]
                place_ids = [it.get("place_id", "") for it in cached_items]
                print(f"  [Cache Hit] Loaded {len(points)} unique '{category}' POIs from {cache_file}")
                return gpd.GeoDataFrame({"name": names, "place_id": place_ids, "geometry": points}, crs="EPSG:4326")
            except Exception as e:
                print(f"  [Warning] Failed to read cache {cache_file}: {e}")

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.location,places.id",
        "Content-Type": "application/json",
    }

    tiles_to_query = []
    if use_mesh:
        # 5x5 grid (25 primary tiles, r=1800m) + 5 nested dense-core tiles (r=800m)
        lats_p = np.linspace(25.265, 25.365, 5)
        lons_p = np.linspace(82.948, 83.045, 5)
        for lat in lats_p:
            for lon in lons_p:
                tiles_to_query.append({"lat": round(lat, 4), "lon": round(lon, 4), "radius_m": 1800.0})
        nested_tiles = [
            {"lat": 25.3100, "lon": 83.0050, "radius_m": 800.0},
            {"lat": 25.3050, "lon": 83.0100, "radius_m": 800.0},
            {"lat": 25.3150, "lon": 83.0120, "radius_m": 800.0},
            {"lat": 25.3180, "lon": 82.9850, "radius_m": 800.0},
            {"lat": 25.2950, "lon": 82.9980, "radius_m": 800.0},
        ]
        tiles_to_query.extend(nested_tiles)
    else:
        min_lat, min_lon, max_lat, max_lon = bbox
        center_lat = (min_lat + max_lat) / 2.0
        center_lon = (min_lon + max_lon) / 2.0
        tiles_to_query.append({"lat": center_lat, "lon": center_lon, "radius_m": radius_m})

    unique_places: dict[str, dict[str, Any]] = {}

    for idx, t in enumerate(tiles_to_query):
        payload = {
            "includedTypes": included_types,
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": t["lat"],
                        "longitude": t["lon"],
                    },
                    "radius": t["radius_m"],
                }
            },
        }

        # 3-attempt exponential backoff
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("places", []):
                        pid = item.get("id")
                        loc = item.get("location", {})
                        lat, lon = loc.get("latitude"), loc.get("longitude")
                        if pid and lat is not None and lon is not None:
                            unique_places[pid] = {
                                "place_id": pid,
                                "name": item.get("displayName", {}).get("text", "Unknown"),
                                "latitude": lat,
                                "longitude": lon,
                            }
                    break
                elif resp.status_code == 429 or resp.status_code >= 500:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[Warning] Places API returned {resp.status_code} on tile {idx+1}: {resp.text[:100]}")
                    break
            except Exception as exc:
                if attempt == 2:
                    print(f"[Warning] Places API fetch failed on tile {idx+1} for '{category}': {exc}")
                time.sleep(1.0)

    # Save to cache
    if cache_dir is not None and unique_places:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{category}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(list(unique_places.values()), f, indent=2)
        print(f"  [Cached] Saved {len(unique_places)} unique '{category}' POIs to {cache_file}")

    points = [Point(it["longitude"], it["latitude"]) for it in unique_places.values()]
    names = [it["name"] for it in unique_places.values()]
    place_ids = list(unique_places.keys())

    if not points:
        return gpd.GeoDataFrame({"name": [], "place_id": [], "geometry": []}, crs="EPSG:4326")

    return gpd.GeoDataFrame({"name": names, "place_id": place_ids, "geometry": points}, crs="EPSG:4326")


def fetch_charging_stations(
    api_key: str,
    bbox: tuple[float, float, float, float],
    cache_dir: Optional[Path] = None,
) -> gpd.GeoDataFrame:
    """Fetch existing EV charging stations via OpenChargeMap API (Competition Criterion).

    Args:
        api_key: OpenChargeMap API Key.
        bbox: Bounding box tuple (min_lat, min_lon, max_lat, max_lon).
        cache_dir: Directory to save and load cached raw responses.

    Returns:
        GeoDataFrame of existing EV station Point geometries in EPSG:4326.
    """
    if cache_dir is not None:
        cache_file = cache_dir / "competitor_evcs.geojson"
        if cache_file.exists():
            try:
                gdf = gpd.read_file(cache_file)
                print(f"  [Cache Hit] Loaded {len(gdf)} existing EV stations from {cache_file}")
                return gdf
            except Exception as e:
                print(f"  [Warning] Failed to read cache {cache_file}: {e}")

    min_lat, min_lon, max_lat, max_lon = bbox
    url = "https://api.openchargemap.io/v3/poi/"
    headers = {"X-API-Key": api_key, "User-Agent": "ev-siting-varanasi-research/1.0"}
    params = {
        "boundingbox": f"({min_lat},{min_lon}),({max_lat},{max_lon})",
        "maxresults": 100,
        "compact": "true",
        "verbose": "false",
    }

    points = []
    station_ids = []

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        items = resp.json()

        for item in items:
            addr = item.get("AddressInfo", {})
            lat = addr.get("Latitude")
            lon = addr.get("Longitude")
            if lat is not None and lon is not None:
                points.append(Point(lon, lat))
                station_ids.append(item.get("ID", 0))
    except Exception as exc:
        print(f"[Warning] OpenChargeMap fetch failed: {exc}")

    if not points:
        gdf = gpd.GeoDataFrame({"station_id": [], "geometry": []}, crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame({"station_id": station_ids, "geometry": points}, crs="EPSG:4326")

    if cache_dir is not None and len(gdf) > 0:
        cache_dir.mkdir(parents=True, exist_ok=True)
        gdf.to_file(cache_dir / "competitor_evcs.geojson", driver="GeoJSON")

    return gdf


def fetch_major_roads(
    bbox: tuple[float, float, float, float],
    cache_dir: Optional[Path] = None,
) -> gpd.GeoDataFrame:
    """Fetch major road network Linestrings via OpenStreetMap Overpass API.

    Queries motorway, trunk, primary, secondary, and tertiary highways.

    Args:
        bbox: Bounding box tuple (min_lat, min_lon, max_lat, max_lon).
        cache_dir: Directory to save and load cached raw responses.

    Returns:
        GeoDataFrame of LineString road geometries in EPSG:4326.
    """
    if cache_dir is not None:
        cache_file = cache_dir / "major_roads.geojson"
        if cache_file.exists():
            try:
                gdf = gpd.read_file(cache_file)
                print(f"  [Cache Hit] Loaded {len(gdf)} road segments from {cache_file}")
                return gdf
            except Exception as e:
                print(f"  [Warning] Failed to read cache {cache_file}: {e}")

    min_lat, min_lon, max_lat, max_lon = bbox
    overpass_endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]
    headers = {
        "User-Agent": "ev-siting-varanasi-research/1.0 (academic research project)",
        "Accept": "application/json",
    }
    overpass_query = f"""
    [out:json][timeout:25];
    (
      way["highway"~"motorway|trunk|primary|secondary|tertiary"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out geom;
    """

    lines = []
    road_types = []

    for endpoint in overpass_endpoints:
        try:
            resp = requests.post(endpoint, data={"data": overpass_query}, headers=headers, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                for element in data.get("elements", []):
                    if element.get("type") == "way" and "geometry" in element:
                        coords = [(pt["lon"], pt["lat"]) for pt in element["geometry"]]
                        if len(coords) >= 2:
                            lines.append(LineString(coords))
                            road_types.append(element.get("tags", {}).get("highway", "primary"))
                if lines:
                    break
        except Exception as exc:
            print(f"[Warning] OSM Overpass endpoint {endpoint} failed: {exc}")

    if not lines:
        gdf = gpd.GeoDataFrame({"highway": [], "geometry": []}, crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame({"highway": road_types, "geometry": lines}, crs="EPSG:4326")

    if cache_dir is not None and len(gdf) > 0:
        cache_dir.mkdir(parents=True, exist_ok=True)
        gdf.to_file(cache_dir / "major_roads.geojson", driver="GeoJSON")

    return gdf


# ---------------------------------------------------------------------------
# 3. Density & Proximity Rasterization (1–9 Suitability Scale)
# ---------------------------------------------------------------------------

def points_to_kernel_density_raster(
    points_gdf: gpd.GeoDataFrame,
    bbox: tuple[float, float, float, float],
    resolution_m: float = 50.0,
    bandwidth_m: float = 400.0,
    epsg_projected: int = 32644,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Convert a point layer into a standardized 1–9 Kernel Density raster surface.

    Following Rashmitha et al. (2024), spatial point features are converted to continuous
    density surfaces and reclassified onto a 1–9 scale (where 9 = highest density/suitability).

    Args:
        points_gdf: GeoDataFrame of Point features in EPSG:4326.
        bbox: Bounding box tuple (min_lat, min_lon, max_lat, max_lon).
        resolution_m: Pixel grid cell size in meters (default: 50m).
        bandwidth_m: Kernel density smoothing bandwidth in meters.
        epsg_projected: Metric projected CRS.

    Returns:
        Tuple of (2D numpy array with values in [1.0, 9.0], grid_metadata dictionary).
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    box_wgs84 = gpd.GeoDataFrame(geometry=[box(min_lon, min_lat, max_lon, max_lat)], crs="EPSG:4326")
    box_proj = box_wgs84.to_crs(epsg=epsg_projected)
    min_x, min_y, max_x, max_y = box_proj.geometry.iloc[0].bounds

    x_grid = np.arange(min_x, max_x + resolution_m, resolution_m)
    y_grid = np.arange(min_y, max_y + resolution_m, resolution_m)
    xx, yy = np.meshgrid(x_grid, y_grid)

    meta = {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "resolution_m": resolution_m,
        "shape": xx.shape,
        "x_coords": x_grid,
        "y_coords": y_grid,
        "epsg": epsg_projected,
    }

    if points_gdf.empty or len(points_gdf) == 0:
        return np.ones_like(xx, dtype=float), meta

    points_proj = points_gdf.to_crs(epsg=epsg_projected)
    pt_x = points_proj.geometry.x.values
    pt_y = points_proj.geometry.y.values

    # Evaluate distance-weighted Kernel Density
    grid_coords = np.vstack([xx.ravel(), yy.ravel()])
    if len(pt_x) >= 2:
        try:
            kde = gaussian_kde(np.vstack([pt_x, pt_y]), bw_method=bandwidth_m / 1000.0)
            density = kde(grid_coords).reshape(xx.shape)
        except Exception:
            density = np.zeros_like(xx)
            for px, py in zip(pt_x, pt_y):
                dist_sq = (xx - px) ** 2 + (yy - py) ** 2
                density += np.exp(-dist_sq / (2 * (bandwidth_m ** 2)))
    else:
        density = np.zeros_like(xx)
        for px, py in zip(pt_x, pt_y):
            dist_sq = (xx - px) ** 2 + (yy - py) ** 2
            density += np.exp(-dist_sq / (2 * (bandwidth_m ** 2)))

    # Reclassify onto 1.0 to 9.0 scale
    d_min, d_max = density.min(), density.max()
    if d_max > d_min:
        norm_density = 1.0 + 8.0 * ((density - d_min) / (d_max - d_min))
    else:
        norm_density = np.ones_like(density) * 5.0

    return norm_density, meta


def linestrings_to_proximity_raster(
    roads_gdf: gpd.GeoDataFrame,
    bbox: tuple[float, float, float, float],
    resolution_m: float = 50.0,
    max_dist_m: float = 2000.0,
    epsg_projected: int = 32644,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Convert a road LineString layer into a 1–9 Proximity raster surface.

    Calculates Euclidean distance to the nearest road network feature and reclassifies onto
    1–9 suitability scale (closer distance = higher score, e.g. <=100m -> 9.0, >=2000m -> 1.0).

    Args:
        roads_gdf: GeoDataFrame of LineString road features in EPSG:4326.
        bbox: Bounding box tuple (min_lat, min_lon, max_lat, max_lon).
        resolution_m: Pixel grid cell size in meters.
        max_dist_m: Maximum distance threshold for zero suitability (1.0).
        epsg_projected: Metric projected CRS.

    Returns:
        Tuple of (2D numpy array with values in [1.0, 9.0], grid_metadata dictionary).
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    box_wgs84 = gpd.GeoDataFrame(geometry=[box(min_lon, min_lat, max_lon, max_lat)], crs="EPSG:4326")
    box_proj = box_wgs84.to_crs(epsg=epsg_projected)
    min_x, min_y, max_x, max_y = box_proj.geometry.iloc[0].bounds

    x_grid = np.arange(min_x, max_x + resolution_m, resolution_m)
    y_grid = np.arange(min_y, max_y + resolution_m, resolution_m)
    xx, yy = np.meshgrid(x_grid, y_grid)

    meta = {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "resolution_m": resolution_m,
        "shape": xx.shape,
        "x_coords": x_grid,
        "y_coords": y_grid,
        "epsg": epsg_projected,
    }

    if roads_gdf.empty or len(roads_gdf) == 0:
        return np.ones_like(xx, dtype=float), meta

    roads_proj = roads_gdf.to_crs(epsg=epsg_projected)
    union_roads = roads_proj.unary_union

    grid_points = gpd.GeoSeries([Point(x, y) for x, y in zip(xx.ravel(), yy.ravel())], crs=f"EPSG:{epsg_projected}")
    distances = grid_points.distance(union_roads).values.reshape(xx.shape)

    clamped_dist = np.clip(distances, 0.0, max_dist_m)
    norm_proximity = 9.0 - 8.0 * (clamped_dist / max_dist_m)

    return norm_proximity, meta


# ---------------------------------------------------------------------------
# 4. Candidate Grid Overlay & Decision Matrix Extraction
# ---------------------------------------------------------------------------

def overlay_candidates(
    candidates_gdf: gpd.GeoDataFrame,
    raster_layers: dict[str, tuple[np.ndarray, dict[str, Any]]],
    epsg_projected: int = 32644,
) -> pd.DataFrame:
    """Extract raster criteria scores for each candidate site point to build the decision matrix.

    Args:
        candidates_gdf: GeoDataFrame containing site_id, latitude, longitude, geometry.
        raster_layers: Dictionary mapping criterion_id to (raster_array, metadata_dict).
        epsg_projected: Metric projected CRS.

    Returns:
        DataFrame containing site_id, coordinates, and extracted 1-9 criteria scores.
    """
    cand_proj = candidates_gdf.to_crs(epsg=epsg_projected)
    site_x = cand_proj.geometry.x.values
    site_y = cand_proj.geometry.y.values

    results_df = pd.DataFrame({
        "site_id": candidates_gdf["site_id"].values,
        "latitude": candidates_gdf["latitude"].values,
        "longitude": candidates_gdf["longitude"].values,
    })

    for crit_name, (raster, meta) in raster_layers.items():
        min_x = meta["min_x"]
        min_y = meta["min_y"]
        res_m = meta["resolution_m"]
        n_rows, n_cols = raster.shape

        col_indices = np.clip(((site_x - min_x) / res_m).astype(int), 0, n_cols - 1)
        row_indices = np.clip(((site_y - min_y) / res_m).astype(int), 0, n_rows - 1)

        scores = raster[row_indices, col_indices]
        results_df[crit_name] = np.round(scores, 4)

    return results_df


# ---------------------------------------------------------------------------
# 5. Stubs for Pending Criteria (NotImplementedError)
# ---------------------------------------------------------------------------

def compute_population_idw_raster(
    census_data_path: Path,
    boundary_gdf: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Interpolate ward-level population density to continuous raster.

    Raises:
        NotImplementedError: Pending population density data source — see docs/PENDING_DECISIONS.md.
    """
    raise NotImplementedError(
        "Population density data source pending verification — see docs/PENDING_DECISIONS.md"
    )


def compute_landuse_raster(
    lulc_raster_path: Path,
    boundary_gdf: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Reclassify land use / land cover classes into 1-9 suitability scores.

    Raises:
        NotImplementedError: Pending LULC data source — see docs/PENDING_DECISIONS.md.
    """
    raise NotImplementedError(
        "Land use / land cover data source pending verification — see docs/PENDING_DECISIONS.md"
    )


def compute_landcost_raster(
    real_estate_data_path: Path,
    boundary_gdf: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Interpolate commercial real estate rental rates proxy raster.

    Raises:
        NotImplementedError: Pending land cost data source — see docs/PENDING_DECISIONS.md.
    """
    raise NotImplementedError(
        "Land cost data source pending verification — see docs/PENDING_DECISIONS.md"
    )


def compute_grid_proximity_raster(
    substation_points_path: Path,
    boundary_gdf: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Compute distance raster to electrical power grid substations.

    Raises:
        NotImplementedError: Pending UPPCL substation coordinates — see docs/PENDING_DECISIONS.md.
    """
    raise NotImplementedError(
        "Grid substation data source pending verification — see docs/PENDING_DECISIONS.md"
    )


# ---------------------------------------------------------------------------
# 6. End-to-End Orchestrator
# ---------------------------------------------------------------------------

def build_decision_matrix(
    mode: Optional[str] = None,
    config_path: Path = Path("config/criteria.yaml"),
    output_processed_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Execute end-to-end GIS pipeline to construct and save the MCDM decision matrix.

    Reads configuration, fetches confirmed spatial criteria, calculates KDE and proximity
    rasters, overlays candidate fishnet points, and exports the final decision matrix CSV.

    Args:
        mode: Optional execution mode override ("sample" or "full").
        config_path: Path to config/criteria.yaml.
        output_processed_path: Destination path for decision_matrix.csv.

    Returns:
        DataFrame representing the populated decision matrix for confirmed criteria.
    """
    load_dotenv()
    google_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
    ocm_key = os.getenv("OPENCHARGEMAP_API_KEY", "")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    exec_cfg = cfg.get("execution", {})
    if mode is None:
        mode = exec_cfg.get("mode", "sample")

    spacing_m = float(exec_cfg.get("fishnet_spacing_m", 500.0))
    res_m = float(exec_cfg.get("raster_resolution_m", 50.0))
    bw_m = float(exec_cfg.get("kde_bandwidth_m", 400.0))
    sample_bbox = exec_cfg.get("sample_bbox")

    if output_processed_path is None:
        if mode == "full_v2":
            output_processed_path = Path("data/processed/gis/decision_matrix_full_v2.csv")
        elif mode == "full":
            output_processed_path = Path("data/processed/gis/decision_matrix_full.csv")
        else:
            output_processed_path = Path("data/processed/gis/decision_matrix.csv")
    else:
        output_processed_path = Path(output_processed_path)

    if mode == "full_v2":
        cache_dir = Path("data/raw/gis/full_run_cache_v2")
        use_mesh = True
    elif mode == "full":
        cache_dir = Path("data/raw/gis/full_run_cache")
        use_mesh = True
    else:
        cache_dir = None
        use_mesh = False

    print(f"[GIS Pipeline] Initializing in '{mode}' mode (spacing: {spacing_m}m)...")

    # 1. Generate Boundary & Candidate Grid
    boundary_gdf = get_varanasi_boundary(mode=mode, sample_bbox=sample_bbox)
    candidates_gdf = generate_candidate_grid(boundary_gdf, spacing_m=spacing_m)
    print(f"[GIS Pipeline] Generated {len(candidates_gdf)} candidate site alternatives.")

    min_lat = candidates_gdf["latitude"].min() - 0.005
    max_lat = candidates_gdf["latitude"].max() + 0.005
    min_lon = candidates_gdf["longitude"].min() - 0.005
    max_lon = candidates_gdf["longitude"].max() + 0.005
    extent_bbox = (min_lat, min_lon, max_lat, max_lon)

    raster_layers: dict[str, tuple[np.ndarray, dict[str, Any]]] = {}

    # 2. Major Roads Criterion (C1)
    print("[GIS Pipeline] Fetching major road networks (OSM Overpass)...")
    roads_gdf = fetch_major_roads(extent_bbox, cache_dir=cache_dir)
    road_raster, road_meta = linestrings_to_proximity_raster(roads_gdf, extent_bbox, resolution_m=res_m)
    raster_layers["C1_Major_Roads"] = (road_raster, road_meta)

    # 3. Competitor EV Stations (C5)
    print("[GIS Pipeline] Fetching competitor EV charging stations (OpenChargeMap)...")
    evcs_gdf = fetch_charging_stations(ocm_key, extent_bbox, cache_dir=cache_dir)
    evcs_raster, evcs_meta = points_to_kernel_density_raster(
        evcs_gdf, extent_bbox, resolution_m=res_m, bandwidth_m=bw_m
    )
    raster_layers["C5_Competitor_EVCS"] = (evcs_raster, evcs_meta)

    # 4. Urban POI Categories (C6) via Google Places
    poi_categories = [
        ("C6_POI_Schools", "schools"),
        ("C6_POI_Shopping_Malls", "shopping_malls"),
        ("C6_POI_Restaurants", "restaurants"),
        ("C6_POI_Hospitals", "hospitals"),
        ("C6_POI_Theatres", "theatres"),
        ("C6_POI_Bus_Stops", "bus_stops"),
        ("C6_POI_Petrol_Bunks", "petrol_bunks"),
    ]

    for crit_id, cat_name in poi_categories:
        print(f"[GIS Pipeline] Fetching POI category: {cat_name} (Google Places)...")
        poi_gdf = fetch_poi_layer(
            cat_name,
            google_key,
            extent_bbox,
            use_mesh=use_mesh,
            cache_dir=cache_dir,
        )
        poi_raster, poi_meta = points_to_kernel_density_raster(
            poi_gdf, extent_bbox, resolution_m=res_m, bandwidth_m=bw_m
        )
        raster_layers[crit_id] = (poi_raster, poi_meta)

    # 5. Candidate Overlay & Decision Matrix Assembly
    print("[GIS Pipeline] Overlaying candidate grid on raster layers...")
    decision_matrix = overlay_candidates(candidates_gdf, raster_layers)

    # 6. Export Output CSV
    output_processed_path.parent.mkdir(parents=True, exist_ok=True)
    decision_matrix.to_csv(output_processed_path, index=False)
    print(f"[GIS Pipeline] Decision matrix successfully saved to: {output_processed_path}")
    print(f"[GIS Pipeline] Matrix dimensions: {decision_matrix.shape[0]} sites x {decision_matrix.shape[1]} columns")

    return decision_matrix


if __name__ == "__main__":
    build_decision_matrix()
