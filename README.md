# Wildlife Trail Cam Processor

Automatically detect and organize wildlife photos from trail cameras using computer vision. Runs completely offline with no ongoing costs.

## Quick Start

```bash
# Setup
./setup.sh

# Configure
cp examples/sample_config.py config.py
# Edit config.py with your paths

# Test single image
source wildlife_env/bin/activate
python test_single_image.py sample_photo.jpg

# Process all photos
python wildlife_processor.py
```

## What it does

- Detects animals in photos using YOLOv8
- Extracts photo dates from EXIF data
- Organizes photos by date and animal type
- **Default**: Only saves photos with wildlife detected (saves storage space)
- Example output: `2024-01-15_14-30-22_deer_raccoon.jpg`

## Requirements

- Python 3.8+
- ~500MB disk space for dependencies
- GPU optional but recommended for speed

## Configuration

Copy and edit the config file:
```bash
cp examples/sample_config.py config.py
```

Key settings in `config.py`:
```python
INPUT_DIR = "trail_cam_photos"      # Your photos folder
OUTPUT_DIR = "processed_wildlife"   # Output folder
CONFIDENCE_THRESHOLD = 0.3          # Detection threshold
SAVE_ALL_PHOTOS = False             # Only save wildlife photos
```

## Performance

- **CPU**: ~2-3 seconds per photo
- **GPU**: ~0.5 seconds per photo  
- **Animals detected**: Birds, mammals, common wildlife
- **Accuracy**: Good for trail cam scenarios

## Output

For each photo with wildlife:
- Renamed file with date and animals
- JSON file with detection details and confidence scores

No wildlife detected? File gets `_no_wildlife` suffix for easy filtering.

![Made with love in Asheville, NC](https://madewithlove.now.sh/us?colorA=%23575757&colorB=%2344cbd5&template=for-the-badge&text=Asheville%2C+NC)