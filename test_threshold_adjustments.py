#!/usr/bin/env python3
"""
Unit tests to validate threshold adjustments
Tests to ensure the new thresholds reduce false negatives while maintaining low false positives
"""

import unittest
from unittest.mock import Mock
import numpy as np
from baby_monitor import BabyMonitor


class TestThresholdAdjustments(unittest.TestCase):
    """Test cases for validating threshold adjustments"""
    
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
        import mediapipe as mp
        index_finger_tip_idx = mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP
        hand_landmarks.landmark[index_finger_tip_idx] = self.create_mock_landmark(x, y, z)
        
        return hand_landmarks
    
    def test_gentle_rubbing_detected(self):
        """Test: Gentle/slow rubbing motion should be detected with new lower motion threshold"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate gentle rubbing motion (slower than old threshold of 0.01)
        # New threshold of 0.005 should detect this
        positions = [
            (0.300, 0.300),
            (0.304, 0.302),  # Small movements
            (0.308, 0.300),
            (0.304, 0.298),
            (0.300, 0.300),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should detect with new lower motion threshold
        self.assertTrue(result, "Should detect gentle rubbing with new lower motion threshold")
    
    def test_slight_depth_variation_detected(self):
        """Test: Rubbing with slight depth variation should be detected with new depth threshold"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate rubbing motion with depth at 0.07 (between old 0.05 and new 0.08)
        # Old threshold would miss this, new threshold should catch it
        positions = [
            (0.30, 0.30),
            (0.32, 0.31),
            (0.34, 0.30),
            (0.32, 0.29),
            (0.30, 0.30),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.07)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should detect with new depth threshold of 0.08
        self.assertTrue(result, "Should detect rubbing with slight depth variation")
    
    def test_faster_detection_with_fewer_frames(self):
        """Test: Detection should occur faster with consecutive_frames_threshold of 2"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate rubbing motion
        positions = [
            (0.30, 0.30),
            (0.34, 0.32),
            (0.28, 0.28),
        ]
        
        detection_count = 0
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            # Track consecutive detections
            if self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480):
                detection_count += 1
        
        # With new threshold of 2, should have detected in 3 frames
        self.assertGreater(detection_count, 0, "Should detect with fewer consecutive frames")
    
    def test_very_slow_motion_still_not_detected(self):
        """Test: Very minimal motion should still not trigger (prevents false positives)"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Extremely slow motion (below even the new 0.005 threshold)
        positions = [
            (0.3000, 0.3000),
            (0.3001, 0.3000),
            (0.3002, 0.3000),
            (0.3003, 0.3000),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect - motion too slow even for new threshold
        self.assertFalse(result, "Very slow motion should still not trigger")
    
    def test_excessive_depth_difference_still_rejected(self):
        """Test: Hand too far from eye depth should still not trigger (prevents false positives)"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate motion with depth at 0.15 (beyond new 0.08 threshold)
        positions = [
            (0.30, 0.30),
            (0.34, 0.32),
            (0.28, 0.28),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.15)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect - depth difference too large
        self.assertFalse(result, "Excessive depth difference should still be rejected")
    
    def test_realistic_eye_rubbing_scenario(self):
        """Test: Realistic eye rubbing with natural variations should be detected"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate realistic rubbing with varying depth and moderate motion
        scenarios = [
            [(0.30, 0.30, 0.00), (0.32, 0.31, 0.02), (0.34, 0.30, 0.04), (0.32, 0.29, 0.03), (0.30, 0.30, 0.01)],
            [(0.30, 0.30, 0.05), (0.33, 0.32, 0.06), (0.28, 0.28, 0.07), (0.31, 0.31, 0.05)],
        ]
        
        for scenario in scenarios:
            self.monitor.hand_position_history = []  # Reset history
            detection_occurred = False
            
            for x, y, z in scenario:
                hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=z)
                if self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480):
                    detection_occurred = True
                    break
            
            self.assertTrue(detection_occurred, f"Realistic rubbing scenario should be detected: {scenario}")
    
    def test_hand_resting_still_not_detected(self):
        """Test: Static hand near eye should still not trigger (motion check prevents this)"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Hand near eye but not moving
        for i in range(10):
            hand_landmarks = self.create_mock_hand_landmarks(x=0.30, y=0.30, z=0.03)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect - no motion
        self.assertFalse(result, "Static hand should not trigger detection")
    
    def test_config_values_correct(self):
        """Test: Verify that config values are set correctly"""
        self.assertEqual(self.monitor.config['detection']['depth_threshold'], 0.08, 
                        "Depth threshold should be 0.08")
        self.assertEqual(self.monitor.config['detection']['motion_threshold'], 0.004, 
                        "Motion threshold should be 0.004")
        self.assertEqual(self.monitor.config['detection']['consecutive_frames_threshold'], 2, 
                        "Consecutive frames threshold should be 2")


if __name__ == '__main__':
    unittest.main()
