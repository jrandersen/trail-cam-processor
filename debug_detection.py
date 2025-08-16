#!/usr/bin/env python3
import sys
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Run detection on your image
image_path = sys.argv[1]
results = model(image_path, verbose=False)

print(f"ALL detections found in {image_path}:")
for result in results:
    boxes = result.boxes
    if boxes is not None:
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            print(f"  - {class_name}: {confidence:.3f} confidence")
    else:
        print("  No detections found at all")
