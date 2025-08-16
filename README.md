# Wildlife Trail Cam Processor

Automatically detect and organize wildlife photos from trail cameras using computer vision. Supports both offline YOLO models and cloud-based Roboflow trail camera models for improved accuracy.

## Quick Start

```bash
# Setup
./setup.sh

# Configure
cp examples/sample_config.py config.py
# Edit config.py with your paths and model preferences

# Test single image
source wildlife_env/bin/activate
python test_single_image.py "/path/to/your/trail_cam_photo.jpg"

# Process all photos
python wildlife_processor.py
```

## What it does

- Detects animals in photos using YOLOv8 or specialized trail camera models
- Extracts photo dates from EXIF data
- Organizes photos by date and animal type
- **Default**: Only saves photos with wildlife detected (saves storage space)
- Example output: `2024-01-15_14-30-22_deer_raccoon.jpg`

## Detection Models

### Option 1: Roboflow Trail Camera Model (Recommended)
- **Better accuracy** for trail camera scenarios
- Trained specifically on trail cam data
- Detects common North American wildlife
- Requires free API key from roboflow.com

### Option 2: Offline YOLO Model
- **No internet required** after initial setup
- Uses standard COCO dataset classes
- Maps similar animals (e.g., squirrels detected as "sheep")
- Good fallback option

## Requirements

- **Python 3.11** (recommended) or 3.8+
- ~500MB disk space for dependencies
- GPU optional but recommended for speed
- Internet connection for Roboflow model (optional)

## Configuration

Copy and edit the config file:
```bash
cp examples/sample_config.py config.py
```

Key settings in `config.py`:
```python
# Basic settings
INPUT_DIR = "/Volumes/YourDrive/TrailCam/Photos"  # Your photos folder
OUTPUT_DIR = "processed_wildlife"                 # Output folder
CONFIDENCE_THRESHOLD = 0.3                        # Detection threshold (0.1-0.9)
SAVE_ALL_PHOTOS = False                          # Only save wildlife photos

# Roboflow settings (for better accuracy)
USE_ROBOFLOW_MODEL = True                        # Enable trail camera model
ROBOFLOW_API_KEY = "your_api_key_here"          # Get free key from roboflow.com
```

## Trail Camera Setup

For **network drives** (SMB shares):
1. Mount your trail camera drive in Finder: `Cmd+K` → `smb://your-camera-server`
2. Use the mounted path in config: `INPUT_DIR = "/Volumes/YourDrive/TrailCam/Photos"`

## Performance

### YOLO Model (Offline)
- **CPU**: ~2-3 seconds per photo
- **GPU**: ~0.5 seconds per photo
- **Accuracy**: Limited to COCO classes (birds, some mammals)

### Roboflow Trail Camera Model
- **Processing**: Similar speed to YOLO
- **Accuracy**: Much better for trail cameras
- **Animals**: Deer, raccoons, squirrels, birds, and more

## Output

For each photo with wildlife:
- **Renamed file** with date and animals: `2024-01-30_10-17-44_deer_squirrel.jpg`
- **JSON sidecar** with detection details and confidence scores
- **Organized structure** for easy browsing

Files without wildlife get `_no_wildlife` suffix for easy filtering.

## Common Issues

### Setup Problems
- **Python version**: Use Python 3.11 for best compatibility
- **NumPy conflicts**: Run `pip install "numpy<2"` if you see warnings
- **Permissions**: Use `chmod +x setup.sh` if setup script won't run

### Detection Issues
- **No animals found**: Try lowering `CONFIDENCE_THRESHOLD` to 0.1-0.2
- **Wrong classifications**: YOLO maps animals to closest COCO class (squirrels → sheep)
- **Poor accuracy**: Enable Roboflow model for trail camera-specific detection

### Path Issues
- **Network drives**: Make sure SMB share is mounted in `/Volumes/`
- **Spaces in paths**: Use quotes around paths with spaces
- **Permissions**: Ensure read access to input directory, write access to output

## Wildlife Detection Viewer

A simple GUI tool to review your processed images with bounding boxes:

```bash
# Run the viewer
python wildlife_viewer.py
```

**Features:**
- Browse images with Previous/Next buttons or arrow keys
- View bounding boxes around detected animals
- See detection confidence scores
- Zoom and scroll for large images
- Works with both YOLO and Roboflow detection results

**Usage:**
1. Click "Select Folder" and choose your `processed_wildlife` output folder
2. Navigate through images using arrow keys or buttons
3. Review detection quality and confidence scores

**Note:** On macOS, you may need to install tkinter: `brew install python-tk`

## Troubleshooting

```bash
# Test a single image first
python test_single_image.py "/path/to/test/image.jpg"

# Check what YOLO actually detects
python debug_detection.py "/path/to/test/image.jpg"

# Force offline YOLO model
# Set USE_ROBOFLOW_MODEL = False in config.py

# View processed results with bounding boxes
python wildlife_viewer.py
```

## Getting Better Results

1. **Use Roboflow model** for trail camera-specific accuracy
2. **Lower confidence threshold** (0.15-0.25) for more detections
3. **Process smaller batches** if you have memory issues
4. **Check sample outputs** before processing entire collection
5. **Use the viewer** to review detection quality and adjust settings

![Made in Asheville, NC](https://madewithlove.now.sh/us?colorA=%23575757&colorB=%2344cbd5&template=for-the-badge&text=Asheville%2C+NC)