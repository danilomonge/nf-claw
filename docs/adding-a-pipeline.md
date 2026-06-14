# Adding a pipeline

```bash
echo -e "fetchngs\thttps://github.com/nf-core/fetchngs.git\tlatest-release" >> sources.tsv
git submodule add https://github.com/nf-core/fetchngs.git pipelines/fetchngs/upstream
make build      # generates skill.md + reference.md + refreshes catalog
make check      # drift gate + tests
```
No Python is written. The generator reads the pipeline's own schema files.
