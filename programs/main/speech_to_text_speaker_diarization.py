from audio_record import record_audio
from extract_audio_segment import extract_audio_segment
from speaker_diarization import speaker_diarization
import whisper


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

def output_transcript(speaker_segments, output_file="text/dialogue.csv"):
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
            output_audio = f"audio/extracted_segment_{speaker}.wav"
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
    while True:
        try:
            print("-" * 20)
            audio_file = record_audio()
            # audio_file = "audio/test_speech_diarization.wav"
            speaker_segments = speaker_diarization(audio_file)
            output_transcript(speaker_segments)
        except KeyboardInterrupt:
            print("\nSpeech-to-text and speaker diarization stopped")
            break

# Hi, this is Bruce, I'm testing my program
# Hi Bruce, this is Arnaz, I'm testing my program too