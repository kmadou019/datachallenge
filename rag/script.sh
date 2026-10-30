#!/usr/bin/env bash
# Start the local Ollama server, then run the LLM debate.
ollama serve > /dev/null 2>&1 &
./run_debate.py
