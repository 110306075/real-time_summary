import pyaudiowpatch as pyaudio
import wave

# Configuration for the recording
FORMAT = pyaudio.paInt16  # 16-bit audio format
CHANNELS = 2              # Stereo
RATE = 48000            # Sampling rate (44.1 kHz)
CHUNK = 1024              # Number of frames per buffer
RECORD_SECONDS = 10       # Duration of the recording
OUTPUT_FILENAME = "output.wav"  # Output file

def record_audio():
    """Record audio from the default speakers using WASAPI loopback."""
    # Initialize PyAudio
    with pyaudio.PyAudio() as p:
        # Get the default WASAPI loopback device
        loopback_device = p.get_default_wasapi_loopback()
        print(loopback_device)

        # Open the audio stream
        with p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=loopback_device['index']) as stream:
            print("Recording...")
            frames = []

            # Record audio in chunks
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            print("Recording finished.")

    # Save the recorded audio to a file
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio recorded and saved as {OUTPUT_FILENAME}")

if __name__ == "__main__":
    record_audio()

