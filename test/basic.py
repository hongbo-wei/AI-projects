import whisper

model = whisper.load_model("base")
result = model.transcribe("test/Nikki.mp3")
print(result["text"])