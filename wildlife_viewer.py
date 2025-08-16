#!/usr/bin/env python3
"""
Wildlife Detection Viewer
Simple local viewer to display trail cam images with bounding boxes from JSON detection files
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from pathlib import Path

class WildlifeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Wildlife Detection Viewer")
        self.root.geometry("1200x800")
        
        # Variables
        self.current_image = None
        self.current_json = None
        self.image_files = []
        self.current_index = 0
        self.photo_ref = None  # Keep reference to prevent garbage collection
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=(0, 10))
        
        # Image counter
        self.counter_label = ttk.Label(control_frame, text="No images loaded")
        self.counter_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current file info
        self.file_label = ttk.Label(info_frame, text="No file selected", font=("Arial", 10))
        self.file_label.pack(anchor=tk.W)
        
        # Detection info
        self.detection_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.detection_label.pack(anchor=tk.W)
        
        # Image frame with scrollbars
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(image_frame, bg='gray')
        v_scrollbar = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        
        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.next_image())
        self.root.focus_set()  # Enable keyboard focus
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
                
    def select_folder(self):
        """Select folder containing processed images and JSON files"""
        folder = filedialog.askdirectory(title="Select folder with processed wildlife images")
        if folder:
            self.load_images(folder)
            
    def load_images(self, folder_path):
        """Load all image files from the selected folder"""
        folder = Path(folder_path)
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        self.image_files = []
        
        for ext in image_extensions:
            self.image_files.extend(folder.glob(f"*{ext}"))
            self.image_files.extend(folder.glob(f"*{ext.upper()}"))
        
        # Sort files
        self.image_files.sort()
        
        if self.image_files:
            self.current_index = 0
            self.update_counter()
            self.load_current_image()
        else:
            messagebox.showwarning("No Images", "No image files found in the selected folder.")
            
    def update_counter(self):
        """Update the image counter display"""
        if self.image_files:
            self.counter_label.config(text=f"Image {self.current_index + 1} of {len(self.image_files)}")
        else:
            self.counter_label.config(text="No images loaded")
            
    def load_current_image(self):
        """Load and display the current image with bounding boxes"""
        if not self.image_files:
            return
            
        image_path = self.image_files[self.current_index]
        json_path = image_path.with_suffix('.json')
        
        # Update file info
        self.file_label.config(text=f"File: {image_path.name}")
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Load JSON detection data if it exists
            detections = []
            if json_path.exists():
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    detections = data.get('detections', [])
            
            # Draw bounding boxes
            if detections:
                image = self.draw_bounding_boxes(image, detections)
                detection_text = f"Detections: {len(detections)} animals found"
                for i, det in enumerate(detections):
                    animal = det['animal']
                    confidence = det['confidence']
                    detection_text += f"\n  {i+1}. {animal}: {confidence:.2f}"
            else:
                detection_text = "No detections found"
                
            self.detection_label.config(text=detection_text)
            
            # Resize image if too large
            max_size = (1000, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_ref = ImageTk.PhotoImage(image)
            
            # Clear canvas and add image
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_ref)
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {e}")
            
    def draw_bounding_boxes(self, image, detections):
        """Draw bounding boxes on the image"""
        # Create a copy to draw on
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("Arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)  # macOS
            except:
                font = ImageFont.load_default()
        
        # Colors for different animals
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'magenta']
        
        for i, detection in enumerate(detections):
            animal = detection['animal']
            confidence = detection['confidence']
            bbox = detection['bbox']
            
            # Handle different bbox formats
            if len(bbox) == 4:
                # Check if it's [x, y, width, height] or [x1, y1, x2, y2]
                x, y, w_or_x2, h_or_y2 = bbox
                
                # If values look like width/height (typically smaller than coordinates)
                if w_or_x2 < image.width and h_or_y2 < image.height and w_or_x2 < 2000 and h_or_y2 < 2000:
                    # Assume [x, y, width, height] format (Roboflow style)
                    x1, y1 = int(x - w_or_x2/2), int(y - h_or_y2/2)  # Convert center to top-left
                    x2, y2 = int(x + w_or_x2/2), int(y + h_or_y2/2)
                else:
                    # Assume [x1, y1, x2, y2] format (YOLO style)
                    x1, y1, x2, y2 = int(x), int(y), int(w_or_x2), int(h_or_y2)
            else:
                continue  # Skip malformed bboxes
            
            # Choose color
            color = colors[i % len(colors)]
            
            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Draw label
            label = f"{animal}: {confidence:.2f}"
            
            # Get text size
            bbox_text = draw.textbbox((0, 0), label, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
            
            # Draw background for text
            draw.rectangle([x1, y1-text_height-5, x1+text_width+10, y1], fill=color)
            
            # Draw text
            draw.text((x1+5, y1-text_height-2), label, fill='white', font=font)
            
        return image_copy
        
    def prev_image(self):
        """Go to previous image"""
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self.update_counter()
            self.load_current_image()
            
    def next_image(self):
        """Go to next image"""
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.update_counter()
            self.load_current_image()

def main():
    root = tk.Tk()
    app = WildlifeViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()