import ollama
import json

# Define file paths for the questions and answers text files
questions_file = "2012_PreEx_questions_EN.txt"
answers_file = "2012_PreEx_answers_EN.txt"

# Read the content of both text files
with open(questions_file, "r", encoding="utf-8") as qf:
    questions_text = qf.read()

with open(answers_file, "r", encoding="utf-8") as af:
    answers_text = af.read()

# Define a detailed prompt for DeepSeek model
prompt = f"""
You are an expert in processing legal patent examination texts. Your task is to extract structured data from the following text files that contain multiple-choice questions and their corresponding answers.

**Instructions:**
- Identify each question and extract its heading, options, and legal references if available.
- Identify the corresponding answers from the answer text and associate them with the correct question.
- Structure the output as a JSON array where each question follows this format:

```json
[
    {{
        "Question": {{
            "heading": "<Question heading>",
            "Options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ]
        }},
        "Answer": ["True/False", "True/False", "True/False", "True/False"],
        "Legal basis": "<If available, provide the legal references>"
    }}
]
```

**Questions Text:**
{questions_text}

**Answers Text:**
{answers_text}

Now, process the text and return only the structured JSON output.
"""

# Send the request to the DeepSeek model
response = ollama.chat(
    model='deepseek',
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}
    ]
)

# Extract and save the JSON output
extracted_data = response['message']['content']
output_file = "structured_questions_answers.json"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(extracted_data)

print(f"Extracted structured data saved to {output_file}")
