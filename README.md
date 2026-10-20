# 🇮🇳 OpenMapIndia

> **100% GitHub-Native Geocompute, Rural Routing & Infrastructure Intelligence for India.**  
> Covers every State, District, Village, Primary Health Centre (PHC/CHC), and Highway corridor with zero backend, zero API keys, and zero cloud hosting fees.

---

## 🚀 Live Interactive Demo (GitHub Pages)

Experience the dataset live directly in your browser:  
🔗 **[https://<your-username>.github.io/<your-repo-name>/](https://<your-username>.github.io/<your-repo-name>/)**

* **Interactive Search**: Select any of India's 35 States & UTs, pick any of 594 Districts, and search across 373,988 villages.
* **Instant Visual Vector Draw**: High-speed WebGL map automatically plots the village, its nearest emergency hospital (with road distance and route), and its nearest arterial highway connection.
* **District Infrastructure Analytics**: Live scores measuring healthcare accessibility and highway connectivity for every district in India.

---

## 📊 Dataset Scale & Infrastructure Analytics

| Metric | Precomputed Coverage |
| :--- | :--- |
| **States & Union Territories** | **35 States & UTs** (`api/v1/states/*.json`) |
| **Districts Indexed** | **594 Districts** (`api/v1/districts/*/*.json`) |
| **Settlements (Villages, Towns, Hamlets)** | **373,988 Settlements** |
| **Healthcare Facilities (PHCs, CHCs, Hospitals, Clinics)** | **128,062 Facilities** |
| **Major Arterial Highway Segments (NH / SH)** | **406,119 Segments** |
| **National Average Distance to Healthcare** | **6.24 km** |
| **Villages within 5km of an Arterial Highway** | **77.4%** |
| **Total Compressed Transfer Size** | **≈ 22 MB** |
| **Hosting & API Cost** | **$0 / Free forever on GitHub** |

---

## ⚡ Quickstart for Developers

### 1. JavaScript / TypeScript (Browser, Node, React, React Native)

```javascript
// Drop into any project with zero dependencies:
async function getVillageRouting(stateSlug, districtSlug, villageName) {
  const CDN = "https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1";
  
  // 1. Fetch the district package (auto-cached by browser & CDN)
  const res = await fetch(`${CDN}/districts/${stateSlug}/${districtSlug}.json`);
  const district = await res.json();

  // 2. Instant in-memory lookup (0ms)
  const village = district.villages.find(v => 
    v.name.toLowerCase() === villageName.toLowerCase().trim()
  );

  return {
    districtAnalytics: district.analytics,
    village
  };
}

// Example:
getVillageRouting("uttar_pradesh", "basti", "Kalwari").then(data => {
  console.log("District Score:", data.districtAnalytics.infrastructure_score);
  console.log("Nearest Hospital:", data.village.precomputed_routing.nearest_health.name);
  console.log("Road Distance:", data.village.precomputed_routing.nearest_health.distance_m, "meters");
  console.log("Nearest Highway:", data.village.precomputed_routing.nearest_highway.ref);
});
```

---

### 2. Python (FastAPI, Flask, Pandas, Django)

```python
import json
import urllib.request

def get_village(state_slug, district_slug, village_name):
    url = f"https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1/districts/{state_slug}/{district_slug}.json"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())
    
    for v in data["villages"]:
        if v["name"].lower() == village_name.lower().strip():
            return {"analytics": data["analytics"], "village": v}
    return None

res = get_village("maharashtra", "pune", "Talegaon Dabhade")
print("Analytics:", res["analytics"])
print("Nearest Hospital:", res["village"]["precomputed_routing"]["nearest_health"])
```

---

## 📦 District JSON Schema

Every district file (`api/v1/districts/<state>/<district>.json`) contains:

```json
{
  "project": "OpenMapIndia",
  "district": "Basti",
  "state": "Uttar Pradesh",
  "state_slug": "uttar_pradesh",
  "district_slug": "basti",
  "bbox": [82.45, 26.65, 83.15, 27.15],
  "total_settlements": 4702,
  "analytics": {
    "infrastructure_score": 80.2,
    "avg_phc_distance_km": 3.91,
    "median_phc_distance_km": 3.8,
    "avg_highway_distance_km": 3.45,
    "pct_villages_under_2km_highway": 33.3,
    "pct_villages_under_5km_highway": 76.0,
    "pct_villages_under_5km_phc": 71.4
  },
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

## 🛠️ Rebuilding or Updating Data

Run the pipeline from scratch anytime:
```bash
./run_pipeline.sh
```

---

## 📄 License
Open Data Commons Open Database License (ODbL) / MIT for Code, Frontend, and SDKs.
