# 🖥️ OpenMapIndia — VPS Heavy Edition (Branch: `vps-heavy`)

[![Branch: vps-heavy](https://img.shields.io/badge/Branch-vps--heavy-purple.svg)](https://github.com/maniratansingh/open-map-india/tree/vps-heavy)
[![Edition: VPS Heavy Server](https://img.shields.io/badge/Edition-VPS%20Heavy%20Routing%20Engine-blue.svg)](vps_heavy_edition/)
[![Zero External API](https://img.shields.io/badge/Routing-Self--Hosted%20%2F%20Zero--External-brightgreen.svg)](#-architecture-overview)
[![Districts Indexed](https://img.shields.io/badge/Districts%20Indexed-594%20Districts-orange.svg)](INDIA_DIRECTORY.md)
[![License: ODbL / MIT](https://img.shields.io/badge/License-ODbL%20%2F%20MIT-blue.svg)](#-license)

> **Dedicated High-Compute & Full-Resolution Routing Engine Branch.**  
> Contains the high-performance Python server, batch builders, and configurations to generate and serve multi-gigabyte dense turn-by-turn road curvatures, dynamic live routing, and high-throughput infrastructure analytics for all of India.
> 
> 🌐 **Looking for the lightweight 100% GitHub-native release?**  
> Switch to the [**`main` branch**](https://github.com/maniratansingh/open-map-india/tree/main) for the zero-cost, static CDN-powered edition (≈ 22 MB).

---

## 🏗️ Architecture: GitHub Edition vs. VPS Heavy Edition

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │                  OPENMAPINDIA PLATFORM                 │
                                  └──────────────────────────┬─────────────────────────────┘
                                                             │
                             ┌───────────────────────────────┴───────────────────────────────┐
                             │                                                               │
                             ▼                                                               ▼
             ┌───────────────────────────────┐                               ┌───────────────────────────────┐
             │       🌐 MAIN BRANCH          │                               │      🖥️ VPS-HEAVY BRANCH       │
             │   100% Lightweight GitHub     │                               │     Dedicated VPS Heavy       │
             └───────────────┬───────────────┘                               └───────────────┬───────────────┘
                             │                                                               │
             ├── 22 MB Total Footprint                                       ├── Multi-GB Dense Road Storage
             ├── Static Precomputed Endpoints                                ├── Live Dynamic Road Routing Engine
             ├── In-Browser Highway Corridor Solver                          ├── Batch Dense Geometry Generator
             ├── Hosted 100% Free on GitHub Pages                            ├── Self-Hosted on VPS (Ubuntu/Debian)
             └── Free jsDelivr / Cloudflare CDN                              └── Systemd Daemon & Nginx Reverse Proxy
```

---

## 💻 Recommended VPS Hardware Specifications

| Deployment Profile | vCPU | RAM | NVMe SSD | Network | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development & Testing** | 2 vCPUs | 4 GB | 40 GB SSD | 1 Gbps | Localhost test, single-state dense batch |
| **State-Level Production** | 4 vCPUs | 8 GB | 80 GB NVMe | 1 Gbps | High-load state portal, dynamic `/route` |
| **All-India High-Throughput** | 8 vCPUs | 16 GB | 160 GB NVMe | 2.5 Gbps | All 594 districts, 10,000+ req/sec |

*Supported Operating Systems: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS, Debian 12, Rocky Linux 9, Arch Linux.*

---

## 📁 Repository Directory Structure

```
open-map-india/
├── README.md                          <-- Master VPS Heavy documentation (this file)
├── index.html                         <-- High-speed WebGL Interactive Visualizer
├── DISTRICT_DIRECTORY.md              <-- State-by-State 594 District Catalog
├── INDIA_DIRECTORY.md                 <-- All-India A-to-Z Master Directory & Rankings
├── API_REFERENCE.md                   <-- Complete API & Schema Specification
├── api/
│   └── v1/
│       ├── states/                    <-- 35 State packages
│       ├── districts/                 <-- 594 District datasets (373,988 settlements)
│       ├── national_corridors.json    <-- Trans-India National Highway topology
│       └── search_index.json          <-- Universal predictive search database
├── scripts/
│   ├── python/                        <-- Extractor and precomputation pipeline
│   │   ├── extract_all.py             <-- OSM planet extract parser (PHCs, CHCs, places)
│   │   ├── extract_highways.py        <-- National & State Highway segment indexer
│   │   ├── precompute_districts.py    <-- District vector & analytics precomputer
│   │   └── build_indexes.py           <-- National and state index generator
│   └── bash/                          <-- Automated pipeline execution
│       ├── run_pipeline.sh            <-- Sequential dataset build workflow
│       └── update_dataset.sh          <-- Automatic upstream OSM refresh script
└── vps_heavy_edition/
    ├── README.md                      <-- In-depth VPS deployment & systemd guide
    ├── server.py                      <-- Production Python API Server (CORS + Routing)
    ├── build_full_india.py            <-- Batch builder for multi-GB dense road curves
    └── data/                          <-- Stored on VPS NVMe disk (Ignored by Git)
        ├── india.osm.pbf              <-- Raw OpenStreetMap planet extract
        └── full_routes/               <-- High-density road curves for all 594 districts
```

---

## 🚀 Quick Deployment Guide on VPS

### 1. Clone the `vps-heavy` Branch
```bash
git clone -b vps-heavy https://github.com/maniratansingh/open-map-india.git
cd open-map-india
```

### 2. Set Up Virtual Environment & Dependencies
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git curl
python3 -m venv .venv
source .venv/bin/activate
pip install urllib3 requests
```

### 3. Start the High-Performance API Server
```bash
python3 vps_heavy_edition/server.py --port 8080 --host 0.0.0.0
```

Verify the health check:
```bash
curl http://localhost:8080/health
```

---

## ⚡ Generating Dense Road Curvatures (`build_full_india.py`)

To compute dense turn-by-turn road curves for all villages in a district and store them locally on VPS disk:

```bash
# Test run for 20 villages in Basti district:
python3 vps_heavy_edition/build_full_india.py --state uttar_pradesh --district basti --limit 20

# Run complete district:
python3 vps_heavy_edition/build_full_india.py --state uttar_pradesh --district basti

# Run all 594 districts in the background:
nohup python3 vps_heavy_edition/build_full_india.py --all > build_full.log 2>&1 &
tail -f build_full.log
```

Generated dense files are saved to `vps_heavy_edition/data/full_routes/<state>/<district>.json`.

---

## 🌐 VPS API Reference & Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | Server status, version, and routing engine health |
| `/route?from_lat=...&from_lon=...&to_lat=...&to_lon=...` | `GET` | Dynamic real-time turn-by-turn road route |
| `/api/v1/full_routes/<state>/<district>.json` | `GET` | Dense turn-by-turn geometries for all district villages |
| `/api/v1/districts/<state>/<district>.json` | `GET` | Precomputed rural healthcare & highway vector bundle |
| `/api/v1/search_index.json` | `GET` | Universal national predictive search database |

### Example: Dynamic Turn-by-Turn Routing Request
```bash
curl "http://localhost:8080/route?from_lat=26.6394&from_lon=82.6806&to_lat=26.7995&to_lon=82.7981"
```

---

## ⚙️ Production Deployment (Systemd & Nginx)

For complete instructions on running OpenMapIndia as an automated system service with Nginx reverse proxy, gzip acceleration, SSL (Let's Encrypt), and local offline OSRM Docker container, see:

👉 [**vps_heavy_edition/README.md**](vps_heavy_edition/README.md)

---

## 📚 Master Catalog & Documentation

* **[Whole India Master Directory](INDIA_DIRECTORY.md)** — All 594 districts indexed A-to-Z with national infrastructure rankings.
* **[State-Wise District Directory](DISTRICT_DIRECTORY.md)** — State-by-state catalog linking to every district dataset.
* **[API Reference Specification](API_REFERENCE.md)** — Complete schema definition and response models.
* **[VPS Heavy Edition Deployment Manual](vps_heavy_edition/README.md)** — Systemd, Nginx, Docker, and multi-GB road generation.

---

## 📄 License
Open Data Commons Open Database License (ODbL) / MIT for Code, Frontend, and Server Software.
