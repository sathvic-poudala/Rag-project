import chromadb
from src.embedder import QueryEmbedder
from src.schemas import RetrivedChunk


class CodeRetriver:

    def __init__(self, directory: str = "data/vector_store"):
        self.embedder = QueryEmbedder
        self.client = chromadb.PersistentClient(path=directory)#connects to chromadb on disk
        self.collection = self.client.get_collection(name="mern_codebase")#Open the collection that was populated during ingestion
    
    def search(self, query: str, number_of_results: int = 5) -> list[RetrivedChunk]:
        """
        Takes a natural-language question, embeds it, and returns
        the top n_results most similar code chunks,uses inbuilt chroma db cosine similarty search
        """
        
        embedded_query = self.embedder.embed(query)

        #serach in chroma db
        raw = self.collection.query(
            query_embeddings=embedded_query ,
            n_results = number_of_results,
            include=["documents", "metadatas", "distances"]
        )

        docs = raw["documents"][0]#multi query possible in chromadb so it returns arrayin array[[]] 
        metas =  raw["metadatas"][0]
        dists = raw["distances"][0]

        result:list[RetrivedChunk] = []
        for i,(docs, metas, dists) in enumerate(zip(docs, metas, dists)):
            result.append(RetrivedChunk(
                content=docs,
                metadata=metas,
                distance=dists,
                rank=i+1,
            ))
        
        return result


    

