from flask import Blueprint, render_template, request, jsonify
from PIL import Image
import pytesseract
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Initialize Blueprint
imgtotext_bp = Blueprint('imgtotext', __name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_image_text(image_files):
    text = ""
    for image in image_files:
        img = Image.open(image)
        text += pytesseract.image_to_string(img)
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Log the number of text chunks
    logger.info(f"Number of text chunks: {len(text_chunks)}")
    
    try:
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
    except Exception as e:
        logger.error(f"Error generating vector store: {e}")
        raise

def get_conversational_chain():
    prompt_template = """
    Please provide a detailed answer of at least 500 words based on the provided context. Ensure you include all relevant details. 
    If the answer is not available in the provided context, respond with "answer is not available in the context" and do not provide a speculative answer.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return response["output_text"]

@imgtotext_bp.route('/process_image', methods=['POST'])
def process_image():
    files = request.files.getlist('image_files')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    raw_text = get_image_text(files)
    if not raw_text:
        return jsonify({'error': 'No text found in the images'}), 400

    text_chunks = get_text_chunks(raw_text)
    if not text_chunks:
        return jsonify({'error': 'No text chunks created from the images'}), 400

    get_vector_store(text_chunks)
    return jsonify({'message': 'Text extracted and processed successfully'})

@imgtotext_bp.route('/ask_question', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    answer = user_input(question)
    return jsonify({'answer': answer})

@imgtotext_bp.route('/imgtotext')
def imgtotext():
    return render_template('imagetotext.html')
        