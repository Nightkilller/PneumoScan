#!/bin/bash
# Robust autostart script for PneumoniaDetector (macOS)

BASE="$HOME/Desktop/PneumoniaDetector"
cd "$BASE" || { echo "Failed to cd to $BASE"; exit 1; }

# find manage.py under BASE (depth 3)
MANAGE_PATH=$(find . -maxdepth 3 -name manage.py -print -quit)

if [ -z "$MANAGE_PATH" ]; then
  echo "manage.py not found under $BASE"
  echo "Please ensure your project exists in $BASE"
  exec $SHELL
  exit 1
fi

PROJECT_DIR=$(dirname "$MANAGE_PATH")
echo "Found manage.py at: $MANAGE_PATH"
echo "Changing to project dir: $PROJECT_DIR"
cd "$PROJECT_DIR" || { echo "Cannot cd to $PROJECT_DIR"; exit 1; }

# activate venv - try common locations
if [ -f "$BASE/venv/bin/activate" ]; then
  source "$BASE/venv/bin/activate"
elif [ -f "../venv/bin/activate" ]; then
  source ../venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
else
  echo "Virtualenv activate script not found. Edit this script to point to your venv."
  exec $SHELL
  exit 1
fi

echo "Virtualenv activated. Python: $(which python) -- $(python --version)"

# Start Django development server
python manage.py runserver 127.0.0.1:8000

# keep the terminal interactive after server stops
exec $SHELL
