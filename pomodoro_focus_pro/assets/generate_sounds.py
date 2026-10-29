import math
import struct
import wave
import os

def generate_chimes():
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. Focus Completed Chime: Upbeat crystal double bell (G5 -> C6)
    focus_file = os.path.join(assets_dir, "focus_complete.wav")
    num_samples = int(2.0 * 44100)
    with wave.open(focus_file, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        frames = bytearray()
        for i in range(num_samples):
            t = i / 44100.0
            # Bell 1: G5 (783.99 Hz)
            env1 = math.exp(-3.8 * t)
            tone1 = 0.5 * math.sin(2 * math.pi * 783.99 * t) + 0.15 * math.sin(2 * math.pi * 1567.98 * t)
            
            # Bell 2: C6 (1046.50 Hz) starts at 0.22s
            tone2 = 0.0
            if t > 0.22:
                t2 = t - 0.22
                env2 = math.exp(-3.2 * t2)
                tone2 = 0.65 * math.sin(2 * math.pi * 1046.50 * t2) + 0.2 * math.sin(2 * math.pi * 2093.0 * t2)
            
            # Bell 3: E6 (1318.51 Hz) starts at 0.44s
            tone3 = 0.0
            if t > 0.44:
                t3 = t - 0.44
                env3 = math.exp(-2.8 * t3)
                tone3 = 0.5 * math.sin(2 * math.pi * 1318.51 * t3)
                
            sample = (tone1 * env1 + tone2 + tone3) * 0.7
            sample = max(-1.0, min(1.0, sample))
            val = int(sample * 32767.0)
            frames.extend(struct.pack('<hh', val, val))
        wav.writeframes(frames)
    print("Created:", focus_file)
    
    # 2. Break Completed Chime: Soft gong/marimba (C5 -> E5 -> G5)
    break_file = os.path.join(assets_dir, "break_complete.wav")
    with wave.open(break_file, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        frames = bytearray()
        for i in range(num_samples):
            t = i / 44100.0
            env1 = math.exp(-3.5 * t)
            tone1 = 0.5 * math.sin(2 * math.pi * 523.25 * t) + 0.1 * math.sin(2 * math.pi * 1046.5 * t)
            
            tone2 = 0.0
            if t > 0.20:
                t2 = t - 0.20
                env2 = math.exp(-3.2 * t2)
                tone2 = 0.5 * math.sin(2 * math.pi * 659.25 * t2)
                
            tone3 = 0.0
            if t > 0.40:
                t3 = t - 0.40
                env3 = math.exp(-3.0 * t3)
                tone3 = 0.6 * math.sin(2 * math.pi * 783.99 * t3)
                
            sample = (tone1 * env1 + tone2 + tone3) * 0.7
            sample = max(-1.0, min(1.0, sample))
            val = int(sample * 32767.0)
            frames.extend(struct.pack('<hh', val, val))
        wav.writeframes(frames)
    print("Created:", break_file)

if __name__ == "__main__":
    generate_chimes()
