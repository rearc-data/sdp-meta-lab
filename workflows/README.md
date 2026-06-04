# Workflows

This directory contains Databricks workflow definitions for orchestrating dlt-meta pipelines.

## Files

### Deployment Workflows
- `dlt_meta_onboard.yml` - Onboarding job to prepare metadata and set up initial pipeline
- `dlt_meta_dataflow.yml` - Main data pipeline execution (Bronze and Silver layers)
- `dlt_meta_scheduled.yml` - Scheduled pipeline runs

## Workflow Structure

Each workflow YAML should define:
- Job name and description
- Cluster configuration
- Notebook/task definitions
- Parameters and environment variables
- Schedule/trigger settings
- Retry logic and alerts

## Example Workflow

```yaml
name: dlt-meta-dataflow
tasks:
  - task_key: dlt_meta_pipeline
    notebook_task:
      notebook_path: /Pipelines/dlt-meta/dlt_meta_pipeline
    cluster:
      spark_version: "14.3.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 2
```

## Deployment

Deploy workflows using Databricks CLI:
```bash
databricks workflows create --from-yaml dlt_meta_dataflow.yml
```

Or use the deploy script:
```bash
./scripts/deploy.sh
```



## Parameters

Pass configuration via workflow parameters:
- `env`: Environment (dev/prod)
- `layer`: Pipeline layer (bronze, silver, bronze_silver)
- `data_flow_group`: Which pipeline group to run

## See Also

- [Databricks Workflows Documentation](https://docs.databricks.com/en/workflows/index.html)
- [dlt-meta CLI Deployment Guide](https://databrickslabs.github.io/dlt-meta/getting_started/dltmeta_cli/)
