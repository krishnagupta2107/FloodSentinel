import pandas as pd
from pathlib import Path
from ultralytics import YOLO
from estimate_occlusion import calculate_occlusion


def test_occlusion_batch(test_dir, model_path):
    """
    Runs the occlusion estimation on all images in a given directory
    and saves the results to a CSV file.
    """
    test_dir_path = Path(test_dir)
    images = list(test_dir_path.glob("*.jpg"))

    if not images:
        print(f"No images found in {test_dir_path}")
        return

    print(f"Found {len(images)} images in {test_dir_path}")
    print(f"Running batch occlusion estimation using model: {model_path}")

    # Load model once
    model = YOLO(model_path)

    results = []

    for i, img_path in enumerate(images):
        pct, _ = calculate_occlusion(str(img_path), model=model)

        # Use arbitrary severity bands for now, but these need validation
        results.append(
            {
                "image_name": img_path.name,
                "occlusion_percentage": round(pct, 2),
                "severity": "High" if pct > 50 else ("Medium" if pct > 20 else "Low"),
            }
        )

        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(images)} images...")

    df = pd.DataFrame(results)
    workspace_dir = Path(__file__).resolve().parent.parent.parent
    out_file = workspace_dir / "runs" / "detect" / "occlusion_results.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)

    print("\nBatch Test Summary")
    print(f"Total processed: {len(df)}")
    print(f"High Severity (>50%): {len(df[df['severity'] == 'High'])}")
    print(f"Medium Severity (20-50%): {len(df[df['severity'] == 'Medium'])}")
    print(f"Low Severity (<20%): {len(df[df['severity'] == 'Low'])}")
    print(f"\nResults saved to: {out_file.absolute()}")


if __name__ == "__main__":
    workspace_dir = Path(__file__).resolve().parent.parent.parent
    test_dir = workspace_dir / "Yolo Dataset" / "test" / "images"
    model_path = (
        workspace_dir / "runs" / "detect" / "flood_sentinels_v3" / "weights" / "best.pt"
    )

    test_occlusion_batch(test_dir, str(model_path))
