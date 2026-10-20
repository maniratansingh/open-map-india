#!/usr/bin/env python3
"""
OpenMapIndia — VPS Heavy Edition Batch Generator
Generates multi-gigabyte dense turn-by-turn road geometry files district-by-district.
Saves directly to `vps_heavy_edition/data/full_routes/` (ignored by Git).
"""

import argparse
import glob
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DISTRICTS_DIR = os.path.join(BASE_DIR, "api", "v1", "districts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "full_routes")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_dense_route(from_coords, to_coords):
    url = f"https://router.project-osrm.org/route/v1/driving/{from_coords[1]},{from_coords[0]};{to_coords[1]},{to_coords[0]}?overview=full&geometries=geojson"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenMapIndia-VPS-Batch/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            res = json.loads(r.read().decode())
            if res.get("routes"):
                rt = res["routes"][0]
                return {
                    "coordinates": rt["geometry"]["coordinates"],
                    "distance_m": round(rt["distance"]),
                    "duration_sec": round(rt["duration"])
                }
    except Exception:
        pass
    return None

def process_village_dense(v):
    v_coords = v["coords"]
    phc = v["precomputed_routing"]["nearest_health"]
    hw = v["precomputed_routing"]["nearest_highway"]

    # Target points
    phc_target = [phc.get("lat", v_coords[0] + 0.02), phc.get("lon", v_coords[1] + 0.02)]
    hw_target = hw.get("junction_coord", [v_coords[0] + 0.01, v_coords[1] + 0.01])

    phc_dense = fetch_dense_route(v_coords, phc_target)
    hw_dense = fetch_dense_route(v_coords, hw_target)

    return {
        "id": v["id"],
        "name": v["name"],
        "coords": v_coords,
        "dense_road_routing": {
            "hospital_route": phc_dense or {
                "coordinates": [[v_coords[1], v_coords[0]], [phc_target[1], phc_target[0]]],
                "distance_m": phc["distance_m"]
            },
            "highway_route": hw_dense or {
                "coordinates": [[v_coords[1], v_coords[0]], [hw_target[1], hw_target[0]]],
                "distance_m": hw["distance_m"]
            }
        }
    }

def process_district(district_file, max_villages=None):
    with open(district_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    state_slug = data["state_slug"]
    district_slug = data["district_slug"]
    villages = data.get("villages", [])
    if max_villages:
        villages = villages[:max_villages]

    out_state_dir = os.path.join(OUTPUT_DIR, state_slug)
    os.makedirs(out_state_dir, exist_ok=True)
    out_file = os.path.join(out_state_dir, f"{district_slug}.json")

    print(f"▶️ Computing {len(villages)} dense routes for {district_slug.title()} ({state_slug.title()})...")
    start_t = time.time()

    dense_villages = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        for res in executor.map(process_village_dense, villages):
            dense_villages.append(res)

    output_doc = {
        "edition": "VPS_HEAVY_FULL_RESOLUTION",
        "district": data["district"],
        "state": data["state"],
        "state_slug": state_slug,
        "district_slug": district_slug,
        "analytics": data.get("analytics", {}),
        "total_dense_settlements": len(dense_villages),
        "villages": dense_villages
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_doc, f, indent=2)

    elapsed = time.time() - start_t
    size_kb = round(os.path.getsize(out_file) / 1024, 1)
    print(f"✅ Finished {district_slug.title()} in {elapsed:.1f}s | Size: {size_kb} KB -> {out_file}")

def main():
    parser = argparse.ArgumentParser(description="OpenMapIndia VPS Batch Full-Resolution Road Generator")
    parser.add_argument("--state", type=str, help="State slug (e.g. uttar_pradesh)")
    parser.add_argument("--district", type=str, help="District slug (e.g. basti)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of villages per district for testing")
    parser.add_argument("--all", action="store_true", help="Process all districts across India")
    args = parser.parse_args()

    if args.state and args.district:
        dist_path = os.path.join(DISTRICTS_DIR, args.state, f"{args.district}.json")
        if os.path.exists(dist_path):
            process_district(dist_path, args.limit)
        else:
            print(f"❌ File not found: {dist_path}")
    elif args.all:
        all_districts = sorted(glob.glob(os.path.join(DISTRICTS_DIR, "*", "*.json")))
        print(f"🌍 Found {len(all_districts)} districts to process. Starting batch run...")
        for idx, dist_file in enumerate(all_districts):
            print(f"\n[{idx+1}/{len(all_districts)}]")
            try:
                process_district(dist_file, args.limit)
            except Exception as e:
                print(f"⚠️ Error on {dist_file}: {e}")
    else:
        # Default test
        print("💡 Usage:")
        print("  python3 build_full_india.py --state uttar_pradesh --district basti --limit 10")
        print("  python3 build_full_india.py --all")

if __name__ == "__main__":
    main()
