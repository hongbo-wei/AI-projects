"""
    Other Libs:
    -- no SpeechRecognition cuz it needs internet & lower accuracy than whisper
    -- no wave2vev cuz whisper outperforms
    
    Streamlit Things:
    -- When the code is rerun, the button's state will be reset, causing the code within the if start_button block to execute again.
    -- Updates don't show immediately due to streamlit's default behavior of buffering and batching updates for performance reasons.
"""

import os
import whisper
import pyaudio
import wave
import threading
import ffmpeg
import numpy as np
import subprocess
import streamlit as st


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000            # for my device
RATE_WHIS = 1600        # for whisper
CHUNK = 1024
DEVICE = 17   # Microphone Array (Realtek(R) Audio), default: (1)Microphone Array (Realtek(R) Au

if "start_button_state" not in st.session_state:
    st.session_state.start_button_state = False

if "stop_button_state" not in st.session_state:
    st.session_state.start_button_state = False

st.title("Whisper XxX")
start_button = st.button("Start Recording")
stop_button = st.button("Stop Recording")



audio = pyaudio.PyAudio()
model = whisper.load_model("base")
#aud_file = st.file_uploader("Upload audio", type=["mp3"])
file_name = "test.wav"
recording = False
file_path = ''
frames = []
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE_WHIS, input=True, frames_per_buffer=CHUNK)


# REAL TIME TRANSCRIPTION
sample_rate = 16000
transcript=""
mutex = threading.Lock()
queue = np.ndarray([], dtype=np.float32)
n_batch_samples = 5 * sample_rate                                       # every 5 seconds
max_queue_size = 3 * n_batch_samples                                    # pause queueing if more than 3 batches behind

recorder = pyaudio.PyAudio()                                            # Initialize pyaudio recorder
text_holder = st.empty()

print("here 4\n")

def process_audio_chunk(in_data, frame_count, time_info, status):
    global queue, transcript
    chunk = np.frombuffer(in_data, dtype=np.float32)
    with mutex:
        if queue.size < max_queue_size:
            queue = np.append(queue, chunk)
    if queue.size >= n_batch_samples:
        samples = queue[:n_batch_samples]
        queue = queue[n_batch_samples:]
        text = model.transcribe(samples)
        #transcript += text["text"]
        transcript = text["text"]
        print(transcript)
    return None, pyaudio.paContinue

if start_button and not st.session_state.start_button_state:
    st.markdown("Recording....")
    st.session_state.start_button_state = True

    model = whisper.load_model("base")
                                                                            # Open microphone input stream
    stream = recorder.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, input=True,
                        frames_per_buffer=1024, stream_callback=process_audio_chunk)
    recorder_active = True                                                  # Flag to start/stop receiving audio
    stream.start_stream()


    while recorder_active:                                                  # Start transcription loop
        try:
            st.markdown("Press Ctrl+C to stop the transcription...")
            break
        except KeyboardInterrupt:
            pass

if stop_button and not st.session_state.start_button_state:
    st.markdown("Recording stopped....")
    st.session_state.start_button_state = False
    st.session_state.stop_button_state = True

    recorder_active = False
    stream.stop_stream()
    stream.close()                                                          # Stop & Close the microphone input stream

    recorder.terminate()                                                    # Close the pyaudio recorder
