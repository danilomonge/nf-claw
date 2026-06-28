PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

.PHONY: add build update check test

add:    ; $(PYTHON) -m librarian.add_pipeline
build:  ; $(PYTHON) -m librarian.write_skill --all && $(PYTHON) -m librarian.write_catalog
update: ; $(PYTHON) -m librarian.update_pipelines && $(MAKE) build
check:  ; $(PYTHON) -m librarian.check_drift && $(PYTEST)
test:   ; $(PYTEST)
