import pyaudio
import wave

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 5
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

#Select Device
print ( "Available devices:\n")
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print ( str(info["index"]) +  ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))
    pass

#ToDo change to your device ID
device_id = 1
device_info = p.get_device_info_by_index(device_id)
channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
# https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.__init__
stream = p.open(format=sample_format,
                channels=channels,
                rate=int(device_info["defaultSampleRate"]),
                input=True,
                frames_per_buffer=chunk,
                input_device_index=device_info["index"],
                as_loopback=True
                )

frames = []  # Initialize array to store frames

print('\nRecording', device_id, '...\n')

# Store data in chunks for 3 seconds
for i in range(0, int(fs / chunk * seconds)):
    data = stream.read(chunk)
    frames.append(data)

# Stop and close the stream 
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

print('Finished recording')

# Save the recorded data as a WAV file
wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()