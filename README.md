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
3. **Eye Rubbing Detection**: Analyzes hand proximity to eye region using both 2D distance and depth (Z-coordinate) to accurately detect rubbing gestures
   - Checks if hand is close to eye in 2D space (X, Y coordinates)
   - Verifies hand is in front of or at the same depth as the eye (Z coordinate)
   - Prevents false positives when hand is behind the eye
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
  - `depth_threshold`: Controls Z-depth tolerance (default: 0.05)
- Ensure camera has clear view of baby

**False positives (detecting rubbing when it's not happening):**
- Increase `eye_rub_threshold` to require hand to be closer to eye
- Decrease `depth_threshold` to require hand to be more clearly in front of eye
- Increase `consecutive_frames_threshold` to require more consistent detection

**False negatives (not detecting actual rubbing):**
- Decrease `eye_rub_threshold` to detect from farther distance
- Increase `depth_threshold` to allow detection when hand is slightly behind
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
