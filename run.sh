#!/bin/bash

# Name of the virtual environment
VENV_NAME="scrape"

# Create venv if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_NAME
else
    echo "Virtual environment already exists."
fi

# Activate venv
echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found!"
fi

echo "Setup complete! Virtual environment '$VENV_NAME' is ready."
echo "To activate in any new terminal, run: source $VENV_NAME/bin/activate"
