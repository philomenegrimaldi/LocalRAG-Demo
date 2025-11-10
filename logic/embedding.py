import json
import multiprocessing
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def vectorize_chunks(chunks_json: str, vectorstore_folder: str):
    chunks_json = chunks_json + ".json"

    # 1. Load the chunks
    try:
        with open(chunks_json, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON file: {e}")
        return

    # 2. Build the documents
    docs = []
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()
        if text:
            docs.append(
                Document(
                    page_content=text,
                    metadata={"chunk_id": chunk.get("chunk_id", f"chunk_{i:03d}")},
                )
            )

    # 3. Initialize Ollama embeddings
    try:
        num_threads = max(1, multiprocessing.cpu_count() - 1)
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            num_gpu=1,
            base_url=ollama_base_url,
            num_thread=num_threads,
        )
    except Exception as e:
        print(f"[ERROR] Failed to initialize embeddings: {e}")
        return


    # 4. Vectorize the documents
    try:
        print("[INFO] Vectorization in progress...")
        db = FAISS.from_documents(docs, embeddings)
    except Exception as e:
        print(f"[ERROR] Vectorization failed: {e}")
        return

    # 5. Save FAISS index locally
    try:
        db.save_local(vectorstore_folder)
        print(f"[OK] Vectorization completed successfully. Folder: {vectorstore_folder}")
    except Exception as e:
        print(f"[ERROR] Failed to save FAISS index: {e}")
        return


# Run from terminal
if __name__ == "__main__":
    vectorize_chunks(
        chunks_json="inputs/file-chunked",
        vectorstore_folder="inputs/vectorstore"
    )
