#!/bin/bash
echo "=== Remote Diagnostic Script ==="
echo "1. Checking Docker images..."
docker images | grep -E "gaudi|habana"
echo ""
echo "2. Checking project directory..."
ls -la ~/gaudi-training-base/ 2>/dev/null || ls -la ~/ | grep gaudi
echo ""
echo "3. Checking recent Docker containers..."
docker ps -a | head -10
echo ""
echo "4. Checking training logs..."
find ~ -name "*.log" -type f -mtime -1 2>/dev/null | head -5
echo ""
echo "5. Checking for training output/error files..."
find ~ -path "*/outputs/logs/*" -type f 2>/dev/null | head -5
