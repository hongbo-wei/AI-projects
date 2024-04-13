from pyannote.audio import Pipeline
from config import HUGGINGFACE_HUB_TOKEN  # Import from config file
import time
import json


def speaker_diarization(audio_file,
                        speaker_0='Hongbo',
                        speaker_1='Bruce',
                        speaker_someone='Someone',
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
        # customize speaker role
        # if speaker == "SPEAKER_00":
        #     speaker = speaker_0
        # elif speaker == "SPEAKER_01":
        #     speaker = speaker_1
        # else:
        #     speaker = speaker_someone

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
    audio_file = "audio/audio_record.wav"
    speaker_segments = speaker_diarization(audio_file)
    for speaker_segment in speaker_segments:
        print(speaker_segment, speaker_segments[speaker_segment])
