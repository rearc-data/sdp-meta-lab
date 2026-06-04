# Databricks Notebooks

Databricks notebook files for pipeline execution and management.

## Files

### dlt_meta_pipeline.py
Main Lakeflow Declarative Pipeline notebook:
- Reads onboarding.json metadata
- Generates Bronze and Silver layer tables
- Applies data quality expectations
- Handles Autoloader ingestion

This is the core notebook that dlt-meta orchestrates. It:
1. Loads the Dataflowspec from `conf/onboarding.json`
2. Creates Bronze layer tables via Autoloader
3. Applies Silver layer transformations
4. Enforces data quality expectations
5. Logs lineage and metrics

## Development

Notebooks should:
1. Use Databricks native features (dlt.*, spark, dbutils)
2. Reference configuration from `conf/` directory
3. Include error handling and retry logic
4. Log metrics and lineage

## Deployment

Deploy to Databricks workspace:
```bash
databricks workspace mkdirs /Pipelines/dlt-meta
databricks workspace import-dir ./notebooks /Pipelines/dlt-meta
```

## See Also

- [Lakeflow Declarative Pipelines Documentation](https://docs.databricks.com/en/delta-live-tables/index.html)
- [dlt-meta Deployment Guide](https://databrickslabs.github.io/dlt-meta/getting_started/dltmeta_manual/)
