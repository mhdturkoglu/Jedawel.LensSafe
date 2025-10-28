#!/usr/bin/env python3
"""
Jedawel LensSafe - AI Baby Monitoring System
Detects when a baby rubs their eyes and alerts caregivers
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import time
import argparse
from datetime import datetime
import sys

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Sound alerts will be disabled.")


class BabyMonitor:
    """Main class for baby monitoring with eye rubbing detection"""
    
    def __init__(self, config_path='config.json'):
        """Initialize the baby monitor with configuration"""
        self.config = self.load_config(config_path)
        
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face mesh and hand tracking
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=self.config['detection']['min_detection_confidence'],
            min_tracking_confidence=self.config['detection']['min_tracking_confidence']
        )
        
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=self.config['detection']['min_detection_confidence'],
            min_tracking_confidence=self.config['detection']['min_tracking_confidence']
        )
        
        # Alert state
        self.last_alert_time = 0
        self.consecutive_detections = 0
        self.alert_cooldown = self.config['alert']['alert_cooldown_seconds']
        
        # Hand position history for motion tracking
        self.hand_position_history = []
        self.max_history_frames = self.config['detection'].get('motion_history_frames', 5)
        
        # Initialize pygame for sound alerts
        if PYGAME_AVAILABLE and self.config['alert']['sound_enabled']:
            try:
                pygame.mixer.init()
                self.sound_enabled = True
            except:
                print("Warning: Could not initialize pygame mixer. Sound alerts disabled.")
                self.sound_enabled = False
        else:
            self.sound_enabled = False
        
        # FPS tracking
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return self.get_default_config()
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {config_path}. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "camera": {"source": 0, "width": 640, "height": 480, "fps": 30},
            "detection": {
                "eye_rub_threshold": 0.15,
                "depth_threshold": 0.05,
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5,
                "consecutive_frames_threshold": 3,
                "motion_threshold": 0.01,
                "motion_history_frames": 5
            },
            "alert": {
                "sound_enabled": False,
                "alert_cooldown_seconds": 5,
                "visual_alert_enabled": True
            },
            "display": {
                "show_video": True,
                "show_fps": True,
                "window_name": "Jedawel LensSafe - Baby Monitor"
            }
        }
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_hand_motion(self, current_position):
        """Calculate hand motion/velocity based on position history
        
        Args:
            current_position: Current hand position as [x, y] array
            
        Returns:
            float: Average motion magnitude (velocity) over history frames
        """
        # Add current position to history
        self.hand_position_history.append(current_position.copy())
        
        # Keep only the last N frames
        if len(self.hand_position_history) > self.max_history_frames:
            self.hand_position_history.pop(0)
        
        # Need at least 2 positions to calculate motion
        if len(self.hand_position_history) < 2:
            return 0.0
        
        # Calculate motion between consecutive frames
        motions = []
        for i in range(1, len(self.hand_position_history)):
            prev_pos = self.hand_position_history[i - 1]
            curr_pos = self.hand_position_history[i]
            motion = self.calculate_distance(prev_pos, curr_pos)
            motions.append(motion)
        
        # Return average motion magnitude
        return np.mean(motions) if motions else 0.0
    
    def get_eye_regions(self, face_landmarks, image_width, image_height):
        """Extract eye region coordinates from face landmarks"""
        # Left eye indices (approximate center region)
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        # Right eye indices (approximate center region)
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        left_eye_points = []
        right_eye_points = []
        left_eye_depths = []
        right_eye_depths = []
        
        for idx in left_eye_indices:
            landmark = face_landmarks.landmark[idx]
            left_eye_points.append([landmark.x * image_width, landmark.y * image_height])
            left_eye_depths.append(landmark.z)
        
        for idx in right_eye_indices:
            landmark = face_landmarks.landmark[idx]
            right_eye_points.append([landmark.x * image_width, landmark.y * image_height])
            right_eye_depths.append(landmark.z)
        
        # Calculate centers
        left_eye_center = np.mean(left_eye_points, axis=0)
        right_eye_center = np.mean(right_eye_points, axis=0)
        
        # Calculate average depth
        left_eye_depth = np.mean(left_eye_depths)
        right_eye_depth = np.mean(right_eye_depths)
        
        return left_eye_center, right_eye_center, left_eye_depth, right_eye_depth
    
    def detect_eye_rubbing(self, face_landmarks, hand_landmarks, image_width, image_height):
        """Detect if hand is rubbing eye region (requires both proximity AND motion)"""
        if face_landmarks is None or hand_landmarks is None:
            # Clear hand position history if no hand is detected
            self.hand_position_history = []
            return False
        
        # Get eye regions
        left_eye_center, right_eye_center, left_eye_depth, right_eye_depth = self.get_eye_regions(
            face_landmarks, image_width, image_height
        )
        
        # Get hand fingertip positions (index finger tip and thumb tip)
        index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pos = np.array([index_finger_tip.x * image_width, index_finger_tip.y * image_height])
        index_depth = index_finger_tip.z
        
        # Calculate distances to eyes
        dist_to_left_eye = self.calculate_distance(index_pos, left_eye_center)
        dist_to_right_eye = self.calculate_distance(index_pos, right_eye_center)
        
        # Normalize distances by image width
        normalized_dist_left = dist_to_left_eye / image_width
        normalized_dist_right = dist_to_right_eye / image_width
        
        # Check if hand is close to either eye
        threshold = self.config['detection']['eye_rub_threshold']
        depth_threshold = self.config['detection'].get('depth_threshold', 0.05)
        
        # Check left eye: hand must be close in 2D AND at approximately the same depth (pressing on eye)
        # The hand should be within a small depth range around the eye, not just in front
        left_depth_diff = abs(index_depth - left_eye_depth)
        left_eye_close = (normalized_dist_left < threshold and 
                         left_depth_diff <= depth_threshold)
        
        # Check right eye: hand must be close in 2D AND at approximately the same depth (pressing on eye)
        # The hand should be within a small depth range around the eye, not just in front
        right_depth_diff = abs(index_depth - right_eye_depth)
        right_eye_close = (normalized_dist_right < threshold and 
                          right_depth_diff <= depth_threshold)
        
        is_near_eye = left_eye_close or right_eye_close
        
        # Calculate hand motion (velocity)
        hand_motion = self.calculate_hand_motion(index_pos)
        
        # Normalize motion by image width for consistency
        normalized_motion = hand_motion / image_width
        
        # Get motion threshold from config
        motion_threshold = self.config['detection'].get('motion_threshold', 0.01)
        
        # Only detect rubbing if hand is near eye AND there's sufficient motion
        # This prevents false positives when hand is just resting on face
        is_rubbing = is_near_eye and (normalized_motion >= motion_threshold)
        
        # If hand is not near eye, clear the position history
        if not is_near_eye:
            self.hand_position_history = []
        
        return is_rubbing
    
    def trigger_alert(self):
        """Trigger an alert (sound and/or visual)"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        self.last_alert_time = current_time
        
        # Sound alert
        if self.sound_enabled:
            try:
                # Generate a simple beep sound
                self.play_alert_sound()
            except Exception as e:
                print(f"Warning: Could not play alert sound: {e}")
        
        # Console alert
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*50}")
        print(f"⚠️  ALERT: Eye rubbing detected! ({timestamp})")
        print(f"{'='*50}\n")
    
    def play_alert_sound(self):
        """Play alert sound using pygame or system beep"""
        if not self.sound_enabled:
            return
        
        try:
            # Try to load custom sound file
            sound_file = self.config['alert'].get('sound_file', 'alert.wav')
            try:
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
            except:
                # If custom sound not available, generate a beep
                self.generate_beep_sound()
        except Exception as e:
            print(f"Sound error: {e}")
    
    def generate_beep_sound(self):
        """Generate a simple beep sound"""
        try:
            # Simple system beep
            print('\a')  # ASCII bell character
        except:
            pass
    
    def update_fps(self):
        """Update FPS calculation"""
        self.fps_frame_count += 1
        elapsed_time = time.time() - self.fps_start_time
        
        if elapsed_time > 1.0:
            self.current_fps = self.fps_frame_count / elapsed_time
            self.fps_frame_count = 0
            self.fps_start_time = time.time()
    
    def draw_overlays(self, frame, face_detected, hands_detected, is_rubbing):
        """Draw status overlays on the frame"""
        height, width = frame.shape[:2]
        
        # Status text
        status_color = (0, 0, 255) if is_rubbing else (0, 255, 0)
        status_text = "⚠️ EYE RUBBING DETECTED!" if is_rubbing else "Monitoring..."
        
        # Draw status bar
        cv2.rectangle(frame, (0, 0), (width, 40), (0, 0, 0), -1)
        cv2.putText(frame, status_text, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Draw FPS if enabled
        if self.config['display']['show_fps']:
            fps_text = f"FPS: {self.current_fps:.1f}"
            cv2.putText(frame, fps_text, (width - 120, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw detection indicators
        indicator_y = 50
        face_color = (0, 255, 0) if face_detected else (128, 128, 128)
        hand_color = (0, 255, 0) if hands_detected else (128, 128, 128)
        
        cv2.putText(frame, f"Face: {'✓' if face_detected else '✗'}", (10, indicator_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, face_color, 2)
        cv2.putText(frame, f"Hands: {'✓' if hands_detected else '✗'}", (100, indicator_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, hand_color, 2)
        
        return frame
    
    def process_frame(self, frame):
        """Process a single frame for detection"""
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        
        # Process face and hands
        face_results = self.face_mesh.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        
        face_detected = face_results.multi_face_landmarks is not None
        hands_detected = hand_results.multi_hand_landmarks is not None
        is_rubbing = False
        
        # Draw face mesh
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                # Draw eye regions
                left_eye_center, right_eye_center, _, _ = self.get_eye_regions(
                    face_landmarks, width, height
                )
                cv2.circle(frame, tuple(left_eye_center.astype(int)), 5, (0, 255, 255), -1)
                cv2.circle(frame, tuple(right_eye_center.astype(int)), 5, (0, 255, 255), -1)
        
        # Draw hand landmarks and check for eye rubbing
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Check for eye rubbing
                if face_results.multi_face_landmarks:
                    if self.detect_eye_rubbing(
                        face_results.multi_face_landmarks[0],
                        hand_landmarks,
                        width, height
                    ):
                        is_rubbing = True
        
        # Handle eye rubbing detection
        if is_rubbing:
            self.consecutive_detections += 1
            if self.consecutive_detections >= self.config['detection']['consecutive_frames_threshold']:
                self.trigger_alert()
        else:
            self.consecutive_detections = 0
        
        # Draw overlays
        if self.config['display']['show_video']:
            frame = self.draw_overlays(frame, face_detected, hands_detected, is_rubbing)
        
        return frame, is_rubbing
    
    def run(self, camera_source=None, show_display=None):
        """Run the baby monitor"""
        if camera_source is None:
            camera_source = self.config['camera']['source']
        
        if show_display is None:
            show_display = self.config['display']['show_video']
        
        # Open camera
        cap = cv2.VideoCapture(camera_source)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_source}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
        cap.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])
        
        print("Baby Monitor Started!")
        print("Press 'q' to quit")
        print("-" * 50)
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: Failed to grab frame")
                    break
                
                # Process frame
                frame, is_rubbing = self.process_frame(frame)
                
                # Update FPS
                self.update_fps()
                
                # Display frame
                if show_display:
                    cv2.imshow(self.config['display']['window_name'], frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopping baby monitor...")
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping baby monitor...")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.sound_enabled:
            try:
                pygame.mixer.quit()
            except:
                pass


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Jedawel LensSafe - AI Baby Monitor')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--camera', type=int, help='Camera source ID')
    parser.add_argument('--no-display', action='store_true', help='Run without video display')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Set debug level
    if args.debug:
        print("Debug mode enabled")
    
    # Initialize and run monitor
    try:
        monitor = BabyMonitor(config_path=args.config)
        
        camera_source = args.camera if args.camera is not None else None
        show_display = not args.no_display
        
        monitor.run(camera_source=camera_source, show_display=show_display)
        
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
