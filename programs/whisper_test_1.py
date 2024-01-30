import whisper
import pyaudio
import threading
import numpy as np

# Essential parameters for audio and model
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000  # Whisper's required sample rate
CHUNK = 1024

transcript = ""
mutex = threading.Lock()
queue = np.ndarray([], dtype=np.float32)
n_batch_samples = 5 * RATE
max_queue_size = 3 * n_batch_samples
update_event = threading.Event()  # Event for synchronization

def get_microphone_device_index(device_name, host_api_index=0):
    info = audio.get_host_api_info_by_index(host_api_index)
    num_devices = info.get('deviceCount')

    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(host_api_index, i)
        if device_info['name'] == device_name:
            return i
    return None

def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, transcript
    chunk = np.frombuffer(in_data, dtype=np.float32)
    
    with mutex:
        queue = np.append(queue, chunk)
        
    if queue.size >= n_batch_samples:
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        
        text = model.transcribe(samples)
        transcript = text["text"]
        print(transcript)  # Print the transcribed text
        update_event.set()  # Set the event to signal an update
    
    return None, pyaudio.paContinue

if __name__ == "__main__":
    audio = pyaudio.PyAudio()
    model = whisper.load_model("medium.en")

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
            print("Starting real-time transcription...")
            stream.start_stream()  # Start the audio stream
            while stream.is_active():
                update_event.wait(timeout=0.01)  # Wait for the event to be set or timeout
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("\nTranscription stopped.")
