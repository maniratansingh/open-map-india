#!/usr/bin/env python3
"""
Step 3: Universal Index and SDK Generator
Traverses the generated `api/v1/districts` directory and generates:
- `api/v1/states/<state_slug>.json` (State dossiers linking to all its districts)
- `api/v1/india.json` (National root linking to all 36 states/UTs)
- `sdk/index.js` (Zero-dependency JavaScript client)
- `sdk/index.py` (Zero-dependency Python client)
"""

import json
import os
import glob

API_BASE = "api/v1"
DISTRICTS_DIR = os.path.join(API_BASE, "districts")
STATES_DIR = os.path.join(API_BASE, "states")
NATIONAL_FILE = os.path.join(API_BASE, "india.json")
SDK_DIR = "sdk"

os.makedirs(STATES_DIR, exist_ok=True)
os.makedirs(SDK_DIR, exist_ok=True)

def main():
    print("=" * 60)
    print("📚 Generating National, State Indexes and SDKs...")
    print("=" * 60)

    states_map = {}
    total_districts = 0
    total_villages = 0

    state_dirs = sorted([d for d in os.listdir(DISTRICTS_DIR) if os.path.isdir(os.path.join(DISTRICTS_DIR, d))])

    for state_slug in state_dirs:
        state_path = os.path.join(DISTRICTS_DIR, state_slug)
        dist_files = sorted(glob.glob(os.path.join(state_path, "*.json")))
        
        state_districts = []
        state_name = None

        for fpath in dist_files:
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            state_name = d['state']
            v_count = d['total_settlements']
            total_villages += v_count
            total_districts += 1

            state_districts.append({
                'district': d['district'],
                'district_slug': d['district_slug'],
                'bbox': d['bbox'],
                'total_settlements': v_count,
                '_ref': f"../districts/{state_slug}/{d['district_slug']}.json"
            })

        states_map[state_slug] = {
            'state': state_name or state_slug.replace('_', ' ').title(),
            'state_slug': state_slug,
            'total_districts': len(state_districts),
            'districts': state_districts,
            '_links': {
                'national': "../india.json"
            }
        }

        # Write state file
        state_out = os.path.join(STATES_DIR, f"{state_slug}.json")
        with open(state_out, "w", encoding="utf-8") as f:
            json.dump(states_map[state_slug], f, separators=(',', ':'))

    print(f"Generated {len(states_map)} State dossiers.")

    # Write national root
    national_doc = {
        'version': "1.0.0",
        'country': "India",
        'iso': "IND",
        'stats': {
            'total_states': len(states_map),
            'total_districts': total_districts,
            'total_settlements': total_villages
        },
        'states': [
            {
                'state': s['state'],
                'state_slug': s['state_slug'],
                'total_districts': s['total_districts'],
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
 * India Universal Geocompute Engine - Zero-Dependency JS SDK
 * Works directly in Browser, React, React Native, Node.js, and Bun.
 */
class IndiaGeoEngine {
  constructor(cdnBase = "https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1") {
    this.cdnBase = cdnBase;
    this.cache = new Map();
  }

  async getNationalIndex() {
    const res = await fetch(`${this.cdnBase}/india.json`);
    return res.json();
  }

  async getStateDossier(stateSlug) {
    const res = await fetch(`${this.cdnBase}/states/${stateSlug}.json`);
    return res.json();
  }

  async getDistrictPackage(stateSlug, districtSlug) {
    const key = `${stateSlug}:${districtSlug}`;
    if (this.cache.has(key)) return this.cache.get(key);

    const res = await fetch(`${this.cdnBase}/districts/${stateSlug}/${districtSlug}.json`);
    const data = await res.json();
    this.cache.set(key, data);
    return data;
  }

  async findVillage(stateSlug, districtSlug, query) {
    const pkg = await this.getDistrictPackage(stateSlug, districtSlug);
    const q = query.toLowerCase().trim();
    return pkg.villages.find(v => v.name.toLowerCase() === q || String(v.id) === q);
  }
}

if (typeof module !== 'undefined') module.exports = IndiaGeoEngine;
"""
    with open(os.path.join(SDK_DIR, "index.js"), "w", encoding="utf-8") as f:
        f.write(js_sdk)

    # Generate Python SDK
    py_sdk = """\"\"\"
India Universal Geocompute Engine - Zero-Dependency Python SDK
\"\"\"
import json
import urllib.request

class IndiaGeoEngine:
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

    print(f"Generated SDKs in {SDK_DIR}/.")
    print("=" * 60)
    print("✅ All Indexes and SDKs Generated Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
