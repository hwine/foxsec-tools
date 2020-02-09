.DEFAULT_GOAL := help


help:
	@echo "The following targets are available:"
	@echo ""
	@echo "help      display this text"
	@echo "dev-setup configure fresh checkout for development"
	@echo "test      test changes"
	@echo "commit    perform all checks & tests that should pass before committing"
	@echo ""
	@echo "all       build and test"
	@echo "clean     remove all artifacts produced by 'make all'"

all:

test:

clean:

commit: commit-common

dev-setup: dev-common # add target as needed dev-python dev-go dev-java

# --------------- Begin Templated Targets -------------------------
#
#  Ideally, there are no local changes needed below here, so template
#  updates are simple to copy/paste if needed.

dev-common:
	test -f .pre-commit-config.yaml && pre-commit install --allow-missing-config --install-hooks || true

commit-common: 
	@# All modifications should be staged
	git diff-files --quiet || { echo "Unstaged files" ; false; }
	pre-commit run


.PHONY:  \
	all  \
	clean  \
	commit  \
	commit-common  \
	dev-common  \
	dev-go  \
	dev-java  \
	dev-python  \
	dev-setup  \
	help  \
	test  \
	\
