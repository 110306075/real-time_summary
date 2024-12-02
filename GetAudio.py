import pyaudio

audio = pyaudio.PyAudio()

print("Available audio devices and their properties:")
for i in range(audio.get_device_count()):
    device_info = audio.get_device_info_by_index(i)
    print(f"\nDevice Index {i}: {device_info['name']}")
    print(f"  Max Input Channels: {device_info['maxInputChannels']}")
    print(f"  Max Output Channels: {device_info['maxOutputChannels']}")
    print(f"  Default Sample Rate: {device_info['defaultSampleRate']}")
    print(f"  Host API: {audio.get_host_api_info_by_index(device_info['hostApi'])['name']}")

audio.terminate()


# import pyaudio

# audio = pyaudio.PyAudio()

# # Get default input device information
# try:
#     default_input_device_info = audio.get_default_input_device_info()
#     default_input_device_index = default_input_device_info['index']
#     default_input_device_name = default_input_device_info['name']
#     print(f"Default input device index: {default_input_device_index}")
#     print(f"Default input device name: {default_input_device_name}")
# except IOError:
#     print("No default input device available")

# # Get default output device information
# try:
#     default_output_device_info = audio.get_default_output_device_info()
#     default_output_device_index = default_output_device_info['index']
#     default_output_device_name = default_output_device_info['name']
#     print(f"Default output device index: {default_output_device_index}")
#     print(f"Default output device name: {default_output_device_name}")
# except IOError:
#     print("No default output device available")

# audio.terminate()

