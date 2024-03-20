# import libraries
import whisper
from pyannote.audio import Pipeline
import sounddevice as sd

from config import HUGGINGFACE_HUB_TOKEN  # Import from config file

from diart import SpeakerDiarization
from diart.sources import MicrophoneAudioSource
from diart.inference import StreamingInference
from diart.sinks import RTTMWriter

pipeline = SpeakerDiarization()
mic = MicrophoneAudioSource()
inference = StreamingInference(pipeline, mic, do_plot=True)
# inference.attach_observers(RTTMWriter(mic.uri, "/text/output_segmentation.rttm"))

try:
    prediction = inference()  # Attempt to run the inference
except Exception as e:
    print(f"An error occurred: {e}")

# # load whisper model for speech-to-text
# whisper_model = whisper.load_model("base.en")

# # load pyannote model for speaker diarization
# pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.1",
#     use_auth_token=HUGGINGFACE_HUB_TOKEN
# )