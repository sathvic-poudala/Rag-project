import os
from dotenv import load_dotenv
from src.generator import Generator
from src.embedder import QueryEmbedder
from src.retriever import CodeRetriver

load_dotenv()

HELP_TEXT = """
Commands:
  /clear   — clear conversation history
  /help    — show this message
  /quit    — exit
"""

def run():
    embedder = QueryEmbedder()
    retriever = CodeRetriver()
    generator = Generator()

    history = [] # stores past (user, assistant) turns

    print("MERN Codebase Assistant — type your question or /help")

    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not raw:
            print("Goodbye.")
            break

        elif raw.startswith("/clear"):
            history = []
            print("Conversation history cleared.")
            continue
        
        elif raw.startswith("\help"):
            print(HELP_TEXT)
            continue

        try:
            chunks = retriever.search(raw, number_of_results=5)

            if not chunks:
                print("No relevant code found. Try rephrasing your question.")
                continue

            print("\nAnswer:\n")
            full_answer = ""

            for token in generator.generate(query=raw, chunks=chunks, history=history):
                print(token, end="", flush=True)
                full_answer += token
            
            print("\n\nSources:")
            for chunk in chunks:
                file_path = chunk.metadata.get("file_path","unkonwn")
                chunk_type = chunk.metadata.get("chunk_type", "unknown")
                print(f"  [{chunk.rank}] {file_path} — {chunk_type}")

            # Add this to history
            history.append({"role": "user", "content": raw})
            history.append({"role": "assistant", "content": full_answer})

            # Cap history at 10 turns (20 messages)
            if len(history) > 20:
                history = history[-20:]
            
        except ValueError as e:
            print(f"input error: {e}")
        except Exception as e:
            print(f"error: {e}")

if __name__ == "__main__":
    run()