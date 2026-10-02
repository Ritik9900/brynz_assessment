.PHONY: install test benchmark download-weights

install:
	pip install -e .
	pip install -r requirements.txt

test:
	pytest tests/

benchmark:
	python tests/benchmark_suite.py

download-weights:
	python scripts/download_weights.py
