# SDP-Meta Lab: Deployment Guide (CLI)

This guide walks you through deploying sdp-meta pipelines using the Declarative Automation Bundle (DABs) workflow in this repository. By the end you will have a running bronze+silver Lakeflow Declarative Pipeline ingesting CSV data via Autoloader. This guide will take you through deploying SDP-Meta from a local shell using the Databricks cli.

---

## Prerequisites

| Requirement | Details |
| --- | --- |
| Databricks CLI | v0.240+ installed and authenticated (`databricks auth login`) |
| Workspace access | Unity Catalog enabled, permission to create catalogs/schemas/volumes |
| Python | 3.9+ (for local validation only) |
| sdp-meta wheel | Built or downloaded; path set in `sdp_meta_dependency` variable |

> **Tip**: Run `databricks auth env` to verify your CLI profile is active.

---

## 1. Clone and Open the Bundle

```bash
git clone <repo-url> sdp_meta_lab
cd sdp_meta_lab
```

Open the project folder in your Databricks workspace or work locally with the CLI.

---

## 2. Understand the Bundle Variables

All tuneable parameters live in `resources/variables.yml`. The most important ones for a first deploy:

| Variable | Purpose | Default |
| --- | --- | --- |
| `uc_catalog_name` | Target Unity Catalog catalog | `sdp_meta_lab` |
| `sdp_meta_schema` | Schema for dataflowspec metadata tables | `sdp_meta_20260826` |
| `bronze_target_schema` | Schema where bronze tables land | `sdp_meta_20260826` |
| `silver_target_schema` | Schema where silver tables land | `sdp_meta_20260826` |
| `layer` | Which layers to onboard: `bronze`, `silver`, or `bronze_silver` | `bronze_silver` |
| `sdp_meta_dependency` | Wheel path or PyPI coordinate for the sdp-meta library | Volume wheel path |
| `serverless` | Run pipelines on serverless compute | `true` |
| `conf_volume` | UC Volume for staged configuration files | `conf` |

### Setting Variable Overrides

For local (non-committed) overrides, edit `.databricks/bundle/dev/variable-overrides.json`:

```json
{
  "uc_catalog_name": "my_catalog",
  "sdp_meta_schema": "my_schema"
}
```

For permanent per-target overrides, add them under `targets.dev.variables` in `databricks.yml`.

---

## 3. Prepare the Catalog and Schema

Before deploying, ensure the target catalog and schema exist:

```sql
CREATE CATALOG IF NOT EXISTS sdp_meta_lab;
CREATE SCHEMA IF NOT EXISTS sdp_meta_lab.sdp_meta_20260826;
```

The onboarding job will create the UC Volume (`conf`) automatically if it does not exist.

---

## 4. Stage the Wheel and Test Data

The bundle includes a script to upload the sdp-meta wheel and sample data to the UC Volume:

```bash
databricks bundle run load_test_data --target dev
```

This copies:
* `wheels/databricks_labs_sdp_meta-*.whl` to `/Volumes/<catalog>/<schema>/conf/wheels/`
* `tests/resources/volume/sample.csv` to `/Volumes/<catalog>/<schema>/conf/data/`

---

## 5. Validate the Bundle

Always validate before deploying:

```bash
databricks bundle validate --target dev
```

Fix any errors before proceeding. Common issues:
* Missing variable values (the `__SET_ME__` sentinel will fail-fast)
* Catalog/schema does not exist
* Wheel file not found at the specified path

---

## 6. Deploy the Bundle

```bash
databricks bundle deploy --target dev
```

This creates (in development mode, prefixed with your username):
* **Onboarding job** (`sdp-meta-lab - sdp-meta onboarding`) -- writes dataflowspec rows
* **Pipeline** (`sdp-meta-lab - bronze+silver`) -- the Lakeflow Declarative Pipeline
* **Pipeline runner job** (`sdp-meta-lab - run pipelines`) -- triggers the pipeline

---

