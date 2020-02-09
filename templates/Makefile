.DEFAULT_GOAL := help


help:
	The following targets are available:

	help      display this text
	dev-setup configure fresh checkout for development
	test      test changes
	commit    perform all checks & tests that should pass before committing

	all       build and test
	clean     remove all artifacts produced by 'make all'

# --------------- Begin Templated Targets -------------------------

dev-setup: dev-common # add target as needed dev-python dev-go dev-java

dev-common:
	pre-commit install --install hooks

commit: 
	@# All modifications should be staged
	git diff-files --quiet || { echo "Unstaged files" ; false; }
	pre-commit run

all: check_venv
	pytest

check_venv:
ifeq ($(VIRTUAL_ENV),)
	$(error "Run frost from a virtualenv (try 'make install && source venv/bin/activate')")
endif

clean: clean-cache clean-python
	rm -rf venv
	# remember to deactivate your active virtual env

clean-cache: check_venv
	@# do as little work as possible to clear the cache, and guarantee success
	pytest --cache-clear --continue-on-collection-errors \
		--collect-only -m "no_such_marker" \
		--noconftest --tb=no --disable-warnings --quiet \
	    || true

clean-python:
	find . -type d -name venv -prune -o -type d -name __pycache__ -print0 | xargs -0 rm -rf

doctest: check_venv
	pytest --doctest-modules -s --offline --debug-calls --ignore pagerduty/

coverage: check_venv
	pytest --cov-config .coveragerc --cov=. \
		--aws-profiles example-account \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/
	coverage report -m
	coverage html

flake8: check_venv
	flake8 --max-line-length 120 $(shell git ls-files | grep \.py$$)

black: check_venv
	pre-commit run black --all-files

install: venv
	( . venv/bin/activate && pip install -U pip && pip install -r requirements.txt  && pre-commit install )

venv:
	python3 -m venv venv

.PHONY: help dev-setup test commit dev-common  dev-python dev-go dev-java
