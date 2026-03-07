.PHONY: test run clean

test:
	python3 -m unittest discover tests

run:
	python3 simulation.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache

