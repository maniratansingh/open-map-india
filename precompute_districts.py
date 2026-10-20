#!/usr/bin/env python3
"""
Step 2 (Enriched): Universal District Precompute Engine with Infrastructure Analytics
Spatially clusters settlements, healthcare points, and highways into 594+ District files,
precomputing nearest emergency/highway vectors AND district-wide infrastructure analytics.
"""

import gzip
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape, Point
from shapely import STRtree, points

DISTRICTS_GEOJSON = "data/raw/india_district.geojson"
VILLAGES_GZ = "data/extracted/villages.jsonl.gz"
HEALTH_GZ = "data/extracted/health.jsonl.gz"
HIGHWAYS_GZ = "data/extracted/highways.jsonl.gz"
OUTPUT_BASE = "api/v1"

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def encode_polyline(coords):
    result = []
    prev_lat = 0
    prev_lon = 0
    for lat, lon in coords:
        lat_i = int(round(lat * 1e5))
        lon_i = int(round(lon * 1e5))
        d_lat = lat_i - prev_lat
        d_lon = lon_i - prev_lon
        prev_lat = lat_i
        prev_lon = lon_i
        for d in (d_lat, d_lon):
            val = ~(d << 1) if d < 0 else (d << 1)
            while val >= 0x20:
                result.append(chr((0x20 | (val & 0x1f)) + 63))
                val >>= 5
            result.append(chr(val + 63))
    return "".join(result)

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return round(2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))

def to_cartesian(lat, lon):
    phi = np.radians(lat)
    lam = np.radians(lon)
    x = np.cos(phi) * np.cos(lam)
    y = np.cos(phi) * np.sin(lam)
    z = np.sin(phi)
    return np.column_stack([x, y, z])

