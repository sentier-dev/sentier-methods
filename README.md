# sentier-methods

## What it is

LCIA methods for the Sentier platform: EF 3.x, IPCC, ReCiPe.
Characterization-factor tables keyed by elementary flow, plus optional normalization and weighting sets.

A **Data Layer** repo. It ships loadable parquet and the schemas that describe it. No fetch, parse, or calculate code.

- **Fed by** `sentier-importers`, which delivers parquet by PR.
- **Read by** `sentier-brightway`, which fetches files pinned by commit. `sentier-platform` (LCIA matrices) is planned.
- **Flow to CF links** resolve via `sentier-mappings`.

## Install

There is no package. Clone `sentier-dev/sentier-methods` and read the parquet directly.

## Use

Read a table with pyarrow:

```bash
uv run --with pyarrow python -c "import pyarrow.parquet as pq; print(pq.read_table('data/01-ef-3.1/methods.parquet').num_rows)"
```

Validate all datasources against the schemas (this is what CI runs on every PR):

```bash
uv run --with pyarrow --with pyyaml --with 'jsonschema[format]' python scripts/validate.py
```

## Layout

```
schema/                  # YAML column definitions + JSON Schema for metadata.json
data/                    # one subfolder per datasource, NN rank prefix
  01-ef-3.1/             #   EF 3.1: 25 methods, 319,393 CFs
  02-ipcc-2021/          #   scaffold, metadata.json only
  03-recipe-2016/        #   scaffold, metadata.json only
scripts/validate.py      # CI validator
.github/workflows/ci.yml # runs validate.py on every PR and non-main push
```

## Data

Each `data/<NN>-<datasource>/` folder holds:

| file | rows |
|---|---|
| `methods.parquet` | one per (method, impact category); PK `method_id` |
| `characterization-factors.parquet` | one per CF; FK `method_id` |
| `normalization-weighting.parquet` | optional; FK `method_id` |
| `metadata.json` | datasource provenance |

`NN` orders datasources and sets resolution precedence. Lower wins.
`method_id` is `<datasource>:<impact_category>`, for example `ef-3.1:climate-change`.

## Schema

Plain-YAML table definitions in `schema/`. LinkML is used only in `sentier-vocab`.

| file | describes |
|---|---|
| `method.yaml` | `methods.parquet` |
| `characterization-factor.yaml` | `characterization-factors.parquet` |
| `normalization-weighting.yaml` | `normalization-weighting.parquet` |
| `metadata.schema.json` | `metadata.json` |

The schemas are the contract. `sentier-importers` reads them to validate and cast data before delivering parquet here.

## Contributing

- New datasource: add `data/<NN>-<name>/metadata.json` first. It validates without parquet.
- Parquet arrives by PR from `sentier-importers`. Do not add loaders or importers here.
- CI runs `scripts/validate.py` on every PR: metadata, required columns, dtypes, PK uniqueness, FK integrity.
- No git-LFS and no release artifacts. Parquet is committed directly.

## License

MIT — open by default, client-loadable.
