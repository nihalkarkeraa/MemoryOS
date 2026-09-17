# **MEMORYOS — AI KNOWLEDGE & RESEARCH ASSISTANT**

MemoryOS is an AI-powered knowledge and research assistant designed to help users organize, retrieve, and understand information from their documents.

The project combines **Retrieval-Augmented Generation (RAG)**, semantic search, document processing, and local Large Language Models (LLMs) to provide an intelligent way to interact with personal knowledge.

MemoryOS is being developed with a modular architecture, focusing on building the core document-processing and retrieval pipeline first, followed by advanced AI capabilities.

## **Key Features**

* **PDF Document Ingestion:** Extracts text from PDF documents.
* **Intelligent Chunking:** Splits documents into manageable chunks for efficient retrieval.
* **Semantic Embeddings:** Converts text into vector representations using `all-MiniLM-L6-v2`.
* **Vector Database:** Stores document embeddings using ChromaDB.
* **Semantic Retrieval:** Retrieves relevant document chunks based on the user's query.
* **Local LLM Integration:** Uses Ollama to run language models locally.
* **RAG Pipeline:** Combines retrieved document context with an LLM to generate responses.
* **Document Management:** Includes document-related functionality such as duplicate detection and deletion.

## **System Architecture**

MemoryOS follows a modular architecture that separates document processing, embedding generation, vector storage, retrieval, and response generation.

```text
          User
           |
           v
      Frontend UI
           |
           v
      FastAPI Backend
           |
     +-----+------+
     |            |
     v            v
 Document       User Query
 Ingestion          |
     |              v
     v        Semantic Retrieval
 PDF Extraction     |
     |              v
     v        Relevant Chunks
 Text Chunking      |
     |              |
     v              |
 Embedding Model    |
     |              |
     v              |
   ChromaDB <-------+
     |
     v
 Retrieved Context
     |
     v
 Local LLM (Ollama)
     |
     v
 Generated Response
```

## **Technologies Used**

| Component               | Technology         |
| ----------------------- | ------------------ |
| Backend API             | FastAPI            |
| Programming Language    | Python             |
| PDF Processing          | pypdf              |
| Embedding Model         | all-MiniLM-L6-v2   |
| Vector Database         | ChromaDB           |
| Local LLM Runtime       | Ollama             |
| Language Model          | Phi-3 Mini         |
| Frontend                | Web-based frontend |
| Development Environment | Visual Studio Code |

## **Document Processing & Retrieval**

### Document Ingestion

PDF documents are processed through a pipeline that extracts their text and prepares the content for semantic search.

### Text Chunking

Extracted text is divided into smaller chunks. Each chunk retains document-related metadata to support retrieval and organization.

### Embedding Generation

The `all-MiniLM-L6-v2` model converts text chunks into numerical vector representations.

The generated embeddings have **384 dimensions**.

### Vector Storage

ChromaDB stores the generated embeddings and associated metadata, enabling similarity-based retrieval.

### Semantic Search

When a user submits a query, MemoryOS retrieves relevant document chunks from the vector database to provide context for the response-generation stage.

## **Installation**

### 1. Clone the Repository

```bash
git clone https://github.com/nihalkarkeraa/MemoryOS.git
cd MemoryOS
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages for the backend:

```bash
pip install -r backend/requirements.txt
```

> If the requirements file is not yet present in the repository, install the dependencies listed in the project's setup instructions.

### 4. Install Ollama

Download and install Ollama from:

https://ollama.com/

Pull the Phi-3 Mini model:

```bash
ollama pull phi3:mini
```

Ensure Ollama is running before testing features that require the local language model.

## **Usage**

### Running the Backend

Start the FastAPI backend using the project's backend entry point.

For example, if the application entry point is `main.py`:

```bash
uvicorn main:app --reload
```

Run this command from the directory containing the backend application entry point.

### Using MemoryOS

1. Launch the backend.
2. Open the frontend application.
3. Ingest a supported PDF document.
4. Allow the document to be processed and indexed.
5. Submit a query related to the uploaded document.
6. Review the retrieved information and generated response.

> Exact frontend and backend launch commands depend on the current project configuration.

## **Testing & Validation**

The core document-processing and retrieval pipeline has been tested through individual components.

| Component               | Test Result                             |
| ----------------------- | --------------------------------------- |
| PDF Text Extraction     | Tested                                  |
| Text Chunking           | 124 chunks generated in a test document |
| Embedding Generation    | 384-dimensional embeddings              |
| ChromaDB Initialization | Tested                                  |
| Embedding Storage       | 124 embeddings stored in a test         |
| Semantic Retrieval      | Tested                                  |

These results represent development tests and do not constitute a comprehensive benchmark of answer accuracy or retrieval quality.

## **Project Development Roadmap**

### Core Architecture

* [x] PDF text extraction
* [x] Document chunking
* [x] Embedding generation
* [x] ChromaDB integration
* [x] Semantic retrieval
* [x] Initial local LLM integration
* [ ] Complete frontend-backend integration
* [ ] End-to-end testing

### Advanced Features

* [ ] Enhanced hybrid retrieval
* [ ] Improved document organization
* [ ] Advanced research workflows
* [ ] Knowledge graph integration
* [ ] Agentic AI capabilities
* [ ] Additional knowledge-management features

## **Hardware & Development Environment**

MemoryOS is being developed and tested on a Windows 11 system with:

* Intel Core i3 processor
* 8 GB RAM
* CPU-based model execution
* Local Ollama inference

The project emphasizes a modular design that can be developed on modest hardware, although model inference and document processing performance may vary with system resources.

## **Project Status**

**Status:** In Development

MemoryOS is being built incrementally, beginning with the core document ingestion, embedding, storage, and retrieval architecture. Advanced capabilities will be introduced after the core workflow is integrated and validated.

## **Future Scope**

Potential future extensions include:

* Multi-document research and synthesis
* Knowledge graphs and relationship discovery
* Advanced RAG pipelines
* Agentic research workflows
* Model fine-tuning and optimization
* More comprehensive document-management capabilities

## **Contributing**

Contributions, suggestions, and feedback are welcome.

If you would like to contribute, fork the repository, create a feature branch, and submit a pull request describing your changes.

## **License**

A license has not yet been specified for this repository. Please check the repository for licensing information before using, modifying, or redistributing the project.

## **Author**

**Nihal Karkera**

B.Tech — Artificial Intelligence and Machine Learning

GitHub: https://github.com/nihalkarkeraa

---

*MemoryOS — Turning documents into searchable, usable knowledge.*
