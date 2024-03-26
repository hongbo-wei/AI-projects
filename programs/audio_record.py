import sounddevice as sd
import wavio

# Set recording parameters
duration = 5  # seconds
fs = 44100  # sampling rate

# Print available devices (optional)
print(sd.query_devices())

# Choose the input device (optional, modify index if needed)
device = sd.query_devices()[0]

def record_audio():
    # Record audio
    # Here number of channels can be 1 or 2 only.
    data = sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)

  
  # Save as WAV file
    wavio.write("audio/recording.wav", data, fs, sampwidth=2)
    print("Recording saved as recording.wav")

# Start recording
record_audio()