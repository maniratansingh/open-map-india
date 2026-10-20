# 🖥️ OpenMapIndia — VPS Heavy Edition (Full-Resolution Routing Server)

This directory contains the server software, routing engine configurations, and batch generators designed for deployment on a **Virtual Private Server (VPS)** or dedicated cloud server (Hetzner, DigitalOcean, AWS EC2, Linode, OVH).

While the **GitHub Edition** is lightweight (~22 MB) and serves precomputed vector endpoints via free CDN, the **VPS Heavy Edition** is designed to store and serve the **complete, multi-gigabyte, high-density turn-by-turn road curvature database** and perform dynamic routing for fleets, ambulances, and police dispatch.

---

## 💻 Recommended VPS Specifications

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **CPU** | 2 vCPUs | 4 to 8 vCPUs |
| **RAM** | 4 GB | 8 GB to 16 GB |
| **Disk Storage** | 40 GB NVMe SSD | 80 GB NVMe SSD |
| **OS** | Ubuntu 22.04 / 24.04 LTS or Debian 12 | Ubuntu 24.04 LTS |

---

## 📁 Directory Structure on VPS

```
vps_heavy_edition/
├── README.md               <-- Deployment guide
├── server.py               <-- High-performance Python API Server
├── build_full_india.py     <-- Batch builder for multi-GB dense turn-by-turn routes
└── data/                   <-- Stored locally on VPS disk (Ignored by Git)
    ├── india.osm.pbf       <-- 1.7 GB OSM raw planet extract
    └── full_routes/        <-- Dense turn-by-turn geometries for all 594 districts
```

---

## 🚀 Quick Deployment Guide on VPS

### Step 1: Clone Repository on your VPS
```bash
git clone https://github.com/maniratansingh/open-map-india.git
cd open-map-india/vps_heavy_edition
```

### Step 2: Install Dependencies
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install urllib3 requests
```

### Step 3: Run the High-Performance VPS Server
```bash
python3 server.py --port 8080
```

---

## ⚡ Generating the Full Multi-GB Road Database Locally

To generate the complete, high-density turn-by-turn road curves for every village in India on your VPS disk:

```bash
# Run for a specific state/district:
python3 build_full_india.py --state uttar_pradesh --district basti

# Run across all districts in background (recommended with nohup or tmux):
nohup python3 build_full_india.py --all > build_full.log 2>&1 &
```

The output will be saved on your VPS disk under `vps_heavy_edition/data/full_routes/`.

---

## 🌐 VPS API Endpoints

When running `server.py`, your VPS exposes:

1. **Lightweight District Endpoints**:  
   `GET http://<vps-ip>:8080/api/v1/districts/<state>/<district>.json`
2. **Dense Full-Resolution Road Routes (VPS-Only)**:  
   `GET http://<vps-ip>:8080/api/v1/full_routes/<state>/<district>.json`
3. **Dynamic On-Demand Route Calculator**:  
   `GET http://<vps-ip>:8080/route?from_lat=26.639&from_lon=82.680&to_lat=26.685&to_lon=82.712`
