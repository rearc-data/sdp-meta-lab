# Configuration Files

This directory contains the core dlt-meta metadata configurations.

## Files

### onboarding.json
The primary Dataflowspec that defines:
- Data source details (cloud storage paths, format, schema location)
- Bronze layer configuration (table names, partitioning, properties, data quality expectations)
- Silver layer configuration (table names, transformations, data quality expectations)
- Environment-specific settings (dev/prod)

**Key Fields:**
- `data_flow_id`: Unique identifier for this data pipeline
- `data_flow_group`: Group identifier for launching multiple pipelines under single Lakeflow Declarative Pipeline
- `source_format`: Type of source (cloudFiles, eventhub, kafka, delta, snapshot)
- `bronze_*`: Bronze layer configuration
- `silver_*`: Silver layer configuration
- `*_dev/*_prod`: Environment-specific overrides

### silver_transformations.json
SQL transformation definitions for Silver layer:
- `target_table`: Target silver table name
- `target_partition_cols`: Partition columns for silver table
- `select_exp`: SQL SELECT expressions
- `where_clause`: Filter conditions

### dqe/ Directory
Data Quality Expectations JSON files:
- `*_bronze_dqe.json`: Bronze layer quality rules (expect, expect_or_drop, expect_or_fail, expect_or_quarantine)
- `*_silver_dqe.json`: Silver layer quality rules

## Adding a New Source

1. Create new `onboarding.json` entry (or add to existing for multiple sources)
2. Update `silver_transformations.json` with transformation logic
3. Add corresponding DQE files in `dqe/` directory
4. Reference in workflow YAML for deployment

## Environment Management

Use environment placeholders in field names:
- `source_path_dev`, `source_path_prod`
- `bronze_catalog_dev`, `bronze_catalog_prod`
- `silver_database_dev`, `silver_database_prod`

This allows single metadata definitions to work across multiple environments.

## See Also

- [dlt-meta Metadata Documentation](https://databrickslabs.github.io/dlt-meta/getting_started/metadatapreperation/)
- [onboarding.template Example](https://github.com/databrickslabs/dlt-meta/blob/main/examples/cloudfiles-onboarding.template)
- [Silver Transformations Example](https://github.com/databrickslabs/dlt-meta/blob/main/examples/silver_transformations.json)
