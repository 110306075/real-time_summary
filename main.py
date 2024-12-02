import threading
import queue
import time
import wave
import pyaudio
import whisper
import struct
from concurrent.futures import ThreadPoolExecutor

# Initialize PyAudio and Whisper model
audio = pyaudio.PyAudio()

model = whisper.load_model("medium")
print('model loaded')
time.sleep(10)
print('model ready')


# Replace these with your actual device indices
MICROPHONE_DEVICE_INDEX = 0
SYSTEM_AUDIO_DEVICE_INDEX = 1

# Function to capture input (microphone)
def capture_input(input_stream, frames_per_buffer, input_queue, stop_event):
    while not stop_event.is_set():
        data = input_stream.read(frames_per_buffer, exception_on_overflow=False)
        input_queue.put(data)

# Function to capture system audio output
def capture_output(output_stream, frames_per_buffer, output_queue, stop_event):
    while not stop_event.is_set():
        data = output_stream.read(frames_per_buffer, exception_on_overflow=False)
        output_queue.put(data)

# Function to interleave audio data
def interleave_audio(input_data, output_data):
    interleaved_data = bytearray()
    input_samples = struct.unpack(f"{len(input_data) // 2}h", input_data)
    output_samples = struct.unpack(f"{len(output_data) // 2}h", output_data)
    min_length = min(len(input_samples), len(output_samples))
    for i in range(min_length):
        interleaved_data.extend(struct.pack("h", input_samples[i]))
        interleaved_data.extend(struct.pack("h", output_samples[i]))
    return interleaved_data

# Function to transcribe audio in a separate thread
def transcribe_audio(filename):
    print(f"Transcribing {filename}...")
    result = model.transcribe(filename, fp16=False)
    print(f"Transcription of {filename}: {result['text']}")

# Function to save and transcribe remaining audio
def save_and_transcribe_remaining_audio(combined_frames, file_index, format, rate, audio):
    if combined_frames:
        filename = f"interleaved_audio_{file_index}_final.wav"
        with wave.open(filename, "wb") as sound_file:
            sound_file.setnchannels(2)
            sound_file.setsampwidth(audio.get_sample_size(format))
            sound_file.setframerate(rate)
            sound_file.writeframes(b"".join(combined_frames))
        # print(f"Saved final audio to {filename}")
        # Submit the transcription task to the executor
        transcription_executor.submit(transcribe_audio, filename)
    else:
        print("No remaining audio data to save.")

# Function to record, save, and transcribe audio
def record_and_save_audio(output_filename_prefix="interleaved_audio", format=pyaudio.paInt16, input_channels=1, output_channels=1, rate=44100, frames_per_buffer=1024, save_interval=20):
    input_queue = queue.Queue()
    output_queue = queue.Queue()

    # Open the microphone input stream
    input_stream = audio.open(format=format, channels=input_channels, rate=rate, input=True,
                              frames_per_buffer=frames_per_buffer)
    
    # Open the system audio output capture stream
    output_stream = audio.open(format=format, channels=output_channels, rate=rate, input=True,
                               frames_per_buffer=frames_per_buffer)

    stop_event = threading.Event()
    input_thread = threading.Thread(target=capture_input, args=(input_stream, frames_per_buffer, input_queue, stop_event))
    output_thread = threading.Thread(target=capture_output, args=(output_stream, frames_per_buffer, output_queue, stop_event))
    
    input_thread.start()
    output_thread.start()

    combined_frames = []
    start_time = time.time()
    file_index = 0

    # Create a ThreadPoolExecutor for transcription tasks
    global transcription_executor
    transcription_executor = ThreadPoolExecutor(max_workers=1)

    try:
        while True:
            current_time = time.time()
            if current_time - start_time >= save_interval:
                filename = f"{output_filename_prefix}_{file_index}.wav"
                with wave.open(filename, "wb") as sound_file:
                    sound_file.setnchannels(2)
                    sound_file.setsampwidth(audio.get_sample_size(format))
                    sound_file.setframerate(rate)
                    sound_file.writeframes(b"".join(combined_frames))
                # print(f"Saved audio to {filename}")
                # Submit the transcription task to the executor
                transcription_executor.submit(transcribe_audio, filename)
                combined_frames.clear()
                start_time = current_time
                file_index += 1

            if not input_queue.empty() and not output_queue.empty():
                input_data = input_queue.get()
                output_data = output_queue.get()
                interleaved_data = interleave_audio(input_data, output_data)
                combined_frames.append(interleaved_data)

    except KeyboardInterrupt:
        print("Stopping recording...")
        # Save and transcribe the remaining audio
        save_and_transcribe_remaining_audio(combined_frames, file_index, format, rate, audio)
    finally:
        stop_event.set()
        input_thread.join()
        output_thread.join()
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        audio.terminate()
        transcription_executor.shutdown(wait=True)
        print("Recording and transcription complete.")

# Start recording, saving, and transcribing audio
record_and_save_audio()
