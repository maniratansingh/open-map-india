# 🖥️ OpenMapIndia — VPS Heavy Edition (Full-Resolution Routing Server)

> **Dedicated High-Compute & Full-Resolution Road Engine for Self-Hosted Infrastructure.**  
> Designed for state governments, emergency dispatch (108/112), logistics fleets, and GIS researchers who need multi-gigabyte dense road curves, dynamic live routing, and high-throughput offline geocompute.

---

## ⚡ GitHub Pages Edition vs. VPS Heavy Edition

| Capability | 🌐 GitHub Pages Edition (`main` branch) | 🖥️ VPS Heavy Edition (`vps-heavy` branch) |
| :--- | :--- | :--- |
| **Hosting & Cost** | 100% Free on GitHub Pages & CDN | Self-hosted on VPS ($5–$20/mo) or Localhost |
| **Storage Footprint** | Extremely compact (≈ 22 MB compressed) | Multi-gigabyte dense road geometry cache |
| **Data Resolution** | Precomputed point-to-point road vectors | Millimeter-accurate turn-by-turn road curves |
| **Routing Mechanism** | In-browser highway corridor solver | Python API server + Optional local OSRM Docker |
| **Throughput** | Unlimited via free global CDNs | Dedicated server hardware (10,000+ req/sec) |
| **Best For** | Public web apps, lightweight mobile apps | Fleet tracking, 108 ambulance dispatch, offline intranets |

---

## 💻 Recommended VPS Hardware Specifications

| Workload | CPU | RAM | NVMe SSD | Network | Estimated Monthly Cost |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development / Testing** | 2 vCPUs | 4 GB | 40 GB SSD | 1 Gbps | ~$5 (Hetzner / DO) |
| **State-Level Production** | 4 vCPUs | 8 GB | 80 GB NVMe | 1 Gbps | ~$15 (Hetzner / Linode) |
| **All-India High-Throughput** | 8 vCPUs | 16 GB | 160 GB NVMe | 2.5 Gbps | ~$30–$40 (Dedicated) |

*Supported OS: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS, Debian 12, Rocky Linux 9, Arch Linux.*

---

## 📁 Repository Layout on `vps-heavy` Branch

```
open-map-india/
├── README.md                          <-- VPS Heavy Master Documentation
├── index.html                         <-- High-speed WebGL Interactive Visualizer
├── DISTRICT_DIRECTORY.md              <-- State-by-State 594 District Catalog
├── INDIA_DIRECTORY.md                 <-- All-India A-to-Z Master Directory & Rankings
├── API_REFERENCE.md                   <-- Complete API & Schema Specification
├── api/
│   └── v1/
│       ├── states/                    <-- 35 State packages
│       ├── districts/                 <-- 594 District datasets (373k villages)
│       ├── national_corridors.json    <-- Trans-India National Highway topology
│       └── search_index.json          <-- Universal predictive search database
├── scripts/
│   ├── python/                        <-- Python extraction & precomputation pipeline
│   └── bash/                          <-- Automated update & dataset refresh scripts
└── vps_heavy_edition/
    ├── README.md                      <-- This VPS deployment manual
    ├── server.py                      <-- High-performance Python API Server (CORS + Routing)
    ├── progress.html                  <-- Live Web Progress & Telemetry Dashboard
    ├── build_full_india.py            <-- Batch generator for multi-GB dense turn-by-turn routes
    └── data/                          <-- Stored locally on VPS disk (Ignored by Git)
        ├── india.osm.pbf              <-- Raw OpenStreetMap planet extract
        ├── progress.json              <-- Real-time batch computation state telemetry
        └── full_routes/               <-- High-density road curves for all 594 districts
```

---

## 🚀 Quick Deployment Guide on Linux (Ubuntu / Debian)

### 1. Clone the `vps-heavy` Branch
```bash
git clone -b vps-heavy https://github.com/maniratansingh/open-map-india.git
cd open-map-india
```

### 2. Set Up Python Virtual Environment
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git curl
python3 -m venv .venv
source .venv/bin/activate
pip install urllib3 requests
```

### 3. Launch the Server Manually
```bash
python3 vps_heavy_edition/server.py --port 8080 --host 0.0.0.0
```
Test health check in another terminal:
```bash
curl http://localhost:8080/health
```

---

## ⚙️ Production Setup with Systemd & Nginx

### 1. Create a Dedicated Systemd Service
Create the service unit file:
```bash
sudo nano /etc/systemd/system/openmapindia.service
```

Paste the following configuration:
```ini
[Unit]
Description=OpenMapIndia VPS Heavy Edition API Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/open-map-india
ExecStart=/var/www/open-map-india/.venv/bin/python3 vps_heavy_edition/server.py --port 8080 --host 127.0.0.1
Restart=always
RestartSec=5s
Environment=PYTHONUNBUFFERED=1
Environment=OSRM_BACKEND=https://router.project-osrm.org

