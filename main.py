import os
from dotenv import load_dotenv
from src.database import VectorDatabase
from  src.chunker import CodebaseParser
from pathlib import Path

load_dotenv()

def main():

    target_directory = r"C:\Users\sathv\Desktop\test"

    parser = CodebaseParser(target_directory)
    documents = parser.load_documents()
    print(f"Total chunks found: {len(documents)}")

    # Show which files were parsed
    from collections import Counter
    files = Counter(doc.metadata.get("file_path") for doc in documents)
    for f, count in files.items():
        print(f"  {count} chunks — {f}")

    #extraction done

    db = VectorDatabase()
    db.insert_document(documents)
    #storage done

if __name__ == "__main__":
    main()
