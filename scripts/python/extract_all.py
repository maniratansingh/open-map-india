#!/usr/bin/env python3
"""
Step 1: Universal OSM Extractor for India
Extracts all Villages, Health Infrastructure, and Major Highway Corridors
from india.osm.pbf using osmium in a single high-speed streaming pass.
"""

import gzip
import json
import os
import sys
import time
import osmium

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(REPO_ROOT)

PBF_PATH = "india_tiles/india.osm.pbf"
OUT_DIR = "data/extracted"

os.makedirs(OUT_DIR, exist_ok=True)

class IndiaUniversalExtractor(osmium.SimpleHandler):
    def __init__(self, f_villages, f_health, f_highways):
        super().__init__()
        self.f_villages = f_villages
        self.f_health = f_health
        self.f_highways = f_highways
        
        self.village_count = 0
        self.health_count = 0
        self.highway_count = 0
        self.start_time = time.time()
        self.last_log = time.time()

    def node(self, n):
        # 1. Villages, hamlets, towns
        if 'place' in n.tags and n.tags['place'] in ('village', 'hamlet', 'town', 'isolated_dwelling'):
            if n.location.valid():
                name = n.tags.get('name', n.tags.get('name:en', 'Unnamed'))
                record = {
                    'id': n.id,
                    'name': name,
                    'type': n.tags['place'],
                    'lat': round(n.location.lat, 6),
                    'lon': round(n.location.lon, 6)
                }
                self.f_villages.write(json.dumps(record) + '\n')
                self.village_count += 1

        # 2. Healthcare facilities (PHC, CHC, Hospital, Clinic)
        is_health = False
        health_type = None
        if 'amenity' in n.tags and n.tags['amenity'] in ('hospital', 'clinic', 'doctors', 'health_post'):
            is_health = True
            health_type = n.tags['amenity']
        elif 'healthcare' in n.tags:
            is_health = True
            health_type = n.tags['healthcare']

        if is_health and n.location.valid():
            name = n.tags.get('name', n.tags.get('name:en', 'Unnamed Health Facility'))
            record = {
                'id': n.id,
                'name': name,
                'type': health_type,
                'lat': round(n.location.lat, 6),
                'lon': round(n.location.lon, 6),
                'emergency': n.tags.get('emergency', 'unknown'),
                'beds': n.tags.get('beds', None)
            }
            self.f_health.write(json.dumps(record) + '\n')
            self.health_count += 1

        if time.time() - self.last_log > 10:
            elapsed = time.time() - self.start_time
            print(f"[{elapsed:.1f}s] Extracted {self.village_count:,} settlements, {self.health_count:,} health facilities...")
            self.last_log = time.time()

    def way(self, w):
        # 3. Major arterial highway corridors (Motorway, Trunk, Primary, Secondary)
        if 'highway' in w.tags and w.tags['highway'] in ('motorway', 'trunk', 'primary', 'secondary'):
            try:
                coords = [(round(n.lat, 6), round(n.lon, 6)) for n in w.nodes if n.valid()]
                if len(coords) >= 2:
                    name = w.tags.get('name', w.tags.get('name:en', 'Unnamed Road'))
                    ref = w.tags.get('ref', None)
                    record = {
                        'id': w.id,
                        'name': name,
                        'ref': ref,
                        'grade': w.tags['highway'],
                        'coords': coords
                    }
                    self.f_highways.write(json.dumps(record) + '\n')
                    self.highway_count += 1
            except Exception:
                pass

def main():
    print("=" * 60)
    print("🚀 Starting All-India Asset Extraction from OSM PBF")
    print(f"Source: {PBF_PATH}")
    print(f"Output Directory: {OUT_DIR}")
    print("=" * 60)

    start_time = time.time()

    with gzip.open(os.path.join(OUT_DIR, "villages.jsonl.gz"), "wt", encoding="utf-8") as f_villages, \
         gzip.open(os.path.join(OUT_DIR, "health.jsonl.gz"), "wt", encoding="utf-8") as f_health, \
         gzip.open(os.path.join(OUT_DIR, "highways.jsonl.gz"), "wt", encoding="utf-8") as f_highways:

        extractor = IndiaUniversalExtractor(f_villages, f_health, f_highways)
        extractor.apply_file(PBF_PATH, locations=True, idx='flex_mem')

    total_time = time.time() - start_time
    print("=" * 60)
    print(f"✅ Extraction Complete in {total_time:.1f} seconds ({total_time/60:.2f} mins)!")
    print(f"📦 Total Settlements Extracted: {extractor.village_count:,}")
    print(f"🏥 Total Health Facilities:     {extractor.health_count:,}")
    print(f"🛣️  Total Highway Segments:       {extractor.highway_count:,}")
    print("=" * 60)

if __name__ == "__main__":
    main()
