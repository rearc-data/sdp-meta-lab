# SDP-Meta Lab: Deployment Guide (Workspace)

This guide walks you through deploying sdp-meta pipelines using the Declarative Automation Bundle (DABs) workflow in this repository. By the end you will have a running bronze+silver Lakeflow Declarative Pipeline ingesting CSV data via Autoloader. This guide will take you through deploying SDP-Meta from a Databricks Workspace.

---

## Prerequisites

| Requirement | Details |
| --- | --- |
| Workspace access | Unity Catalog enabled, permission to create catalogs/schemas/volumes |
| Git repo access | Read access to https://github.com/rearc-data/sdp_meta_lab and the ability to create Git Folders from this repo |

---

## 1. Create a Git Folder from this repo


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
  "uc_catalog_name": "sdp_meta_lab",
  "sdp_meta_schema": "sdp_meta_<YOUR USERNAME>"
}
```

For permanent per-target overrides, add them under `targets.dev.variables` in `databricks.yml`.

Choose a unique schema location for the lab to prevent collision with other labs.

---

## 3. Prepare the Catalog and Schema

Before deploying, ensure the target catalog and schema exist:

```sql
CREATE CATALOG IF NOT EXISTS sdp_meta_lab;
CREATE SCHEMA IF NOT EXISTS sdp_meta_lab.sdp_meta_<YOUR USERNAME>;
```

The onboarding job will create the UC Volume (`conf`) automatically if it does not exist.

---

## 4. Stage the Wheel and Test Data


---

## 5. Validate the Bundle


---

## 6. Deploy the Bundle


---

## 7. Run Onboarding


---

## 8. Run the Pipeline


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

# Re-run onboarding after metadata changes

# Re-run the pipeline (incremental -- only processes new files)

# Full refresh (reprocesses everything)
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
