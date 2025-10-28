# Quick Start Guide - Jedawel LensSafe

## Installation Steps

1. **Install Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Open Terminal/Command Prompt**
   - Windows: Press Win+R, type `cmd`, press Enter
   - Mac: Press Cmd+Space, type `terminal`, press Enter
   - Linux: Press Ctrl+Alt+T

3. **Navigate to project directory**
   ```bash
   cd path/to/Jedawel.LensSafe
   ```

4. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

5. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

6. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

7. **Generate alert sound** (optional)
   ```bash
   python generate_alert_sound.py
   ```

## Running the Application

### Basic Usage
```bash
python baby_monitor.py
```

### With specific camera (if you have multiple cameras)
```bash
python baby_monitor.py --camera 1
```

### Without video display (headless mode)
```bash
python baby_monitor.py --no-display
```

### With debug information
```bash
python baby_monitor.py --debug
```

## Controls

- **Press 'q'** to quit the application
- The application will automatically detect faces and hands
- When eye rubbing is detected, you'll see/hear an alert

## Troubleshooting

### Camera Issues
- If camera doesn't open, try different camera IDs: `--camera 0`, `--camera 1`, etc.
- Check if other applications are using the camera
- On Linux, you may need to add your user to the `video` group

### Permission Issues
- **Windows**: Run as administrator if camera access is denied
- **Mac**: Grant camera permissions in System Preferences → Security & Privacy
- **Linux**: Add user to video group: `sudo usermod -a -G video $USER`

### Installation Issues
- If `pip install` fails, try updating pip: `python -m pip install --upgrade pip`
- For OpenCV issues on Linux: `sudo apt-get install python3-opencv`
- For audio issues: Install system audio libraries

### Poor Detection
- Ensure good lighting conditions
- Position camera to have clear view of baby's face
- Adjust `eye_rub_threshold` in `config.json` (lower = more sensitive)

## Configuration Tips

Edit `config.json` to customize:

- **Camera resolution**: Change `width` and `height` for better quality
- **Detection sensitivity**: Adjust `eye_rub_threshold` (0.1 to 0.2 recommended)
- **Alert cooldown**: Change `alert_cooldown_seconds` to prevent spam
- **Disable sound**: Set `sound_enabled` to `false`

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: 2GB minimum, 4GB recommended
- **Camera**: Any USB/built-in webcam (640x480 or higher)
- **Processor**: Dual-core CPU or better

## Safety Reminders

⚠️ **Important**: This is a monitoring aid, not a replacement for supervision!

- Always supervise children directly
- Test the system before relying on it
- Ensure camera has unobstructed view
- Keep system within hearing distance for alerts

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the main README.md
3. Open an issue on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - Error messages
   - Steps to reproduce

## Next Steps

- Experiment with different camera positions
- Adjust detection settings for your environment
- Consider using an external camera for better angles
- Set up the system in a well-lit area

---

For more detailed information, see the main README.md file.
