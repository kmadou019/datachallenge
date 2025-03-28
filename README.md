# Legal Question Search & Evaluation API

## Overview
The **Legal Question Search & Evaluation API** is a backend service built with FastAPI that enables users to:
- **Search** for legal questions using advanced **text embedding** and **similarity search** (Sentence Transformers + FAISS).
- **Evaluate** open-ended responses using an external **language model** (e.g., Mistral LLM).
- **Export search results as a PDF** for easy reference.
- **Integrate with a Vue.js frontend** for an interactive UI.

## Features
- **Search Endpoint (`/search`)** – Retrieve relevant legal questions.
- **Evaluation Endpoint (`/evaluate`)** – Assess open-ended responses.
- **Text Embeddings & Similarity Search** – Uses Sentence Transformers and FAISS.
- **PDF Export** – Option to export search results.
- **CORS Support** – Configured for cross-origin requests.

## Repository Structure
```
├── backend
│   ├── embeddings.py      # Main FastAPI application
│   ├── requirements.txt   # Python dependencies for the backend
│
├── frontend
│   ├── package.json       # Node.js dependencies for the Vue.js frontend
│   ├── src/               # Vue.js application source code
│
├── datasets
│   ├── data_mcq.json      # Dataset for multiple-choice questions
│   ├── data_open.json     # Dataset for open-ended questions
│
└── README.md              # Project documentation
```

## Prerequisites
### Backend
- **Python 3.8+**
- **pip**

### Frontend
- **Node.js (v12+)**
- **npm** (or yarn)

### External API
- A running instance of a language model API (e.g., Mistral LLM) accessible at `http://localhost:11434/api/generate`.

## Installation and Setup
### Backend Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository/backend
   ```
2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   **Ensure `requirements.txt` includes:**
   ```
   fastapi
   uvicorn
   pydantic
   sentence-transformers
   faiss-cpu   # or faiss-gpu if applicable
   numpy
   requests
   fpdf
   starlette
   ```
4. **Prepare Datasets**
   Ensure that the `datasets` folder contains:
   ```
   data_mcq.json
   data_open.json
   ```
5. **Run the Backend Server**
   ```bash
   uvicorn embeddings:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be available at: **http://localhost:8000**

### Frontend Setup
1. **Navigate to the Frontend Directory**
   ```bash
   cd ../readlib-front
   ```
2. **Install Dependencies**
   ```bash
   npm install  # or yarn install
   ```
3. **Configure API Endpoint** (if needed)
   The Vue.js frontend is configured to communicate with `http://localhost:8000`. Update config files if your backend is hosted elsewhere.
4. **Run the Frontend Development Server**
   ```bash
   npm run serve  # or yarn serve
   ```
   The frontend will be accessible at **http://localhost:8080** (default port).

## API Endpoints
### **Search Endpoint**
- **URL:** `/search`
- **Method:** `GET`
- **Query Parameters:**
  - `query` (string, required): Keyword(s) for searching legal questions.
  - `k` (integer, optional): Number of results to return (default: 5).
  - `mode` (string, optional): Search mode (`exam`, `summary`, `explanation`, default: `exam`).
  - `question_type` (string, optional): Filter by type (`qcm` for multiple-choice, `open` for open-ended).
  - `export_pdf` (boolean, optional): Set to `true` to export results as a PDF.
- **Example Request:**
   ```bash
   curl "http://localhost:8000/search?query=contract&k=3&mode=summary&question_type=qcm"
   ```

### **Evaluation Endpoint**
- **URL:** `/evaluate`
- **Method:** `POST`
- **Payload:** JSON object with:
  - `question`: The open-ended question text.
  - `real_answer`: The correct answer provided by the creator.
  - `user_answer`: The user's submitted response.
- **Example Request:**
   ```bash
   curl -X POST "http://localhost:8000/evaluate" -H "Content-Type: application/json" -d '{
     "question": "What is the principle of contract law?",
     "real_answer": "Offer, acceptance, and consideration constitute a valid contract.",
     "user_answer": "A contract requires offer and acceptance."
   }'
   ```

## Additional Notes
- **External API Integration:** Ensure that the language model API (`http://localhost:11434/api/generate`) is running. Update if needed.
- **CORS Configuration:** The backend allows all origins for ease of development. Modify in production.
- **PDF Export:** When `export_pdf` is enabled in `/search`, results are formatted and returned as a PDF.
