import os
from groq import Groq
from src.schemas import RetrivedChunk


# Codebase-aware system prompt — tells the LLM what context it's working with
SYSTEM_PROMPT = """You are an expert code assistant helping a developer understand their MERN stack codebase.

You will be given relevant code chunks retrieved from the codebase as context.
Use ONLY the provided context to answer the question.
If the answer is not in the context, say "I couldn't find relevant code for that in the codebase."

When referencing code, mention the file name and function so the developer knows where to look.
Keep answers clear and practical."""

class Generator:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Make sure it's set in your .env file.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate(
            self, 
            query: str,
            chunks: list[RetrivedChunk], 
            history: list[dict]
    ):
        context_parts = []
        for chunk in chunks:
            file_path = chunk.metadata.get("file_path", "unknown")
            chunk_type = chunk.metadata.get("chunk_type", "unkonwn")
            label = f"[{chunk.rank}] {file_path} ({chunk_type})"
            context_parts.append(f"{label}\n{chunk.content}")

        context_text = "\n\n---\n\n".join(context_parts)# Join all chunks with a separator

        # Build message list: system + history + current question with context
        messages = [{"role": "system", "content":SYSTEM_PROMPT}]

        messages.extend(history)# Add past conversation turns

        augmented_query = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{query}"
        messages.append({"role": "user", "content": augmented_query})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )

        for chunk_delta in stream:
            token = chunk_delta.choices[0].delta.content
            if token:
                yield token
