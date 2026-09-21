#!/bin/bash
# Quick diagnostic - run this first to see what's wrong
echo "=== Quick Gaudi2 Training Diagnostic ==="
echo ""
echo "1. Gaudi Cards:"
hl-smi | grep -E "HL-225|AIP"
echo ""
echo "2. Docker Image:"
docker images gaudi-training-base:latest
echo ""
echo "3. Recent Container Status:"
docker ps -a --filter "ancestor=gaudi-training-base:latest" --format "table {{.ID}}\t{{.Status}}\t{{.CreatedAt}}" | head -5
echo ""
echo "4. Last Container Logs (if any failed):"
LAST_CONTAINER=$(docker ps -a --filter "ancestor=gaudi-training-base:latest" --format "{{.ID}}" | head -1)
if [ -n "$LAST_CONTAINER" ]; then
    echo "Container ID: $LAST_CONTAINER"
    docker logs --tail 50 "$LAST_CONTAINER" 2>&1 | tail -30
else
    echo "No containers found"
fi
echo ""
echo "5. Project Directory:"
if [ -d ~/gaudi-training-base ]; then
    cd ~/gaudi-training-base
    echo "✓ Found at: ~/gaudi-training-base"
    echo "Data files:"
    ls -lh data/examples/*.jsonl 2>/dev/null || echo "No data files"
else
    echo "❌ Project not found at ~/gaudi-training-base"
fi
