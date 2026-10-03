from unittest.mock import MagicMock
import numpy as np

from src.floodsentinel.estimate_occlusion import calculate_occlusion


class MockBox:
    def __init__(self, cls_id, xyxy):
        self.cls = [cls_id]
        self.xyxy = [xyxy]


class MockResult:
    def __init__(self, boxes, orig_shape=(100, 100)):
        self.orig_shape = orig_shape
        self.boxes = boxes


class MockModel:
    def __init__(self, result):
        self.names = {0: "Defects", 1: "Sewage blockage"}
        self.result = result

    def __call__(self, *args, **kwargs):
        return [self.result]


def test_calculate_occlusion_no_blockage():
    """Test that occlusion returns 0.0 when no blockages are found"""
    boxes = [MockBox(cls_id=0, xyxy=[10, 10, 20, 20])]  # Only Defects found
    mock_model = MockModel(MockResult(boxes=boxes))

    pct, _ = calculate_occlusion("fake_path.jpg", model=mock_model)
    assert pct == 0.0


def test_calculate_occlusion_empty_image():
    """Test when no detections are made at all"""
    mock_model = MockModel(MockResult(boxes=[]))
    pct, _ = calculate_occlusion("fake_path.jpg", model=mock_model)
    assert pct == 0.0


def test_calculate_occlusion_partial_blockage():
    """Test occlusion calculation with a blockage taking up part of the grate"""
    boxes = [
        MockBox(cls_id=0, xyxy=[0, 0, 100, 100]),  # Grate (Defect bounding box)
        MockBox(cls_id=1, xyxy=[0, 0, 50, 50]),    # Blockage covering 1/4th of the area
    ]
    mock_model = MockModel(MockResult(boxes=boxes))

    pct, _ = calculate_occlusion("fake_path.jpg", model=mock_model)
    # Total grate area = 100x100 = 10000
    # Blockage area = 50x50 = 2500
    # Percentage = 2500 / 10000 * 100 = 25.0
    assert pct == 25.0


def test_calculate_occlusion_full_blockage():
    """Test occlusion calculation with a blockage taking up the entire grate"""
    boxes = [
        MockBox(cls_id=0, xyxy=[10, 10, 50, 50]),
        MockBox(cls_id=1, xyxy=[10, 10, 50, 50]),
    ]
    mock_model = MockModel(MockResult(boxes=boxes))

    pct, _ = calculate_occlusion("fake_path.jpg", model=mock_model)
    assert pct == 100.0


def test_calculate_occlusion_overlapping_blockages():
    """Test multiple overlapping blockages. Area should be calculated correctly without double counting."""
    boxes = [
        MockBox(cls_id=0, xyxy=[0, 0, 100, 100]),
        MockBox(cls_id=1, xyxy=[0, 0, 50, 50]),    # 2500 pixels
        MockBox(cls_id=1, xyxy=[25, 25, 75, 75]),  # 2500 pixels, but overlaps!
    ]
    mock_model = MockModel(MockResult(boxes=boxes))

    pct, _ = calculate_occlusion("fake_path.jpg", model=mock_model)
    # The mask union of [0,0,50,50] and [25,25,75,75] 
    # Total mask area = (50*50) + (50*50) - (25*25) = 2500 + 2500 - 625 = 4375
    # Grate area = 10000
    assert pct == 43.75
