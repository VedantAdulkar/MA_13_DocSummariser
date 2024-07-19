import moviepy.editor as mp
import speech_recognition as sr
from transformers import pipeline

def extract_audio_from_video(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return text

def summarize_text(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def process_video(video_path):
    # Step 1: Extract audio from video
    audio_path = "extracted_audio.wav"
    extract_audio_from_video(video_path, audio_path)

    # Step 2: Convert audio to text
    text = convert_audio_to_text(audio_path)
    filename = "/transcript/output.txt"
    data = text
    with open(filename, 'w') as file:
        file.write(data)

    # Step 3: Summarize the text
    summary = summarize_text(text)

    return summary