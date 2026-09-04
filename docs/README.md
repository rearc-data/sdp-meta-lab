# SDP-Meta Lab Documentation

Learning materials and reference guides for [dlt-meta](https://databrickslabs.github.io/dlt-meta/) (sdp-meta) on Lakeflow Declarative Pipelines.

## Getting Started

Start here, in order:

1. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** -- Deploy your first pipeline end-to-end
2. **[LAB_EXERCISES.md](LAB_EXERCISES.md)** -- Hands-on exercises (append, new sources, CDC merge, data quality)

## Lab Exercises Overview

| Lab | Topic | Time |
| --- | --- | --- |
| Lab 1 | Deploy and explore the append pipeline | 30 min |
| Lab 2 | Add a new data source (append mode) | 45 min |
| Lab 3 | SCD Type 2 bronze merge into SCD Type 1 silver | 60 min |
| Lab 4 | Data quality expectations | 30 min |
| Lab 5 | Challenge -- multi-layer pipeline modes | 45 min |

## Examples

The `examples/` directory contains reference configurations:

* **[onboarding.example.json](examples/onboarding.example.json)** -- Full-featured append onboarding template
* **[silver_transformations.json](examples/silver_transformations.json)** -- Basic silver transformation template
* **[cdc_onboarding.example.json](examples/cdc_onboarding.example.json)** -- CDC merge onboarding (SCD Type 2 bronze, SCD Type 1 silver)
* **[cdc_silver_transformations.example.json](examples/cdc_silver_transformations.example.json)** -- CDC silver transformation template
* **[cdc_bronze_dqe.example.json](examples/cdc_bronze_dqe.example.json)** -- DQE rules for CDC pipelines

## Reference

* [dlt-meta Official Docs](https://databrickslabs.github.io/dlt-meta/)
* [dlt-meta CDC Guide](https://databrickslabs.github.io/dlt-meta/getting_started/cdc/)
* [Lakeflow Declarative Pipelines](https://docs.databricks.com/en/delta-live-tables/index.html)
* [SDP Expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html)

## See Also

* [CLAUDE.md](../CLAUDE.md) -- AI agent guidelines
* [README.md](../README.md) -- Project overview
* [STRUCTURE.md](../STRUCTURE.md) -- Project structure reference
