.PHONY: help install dev test lint panels baselines reproduce clean

help:
	@echo "Verify-or-Trust — make targets"
	@echo "  install     pip install -e ."
	@echo "  dev         pip install -e '.[agent,dev]'"
	@echo "  test        run the test suite"
	@echo "  lint        ruff check"
	@echo "  panels      build evaluation panels (gears_norman substrate)"
	@echo "  baselines   LLM-free value proof (K1) on the panels"
	@echo "  reproduce   end-to-end: panels -> baselines -> grade committed results"

install:
	pip install -e .

dev:
	pip install -e '.[agent,dev]'

test:
	pytest

lint:
	ruff check src tests

panels:
	vot panels --substrate gears_norman --out runs/panels.jsonl

baselines: panels
	vot baselines --panels runs/panels.jsonl

reproduce: baselines
	@echo "(grading of committed episode outputs wired with the grader in release step 5)"

clean:
	rm -rf build dist *.egg-info runs/ .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
