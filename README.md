🚀 LocalRAG Demo

This project is a complete Streamlit application for a RAG (Retrieval-Augmented Generation) pipeline. It uses `unstructured` for PDF processing, `Ollama` for the LLM and embeddings, and `FAISS` for the vector store.

The entire project is containerized using Docker and Docker Compose.

---

## 📋 Prerequisites

Before you begin, ensure you have this one dependency installed:

* **Docker Desktop** (or Docker Engine on Linux).

---

## ⚙️ 1. Initial Setup (One-Time Only)

These steps only need to be done **once** when setting up the project on a new machine.

## Step 1: Build the Application Image

Open a terminal at the project root and run:

```bash
docker compose build
```

What this does:
* Downloads the `python:3.11-slim` base image.
* Installs the required system dependencies (Tesseract, Poppler, libgl1).
* Creates a Python environment and installs all packages from `requirements.txt` (including the CPU-only version of PyTorch).
* Creates your local Docker image: `localrag-demo-app`.

### Step 2: Start the Services

Now, start both containers (`app` and `ollama`) in the background:

```bash
docker compose up -d
```

### Step 3: Download the Ollama Models (Crucial)

The containers are running, but the Ollama service is "empty." You must tell it to download the models.

In the same terminal (or a new one), run these two commands, one after the other:

```bash
# 1. Download the embedding model (nomic-embed-text)
docker exec localrag_ollama ollama pull nomic-embed-text

# 2. Download the LLM (mistral:7b)
docker exec localrag_ollama ollama pull mistral:7b
```

Note: This download may take several minutes. The models are saved to a Docker volume, so you will **never** have to do this step again on this machine.

---

## 🏃‍♂️ 2. Running the Application (Daily Use)

Once the initial setup is complete, starting your application is simple.

```bash
docker compose up -d
```

(If the containers are already running, this command will do nothing, which is normal).

Just open your browser and go to:

**http://localhost:8501**

---

## 🛑 3. Stopping the Application

To stop both containers (`app` and `ollama`):

```bash
docker compose down
```

---

## 🔄 4. How to Update Your Code

If you **modify the Python code** (like `app.py`, a file in `logic/`) or change the `requirements.txt` file:

1.  Make sure the application is stopped (run `docker compose down`).
2.  Re-build the application image with your changes and start it:

    ```bash
     docker compose up --build -d
     ```

(The `-d` is optional; it runs the containers in the background).
