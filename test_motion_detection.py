#!/usr/bin/env python3
"""
Unit tests for motion-based eye rubbing detection
Tests to ensure false positives are reduced by requiring motion
"""

import unittest
from unittest.mock import Mock
import numpy as np
from baby_monitor import BabyMonitor


class TestMotionDetection(unittest.TestCase):
    """Test cases for motion-based eye rubbing detection"""
    
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
    
    def test_static_hand_near_eye_no_motion(self):
        """Test: Static hand near eye without motion - should NOT detect rubbing"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate static hand at same position for multiple frames
        for i in range(10):
            hand_landmarks = self.create_mock_hand_landmarks(x=0.3, y=0.3, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
            
        # Last detection should be False because hand is not moving
        self.assertFalse(result, "Should NOT detect rubbing when hand is static near eye")
    
    def test_moving_hand_near_eye_with_motion(self):
        """Test: Moving hand near eye with motion - should detect rubbing"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate hand moving near eye (rubbing motion)
        positions = [
            (0.30, 0.30),
            (0.32, 0.31),
            (0.34, 0.30),
            (0.32, 0.29),
            (0.30, 0.30),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should detect rubbing after several frames of motion
        self.assertTrue(result, "Should detect rubbing when hand is moving near eye")
    
    def test_hand_motion_calculation_static(self):
        """Test: Motion calculation for static hand should be zero"""
        # Add same position multiple times
        pos = np.array([100.0, 100.0])
        for i in range(5):
            motion = self.monitor.calculate_hand_motion(pos)
        
        self.assertEqual(motion, 0.0, "Motion should be zero for static hand")
    
    def test_hand_motion_calculation_moving(self):
        """Test: Motion calculation for moving hand should be positive"""
        # Add positions with increasing values (moving hand)
        positions = [
            np.array([100.0, 100.0]),
            np.array([110.0, 105.0]),
            np.array([120.0, 110.0]),
            np.array([130.0, 115.0]),
        ]
        
        motion = 0.0
        for pos in positions:
            motion = self.monitor.calculate_hand_motion(pos)
        
        self.assertGreater(motion, 0.0, "Motion should be positive for moving hand")
    
    def test_hand_position_history_limit(self):
        """Test: Hand position history should be limited to max_history_frames"""
        # Add more positions than max_history_frames
        for i in range(20):
            pos = np.array([float(i), float(i)])
            self.monitor.calculate_hand_motion(pos)
        
        self.assertEqual(
            len(self.monitor.hand_position_history), 
            self.monitor.max_history_frames,
            f"History should be limited to {self.monitor.max_history_frames} frames"
        )
    
    def test_slow_motion_below_threshold(self):
        """Test: Very slow motion below threshold should not trigger detection"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate very slow motion (below motion threshold)
        positions = [
            (0.300, 0.300),
            (0.301, 0.300),
            (0.302, 0.300),
            (0.303, 0.300),
            (0.304, 0.300),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect because motion is too slow (below threshold)
        self.assertFalse(result, "Should NOT detect rubbing for very slow motion")
    
    def test_fast_motion_above_threshold(self):
        """Test: Fast motion above threshold should trigger detection"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate fast rubbing motion (above motion threshold)
        positions = [
            (0.30, 0.30),
            (0.35, 0.32),
            (0.28, 0.28),
            (0.33, 0.31),
            (0.29, 0.29),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should detect because motion is fast enough
        self.assertTrue(result, "Should detect rubbing for fast motion")
    
    def test_hand_far_from_eye_with_motion(self):
        """Test: Hand far from eye with motion - should NOT detect"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate hand moving but far from eye
        positions = [
            (0.80, 0.80),
            (0.82, 0.81),
            (0.84, 0.80),
            (0.82, 0.79),
            (0.80, 0.80),
        ]
        
        result = False
        for x, y in positions:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect because hand is far from eye
        self.assertFalse(result, "Should NOT detect when hand is far from eye even with motion")
    
    def test_hand_resting_on_face_scenario(self):
        """Test: Realistic scenario - hand resting on face without rubbing"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate hand moving to face, then staying still (resting)
        # This is the main false positive scenario we want to fix
        moving_to_face = [
            (0.50, 0.50),
            (0.40, 0.40),
            (0.35, 0.35),
            (0.32, 0.32),
            (0.30, 0.30),
        ]
        
        # Hand arrives at face and stops
        for x, y in moving_to_face:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Now hand is static on face for several frames
        result = False
        for i in range(10):
            hand_landmarks = self.create_mock_hand_landmarks(x=0.30, y=0.30, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Should NOT detect because hand stopped moving
        self.assertFalse(result, "Should NOT detect when hand is resting on face without motion")
    
    def test_actual_rubbing_scenario(self):
        """Test: Realistic scenario - actual eye rubbing with continuous motion"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Simulate actual rubbing - continuous back and forth motion near eye
        rubbing_motion = [
            (0.30, 0.30),
            (0.34, 0.32),
            (0.28, 0.28),
            (0.33, 0.31),
            (0.29, 0.29),
            (0.35, 0.33),
            (0.27, 0.27),
            (0.32, 0.30),
        ]
        
        detection_count = 0
        for x, y in rubbing_motion:
            hand_landmarks = self.create_mock_hand_landmarks(x=x, y=y, z=0.0)
            result = self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
            if result:
                detection_count += 1
        
        # Should detect rubbing in most frames during active rubbing
        self.assertGreater(detection_count, 3, "Should detect rubbing during continuous motion")
    
    def test_history_cleared_when_hand_leaves_eye(self):
        """Test: Position history should be cleared when hand moves away from eye"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Build up some history near eye
        for i in range(5):
            hand_landmarks = self.create_mock_hand_landmarks(x=0.30 + i*0.01, y=0.30, z=0.0)
            self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Verify history has items
        self.assertGreater(len(self.monitor.hand_position_history), 0)
        
        # Move hand far from eye
        hand_landmarks = self.create_mock_hand_landmarks(x=0.80, y=0.80, z=0.0)
        self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # History should be cleared
        self.assertEqual(
            len(self.monitor.hand_position_history), 0, 
            "History should be cleared when hand leaves eye region"
        )
    
    def test_history_cleared_when_no_hand_detected(self):
        """Test: Position history should be cleared when hand is not detected"""
        face_landmarks = self.create_mock_face_landmarks(eye_z_depth=0.0)
        
        # Build up some history
        for i in range(5):
            hand_landmarks = self.create_mock_hand_landmarks(x=0.30 + i*0.01, y=0.30, z=0.0)
            self.monitor.detect_eye_rubbing(face_landmarks, hand_landmarks, 640, 480)
        
        # Verify history has items
        self.assertGreater(len(self.monitor.hand_position_history), 0)
        
        # Call with None hand_landmarks
        self.monitor.detect_eye_rubbing(face_landmarks, None, 640, 480)
        
        # History should be cleared
        self.assertEqual(
            len(self.monitor.hand_position_history), 0,
            "History should be cleared when hand is not detected"
        )


if __name__ == '__main__':
    unittest.main()