def main():
    print("=" * 65)
    print("🇮🇳 OpenMapIndia: District Precompute & Analytics Engine")
    print("=" * 65)
    start_time = time.time()

    # 1. Load Districts
    print("1️⃣  Loading District Boundaries...")
    with open(DISTRICTS_GEOJSON, "r", encoding="utf-8") as f:
        dist_data = json.load(f)

    districts = []
    dist_geoms = []
    dist_centroids = []
    for feat in dist_data['features']:
        state_name = feat['properties'].get('NAME_1', 'Unknown_State')
        dist_name = feat['properties'].get('NAME_2', 'Unknown_District')
        geom = shape(feat['geometry'])
        if geom.is_valid and not geom.is_empty:
            c = geom.centroid
            dist_info = {
                'id': len(districts),
                'state': state_name,
                'state_slug': slugify(state_name),
                'district': dist_name,
                'district_slug': slugify(dist_name),
                'bbox': [round(b, 4) for b in geom.bounds],
                'geom': geom,
                'centroid': (c.y, c.x)
            }
            districts.append(dist_info)
            dist_geoms.append(geom)
            dist_centroids.append((c.y, c.x))

    print(f"Loaded {len(districts)} valid district polygons.")
    tree = STRtree(dist_geoms)
    dist_c_arr = np.array(dist_centroids)
    dist_kdtree = cKDTree(to_cartesian(dist_c_arr[:, 0], dist_c_arr[:, 1]))

    # 2. Load Healthcare Facilities
    print("2️⃣  Loading Health Facilities & Spatial Index...")
    health_records = []
    with gzip.open(HEALTH_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            health_records.append(json.loads(line))
    print(f"Loaded {len(health_records):,} health facilities.")

    health_lats = np.array([h['lat'] for h in health_records], dtype=np.float32)
    health_lons = np.array([h['lon'] for h in health_records], dtype=np.float32)
    health_cartesian = to_cartesian(health_lats, health_lons)
    health_kdtree = cKDTree(health_cartesian)

    # 3. Load Highways & Sample Key Cut Points
    print("3️⃣  Loading Highway Corridors & Sampling Cut Points...")
    highway_meta = []
    hw_sample_coords = []
    with gzip.open(HIGHWAYS_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            h = json.loads(line)
            coords = h['coords']
            ref = h.get('ref') or h.get('name') or 'Arterial Road'
            grade = h.get('grade', 'primary')
            step = max(1, len(coords) // 4)
            for idx in range(0, len(coords), step):
                pt = coords[idx]
                hw_sample_coords.append(pt)
                highway_meta.append({'ref': ref, 'grade': grade, 'coord': pt})

    print(f"Sampled {len(hw_sample_coords):,} highway access nodes.")
    hw_coords_arr = np.array(hw_sample_coords, dtype=np.float32)
    hw_cartesian = to_cartesian(hw_coords_arr[:, 0], hw_coords_arr[:, 1])
    hw_kdtree = cKDTree(hw_cartesian)

    # 4. Stream Settlements & Partition
    print("4️⃣  Loading Settlements & Performing Spatial Partitioning...")
    all_villages = []
    with gzip.open(VILLAGES_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            all_villages.append(json.loads(line))

    total_v = len(all_villages)
    v_lats = np.array([v['lat'] for v in all_villages], dtype=np.float32)
    v_lons = np.array([v['lon'] for v in all_villages], dtype=np.float32)
    v_points = points(v_lons, v_lats)

    res = tree.query(v_points, predicate='intersects')

    district_villages = defaultdict(list)
    assigned_indices = set()

    for i in range(res.shape[1]):
        dist_idx = res[0, i]
        v_idx = res[1, i]
        if v_idx not in assigned_indices:
            district_villages[dist_idx].append(all_villages[v_idx])
            assigned_indices.add(v_idx)

    unassigned = [i for i in range(total_v) if i not in assigned_indices]
    if unassigned:
        unassigned_lats = v_lats[unassigned]
        unassigned_lons = v_lons[unassigned]
        unassigned_cart = to_cartesian(unassigned_lats, unassigned_lons)
        _, nearest_dist_ids = dist_kdtree.query(unassigned_cart, k=1)
        for idx, dist_idx in enumerate(nearest_dist_ids):
            district_villages[dist_idx].append(all_villages[unassigned[idx]])

    print(f"✅ All {total_v:,} settlements binned across districts.")

    # 5. Precompute Vectors & Infrastructure Analytics
    print("5️⃣  Precomputing Routes & District Infrastructure Analytics...")
    generated_count = 0

    for dist_idx, dist in enumerate(districts):
        v_list = district_villages.get(dist_idx, [])
        if not v_list:
            continue

        state_slug = dist['state_slug']
        dist_slug = dist['district_slug']
        out_dir = os.path.join(OUTPUT_BASE, "districts", state_slug)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{dist_slug}.json")

        sub_lats = np.array([v['lat'] for v in v_list], dtype=np.float32)
        sub_lons = np.array([v['lon'] for v in v_list], dtype=np.float32)
        sub_cartesian = to_cartesian(sub_lats, sub_lons)

        _, nearest_health_indices = health_kdtree.query(sub_cartesian, k=1)
        _, nearest_hw_indices = hw_kdtree.query(sub_cartesian, k=1)

        enriched_villages = []
        health_distances_m = []
        highway_distances_m = []

        for i, v in enumerate(v_list):
            h_idx = nearest_health_indices[i]
            h_obj = health_records[h_idx]
            h_dist = int(haversine_m(v['lat'], v['lon'], h_obj['lat'], h_obj['lon']) * 1.3)
            h_poly = encode_polyline([(v['lat'], v['lon']), (h_obj['lat'], h_obj['lon'])])
            health_distances_m.append(h_dist)

            hw_idx = nearest_hw_indices[i]
            hw_obj = highway_meta[hw_idx]
            hw_dist = int(haversine_m(v['lat'], v['lon'], hw_obj['coord'][0], hw_obj['coord'][1]) * 1.25)
            hw_poly = encode_polyline([(v['lat'], v['lon']), (hw_obj['coord'][0], hw_obj['coord'][1])])
            highway_distances_m.append(hw_dist)

            enriched_villages.append({
                'id': v['id'],
                'name': v['name'],
                'type': v['type'],
                'coords': [v['lat'], v['lon']],
                'precomputed_routing': {
                    'nearest_health': {
                        'name': h_obj['name'],
                        'type': h_obj['type'],
                        'distance_m': h_dist,
                        'polyline': h_poly
                    },
                    'nearest_highway': {
                        'ref': hw_obj['ref'],
                        'grade': hw_obj['grade'],
                        'distance_m': hw_dist,
                        'junction_coord': hw_obj['coord'],
                        'polyline': hw_poly
                    }
                }
            })

        # Calculate District Infrastructure Analytics
        h_arr = np.array(health_distances_m)
        hw_arr = np.array(highway_distances_m)
        v_count = len(enriched_villages)

        avg_health_km = round(float(np.mean(h_arr)) / 1000.0, 2)
        median_health_km = round(float(np.median(h_arr)) / 1000.0, 2)
        avg_highway_km = round(float(np.mean(hw_arr)) / 1000.0, 2)
        median_highway_km = round(float(np.median(hw_arr)) / 1000.0, 2)

        pct_hw_under_2km = round(float(np.sum(hw_arr <= 2000)) / v_count * 100.0, 1)
        pct_hw_under_5km = round(float(np.sum(hw_arr <= 5000)) / v_count * 100.0, 1)
        pct_phc_under_5km = round(float(np.sum(h_arr <= 5000)) / v_count * 100.0, 1)

        # Composite Infrastructure Connectivity Score (0 - 100)
        # Higher score = closer to highways and hospitals
        raw_score = (100.0 - min(100.0, avg_health_km * 4.0)) * 0.5 + pct_hw_under_5km * 0.5
        infrastructure_score = round(max(5.0, min(99.0, raw_score)), 1)

        analytics = {
            'infrastructure_score': infrastructure_score,
            'avg_phc_distance_km': avg_health_km,
            'median_phc_distance_km': median_health_km,
            'avg_highway_distance_km': avg_highway_km,
            'median_highway_distance_km': median_highway_km,
            'pct_villages_under_2km_highway': pct_hw_under_2km,
            'pct_villages_under_5km_highway': pct_hw_under_5km,
            'pct_villages_under_5km_phc': pct_phc_under_5km
        }

        output_doc = {
            'project': "OpenMapIndia",
            'district': dist['district'],
            'state': dist['state'],
            'state_slug': state_slug,
            'district_slug': dist_slug,
            'bbox': dist['bbox'],
            'total_settlements': v_count,
            'analytics': analytics,
            'villages': enriched_villages,
            '_links': {
                'state': f"../../states/{state_slug}.json",
                'national': "../../india.json"
            }
        }

        with open(out_file, "w", encoding="utf-8") as out_f:
            json.dump(output_doc, out_f, separators=(',', ':'))

        generated_count += 1
        if generated_count % 50 == 0:
            print(f"  Generated {generated_count}/{len(districts)} districts with analytics...")

    total_time = time.time() - start_time
    print("=" * 65)
    print(f"🎉 Complete! Generated {generated_count} District Packages with Analytics in {total_time:.1f}s!")
    print("=" * 65)

if __name__ == "__main__":
    main()
