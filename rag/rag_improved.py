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

app = FastAPI()

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

# Normalize
documents = []
for q in mcq_data:
    documents.append(Question(type="MCQ", text=format_text_for_embedding(q), full=q))
for q in open_data:
    documents.append(Question(type="Open", text=format_text_for_embedding(q), full=q))

# Embed
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
           export_pdf: bool = False):

    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, k)
    results = []
    context_parts = []
    for i in indices[0]:
        doc = documents[i].full
        location = match_location(query, doc)
        doc["match_location"] = location
        results.append(doc)
        context_parts.append(doc["Question"]["heading"])
        options = doc["Question"].get("Options", [])
        if options:
            context_parts.append("Options: " + "; ".join(options))

    context_text = "\n".join(context_parts)

    # Call Ollama (Mistral 7B)
    prompt = build_prompt(context_text, query, mode)

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
        "results": results,
        "generated_answer": generation
    }

if __name__ == "__main__":
    uvicorn.run("embeddings:app", host="0.0.0.0", port=8000, reload=True)
