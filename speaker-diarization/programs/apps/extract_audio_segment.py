from pydub import AudioSegment

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
    audio_file = AudioSegment.from_file(input_file)

    # Define start and end time in seconds (multiply by 1000 for milliseconds)
    start_time = start_time * 1000
    end_time = end_time * 1000

    # Extract the segment
    extracted_segment = audio_file[start_time:end_time]

    # Save the segment as a new wav file
    extracted_segment.export(output_file, format="wav")


if __name__ == "__main__":
    # Save the segment as a new wav file
    input_file = 'audio/test_speech_diarization.wav'
    output_file = "audio/SPEAKER_00.wav"

    # Define start and end time in seconds (multiply by 1000 for milliseconds)
    start_time = 1.34
    end_time = 4.62

    extract_audio_segment(input_file, start_time, end_time, output_file)

    start_time = 6.2
    end_time = 7.47
    output_file = "audio/SPEAKER_01.wav"
    extract_audio_segment(input_file, start_time, end_time, output_file)
