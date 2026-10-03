import sys
from pathlib import Path
from ultralytics import YOLO

def main():
    workspace_dir = Path(__file__).resolve().parent
    
    # Check for best.pt from the latest run (assuming flood_sentinels_v3 or fallback)
    model_path = workspace_dir / "runs" / "detect" / "flood_sentinels_v3" / "weights" / "best.pt"
    if len(sys.argv) > 1:
        model_path = Path(sys.argv[1])
        
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        sys.exit(1)
        
    data_path = workspace_dir / "Yolo Dataset" / "data.yaml"
        
    model = YOLO(model_path)
    
    print("\nEvaluating model on Test Set...")
    metrics = model.val(
        data=str(data_path),
        split='test',
        device=0  # Use GPU if available
    )
    
    print("\nEvaluation Complete.")
    # Ultralytics auto-prints metrics, but we can also print the specific mAP
    print(f"mAP@50: {metrics.box.map50:.3f}")
    print(f"mAP@50-95: {metrics.box.map:.3f}")

if __name__ == "__main__":
    main()