## 7. Run Onboarding

Onboarding reads `conf/onboarding.json` and writes rows into the `bronze_dataflowspec` and `silver_dataflowspec` metadata tables:

```bash
databricks bundle run onboarding --target dev
```

The job has two tasks:
1. **stage_conf** -- copies the bundle's `conf/` directory to the UC Volume (required for serverless compute)
2. **onboard_dataflowspecs** -- reads the onboarding file and writes/merges dataflowspec rows

Verify the dataflowspec tables were populated:

```sql
SELECT * FROM sdp_meta_lab.sdp_meta_20260826.bronze_dataflowspec;
SELECT * FROM sdp_meta_lab.sdp_meta_20260826.silver_dataflowspec;
```

---

## 8. Run the Pipeline

Trigger the combined bronze+silver pipeline:

```bash
databricks bundle run pipelines --target dev
```

Or run the pipeline directly:

```bash
databricks bundle run bronze_silver --target dev
```

Monitor progress in the Databricks workspace under **Lakeflow Declarative Pipelines**.

---

## 9. Verify Results

Once the pipeline completes, query the output tables:

```sql
-- Bronze table (raw ingestion via Autoloader)
SELECT * FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_csv_bronze;

-- Silver table (cleaned and transformed)
SELECT * FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_csv_silver;
```

Expected results:
* Bronze contains all rows from `sample.csv` with Autoloader metadata columns
* Silver contains filtered, type-cast rows with a `processed_at` timestamp
* Rows failing DQE `expect_or_drop` rules (null `system_id` or `start_date`) are excluded
* Rows failing `expect_or_fail` rules (invalid `status`) cause the pipeline to error

---

## 10. Iterating and Redeploying

```bash
# Edit configs, then redeploy
databricks bundle deploy --target dev

# Re-run onboarding after metadata changes
databricks bundle run onboarding --target dev

# Re-run the pipeline (incremental -- only processes new files)
databricks bundle run bronze_silver --target dev

# Full refresh (reprocesses everything)
databricks bundle run bronze_silver --target dev --pipeline-flag full_refresh=true
```

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `sdp_meta_dependency is still set to __SET_ME__` | Wheel variable not configured | Set `sdp_meta_dependency` in variables or overrides |
| `Table or view not found: bronze_dataflowspec` | Onboarding not run | Run `databricks bundle run onboarding` |
| Pipeline starts but produces no tables | No matching dataflowspec rows | Check `data_flow_group` matches the pipeline config |
| `Cannot read file from workspace path` on serverless | conf files not staged to Volume | Run onboarding (the `stage_conf` task handles this) |
| Schema mismatch / `_rescued_data` not empty | Source file schema changed | Check `conf/schemas/` DDL and `cloudFiles.inferColumnTypes` setting |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  databricks bundle deploy                               │
├─────────────┬───────────────────────┬───────────────────┤
│ Onboarding  │  Lakeflow Declarative │  Pipeline Runner  │
│ Job         │  Pipeline             │  Job              │
│             │                       │                   │
│ stage_conf  │  init_sdp_meta_       │  Triggers the     │
│   → Volume  │  pipeline notebook    │  pipeline via     │
│ onboard     │    ↓                  │  pipeline_task    │
│   → dfspec  │  DataflowPipeline     │                   │
│     tables  │  .invoke_dlt_pipeline │                   │
│             │    ↓                  │                   │
│             │  Bronze (Autoloader)  │                   │
│             │    ↓                  │                   │
│             │  Silver (Transform)   │                   │
└─────────────┴───────────────────────┴───────────────────┘
```

---

## Next Steps

* [Lab Exercises](LAB_EXERCISES.md) -- hands-on exercises to extend this pipeline
* [dlt-meta Official Docs](https://databrickslabs.github.io/dlt-meta/) -- full framework reference
* [Lakeflow Declarative Pipelines](https://docs.databricks.com/en/delta-live-tables/index.html) -- platform documentation
