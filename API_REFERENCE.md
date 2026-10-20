# 📚 OpenMapIndia — Complete API Reference & Endpoint Directory

OpenMapIndia is a **100% static, hyperlinked JSON API** hosted directly on GitHub and served via the jsDelivr global CDN with zero rate-limit blocks and zero token authentication.

```
CDN Base URL: https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1
Localhost URL: http://localhost:8000/api/v1
```

---

## 1. National Root Endpoint

* **URL**: `https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1/india.json`
* **Localhost**: `http://localhost:8000/api/v1/india.json`
* **Method**: `GET`
* **Description**: Returns all 35 States & Union Territories, total settlement counts, and national infrastructure accessibility metrics.

### Sample Response:
```json
{
  "project": "OpenMapIndia",
  "version": "1.0.0",
  "country": "India",
  "iso": "IND",
  "stats": {
    "total_states": 35,
    "total_districts": 594,
    "total_settlements": 373988
  },
  "national_analytics": {
    "avg_infrastructure_score": 77.9,
    "avg_distance_to_phc_km": 6.24,
    "avg_villages_under_5km_highway_pct": 77.4
  },
  "states": [
    {
      "state": "Uttar Pradesh",
      "state_slug": "uttar_pradesh",
      "total_districts": 70,
      "analytics": {
        "avg_infrastructure_score": 81.2,
        "avg_phc_distance_km": 4.1,
        "pct_villages_under_5km_highway": 79.5
      },
      "_ref": "./states/uttar_pradesh.json"
    }
  ]
}
```

---

## 2. State Dossier Endpoints (All 35 States & UTs)

To get all districts in a state, append `/states/<state_slug>.json`:

| State / UT | Slug | API Endpoint URL |
| :--- | :--- | :--- |
| **Uttar Pradesh** | `uttar_pradesh` | `.../api/v1/states/uttar_pradesh.json` |
| **Maharashtra** | `maharashtra` | `.../api/v1/states/maharashtra.json` |
| **Bihar** | `bihar` | `.../api/v1/states/bihar.json` |
| **Madhya Pradesh** | `madhya_pradesh` | `.../api/v1/states/madhya_pradesh.json` |
| **West Bengal** | `west_bengal` | `.../api/v1/states/west_bengal.json` |
| **Tamil Nadu** | `tamil_nadu` | `.../api/v1/states/tamil_nadu.json` |
| **Rajasthan** | `rajasthan` | `.../api/v1/states/rajasthan.json` |
| **Karnataka** | `karnataka` | `.../api/v1/states/karnataka.json` |
| **Gujarat** | `gujarat` | `.../api/v1/states/gujarat.json` |
| **Andhra Pradesh** | `andhra_pradesh` | `.../api/v1/states/andhra_pradesh.json` |
| **Odisha** | `orissa` | `.../api/v1/states/orissa.json` |
| **Kerala** | `kerala` | `.../api/v1/states/kerala.json` |
| **Jharkhand** | `jharkhand` | `.../api/v1/states/jharkhand.json` |
| **Assam** | `assam` | `.../api/v1/states/assam.json` |
| **Punjab** | `punjab` | `.../api/v1/states/punjab.json` |
| **Chhattisgarh** | `chhattisgarh` | `.../api/v1/states/chhattisgarh.json` |
| **Haryana** | `haryana` | `.../api/v1/states/haryana.json` |
| **Delhi** | `delhi` | `.../api/v1/states/delhi.json` |
| **Jammu & Kashmir** | `jammu_and_kashmir`| `.../api/v1/states/jammu_and_kashmir.json` |
| **Uttarakhand** | `uttaranchal` | `.../api/v1/states/uttaranchal.json` |
| **Himachal Pradesh** | `himachal_pradesh`| `.../api/v1/states/himachal_pradesh.json` |
| **Tripura** | `tripura` | `.../api/v1/states/tripura.json` |
| **Meghalaya** | `meghalaya` | `.../api/v1/states/meghalaya.json` |
| **Manipur** | `manipur` | `.../api/v1/states/manipur.json` |
| **Nagaland** | `nagaland` | `.../api/v1/states/nagaland.json` |
| **Goa** | `goa` | `.../api/v1/states/goa.json` |
| **Arunachal Pradesh**| `arunachal_pradesh`| `.../api/v1/states/arunachal_pradesh.json`|
| **Mizoram** | `mizoram` | `.../api/v1/states/mizoram.json` |
| **Sikkim** | `sikkim` | `.../api/v1/states/sikkim.json` |
| **Puducherry** | `puducherry` | `.../api/v1/states/puducherry.json` |
| **Chandigarh** | `chandigarh` | `.../api/v1/states/chandigarh.json` |
| **A & N Islands** | `andaman_and_nicobar`| `.../api/v1/states/andaman_and_nicobar.json`|
| **Dadra & Nagar** | `dadra_and_nagar_haveli`| `.../api/v1/states/dadra_and_nagar_haveli.json`|
| **Daman & Diu** | `daman_and_diu` | `.../api/v1/states/daman_and_diu.json` |
| **Lakshadweep** | `lakshadweep` | `.../api/v1/states/lakshadweep.json` |

---

## 3. District Package Endpoints (Sample Highlights)

Each district endpoint delivers all villages, coordinates, nearest PHC/hospital, nearest highway junction, and district infrastructure analytics:

* **Pattern**: `.../api/v1/districts/<state_slug>/<district_slug>.json`

### Key District Endpoints:
* **Basti (UP)**: `.../api/v1/districts/uttar_pradesh/basti.json` (4,702 settlements)
* **Sant Kabir Nagar (UP)**: `.../api/v1/districts/uttar_pradesh/sant_kabir_nagar.json` (2,180 settlements)
* **Gorakhpur (UP)**: `.../api/v1/districts/uttar_pradesh/gorakhpur.json` (3,410 settlements)
* **Lucknow (UP)**: `.../api/v1/districts/uttar_pradesh/lucknow.json`
* **Varanasi (UP)**: `.../api/v1/districts/uttar_pradesh/varanasi.json`
* **Pune (MH)**: `.../api/v1/districts/maharashtra/pune.json`
* **Bangalore (KA)**: `.../api/v1/districts/karnataka/bangalore.json`
* **Patna (BR)**: `.../api/v1/districts/bihar/patna.json`
* **Wayanad (KL)**: `.../api/v1/districts/kerala/wayanad.json`

---

## 4. Village Routing Object Schema

Inside any district file, each settlement in the `villages` array has this exact structure:

```json
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
```

### Decoding Polylines
Polylines are encoded using the standard Google / OSRM algorithm (precision: 5 decimals). You can decode them in any language or map library (MapLibre, Mapbox, Leaflet, Google Maps, Turf.js):

```javascript
import polyline from '@mapbox/polyline';

// Returns [[lat, lon], ...]
const points = polyline.decode("i~qaDaoswNyfHee@");
```
