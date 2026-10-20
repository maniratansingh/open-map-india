#!/usr/bin/env python3
"""
OpenMapIndia — VPS Heavy Edition API Server
Serves static lightweight endpoints, local multi-GB full-resolution routes,
and dynamic turn-by-turn road calculations with full CORS support.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FULL_ROUTES_DIR = os.path.join(os.path.dirname(__file__), "data", "full_routes")

class VPSAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for web and mobile frontends
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 0. Health check endpoint
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status_obj = {
                "status": "healthy",
                "edition": "VPS_HEAVY_EDITION",
                "version": "1.0.0",
                "service": "OpenMapIndia VPS High-Performance Engine",
                "osrm_backend": os.environ.get("OSRM_BACKEND", "https://router.project-osrm.org"),
                "endpoints": [
                    "/health",
                    "/route?from_lat=<lat>&from_lon=<lon>&to_lat=<lat>&to_lon=<lon>",
                    "/api/v1/full_routes/<state>/<district>.json",
                    "/api/v1/districts/<state>/<district>.json",
                    "/api/v1/search_index.json"
                ]
            }
            self.wfile.write(json.dumps(status_obj, indent=2).encode("utf-8"))
            return

        # 1. Dynamic On-Demand Routing Engine
        if path == "/route":
            params = urllib.parse.parse_qs(parsed.query)
            try:
                from_lat = float(params.get("from_lat", [0])[0])
                from_lon = float(params.get("from_lon", [0])[0])
                to_lat = float(params.get("to_lat", [0])[0])
                to_lon = float(params.get("to_lon", [0])[0])

                backend = os.environ.get("OSRM_BACKEND", "http://router.project-osrm.org")
                osrm_url = f"{backend}/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}?overview=full&geometries=geojson"
                try:
                    req = urllib.request.Request(osrm_url, headers={"User-Agent": "OpenMapIndia-VPS/1.0"})
                    with urllib.request.urlopen(req, timeout=8) as r:
                        res_data = r.read()
                except Exception as inner_e:
                    if osrm_url.startswith("https://"):
                        fallback_url = osrm_url.replace("https://", "http://", 1)
                        req = urllib.request.Request(fallback_url, headers={"User-Agent": "OpenMapIndia-VPS/1.0"})
                        with urllib.request.urlopen(req, timeout=8) as r:
                            res_data = r.read()
                    else:
                        raise inner_e

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(res_data)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                err = json.dumps({"error": str(e), "message": "Failed to compute road route"})
                self.wfile.write(err.encode("utf-8"))
                return

        # 2. Heavy Full-Resolution District Routes
        if path.startswith("/api/v1/full_routes/"):
            rel_path = path[len("/api/v1/full_routes/"):]
            full_file = os.path.join(FULL_ROUTES_DIR, rel_path)
            if os.path.exists(full_file):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                with open(full_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                err = json.dumps({
                    "error": "Not Found",
                    "message": f"Full-resolution file not generated yet. Run build_full_india.py for {rel_path}."
                })
                self.wfile.write(err.encode("utf-8"))
                return

        # 3. Default: Fall through to standard files (api/v1/, index.html)
        super().do_GET()

def main():
    parser = argparse.ArgumentParser(description="OpenMapIndia VPS Heavy API Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), VPSAPIHandler)
    print("=" * 65)
    print(f"🚀 OpenMapIndia VPS Server Running on http://{args.host}:{args.port}")
    print(f"📁 Serving Base: {BASE_DIR}")
    print(f"📁 Heavy Full Routes: {FULL_ROUTES_DIR}")
    print("=" * 65)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping VPS Server...")
        server.server_close()

if __name__ == "__main__":
    main()
