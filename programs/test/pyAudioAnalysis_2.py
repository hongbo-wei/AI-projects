import numpy as np
import pyaudio
import threading  # for synchronization
import whisper
from audio_processing import get_microphone_device_index
from datetime import datetime
from pyAudioAnalysis import audioSegmentation

# Define constants
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

transcription_record = "text/dialogue.txt"

def process_audio_chunk(in_data, frame_count, time_info, status):
    # Your existing audio processing code for Whisper
    global queue
    transcript = ""
    chunk = np.frombuffer(in_data, dtype=np.float32)
    
    with mutex:
        queue = np.append(queue, chunk)
        
    if queue.size >= n_batch_samples:            
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        
        text = model.transcribe(samples)
        transcript = text["text"].strip()
        print(transcript)  # Print the transcribed text

        # record the transcription
        # transcription_record_file.write(f"{transcript}\n")

        update_event.set()  # Set the event to signal an update

    # Perform real-time speaker diarization using pyAudioAnalysis
    speaker = audioSegmentation.speaker_diarization(in_data, RATE)

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the result to the CSV file
    transcription_record_file.write(f"{timestamp},{speaker},{transcript}\n")

    return None, pyaudio.paContinue

# Main function
if __name__ == "__main__":
    audio = pyaudio.PyAudio()
    # Adjust the model according to your requirements
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
        transcription_record_file.close()

    except FileNotFoundError as e:
        print(f"Error: {e}")
