#!/usr/bin/env bash

source ../../subjective-comment-clf/mon_env/bin/activate
/home/daisy/konema/Documents/ollama/bin/ollama serve & >/dev/null
./run_debate.py