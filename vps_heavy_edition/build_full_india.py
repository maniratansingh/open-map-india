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
OSRM_BACKEND = os.environ.get("OSRM_BACKEND", "http://router.project-osrm.org")

def fetch_dense_route(from_coords, to_coords):
    url = f"{OSRM_BACKEND}/route/v1/driving/{from_coords[1]},{from_coords[0]};{to_coords[1]},{to_coords[0]}?overview=full&geometries=geojson"
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
    except Exception as inner_e:
        if url.startswith("https://"):
            try:
                fallback_url = url.replace("https://", "http://", 1)
                req = urllib.request.Request(fallback_url, headers={"User-Agent": "OpenMapIndia-VPS-Batch/1.0"})
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

    # Derived travel duration and emergency tiers
    hosp_dist = phc_dense["distance_m"] if phc_dense else phc["distance_m"]
    hosp_dur_sec = phc_dense["duration_sec"] if phc_dense else round((hosp_dist / 1000) / 30 * 3600)
    hosp_dur_min = round(hosp_dur_sec / 60, 1)

    hw_dist = hw_dense["distance_m"] if hw_dense else hw["distance_m"]
    hw_dur_sec = hw_dense["duration_sec"] if hw_dense else round((hw_dist / 1000) / 40 * 3600)
    hw_dur_min = round(hw_dur_sec / 60, 1)

    if hosp_dur_min <= 15:
        emergency_tier = "Tier-1 (Immediate: <=15 min)"
    elif hosp_dur_min <= 30:
        emergency_tier = "Tier-2 (Moderate: 15-30 min)"
    else:
        emergency_tier = "Tier-3 (High Risk: >30 min)"

    return {
        "id": v["id"],
        "name": v["name"],
        "coords": v_coords,
        "metrics": {
            "hospital_distance_km": round(hosp_dist / 1000, 2),
            "hospital_duration_min": hosp_dur_min,
            "highway_distance_km": round(hw_dist / 1000, 2),
            "highway_duration_min": hw_dur_min,
            "emergency_tier": emergency_tier,
            "last_computed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "dense_road_routing": {
            "hospital_route": phc_dense or {
                "coordinates": [[v_coords[1], v_coords[0]], [phc_target[1], phc_target[0]]],
                "distance_m": hosp_dist,
                "duration_sec": hosp_dur_sec
            },
            "highway_route": hw_dense or {
                "coordinates": [[v_coords[1], v_coords[0]], [hw_target[1], hw_target[0]]],
                "distance_m": hw_dist,
                "duration_sec": hw_dur_sec
            }
        }
    }

def process_district(district_file, max_villages=None, force=False):
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

    # Incremental Cache Loading
    cached_map = {}
    if os.path.exists(out_file) and not force:
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
                for pv in prev_data.get("villages", []):
                    if "dense_road_routing" in pv and pv["dense_road_routing"].get("hospital_route"):
                        cached_map[pv["id"]] = pv
        except Exception:
            cached_map = {}

    to_compute = []
    final_villages = []
    cache_hits = 0

    for v in villages:
        vid = v["id"]
        if vid in cached_map:
            final_villages.append(cached_map[vid])
            cache_hits += 1
        else:
            to_compute.append(v)

    print(f"▶️ Processing {district_slug.title()} ({state_slug.title()}): {len(villages)} total | ♻️ {cache_hits} cached (0ms) | ⚡ {len(to_compute)} to compute...")
    start_t = time.time()

    if to_compute:
        with ThreadPoolExecutor(max_workers=8) as executor:
            for res in executor.map(process_village_dense, to_compute):
                final_villages.append(res)

    output_doc = {
        "edition": "VPS_HEAVY_FULL_RESOLUTION",
        "district": data["district"],
        "state": data["state"],
        "state_slug": state_slug,
        "district_slug": district_slug,
        "analytics": data.get("analytics", {}),
        "total_dense_settlements": len(final_villages),
        "cache_hits": cache_hits,
        "newly_computed": len(to_compute),
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "villages": final_villages
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_doc, f, indent=2)

    elapsed = time.time() - start_t
    size_kb = round(os.path.getsize(out_file) / 1024, 1)
    rate = len(to_compute) / max(elapsed, 0.001) if to_compute else 0
    print(f"✅ Finished {district_slug.title()} in {elapsed:.1f}s ({rate:.1f} villages/s) | Size: {size_kb} KB -> {out_file}")

def main():
    parser = argparse.ArgumentParser(description="OpenMapIndia VPS Batch Full-Resolution Road Generator")
    parser.add_argument("--state", type=str, help="State slug (e.g. uttar_pradesh)")
    parser.add_argument("--district", type=str, help="District slug (e.g. basti)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of villages per district for testing")
    parser.add_argument("--force", action="store_true", help="Force recomputing cached routes")
    parser.add_argument("--all", action="store_true", help="Process all districts across India")
    args = parser.parse_args()

    if args.state and args.district:
        dist_path = os.path.join(DISTRICTS_DIR, args.state, f"{args.district}.json")
        if os.path.exists(dist_path):
            process_district(dist_path, args.limit, args.force)
        else:
            print(f"❌ File not found: {dist_path}")
    elif args.all:
        all_districts = sorted(glob.glob(os.path.join(DISTRICTS_DIR, "*", "*.json")))
        print(f"🌍 Found {len(all_districts)} districts to process. Starting batch run...")
        for idx, dist_file in enumerate(all_districts):
            print(f"\n[{idx+1}/{len(all_districts)}]")
            try:
                process_district(dist_file, args.limit, args.force)
            except Exception as e:
                print(f"⚠️ Error on {dist_file}: {e}")
    else:
        print("💡 Usage:")
        print("  python3 build_full_india.py --state uttar_pradesh --district basti --limit 100")
        print("  python3 build_full_india.py --all")

if __name__ == "__main__":
    main()
