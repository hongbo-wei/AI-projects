import whisper

model = whisper.load_model("base")
result = model.transcribe("audio/test_speech_diarization.mp3")
print(result["text"])
print(len(result['text']))