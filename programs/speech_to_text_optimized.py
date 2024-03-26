import numpy as np
import pyaudio  # for audio input
import soundfile as sf  # For audio file I/O
import time
import threading  # for synchronization
import whisper  # for real-time transcription

from datetime import datetime
from audio_processing import get_microphone_device_index


# configuration
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

# for audio recording
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, start_time, audio_segment_count
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
        transcription_record_file.write(f"{transcript}\n")

        update_event.set()  # Set the event to signal an update
    
    return None, pyaudio.paContinue


def record_audio():
    global queue, recordings_counter
    print(f"Recording audio")
    with sf.SoundFile(WAVE_OUTPUT_FILENAME, mode='x', samplerate=RATE, channels=CHANNELS) as file:
        for _ in range(int(RECORD_SECONDS * RATE / CHUNK)):
            data = queue[:CHUNK]
            queue = queue[CHUNK:]
            file.write(data)
            if len(queue) < CHUNK:
                break


if __name__ == "__main__":
    audio = pyaudio.PyAudio()
    model_size = "base.en" # adjust the model accoding to requets
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
                # time.sleep(0.01)  # Introduce a short delay before acquiring the mutex
                # with mutex:
                #     if transcript:
                #         print(transcript)
                #         transcript = ""  # Clear the transcript after printing

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