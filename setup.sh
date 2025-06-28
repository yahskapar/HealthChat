#!/bin/bash

# This script creates a clean conda environment named 'healthchat',
# activates it, and installs the necessary Python packages.

set -e

ENV_NAME="healthchat"
PYTHON_VERSION="3.13"

echo "--- Setting up conda environment '$ENV_NAME' ---"

trap 'echo "  ERROR: Setup failed. Please check the logs above." >&2' ERR

# Remove existing environment to ensure a clean install
echo "--> Removing old '$ENV_NAME' environment (if it exists)..."
conda remove --name "$ENV_NAME" --all -y

echo "--> Creating new conda environment '$ENV_NAME' with Python $PYTHON_VERSION..."
conda create --name "$ENV_NAME" python="$PYTHON_VERSION" -y

echo "--> Initializing conda for this shell..."
source "$(conda info --base)/etc/profile.d/conda.sh"

echo "--> Activating '$ENV_NAME'..."
conda activate "$ENV_NAME"

which python

echo "--> Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "--- Setup complete! ---"
echo "To activate the environment in a new terminal, run:"
echo "conda activate $ENV_NAME"
