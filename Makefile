.PHONY: add build update check test

add:    ; python -m librarian.add_pipeline
build:  ; python -m librarian.write_skill --all && python -m librarian.write_catalog
update: ; python -m librarian.update_pipelines && $(MAKE) build
check:  ; python -m librarian.check_drift && pytest
test:   ; pytest