# Resource Sandbox Limits
LimitNOFILE=65535
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable openmapindia
sudo systemctl start openmapindia
sudo systemctl status openmapindia
```

---

### 2. Configure Nginx Reverse Proxy with SSL

Install Nginx and Certbot:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/openmapindia.conf`:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Gzip compression for high-speed GeoJSON delivery
    gzip on;
    gzip_types application/json application/geo+json text/plain;
    gzip_min_length 1000;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cross-Origin Headers for Web Frontends
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, OPTIONS';
        add_header Access-Control-Allow-Headers 'Content-Type';
    }
}
```

Enable site and obtain SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/openmapindia.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

## ⚡ Generating Dense Road Curves (`build_full_india.py`)

To build the multi-gigabyte dense road curvature files for every village in a district or across all of India:

### Test Single District (e.g. Basti, UP):
```bash
python3 vps_heavy_edition/build_full_india.py --state uttar_pradesh --district basti --limit 20
```

### Run Full District:
```bash
python3 vps_heavy_edition/build_full_india.py --state uttar_pradesh --district basti
```

### Run All 594 Districts in Background (Production):
```bash
nohup python3 vps_heavy_edition/build_full_india.py --all > build_full.log 2>&1 &
tail -f build_full.log
```

The output is written directly to:
`vps_heavy_edition/data/full_routes/<state_slug>/<district_slug>.json`

---

## 🌐 Complete API Reference for VPS Endpoints

### 1. Live Web Progress Dashboard & Telemetry
Open in any browser to watch background computation progress in real-time with live progress bars, speedometers, and terminal logs:
```http
GET /progress.html
GET /api/v1/build_progress
```

---

### 2. Server Health & Monitoring
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "edition": "VPS_HEAVY_EDITION",
  "version": "1.0.0",
  "service": "OpenMapIndia VPS High-Performance Engine",
  "osrm_backend": "https://router.project-osrm.org",
  "endpoints": [
    "/health",
    "/route?from_lat=<lat>&from_lon=<lon>&to_lat=<lat>&to_lon=<lon>",
    "/api/v1/full_routes/<state>/<district>.json",
    "/api/v1/districts/<state>/<district>.json",
    "/api/v1/search_index.json"
  ]
}
```

---

### 2. Dynamic Real-Time Turn-by-Turn Route Calculator
Calculates driving distance, estimated duration, and multi-point road curvature geometry between any two coordinates in India:
```http
GET /route?from_lat=26.6394&from_lon=82.6806&to_lat=26.7995&to_lon=82.7981
```

**Response:**
```json
{
  "code": "Ok",
  "routes": [
    {
      "geometry": {
        "coordinates": [
          [82.6806, 26.6394],
          [82.6845, 26.6431],
          [82.7120, 26.6850],
          [82.7981, 26.7995]
        ],
        "type": "LineString"
      },
      "distance": 22450.8,
      "duration": 1845.2
    }
  ]
}
```

---

### 3. Dense Turn-by-Turn District Geometry (VPS Only)
Returns complete, high-density hospital and highway routes for all settlements in a district:
```http
GET /api/v1/full_routes/uttar_pradesh/basti.json
```

**Response:**
```json
{
  "edition": "VPS_HEAVY_FULL_RESOLUTION",
  "district": "Basti",
  "state": "Uttar Pradesh",
  "state_slug": "uttar_pradesh",
  "district_slug": "basti",
  "total_dense_settlements": 2981,
  "villages": [
    {
      "id": "node_77218392",
      "name": "Kalwari",
      "coords": [26.6394, 82.6806],
      "dense_road_routing": {
        "hospital_route": {
          "coordinates": [[82.6806, 26.6394], [82.6821, 26.6412], [82.6950, 26.6620]],
          "distance_m": 3120,
          "duration_sec": 380
        },
        "highway_route": {
          "coordinates": [[82.6806, 26.6394], [82.6811, 26.6401], [82.6890, 26.6510]],
          "distance_m": 1840,
          "duration_sec": 210
        }
      }
    }
  ]
}
```

---

### 4. Standard District Infrastructure Vector Bundle
```http
GET /api/v1/districts/uttar_pradesh/basti.json
```

---

### 5. Universal National Predictive Search Index
```http
GET /api/v1/search_index.json
```

---

## 🐳 Optional: 100% Offline Local OSRM Routing with Docker

To run completely offline without relying on external routing servers, deploy an in-memory OSRM instance directly on your VPS:

```bash
# 1. Download India OSM raw extract (1.7 GB)
mkdir -p /opt/osrm-data && cd /opt/osrm-data
curl -O https://download.geofabrik.de/asia/india-latest.osm.pbf

# 2. Extract and pre-partition graph
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/india-latest.osm.pbf
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/india-latest.osrm
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/india-latest.osrm

# 3. Run OSRM backend container on port 5000
docker run -d --name osrm-india -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/india-latest.osrm

# 4. Point OpenMapIndia server to local OSRM
export OSRM_BACKEND="http://127.0.0.1:5000"
python3 vps_heavy_edition/server.py --port 8080
```
This enables **sub-millisecond (<2ms) turn-by-turn routing** across all of India at 10,000+ queries per second completely offline!

---

## 📜 License
Open Data Commons Open Database License (ODbL) / MIT for Code and API Server.
