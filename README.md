
# 🚀 LocalRAG Demo

![Python](https://img.shields.io/badge/python-3.10-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-⚡-red)
![LangChain](https://img.shields.io/badge/LangChain-📚-green)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Store-orange)
![Ollama](https://img.shields.io/badge/Ollama-LLM-lightblue)

---

### 🧠 Overview

**LocalRAG Demo** is a fully containerized **Retrieval-Augmented Generation (RAG)** pipeline built with **Streamlit** for document querying and visualization.  
It demonstrates a complete local setup — no external API calls — ideal for **confidential or on-premise applications**.

This project uses:
- 🧾 **Unstructured** for PDF parsing  
- 🧠 **Ollama** for both LLM and embeddings  
- 📦 **FAISS** as the vector store  
- 🐳 **Docker Compose** for orchestration

---

## 🧰 Prerequisites

Make sure you have the following installed before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine on Linux)

---

## ⚙️ Setup (One-Time Only)

Clone the repository:

```bash
git clone https://github.com/philomenegrimaldi/LocalRAG-Demo.git
cd LocalRAG-Demo
```

## Step 1️⃣ — Build the Application

```bash
docker compose build
```

## Step 2️⃣ — Start the Services

```bash
docker compose up -d
```

## Step 3️⃣ — Download the Ollama Models (Important)

You’ll need to pull the required models once:

```bash
# Embedding model
docker exec localrag_ollama ollama pull nomic-embed-text

# LLM model
docker exec localrag_ollama ollama pull mistral:7b
```

🕐 *This may take a few minutes. The models are cached in a Docker volume, so this step is only needed once per machine.*

---

## ▶️ Run the App

Start everything:

# ```bash
# docker compose up -d
# ```

Then open your browser at:

👉 **http://localhost:8501**

---

## 🛑 Stop the App

To stop both containers:

# ```bash
# docker compose down
# ```

---

## 🔄 Update After Code Changes

If you modify Python files or dependencies:

# ```bash
# docker compose down
# docker compose up --build -d
# ```


---

## 💡 About

This project is a simplified, open-source version of a confidential RAG pipeline developed during my AI internship.  
It reproduces the same architecture using public data — a clean, reproducible example of document-based retrieval and local LLM orchestration.

In the original version, I implemented:
- A verification loop to ensure the consistency and reliability of extracted information.  
- An automated output module exporting structured results to a PostgreSQL database.  
- A scalable workflow repeated for around twenty distinct data fields per document, each processed independently through the pipeline.  
- GPU acceleration to speed up embedding generation and model inference.  
- A more powerful 12B LLM model, which improved precision, reduced hallucinations, and produced higher-quality answers on complex technical content.

This demo focuses on the same processing logic, using lightweight models and public data for demonstration purposes.


---

## 🧑‍💻 Author

**Philomène Grimaldi**  
📧 [philomene.grimaldi@iteem.centralelille.fr](mailto:philomene.grimaldi@iteem.centralelille.fr)  
🌐 [LinkedIn](https://www.linkedin.com/in/philomene-grimaldi/)  
💻 [GitHub](https://github.com/philomenegrimaldi)


