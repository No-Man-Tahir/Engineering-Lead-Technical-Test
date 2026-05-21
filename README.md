# Document QA API

Small FastAPI application that ingests plain text documents, stores chunk embeddings in memory, and answers document-scoped questions with OpenAI.

The project includes:

- a backend API for ingestion and question answering
- a simple browser UI for uploading documents and selecting which document to query
- Docker support for running the app without manual environment setup

## Features

- Upload UTF-8 `.txt` documents through the UI or API
- Split documents into overlapping chunks
- Generate embeddings with OpenAI
- Store vectors in an in-memory vector store
- Retrieve the most relevant chunks for a question using cosine similarity
- Generate answers from retrieved context only
- Return source chunk metadata with each answer
- List ingested documents and select one from the frontend library view

## Tech Stack

- Python
- FastAPI
- Pydantic Settings
- OpenAI Python SDK
- Simple HTML, CSS, and vanilla JavaScript frontend
- Docker and Docker Compose

## Project Structure

```text
app/
  api/
    ask.py
    documents.py
    ingest.py
  frontend/
    index.html
  models/
    domain.py
    requests.py
    responses.py
  services/
    chunking_service.py
    embedding_service.py
    llm_service.py
    retrieval_service.py
    vector_store.py
  config.py
  main.py
  ui.py
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## How To Run

## Local

1. Install dependencies.

```bash
python -m pip install -r requirements.txt
```

2. Create a local environment file.

```bash
copy .env.example .env
```

3. Fill in `OPENAI_API_KEY` in `.env`.

Example:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TIMEOUT_SECONDS=30
OPENAI_MAX_RETRIES=2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=3
MAX_FILE_SIZE_BYTES=2000000
MAX_QUESTION_LENGTH=1000
```

4. Start the app.

```bash
python -m uvicorn app.main:app --reload
```

5. Open the app.

- UI: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Docker

1. Create `.env` from `.env.example` and set `OPENAI_API_KEY`.
2. Start the container.

```bash
docker compose up --build
```

3. Open the app.

- UI: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`

## Frontend Flow

1. Upload a `.txt` file with an optional title.
2. The backend generates a UUID-based `document_id` automatically.
3. Click a document in the library to make it active.
4. Ask a question against the selected document.
5. Review the answer and returned source chunk scores.

## API Overview

### `POST /ingest`

Accepts multipart form data:

- `title` optional
- `file` required, `.txt` only

Validation notes:

- file size is limited by `MAX_FILE_SIZE_BYTES`

Example response:

```json
{
  "message": "Document ingested successfully",
  "document_id": "d388c507-6c8c-4d55-a953-c760be1174d1",
  "chunks_created": 4
}
```

### `GET /documents`

Returns the list of documents currently stored in memory.

Example response:

```json
[
  {
    "document_id": "d388c507-6c8c-4d55-a953-c760be1174d1",
    "title": "Refund Policy",
    "chunks_created": 4
  }
]
```

### `POST /ask`

Accepts JSON:

```json
{
  "document_id": "d388c507-6c8c-4d55-a953-c760be1174d1",
  "question": "What does the document say about refunds?"
}
```

Validation notes:

- `question` is limited by `MAX_QUESTION_LENGTH`
- `document_id` must exist in the current in-memory store

Example response:

```json
{
  "answer": "Refunds are allowed within 30 days of purchase.",
  "sources": [
    {
      "document_id": "d388c507-6c8c-4d55-a953-c760be1174d1",
      "chunk_id": "d388c507-6c8c-4d55-a953-c760be1174d1-0",
      "score": 0.91
    }
  ]
}
```

## Architecture Overview

The request flow is intentionally simple.

### Ingestion

```text
Client -> /ingest -> chunking_service -> embedding_service -> vector_store
```

### Question Answering

```text
Client -> /ask -> retrieval_service -> vector_store -> llm_service -> response
```

### UI

```text
Browser -> / -> frontend page -> /documents, /ingest, /ask
```

The API layer handles validation and HTTP responses. The service layer contains the chunking, embedding, retrieval, vector search, and LLM interaction logic.

More detail is in `ARCHITECTURE.md`.

## Design Decisions

### FastAPI

FastAPI keeps the project small and easy to run. It also provides request validation and interactive Swagger docs out of the box.

### In-memory vector store

The vector store is kept in process memory to keep setup simple and focused on the RAG pipeline. This means data is lost on restart.

### OpenAI for embeddings and answer generation

Using OpenAI keeps the embedding and answer generation code short and readable. The provider-specific logic is kept in dedicated service files so the rest of the app does not depend on SDK details. The client is configured with basic timeout and retry settings from environment variables.

### Document-scoped questions

`/ask` requires `document_id`. That avoids ambiguous cross-document retrieval and makes the behavior explicit in both the API and the UI.

### Plain text input only

The first version supports `.txt` uploads only. That keeps parsing logic straightforward and avoids pulling in PDF or DOCX parsing complexity that is not central to the assignment.

### Minimal frontend

The frontend is a small server-rendered static page served by FastAPI. It is enough to demonstrate the full flow without introducing a separate frontend build system.

## Limitations

- Only `.txt` files are supported
- Data is stored in memory and is lost when the server restarts
- No authentication or multi-user separation
- No background processing for large uploads
- No persistent database or vector index
- No test suite has been added yet
- OpenAI retry behavior is basic client-level retry configuration rather than a more advanced resilience layer

## Production Improvements

- Replace the in-memory vector store with a persistent store such as FAISS
- Add document persistence and metadata storage in a database
- Support more file types with dedicated parsing and validation
- Add authentication and per-user document isolation
- Add observability, request logging, and tracing around OpenAI calls
- Add retries, rate-limit handling, and timeout policies for external API calls
- Add automated tests for ingestion, retrieval, and answer generation flows
