from flask import Flask, Blueprint, render_template, request, jsonify, session
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import moviepy.editor as mp
import speech_recognition as sr
from transformers import pipeline
from dotenv import load_dotenv

# Initialize Flask app and Blueprint
app = Flask(__name__)
video_bp = Blueprint('video', __name__)

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model for YouTube summarization
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

youtube_prompt = """You are a YouTube Summarizer. 
You will be taking transcript text and summarizing the entire video, providing an important summary in points within 250 words.
Please provide the summary of the following:"""

# Function to get transcript from YouTube video
def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_data])
        return transcript
    except Exception as e:
        return str(e)

# Function to generate Gemini content
def generate_gemini_content(transcript_text, prompt):
    try:
        response = model.generate_content(prompt + transcript_text)
        if response.text:
            return response.text
        else:
            return "Content generation was blocked. Please try with different content."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to extract audio from video
def extract_audio_from_video(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

# Function to convert audio to text
def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return text

# Function to summarize text
def summarize_text(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Function to process local video
def process_video(video_path):
    audio_path = "extracted_audio.wav"
    extract_audio_from_video(video_path, audio_path)
    text = convert_audio_to_text(audio_path)
    summary = summarize_text(text)
    return summary

@video_bp.route('/summarize', methods=['POST'])
def summarize():
    video_type = request.form.get('type')
    
    if video_type == 'youtube':
        youtube_url = request.form.get('youtube_url')
        if not youtube_url:
            return jsonify({'error': 'No YouTube URL provided'}), 400

        transcript_text = get_transcript(youtube_url)
        if not transcript_text:
            return jsonify({'error': 'Failed to fetch transcript'}), 400

        summary = generate_gemini_content(transcript_text, youtube_prompt)
        return jsonify({'summary': summary, 'transcript': transcript_text})

    elif video_type == 'import':
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        file_path = "uploaded_video.mp4"
        file.save(file_path)
        summary = process_video(file_path)
        return jsonify({'summary': summary})

    else:
        return jsonify({'error': 'Invalid video type'}), 400

@video_bp.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    transcript = data.get('transcript')
    question = data.get('question')

    # Create the prompt for question answering
    prompt = f"Answer the following question based on the provided transcript:\n\nTranscript: {transcript}\n\nQuestion: {question}\nAnswer:"
    print('running..!!')
    print(transcript)
    print(question)
    try:
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})
#def chat():
#    if 'chat_history' not in session:
#        session['chat_history'] = []
#
#    if request.method == 'POST':
#        user_input = request.form['user_input']
#        if user_input:
#            try:
#                # Add user message to chat history
#                session['chat_history'].append({"role": "user", "parts": [{"text": user_input}]})
#
#                # Create the chat object with the correct history format
#                chat = model.start_chat(history=[
#                    {"role": msg["role"], "parts": [{"text": msg["parts"][0]["text"]}]}
#                    for msg in session['chat_history']
#                ])
#
#                # Send the message and get the response
#                response = chat.send_message(user_input)
#
#                # Add model response to chat history
#                session['chat_history'].append({"role": "model", "parts": [{"text": response.text}]})
#
#                return jsonify({"success": True, "response": response.text})
#            except genai.types.generation_types.StopCandidateException:
#                return jsonify({"success": False, "error": "The model stopped generating content. This might be due to content recitation or safety concerns."})
#            except Exception as e:
#                return jsonify({"success": False, "error": f"An error occurred: {str(e)}"})
#        else:
#            return jsonify({"success": False, "error": "Please enter a question."})
#
#    return render_template('chat.html', chat_history=session['chat_history'])


@video_bp.route('/video')
def video():
    return render_template('video.html')

# Register the Blueprint
app.register_blueprint(video_bp)

if __name__ == '__main__':
    app.run(debug=True)
