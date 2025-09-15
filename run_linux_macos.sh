#!/bin/bash
# LazyPaper Launcher - Linux / macOS
cd "$(dirname "$0")" || exit
# Check correct directory
if [ ! -d "lazypaper" ] || [ ! -f "lazypaper/lazypaper.py" ]; then
    echo "Error: Incorrect project structure.."
    echo "Must exist: lazypaper/lazypaper.py"
    exit 1
fi
# Activate or create virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        echo "Installing dependencies..."
        pip install -r requirements.txt
    fi
  else
    echo "Already in virtual environment: $VIRTUAL_ENV"
fi
# Execute program directly
cd lazypaper
python3 lazypaper.py
cd ..
read -p "Press Enter to close..."
deactivate
# --- IGNORE ---