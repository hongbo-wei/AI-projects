import pyaudio
import wave
import threading
import time

class AudioRecorder:
    def __init__(self, filename_template, chunk_size=1024, channels=1, sample_rate=44100, record_duration=5):
        self.filename_template = filename_template
        self.chunk_size = chunk_size
        self.channels = channels
        self.sample_rate = sample_rate
        self.record_duration = record_duration
        self.audio_interface = pyaudio.PyAudio()
        self.stream = self.audio_interface.open(format=pyaudio.paInt16,
                                                channels=self.channels,
                                                rate=self.sample_rate,
                                                input=True,
                                                frames_per_buffer=self.chunk_size)
        self.is_recording = False
        self.thread = None

    def _record_segment(self):
        while self.is_recording:
            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * self.record_duration)):
                data = self.stream.read(self.chunk_size)
                frames.append(data)
            self.save_audio(frames)

    def save_audio(self, frames):
        wf = wave.open(self.filename_template.format(int(time.time())), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.thread = threading.Thread(target=self._record_segment)
            self.thread.start()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.thread.join()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()


if __name__ == "__main__":
    # Usage
    filename_template = "audio_segment.wav"
    recorder = AudioRecorder(filename_template)
    recorder.start_recording()
    update_event = threading.Event()  # Event for synchronization


    try:
        while True:
            update_event.wait(timeout=0.01)  # Wait for the event to be set or timeout
            if not update_event.is_set():
                break  # Exit the loop if the event is not set
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping recording.")
        recorder.stop_recording()
        recorder.close()
