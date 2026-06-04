# Databricks SDP dlt-meta Pipelines

A repository for declarative, metadata-driven data pipelines on Databricks using [dlt-meta](https://databrickslabs.github.io/dlt-meta/) and Autoloader. This project builds pipelines on [Lakeflow Declarative Pipelines](https://www.databricks.com/product/data-engineering/lakeflow-declarative-pipelines) powered by Spark Declarative Pipelines (SDP), with multi-source ingestion patterns.

## Quick Start

### Prerequisites

- Databricks workspace with admin access
- Databricks CLI configured (`databricks configure`)
- Python 3.9+
- Access to cloud storage (S3, Azure Blob, or ADLS)

### Setup

1. Clone and navigate to the repository:
```bash
git clone <repo-url>
cd dlt-meta-pipelines
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Databricks environment:
```bash
databricks workspace ls /
```

4. Deploy the pipeline:
```bash
# Recommended: use the dlt-meta CLI to onboard and deploy pipelines
# Prerequisites: databricks CLI installed and authenticated
databricks auth login --host <WORKSPACE_HOST>

# Install dlt-meta tooling via Databricks Labs CLI
databricks labs install dlt-meta

# (Optional local workflow) clone dlt-meta and prepare a venv for CLI tooling
git clone https://github.com/databrickslabs/dlt-meta.git vendor/dlt-meta
python3 -m venv .venv
source .venv/bin/activate
pip install "PyYAML>=6.0" setuptools databricks-sdk typer[all]==0.6.1

# Onboard your pipeline (interactive prompt will guide you; you can supply a local onboarding JSON)
databricks labs dlt-meta onboard --file conf/onboarding_csv.json

# Deploy Bronze and Silver Lakeflow Declarative Pipelines
databricks labs dlt-meta deploy --file conf/onboarding_csv.json

# Alternatively you can use the included helper script to perform the recommended steps:
./scripts/deploy_dlt_meta.sh --all --file conf/onboarding_csv.json
```

## Project Structure

```
dlt-meta-pipelines/
├── configs/                          # Pipeline metadata configurations
│   ├── pipeline_configs.json        # Main pipeline definitions
│   ├── source_templates/            # Reusable Autoloader source templates
│   └── transformations/             # SQL transformation definitions
├── workflows/                       # Databricks workflow definitions
│   └── *.yml                        # Workflow YAML files
├── scripts/                         # Utility and deployment scripts
│   ├── setup_pipeline.py            # Pipeline initialization
│   └── deploy.sh                    # Deployment helper
├── notebooks/                       # Databricks notebooks
│   └── dlt_meta_pipeline.py         # Main DLT pipeline notebook
├── tests/                           # Test files
│   └── test_pipeline.py             # Pipeline validation tests
├── docs/                            # Documentation
│   ├── SOURCES.md                   # Data source configurations
│   └── DEPLOYMENT.md                # Deployment guide
├── AGENTS.md                        # AI agent guidelines
└── README.md                        # This file
```

## Key Concepts

### dlt-meta Framework
A metadata-driven framework designed to work with [Lakeflow Declarative Pipelines](https://www.databricks.com/product/data-engineering/lakeflow-declarative-pipelines). Pipelines are defined through **metadata configurations** (JSON/YAML), not imperative code. The dlt-meta framework automates:
- Bronze layer generation from Autoloader
- Silver layer data cleaning and deduplication
- Data quality expectations and validations
- CDC (Change Data Capture) handling
- Lakeflow Declarative Pipelines graph building

### Autoloader
Provides cloud-native, incremental file ingestion with:
- Automatic schema evolution detection
- Exactly-once processing semantics via checkpointing
- Support for S3, Azure Blob Storage, and ADLS
- Schema location tracking for evolved schemas

### Architecture Layers
- **Bronze**: Raw ingestion via Autoloader (no transformations)
- **Silver**: Cleaned, conformed, deduplicated data with quality validation
- **Gold**: Business-ready aggregated datasets (optional)

### Technology Stack
- **Lakeflow Declarative Pipelines**: Databricks product for declarative data workflows
- **SDP (Spark Declarative Pipelines)**: Underlying technology powering Lakeflow
- **dlt-meta**: Framework that automates pipeline creation and management

## Adding a New Data Source

1. **Create source template** in `configs/source_templates/`:
```json
{
  "name": "my_source",
  "source_format": "autoloader",
  "source_location": "s3://my-bucket/data/",
  "cloudfiles_format": "parquet",
  "schema_location": "s3://my-bucket/schemas/",
  "trigger": "append",
  "bronze_table": "bronze.my_source",
  "options": {
    "rescuedDataColumn": "_rescued_data"
  }
}
```

2. **Add to pipeline config** in `configs/pipeline_configs.json`

3. **Define transformations** in `configs/transformations/`

4. **Test locally** in Databricks workspace

5. **Deploy** via workflow

## Running Locally

### Test Pipeline Syntax
```bash
python scripts/setup_pipeline.py validate configs/pipeline_configs.json
```

### Deploy to Dev Workspace
```bash
databricks workspace mkdirs /Pipelines/dlt-meta
databricks workspace import-dir ./notebooks /Pipelines/dlt-meta
```

### Run Pipeline
```bash
databricks workflows run-now --job-id <job-id>
```

## Environment Configuration

### Workspace Parameters
Set these in your Databricks workspace:
- `source_path`: Cloud storage path for input data
- `schema_path`: Cloud storage path for schema tracking
- `catalog_name`: Unity Catalog name
- `schema_name`: Schema within catalog

### Secrets
Store credentials securely:
```bash
databricks secrets put --scope pipelines --key cloud-storage-key
```

## Data Quality

Define expectations in Silver layer:
```python
@dlt.table
def silver_my_table():
  return (
    dlt.read_stream("bronze_my_table")
    .dropDuplicates()
    .filter("col1 is not null")
  )

dlt.expect_or_drop("valid_dates", "date_col >= '2020-01-01'")
```

## Testing

Run validation tests:
```bash
pytest tests/
```

Typical test coverage:
- Metadata configuration syntax validation
- Schema compatibility checks
- Autoloader path accessibility
- Transformation idempotency

## Debugging

### Autoloader Issues
- Check `_rescued_data` column for schema mismatches
- Verify cloud storage paths and IAM permissions
- Review Autoloader logs in cluster logs

### Transformation Issues
- Enable DLT lineage visualization in Databricks workspace
- Check data quality expectations failures
- Validate row counts at each layer

### Deployment Issues
- Verify workspace parameter settings
- Check Databricks secret accessibility
- Ensure workflow YAML syntax is valid

## Best Practices

1. **Configuration-First**: Define metadata, then transformations
2. **Idempotent Transforms**: Safe to re-run without duplicates
3. **Schema Evolution**: Always use `rescuedDataColumn` in Autoloader
4. **Environment Awareness**: Never hardcode paths or credentials
5. **Data Quality**: Define expectations early in Silver layer
6. **Testing**: Validate with small data samples before production

## Documentation

- [AGENTS.md](./AGENTS.md) - AI agent guidelines and patterns
- [docs/SOURCES.md](./docs/SOURCES.md) - Data source configurations
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) - Deployment guide
- [dlt-meta Official Docs](https://databrickslabs.github.io/dlt-meta/)

## Contributing

1. Follow naming conventions (bronze.*, silver.domain_subject, gold.business_domain)
2. Use configuration templates for new sources
3. Include data quality expectations in Silver transformations
4. Test metadata syntax before committing
5. Document new sources in SOURCES.md

## Support

- dlt-meta: [Official Documentation](https://databrickslabs.github.io/dlt-meta/)
- Databricks: [Community Forums](https://community.databricks.com/)
- DLT: [Delta Live Tables Guide](https://docs.databricks.com/en/delta-live-tables/index.html)

## License

[Add your license here]
