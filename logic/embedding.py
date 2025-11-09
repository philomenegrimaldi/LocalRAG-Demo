import json
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import multiprocessing

def vectoriser_chunks(chunks_json: str, dossier_vectorstore: str):
    chunks_json=chunks_json+".json"
    # 1. Charger les chunks
    try:
        with open(chunks_json, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"[ERREUR] Lecture du fichier JSON: {e}")
        return

    # 2. Construire les documents 
    docs = []
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()
        if text:
            docs.append(Document(
                page_content=text,
                metadata={"chunk_id": chunk.get("chunk_id", f"chunk_{i:03d}")}
            ))


    # 3. Initialiser les embeddings Ollama
    try:
        num_threads = max(1, multiprocessing.cpu_count() - 1)
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            num_gpu=1,
            num_thread=num_threads,
        )
    except Exception as e:
        print(f"[ERREUR] Chargement des embeddings: {e}")
        return

    # 4. Vectoriser les documents
    try:
        print("[INFO] Vectorisation en cours...")
        db = FAISS.from_documents(docs, embeddings)
    except Exception as e:
        print(f"[ERREUR] Échec de la vectorisation: {e}")
        return

    # 5. Sauvegarder FAISS
    try:
        db.save_local(dossier_vectorstore)
        print(f"[OK] Vectorisation terminée. Dossier: {dossier_vectorstore}")
    except Exception as e:
        print(f"[ERREUR] Sauvegarde de l'index: {e}")
        return

# Lancer depuis le terminal
if __name__ == "__main__":
    vectoriser_chunks(
        chunks_json="inputs/file-chunked",
        dossier_vectorstore="inputs/vectorstore"
    )
