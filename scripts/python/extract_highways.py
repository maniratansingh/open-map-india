#!/usr/bin/env python3
"""
Step 1B: Extract Major Highway Corridors
Extracts all Motorway, Trunk, Primary, and Secondary Highways with exact GPS coordinates.
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
OUT_FILE = "data/extracted/highways.jsonl.gz"

class HighwayExtractor(osmium.SimpleHandler):
    def __init__(self, f_out):
        super().__init__()
        self.f_out = f_out
        self.count = 0
        self.start = time.time()
        self.last_log = time.time()

    def way(self, w):
        if 'highway' in w.tags and w.tags['highway'] in ('motorway', 'trunk', 'primary', 'secondary'):
            try:
                coords = [(round(n.lat, 6), round(n.lon, 6)) for n in w.nodes]
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
                    self.f_out.write(json.dumps(record) + '\n')
                    self.count += 1
            except Exception:
                pass

        if time.time() - self.last_log > 10:
            elapsed = time.time() - self.start
            print(f"[{elapsed:.1f}s] Extracted {self.count:,} major highway segments...")
            self.last_log = time.time()

def main():
    print("=" * 60)
    print("🛣️  Extracting Major Highway Corridors from India OSM PBF...")
    print("=" * 60)
    start_time = time.time()

    with gzip.open(OUT_FILE, "wt", encoding="utf-8") as f_out:
        extractor = HighwayExtractor(f_out)
        extractor.apply_file(PBF_PATH, locations=True, idx='flex_mem')

    total_time = time.time() - start_time
    print("=" * 60)
    print(f"✅ Highway Extraction Complete in {total_time:.1f}s ({total_time/60:.2f} mins)!")
    print(f"🛣️  Total Highway Segments Extracted: {extractor.count:,}")
    print("=" * 60)

if __name__ == "__main__":
    main()
