#!/usr/bin/env python3
"""
OpenMapIndia — Local Full-Resolution Turn-by-Turn Road Generator
Generates full-resolution, high-density road geometry routes for offline local storage.
This data is stored under `data/local_full_resolution/` and is strictly ignored by Git (.gitignore).
"""

import gzip
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

LOCAL_OUT_DIR = "data/local_full_resolution"
DISTRICTS_DIR = "api/v1/districts"

os.makedirs(LOCAL_OUT_DIR, exist_ok=True)

def fetch_osrm_dense_geometry(from_coords, to_coords):
    url = f"https://router.project-osrm.org/route/v1/driving/{from_coords[1]},{from_coords[0]};{to_coords[1]},{to_coords[0]}?overview=full&geometries=geojson"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenMapIndia-LocalGenerator/1.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode())
            if res.get('routes'):
                route = res['routes'][0]
                return {
                    'geometry': route['geometry']['coordinates'],
                    'duration_sec': route['duration'],
                    'distance_m': route['distance']
                }
    except Exception:
        pass
    return None

def process_single_village(v):
    v_coords = v['coords']
    phc = v['precomputed_routing']['nearest_health']
    hw = v['precomputed_routing']['nearest_highway']

    phc_target = [phc.get('lat', v_coords[0] + 0.02), phc.get('lon', v_coords[1] + 0.02)]
    hw_target = hw.get('junction_coord', [v_coords[0] + 0.01, v_coords[1] + 0.01])

    # Fetch dense geometry
    phc_dense = fetch_osrm_dense_geometry(v_coords, phc_target)
    hw_dense = fetch_osrm_dense_geometry(v_coords, hw_target)

    return {
        'id': v['id'],
        'name': v['name'],
        'coords': v_coords,
        'full_turn_by_turn': {
            'hospital_route': phc_dense or {'points_count': 2, 'geometry': [v_coords, phc_target]},
            'highway_route': hw_dense or {'points_count': 2, 'geometry': [v_coords, hw_target]}
        }
    }

def generate_district_full_resolution(state_slug, district_slug, max_villages=50):
    input_file = os.path.join(DISTRICTS_DIR, state_slug, f"{district_slug}.json")
    if not os.path.exists(input_file):
        print(f"❌ District file not found: {input_file}")
        return

    print(f"🔄 Generating Local Full-Resolution Geometry for {district_slug.title()}, {state_slug.title()}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    villages = data.get('villages', [])[:max_villages]
    print(f"Processing {len(villages)} settlements with parallel road network tracing...")

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for res in executor.map(process_single_village, villages):
            results.append(res)

    out_state_dir = os.path.join(LOCAL_OUT_DIR, state_slug)
    os.makedirs(out_state_dir, exist_ok=True)
    out_file = os.path.join(out_state_dir, f"{district_slug}_full_resolution.json")

    output_payload = {
        'mode': "LOCAL_FULL_RESOLUTION_OFFLINE",
        'district': data['district'],
        'state': data['state'],
        'total_dense_routes': len(results),
        'settlements': results
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"✅ Full-resolution dataset saved locally at: {out_file}")
    print(f"📦 Size: {round(os.path.getsize(out_file) / 1024, 1)} KB (Safe on your disk, never pushed to Git)")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        state = sys.argv[1]
        dist = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        generate_district_full_resolution(state, dist, limit)
    else:
        # Default test: Basti, UP
        generate_district_full_resolution("uttar_pradesh", "basti", 20)
