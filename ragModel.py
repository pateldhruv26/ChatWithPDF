from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

qa_pipeline = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1", tokenizer="mistralai/Mistral-7B-Instruct-v0.1", device=0)

def get_pdf_content(documents):
    raw_text = ""
    for document in documents:
        pdf_reader = PdfReader(document)
        for page in pdf_reader.pages:
            raw_text += page.extract_text() or ""
    return raw_text

def get_chunks(text, chunk_size=1000, overlap=200):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def get_embeddings(chunks):
    embeddings = embedding_model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings, chunks

def get_conversation(text):
    chunks = get_chunks(text)
    index, embeddings, chunk_texts = get_embeddings(chunks)
    return {"index": index, "embeddings": embeddings, "chunks": chunk_texts}

def get_response(conversation, question, top_k=3):
    question_vector = embedding_model.encode([question])
    distances, indices = conversation["index"].search(np.array(question_vector), top_k)
    context = "\n".join([conversation["chunks"][idx] for idx in indices[0]])

    prompt = f"Answer the question based on the context:\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = qa_pipeline(prompt, max_new_tokens=200, do_sample=True)[0]['generated_text']
    
    return response.split("Answer:")[-1].strip()
