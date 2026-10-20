# 🇮🇳 OpenMapIndia

> **100% GitHub-Native Geocompute, Rural Routing & Infrastructure Intelligence for India.**  
> Covers every State, District, Village, Primary Health Centre (PHC/CHC), and Highway corridor with zero backend, zero API keys, and zero cloud hosting fees.

---

## 🚀 Live Interactive Demo (Localhost & GitHub Pages)

* **Localhost Preview (Active Now)**:  
  👉 **[http://localhost:8000/](http://localhost:8000/)**
* **GitHub Pages (After Push)**:  
  👉 **`https://maniratansingh.github.io/open-map-india/`**

### What You Can Do in the Live Demo:
* **Interactive Dropdowns**: Select any of India's **35 States & UTs** $\rightarrow$ select any of **594 Districts** $\rightarrow$ search across **373,988 Villages**.
* **Instant Visual Vector Draw**: High-speed WebGL map plots the village, its nearest emergency hospital (with distance and route), and its nearest arterial highway connection.
* **District Infrastructure Analytics**: Live scores measuring healthcare accessibility and highway connectivity for every district in India.

---

## 🛡️ 100% Zero-External API Architecture (Git-Native & Bulletproof)

OpenMapIndia is strictly designed to be **100% self-contained on GitHub Pages** with **ZERO external API dependencies**:
* **Zero External Routing APIs**: We do NOT proxy or depend on third-party routing services (like OSRM demo servers or Google Directions). All rural health vectors and highway connections are precomputed offline and served statically from this Git repository.
* **Zero External Geocoders**: Universal predictive search runs 100% client-side from [`api/v1/search_index.json`](file:///Users/mrps/Documents/MAP/api/v1/search_index.json) in 0ms without hitting rate-limited geocoding APIs.
* **Strict Indian Territorial Boundary**: Enforced bounding box (`68.0°E` to `97.5°E`, `6.5°N` to `37.2°N`). Foreign coordinates outside India are hard-blocked at the boundary.
* **National Highway Corridor Solver**: Point A ➔ Point B navigation uses an in-browser highway corridor algorithm that routes across India's National Highway network connecting district hubs offline.
* **Heavy VPS Edition (Isolated)**: For developers who want to run a multi-gigabyte dense turn-by-turn road server on their own VPS or localhost, see the isolated [`vps_heavy_edition/`](file:///Users/mrps/Documents/MAP/vps_heavy_edition/) folder (strictly excluded from Git to prevent repository bloat).

---

## 📚 Complete API Reference & Documentation

* **Complete State-Wise District Directory (594 Districts Linked)**:  
  👉 Browse the [**DISTRICT_DIRECTORY.md**](DISTRICT_DIRECTORY.md) for direct links to all 594 district datasets!
* **API Documentation & Schema Reference**:  
  👉 Read the [**API_REFERENCE.md**](API_REFERENCE.md)

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
  const CDN = "https://cdn.jsdelivr.net/gh/maniratansingh/open-map-india@main/api/v1";
  
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
    url = f"https://cdn.jsdelivr.net/gh/maniratansingh/open-map-india@main/api/v1/districts/{state_slug}/{district_slug}.json"
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

## 🔄 Updating the Dataset (Keeping Data Fresh)

Whenever OpenStreetMap releases new roads, or new hospitals/bypasses are added to India:

```bash
./update_dataset.sh
```

This single command:
1. Downloads the newest `india-latest.osm.pbf` diff.
2. Extracts updated settlements, hospitals, and highways.
3. Recomputes all 594 district packages and infrastructure analytics.
4. Updates state and national indexes.

---

## 📄 License
Open Data Commons Open Database License (ODbL) / MIT for Code, Frontend, and SDKs.
