class EvaluationRequest(BaseModel):
    question: str
    reference_answer: str  # Réponse modèle (à retrouver dans open_data)
    user_answer: str

@app.post("/evaluate")
def evaluate_answer(payload: EvaluationRequest):
    prompt = f"""
You are a legal exam corrector.

Here is the question:
{payload.question}

Here is the reference answer (what a perfect answer should contain):
{payload.reference_answer}

Now evaluate the following user's answer:
{payload.user_answer}

Instructions:
- Give a score out of 10.
- Explain what the user did well and what is missing.
- Be objective and use only the reference answer to evaluate.

Respond in JSON format:
{{
    "score": ...,
    "feedback": "...",
    "missing_points": "..."
}}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    result_text = response.json().get("response", "{}")

    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        result_json = {"error": "Could not parse LLM output", "raw": result_text}

    return result_json
