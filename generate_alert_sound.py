#!/usr/bin/env python3
"""
Utility script to generate a simple alert sound file
"""

import numpy as np
import wave
import struct

def generate_alert_sound(filename='alert.wav', duration=1.0, frequency=800):
    """Generate a simple beep sound file"""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Generate a sine wave
    t = np.linspace(0, duration, num_samples)
    
    # Create a beep with fade in/out to avoid clicks
    fade_samples = int(sample_rate * 0.05)  # 50ms fade
    envelope = np.ones(num_samples)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    # Generate tone (combine two frequencies for a more pleasant sound)
    signal = 0.5 * np.sin(2 * np.pi * frequency * t) + 0.3 * np.sin(2 * np.pi * frequency * 1.5 * t)
    signal = signal * envelope
    
    # Normalize
    signal = signal / np.max(np.abs(signal))
    
    # Convert to 16-bit integer
    signal_int = np.int16(signal * 32767)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes (16-bit)
        wav_file.setframerate(sample_rate)
        
        for sample in signal_int:
            wav_file.writeframes(struct.pack('h', sample))
    
    print(f"Alert sound generated: {filename}")

if __name__ == '__main__':
    generate_alert_sound()
    print("Done!")
