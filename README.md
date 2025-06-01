🧠 Intelligent Document Q&A Platform with RAG


📘 Overview
This project demonstrates a Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask questions, receiving contextually relevant answers powered by Large Language Models (LLMs).

🚀 Features
Document upload and text extraction

Text chunking and embedding using sentence-transformers

Vector storage with FAISS

Question answering via Hugging Face Transformers

Backend API built with FastAPI

Frontend interface using Next.js

CI/CD pipeline with GitHub Actions

Deployment on AWS SageMaker (Free Tier)

Metadata storage in Snowflake (Free Trial)

🛠️ Tech Stack
Frontend: Next.js, Tailwind CSS

Backend: FastAPI, Python

LLM: Hugging Face Transformers

Embeddings: sentence-transformers

Vector Store: FAISS

CI/CD: GitHub Actions

Deployment: Docker, AWS SageMaker

Database: Snowflake

📂 Project Structure
├── backend/
│   ├── main.py
│   ├── ingestion.py
│   ├── embedding.py
│   ├── qa_pipeline.py
│   └── requirements.txt
├── frontend/
│   └── (Next.js app files)
├── data/
│   ├── sample_pdfs/
│   └── chunked_data.json
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Dockerfile
├── README.md


🧪 Getting Started
1. Clone the repository:
git clone https://github.com/yourusername/rag-qa-platform.git
cd rag-qa-platform

2. Set up the backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

3. Set up the frontend:
cd frontend
npm install
npm run dev

📸 Screenshots