#!/usr/bin/env python3
"""
Test script for wildlife detection
Tests the system on a single image before processing the full batch
"""

import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
from PIL import Image
import json

def test_single_image(image_path):
    """Test wildlife detection on a single image"""
    
    print(f"Testing wildlife detection on: {image_path}")
    print("-" * 50)
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"ERROR: File {image_path} does not exist!")
        return
    
    try:
        # Load model
        print("Loading YOLO model...")
        model = YOLO('yolov8n.pt')
        
        # Run detection
        print("Running detection...")
        results = model(image_path, verbose=False)
        
        # Wildlife classes we care about
        wildlife_classes = {
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 
            'bear', 'zebra', 'giraffe', 'person'
        }
        
        # Process results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    # Check if it's an animal
                    if class_name in wildlife_classes:
                        detections.append({
                            'animal': class_name,
                            'confidence': confidence
                        })
        
        # Display results
        print(f"\nResults for {Path(image_path).name}:")
        if detections:
            print(f"✓ Found {len(detections)} animal(s):")
            for detection in detections:
                print(f"  - {detection['animal']}: {detection['confidence']:.2f} confidence")
        else:
            print("- No wildlife detected")
        
        # Show image info
        try:
            with Image.open(image_path) as img:
                print(f"\nImage info:")
                print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
                print(f"  Format: {img.format}")
                
                # Try to get EXIF date
                exif_data = img._getexif()
                if exif_data:
                    from PIL.ExifTags import TAGS
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        if tag_name == 'DateTime':
                            print(f"  Date taken: {value}")
                            break
                    else:
                        print(f"  Date taken: Not found in EXIF")
                else:
                    print(f"  Date taken: No EXIF data")
        except Exception as e:
            print(f"  Could not read image info: {e}")
        
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        print("Make sure you have activated the virtual environment and installed dependencies.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_single_image.py <path_to_image>")
        print("Example: python test_single_image.py sample_photo.jpg")
        return
    
    image_path = sys.argv[1]
    test_single_image(image_path)

if __name__ == "__main__":
    main()