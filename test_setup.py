#!/usr/bin/env python3
"""
Test script to verify system setup and dependencies
"""

import sys

def test_python_version():
    """Check Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_opencv():
    """Test OpenCV installation"""
    print("\nTesting OpenCV...")
    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__} installed")
        return True
    except ImportError:
        print("✗ OpenCV not installed")
        return False

def test_mediapipe():
    """Test MediaPipe installation"""
    print("\nTesting MediaPipe...")
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe {mp.__version__} installed")
        return True
    except ImportError:
        print("✗ MediaPipe not installed")
        return False

def test_numpy():
    """Test NumPy installation"""
    print("\nTesting NumPy...")
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__} installed")
        return True
    except ImportError:
        print("✗ NumPy not installed")
        return False

def test_pygame():
    """Test Pygame installation"""
    print("\nTesting Pygame...")
    try:
        import pygame
        print(f"✓ Pygame {pygame.version.ver} installed")
        return True
    except ImportError:
        print("⚠ Pygame not installed (optional - needed for sound alerts)")
        return None  # Optional dependency

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✓ Camera accessible")
                return True
            else:
                print("⚠ Camera opened but couldn't read frame")
                return False
        else:
            print("⚠ Could not open camera (may be in use or not connected)")
            return False
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_config_file():
    """Test configuration file"""
    print("\nTesting configuration file...")
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ config.json found and valid")
        return True
    except FileNotFoundError:
        print("⚠ config.json not found (will use defaults)")
        return None
    except json.JSONDecodeError:
        print("✗ config.json is not valid JSON")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("Jedawel LensSafe - System Check")
    print("="*50)
    
    results = []
    
    # Required tests
    results.append(("Python Version", test_python_version()))
    results.append(("OpenCV", test_opencv()))
    results.append(("MediaPipe", test_mediapipe()))
    results.append(("NumPy", test_numpy()))
    
    # Optional tests
    pygame_result = test_pygame()
    if pygame_result is not None:
        results.append(("Pygame", pygame_result))
    
    results.append(("Camera", test_camera()))
    
    config_result = test_config_file()
    if config_result is not None:
        results.append(("Config File", config_result))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    passed = sum(1 for name, result in results if result is True)
    failed = sum(1 for name, result in results if result is False)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    
    if failed == 0:
        print("\n✓ All tests passed! System is ready.")
        print("\nTo start the baby monitor, run:")
        print("  python baby_monitor.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
