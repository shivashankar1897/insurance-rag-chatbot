# Insurance Policy RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) based chatbot built for answering questions from insurance policy documents.

The main goal of the project is to make it easier to search through long policy documents and return answers that are grounded in the available source data instead of relying only on the language model's general knowledge.

The application uses a combination of vector search, BM25 keyword search and reranking to retrieve the most relevant document chunks before generating the final answer.

## Features

* Insurance policy question answering
* Document ingestion from AWS S3
* Semantic search using ChromaDB
* BM25 keyword retrieval
* Hybrid search using Reciprocal Rank Fusion
* Cross-encoder reranking
* Query classification
* Input guardrails
* PII detection
* Prompt injection detection
* Out-of-scope query filtering
* Hallucination checking
* Confidence scoring
* Source-based answers
* FastAPI backend
* Streamlit user interface
* Docker support
* AWS deployment setup
* GitHub Actions CI/CD

## How it works

The general flow is:

```text
User Question
      |
      v
Input Guardrails
      |
      v
Query Classification
      |
      v
Hybrid Retrieval
  |         |
  |         |
Vector     BM25
Search     Search
  \         /
   \       /
     RRF
      |
      v
Cross-Encoder Reranking
      |
      v
Prompt + Retrieved Context
      |
      v
LLM Response
      |
      v
Hallucination Check
      |
      v
Confidence Score
      |
      v
Final Answer + Sources
```

The retrieval stage combines semantic similarity with exact keyword matching. This was useful because insurance questions can contain both general language and very specific terms such as policy names, coverage limits, exclusions and clause references.

## Project Structure

```text
insurance-rag-chatbot/
│
├── backend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── api/
│   │   ├── pipeline/
│   │   ├── retrieval/
│   │   ├── ingestion/
│   │   └── guardrails/
│   │
│   ├── prompts/
│   └── tests/
│
├── k8s/
├── .github/
│   └── workflows/
│       └── ci_cd.yml
│
├── docker-compose.yml
└── README.md
```

## Tech Stack

* Python
* FastAPI
* Streamlit
* ChromaDB
* BM25
* OpenAI / Azure OpenAI
* AWS S3
* Docker
* Kubernetes
* Amazon ECR
* Amazon EKS
* GitHub Actions
* Pytest

## Retrieval Approach

I used a hybrid retrieval approach instead of relying only on vector search.

### Vector Search

Document chunks are converted into embeddings and stored in ChromaDB.

This helps retrieve content based on semantic similarity even if the wording of the user's question is different from the wording used in the policy document.

### BM25

BM25 is used for keyword-based retrieval.

This is useful for exact terms such as:

* policy names
* medical procedures
* policy sections
* limits
* exclusions
* claim terms

### Reciprocal Rank Fusion

The vector search and BM25 results are combined using Reciprocal Rank Fusion.

This gives a better final retrieval set than using either method independently.

### Reranking

After hybrid retrieval, a cross-encoder reranker scores the retrieved chunks again based on the relationship between the question and each chunk.

Only the most relevant chunks are passed to the language model.

## Guardrails

The pipeline includes a few checks before and after response generation.

Input checks include:

* PII detection
* prompt injection detection
* out-of-scope question detection
* input length validation

After the response is generated, the application checks whether the answer is actually supported by the retrieved context.

If the generated answer is not sufficiently grounded, the confidence score is reduced.

## Confidence Scoring

Each response receives a confidence score based on retrieval quality, reranking score and grounding.

The application groups responses into:

```text
HIGH
MEDIUM
LOW
```

Low-confidence answers can be flagged for manual review.

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/insurance-rag-chatbot.git
cd insurance-rag-chatbot
```

### 2. Create a virtual environment

```bash
cd backend
python -m venv venv
```

Windows:

```bash
source venv/Scripts/activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the backend folder using `.env.example`.

Example:

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_DEPLOYMENT=your_deployment

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

S3_BUCKET=your_bucket_name
TENANT_ID=star-health
```

Do not commit the `.env` file or any credentials to GitHub.

## Run FastAPI

Open the first terminal:

```bash
cd backend
source venv/Scripts/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

FastAPI runs on:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

## Run Streamlit

Open another terminal:

```bash
cd backend
source venv/Scripts/activate
BACKEND_URL=http://localhost:8000 streamlit run streamlit_app.py --server.port 8501
```

Open:

```text
http://localhost:8501
```

## Docker

The project can also be started using Docker Compose.

From the project root:

```bash
docker compose up --build
```

Available services:

```text
FastAPI   -> http://localhost:8000
Streamlit -> http://localhost:8501
```

To stop:

```bash
docker compose down
```

## Document Ingestion

Before asking questions, the source documents need to be ingested.

During ingestion, the application:

```text
Downloads documents from S3
        |
        v
Parses document content
        |
        v
Creates chunks
        |
        v
Generates embeddings
        |
        v
Stores embeddings in ChromaDB
        |
        v
Builds BM25 index
```

Once ingestion is complete, the documents are available for retrieval.

## Example Questions

Some example questions supported by the chatbot:

```text
What is the room rent limit?

Is cataract surgery covered?

What is the waiting period for pre-existing conditions?

How do I file a claim?

What documents are needed for reimbursement?
```

The response includes the generated answer along with source information and a confidence level.

## Testing

Tests can be run using:

```bash
cd backend
pytest tests/ -v
```

## Deployment

The repository also contains deployment files for Docker, Kubernetes and AWS.

The general deployment flow is:

```text
Git Push
   |
   v
GitHub Actions
   |
   v
Run Tests
   |
   v
Build Docker Image
   |
   v
Push Image to Amazon ECR
   |
   v
Deploy to Amazon EKS
```

## What I learned from this project

This project helped me understand how different parts of a RAG system work together instead of treating RAG as only an embedding search problem.

Some of the areas I worked on include:

* document chunking
* embeddings
* vector search
* BM25 retrieval
* hybrid retrieval
* reranking
* prompt design
* guardrails
* hallucination detection
* confidence scoring
* FastAPI integration
* Streamlit integration
* Docker
* AWS deployment
* CI/CD

One of the main challenges was improving retrieval quality for questions where semantic similarity alone was not enough. Combining BM25 with vector search and reranking gave much more consistent results for policy-specific questions.

## Future Improvements

A few things I plan to add or improve:

* conversation history
* Redis caching
* better observability
* document upload directly from the UI
* authentication
* support for multiple insurance providers
* multilingual queries
* improved evaluation dataset
* additional RAGAS evaluation
* better monitoring for low-confidence answers

## Disclaimer

This project was developed as a learning and portfolio project.

The responses generated by the chatbot should not be considered official insurance advice. Final coverage decisions should always be verified against the original policy documents.
