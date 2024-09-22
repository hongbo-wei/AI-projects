'''
This is an AI program focusing on NLP: Speech-to-text and speaker diarization
'''

import whisper
from pydub import AudioSegment
from pyannote.audio import Pipeline
import time
import json
import os
# from dotenv import load_dotenv

def extract_audio_segment(input_file, start_time, end_time, output_file):
    """
    This function extracts a segment from an audio file and saves it as a new wav file.

    args:
        input_file (str): the path to the input audio file
        start_time (float): the start time in seconds
        end_time (float): the end time in seconds
        output_file (str): the path to the output audio file

    returns:
        None 
    """
    # Load the audio file
    audio_file = AudioSegment.from_wav(input_file)

    # Define start and end time in seconds (multiply by 1000 for milliseconds)
    start_time = start_time * 1000
    end_time = end_time * 1000

    # Extract the segment
    extracted_segment = audio_file[start_time:end_time]

    # Save the segment as a new wav file
    extracted_segment.export(output_file, format="wav")


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
    # load_dotenv()
    # HUGGINGFACE_HUB_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
    HUGGINGFACE_HUB_TOKEN = "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"
    
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


def transcribe_audio(audio_file):
    """
    This function transcribes the audio file with speaker-specific segments.

    args:
        audio_file (str): the path to the audio file
    
    returns:
        transcript (str): the transcribed text
    """
    model = whisper.load_model("base.en")
    transcript = model.transcribe(audio_file)
    return transcript["text"].strip()


def output_transcript(speaker_segments,
                      speaker_0='Hongbo',
                      speaker_1='Bruce',
                      speaker_someone='Someone',
                      output_file="text/dialogue.csv"):
    """
    This function writes the speaker-specific segments to a CSV file.

    args:
        speaker_segments (dict): the speaker-specific segments
        output_file (str): the path to the output file

    returns:
        None
    """
    with open(output_file, "a") as dialogue:
        # Extract the speaker-specific segments
        print("Extracting audio segment")
        for speaker, segment in speaker_segments.items():
            start_seconds = segment["start_seconds"]
            end_seconds = segment["end_seconds"]

            # customize speaker role
            # if speaker == "SPEAKER_00":
            #     speaker = speaker_0
            # elif speaker == "SPEAKER_01":
            #     speaker = speaker_1
            # else:
            #     speaker = speaker_someone

            output_audio = f"audio/{speaker}.wav" # extracted segments
            extract_audio_segment(audio_file, start_seconds, end_seconds, output_audio)
            transcript = transcribe_audio(output_audio)

            # Write the speaker, date, start time, end time, and transcript to a CSV file
            date = segment["date"]
            start_timestamp = segment["start_timestamp"]
            end_timestamp = segment["end_timestamp"]
            dialogue.write(f'\n{speaker},{date},{start_timestamp},{end_timestamp},"{transcript}"')
            
        print("Save speaker-specific segments to a CSV file")


if __name__ == "__main__":
    # Start recording
    try:
        print("Speech-to-text and speaker diarization started")
        print("-" * 20)
        audio_file = "audio/test_speech_diarization.wav"
        speaker_segments = speaker_diarization(audio_file)
        output_transcript(speaker_segments)
    except KeyboardInterrupt:
        print("\nSpeech-to-text and speaker diarization stopped")
        break

