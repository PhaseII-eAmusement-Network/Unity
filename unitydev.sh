#!/bin/bash

VENV_DIR=".venv"
CONFIG_FILE="development.config.yaml"
TEMPLATE_FILE="config.yaml"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"

    source "$VENV_DIR/bin/activate"
    pip install -r requirements.txt
    pip install .
    deactivate
    echo "Created and installed!"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found. Creating from template..."
    
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "[ERROR] Template config.yaml not found!"
        exit 1
    fi

    cp "$TEMPLATE_FILE" "$CONFIG_FILE"
    
    echo "Config created at $CONFIG_FILE"
    echo "Please edit it before running again."
    exit 0
fi

source .venv/bin/activate
pip install --upgrade pip
python ./startapi --config ./development.config.yaml 
