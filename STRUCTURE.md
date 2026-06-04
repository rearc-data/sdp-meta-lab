# Project Structure Reference

This document confirms the project directory structure aligns with dlt-meta expected patterns and best practices.

## Directory Structure

```
dlt-meta/
├── conf/                              # Core dlt-meta metadata (per official pattern)
│   ├── onboarding.json               # Dataflowspec: source/bronze/silver configuration
│   ├── silver_transformations.json   # SQL transformation definitions
│   ├── dqe/                          # Data Quality Expectations
│   │   ├── my_source_bronze_dqe.json # Bronze layer quality rules
│   │   └── my_source_silver_dqe.json # Silver layer quality rules
│   └── README.md                     # Configuration documentation
├── workflows/                         # Databricks workflow orchestration
│   ├── dlt_meta_onboard.yml          # Onboarding job
│   ├── dlt_meta_dataflow.yml         # Main pipeline execution
│   ├── dlt_meta_scheduled.yml        # Scheduled runs
│   └── README.md                     # Workflow documentation
├── scripts/                           # Utility and deployment scripts
│   ├── setup_pipeline.py             # Pipeline initialization & validation
│   ├── deploy.sh                     # Deployment helper
│   └── README.md                     # Scripts documentation
├── notebooks/                         # Databricks notebook files
│   ├── dlt_meta_pipeline.py          # Main Lakeflow Declarative Pipeline
│   └── README.md                     # Notebook documentation
├── tests/                             # Test files
│   ├── test_pipeline.py              # Pipeline validation tests
│   └── README.md                     # Testing documentation
├── docs/                              # Project documentation
│   ├── SOURCES.md                    # Data source configurations
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── ARCHITECTURE.md               # Architecture decisions
│   └── README.md                     # Documentation index
├── .gitignore                         # Git ignore rules
├── AGENTS.md                          # AI agent guidelines
├── README.md                          # Project overview
└── STRUCTURE.md                       # This file
```

## Core Pattern Validation

### ✅ Official dlt-meta Pattern
The `conf/` directory follows the official dlt-meta structure:

```
conf/
  onboarding.json                    # Dataflowspec (REQUIRED)
  silver_transformations.json        # Silver transformations (REQUIRED)
  dqe/                              # Data Quality Expectations (OPTIONAL)
    bronze_data_quality_expectations.json
    silver_data_quality_expectations.json
```

**Reference:** [dlt-meta Metadata Preparation](https://databrickslabs.github.io/dlt-meta/getting_started/metadatapreperation/)

### ✅ File Purposes

| File | Purpose | dlt-meta Role |
|------|---------|---------------|
| `conf/onboarding.json` | Dataflowspec defining all pipeline metadata | Required - defines sources, bronze, silver config |
| `conf/silver_transformations.json` | SQL transformations for Silver layer | Optional - referenced by onboarding.json |
| `conf/dqe/*.json` | Data quality expectations | Optional - referenced by onboarding.json |
| `workflows/*.yml` | Databricks workflow definitions | Orchestration (not part of dlt-meta core) |
| `notebooks/dlt_meta_pipeline.py` | Main Lakeflow Declarative Pipeline | Execution (generated/managed by dlt-meta) |
| `scripts/*.py` | Validation and deployment helpers | Support tools |
| `tests/*.py` | Pipeline validation tests | Quality assurance |

## Configuration File Format

### onboarding.json Structure
```json
{
  "data_flow_id": "unique_identifier",
  "data_flow_group": "pipeline_group",
  "source_format": "cloudFiles|eventhub|kafka|delta|snapshot",
  "source_details": { /* source configuration */ },
  "bronze_catalog_dev": "catalog_name",
  "bronze_database_dev": "database_name",
  "bronze_table": "table_name",
  "bronze_table_properties": { /* LDP table properties */ },
  "bronze_data_quality_expectations_json": "conf/dqe/bronze_dqe.json",
  "silver_catalog_dev": "catalog_name",
  "silver_database_dev": "database_name",
  "silver_table": "table_name",
  "silver_transformation_json": "conf/silver_transformations.json",
  "silver_data_quality_expectations_json_dev": "conf/dqe/silver_dqe.json"
}
```

### silver_transformations.json Structure
```json
[
  {
    "target_table": "silver.table_name",
    "target_partition_cols": ["col1"],
    "select_exp": ["col1", "col2", "current_timestamp()"],
    "where_clause": ["col1 is not null"]
  }
]
```

### Data Quality Expectations Structure
```json
{
  "expect": { "rule_name": "sql_condition" },
  "expect_or_drop": { "rule_name": "sql_condition" },
  "expect_or_fail": { "rule_name": "sql_condition" },
  "expect_or_quarantine": { "rule_name": "sql_condition" }
}
```

## Environment Configuration

Environment-specific settings are managed via field suffixes:
- `source_path_dev`, `source_path_prod`
- `bronze_catalog_dev`, `bronze_catalog_prod`
- `silver_database_dev`, `silver_database_prod`

This allows single metadata definitions to work across multiple Databricks workspaces.

## Supported Data Sources

dlt-meta supports multiple source formats via `source_format` field:
- **cloudFiles** - Autoloader for cloud storage (S3, Azure Blob, ADLS)
- **eventhub** - Azure Event Hub
- **kafka** - Apache Kafka
- **delta** - Delta Lake tables
- **snapshot** - Snapshot-based CDC

## Next Steps

1. **Update Metadata**: Customize `conf/onboarding.json` with your data sources
2. **Define Transformations**: Add SQL transformations to `conf/silver_transformations.json`
3. **Add Quality Rules**: Create DQE files in `conf/dqe/` for data validation
4. **Create Workflows**: Define Databricks workflows in `workflows/` for orchestration
5. **Deploy**: Use `scripts/deploy.sh` to deploy to your Databricks workspace

## See Also

- [dlt-meta Official Documentation](https://databrickslabs.github.io/dlt-meta/)
- [dlt-meta Examples on GitHub](https://github.com/databrickslabs/dlt-meta/tree/main/examples)
- [Lakeflow Declarative Pipelines Docs](https://docs.databricks.com/en/delta-live-tables/index.html)
- [AGENTS.md](./AGENTS.md) - AI agent guidelines for this repository
