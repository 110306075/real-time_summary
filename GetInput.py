import pyaudio
import wave
import numpy as np
from scipy.signal import resample
audio = pyaudio.PyAudio()

stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
frames = []


def downsample_audio(frames, original_rate, target_rate):
    """
    Downsample audio frames from original_rate to target_rate.

    Args:
        frames (list of bytes): Audio frames to be downsampled.
        original_rate (int): The original sampling rate.
        target_rate (int): The desired sampling rate.

    Returns:
        bytes: The downsampled audio frames as a single bytes object.
    """
    # Convert frames (list of bytes) into a numpy array of int16
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

    # Calculate the number of samples for the new rate
    num_samples = int(len(audio_data) * target_rate / original_rate)

    # Resample the audio data
    downsampled_data = resample(audio_data, num_samples).astype(np.int16)

    # Convert back to bytes
    return downsampled_data.tobytes()


print('start recording')
try:
    while True:
        data = stream.read(1024)
        frames.append(data)
except KeyboardInterrupt:
    print('stop recording')

stream.stop_stream()
stream.close()
audio.terminate()

downsampled_frames = downsample_audio(frames, original_rate=44100, target_rate=22050)

sound_file=wave.open("testing_convert_2.wav","wb")
sound_file.setnchannels(1)
sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
sound_file.setframerate(22050)
sound_file.writeframes(downsampled_frames)
sound_file.close()

print('end record and save to .wav file successfully')


        