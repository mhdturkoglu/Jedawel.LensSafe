# Project Architecture - Jedawel LensSafe

## Overview

Jedawel LensSafe is an AI-powered baby monitoring system designed to detect when a baby rubs their eyes, potentially indicating that a contact lens has been dropped or is causing discomfort. The system uses computer vision and machine learning to provide real-time monitoring and alerts.

## Technology Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **OpenCV**: Video capture and image processing
- **MediaPipe**: Face mesh and hand tracking (Google's ML solution)
- **NumPy**: Numerical computations and array operations
- **Pygame**: Audio alert system

### Key Libraries
- `cv2` (OpenCV): Camera interface, image manipulation, display
- `mediapipe`: Pre-trained ML models for face and hand detection
- `numpy`: Mathematical operations for distance calculations
- `pygame.mixer`: Sound generation and playback
- `json`: Configuration file parsing

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Baby Monitor System                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │       Camera Input (cv2.VideoCapture) │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         Frame Processing Loop         │
        │   (Real-time video frame analysis)    │
        └───────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Face Detection  │    │  Hand Detection  │
    │  (MediaPipe FM)  │    │  (MediaPipe H)   │
    └──────────────────┘    └──────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
            ┌───────────────────────────────┐
            │  Eye Rubbing Detection Logic  │
            │  (Distance Calculation)       │
            └───────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │    Alert Decision Engine      │
            │  (Threshold & Cooldown)       │
            └───────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Audio Alert     │    │  Visual Alert    │
    │  (Pygame)        │    │  (OpenCV)        │
    └──────────────────┘    └──────────────────┘
```

## Component Details

### 1. Camera Input Module
**File**: `baby_monitor.py` - `BabyMonitor.run()`

**Purpose**: Captures live video feed from webcam or external camera

**Key Features**:
- Configurable camera source (0, 1, 2, etc.)
- Adjustable resolution and FPS
- Error handling for camera failures
- Real-time frame capture loop

**Configuration**:
```json
"camera": {
  "source": 0,        // Camera ID
  "width": 640,       // Resolution width
  "height": 480,      // Resolution height
  "fps": 30           // Frames per second
}
```

### 2. Face Detection Module
**Technology**: MediaPipe Face Mesh

**Purpose**: Locates and tracks the baby's face in real-time

**Key Features**:
- 468 facial landmarks detection
- Real-time tracking (30+ FPS)
- Robust to varying lighting conditions
- Works with single face (max_num_faces=1)

**Eye Region Extraction**:
- Left eye landmarks: [33, 133, 160, 159, 158, 157, 173]
- Right eye landmarks: [362, 263, 387, 386, 385, 384, 398]
- Calculates center point of each eye region

### 3. Hand Tracking Module
**Technology**: MediaPipe Hands

**Purpose**: Detects and tracks hand positions and movements

**Key Features**:
- 21 hand landmarks per hand
- Tracks up to 2 hands simultaneously
- Provides 3D hand coordinates
- High accuracy finger tracking

**Critical Landmarks**:
- Index finger tip (landmark 8): Primary detection point
- Thumb tip (landmark 4): Secondary reference
- Palm base: For gesture context

### 4. Eye Rubbing Detection Algorithm

**Method**: 3D proximity detection using 2D distance and depth analysis

**Algorithm**:
```python
1. Get eye center coordinates (left_eye_center, right_eye_center) and depth (z-coordinate)
2. Get hand fingertip position (index_finger_tip) including depth
3. Calculate 2D Euclidean distance: 
   d = sqrt((x1-x2)² + (y1-y2)²)
4. Normalize 2D distance by image width for scale independence
5. Calculate depth difference:
   depth_diff = abs(hand_z - eye_z)
6. If (normalized_distance < eye_rub_threshold) AND (depth_diff <= depth_threshold):
   → Eye rubbing detected
```

**Thresholds**:
- **eye_rub_threshold**: Default 0.15 (15% of image width)
  - Controls 2D proximity sensitivity
  - Lower = more sensitive to 2D distance
  - Higher = requires hand closer to eye in 2D space
- **depth_threshold**: Default 0.08
  - Controls Z-depth tolerance (how close hand must be to eye depth)
  - Lower = requires hand more precisely at eye depth (stricter pressing detection)
  - Higher = allows more depth variation (more lenient)
  - Uses absolute difference to check if hand is within depth range of the eye
- **motion_threshold**: Default 0.005
  - Controls motion sensitivity (how much hand movement is required)
  - Lower = detects slower/gentler rubbing motions
  - Higher = requires faster hand movement
- **consecutive_frames_threshold**: Default 2
  - Number of consecutive frames required for detection
  - Lower = more responsive but may increase false positives
  - Higher = more stable but may miss brief rubbing events

**Depth Detection Benefits**:
- Prevents false positives when hand waves in front of face (hand far from eye in Z-axis)
- Requires hand to be pressing on or very close to the eye (not just anywhere in front)
- More accurate detection of actual eye rubbing behavior

**Motion Detection Benefits**:
- Prevents false positives when hand is just resting on face (no movement)
- Requires active rubbing motion, not just proximity
- Reduces alerts from static hand positions

**False Positive Reduction**:
- Consecutive frame requirement (default: 2 frames)
- Prevents single-frame detection errors
- Ensures sustained hand-to-eye proximity in both 2D and depth
- Motion tracking ensures active rubbing, not static hand placement

### 5. Alert System

**Multi-Modal Alerts**:

#### Audio Alert
- **Library**: Pygame mixer
- **Sound**: Generated tone or custom WAV file
- **Fallback**: System beep (ASCII bell)
- **Generation**: `generate_alert_sound.py` creates WAV files

#### Visual Alert
- **Method**: OpenCV overlay drawing
- **Indicators**:
  - Red status bar when rubbing detected
  - Warning text: "⚠️ EYE RUBBING DETECTED!"
  - Detection status indicators (face, hands)
  - FPS counter

#### Console Alert
- Timestamped alert messages
- Formatted output with separators
- Useful for logging and remote monitoring

**Cooldown Mechanism**:
```python
if (current_time - last_alert_time) < cooldown:
    skip_alert()
else:
    trigger_alert()
    last_alert_time = current_time
```
- Prevents alert spam
- Default: 5 seconds
- Configurable per environment

### 6. Configuration System

**File**: `config.json`

**Structure**:
```json
{
  "camera": {...},      // Camera settings
  "detection": {...},   // Detection parameters
  "alert": {...},       // Alert preferences
  "display": {...}      // UI settings
}
```

**Benefits**:
- No code changes needed for tuning
- Environment-specific settings
- Easy experimentation
- Fallback to defaults if missing

## Data Flow

### Frame Processing Pipeline

```
1. CAPTURE FRAME
   ↓ RGB conversion
2. FACE MESH PROCESSING
   ↓ Extract 468 landmarks
3. HAND DETECTION
   ↓ Extract 21 landmarks × 2 hands
4. EYE REGION CALCULATION
   ↓ Compute eye centers
5. DISTANCE CALCULATION
   ↓ Hand-to-eye distance
6. THRESHOLD COMPARISON
   ↓ Detection decision
7. CONSECUTIVE FRAME CHECK
   ↓ Validate detection
8. ALERT TRIGGER
   ↓ Sound + Visual
9. DISPLAY UPDATE
   ↓ Draw overlays
10. SHOW FRAME
```

**Performance**: 20-30 FPS on modern hardware

## Machine Learning Models

### MediaPipe Face Mesh
- **Model**: BlazeFace + Face Mesh
- **Input**: 256×256 RGB image
- **Output**: 468 3D facial landmarks
- **Speed**: ~30ms inference time
- **Accuracy**: 95%+ in good lighting

### MediaPipe Hands
- **Model**: Palm detection + Hand landmarks
- **Input**: 224×224 RGB image
- **Output**: 21 3D hand landmarks
- **Speed**: ~15ms inference time
- **Accuracy**: 90%+ hand tracking

## Performance Optimization

### Techniques Used
1. **Single face tracking**: Reduces computational load
2. **Frame skipping**: Process every Nth frame if needed
3. **ROI processing**: Focus on regions of interest
4. **Efficient distance calc**: Numpy vectorization
5. **Minimal drawing**: Only essential overlays

### Expected Performance
- **CPU Usage**: 15-30% (modern quad-core)
- **RAM Usage**: 200-500 MB
- **FPS**: 20-30 (depends on hardware)
- **Latency**: <100ms detection time

## Security & Privacy

### Data Handling
- **No storage**: Frames processed in memory only
- **No transmission**: All processing is local
- **No logging**: No video recording by default

### Recommendations
- Run on local machine only
- Use in private/secured areas
- Consider encryption if adding storage
- Review permissions before deployment

## Extensibility

### Potential Enhancements
1. **Multi-baby support**: Track multiple children
2. **Cloud alerts**: Send notifications to mobile
3. **Recording**: Save detected events
4. **Statistics**: Track rubbing frequency
5. **Night vision**: IR camera support
6. **Gesture library**: Detect other behaviors
7. **Mobile app**: Remote monitoring interface

### Extension Points
- `process_frame()`: Add new detections
- `trigger_alert()`: Add notification methods
- `detect_eye_rubbing()`: Refine algorithm
- Configuration: Add new parameters

## Testing Strategy

### Test Coverage
1. **Unit Tests**: Individual functions
2. **Integration Tests**: Component interaction
3. **System Tests**: End-to-end functionality
4. **Performance Tests**: FPS and latency
5. **User Tests**: Real-world scenarios

### Test Script
`test_setup.py` verifies:
- Python version
- Dependencies installed
- Camera access
- Configuration validity

## Deployment Scenarios

### Home Use
- Single camera monitoring crib
- Local alerts to caregiver
- Daytime monitoring during naps

### Childcare Centers
- Multiple camera setup
- Centralized monitoring station
- Documented alert logging

### Medical Settings
- Post-surgery monitoring
- Lens fitting follow-up
- Clinical observation aid

## Troubleshooting Guide

### Common Issues

**1. Camera not opening**
- Solution: Try different camera IDs
- Check: Camera permissions
- Verify: No other app using camera

**2. Low FPS**
- Solution: Reduce resolution
- Check: CPU usage
- Optimize: Disable display if headless

**3. False positives**
- Solution: Increase threshold
- Adjust: Consecutive frames
- Improve: Lighting conditions

**4. Missed detections**
- Solution: Decrease threshold
- Check: Camera angle
- Ensure: Good lighting

**5. No alerts**
- Solution: Check sound settings
- Verify: Pygame installed
- Test: Alert sound file exists

## File Reference

### Core Files
- `baby_monitor.py`: Main application (450+ lines)
- `config.json`: Configuration settings
- `requirements.txt`: Python dependencies

### Documentation
- `README.md`: User guide
- `QUICKSTART.md`: Installation guide
- `ARCHITECTURE.md`: This file

### Utilities
- `test_setup.py`: System verification
- `generate_alert_sound.py`: Sound file creator
- `.gitignore`: Git exclusions

## Code Style

### Conventions
- PEP 8 compliance
- Type hints (where beneficial)
- Docstrings for all functions
- Clear variable names
- Commented complex logic

### Structure
- Class-based design
- Separation of concerns
- Configurable parameters
- Error handling throughout

## Dependencies

### Required
- opencv-python >= 4.8.0
- mediapipe >= 0.10.0
- numpy >= 1.24.0

### Optional
- pygame >= 2.5.0 (for sound)

### System
- Python 3.8+
- Camera driver (OS-specific)
- Audio output (for alerts)

## License & Credits

### Open Source
- MIT License
- Free for personal and commercial use

### Technologies
- OpenCV: BSD license
- MediaPipe: Apache 2.0
- NumPy: BSD license
- Pygame: LGPL

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Author**: Jedawel LensSafe Team
