#!/usr/bin/env bash
# ==============================================================================
# OpenMapIndia — Automated Dataset Updater
# Fetches the latest OpenStreetMap India extract, recomputes vectors,
# generates new district analytics, and updates all API endpoints.
# ==============================================================================

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

echo "=================================================================="
echo "🔄 OpenMapIndia: Starting Dataset Refresh Pipeline"
echo "Time: $(date)"
echo "=================================================================="

# 1. Activate Python Environment
if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
else
    echo "❌ Error: Virtual environment .venv not found. Run ./run_pipeline.sh first."
    exit 1
fi

# 2. Check and Download Latest Geofabrik India OSM Extract
mkdir -p india_tiles
echo "▶️ Step 1: Checking for newer India OSM PBF from Geofabrik..."
curl -L -z india_tiles/india.osm.pbf -o india_tiles/india.osm.pbf "https://download.geofabrik.de/asia/india-latest.osm.pbf" || true

# 3. Clean intermediate extracted cache to force re-extraction
echo "▶️ Step 2: Clearing old extraction cache..."
rm -rf data/extracted/*.gz

# 4. Extract Villages and Health Infrastructure
echo "▶️ Step 3: Extracting fresh settlements & healthcare facilities..."
python3 extract_all.py

# 5. Extract Major Highways
echo "▶️ Step 4: Extracting fresh arterial highways..."
python3 extract_highways.py

# 6. Precompute District Packages & Analytics
echo "▶️ Step 5: Precomputing district vectors & infrastructure analytics..."
python3 precompute_districts.py

# 7. Generate National & State Indexes + SDKs
echo "▶️ Step 6: Updating state & national rollups..."
python3 build_indexes.py

# 8. Git Commit (Optional prompt or automated)
echo "=================================================================="
echo "✅ Data refresh complete!"
echo "To commit and push the updated data to GitHub, run:"
echo "  git add api/ v1/ && git commit -m 'chore: refresh India map dataset ($(date +%Y-%m-%d))' && git push"
echo "=================================================================="
