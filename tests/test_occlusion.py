import pytest
import numpy as np
from src.floodsentinel.estimate_occlusion import calculate_occlusion

def test_calculate_occlusion_no_blockage():
    """Test that occlusion returns 0.0 when no blockages are found"""
    # Create a mock YOLO result
    class MockBox:
        def __init__(self):
            self.cls = [0] # 0 = Defects
            self.xyxy = [[10, 10, 20, 20]]
            
    class MockResult:
        def __init__(self):
            self.orig_shape = (100, 100)
            self.boxes = [MockBox()]
            
    class MockModel:
        def __init__(self):
            self.names = {0: 'Defects', 1: 'Sewage blockage'}
            
        def __call__(self, *args, **kwargs):
            return [MockResult()]
            
    mock_model = MockModel()
    
    # We pass a fake image path since we mock the model anyway
    pct, res = calculate_occlusion("fake_path.jpg", model=mock_model)
    
    assert pct == 0.0
