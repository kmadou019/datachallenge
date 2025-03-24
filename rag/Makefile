.PHONY : run clean install require 

run:
	./rag.py
clean:
	rm db/*
install:
	pip install -r require.txt

require:
	pip freeze > require.txt