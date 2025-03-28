#!/usr/bin/env python3
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline

model_path = "./gpt2_legal_model"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
prompt = "What is the assessment of the Rule 126(2) "
result = generator(prompt, max_length=500, num_return_sequences=3, truncation=True)
print(result[0]["generated_text"])