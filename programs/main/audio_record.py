import sounddevice as sd
import wavio
import time

# Set recording parameters
duration = 10  # seconds
freq = 44100  # sampling rate

# Print available devices (optional)
# print(sd.query_devices())

# Choose the input device (optional, modify index if needed)
# device = sd.query_devices()[0]

def record_audio():
    """
    Reocrd audio from the microphone and save it as a .wav file.

    args:
        None

    returns:
        audio_file (str): the path to the saved audio file
    """

    # Record audio
    # Here number of channels can be 1 or 2 only.
    print("Recording audio...")
    data = sd.rec(int(duration * freq), samplerate=freq, channels=1, blocking=True)

    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
    audio_file = f"audio/recording_{timestamp}.wav"
    # Save as WAV file
    wavio.write(audio_file, data, freq, sampwidth=2)
    
    print("Audio recorded")
    return audio_file

if __name__ == "__main__":
    # Start recording
    while True:
        try:
            audio_file = record_audio()
        except KeyboardInterrupt:
            print("\nSpeech-to-text and speaker diarization stopped")
            break
