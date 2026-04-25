# MAARS Command — developer entry points.
#
#   make setup   one-shot init: deps, .env, migrations, seed, run
#   make dev     run the backend against an existing .env
#   make seed    re-seed the test user (new API key + top-up)
#   make test    run the four-phase test suite
#   make creds   print cached test credentials from .maars-setup.env
#   make front   launch the frontend dev server (port 3000)
#   make clean   drop __pycache__ + *.pyc

SHELL    := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

PY    ?= $(shell command -v python 2>/dev/null || command -v python3)
PORT  ?= 8000
ENV   ?= $(CURDIR)/.env
BACK  := $(CURDIR)/backend
FRONT := $(CURDIR)/frontend

.PHONY: help setup dev seed test creds front clean

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?##"}{printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

setup: ## one-command init: deps + .env + migrate + seed + run
	@bash $(CURDIR)/setup.sh

dev: ## run backend with reload against the current .env
	@test -f $(ENV) || { echo "no .env — run 'make setup' first"; exit 1; }
	@set -a; . $(ENV); set +a; cd $(BACK) && $(PY) -m uvicorn server:app --reload --port $(PORT)

seed: ## re-seed the test user: fresh API key + top up to 50 credits
	@test -f $(ENV) || { echo "no .env — run 'make setup' first"; exit 1; }
	@set -a; . $(ENV); set +a; cd $(BACK) && $(PY) -m scripts.seed_test_user

test: ## run all 4 phases of the test suite
	@test -f $(ENV) || { echo "no .env — run 'make setup' first"; exit 1; }
	@set -a; . $(ENV); set +a; cd $(BACK) && $(PY) -m pytest \
		tests/test_wallet_ledger_foundation.py \
		tests/test_phase2_providers_scoring_stripe.py \
		tests/test_platform_layer.py \
		tests/test_hardening_and_context.py -v -p no:warnings

creds: ## print the cached test credentials (from .maars-setup.env)
	@test -f $(CURDIR)/.maars-setup.env || { echo "no cached creds — run 'make setup' or 'make seed'"; exit 1; }
	@cat $(CURDIR)/.maars-setup.env

front: ## launch the frontend dev server on :3000
	@cd $(FRONT) && ( yarn install && yarn start ) || ( npm install && npm run start )

clean: ## drop python caches
	@find $(BACK) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find $(BACK) -type f -name '*.pyc' -delete 2>/dev/null || true
	@echo "cleaned"
