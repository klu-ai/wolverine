import openai
import pyaudio
import wave
import base64
import requests

# Record 5 seconds of audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "audio.wav"

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Recording...")

frames = []

for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording")

stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

# Convert audio to text using OpenAI Whisper API
with open(WAVE_OUTPUT_FILENAME, "rb") as f:
    audio_data = f.read()

base64_audio = base64.b64encode(audio_data).decode("utf-8")

openai.api_key = "your_openai_api_key"

response = openai.Audio.create(
    audio=base64_audio,
    model="whisper",
    sample_rate=RATE,
    num_channels=CHANNELS,
    format="wav",
)

transcription = response["choices"][0]["text"]

print("Transcription:", transcription)