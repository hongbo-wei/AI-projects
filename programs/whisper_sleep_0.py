import whisper
import pyaudio
import threading
import numpy as np
import time

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

start_time = None
latency_record = "text/latency_record.txt"

def get_microphone_device_name():
    devices = []
    for i in range(audio.get_device_count()):
        devices.append(audio.get_device_info_by_index(i))
    return devices

def get_microphone_device_index(device_name):
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(0, i)
        if device_info['name'] == device_name:
            return i
    return None

def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, transcript, start_time
    chunk = np.frombuffer(in_data, dtype=np.float32)
    with mutex:
        if queue.size < max_queue_size:
            queue = np.append(queue, chunk)
    if queue.size >= n_batch_samples:
        if start_time is None:
            start_time = time.time()  # Record the start time
            
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        
        text = model.transcribe(samples)
        transcript = text["text"]

        # Calculate the latency
        end_time = time.time()
        latency = end_time - start_time
        latency_record_file.write(f"{latency:.2f}" + "\n")
        start_time = None  # Reset the start time
    return None, pyaudio.paContinue

if __name__ == "__main__":
    audio = pyaudio.PyAudio()
    model = whisper.load_model("base.en")

    # Find the microphone device index
    microphone_devices = get_microphone_device_name()
    microphone_name = microphone_devices[0]['name'] # normally the default output device is at index 0
    mic_device_index = get_microphone_device_index(microphone_name)
    if mic_device_index is not None:
        print(f"Found microphone at device index {mic_device_index}, namely {microphone_name}")
        # sample_rate = int(audio.get_device_info_by_index(mic_device_index)['defaultSampleRate'])

        # Open the audio stream, start the stream, and keep the program running
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            input_device_index=mic_device_index,
                            stream_callback=process_audio_chunk)
        try:
            stream.start_stream()  # Start the audio stream
            print("Starting real-time transcription...")
            latency_record_file = open(latency_record,'a')

            while True:
                time.sleep(0.01)  # Introduce a short delay before acquiring the mutex
                with mutex:
                    if transcript:
                        print(transcript)
                        transcript = ""  # Clear the transcript after printing
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            latency_record_file.close()
            print("\nTranscription stopped.")

'''
Hello, this is Bruce. I'm testing our speech-to-text program. Let's see how well the Whisper by OpenAI can automatically generate the corresponding transcription. 
Firstly, we record the latency time between capturing audio and displaying the transcribed text. Secondly, we compare the input text with the transcription to see the word error rate.
Testing completed.
'''