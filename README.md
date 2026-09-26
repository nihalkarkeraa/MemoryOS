Yes — you want **exactly this clean Markdown format**, just updated with the current MemoryOS functionality. Copy this entire block directly into `README.md`:

````markdown
# **MEMORYOS — AI KNOWLEDGE & RESEARCH ASSISTANT**

MemoryOS is an AI-powered knowledge and research assistant designed to help users organize, retrieve, compare, summarize, and understand information from their documents.

The project combines **Retrieval-Augmented Generation (RAG)**, semantic search, hybrid retrieval, document processing, cross-encoder reranking, local Large Language Models (LLMs), and knowledge graph technology to provide an intelligent way to interact with personal knowledge.

MemoryOS follows a modular architecture consisting of a React frontend, FastAPI backend, document-processing pipeline, vector database, local LLM inference, and knowledge graph layer.

## **Key Features**

* **PDF Document Ingestion:** Extracts text from PDF documents.
* **Intelligent Chunking:** Splits documents into manageable chunks for efficient retrieval.
* **Semantic Embeddings:** Converts text into vector representations using `all-MiniLM-L6-v2`.
* **Vector Database:** Stores document embeddings using ChromaDB.
* **Semantic Retrieval:** Retrieves relevant document chunks based on the user's query.
* **Hybrid Retrieval:** Combines retrieval approaches to improve relevant context selection.
* **Cross-Encoder Reranking:** Reranks retrieved results based on query relevance.
* **Local LLM Integration:** Uses Ollama to run language models locally.
* **RAG Pipeline:** Combines retrieved document context with an LLM to generate document-grounded responses.
* **Source & Citation Handling:** Provides document, page, and chunk references for retrieved information.
* **Document Management:** Supports document upload, duplicate detection, metadata handling, processing status, and deletion.
* **Document Summarization:** Generates AI-powered summaries of uploaded documents.
* **Document Comparison:** Compares two documents and identifies document-specific findings, similarities, differences, and information not established by the retrieved evidence.
* **Knowledge Graph:** Extracts and represents concepts and relationships discovered from documents.
* **Interactive Knowledge Graph:** Supports concept selection, relationship exploration, zooming, panning, and document provenance.
* **Frontend-Backend Integration:** Provides a complete web interface connected to the FastAPI backend.
* **Backend Health Monitoring:** Displays the backend connection status in the frontend.

## **System Architecture**

MemoryOS follows a modular architecture that separates document processing, embedding generation, vector storage, retrieval, reranking, response generation, and knowledge graph processing.

```text
                         User
                          |
                          v
                    React Frontend
                          |
                          v
                   FastAPI Backend
                          |
          +---------------+----------------+
          |               |                |
          v               v                v
    Document          User Query      Knowledge Graph
    Processing             |                |
          |                v                |
          v         Hybrid Retrieval       |
    PDF Extraction         |                |
          |                v                |
          v        Cross-Encoder           |
     Text Chunking       Reranking          |
          |                |                |
          v                v                |
     Embedding       Relevant Chunks       |
     Generation             |               |
          |                 v               |
          v          Retrieved Context      |
       ChromaDB              |               |
                             v               |
                       Local LLM             |
                        (Ollama)             |
                             |               |
                             v               |
                     Generated Response      |
                             |               |
                             v               |
                       Sources / Citations  |
````

## **Technologies Used**

| Component               | Technology                          |
| ----------------------- | ----------------------------------- |
| Frontend                | React + Vite                        |
| Backend API             | FastAPI                             |
| Programming Language    | Python                              |
| PDF Processing          | pypdf                               |
| Embedding Model         | all-MiniLM-L6-v2                    |
| Embedding Dimensions    | 384                                 |
| Vector Database         | ChromaDB                            |
| Retrieval               | Semantic + Hybrid Retrieval         |
| Reranking               | Cross-Encoder                       |
| Local LLM Runtime       | Ollama                              |
| Language Model          | Phi-3 Mini                          |
| Knowledge Graph         | NetworkX / Persistent Graph Storage |
| Development Environment | Visual Studio Code                  |
| Operating System        | Windows 11                          |

## **Document Processing & Retrieval**

### Document Ingestion

PDF documents are processed through a pipeline that extracts their text, generates document metadata, divides the content into chunks, and prepares the content for semantic and hybrid retrieval.

MemoryOS also performs duplicate detection to prevent the same document from being unnecessarily processed again.

### Text Chunking

Extracted text is divided into smaller chunks for efficient retrieval.

Each chunk retains document-related metadata such as:

* Document ID
* Page number
* Chunk ID
* Document information

This metadata is later used for retrieval, source tracking, and citations.

### Embedding Generation

The `all-MiniLM-L6-v2` model converts text chunks into numerical vector representations.

The generated embeddings have **384 dimensions**.

### Vector Storage

ChromaDB stores the generated embeddings and associated metadata, enabling similarity-based retrieval.

### Semantic & Hybrid Search

When a user submits a query, MemoryOS retrieves relevant document chunks from the vector database.

The retrieval pipeline combines semantic retrieval with hybrid retrieval techniques and uses a cross-encoder reranker to improve the ordering of retrieved results.

The retrieved evidence is then passed to the RAG generation stage.

## **RAG & Local LLM**

MemoryOS uses a Retrieval-Augmented Generation pipeline to generate responses based on information retrieved from the user's documents.

The workflow is:

```text
User Question
      |
      v
