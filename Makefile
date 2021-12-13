.DEFAULT_GOAL:= build
SHELL := /bin/bash
VENV ?= "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

# Releasing
tag:
	@git tag -a $(version) -m "Release $(version) -> Azure Key Vault Browser"
	@git push --follow-tags

# Building
build: check
	@source $(VENV)
	python tools/bump_version.py
	rm -rf dist || true
	@poetry build

check:
	@source $(VENV)
	black --check .
	mypy tools
	isort --check src/azure_keyvault_browser
	mypy src/azure_keyvault_browser
	flake8 src/azure_keyvault_browser
	darglint -m "{path}:{line} -> {msg_id}: {msg}" src/azure_keyvault_browser

# Developing
.PHONY: init
init:
	@poetry install
	@pre-commit install

.PHONY: app-run
app-run:
	@poetry env use 3.9
	@poetry run kv --config ./dev/.azure_keyvault_browser.toml --debug