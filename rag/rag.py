#!/usr/bin/env python3
from fastapi import FastAPI, Query
import faiss
import uvicorn
import numpy as np
import requests

app = FastAPI()

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

index = faiss.read_index("./db/index.faiss")

@app.get("/search")
def search(query: str = Query(..., description="Your keyword(s)"), k: int = 5):
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
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": f"""Given the legal query: '{query}'

You are provided with related legal questions and options.

Based only on the text below, do the following:
1. Create one relevant training exam question (if possible).
2. List the multiple-choice options.
3. Explain the correct legal conclusion using only what is stated below.
4. Do not assume facts that are not explicitly written in the retrieved content.

Context:
{context_text}

""",
"stream": False
        }
    )
    generation = response.json().get("response", "[No response from Mistral]")

    return {
        "query": query,
        "results": results,
        "generated_answer": generation
    }

if __name__ == "__main__":
    uvicorn.run("embeddings:app", host="0.0.0.0", port=8000, reload=True)
