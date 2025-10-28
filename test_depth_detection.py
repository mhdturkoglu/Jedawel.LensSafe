#!/usr/bin/env python3
"""
Unit tests for depth-based eye rubbing detection
"""

import unittest
from unittest.mock import Mock
import numpy as np
from baby_monitor import BabyMonitor


class TestDepthDetection(unittest.TestCase):
    """Test cases for depth-based eye rubbing detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = BabyMonitor()
        
    def create_mock_landmark(self, x, y, z):
        """Create a mock landmark with x, y, z coordinates"""
        landmark = Mock()
        landmark.x = x
        landmark.y = y
        landmark.z = z
        return landmark
    
    def create_mock_face_landmarks(self, eye_z_depth=0.0):
        """Create mock face landmarks with specific depth"""
        face_landmarks = Mock()
        face_landmarks.landmark = {}
        
        # Left eye indices
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        # Right eye indices
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        # Create landmarks for left eye (centered around x=0.3, y=0.3)
        for idx in left_eye_indices:
            face_landmarks.landmark[idx] = self.create_mock_landmark(0.3, 0.3, eye_z_depth)
        
        # Create landmarks for right eye (centered around x=0.7, y=0.3)
        for idx in right_eye_indices:
            face_landmarks.landmark[idx] = self.create_mock_landmark(0.7, 0.3, eye_z_depth)
        
        return face_landmarks
    
    def create_mock_hand_landmarks(self, x, y, z):
        """Create mock hand landmarks with index finger at specific position"""
        hand_landmarks = Mock()
        hand_landmarks.landmark = {}
        
        # Create index finger tip landmark
        from baby_monitor import mp
        index_finger_tip_idx = mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP
        hand_landmarks.landmark[index_finger_tip_idx] = self.create_mock_landmark(x, y, z)
        
        return hand_landmarks
    
    def test_hand_in_front_of_eye_close_proximity(self):
        """Test: Hand in front of eye and close - should detect rubbing"""
        # Eye at depth 0.0, hand at depth -0.02 (in front)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=-0.02)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing when hand is in front and close")
    
    def test_hand_behind_eye_close_proximity(self):
        """Test: Hand behind eye but close in 2D - should NOT detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.1 (behind)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.1)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should NOT detect eye rubbing when hand is behind the eye")
    
    def test_hand_far_from_eye_in_2d(self):
        """Test: Hand far from eye in 2D - should NOT detect rubbing"""
        # Eye at depth 0.0, hand at depth -0.02 (in front) but far in 2D
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.9, y=0.9, z=-0.02)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should NOT detect eye rubbing when hand is far in 2D space")
    
    def test_hand_at_same_depth_as_eye(self):
        """Test: Hand at same depth as eye and close - should detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.0 (same level)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.0)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing when hand is at same depth and close")
    
    def test_hand_slightly_behind_within_threshold(self):
        """Test: Hand slightly behind but within depth threshold - should detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.04 (slightly behind but within 0.05 threshold)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.04)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing when hand is within depth threshold")
    
    def test_hand_behind_beyond_threshold(self):
        """Test: Hand behind and beyond depth threshold - should NOT detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.1 (beyond 0.05 threshold)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.1)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should NOT detect eye rubbing when hand is beyond depth threshold")
    
    def test_right_eye_detection(self):
        """Test: Detection works for right eye as well"""
        # Eye at depth 0.0, hand near right eye (x=0.7)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.7, y=0.3, z=-0.02)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing for right eye")
    
    def test_no_face_landmarks(self):
        """Test: No detection when face landmarks are missing"""
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.0)
        
        result = self.monitor.detect_eye_rubbing(None, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should return False when face landmarks are None")
    
    def test_no_hand_landmarks(self):
        """Test: No detection when hand landmarks are missing"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, None, 640, 480)
        self.assertFalse(result, "Should return False when hand landmarks are None")
    
    def test_hand_far_in_front_close_in_2d(self):
        """Test: Hand far in front of eye but close in 2D - should NOT detect rubbing"""
        # Eye at depth 0.0, hand at depth -0.1 (far in front) but close in 2D
        # This simulates hand waving in front of face but not touching eye
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=-0.1)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should NOT detect eye rubbing when hand is far in front of eye")
    
    def test_hand_very_close_depth_match(self):
        """Test: Hand at exact same depth as eye and close in 2D - should detect rubbing"""
        # Eye at depth 0.0, hand at exact same depth (pressing on eye)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.0)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing when hand is at exact same depth")
    
    def test_hand_just_within_depth_threshold(self):
        """Test: Hand just within depth threshold - should detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.049 (just within 0.05 threshold)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.049)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertTrue(result, "Should detect eye rubbing when hand is just within depth threshold")
    
    def test_hand_just_outside_depth_threshold(self):
        """Test: Hand just outside depth threshold - should NOT detect rubbing"""
        # Eye at depth 0.0, hand at depth 0.06 (just outside 0.05 threshold)
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.06)
        
        result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        self.assertFalse(result, "Should NOT detect eye rubbing when hand is just outside depth threshold")


if __name__ == '__main__':
    unittest.main()
