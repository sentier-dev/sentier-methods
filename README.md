# sentier-methods

**LCIA methods** (EF 3.x, IPCC, ReCiPe, …) for the Sentier platform —
characterization-factor tables keyed by elementary flow, with normalization and
weighting sets. A **Data Layer** repo: loadable artifacts only, no
fetch/parse/calculate code.

- **Fed by:** `sentier-importers` (PR / Push).
- **Read by:** `sentier-platform` (GET LCIA matrices).
- **Flow ↔ CF links** resolve via `sentier-mappings`.

## Layout

```
schema/   # YAML column definitions + JSON Schema for metadata
data/     # raw parquet, one subfolder per datasource (ranked)
```

## Data

Each `data/<NN>-<datasource>/` folder holds:

| file | rows |
|---|---|
| `methods.parquet` | one per (method, impact category) |
| `characterization-factors.parquet` | one per CF |
| `normalization-weighting.parquet` | optional normalization & weighting sets |
| `metadata.json` | datasource provenance |

The `NN` rank prefix orders datasources and sets resolution precedence (lower
wins). Parquet payloads are pushed by the Application Layer — the skeleton ships
only folder structure, schemas, and `metadata.json` stubs.

## Schema

Plain-YAML table definitions (`schema/method.yaml`,
`schema/characterization-factor.yaml`, `schema/normalization-weighting.yaml`).
LinkML is used only in `sentier-vocab`; here schemas describe parquet columns
directly.

These files are the **contract**, not code. `sentier-importers` reads them to
validate and cast incoming data before delivering parquet here. This repo ships
no Python package, loader, or tests — all ingestion logic lives in the importer,
the read side in `sentier-platform`.

## License

MIT — open by default, client-loadable.
