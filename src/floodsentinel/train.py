import argparse
from pathlib import Path
from ultralytics import YOLO


def main(epochs=50, batch_size=16, model_size="m"):
    """
    Trains the YOLO model with optimized hyperparameters for real-world accuracy.
    """
    workspace = Path(__file__).resolve().parent.parent.parent

    data_yaml = workspace / "Yolo Dataset" / "data.yaml"

    # Select model size: n=nano, s=small, m=medium, l=large, x=xlarge
    # We use 'm' by default to vastly improve accuracy over 'n'
    model_name = f"yolov8{model_size}.pt"
    print(f"Loading base architecture: {model_name}")

    # Initialize the model (downloads the pretrained weights automatically)
    model = YOLO(model_name)

    print("\nStarting Training with optimized hyperparameters...")
    # Key Hyperparameters for robust real-world generalization:
    # - mixup/mosaic: Combines multiple images to handle complex occlusions
    # - hsv_h/s/v: Shifts colors/lighting to handle shadows, rain, and glare
    # - degrees/perspective: Warps images to simulate different camera angles

    model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=640,
        name=f"flood_sentinels_optimized_{model_size}",
        device=0,  # Changed to 0 to utilize the Nvidia GPU
        # Heavy augmentations to prevent overfitting and improve field accuracy
        mosaic=1.0,  # 100% chance to mix 4 images
        mixup=0.1,  # 10% chance to overlay images
        hsv_h=0.015,  # Hue shift
        hsv_s=0.7,  # Saturation shift
        hsv_v=0.4,  # Value (brightness) shift
        degrees=10.0,  # Rotate images slightly
        perspective=0.0001,  # Perspective warping
        fliplr=0.5,  # 50% chance to flip horizontally
        # Optimization
        warmup_epochs=3.0,
        lr0=0.01,
        lrf=0.01,
        patience=15,  # Stop early if no improvement for 15 epochs
    )

    print(
        "\nTraining complete! Check the 'runs/detect/' folder for results and the new weights."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train optimized YOLO model")
    parser.add_argument(
        "--epochs", type=int, default=50, help="Number of epochs to train"
    )
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument(
        "--size",
        type=str,
        choices=["n", "s", "m", "l", "x"],
        default="m",
        help="YOLOv8 model size",
    )
    args = parser.parse_args()

    main(epochs=args.epochs, batch_size=args.batch, model_size=args.size)
