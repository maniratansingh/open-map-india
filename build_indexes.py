#!/usr/bin/env python3
"""
Step 3 (Enriched): OpenMapIndia Universal Index and SDK Generator
Aggregates district infrastructure analytics up to State and National levels,
and generates zero-dependency SDKs for JavaScript and Python.
"""

import json
import os
import glob
import numpy as np

API_BASE = "api/v1"
DISTRICTS_DIR = os.path.join(API_BASE, "districts")
STATES_DIR = os.path.join(API_BASE, "states")
NATIONAL_FILE = os.path.join(API_BASE, "india.json")
SDK_DIR = "sdk"

os.makedirs(STATES_DIR, exist_ok=True)
os.makedirs(SDK_DIR, exist_ok=True)

def main():
    print("=" * 60)
    print("🇮🇳 OpenMapIndia: Generating Rollup Indexes & SDKs...")
    print("=" * 60)

    states_map = {}
    total_districts = 0
    total_villages = 0
    all_scores = []
    all_phc_dists = []
    all_hw_pcts = []

    state_dirs = sorted([d for d in os.listdir(DISTRICTS_DIR) if os.path.isdir(os.path.join(DISTRICTS_DIR, d))])

    for state_slug in state_dirs:
        state_path = os.path.join(DISTRICTS_DIR, state_slug)
        dist_files = sorted(glob.glob(os.path.join(state_path, "*.json")))
        
        state_districts = []
        state_name = None
        state_scores = []
        state_phc_km = []
        state_hw_pct = []

        for fpath in dist_files:
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            state_name = d['state']
            v_count = d['total_settlements']
            analytics = d.get('analytics', {})

            total_villages += v_count
            total_districts += 1

            if analytics:
                s_score = analytics.get('infrastructure_score', 50.0)
                p_km = analytics.get('avg_phc_distance_km', 5.0)
                h_pct = analytics.get('pct_villages_under_5km_highway', 50.0)
                state_scores.append(s_score)
                state_phc_km.append(p_km)
                state_hw_pct.append(h_pct)
                all_scores.append(s_score)
                all_phc_dists.append(p_km)
                all_hw_pcts.append(h_pct)

            state_districts.append({
                'district': d['district'],
                'district_slug': d['district_slug'],
                'bbox': d['bbox'],
                'total_settlements': v_count,
                'analytics': analytics,
                '_ref': f"../districts/{state_slug}/{d['district_slug']}.json"
            })

        state_analytics = {
            'avg_infrastructure_score': round(float(np.mean(state_scores)), 1) if state_scores else 50.0,
            'avg_phc_distance_km': round(float(np.mean(state_phc_km)), 2) if state_phc_km else 5.0,
            'pct_villages_under_5km_highway': round(float(np.mean(state_hw_pct)), 1) if state_hw_pct else 50.0
        }

        states_map[state_slug] = {
            'project': "OpenMapIndia",
            'state': state_name or state_slug.replace('_', ' ').title(),
            'state_slug': state_slug,
            'total_districts': len(state_districts),
            'analytics': state_analytics,
            'districts': state_districts,
            '_links': {
                'national': "../india.json"
            }
        }

        state_out = os.path.join(STATES_DIR, f"{state_slug}.json")
        with open(state_out, "w", encoding="utf-8") as f:
            json.dump(states_map[state_slug], f, separators=(',', ':'))

    print(f"Generated {len(states_map)} State dossiers with infrastructure rollups.")

    national_doc = {
        'project': "OpenMapIndia",
        'version': "1.0.0",
        'country': "India",
        'iso': "IND",
        'stats': {
            'total_states': len(states_map),
            'total_districts': total_districts,
            'total_settlements': total_villages
        },
        'national_analytics': {
            'avg_infrastructure_score': round(float(np.mean(all_scores)), 1) if all_scores else 50.0,
            'avg_distance_to_phc_km': round(float(np.mean(all_phc_dists)), 2) if all_phc_dists else 5.0,
            'avg_villages_under_5km_highway_pct': round(float(np.mean(all_hw_pcts)), 1) if all_hw_pcts else 50.0
        },
        'states': [
            {
                'state': s['state'],
                'state_slug': s['state_slug'],
                'total_districts': s['total_districts'],
                'analytics': s['analytics'],
                '_ref': f"./states/{s['state_slug']}.json"
            }
            for s in states_map.values()
        ]
    }

    with open(NATIONAL_FILE, "w", encoding="utf-8") as f:
        json.dump(national_doc, f, indent=2)

    print(f"Generated National Root at {NATIONAL_FILE}.")

    # Generate JavaScript SDK
    js_sdk = """/**
 * OpenMapIndia - Zero-Dependency JS SDK
 * Precomputed Geocompute, Rural Routing & Infrastructure Intelligence for India
 */
class OpenMapIndia {
  constructor(cdnBase = "https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1") {
    this.cdnBase = cdnBase;
    this.cache = new Map();
  }

  async getNationalIndex() {
    const res = await fetch(`${this.cdnBase}/india.json`);
    return res.json();
  }

  async getState(stateSlug) {
    const res = await fetch(`${this.cdnBase}/states/${stateSlug}.json`);
    return res.json();
  }

  async getDistrict(stateSlug, districtSlug) {
    const key = `${stateSlug}:${districtSlug}`;
    if (this.cache.has(key)) return this.cache.get(key);

    const res = await fetch(`${this.cdnBase}/districts/${stateSlug}/${districtSlug}.json`);
    const data = await res.json();
    this.cache.set(key, data);
    return data;
  }

  async findVillage(stateSlug, districtSlug, query) {
    const pkg = await this.getDistrict(stateSlug, districtSlug);
    const q = query.toLowerCase().trim();
    return pkg.villages.find(v => v.name.toLowerCase() === q || String(v.id) === q);
  }
}

if (typeof module !== 'undefined') module.exports = OpenMapIndia;
"""
    with open(os.path.join(SDK_DIR, "index.js"), "w", encoding="utf-8") as f:
        f.write(js_sdk)

    # Generate Python SDK
    py_sdk = """\"\"\"
OpenMapIndia - Zero-Dependency Python SDK
Precomputed Geocompute, Rural Routing & Infrastructure Intelligence for India
\"\"\"
import json
import urllib.request

class OpenMapIndia:
    def __init__(self, cdn_base="https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1"):
        self.cdn_base = cdn_base.rstrip('/')
        self._cache = {}

    def _get(self, path):
        url = f"{self.cdn_base}/{path}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

    def get_national_index(self):
        return self._get("india.json")

    def get_state(self, state_slug):
        return self._get(f"states/{state_slug}.json")

    def get_district(self, state_slug, district_slug):
        key = (state_slug, district_slug)
        if key not in self._cache:
            self._cache[key] = self._get(f"districts/{state_slug}/{district_slug}.json")
        return self._cache[key]

    def find_village(self, state_slug, district_slug, name_or_id):
        dist = self.get_district(state_slug, district_slug)
        q = str(name_or_id).lower().strip()
        for v in dist.get('villages', []):
            if v['name'].lower() == q or str(v['id']) == q:
                return v
        return None
"""
    with open(os.path.join(SDK_DIR, "index.py"), "w", encoding="utf-8") as f:
        f.write(py_sdk)

    print(f"Updated SDKs in {SDK_DIR}/.")
    print("=" * 60)
    print("✅ OpenMapIndia: Indexes & SDKs Updated Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
