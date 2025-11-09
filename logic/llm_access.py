from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import json
import os
ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def semantic_search(query: str, vectorstore_folder: str, k: int = 3, debug: bool = False):
    """
    Perform a semantic search over the FAISS vectorstore using Ollama embeddings.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_base_url,)
    db = FAISS.load_local(
        vectorstore_folder,
        embeddings,
        allow_dangerous_deserialization=True
    )
    results = db.similarity_search(query, k=k)

    for i, doc in enumerate(results):
        if debug:
            print(f"[DEBUG] RAG SEM result {i+1} chunk_id={doc.metadata.get('chunk_id', 'unknown')}\n{doc.page_content}")

    return results


def ask_llm(question: str, retrieved_docs):
    """
    Ask an LLM (Ollama) a question based on retrieved documents (RAG).
    """
    llm_model = "mistral:7b"

    # Combine retrieved chunk contents
    raw_context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = f"""
{question}

Give the unique response between brackets: [response] 
Here is the raw data:
{raw_context}
"""

    llm = OllamaLLM(model=llm_model,base_url=ollama_base_url)
    response = llm.invoke(prompt)
    return response


def access_llm(question_llm: str, query_semantic: str, debug: bool = False):
    """
    High-level function to perform semantic search and ask the LLM.
    """
    vectorstore_folder = "inputs/vectorstore"
    retrieved_docs = semantic_search(query_semantic, vectorstore_folder, debug=debug)
    response = ask_llm(question_llm, retrieved_docs)

    if debug:
        print(f"[INFO] LLM question: {question_llm}\n[INFO] LLM response: {response}")

    return response


if __name__ == "__main__":
    question_llm = "What is the Surface Area Consumed (m²) of RC (Resin Coated) Paper?"
    query_semantic = "RC (Resin Coated) Paper"

    answer = access_llm(question_llm, query_semantic)
    print(answer)
