from pyAudioAnalysis import audioSegmentation
import pyaudio
import numpy as np
import threading
import whisper # for real-time transcription


# Configurations
# Essential parameters for audio and model
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000  # Whisper's required sample rate
CHUNK = 1024

mutex = threading.Lock()
queue = np.array([], dtype=np.float32)
n_batch_samples = 5 * RATE
update_event = threading.Event()  # Event for synchronization

# Open files outside the main loop
dialogue = "text/dialogue_output.txt"  # File to record the output with timestamp

# Initialize PyAudioAnalysis parameters
model_type = "knn"  # You can choose the classification model type
n_speakers = 2  # Assuming there are two speakers: doctor and patient

def get_microphone_device_index(device_name, host_api_index=0):
    info = audio.get_host_api_info_by_index(host_api_index)
    num_devices = info.get('deviceCount')

    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(host_api_index, i)
        if device_info['name'] == device_name:
            return i
    return None


# Function to perform speech diarization
def perform_speech_diarization(samples, rate):
    segments = audioSegmentation.speaker_diarization(samples, rate, n_speakers)
    return segments


# Modify the process_audio_chunk function to include speech diarization
def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, start_time, current_speaker
    chunk = np.frombuffer(in_data, dtype=np.float32)
    
    with mutex:
        queue = np.append(queue, chunk)
        
    if queue.size >= n_batch_samples:
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        
        # Perform speech diarization
        segments = perform_speech_diarization(samples, RATE)
        
        # Iterate over speaker segments and transcribe each segment
        for segment in segments:
            start, end, label = segment
            segment_samples = samples[start:end]
            text = model.transcribe(segment_samples)
            transcript = text["text"].strip()
            print(f"{label.capitalize()} says: {transcript}")
            
            # Record the conversation with speaker labels
            if label == 0:  # Assuming doctor is labeled as 0
                doctor_conversation.append(transcript)
            else:
                patient_conversation.append(transcript)
    
    return None, pyaudio.paContinue

# Define doctor and patient conversation lists
doctor_conversation = []
patient_conversation = []

if __name__ == "__main__":
    # Initialize PyAudio and other parameters
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
            # Other code...
            dialogue_file = open(dialogue, 'a')
            stream.start_stream()  # Start the audio stream
            print("Starting real-time speaker diarization...")
            print("Please start speaking...")
            while stream.is_active():
                update_event.wait(timeout=0.01)
                
            # After transcription stopped, save the conversation
            with open("doctor_conversation.txt", "w") as f:
                f.write("\n".join(doctor_conversation))
            with open("patient_conversation.txt", "w") as f:
                f.write("\n".join(patient_conversation))
                
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("\nTranscription stopped.")

            # Close files
            dialogue_file.close()

        except FileNotFoundError as e:
            print(f"Error: {e}")
