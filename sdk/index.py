"""
OpenMapIndia - Zero-Dependency Python SDK
Precomputed Geocompute, Rural Routing & Infrastructure Intelligence for India
"""
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
