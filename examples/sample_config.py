#!/usr/bin/env python3
"""
Sample configuration file for wildlife processor
Copy this to config.py and modify for your setup
"""

# Input and output directories
INPUT_DIR = "trail_cam_photos"        # Directory containing your trail cam photos
OUTPUT_DIR = "processed_wildlife"     # Where to save organized photos

# Detection settings
CONFIDENCE_THRESHOLD = 0.3            # Minimum confidence for detections (0.0 to 1.0)
                                     # Lower = more detections but more false positives
                                     # Higher = fewer detections but more accurate

# YOLO model selection
MODEL_SIZE = "yolov8n.pt"            # Options: yolov8n.pt (nano), yolov8s.pt (small), 
                                     # yolov8m.pt (medium), yolov8l.pt (large)
                                     # Larger models = more accurate but slower

# Wildlife classes to detect (from COCO dataset)
WILDLIFE_CLASSES = {
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 
    'elephant', 'bear', 'zebra', 'giraffe'
}

# Include humans in detections? (useful for filtering out people)
INCLUDE_PEOPLE = True

# File naming options
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"     # How to format dates in filenames
ANIMAL_SEPARATOR = "_"                # Character between animal names
MAX_ANIMALS_IN_NAME = 3               # Max animals to include in filename

# Processing options
SAVE_DETECTION_JSON = True            # Save detailed detection info as JSON files
COPY_ORIGINALS = True                 # Copy files (True) or move them (False)
SAVE_ALL_PHOTOS = False               # Save all photos (True) or only wildlife photos (False)
BATCH_SIZE = 10                       # Number of images to process at once

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}

# Advanced settings
ENABLE_GPU = True                     # Use GPU if available
VERBOSE_OUTPUT = True                 # Print detailed processing info