#!/usr/bin/env python3
from codecarbon import track_emissions
from fastapi import FastAPI, Query, Response
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
import faiss
import json
import uvicorn
import numpy as np
import requests
from starlette.middleware.cors import CORSMiddleware
from weasyprint import HTML
from jinja2 import Template
from codecarbon import EmissionsTracker

tracker = EmissionsTracker()

tracker = EmissionsTracker()
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load datasets
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

# Prepare documents
documents = []
for q in mcq_data:
    documents.append(Question(type="MCQ", text=format_text_for_embedding(q), full=q))
for q in open_data:
    documents.append(Question(type="Open", text=format_text_for_embedding(q), full=q))

# Embedding + FAISS
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode([doc.text for doc in documents])
embeddings = np.array(embeddings).astype("float32")
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
    else:
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

@track_emissions(
    measure_power_secs=30,
    api_call_interval=4,
    experiment_id="2bcbcbb8-850d-4692-af0d-76f6f36d79b2",
    save_to_api=True,
)
@app.get("/search")
def search(query: str = Query(...),
           k: int = 5,
           mode: str = Query("exam", enum=["exam", "summary", "explanation"]),
           question_type: str = Query(None),
           export_pdf: bool = False):

    if question_type:
        if question_type.lower() == "qcm":
            with open("../datasets/data_mcq.json") as f:
                selected_data = json.load(f)
        elif question_type.lower() == "open":
            with open("../datasets/data_open.json") as f:
                selected_data = json.load(f)
        else:
            selected_data = mcq_data + open_data
    else:
        selected_data = mcq_data + open_data

    selected_documents = []
    for q in selected_data:
        if "Options" in q["Question"]:
            selected_documents.append(Question(type="MCQ", text=format_text_for_embedding(q), full=q))
        else:
            selected_documents.append(Question(type="Open", text=format_text_for_embedding(q), full=q))

    selected_embeddings = model.encode([doc.text for doc in selected_documents])
    selected_embeddings = np.array(selected_embeddings).astype("float32")
    dimension = selected_embeddings.shape[1]
    selected_index = faiss.IndexFlatL2(dimension)
    selected_index.add(selected_embeddings)

    query_vector = model.encode([query]).astype("float32")
    distances, indices = selected_index.search(query_vector, k)

    results = []
    context_parts = []
    for idx in indices[0]:
        doc_entry = selected_documents[idx]
        location = match_location(query, doc_entry.full)
        doc_entry.full["match_location"] = location
        results.append(doc_entry.full)
        context_parts.append(doc_entry.full["Question"]["heading"])
        options = doc_entry.full["Question"].get("Options", [])
        if options:
            context_parts.append("Options: " + "; ".join(options))

    context_text = "\n".join(context_parts)

    prompt = build_prompt(context_text, query, mode)
    tracker.start()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    generation = response.json().get("response", "[No response from Mistral]")

    if export_pdf:
        template = Template("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1, h2 { color: #2c3e50; }
                .question { margin-bottom: 20px; }
                .options { margin-left: 20px; }
                .generated { border-top: 1px solid #ccc; padding-top: 10px; margin-top: 30px; }
                .meta { font-size: 0.9em; color: #555; }
                .appendix { border-top: 2px dashed #ccc; padding-top: 20px; margin-top: 40px; }
                .qa { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Legal Query</h1>
            <p class="meta"><strong>Query:</strong> {{ query }}<br>
            <strong>Mode:</strong> {{ mode }}<br>
            {% if question_type %}<strong>Question Type:</strong> {{ question_type }}<br>{% endif %}</p>

            <h2>Retrieved Questions</h2>
            {% for q in results %}
            <div class="question">
                <p><strong>{{ loop.index }}. ({{ "MCQ" if "Options" in q.Question else "Open" }})</strong>
                [Matched in: {{ q.match_location }}]</p>
                <p>{{ q.Question.heading }}</p>
                {% if q.Question.Options %}
                <div class="options">
                    <ul>
                    {% for opt in q.Question.Options %}
                        <li>{{ opt }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}

            <div class="generated">
                <h2>Generated Answer</h2>
                <p>{{ generation }}</p>
            </div>

            <div class="appendix">
                <h2>Appendix: Answers, Legal Basis, and Explanation</h2>
                {% for q in results %}
                <div class="qa">
                    <p><strong>{{ loop.index }}. {{ q.Question.heading }}</strong></p>
                    {% if q.Question.Answer %}
                        <p><strong>Answer:</strong> {{ q.Question.Answer }}</p>
                    {% endif %}
                    {% if q.Question.LegalBasis %}
                        <p><strong>Legal Basis:</strong> {{ q.Question.LegalBasis }}</p>
                    {% endif %}
                    {% if q.Question.Explanation %}
                        <p><strong>Explanation:</strong> {{ q.Question.Explanation }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """)

        html_content = template.render(
            query=query,
            mode=mode,
            question_type=question_type,
            results=results,
            generation=generation
        )

        pdf_file = "output.pdf"
        HTML(string=html_content).write_pdf(pdf_file)
        with open(pdf_file, "rb") as f:
            return Response(content=f.read(), media_type="application/pdf")

    return {
        "query": query,
        "mode": mode,
        "question_type": question_type,
        "results": results,
        "generated_answer": generation
    }

class EvaluationRequest(BaseModel):
    question: str
    real_answer: str
    user_answer: str

@app.post("/evaluate")
def evaluate_open_question(evaluation: EvaluationRequest):
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
    tracker.start()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    emission = tracker.stop()
    evaluation_result = response.json().get("response", "[No response from LLM]")
    return {
        "evaluation": evaluation_result,
        "emission": round(emission, 6)
    }

class LegalQueryRequest(BaseModel):
    question: str

@app.post("/legal_query")
def legal_query(request: LegalQueryRequest):
    query = request.question
    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, 1)
    best_distance = distances[0][0]
    SIMILARITY_THRESHOLD = 0.6

    if best_distance < SIMILARITY_THRESHOLD:
        similar_question = documents[indices[0][0]].full
        return {
            "found_similar": True,
            "similar_question": similar_question,
            "message": "A similar legal question was found in the database."
        }
    else:
        prompt = f"""
Given the legal query: '{query}'

Provide a detailed explanation of the legal issue, including the legal basis for your conclusion. Do not invent laws or facts.
"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )
        generation = response.json().get("response", "[No response from Mistral]")
        return {
            "found_similar": False,
            "generated_explanation": generation,
            "message": "No similar question was found in the database, so an explanation was generated."
        }

if __name__ == "__main__":
    uvicorn.run("rag:app", host="0.0.0.0", port=8000, reload=True)
