import sys
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path


def calculate_occlusion(image_path, model=None, model_path=None):
    """
    Estimates the occlusion percentage of a storm drain catch basin.
    To approximate the drain grate area without a dedicated mask, we take the
    bounding box of all detections (Defects + Sewage blockage). The occlusion is
    the union area of 'Sewage blockage' boxes divided by this estimated grate area.
    """
    if model is None:
        if model_path is None:
            raise ValueError("Either model or model_path must be provided")
        model = YOLO(model_path)

    results = model(image_path, conf=0.25, verbose=False)

    # Process just the first result (assuming single image inference)
    for result in results:
        img_h, img_w = result.orig_shape
        boxes = result.boxes

        if len(boxes) == 0:
            return 0.0, result

        # 1. Estimate Grate Area (bounding box of all detections)
        min_x = img_w
        min_y = img_h
        max_x = 0
        max_y = 0
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            min_x = min(min_x, x1)
            min_y = min(min_y, y1)
            max_x = max(max_x, x2)
            max_y = max(max_y, y2)

        grate_w = max_x - min_x
        grate_h = max_y - min_y

        # Avoid division by zero
        if grate_w <= 0 or grate_h <= 0:
            grate_area = img_w * img_h
        else:
            grate_area = grate_w * grate_h

        # 2. Calculate Occlusion Area (union of 'Sewage blockage' boxes)
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        has_blockage = False

        for box in boxes:
            class_id = int(box.cls[0])
            if model.names[class_id] == "Sewage blockage":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(mask, (x1, y1), (x2, y2), 1, -1)
                has_blockage = True

        if not has_blockage:
            return 0.0, result

        occluded_area = np.sum(mask)
        occlusion_percentage = (occluded_area / grate_area) * 100
        # Cap at 100% just in case of slight misalignments
        return min(occlusion_percentage, 100.0), result

    return 0.0, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python estimate_occlusion.py <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    workspace_dir = Path(__file__).resolve().parent.parent.parent
    model_path = (
        workspace_dir / "runs" / "detect" / "flood_sentinels_v3" / "weights" / "best.pt"
    )

    print(f"Running occlusion estimation on: {img_path}")
    pct, res = calculate_occlusion(img_path, model_path=str(model_path))
    print(f"\nEstimated Occlusion: {pct:.2f}%\n")
