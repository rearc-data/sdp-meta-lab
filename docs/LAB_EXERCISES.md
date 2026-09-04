# SDP-Meta Lab Exercises

Hands-on exercises for learning [dlt-meta](https://databrickslabs.github.io/dlt-meta/) (also known as sdp-meta) on Lakeflow Declarative Pipelines. Each lab builds on the previous one, progressing from basic deployment through CDC merge patterns.

**Prerequisites**: Complete the [Deployment Guide](DEPLOYMENT_GUIDE.md) first. You should have a working bundle with the `host_status_updates` append pipeline deployed and producing data.

---

## Lab 1: Deploy and Explore the Append Pipeline

**Objective**: Understand the end-to-end sdp-meta flow by deploying the pre-built append-mode pipeline.

### Steps

1. Follow the [Deployment Guide](DEPLOYMENT_GUIDE.md) through Step 9 to deploy and run the existing pipeline.

2. Examine the onboarding configuration:
   ```bash
   cat conf/onboarding.json
   ```
   Answer these questions:
   * What `source_format` is configured?
   * Where does the source data come from (which Volume path)?
   * What are the bronze and silver table names?

3. Examine the dataflowspec tables that onboarding created:
   ```sql
   SELECT data_flow_id, data_flow_group, source_format, bronze_table, silver_table
   FROM sdp_meta_lab.sdp_meta_20260826.bronze_dataflowspec;
   ```

4. Inspect the bronze output:
   ```sql
   SELECT * FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_csv_bronze
   LIMIT 20;
   ```
   Notice the Autoloader metadata columns (`_rescued_data`, ingestion timestamp, etc.).

5. Inspect the silver output:
   ```sql
   SELECT * FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_csv_silver
   LIMIT 20;
   ```
   Compare to the silver transformation rules in `conf/host_status_updates_silver_transformations.json`.

6. Open the pipeline in the Databricks UI and explore the DAG visualization.

### Checkpoint

You should be able to explain:
* How `onboarding.json` maps to rows in the `bronze_dataflowspec` / `silver_dataflowspec` tables
* How the `init_sdp_meta_pipeline` notebook reads pipeline `configuration` to invoke sdp-meta
* How `data_flow_group` links the onboarding spec to the pipeline

---

## Lab 2: Add a New Data Source (Append Mode)

**Objective**: Onboard a second data source into the same pipeline by adding another entry to the onboarding configuration.

**Time estimate**: 45 minutes

### Scenario

You have a new CSV data source called `deployment_events` that tracks application deployments. The data lands in a Volume as CSV files.

### Sample Data

Create `tests/resources/volume/deployment_events.csv`:

```csv
deploy_id,app_name,environment,deploy_status,deployed_by,deploy_timestamp
DEP-001,web-frontend,production,SUCCESS,alice,2025-06-01T10:30:00
DEP-002,api-gateway,staging,SUCCESS,bob,2025-06-01T11:00:00
DEP-003,web-frontend,production,FAILED,charlie,2025-06-02T09:15:00
DEP-004,data-service,production,SUCCESS,alice,2025-06-02T14:00:00
DEP-005,api-gateway,production,ROLLBACK,bob,2025-06-03T08:45:00
```

### Steps

1. **Create the schema DDL** at `conf/schemas/deployment_events/deployment_events.ddl`:
   ```
   deploy_id STRING,
   app_name STRING,
   environment STRING,
   deploy_status STRING,
   deployed_by STRING,
   deploy_timestamp STRING
   ```

2. **Create bronze DQE** at `conf/dqe/deployment_events_bronze_dqe.json`:
   ```json
   {
     "expect_or_drop": {
       "deploy_id_not_null": "deploy_id IS NOT NULL",
       "app_name_not_null": "app_name IS NOT NULL"
     },
     "expect_or_fail": {
       "valid_status": "deploy_status IN ('SUCCESS', 'FAILED', 'ROLLBACK', 'IN_PROGRESS')"
     }
   }
   ```

3. **Create silver DQE** at `conf/dqe/deployment_events_silver_dqe.json`:
   ```json
   {
     "expect_or_drop": {
       "deploy_id_not_null": "deploy_id IS NOT NULL"
     }
   }
   ```

4. **Create silver transformations** at `conf/deployment_events_silver_transformations.json`:
   ```json
   [
     {
       "target_table": "sdp_meta_20260826.deployment_events_silver",
       "target_partition_cols": [],
       "select_exp": [
         "deploy_id",
         "app_name",
         "environment",
         "deploy_status",
         "deployed_by",
         "to_timestamp(deploy_timestamp) as deploy_timestamp",
         "current_timestamp() as processed_at"
       ],
       "where_clause": [
         "deploy_id is not null"
       ]
     }
   ]
   ```

5. **Create the onboarding entry**. Add a new file `conf/onboarding_deployment_events.json`:
   ```json
   {
     "data_flow_group": "sdp_meta_lab_flow_group",
     "data_flow_id": "deployment_events_csv_volume",
     "source_format": "cloudFiles",
     "source_details": {
       "source_path_dev": "/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/deployment_events/",
       "source_schema_path": "${workspace.file_path}/conf/schemas/deployment_events/deployment_events.ddl"
     },
     "bronze_catalog_dev": "sdp_meta_lab",
     "bronze_database_dev": "sdp_meta_20260826",
     "bronze_table": "deployment_events_csv_bronze",
     "bronze_reader_options": {
       "cloudFiles.format": "csv",
       "header": "true",
       "cloudFiles.inferColumnTypes": "true",
       "cloudFiles.rescuedDataColumn": "_rescued_data"
     },
     "bronze_partition_columns": [],
     "bronze_data_quality_expectations_json": "${workspace.file_path}/conf/dqe/deployment_events_bronze_dqe.json",
     "silver_catalog_dev": "sdp_meta_lab",
     "silver_database_dev": "sdp_meta_20260826",
     "silver_table": "deployment_events_csv_silver",
     "silver_transformation_json_dev": "${workspace.file_path}/conf/deployment_events_silver_transformations.json",
     "silver_data_quality_expectations_json_dev": "${workspace.file_path}/conf/dqe/deployment_events_silver_dqe.json"
   }
   ```

6. **Upload sample data** to the Volume:
   ```bash
   databricks fs mkdirs "dbfs:/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/deployment_events/"
   databricks fs cp tests/resources/volume/deployment_events.csv \
     "dbfs:/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/deployment_events/deployment_events.csv"
   ```

7. **Update the onboarding job** to reference the new file, or run onboarding manually:
   ```bash
   databricks bundle deploy --target dev
   databricks bundle run onboarding --target dev
   ```

   > **Note**: The default `onboarding_file_name` variable points to `onboarding.json`. To onboard the new source, you can either:
   > * Merge the new entry into `conf/onboarding.json` (as a JSON array), or
   > * Override `onboarding_file_name` temporarily to point at the new file.

8. **Run the pipeline** and verify both sources produce tables:
   ```bash
   databricks bundle run bronze_silver --target dev
   ```

### Checkpoint

You should see four tables:
* `host_status_updates_csv_bronze` / `host_status_updates_csv_silver`
* `deployment_events_csv_bronze` / `deployment_events_csv_silver`

All driven by the same pipeline, same notebook, just different metadata rows.

---

## Lab 3: SCD Type 2 Bronze Merge into SCD Type 1 Silver

**Objective**: Configure a CDC merge pipeline where bronze captures full change history (SCD Type 2) and silver maintains only the latest state per key (SCD Type 1).

**Time estimate**: 60 minutes

### Concepts

**SCD Type 2 (Bronze)**: Every change to a record is preserved as a separate row with validity timestamps (`__START_AT`, `__END_AT`). A system can have multiple rows showing its status history.

**SCD Type 1 (Silver)**: Only the most recent state per key is kept. When a new change arrives, the existing row is overwritten (merged) with the latest values.

In sdp-meta, this is configured through the `bronze_cdc_apply_changes` field in the onboarding spec. The framework calls the SDP `apply_changes` API under the hood.

### Sample CDC Data

Create `tests/resources/volume/host_status_updates_cdc.csv`:

```csv
system_id,status,region,hostname,start_date,end_date,operation,change_sequence
SYS-2001,ACTIVE,us-east,web-01,2025-01-01,,INSERT,1
SYS-2002,ACTIVE,eu-west,api-01,2025-01-05,,INSERT,2
SYS-2003,ACTIVE,ap-south,db-01,2025-01-10,,INSERT,3
SYS-2001,DEGRADED,us-east,web-01,2025-02-01,,UPDATE,4
SYS-2002,MAINTENANCE,eu-west,api-01,2025-02-15,2025-02-20,UPDATE,5
SYS-2001,ACTIVE,us-east,web-01,2025-02-15,,UPDATE,6
SYS-2003,OFFLINE,ap-south,db-01,2025-03-01,2025-03-02,UPDATE,7
SYS-2003,ACTIVE,ap-south,db-01,2025-03-03,,UPDATE,8
SYS-2004,ACTIVE,us-west,cache-01,2025-03-10,,INSERT,9
SYS-2002,ACTIVE,eu-west,api-01,2025-02-21,,UPDATE,10
SYS-2004,OFFLINE,us-west,cache-01,2025-04-01,,DELETE,11
```

Notice:
* `operation` column indicates INSERT / UPDATE / DELETE
* `change_sequence` provides ordering (the `sequence_by` field for apply_changes)
* Multiple changes per `system_id` over time

### Step 1: Create the Onboarding Configuration

Create `conf/onboarding_cdc.json`:

```json
{
  "data_flow_group": "sdp_meta_lab_flow_group",
  "data_flow_id": "host_status_updates_cdc",
  "source_format": "cloudFiles",
  "source_details": {
    "source_path_dev": "/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/cdc/",
    "source_schema_path": "${workspace.file_path}/conf/schemas/host_status_updates_cdc/host_status_updates_cdc.ddl"
  },
  "bronze_catalog_dev": "sdp_meta_lab",
  "bronze_database_dev": "sdp_meta_20260826",
  "bronze_table": "host_status_updates_cdc_bronze",
  "bronze_reader_options": {
    "cloudFiles.format": "csv",
    "header": "true",
    "cloudFiles.inferColumnTypes": "true",
    "cloudFiles.rescuedDataColumn": "_rescued_data"
  },
  "bronze_cdc_apply_changes": {
    "keys": ["system_id"],
    "sequence_by": "change_sequence",
    "scd_type": "2",
    "apply_as_deletes": "operation = 'DELETE'",
    "except_column_list": ["operation", "change_sequence"]
  },
  "bronze_partition_columns": [],
  "bronze_data_quality_expectations_json": "${workspace.file_path}/conf/dqe/host_status_updates_cdc_bronze_dqe.json",
  "silver_catalog_dev": "sdp_meta_lab",
  "silver_database_dev": "sdp_meta_20260826",
  "silver_table": "host_status_updates_cdc_silver",
  "silver_cdc_apply_changes": {
    "keys": ["system_id"],
    "sequence_by": "change_sequence",
    "scd_type": "1",
    "except_column_list": ["operation", "change_sequence"]
  },
  "silver_transformation_json_dev": "${workspace.file_path}/conf/host_status_updates_cdc_silver_transformations.json",
  "silver_data_quality_expectations_json_dev": "${workspace.file_path}/conf/dqe/host_status_updates_cdc_silver_dqe.json"
}
```

**Key configuration explained**:

| Field | Value | Purpose |
| --- | --- | --- |
| `bronze_cdc_apply_changes.keys` | `["system_id"]` | Business key for identifying unique records |
| `bronze_cdc_apply_changes.sequence_by` | `change_sequence` | Ordering column to determine "latest" change |
| `bronze_cdc_apply_changes.scd_type` | `2` | Keep full history in bronze (adds `__START_AT`, `__END_AT`) |
| `bronze_cdc_apply_changes.apply_as_deletes` | `operation = 'DELETE'` | Rows matching this condition are treated as deletes |
| `bronze_cdc_apply_changes.except_column_list` | `["operation", "change_sequence"]` | Columns excluded from the target table |
| `silver_cdc_apply_changes.scd_type` | `1` | Only latest state in silver (upsert behavior) |

### Step 2: Create the Schema DDL

Create `conf/schemas/host_status_updates_cdc/host_status_updates_cdc.ddl`:

```
system_id STRING,
status STRING,
region STRING,
hostname STRING,
start_date STRING,
end_date STRING,
operation STRING,
change_sequence INT
```

### Step 3: Create DQE Rules

Create `conf/dqe/host_status_updates_cdc_bronze_dqe.json`:

```json
{
  "expect_or_drop": {
    "system_id_not_null": "system_id IS NOT NULL",
    "operation_not_null": "operation IS NOT NULL"
  },
  "expect_or_fail": {
    "valid_operation": "operation IN ('INSERT', 'UPDATE', 'DELETE')",
    "valid_status": "status IN ('ACTIVE', 'DEGRADED', 'MAINTENANCE', 'OFFLINE')"
  }
}
```

Create `conf/dqe/host_status_updates_cdc_silver_dqe.json`:

```json
{
  "expect_or_drop": {
    "system_id_not_null": "system_id IS NOT NULL"
  }
}
```

### Step 4: Create Silver Transformations

Create `conf/host_status_updates_cdc_silver_transformations.json`:

```json
[
  {
    "target_table": "sdp_meta_20260826.host_status_updates_cdc_silver",
    "target_partition_cols": [],
    "select_exp": [
      "system_id",
      "status",
      "region",
      "hostname",
      "to_date(start_date, 'yyyy-MM-dd') as start_date",
      "to_date(end_date, 'yyyy-MM-dd') as end_date",
      "current_timestamp() as processed_at"
    ],
    "where_clause": [
      "system_id is not null"
    ]
  }
]
```

### Step 5: Upload CDC Data and Deploy

```bash
# Upload CDC sample data
databricks fs mkdirs "dbfs:/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/cdc/"
databricks fs cp tests/resources/volume/host_status_updates_cdc.csv \
  "dbfs:/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/cdc/host_status_updates_cdc.csv"

# Deploy and run onboarding
databricks bundle deploy --target dev
databricks bundle run onboarding --target dev

# Run the pipeline
databricks bundle run bronze_silver --target dev
```

### Step 6: Verify the Results

**Bronze (SCD Type 2)** -- should contain the full history with validity windows:

```sql
SELECT system_id, status, region, hostname, start_date,
       __START_AT, __END_AT
FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_cdc_bronze
ORDER BY system_id, __START_AT;
```

Expected: Multiple rows per `system_id` showing the progression of status changes. `__END_AT IS NULL` means the row is current.

| system_id | status | \_\_START_AT | \_\_END_AT |
| --- | --- | --- | --- |
| SYS-2001 | ACTIVE | seq 1 | seq 4 |
| SYS-2001 | DEGRADED | seq 4 | seq 6 |
| SYS-2001 | ACTIVE | seq 6 | NULL |
| SYS-2004 | ACTIVE | seq 9 | seq 11 |
| SYS-2004 | (deleted) | seq 11 | NULL |

**Silver (SCD Type 1)** -- should contain only the latest state per key:

```sql
SELECT system_id, status, region, hostname, start_date, processed_at
FROM sdp_meta_lab.sdp_meta_20260826.host_status_updates_cdc_silver
ORDER BY system_id;
```

Expected: One row per `system_id` with the most recent values:

| system_id | status | region | hostname |
| --- | --- | --- | --- |
| SYS-2001 | ACTIVE | us-east | web-01 |
| SYS-2002 | ACTIVE | eu-west | api-01 |
| SYS-2003 | ACTIVE | ap-south | db-01 |

`SYS-2004` should be absent (it was deleted).

### Step 7: Simulate Incremental Changes

Create a second CSV file `host_status_updates_cdc_batch2.csv` with new changes:

```csv
system_id,status,region,hostname,start_date,end_date,operation,change_sequence
SYS-2001,MAINTENANCE,us-east,web-01,2025-04-01,2025-04-02,UPDATE,12
SYS-2005,ACTIVE,eu-central,ml-01,2025-04-05,,INSERT,13
SYS-2001,ACTIVE,us-east,web-01,2025-04-03,,UPDATE,14
```

Upload and re-run:

```bash
databricks fs cp host_status_updates_cdc_batch2.csv \
  "dbfs:/Volumes/sdp_meta_lab/sdp_meta_20260826/conf/data/cdc/batch2.csv"

databricks bundle run bronze_silver --target dev
```

Verify:
* Bronze now has additional history rows for SYS-2001 and a new entry for SYS-2005
* Silver SYS-2001 status is back to ACTIVE (latest), SYS-2005 appears

### Checkpoint

You should be able to explain:
* How `bronze_cdc_apply_changes` maps to the SDP `apply_changes` API
* The difference between `scd_type: 1` (upsert) and `scd_type: 2` (full history)
* How `apply_as_deletes` identifies delete operations
* How `sequence_by` determines event ordering
* Why `except_column_list` excludes operational columns from the target

---

## Lab 4: Data Quality Expectations

**Objective**: Understand and extend the DQE framework to build quality gates at each layer.

**Time estimate**: 30 minutes

### Concepts

sdp-meta supports four expectation levels (mirroring SDP expectations):

| Level | Behavior | Use case |
| --- | --- | --- |
| `expect` | Log a warning, keep the row | Soft monitoring |
| `expect_or_drop` | Silently drop failing rows | Filter out bad data |
| `expect_or_fail` | Fail the entire pipeline | Critical data integrity |
| `expect_or_quarantine` | Route failing rows to a quarantine table | Investigate issues without blocking |

### Steps

1. **Review existing DQE rules**:
   ```bash
   cat conf/dqe/host_status_updates_bronze_dqe.json
   cat conf/dqe/host_status_updates_silver_dqe.json
   ```

2. **Add monitoring expectations** to the bronze DQE (these warn but don't drop):
   ```json
   {
     "expect": {
       "hostname_not_empty": "hostname IS NOT NULL AND hostname != ''",
       "region_is_known": "region IN ('us-east', 'us-west', 'eu-west', 'eu-central', 'ap-south', 'ap-east')"
     },
     "expect_or_drop": {
       "system_id_not_null": "system_id IS NOT NULL",
       "start_date_not_null": "start_date IS NOT NULL"
     },
     "expect_or_fail": {
       "valid_status": "status IN ('ACTIVE', 'DEGRADED', 'MAINTENANCE', 'OFFLINE')"
     },
     "expect_or_quarantine": {
       "valid_start_date": "try_to_date(start_date, 'yyyy-MM-dd') IS NOT NULL",
       "valid_end_date": "end_date IS NULL OR end_date = '' OR try_to_date(end_date, 'yyyy-MM-dd') IS NOT NULL"
     }
   }
   ```

3. **Test with intentionally bad data**. Create `tests/resources/volume/bad_data.csv`:
   ```csv
   system_id,status,region,hostname,start_date,end_date
   ,ACTIVE,us-east,db-01,2025-01-01,
   SYS-9001,UNKNOWN,us-east,db-02,2025-01-01,
   SYS-9002,ACTIVE,us-east,db-03,not-a-date,
   SYS-9003,ACTIVE,mars,db-04,2025-01-01,
   SYS-9004,ACTIVE,us-east,db-05,2025-01-01,also-not-a-date
   ```

4. **Upload, run, and observe**:
   * Row 1 (null `system_id`): dropped by `expect_or_drop`
   * Row 2 (`UNKNOWN` status): fails `expect_or_fail` -- pipeline errors
   * Row 3 (bad date): quarantined by `expect_or_quarantine`
   * Row 4 (unknown region): warning logged by `expect`, row kept
   * Row 5 (bad end_date): quarantined

5. **Check the pipeline event log** in the Databricks UI for expectation metrics.

### Challenge

Design a DQE rule set for the `deployment_events` source from Lab 2 that:
* Drops rows missing `deploy_id`
* Fails if `deploy_status` is not in the valid set
* Warns (but keeps) rows where `deployed_by` is null
* Quarantines rows where `deploy_timestamp` is not a valid timestamp

---

## Lab 5: Challenge -- Multi-Layer Pipeline Modes

**Objective**: Explore the `pipeline_mode` variable and run bronze and silver as separate pipelines.

**Time estimate**: 45 minutes

### Background

The bundle's `pipeline_mode` variable supports two modes:
* `combined` (default): One pipeline handles both bronze and silver
* `split`: Two separate pipelines where silver depends on bronze

### Steps

1. Change the `pipeline_mode` variable to `split` in your overrides
2. Examine how the resource template in `resources/sdp_meta_pipelines.yml` would need to change
3. Create a second pipeline resource for silver-only processing
4. Deploy and verify both pipelines run in sequence
5. Compare the DAG visualization in combined vs split mode

### Discussion Questions

* When would you choose split over combined mode?
* How does split mode affect error handling (if bronze fails, silver doesn't run)?
* What are the compute cost implications of running two separate pipelines?

---

## Further Reading

* [dlt-meta CDC Documentation](https://databrickslabs.github.io/dlt-meta/getting_started/cdc/) -- full CDC reference
* [dlt-meta Onboarding Metadata](https://databrickslabs.github.io/dlt-meta/getting_started/metadatapreperation/) -- all onboarding fields
* [SDP apply_changes](https://docs.databricks.com/en/delta-live-tables/cdc.html) -- underlying SDP CDC API
* [Lakeflow Declarative Pipelines](https://docs.databricks.com/en/delta-live-tables/index.html) -- platform documentation
* [Data Quality Expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html) -- SDP expectations reference
