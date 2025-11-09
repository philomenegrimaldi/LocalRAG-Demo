from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import json

def recherche_semantique(question_semantique, dossier_vectorstore, k=3, debug: bool = False):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = FAISS.load_local(dossier_vectorstore, embeddings, allow_dangerous_deserialization=True)
    results = db.similarity_search(question_semantique, k=k)
    for i, doc in enumerate(results):
        if debug:
            print(f"[DEBUG] RAG SEM résultat {i+1} chunk_id={doc.metadata.get('chunk_id', 'unknown')}\n{doc.page_content}")
    return results




def poser_question_au_llm(question_llm, rag_sem):
    llm_model="mistral:7b"
    
    # Préparer le contenu brut des chunks
    rag_sem = "\n\n".join([doc.page_content for doc in rag_sem])


    prompt = f"""
            {question_llm}

            Give the unique response between crochet : [response] 
            Here are raw datas :
            {rag_sem}

            """


    llm = OllamaLLM(model=llm_model)
    reponse_llm = llm.invoke(prompt)

    return reponse_llm



def acces_llm(question_llm, question_semantique, debug: bool = False):
    # print(f"Question : Je cherche {question_llm}")
    dossier_vectorstore=f"inputs/vectorstore"
    rag_sem = recherche_semantique(question_semantique, dossier_vectorstore, debug=debug)
    reponse_llm = poser_question_au_llm(question_llm, rag_sem)
    if debug:
        print(f"[INFO] LLM question: {question_llm}\n[INFO] LLM réponse: {reponse_llm}")
    return reponse_llm




if __name__ == "__main__":

    question=f"""What is the Surface Area Consumed (m²) of RC (Resin Coated) Paper  ?
    """
    question_semantique="RC (Resin Coated) Paper"
                            
    rep=acces_llm(question, question_semantique)
    print(rep)






