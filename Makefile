.PHONY: help install dev test lint reproduce clean
SUBSTRATE ?= data/substrates/gears_norman.csv
help:
	@echo "make install|dev|test|lint|reproduce"
install:
	pip install -e .
dev:
	pip install -e '.[agent,dev]'
test:
	pytest
lint:
	ruff check src tests
reproduce:
	vot panels --substrate-table $(SUBSTRATE) --out runs/panels.jsonl --seed 13
	vot baselines --panels runs/panels.jsonl --lam 0.5
clean:
	rm -rf build dist *.egg-info runs/ .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
