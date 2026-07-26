#!/bin/bash
echo "🚀 Starting Anysnap API Setup..."

# 1. Virtual Environment banana
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies install karna
pip install --upgrade pip
pip install -r requirements.txt

# 3. Docker databases start karna
docker compose up -d

echo "✅ Setup Complete! Now run: source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"