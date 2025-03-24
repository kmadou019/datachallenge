#!/usr/bin/env python3
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np


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
faiss.write_index(index, "./db/index.faiss")