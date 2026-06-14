import os
import chromadb
from src.schemas import CustomDocument
from sentence_transformers import SentenceTransformer
import uuid


class VectorDatabase:
    def __init__(self, directory: str = "data/vector_store"):

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")#using this model
        self.client = chromadb.PersistentClient(path=directory)

        self.collection = self.client.get_or_create_collection(
            name="mern_codebase",
            metadata={"hnsw:space": "cosine"}#learn more abt cosine similaruty
        )
    
    def insert_document(self,documents: list[CustomDocument]):

        """
        Converts a list of CustomDocuments into vectors and saves them to disk.
        """
        if not documents:
           print("No documents provided!!")
           return
       
        print(f"Preparing to embed and store {len(documents)} code chunks...")

        ids = []
        text = []
        metadata = []

        for doc in documents:
           
           doc_id = str(uuid.uuid4())

           ids.append(doc_id)
           text.append(doc.content)
           metadata.append(doc.metadata)

        embeddings = self.embedding_model.encode(text, show_progress_bar=True).tolist()#convert to list bcz this function returns numpy arary but chromadb dosent take that as input it created a lot of problem so i just converted it to a list

        self.collection.add(
            ids=ids,
            documents=text,
            metadatas=metadata,
            embeddings=embeddings
        )
        print(f"Successfully saved {len(documents)} vectors to ChromaDB.")


