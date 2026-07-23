#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  export $(grep -v '^#' .env | grep -v '^\s*$' | xargs -d '\n')
fi

pip install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip install -r requirements.txt --quiet

cd backend
python3 app.py
