# schema/

Plain-YAML definitions of the parquet tables in `../data/`. Each file maps to one
parquet artifact and lists its columns (`name`, `type`, `required`,
`description`). LinkML is used **only** in `sentier-vocab`; the Data Layer's
parquet repos describe columns directly.

| file | describes |
|---|---|
| `common.yaml` | shared notes / types |
| `method.yaml` | `methods.parquet` |
| `characterization-factor.yaml` | `characterization-factors.parquet` |
| `normalization-weighting.yaml` | `normalization-weighting.parquet` (optional) |
| `metadata.schema.json` | JSON Schema for each datasource's `metadata.json` |

Column types: `string` · `double` · `int` · `date`. `methods.parquet` is the
parent (keyed by `method_id`); the CF and normalization/weighting tables join on
`method_id`.
