# Jedawel LensSafe - AI Baby Monitoring System

An AI-powered baby monitoring application that uses computer vision to detect when a baby rubs their eyes, alerting caregivers that a contact lens might have been dropped.

## Features

- **Real-time Baby Tracking**: Uses computer vision to track baby's face and movements
- **Eye Rubbing Detection**: Detects hand-to-face gestures that indicate eye rubbing
- **Smart Alerts**: Audio and visual alerts when eye rubbing is detected
- **Configurable Settings**: Customizable detection sensitivity and alert preferences
- **Easy to Use**: Simple setup and operation

## Requirements

- Python 3.8 or higher
- Webcam or IP camera
- See `requirements.txt` for Python package dependencies

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mhdturkoglu/Jedawel.LensSafe.git
cd Jedawel.LensSafe
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application with default settings:
```bash
python baby_monitor.py
```

### With Custom Configuration

Edit `config.json` to customize settings, then run:
```bash
python baby_monitor.py --config config.json
```

### Command Line Options

- `--config`: Path to configuration file (default: config.json)
- `--camera`: Camera source ID (default: 0)
- `--no-display`: Run without showing video feed
- `--debug`: Enable debug mode with additional logging

Example:
```bash
python baby_monitor.py --camera 0 --debug
```

## Configuration

Edit `config.json` to customize the behavior:

- **camera**: Camera settings (source, resolution, FPS)
- **detection**: Detection sensitivity and thresholds
- **alert**: Alert settings (sound, cooldown period)
- **display**: Video display options

## How It Works

1. **Face Detection**: Uses MediaPipe to detect the baby's face in real-time
2. **Hand Tracking**: Tracks hand positions and movements in 3D space
3. **Eye Rubbing Detection**: Analyzes hand proximity and motion near eye region using both 2D distance, depth (Z-coordinate), and motion tracking
   - Checks if hand is close to eye in 2D space (X, Y coordinates)
   - Verifies hand is at approximately the same depth as the eye (Z coordinate) - this ensures the hand is pressing on the eye, not just waving in front
   - **Motion Detection**: Tracks hand movement over multiple frames and only triggers alerts when there's sufficient motion (rubbing), preventing false positives when hand is just resting on face
   - Uses absolute depth difference to prevent false positives when hand is far in front or behind the eye
4. **Alert System**: Triggers audio/visual alerts when eye rubbing is detected
5. **Cooldown Period**: Prevents alert spam with configurable cooldown

## Safety Notes

- This application is a monitoring aid and should not replace direct supervision
- Ensure proper lighting for optimal detection
- Test the system before relying on it
- Keep the camera positioned to have a clear view of the baby

## Technical Details

- **Computer Vision**: OpenCV + MediaPipe
- **Face Detection**: MediaPipe Face Mesh
- **Hand Tracking**: MediaPipe Hands
- **Alert System**: Pygame for audio

## Troubleshooting

**Camera not detected:**
- Check camera permissions
- Try different camera source IDs (0, 1, 2, etc.)

**Poor detection accuracy:**
- Improve lighting conditions
- Adjust detection thresholds in config.json:
  - `eye_rub_threshold`: Controls 2D proximity sensitivity (default: 0.15)
  - `depth_threshold`: Controls Z-depth tolerance - hand must be within this depth range of the eye (default: 0.08)
  - `motion_threshold`: Controls motion sensitivity - hand must move at least this much to trigger detection (default: 0.005)
  - `motion_history_frames`: Number of frames to track for motion calculation (default: 5)
  - `consecutive_frames_threshold`: Number of consecutive frames required for detection (default: 2)
- Ensure camera has clear view of baby

**False positives (detecting rubbing when it's not happening):**
- Increase `eye_rub_threshold` to require hand to be closer to eye in 2D space
- Decrease `depth_threshold` to require hand to be more precisely at the same depth as eye (more strict pressing detection)
- Increase `motion_threshold` to require more hand movement before triggering detection
- Increase `consecutive_frames_threshold` to require more consistent detection

**False negatives (not detecting actual rubbing):**
- Decrease `eye_rub_threshold` to detect from farther 2D distance
- Increase `depth_threshold` to allow detection when hand depth varies slightly from eye depth
- Decrease `motion_threshold` to detect slower rubbing motions
- Decrease `consecutive_frames_threshold` for more sensitive detection

**Alerts not working:**
- Check sound settings and volume
- Verify alert.wav file exists (or disable sound alerts)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Disclaimer

This software is provided as-is for monitoring purposes. It should be used as a supplementary tool and not as a replacement for direct adult supervision of infants and children.
