# Architecture

## System Design

This application is a small document question-answering system built around a simple RAG flow:

```text
document -> chunking -> embeddings -> in-memory vector search -> retrieved context -> LLM answer
```

The implementation is intentionally small. It is designed to show the core mechanics clearly rather than simulate a production platform.

## Main Components

### `app/main.py`

Creates the FastAPI app and registers API and UI routes.

### API layer

- `app/api/ingest.py`
  - validates file uploads
  - decodes text
  - triggers chunking, embeddings, and storage
- `app/api/documents.py`
  - returns the currently ingested document list
- `app/api/ask.py`
  - validates question requests
  - retrieves relevant chunks for a document
  - generates the final answer from retrieved context

### Service layer

- `chunking_service.py`
  - splits document text into overlapping chunks
- `embedding_service.py`
  - wraps OpenAI embedding calls
- `vector_store.py`
  - stores embedded chunks in memory
  - runs cosine similarity search
- `retrieval_service.py`
  - embeds the question and queries the vector store
- `llm_service.py`
  - builds the grounded prompt
  - calls OpenAI to generate the final answer

### Models

- `requests.py` and `responses.py` define API input and output shapes
- `domain.py` contains internal data structures used by the services

### UI layer

- `app/ui.py` serves the frontend page
- `app/frontend/index.html` provides:
  - document upload form
  - document library list
  - question input for the selected document

## Request Flows

## `/ingest`

```text
Browser or client
  -> POST /ingest
  -> validate document_id and file
  -> decode uploaded .txt file
  -> chunking_service.chunk_text
  -> embedding_service.embed_texts
  -> vector_store.upsert_document
  -> response with document_id and chunk count
```

Key behavior:

- only `.txt` files are accepted
- UTF-8 decoding is required
- an existing `document_id` is replaced in the current in-memory store

## `/ask`

```text
Browser or client
  -> POST /ask
  -> validate document_id and question
  -> retrieval_service.retrieve_relevant_chunks
      -> embedding_service.embed_texts(question)
      -> vector_store.search(document_id)
  -> llm_service.generate_answer_from_context
  -> response with answer and sources
```

Key behavior:

- the request is scoped to one `document_id`
- only retrieved chunks are passed into the LLM prompt
- if there is not enough support in context, the system instructs the model to return a clear fallback answer

## Data Model

The in-memory store keeps a list of chunks per document.

Each stored chunk contains:

- `document_id`
- `chunk_id`
- `content`
- `embedding`
- optional `title`

This is enough for the current retrieval and response flow, but it is not durable storage.

## Why The System Is Intentionally Simple

The assignment focuses on backend clarity and RAG understanding. Because of that, the implementation avoids:

- persistent infrastructure
- asynchronous job queues
- complex parsing pipelines
- authentication
- separate frontend build tooling
- heavy abstractions or framework layers

That keeps the project easy to run and easy to review.

## Tradeoffs

### In-memory storage

Pros:

- very small setup
- no extra services required
- easy to understand during review

Cons:

- data is lost on restart
- not suitable for multiple app instances
- not suitable for larger corpora

### OpenAI dependency

Pros:

- simple integration
- good answer quality for a small implementation

Cons:

- requires an API key
- introduces network dependency and external service latency

### Document-scoped retrieval

Pros:

- predictable behavior
- simpler UX and API contract

Cons:

- no cross-document search
- no document ranking across the whole library

## Production-Scale Improvements

If this were extended beyond an assessment project, the main changes would be:

### Persistence

- store documents and metadata in a relational database
- move vectors to FAISS, pgvector, or Qdrant
- preserve ingestion state across restarts

### Ingestion pipeline

- support PDF, DOCX, and HTML parsing
- add structured validation and file size limits
- move embedding generation to background jobs for larger files

### Retrieval quality

- improve chunking strategy
- add metadata-aware filtering
- tune top-k and prompt construction with evaluation data
- optionally add reranking

### Reliability

- add retries and timeout handling for OpenAI calls
- add structured logging and metrics
- add tracing for API and model interactions

### Security and multi-user support

- authentication and authorization
- per-user document ownership
- request auditing and secret management

### Testing

- unit tests for chunking and vector search
- integration tests for `/ingest`, `/documents`, and `/ask`
- mocked OpenAI tests for deterministic CI coverage
