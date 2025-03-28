#!/usr/bin/env python3
from fastapi import FastAPI, Query, Response
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
import faiss
import json
import uvicorn
import numpy as np
import requests
from fpdf import FPDF
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. You can restrict this to specific domains.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Load and preprocess the data
with open("../datasets/data_mcq.json") as f:
    mcq_data = json.load(f)

with open("../datasets/data_open.json") as f:
    open_data = json.load(f)

class Question(BaseModel):
    type: str
    text: str
    full: dict

def format_text_for_embedding(q):
    heading = q["Question"]["heading"]
    options = q["Question"].get("Options", [])
    full_text = heading
    if options:
        full_text += "\nOptions:\n" + "\n".join(options)
    return full_text

def match_location(query: str, result: dict) -> str:
    heading = result["Question"]["heading"].lower()
    options = "\n".join(result["Question"].get("Options", [])).lower()
    query = query.lower()
    if query in heading:
        return "heading"
    elif query in options:
        return "options"
    else:
        return "other"

# Normalize and build a combined list of documents
documents = []
for q in mcq_data:
    # For MCQ questions, we assign the type "MCQ"
    documents.append(Question(type="MCQ", text=format_text_for_embedding(q), full=q))
for q in open_data:
    # For Open questions, we assign the type "Open"
    documents.append(Question(type="Open", text=format_text_for_embedding(q), full=q))

# Embed using a Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode([doc.text for doc in documents])
embeddings = np.array(embeddings).astype("float32")

# FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

def build_prompt(context_text: str, query: str, mode: str) -> str:
    if mode == "summary":
        return f"""
Given the legal query: '{query}'

Summarize the key legal concepts based only on the text below. Do not invent information.

Context:
{context_text}
"""
    elif mode == "explanation":
        return f"""
Given the legal query: '{query}'

Explain the legal background and correct interpretation using only the information below. Do not make up laws.

Context:
{context_text}
"""
    else:  # default to exam mode
        return f"""
Given the legal query: '{query}'

You are provided with related legal questions and options.

Based only on the text below, do the following:
1. Create one relevant training exam question (if possible).
2. List the multiple-choice options.
3. Explain the correct legal conclusion using only what is stated below.
4. Do not assume facts that are not explicitly written in the retrieved content.

Context:
{context_text}
"""

@app.get("/search")
def search(query: str = Query(..., description="Your keyword(s)"),
           k: int = 5,
           mode: str = Query("exam", enum=["exam", "summary", "explanation"]),
           question_type: str = Query(None, description="Use 'open' for open questions or 'qcm' for multiple choice questions"),
           export_pdf: bool = False):

    # Dynamically load the dataset based on the question_type parameter
    if question_type:
        if question_type.lower() == "qcm":
            with open("../datasets/data_mcq.json") as f:
                selected_data = json.load(f)
        elif question_type.lower() == "open":
            with open("../datasets/data_open.json") as f:
                selected_data = json.load(f)
        else:
            # If an invalid type is provided, default to combined data
            selected_data = mcq_data + open_data
    else:
        selected_data = mcq_data + open_data

    # Build documents for the selected dataset
    selected_documents = []
    for q in selected_data:
        # Use the presence of Options to decide the type; otherwise assume Open
        if "Options" in q["Question"]:
            selected_documents.append(Question(type="MCQ", text=format_text_for_embedding(q), full=q))
        else:
            selected_documents.append(Question(type="Open", text=format_text_for_embedding(q), full=q))

    # Embed the texts for the selected documents
    selected_embeddings = model.encode([doc.text for doc in selected_documents])
    selected_embeddings = np.array(selected_embeddings).astype("float32")

    # Build a FAISS index for the selected dataset
    dimension = selected_embeddings.shape[1]
    selected_index = faiss.IndexFlatL2(dimension)
    selected_index.add(selected_embeddings)

    # Get the query embedding and search the index
    query_vector = model.encode([query]).astype("float32")
    distances, indices = selected_index.search(query_vector, k)

    results = []
    context_parts = []
    for idx in indices[0]:
        doc_entry = selected_documents[idx]
        # Determine the location of the match in the question (heading, options, or other)
        location = match_location(query, doc_entry.full)
        doc_entry.full["match_location"] = location
        results.append(doc_entry.full)
        context_parts.append(doc_entry.full["Question"]["heading"])
        options = doc_entry.full["Question"].get("Options", [])
        if options:
            context_parts.append("Options: " + "; ".join(options))

    context_text = "\n".join(context_parts)

    # Build the prompt for the legal query using the selected context
    prompt = build_prompt(context_text, query, mode)

    # Call your external API (Ollama / Mistral 7B)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    generation = response.json().get("response", "[No response from Mistral]")

    # Optionally export the results as a PDF
    if export_pdf:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Query: {query}\n\nGenerated Answer:\n{generation}")
        pdf_output = "output.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            return Response(content=f.read(), media_type="application/pdf")

    return {
        "query": query,
        "mode": mode,
        "question_type": question_type,
        "results": results,
        "generated_answer": generation
    }
# New model for evaluation requests with the complete details provided by the client
class EvaluationRequest(BaseModel):
    question: str
    real_answer: str
    user_answer: str

@app.post("/evaluate")
def evaluate_open_question(evaluation: EvaluationRequest):
    """
    Evaluation endpoint for open questions.
    Expects a JSON payload with:
      - question: the open question text
      - real_answer: the correct answer provided by the question creator
      - user_answer: the user's answer
    It builds a prompt that compares both answers and sends it to the LLM for evaluation.
    """
    prompt = f"""
Given the open question, its correct answer, and the user's answer, evaluate the user's response for correctness.

Open Question:
{evaluation.question}

Correct Answer:
{evaluation.real_answer}

User's Answer:
{evaluation.user_answer}

Please provide an evaluation stating whether the user's answer is correct, partially correct, or incorrect, and explain your reasoning.
"""
    # Call your external LLM API to evaluate the answer
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    evaluation_result = response.json().get("response", "[No response from LLM]")

    return {
        "evaluation": evaluation_result
    }

if __name__ == "__main__":
    uvicorn.run("embeddings:app", host="0.0.0.0", port=8000, reload=True)
