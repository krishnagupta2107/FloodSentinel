import sys
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

def calculate_occlusion(image_path, model_path):
    """
    Estimates the occlusion percentage of a storm drain catch basin.
    Assumes the image is cropped to or focuses on the catch basin.
    Calculates the union area of all detected 'Sewage blockage' bounding boxes
    divided by the total image area.
    """
    # YOLO model ko load kar rahe hain
    model = YOLO(model_path)
    
    # Image pe inference run karo, verbose output band karke
    results = model(image_path, conf=0.25, verbose=False)
    
    for result in results:
        # Original image dimensions
        img_h, img_w = result.orig_shape
        total_image_area = img_h * img_w
        
        # Overlap double-counting se bachne ke liye sabhi blockage boxes ka union calculate karenge.
        # Ek blank mask banayenge, usme boxes draw karke non-zero pixels count karenge.
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        
        boxes = result.boxes
        # Agar koi blockage nahi mili toh return zero
        if len(boxes) == 0:
            return 0.0, result
        
        has_blockage = False
        for box in boxes:
            class_id = int(box.cls[0])
            # Assuming class 'Sewage blockage' is what we care about for occlusion
            if model.names[class_id] == 'Sewage blockage':
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(mask, (x1, y1), (x2, y2), 1, -1)
                has_blockage = True
                
        if not has_blockage:
            return 0.0, result
            
        occluded_area = np.sum(mask)
        occlusion_percentage = (occluded_area / total_image_area) * 100
        return occlusion_percentage, result
    
    return 0.0, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python estimate_occlusion.py <image_path>")
        sys.exit(1)
        
    img_path = sys.argv[1]
    
    # Use the best trained model (v3 based on latest runs)
    workspace_dir = Path(__file__).parent.parent
    model_path = workspace_dir / "runs" / "detect" / "flood_sentinels_v3" / "weights" / "best.pt"
    
    print(f"Running occlusion estimation on: {img_path}")
    pct, res = calculate_occlusion(img_path, str(model_path))
    print(f"\nEstimated Occlusion: {pct:.2f}%\n")
