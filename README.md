# 🇮🇳 India Universal Geocompute Engine

> **A 100% GitHub-Native, Zero-Cost, Precomputed Geocompute & Routing Infrastructure for India.**  
> Covers every State, District, Village, Primary Health Centre (PHC/CHC), and Highway corridor with zero backend, zero API keys, and zero cloud hosting fees.

---

## 📊 Dataset Scale & Statistics

| Metric | Precomputed Coverage |
| :--- | :--- |
| **States & Union Territories** | **35 States & UTs** |
| **Districts Indexed** | **594 Districts** |
| **Settlements (Villages, Towns, Hamlets)** | **373,988 Settlements** |
| **Health Facilities (PHCs, CHCs, Hospitals, Clinics)** | **128,062 Facilities** |
| **Major Arterial Highway Segments (NH / SH)** | **406,119 Segments** |
| **Total Compressed Transfer Size** | **≈ 22 MB** |
| **Runtime Infrastructure Required** | **None (100% Static on GitHub CDN)** |

---

## ⚡ Quickstart for Developers (Copy & Paste Ready)

### JavaScript / TypeScript (Browser, React, React Native, Node.js)

```javascript
// Drop into any app (zero dependencies):
async function getVillageRouting(stateSlug, districtSlug, villageName) {
  const CDN = "https://cdn.jsdelivr.net/gh/<YOUR_GITHUB_USER>/<REPO_NAME>@main/api/v1";
  
  // 1. Fetch the district package (auto-cached by browser & CDN)
  const res = await fetch(`${CDN}/districts/${stateSlug}/${districtSlug}.json`);
  const district = await res.json();

  // 2. Instant in-memory lookup (0ms)
  const village = district.villages.find(v => 
    v.name.toLowerCase() === villageName.toLowerCase().trim()
  );

  return village;
}

// Example:
getVillageRouting("uttar_pradesh", "basti", "Kalwari").then(v => {
  console.log("Village Coords:", v.coords);
  console.log("Nearest Hospital:", v.precomputed_routing.nearest_health.name);
  console.log("Hospital Distance:", v.precomputed_routing.nearest_health.distance_m, "meters");
  console.log("Nearest Highway:", v.precomputed_routing.nearest_highway.ref);
  console.log("Highway Distance:", v.precomputed_routing.nearest_highway.distance_m, "meters");
});
```

---

### Python

```python
import json
import urllib.request

def get_village(state_slug, district_slug, village_name):
    url = f"https://cdn.jsdelivr.net/gh/<YOUR_GITHUB_USER>/<REPO_NAME>@main/api/v1/districts/{state_slug}/{district_slug}.json"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())
    
    for v in data["villages"]:
        if v["name"].lower() == village_name.lower().strip():
            return v
    return None

v = get_village("maharashtra", "pune", "Talegaon Dabhade")
print(v["precomputed_routing"])
```

---

## 🌐 The Hyperlinked HATEOAS Graph

Navigate the entire nation without hardcoded URLs:

```
[National Root]     https://cdn.jsdelivr.net/gh/.../api/v1/india.json
                             │
                             ├──> States List: UP, MH, BR, KA, ...
                             │
[State Dossier]     https://cdn.jsdelivr.net/gh/.../api/v1/states/uttar_pradesh.json
                             │
                             ├──> Districts List: basti, gorakhpur, ...
                             │
[District Package]  https://cdn.jsdelivr.net/gh/.../api/v1/districts/uttar_pradesh/basti.json
                             │
                             ├──> Bounding Box & Metadata
                             └──> 4,702 Villages with precomputed vectors
```

---

## 📦 District JSON Schema

Every district file (`api/v1/districts/<state>/<district>.json`) contains:

```json
{
  "district": "Basti",
  "state": "Uttar Pradesh",
  "state_slug": "uttar_pradesh",
  "district_slug": "basti",
  "bbox": [82.45, 26.65, 83.15, 27.15],
  "total_settlements": 4702,
  "villages": [
    {
      "id": 245750772,
      "name": "Kalwari",
      "type": "village",
      "coords": [26.639246, 82.680327],
      "precomputed_routing": {
        "nearest_health": {
          "name": "PHC AMNAIKEPUR",
          "type": "centre",
          "distance_m": 6887,
          "polyline": "i~qaDaoswNyfHee@"
        },
        "nearest_highway": {
          "ref": "NH28",
          "grade": "trunk",
          "distance_m": 521,
          "junction_coord": [26.642981, 82.680648],
          "polyline": "i~qaDaoswNiV_A"
        }
      }
    }
  ]
}
```

---

## 🛠️ How to Rebuild or Update Data

This entire dataset was generated using the included batch scripts:
1. `extract_all.py` / `extract_highways.py`: Streams through `india.osm.pbf` in 1 pass.
2. `precompute_districts.py`: Vectorized STRtree spatial partitioning and KD-Tree vector computation.
3. `build_indexes.py`: Generates the national root, state dossiers, and SDKs.

To run the whole pipeline locally:
```bash
./run_pipeline.sh
```

---

## 📄 License
Open Data Commons Open Database License (ODbL) / MIT for code and SDKs.
