import chromadb
import uuid
from sentence_transformers import SentenceTransformer


client = chromadb.PersistentClient(path="./my_local_db")
collection = client.get_or_create_collection(name="documentforllm")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", device="cpu")

# 1. require a 'question' string to be passed into the function
def query_database(question: str):
    
    # 2. encoding the dynamic question
    query_embedding = model.encode([question]).tolist()
    
    # 3. searching the database
    result = collection.query(
        query_embeddings=query_embedding,
        n_results=4
    )
    
    # 4. safely extracting the text from the dictionary and returning it as a string
    retrieved_text = result.get('documents', [[]])[0]
    return "\n\n".join(retrieved_text)

def add_documents_to_db(chunks: list):
    """
    Takes a list of text chunks, embeds them, and saves them 
    into the existing ChromaDB collection with unique IDs.
    """
    # Tell Python we want to modify the global collection variable at the top
    global collection 
    
    # 1. FRESH START: Wipe out the old collection entirely so contexts don't mix!
    try:
        client.delete_collection(name="documentforllm")
    except Exception:
        pass # If it doesn't exist yet, just skip
        
    # 2. Re-create a clean, empty collection with the same name
    collection = client.get_or_create_collection(name="documentforllm")
    
    # 3. Generate embeddings and save the new chunks normally
    embeddings = model.encode(chunks).tolist()
    unique_ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=unique_ids
    )