Query Processing
      |
      v
Hybrid Retrieval
      |
      v
Relevant Document Chunks
      |
      v
Cross-Encoder Reranking
      |
      v
Retrieved Context
      |
      v
Ollama
      |
      v
Phi-3 Mini
      |
      v
Generated Answer
      |
      v
Sources & Page References
```

The LLM runs locally through Ollama.

This allows MemoryOS to perform its core document-based question answering workflow without depending on a hosted LLM API.

## **Document Comparison**

MemoryOS supports comparison between two uploaded documents.

The user can select:

* Document 1
* Document 2
* A comparison question

The system retrieves relevant evidence from both documents and generates a structured comparison containing:

* Document-specific findings
* Similarities
* Differences
* Information not established by the retrieved evidence
* Source and page references

The comparison workflow uses the same retrieval and local LLM architecture.

> Local CPU-based LLM inference can make complex document comparisons take several minutes on modest hardware.

## **Knowledge Graph**

MemoryOS includes a knowledge graph layer for representing concepts and relationships discovered from uploaded documents.

The knowledge graph supports:

* Concept extraction
* Relationship extraction
* Persistent graph storage
* Interactive graph visualization
* Concept selection
* Relationship exploration
* Relationship labels
* Connected-node highlighting
* Zoom and pan
* Concept details
* Document provenance
* Graph cleanup when documents are deleted

The knowledge graph provides an additional way to explore information beyond traditional document search.

## **Document Management**

MemoryOS provides document management functionality including:

* PDF upload
* Duplicate detection
* Document metadata
* Processing status
* Document listing
* Document details
* Document deletion
* Vector-store cleanup
* Extracted-data cleanup
* Knowledge graph provenance cleanup

Deleting a document also removes its associated data from the relevant storage layers.

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

### 3. Install Backend Dependencies

Install the required Python packages for the backend:

```bash
pip install -r backend/requirements.txt
```

### 4. Install Frontend Dependencies

Navigate to the frontend directory:

```bash
cd frontend
```

Install the required Node.js packages:

```bash
npm install
```

### 5. Install Ollama

Download and install Ollama from:

[https://ollama.com/](https://ollama.com/)

Pull the Phi-3 Mini model:

```bash
ollama pull phi3:mini
```

Ensure Ollama is running before testing features that require the local language model.

## **Usage**

### Running the Backend

Navigate to the backend directory:

```bash
cd backend
```

Activate the virtual environment if it is not already active:

```bash
.venv\Scripts\activate
```

Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Running the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

### Using MemoryOS

1. Launch the Ollama service.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Open the MemoryOS web interface.
5. Upload one or more PDF documents.
6. Allow the documents to be processed and indexed.
7. Search the uploaded documents.
8. Ask questions using the RAG interface.
9. Generate document summaries.
10. Compare two documents.
11. Explore concepts through the Knowledge Graph.
12. Delete documents when they are no longer required.

## **Testing & Validation**

The core document-processing, retrieval, RAG, comparison, and knowledge graph workflows have been tested during development.

| Component                    | Test Result                             |
| ---------------------------- | --------------------------------------- |
| PDF Text Extraction          | Tested                                  |
| Text Chunking                | 124 chunks generated in a test document |
| Embedding Generation         | 384-dimensional embeddings              |
| ChromaDB Initialization      | Tested                                  |
| Embedding Storage            | 124 embeddings stored in a test         |
| Semantic Retrieval           | Tested                                  |
| Hybrid Retrieval             | Working                                 |
| Cross-Encoder Reranking      | Working                                 |
| PDF Upload                   | Working                                 |
| Duplicate Detection          | Working                                 |
| Document Deletion            | Working                                 |
| RAG Question Answering       | Working                                 |
| Source Handling              | Working                                 |
| Document Summaries           | Working                                 |
| Document Comparison          | Working                                 |
| Knowledge Graph              | Working                                 |
| Graph Provenance Cleanup     | Tested                                  |
| Frontend-Backend Integration | Working                                 |

These results represent development tests and functional validation and do not constitute a comprehensive benchmark of answer accuracy, retrieval quality, or model performance.

## **Project Development Roadmap**

### Core Architecture

* [x] PDF text extraction
* [x] Document chunking
* [x] Embedding generation
* [x] ChromaDB integration
* [x] Semantic retrieval
* [x] Hybrid retrieval
* [x] Cross-encoder reranking
* [x] Local LLM integration
* [x] RAG question answering
* [x] Source and citation handling
* [x] Document management
* [x] Document deletion and cleanup
* [x] Document summaries
* [x] Document comparison
* [x] Knowledge graph integration
* [x] Complete frontend-backend integration
* [x] End-to-end functional validation

### Deployment & Finalization

* [ ] Dockerize backend
* [ ] Dockerize frontend
* [ ] Configure Docker Compose
* [ ] Configure persistent data volumes
* [ ] Configure Ollama connectivity
* [ ] Test complete Docker workflow
* [ ] Final GitHub repository cleanup
* [ ] Final README documentation
* [ ] Add project screenshots and architecture visuals

### Advanced Features

* [ ] Advanced multi-document research workflows
* [ ] Agentic AI capabilities
* [ ] Advanced knowledge-management workflows
* [ ] Additional knowledge graph reasoning
* [ ] Model optimization and fine-tuning
* [ ] Expanded document format support
* [ ] Advanced research automation

## **Hardware & Development Environment**

MemoryOS is currently developed and tested on a Windows 11 system with:

* Intel Core i3 processor
* 8 GB RAM
* CPU-based model execution
* No dedicated GPU
* Local Ollama inference

The project emphasizes a modular design that can be developed on modest hardware, although model inference and document processing performance may vary with system resources.

In particular, multi-document comparison can require several minutes of CPU-based inference.

## **Project Status**

**Status:** Core Platform Complete — Deployment Preparation in Progress

MemoryOS's core workflow has been implemented and functionally validated.

The currently working system includes:

* Document ingestion
* PDF extraction
* Intelligent chunking
* Embedding generation
* ChromaDB storage
* Semantic retrieval
* Hybrid retrieval
* Cross-encoder reranking
* RAG question answering
* Source and citation handling
* Document summaries
* Document comparison
* Knowledge graph
* Document management
* Frontend-backend integration

The next major development stage is **Dockerization and deployment preparation**.

## **Future Scope**

Potential future extensions include:

* Multi-document research and synthesis
* Knowledge graph reasoning
* Advanced RAG pipelines
* Agentic research workflows
* Model fine-tuning and optimization
* More comprehensive document-management capabilities
* Additional document formats
* Automated research workflows
* Advanced knowledge-management features

## **Contributing**

Contributions, suggestions, and feedback are welcome.

If you would like to contribute, fork the repository, create a feature branch, and submit a pull request describing your changes.

## **License**

A license has not yet been specified for this repository. Please check the repository for licensing information before using, modifying, or redistributing the project.

## **Author**

**Nihal Karkera**

B.Tech — Artificial Intelligence and Machine Learning

GitHub: [https://github.com/nihalkarkeraa](https://github.com/nihalkarkeraa)

---

*MemoryOS — Turning documents into searchable, usable knowledge.*

```


**MemoryOS progress: 96%** 🚀
```
