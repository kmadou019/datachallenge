from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
import faiss
import json
import uvicorn
import numpy as np

app = FastAPI()

# Load and preprocess the data
with open("data_mcq.json") as f:
    mcq_data = json.load(f)

with open("data_open.json") as f:
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

@app.get("/search")
def search(query: str = Query(..., description="Your keyword(s)"), k: int = 5):
    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, k)
    results = []
    for i in indices[0]:
        doc = documents[i].full
        location = match_location(query, doc)
        doc["match_location"] = location
        results.append(doc)
    return {"query": query, "results": results}

if __name__ == "__main__":
    uvicorn.run("embeddings:app", host="0.0.0.0", port=8000, reload=True)