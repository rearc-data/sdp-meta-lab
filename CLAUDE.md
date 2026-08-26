# Databricks SDP dlt-meta Pipelines - AI Agent Guide

This repository contains metadata-driven data pipelines built with [dlt-meta](https://databrickslabs.github.io/dlt-meta/) on [Lakeflow Declarative Pipelines](https://www.databricks.com/product/data-engineering/lakeflow-declarative-pipelines). dlt-meta is a framework for automating declarative, metadata-driven pipeline creation using Spark Declarative Pipelines (SDP). The pipelines use Autoloader to ingest data from multiple sources with modern best practices.

## Project Overview

- **Framework**: [dlt-meta](https://databrickslabs.github.io/dlt-meta/) - Automates metadata-driven pipeline creation on Lakeflow Declarative Pipelines
- **Platform**: [Lakeflow Declarative Pipelines](https://www.databricks.com/product/data-engineering/lakeflow-declarative-pipelines) powered by SDP (Spark Declarative Pipelines)
- **Pattern**: Autoloader-based incremental ingestion with medallion architecture
- **Target**: Multi-source data ingestion supporting diverse patterns
- **Deployment**: Databricks workflows orchestration

## Core Architecture Principles

### dlt-meta Metadata-Driven Approach
- Pipelines are defined through **metadata** (JSON/YAML configurations) rather than imperative code
- This repository stores pipeline metadata definitions, configuration templates, and transformation logic
- dlt-meta framework automates Lakeflow Declarative Pipeline creation and manages medallion architecture (Bronze/Silver/Gold)
- Single generic pipeline reads metadata and orchestrates all data processing workloads

### Autoloader Patterns
- **Cloud Source Detection**: Autoloader continuously monitors cloud storage paths (S3, Azure Blob Storage, ADLS)
- **Incremental Processing**: Only processes new/updated files
- **Schema Evolution**: Handles schema changes automatically via `cloudFiles` API
- **Checkpointing**: Maintains state to ensure exactly-once semantics

### Medallion Architecture
- **Bronze Layer**: Raw ingestion via Autoloader (minimal transformations)
- **Silver Layer**: Cleaned, deduplicated, conformed data
- **Gold Layer**: Business-ready aggregated datasets (optional)
- **Data Quality**: Enforced at each layer transition via expectations

## Project Structure Conventions

```
dlt-meta-pipelines/
├── configs/                          # dlt-meta configuration files
│   ├── pipeline_configs.json        # Main pipeline definitions
│   ├── source_templates/            # Reusable Autoloader source templates
│   └── transformations/             # SQL transformation definitions
├── workflows/                       # Databricks workflow definitions
│   └── *.yml                        # Workflow YAML files
├── scripts/                         # Utility and deployment scripts
│   ├── setup_pipeline.py            # Pipeline initialization
│   └── deploy.sh                    # Deployment helper
├── notebooks/                       # Databricks notebooks (if needed)
│   └── dlt_meta_pipeline.py         # Main DLT pipeline notebook
├── tests/                           # Test files
│   └── test_pipeline.py             # Pipeline validation tests
├── docs/                            # Documentation
│   ├── SOURCES.md                   # Data source configurations
│   └── DEPLOYMENT.md                # Deployment guide
└── README.md                        # Project overview
```

## Key Files and Patterns

### Pipeline Metadata Configuration
- **Location**: `configs/pipeline_configs.json`
- **Pattern**: Declarative JSON schema defining sources, transformations, and targets
- **Key Fields**: `source`, `source_format`, `target_schema`, `bronze_layer`, `silver_layer`, `gold_layer`

### Autoloader Source Template
```json
{
  "name": "source_name",
  "source_format": "autoloader",
  "source_location": "s3://bucket/path or abfss://container/path",
  "cloudfiles_format": "parquet|csv|json",
  "schema_location": "s3://bucket/schema_location",
  "trigger": "append|update",
  "bronze_table": "bronze.source_name"
}
```

### DLT Notebook Pattern
- Use `@dlt.table` and `@dlt.view` decorators for declarative transforms
- Leverage dlt-meta for auto-generating Bronze tables from Autoloader
- Write SQL/Python transformations for Silver and Gold layers
- Implement data quality rules with `@dlt.quality` expectations

## Development Best Practices

### 1. Configuration-Driven Design
- Minimize hardcoded values; use configuration files for sources, paths, and transformations
- Keep metadata separate from logic for reusability across environments (dev/staging/prod)

### 2. Autoloader Configuration
- Always specify `schema_location` for schema evolution tracking
- Use `trigger` appropriately: `"append"` for new files, `"update"` for updated files
- Enable `rescuedDataColumn` for handling schema mismatches: `"option": {"rescuedDataColumn": "_rescued_data"}`

### 3. Multi-Source Patterns
- Create separate source definitions for each data source
- Use naming conventions: `bronze.<source_name>`, `silver.<domain>_<subject>`, `gold.<business_domain>`
- Implement idempotent transformations (safe to re-run without duplicates)

### 4. Data Quality
- Define expectations in Silver layer to validate Bronze data
- Use `assert_valid_data` patterns for quality checks
- Tag quality-critical transformations for monitoring

### 5. Testing Strategy
- Validate pipeline metadata syntax before deployment
- Test Autoloader discovery with small data samples
- Verify transformations produce expected schema and row counts
- Implement row-level data quality tests

### 6. Environment Management
- Use Databricks secrets for cloud credentials and API keys
- Keep separate workspace configurations for dev/staging/production
- Use workspace parameters for paths and catalog names
- Document environment-specific overrides

## Common Development Tasks

### Adding a New Data Source
1. Create source definition in `configs/source_templates/`
2. Add to `configs/pipeline_configs.json` with Autoloader configuration
3. Define Bronze → Silver transformation in `configs/transformations/`
4. Add schema validation tests
5. Deploy via workflow

### Modifying Transformations
1. Update SQL/Python in DLT notebook
2. Test locally in Databricks workspace
3. Validate data quality rules
4. Deploy via workflow with rollback plan

### Debugging Pipeline Failures
- Check Autoloader logs in Databricks cluster logs
- Validate schema compatibility (use `rescuedDataColumn`)
- Verify source file paths and permissions
- Check for schema evolution issues in `_rescued_data` column
- Review DLT lineage for transformation failures

## Common Pitfalls to Avoid

1. **Schema Evolution**: Don't ignore `_rescued_data` column; investigate schema mismatches
2. **Duplicate Processing**: Ensure transformations are idempotent; check checkpoint integrity
3. **Path Configuration**: Verify cloud storage paths and permissions before deployment
4. **Environment Variables**: Never hardcode paths; use workspace configs and secrets
5. **Performance**: Monitor Autoloader scan times; consider partitioning strategies
6. **Expectations Definition**: Define quality expectations early; don't add them as afterthought

## Useful Commands & References

### Databricks CLI
```bash
databricks workspace export-dir . ./local_export    # Export workspace
databricks workflows run-now --job-id <ID>          # Trigger pipeline
databricks secrets put --scope <scope> --key <key>  # Store secrets
```

### dlt-meta Documentation
- [Official dlt-meta Docs](https://databrickslabs.github.io/dlt-meta/)
- [Autoloader Configuration](https://databrickslabs.github.io/dlt-meta/user_guide/autoloader)
- [SDP Pattern Guide](https://databrickslabs.github.io/dlt-meta/patterns/sdp)

### Testing & Validation
- Use DLT's built-in quality expectations
- Enable table versioning for rollback capability
- Test schema evolution with sample files

## AI Agent Guidelines

When working on this repository:

1. **Understand dlt-meta First**: Reference the official dlt-meta documentation for configuration patterns
2. **Configuration-First Approach**: Start with metadata definitions; code generation/transformations follow
3. **Multi-Source Thinking**: Always consider how changes scale to new sources
4. **Environment Awareness**: Consider dev/staging/prod implications; don't hardcode values
5. **Quality Validation**: Include data quality expectations and tests
6. **Documentation**: Keep source configurations documented (purpose, source location, refresh cadence)
7. **Idempotency**: Ensure all transformations can be safely re-run

## Related Skills & Patterns

- Lakeflow Declarative Pipelines and Spark Declarative Pipelines (SDP) best practices
- Metadata-driven pipeline automation with dlt-meta
- Data pipeline orchestration patterns
- Schema evolution and data quality frameworks
- Incremental ingestion with Autoloader
- Environment-driven configuration management

