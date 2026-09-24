"""
COCO to YOLO Annotation Converter
Converts _annotations.coco.json in each split (train/valid/test)
into per-image YOLO .txt label files.
YOLO format per line: class_id  cx  cy  w  h  (all normalized 0-1)
Also fixes data.yaml with correct nc and class names.
"""

import json
from pathlib import Path

DATASET_ROOT = Path(r"c:\Users\Lenovo\OneDrive\Desktop\Flood Sentinals\Yolo Dataset")
SPLITS = ["train", "valid", "test"]
DATA_YAML = DATASET_ROOT / "data.yaml"


def convert_split(split):
    split_dir  = DATASET_ROOT / split
    coco_json  = split_dir / "_annotations.coco.json"
    labels_dir = split_dir / "labels"

    if not coco_json.exists():
        print(f"  WARNING: No COCO JSON found for {split}, skipping.")
        return {}

    labels_dir.mkdir(exist_ok=True)

    with open(coco_json, "r") as f:
        coco = json.load(f)

    categories    = sorted(coco["categories"], key=lambda c: c["id"])
    cat_id_to_idx = {cat["id"]: idx for idx, cat in enumerate(categories)}
    class_names   = [cat["name"] for cat in categories]

    ann_by_image = {}
    for ann in coco["annotations"]:
        ann_by_image.setdefault(ann["image_id"], []).append(ann)

    written = 0
    empty   = 0

    for img_info in coco["images"]:
        img_id   = img_info["id"]
        img_w    = img_info["width"]
        img_h    = img_info["height"]
        img_stem = Path(img_info["file_name"]).stem
        txt_path = labels_dir / f"{img_stem}.txt"

        annotations = ann_by_image.get(img_id, [])

        if not annotations:
            txt_path.write_text("")
            empty += 1
            continue

        lines = []
        for ann in annotations:
            x, y, w, h = ann["bbox"]
            class_idx  = cat_id_to_idx[ann["category_id"]]

            cx = (x + w / 2.0) / img_w
            cy = (y + h / 2.0) / img_h
            nw = w / img_w
            nh = h / img_h

            cx = max(0.0, min(1.0, cx))
            cy = max(0.0, min(1.0, cy))
            nw = max(0.0, min(1.0, nw))
            nh = max(0.0, min(1.0, nh))

            lines.append(f"{class_idx} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        txt_path.write_text("\n".join(lines) + "\n")
        written += 1

    return {"class_names": class_names, "total": len(coco["images"]), "written": written, "empty": empty}


def fix_data_yaml(class_names):
    names_str    = "[" + ", ".join(class_names) + "]"
    yaml_content = (
        "train: ../train/images\n"
        "val: ../valid/images\n"
        "test: ../test/images\n\n"
        f"nc: {len(class_names)}\n"
        f"names: {names_str}\n\n"
        "roboflow:\n"
        "  workspace: krishna-gupta-v9ctt\n"
        "  project: storm-drain-model-cjhye-3oypn\n"
        "  version: 1\n"
        "  license: CC BY 4.0\n"
        "  url: https://app.roboflow.com/krishna-gupta-v9ctt/storm-drain-model-cjhye-3oypn/1\n"
    )
    DATA_YAML.write_text(yaml_content)
    print(f"\ndata.yaml updated: nc={len(class_names)}, names={class_names}")


def verify_labels(split, n=2):
    labels_dir = DATASET_ROOT / split / "labels"
    non_empty  = [f for f in labels_dir.glob("*.txt") if f.stat().st_size > 0]
    print(f"\n  Sample non-empty labels from {split}:")
    for lbl in non_empty[:n]:
        print(f"     {lbl.name}:")
        for line in lbl.read_text().strip().splitlines():
            print(f"       {line}")


def main():
    print("=" * 60)
    print("  COCO to YOLO Annotation Converter")
    print("=" * 60)

    all_class_names = []

    for split in SPLITS:
        print(f"\nProcessing {split} ...")
        result = convert_split(split)
        if not result:
            continue

        names = result["class_names"]
        if names and not all_class_names:
            all_class_names = names

        print(f"   Classes   : {names}")
        print(f"   Total imgs: {result['total']}")
        print(f"   Annotated : {result['written']}  (labels with bounding boxes)")
        print(f"   Negative  : {result['empty']}   (empty labels - background)")

    if all_class_names:
        fix_data_yaml(all_class_names)
    else:
        print("\nWARNING: Could not determine class names - data.yaml NOT updated.")

    for split in SPLITS:
        labels_dir = DATASET_ROOT / split / "labels"
        if labels_dir.exists():
            verify_labels(split, n=2)

    print("\n" + "=" * 60)
    print("  Conversion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
