import os
from dotenv import load_dotenv
from src.database import VectorDatabase
from  src.parser import CodebaseParser

load_dotenv()

def main():
    target_directory = r"C:\Users\sathv\Desktop\test"

    parser = CodebaseParser(target_directory)
    documents = parser.load_documents()

    if not documents:
        print("Pipeline Halted: No .js files found to process.")
        return
    #extraction done

    db = VectorDatabase()
    db.insert_document(documents)
    #storage done

if __name__ == "__main__":
    main()
