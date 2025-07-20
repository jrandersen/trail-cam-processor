#!/bin/bash
# Wildlife Detection Setup Script

echo "Wildlife Trail Cam Processor Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv wildlife_env

# Activate virtual environment
echo "Activating virtual environment..."
source wildlife_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install ultralytics opencv-python pillow

# Test installation
echo "Testing installation..."
python3 -c "
import cv2
from PIL import Image
from ultralytics import YOLO
print('✓ All packages imported successfully')
print('✓ OpenCV version:', cv2.__version__)
"

echo ""
echo "Setup complete!"
echo ""
echo "To use the wildlife processor:"
echo "1. Activate the environment: source wildlife_env/bin/activate"
echo "2. Update the paths in wildlife_processor.py"
echo "3. Run: python wildlife_processor.py"
echo ""
echo "Note: The YOLO model will be downloaded automatically on first run (~6MB)"