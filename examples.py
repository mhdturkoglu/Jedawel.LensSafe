#!/usr/bin/env python3
"""
Example usage script for Jedawel LensSafe Baby Monitor
Demonstrates different ways to use the monitoring system
"""

from baby_monitor import BabyMonitor
import json

def example_basic_usage():
    """Basic usage example with default settings"""
    print("Example 1: Basic Usage")
    print("-" * 50)
    
    # Create monitor with default config
    monitor = BabyMonitor()
    
    # Run the monitor
    monitor.run()

def example_custom_config():
    """Example with custom configuration"""
    print("Example 2: Custom Configuration")
    print("-" * 50)
    
    # Create custom config
    custom_config = {
        "camera": {
            "source": 0,
            "width": 1280,  # Higher resolution
            "height": 720,
            "fps": 30
        },
        "detection": {
            "eye_rub_threshold": 0.12,  # More sensitive
            "min_detection_confidence": 0.6,
            "min_tracking_confidence": 0.6,
            "consecutive_frames_threshold": 2  # Faster detection
        },
        "alert": {
            "sound_enabled": True,
            "alert_cooldown_seconds": 3,  # Shorter cooldown
            "visual_alert_enabled": True
        },
        "display": {
            "show_video": True,
            "show_fps": True,
            "window_name": "Baby Monitor - High Sensitivity"
        }
    }
    
    # Save custom config
    with open('custom_config.json', 'w') as f:
        json.dump(custom_config, f, indent=2)
    
    # Create monitor with custom config
    monitor = BabyMonitor(config_path='custom_config.json')
    
    # Run the monitor
    monitor.run()

def example_headless_mode():
    """Example for running without display (headless/server mode)"""
    print("Example 3: Headless Mode")
    print("-" * 50)
    print("Running without video display...")
    print("Alerts will be printed to console and played as sound")
    
    # Create monitor
    monitor = BabyMonitor()
    
    # Run without display
    monitor.run(show_display=False)

def example_specific_camera():
    """Example using a specific camera"""
    print("Example 4: Specific Camera")
    print("-" * 50)
    print("Using camera 1 (external camera)...")
    
    # Create monitor
    monitor = BabyMonitor()
    
    # Run with specific camera
    monitor.run(camera_source=1)

def example_programmatic_monitoring():
    """Example showing programmatic access to monitoring data"""
    print("Example 5: Programmatic Monitoring")
    print("-" * 50)
    
    import cv2
    
    # Create monitor
    monitor = BabyMonitor()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Processing frames programmatically...")
    print("Press 'q' to quit")
    
    frame_count = 0
    detection_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, is_rubbing = monitor.process_frame(frame)
            
            # Custom handling of detection
            if is_rubbing:
                detection_count += 1
                print(f"Frame {frame_count}: Eye rubbing detected!")
            
            # Display frame
            cv2.imshow("Programmatic Monitor", processed_frame)
            
            frame_count += 1
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        monitor.cleanup()
        
        # Print statistics
        print(f"\nStatistics:")
        print(f"Total frames processed: {frame_count}")
        print(f"Eye rubbing detections: {detection_count}")
        if frame_count > 0:
            print(f"Detection rate: {(detection_count/frame_count)*100:.2f}%")

def main():
    """Main example selector"""
    print("="*60)
    print("Jedawel LensSafe - Usage Examples")
    print("="*60)
    print("\nAvailable examples:")
    print("1. Basic Usage (default settings)")
    print("2. Custom Configuration (high sensitivity)")
    print("3. Headless Mode (no display)")
    print("4. Specific Camera (external camera)")
    print("5. Programmatic Monitoring (custom processing)")
    print("\nNote: Press 'q' in any example to quit")
    print("\n" + "="*60)
    
    choice = input("\nSelect example (1-5) or 'q' to quit: ").strip()
    
    examples = {
        '1': example_basic_usage,
        '2': example_custom_config,
        '3': example_headless_mode,
        '4': example_specific_camera,
        '5': example_programmatic_monitoring,
    }
    
    if choice.lower() == 'q':
        print("Goodbye!")
        return
    
    if choice in examples:
        print("\n")
        examples[choice]()
    else:
        print("Invalid choice. Please select 1-5.")

if __name__ == '__main__':
    main()
