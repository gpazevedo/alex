#!/bin/bash
# Quick test script for Magia Total website

echo "========================================="
echo "  MAGIA TOTAL - Testing Website Locally"
echo "========================================="
echo ""
echo "Starting web server on port 8000..."
echo ""
echo "Open your browser and go to:"
echo ""
echo "  👉 http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

cd /home/gpazevedo/magiatotal
python3 -m http.server 8000
