#!/bin/bash
# Quick Start Script for AuditMate
# Run this to set up and test AuditMate in mock mode

set -e

echo "=========================================="
echo "AuditMate Quick Start Setup"
echo "=========================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Step 1: Create virtual environment
echo
echo "Step 1: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

echo "✓ Virtual environment activated"

# Step 2: Install dependencies
echo
echo "Step 2: Installing dependencies..."
pip install -q -r Agents/requirements.txt -r Backend/requirements.txt
echo "✓ Dependencies installed"

# Step 3: Install Playwright
echo
echo "Step 3: Installing Playwright chromium..."
python3 -m playwright install chromium -q
echo "✓ Playwright configured"

# Step 4: Setup .env
echo
echo "Step 4: Setting up .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env created from template"
    echo "  ⚠ Please review .env and update as needed"
else
    echo "✓ .env already exists"
fi

# Step 5: Set mock mode
export AUDITMATE_MODE=mock
export PYTHONPATH=.

# Step 6: Verify installation
echo
echo "Step 5: Verifying installation..."
echo

echo "Testing Graph Store..."
python3 data/graph_store.py > /dev/null && echo "  ✓ Graph store OK" || echo "  ✗ Graph store failed"

echo "Testing GitHub Agent..."
python3 -m Agents.github_agent.agent > /dev/null && echo "  ✓ GitHub agent OK" || echo "  ✗ GitHub agent failed"

echo "Testing Audit Intake..."
python3 -m Agents.audit_intake_agent.agent > /dev/null && echo "  ✓ Audit intake OK" || echo "  ✗ Audit intake failed"

echo
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "Option A: Run Backend + Frontend"
echo "  Terminal 1: python -m uvicorn Backend.app.main:app --port 8000"
echo "  Terminal 2: cd Frontend && npm install && npm run dev"
echo "  Browser:   http://localhost:5173"
echo
echo "Option B: Run CLI Orchestrator"
echo "  python -m Agents.orchestrator.run \\\"Trace CHG-000123...\\\" --app APP-001"
echo
echo "Option C: Test Backend Endpoint"
echo "  python -m uvicorn Backend.app.main:app --port 8000"
echo "  curl http://localhost:8000/api/health"
echo
echo "=========================================="
