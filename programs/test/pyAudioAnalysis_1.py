from pyAudioAnalysis import audioSegmentation

# load audio file and perform speaker diarization
audio_file = "audio/test_speech_diarization.wav"

# Perform speaker diarization
segments = audioSegmentation.speaker_diarization(audio_file, 2)

# # Print speaker segments with start and end times
# for segment in segments:
#     start_time, end_time, label = segment
#     print(f"Speaker {label} speaks from {start_time:.2f} seconds to {end_time:.2f} seconds.")

# Check if segments is indeed a list of lists or tuples
if isinstance(segments[0], list):
    # Extract start_time, end_time, and label
    for segment in segments:
        start_time, end_time, label = segment
        print(f"Speaker {label} speaks from {start_time:.2f} seconds to {end_time:.2f} seconds.")
else:
    # Handle case where segments is not a list of lists:
    # (Modify based on the actual output format)
    for segment in segments:
        # Example for dictionaries:
        print(f"Speaker {segment['label']} speaks from {segment['start_time']:.2f} seconds to {segment['end_time']:.2f} seconds.")

# https://huggingface.co/pyannote/speaker-diarization