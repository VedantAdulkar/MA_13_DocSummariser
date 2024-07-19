import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
genai.configure(api_key='AIzaSyDMuxmy8CrJFWwDPD5SDtMsHNx163QFtmg')

# Create the model
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

prompt = """You are a YouTube Summarizer.
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
        return None

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
    

def getYTsum(youtube_url):
    if youtube_url:
        video_id = youtube_url.split("v=")[1]
        #st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        transcript_text = get_transcript(youtube_url)
        filename = "/transcript/output.txt"
        data = transcript_text
        with open(filename, 'w') as file:
            file.write(data)
        summary = generate_gemini_content(transcript_text, prompt)
        return summary
    else:
        return 0