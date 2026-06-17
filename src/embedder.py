from sentence_transformers import SentenceTransformer

class QueryEmbedder:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed(self, content: str) -> list[float]:
        # Convert text → 384-dimensional vector
        content = content.strip()
        if not content:
            raise ValueError("content must be a non-empty string.")
        
        return self.model.encode([content]).tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Embed multiple texts at once — used during ingestion
        return self.model.encode(texts, show_progress_bar=True).tolist()