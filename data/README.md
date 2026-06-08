# data/

Raw **parquet** LCIA artifacts, **one subfolder per datasource**, ranked by a
numeric prefix:

```
data/
  01-ef-3.1/       # rank 1 — highest resolution precedence
  02-ipcc-2021/
  03-recipe-2016/
```

Convention: `data/<NN>-<datasource>/`, where `<datasource>` is the lower-kebab,
version-suffixed id (`ef-3.1`) and `<NN>` sets resolution precedence (lower wins
when records overlap). The rank prefix is **not** part of the datasource id
stored in columns.

Each folder holds `methods.parquet`, `characterization-factors.parquet`,
optionally `normalization-weighting.parquet`, and `metadata.json`. See
[../schema/](../schema/) for column definitions. Parquet payloads are pushed by
`sentier-importers`; the skeleton ships `.gitkeep` + `metadata.json` stubs only.
