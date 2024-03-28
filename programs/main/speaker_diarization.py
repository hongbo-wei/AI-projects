from pyannote.audio import Pipeline
from config import HUGGINGFACE_HUB_TOKEN  # Import from config file
import time
import json


def online_diarization(audio_file, window_duration=1.0, step_duration=0.5):
    """
    This function performs speaker diarization using a sliding window approach.

    Args:
        audio_file (str): a string or Path instance pointing to the audio file
        window_duration (float): the duration of the sliding window in seconds
        step_duration (float): the duration of the step in seconds

    Returns:
        speaker_segments (dic): a dictionary containing speaker segments with timestamps
    """
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HUGGINGFACE_HUB_TOKEN
    )

    # apply pretrained pipeline on your audio file
    diarization = pipeline(audio_file)
    
    speaker_segments = {}
    # Extract speaker segments with timestamps
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        current_time = time.time()
        date = time.strftime("%Y-%m-%d")

        start_timestamp = current_time + turn.start
        end_timestamp = current_time + turn.end
        formatted_start = time.strftime("%H:%M:%S", time.localtime(start_timestamp))
        formatted_end = time.strftime("%H:%M:%S", time.localtime(end_timestamp))
        
        start_seconds = float(str(turn.start)[:4])
        end_seconds = float(str(turn.end)[:4])

        # Use setdefault to create an empty dictionary for the speaker if it doesn't exist
        speaker_dict = speaker_segments.setdefault(speaker, {})
        # Update the dictionary with the segment information
        speaker_dict['date'] = time.strftime("%Y-%m-%d", time.localtime(start_timestamp))
        speaker_dict['start_timestamp'] = formatted_start
        speaker_dict['end_timestamp'] = formatted_end
        speaker_dict['start_seconds'] = start_seconds
        speaker_dict['end_seconds'] = end_seconds

    # Print the speaker_segments dictionary in JSON format
    # print(json.dumps(speaker_segments, indent=4))

    '''
    {
    "SPEAKER_00": {
        "date": "2024-03-28",
        "start_timestamp": "16:46:22",
        "end_timestamp": "16:46:26",
        "start_seconds": "0.78",
        "end_seconds": "4.88"
    },
    '''
    return speaker_segments


if __name__ == "__main__":
    audio_file = "audio/test_speech_diarization.wav"
    speaker_segments = online_diarization(audio_file)
    print(speaker_segments)

    # for speaker, segments in audio_segments.items():
    #     print(f"Speaker: {speaker}")
    #     for i, segment in enumerate(segments):
    #         sf.write(f"{speaker}_segment_{i}.wav", segment, samplerate=44100)
    
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