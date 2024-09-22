from pyannote.audio import Pipeline
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()
HUGGINGFACE_HUB_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")

def speaker_diarization(audio_file,
                        window_duration=1.0,
                        step_duration=0.5):
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
    # In case the number of speakers is known in advance, one can use the num_speakers option:
    diarization = pipeline(audio_file)
    
    speaker_segments = []
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

        speaker_dict = {speaker: {
            "date": date,
            "start_timestamp": formatted_start,
            "end_timestamp": formatted_end,
            "start_seconds": start_seconds,
            "end_seconds": end_seconds
        }}
        speaker_segments.append(speaker_dict)
        # Update the dictionary with the segment information

    # Print the speaker_segments dictionary in JSON format
    # print(json.dumps(speaker_segments, indent=4))

    '''
    [{"SPEAKER_00": {
        "date": "2024-03-28",
        "start_timestamp": "16:46:22",
        "end_timestamp": "16:46:26",
        "start_seconds": "0.78",
        "end_seconds": "4.88"
        }
    }]
    '''
    return speaker_segments


if __name__ == "__main__":
    audio_file = "audio/audio_record.wav"
    speaker_segments = speaker_diarization(audio_file)
    for speaker_segment in speaker_segments:
        print(speaker_segment, speaker_segments[speaker_segment])
