from pyannote.audio import Pipeline
from config import HUGGINGFACE_HUB_TOKEN  # Import from config file
import datetime


def online_diarization(audio_file, window_duration=1.0, step_duration=0.5):
    """
    This function performs online speaker diarization using a sliding window approach.
    """
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HUGGINGFACE_HUB_TOKEN
    )

    # apply pretrained pipeline

    diarization = pipeline(audio_file)

    # dump the diarization output to disk using CSV format
    with open("text/dialogue.txt", "a") as dialogue:

        # print the result
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=turn.start)
            end_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=turn.end)
            
            date = start_timestamp.strftime("%Y-%m-%d")
            formatted_start = start_timestamp.strftime("%H:%M:%S")
            formatted_end = end_timestamp.strftime("%H:%M:%S")

            record = f"\n{speaker},{date},{formatted_start},{formatted_end}"
            dialogue.write(record)
            
            print(date)
            print(f"start={formatted_start} stop={formatted_end} speaker={speaker}")
            print("-" * 20)  # Optional: Add a separator line between entries


if __name__ == "__main__":
    audio_file = "audio/test_speech_diarization.wav"
    online_diarization(audio_file)
    
    # pass the byte string of the audio file to the function
    # audio_str = []
    # with open(audio_file, "rb") as f:
    #     for line in f:
    #         audio_str.append(line)
    #         # Byte string
    # online_diarization(audio_str[0])

    # byte_string = b'\x00\x0b\x00\x0b\x00\r\x00\x0e\x00\x0e\x00\x0e\x00\x0e\x00\x0e\x00\x0f\x00\x0f\x00\x10\x00\x11\x00\x12\x00\x13\x00\x13\x00\x13\x00\x13\x00\x13\x00\x14\x00\x15\x00\x15\x00\x15\x00\x15\x00\x15\x00\x15\x00\x14\x00\x14\x00\x14\x00\x15\x00\x17\x00\x18\x00\x19\x00\x19\x00\x18\x00\x17\x00\x17\x00\x17\x00\x17\x00\x17\x00\x18\x00\x19\x00\x1a\x00\x1a\x00\x19\x00\x19\x00\x1a'
    
    # online_diarization(byte_string)

    # raise ValueError(AudioFileDocString)
    # ValueError: 
    # Audio files can be provided to the Audio class using different types:
    #     - a "str" or "Path" instance: "audio.wav" or Path("audio.wav")
    #     - a "IOBase" instance with "read" and "seek" support: open("audio.wav", "rb")
    #     - a "Mapping" with any of the above as "audio" key: {"audio": ...}
    #     - a "Mapping" with both "waveform" and "sample_rate" key:
    #         {"waveform": (channel, time) numpy.ndarray or torch.Tensor, "sample_rate": 44100}

    # For last two options, an additional "channel" key can be provided as a zero-indexed
    # integer to load a specific channel: {"audio": "stereo.wav", "channel": 0}