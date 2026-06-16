import chromadb
from src.schemas import CustomDocument
from src.embedder import QueryEmbedder
import uuid


class VectorDatabase:
    def __init__(self, directory: str = "data/vector_store"):
        self.embedder = QueryEmbedder()#using this model
        self.client = chromadb.PersistentClient(path=directory)

        self.collection = self.client.get_or_create_collection(
            name="mern_codebase",
            metadata={"hnsw:space": "cosine"}#cosine similarity is used for semantic search
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
        texts = []
        metadatas = []

        for doc in documents:
           ids.append(str(uuid.uuid4()))
           texts.append(doc.content)
           metadatas.append(doc.metadata)

        embeddings = embeddings = self.embedder.embed_batch(texts)#convert to list bcz this function returns numpy arary but chromadb dosent take that as input it created a lot of problem so i just converted it to a list

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        print(f"Successfully saved {len(documents)} vectors to ChromaDB.")


