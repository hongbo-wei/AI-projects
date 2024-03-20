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