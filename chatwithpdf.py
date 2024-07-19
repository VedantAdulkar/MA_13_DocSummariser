from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

def pdf_qa_system(user_question, pdf_docs=None, api_key='AIzaSyDMuxmy8CrJFWwDPD5SDtMsHNx163QFtmg'):
    if api_key:
        genai.configure(api_key=api_key)
    else:
        raise ValueError("API key is required")

    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_conversational_chain():
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n
        Answer:
        """
        
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        
        return chain

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # If pdf_docs is provided, process them and create a new FAISS index
    if pdf_docs:
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        vectorstore = FAISS.from_texts(text_chunks, embeddings)
        vectorstore.save_local("faiss_index")
    
    # Load the FAISS index
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    
    chain = get_conversational_chain()
    
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )
    
    return response["output_text"]

# Example usage:
# api_key = "your_api_key_here"
# pdf_docs = ["path/to/your/pdf1.pdf", "path/to/your/pdf2.pdf"]  # Only needed for initial setup
# question = "What is the main topic of the document?"
# answer = pdf_qa_system(question, pdf_docs=pdf_docs)
# print(answer)

# For subsequent queries (after initial setup):
# answer = pdf_qa_system(question, api_key=api_key)
# print(answer)