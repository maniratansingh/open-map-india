#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🇮🇳  INDIA GEO-ENGINE: ALL-INDIA BATCH PRECOMPUTATION"
echo "=========================================================="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
fi

if [[ ! -f data/extracted/villages.jsonl.gz ]]; then
    echo "▶️ Step 1: Extracting raw assets from OSM PBF..."
    python3 scripts/python/extract_all.py
else
    echo "✅ Step 1: Assets already extracted in data/extracted/. Skipping."
fi

echo "▶️ Step 2: Precomputing District Packages..."
python3 scripts/python/precompute_districts.py

echo "▶️ Step 3: Building National & State Indexes + SDKs..."
python3 scripts/python/build_indexes.py

echo "=========================================================="
echo "🎉 PIPELINE COMPLETE!"
echo "Check api/v1/ for generated national datasets."
echo "=========================================================="
