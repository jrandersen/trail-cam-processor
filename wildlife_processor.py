#!/usr/bin/env python3
"""
Wildlife Trail Camera Photo Processor
Detects animals in photos and organizes them by date and species
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import cv2
from PIL import Image
from PIL.ExifTags import TAGS
import json
from ultralytics import YOLO
import config

class WildlifeProcessor:
    def __init__(self, input_dir, output_dir, confidence_threshold=0.3):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.confidence_threshold = confidence_threshold
        self.save_all_photos = False  # Default: only save wildlife photos
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Try Roboflow trail camera model first
        if hasattr(config, 'USE_ROBOFLOW_MODEL') and config.USE_ROBOFLOW_MODEL and config.ROBOFLOW_API_KEY:
            try:
                from roboflow import Roboflow
                rf = Roboflow(api_key=config.ROBOFLOW_API_KEY)
                workspace = rf.workspace("sanskriti-jain")
                project = workspace.project("trail-camera-animal-detection")
                self.model = project.version(6).model
                print("✓ Using Roboflow trail camera model!")
                self.using_roboflow = True
                # Roboflow models have different class names
                self.wildlife_classes = set()  # Will be determined by model
            except Exception as e:
                print(f"✗ Roboflow failed: {e}")
                print("Falling back to YOLO...")
                self.model = YOLO('yolov8n.pt')
                self.using_roboflow = False
        else:
            print("Loading YOLO model...")
            self.model = YOLO('yolov8n.pt')
            self.using_roboflow = False
        
        # Set wildlife classes based on model type
        if not self.using_roboflow:
            # COCO classes that actually exist
            self.wildlife_classes = {
                'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 
                'bear', 'zebra', 'giraffe', 'elephant', 'person'
            }
        
        # Stats tracking
        self.stats = {
            'total_processed': 0,
            'wildlife_found': 0,
            'animals_detected': {},
            'errors': []
        }
    
    def get_image_date(self, image_path):
        """Extract date from image EXIF data or file modification time"""
        try:
            # Try to get date from EXIF
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        if tag_name == 'DateTime':
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            print(f"EXIF error for {image_path}: {e}")
        
        # Fallback to file modification time
        timestamp = os.path.getmtime(image_path)
        return datetime.fromtimestamp(timestamp)
    
    def detect_wildlife(self, image_path):
        """Run detection on image and return wildlife found"""
        try:
            if self.using_roboflow:
                # Roboflow API
                results = self.model.predict(str(image_path), confidence=40, overlap=30)
                
                wildlife_detected = []
                for prediction in results.json().get('predictions', []):
                    class_name = prediction['class']
                    confidence = prediction['confidence']
                    
                    if confidence >= self.confidence_threshold:
                        wildlife_detected.append({
                            'animal': class_name,
                            'confidence': confidence,
                            'bbox': [prediction['x'], prediction['y'], prediction['width'], prediction['height']]
                        })
                
                return wildlife_detected
                
            else:
                # YOLO API (your existing code)
                results = self.model(image_path, verbose=False)
                
                wildlife_detected = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0])
                            class_name = self.model.names[class_id]
                            confidence = float(box.conf[0])
                            
                            if (class_name in self.wildlife_classes and 
                                confidence >= self.confidence_threshold):
                                wildlife_detected.append({
                                    'animal': class_name,
                                    'confidence': confidence,
                                    'bbox': box.xyxy[0].tolist()
                                })
                
                return wildlife_detected
                
        except Exception as e:
            self.stats['errors'].append(f"Detection error for {image_path}: {e}")
            return []
    
    def create_filename(self, original_path, date_taken, animals):
        """Create new filename with date and animals"""
        date_str = date_taken.strftime('%Y-%m-%d_%H-%M-%S')
        
        if animals:
            # Get unique animal names, sort for consistency
            animal_names = sorted(set([a['animal'] for a in animals]))
            animals_str = '_'.join(animal_names)
            filename = f"{date_str}_{animals_str}"
        else:
            filename = f"{date_str}_no_wildlife"
        
        # Keep original extension
        extension = original_path.suffix.lower()
        return f"{filename}{extension}"
    
    def save_detection_info(self, output_path, animals, original_path):
        """Save detection details as JSON sidecar file"""
        info = {
            'original_file': str(original_path),
            'processed_date': datetime.now().isoformat(),
            'detections': animals
        }
        
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(info, f, indent=2)
    
    def process_single_image(self, image_path):
        """Process a single image"""
        print(f"Processing: {image_path.name}")
        
        # Get image date
        date_taken = self.get_image_date(image_path)
        
        # Detect wildlife
        animals = self.detect_wildlife(image_path)
        
        # Create new filename
        new_filename = self.create_filename(image_path, date_taken, animals)
        output_path = self.output_dir / new_filename
        
        # Copy image to output directory (if configured to save all, or if wildlife found)
        if self.save_all_photos or animals:
            shutil.copy2(image_path, output_path)
            
            # Save detection info if animals found
            if animals:
                self.save_detection_info(output_path, animals, image_path)
                self.stats['wildlife_found'] += 1
                
                # Update animal counts
                for animal in animals:
                    name = animal['animal']
                    self.stats['animals_detected'][name] = self.stats['animals_detected'].get(name, 0) + 1
        
        self.stats['total_processed'] += 1
        
        return len(animals) > 0, self.save_all_photos or len(animals) > 0
    
    def process_all_images(self):
        """Process all images in the input directory"""
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
        # Find all image files
        image_files = []
        for ext in image_extensions:
            image_files.extend(self.input_dir.glob(f"*{ext}"))
            image_files.extend(self.input_dir.glob(f"*{ext.upper()}"))
        
        print(f"Found {len(image_files)} images to process")
        
        if not image_files:
            print("No image files found!")
            return
        
        # Process each image
        for i, image_path in enumerate(image_files, 1):
            try:
                has_wildlife, was_saved = self.process_single_image(image_path)
                if was_saved:
                    status = "✓ Wildlife found" if has_wildlife else "✓ Saved (no wildlife)"
                else:
                    status = "- Skipped (no wildlife)"
                print(f"  [{i}/{len(image_files)}] {status}")
                
            except Exception as e:
                error_msg = f"Failed to process {image_path}: {e}"
                print(f"  [ERROR] {error_msg}")
                self.stats['errors'].append(error_msg)
        
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(f"Total images processed: {self.stats['total_processed']}")
        print(f"Images with wildlife: {self.stats['wildlife_found']}")
        print(f"Success rate: {self.stats['wildlife_found']/max(1,self.stats['total_processed'])*100:.1f}%")
        
        if self.stats['animals_detected']:
            print("\nAnimals detected:")
            for animal, count in sorted(self.stats['animals_detected'].items()):
                print(f"  {animal}: {count} photos")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")

def main():
    """Main function to run the wildlife processor"""
    
    # Import configuration
    try:
        import config
        INPUT_DIR = config.INPUT_DIR
        OUTPUT_DIR = config.OUTPUT_DIR
        CONFIDENCE = config.CONFIDENCE_THRESHOLD
        SAVE_ALL = config.SAVE_ALL_PHOTOS
    except ImportError:
        print("ERROR: config.py not found!")
        print("Please copy examples/sample_config.py to config.py and update the paths.")
        return
    except AttributeError as e:
        print(f"ERROR: Missing setting in config.py: {e}")
        print("Please check examples/sample_config.py for required settings.")
        return
    
    print("Wildlife Trail Camera Processor")
    print("=" * 40)
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Confidence threshold: {CONFIDENCE}")
    print()
    
    # Check if input directory exists
    if not Path(INPUT_DIR).exists():
        print(f"ERROR: Input directory '{INPUT_DIR}' does not exist!")
        print("Please update the INPUT_DIR path in the script.")
        return
    
    # Create processor and run
    processor = WildlifeProcessor(INPUT_DIR, OUTPUT_DIR, CONFIDENCE)
    
    # Configure whether to save all photos or only wildlife photos
    processor.save_all_photos = SAVE_ALL
    
    processor.process_all_images()

if __name__ == "__main__":
    main()