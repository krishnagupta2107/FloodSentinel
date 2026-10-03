import yaml
import torch
from pathlib import Path
from ultralytics import YOLO

def main():
    workspace_dir = Path(__file__).resolve().parent
    config_path = workspace_dir / "configs" / "train.yaml"
    
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
        
    print(f"PyTorch version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        
    # data.yaml is inside Yolo Dataset
    data_path = workspace_dir / "Yolo Dataset" / cfg['data']
        
    model = YOLO(cfg['model'])
    
    print("\nStarting config-driven training...")
    model.train(
        data=str(data_path),
        epochs=cfg['epochs'],
        imgsz=cfg['imgsz'],
        batch=cfg['batch'],
        seed=cfg['seed'],
        deterministic=cfg['deterministic'],
        project=cfg['project'],
        name=cfg['name'],
        patience=cfg.get('patience', 50)
    )

if __name__ == "__main__":
    main()
