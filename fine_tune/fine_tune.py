#!/usr/bin/env python3
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

tokenizer.pad_token = tokenizer.eos_token

dataset = load_dataset("text", data_files={"train": "legal_corpus.txt"})

dataset = dataset["train"].train_test_split(test_size=0.2)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./gpt2_legal_model",
    evaluation_strategy="no",  
    save_strategy="epoch",  
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3, 
    weight_decay=0.01,
    save_total_limit=2,  
    logging_dir="./logs",
    logging_steps=500,  
    report_to="none", 
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

model.save_pretrained("./gpt2_legal_model")
tokenizer.save_pretrained("./gpt2_legal_model")
