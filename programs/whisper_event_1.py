import whisper # for real-time transcription
import pyaudio # for audio input
import threading # for synchronization
import numpy as np
import time
from datetime import datetime

# Essential parameters for audio and model
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000  # Whisper's required sample rate
CHUNK = 1024

mutex = threading.Lock()
queue = np.ndarray([], dtype=np.float32)
n_batch_samples = 5 * RATE
max_queue_size = 3 * n_batch_samples
start_time = None
update_event = threading.Event()  # Event for synchronization

latency_record = "text/latency_record.txt"
transcription_record = "text/transcription_record.txt"

def get_microphone_device_index(device_name, host_api_index=0):
    info = audio.get_host_api_info_by_index(host_api_index)
    num_devices = info.get('deviceCount')

    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(host_api_index, i)
        if device_info['name'] == device_name:
            return i
    return None

def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, start_time
    transcript = ""
    chunk = np.frombuffer(in_data, dtype=np.float32)
    
    with mutex:
        queue = np.append(queue, chunk)
        
    if queue.size >= n_batch_samples:
        if start_time is None:
            start_time = time.time()  # Record the start time
            
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        
        text = model.transcribe(samples)
        transcript = text["text"].strip()
        print(transcript)  # Print the transcribed text

        # Calculate the latency
        end_time = time.time()
        latency = end_time - start_time
        latency_record_file.write(f"{latency:.2f}\n")

        # record the transcription
        transcription_record_file.write(f"{transcript}\n")

        start_time = None  # Reset the start time
        update_event.set()  # Set the event to signal an update
    
    return None, pyaudio.paContinue

if __name__ == "__main__":
    audio = pyaudio.PyAudio()
    # adjust the model accoding to requets
    model_size = "base.en"
    model = whisper.load_model(model_size)

    # Find the microphone device index
    microphone_name = audio.get_default_input_device_info()['name']
    mic_device_index = get_microphone_device_index(microphone_name)
    
    if mic_device_index is not None:
        print(f"Found microphone at device index {mic_device_index}, namely {microphone_name}")
        # Open the audio stream, start the stream, and keep the program running
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            input_device_index=mic_device_index,
                            stream_callback=process_audio_chunk)
        
        try:
            latency_record_file = open(latency_record, 'a')
            transcription_record_file = open(transcription_record, 'a')

            stream.start_stream()  # Start the audio stream
            print("Starting real-time speaker diarization...")
            print("Please start speaking...")

            while stream.is_active():
                update_event.wait(timeout=0.01)  # Wait for the event to be set or timeout
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("\nTranscription stopped.")

            # Close files
            latency_record_file.close()
            transcription_record_file.close()

        except FileNotFoundError as e:
            print(f"Error: {e}")

'''
Hello, this is Bruce.
I'm testing our speech to text program.
Let's see how well the Whisper can automatically generate the transcription. 
Firstly, we record the latency time between capturing audio and displaying transcription.
Secondly, we compare the input text with the transcription to see the word error rate.
Testing completed.
'''