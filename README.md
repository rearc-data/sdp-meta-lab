# SDP-META Learning Lab by Rearc

A hands-on lab for learning [SDP-Meta](https://github.com/databrickslabs/dlt-meta) (Spark Declarative Pipelines Meta) on Databricks. You will deploy metadata-driven bronze+silver Lakeflow Declarative Pipelines using a Declarative Automation Bundle (DAB), then progressively add CDC, splitting, and merging capabilities through guided lab exercises.

## Prerequisites

| Requirement | Details |
| --- | --- |
| Databricks workspace | Unity Catalog enabled, with permission to create tables, volumes, jobs, and pipelines. Serverless compute must be available. |
| Catalog & schema access | Ability to create (or use an existing) catalog and schema for the lab tables. The default catalog is `sdp_meta_lab`. |
| Git repo access | Read access to <https://github.com/rearc-data/sdp_meta_lab> and the ability to create Git Folders in your workspace. |

## Repository Structure

```
sdp_meta_lab/
├── databricks.yml              # Bundle definition (targets, scripts, includes)
├── requirements.txt            # Python dependencies (pandas, pyarrow, pytest)
├── resources/
│   ├── variables.yml           # All tuneable bundle variables
│   ├── sdp_meta_pipelines.yml  # Lakeflow Declarative Pipeline + run job
│   └── sdp_meta_onboarding_job.yml  # Onboarding job (stage conf → write dataflowspecs)
├── notebooks/
│   └── init_sdp_meta_pipeline  # Runner notebook invoked by the SDP Pipeline
├── labs/
│   ├── LAB 1 - Deploying and Onboarding new Pipelines
│   ├── LAB 2 - CDC - Handling Update Events In Your Data Streams
│   ├── LAB 3 - Complex Pipelines (Splits and Merges)
│   └── Bonus - Advanced Concepts
├── conf/
│   ├── templates/              # Onboarding JSON templates used by the labs
│   ├── schemas/                # Schema definitions for source data
│   ├── dqe/                    # Data quality expectation rules (bronze & silver)
│   └── README.md               # Detailed config file reference
├── data/
│   ├── lab1/                   # Sample CSV (host_status_updates.csv)
│   └── lab3/                   # Regional data splits (us/, eu/, ap/)
└── wheels/
    └── databricks_labs_sdp_meta-0.1.0-py3-none-any.whl
```

## Labs Overview

### Lab 1 — Deploying and Onboarding new Pipelines

Set up the SDP-Meta environment end-to-end: create a Git Folder, configure bundle variables for your user, prepare the Unity Catalog schema and volume, stage test data, generate onboarding configuration from templates, deploy the bundle, run the onboarding job, and start the bronze+silver pipeline.

### Lab 2 — CDC: Handling Update Events In Your Data Streams

Build on Lab 1 by adding change-data-capture semantics. Configure SCD Type 1 merges on the silver table, SCD Type 2 history tracking on the bronze table, delete handling for terminated records, and source-file metadata columns — all through onboarding configuration changes.

### Lab 3 — Complex Pipelines (Splits and Merges)

Learn to split a single bronze table into multiple silver tables by region (demultiplexing), and merge data from multiple regional sources into a single bronze table (multiplexing). Covers `silver_append_flows` and `bronze_reader_options` configuration.

### Bonus — Advanced Concepts

Reference material for snapshot ingestion, custom notebook hooks (`bronze_custom_transform_func` / `silver_custom_transform_func`), row filters, split pipeline modes, and building custom SDP-Meta wheel files.

## Getting Started

### 1. Create a Git Folder

1. In the Databricks sidebar, click **Workspace**.
2. Navigate to your user directory.
3. Click the kebab menu (**⋮**) → **Create** → **Git Folder**.
4. Enter the repository URL: `https://github.com/rearc-data/sdp_meta_lab`
5. Select **GitHub** as the Git provider and click **Create Git Folder**.

### 2. Open Lab 1

Navigate to `labs/LAB 1 - Deploying and Onboarding new Pipelines` inside the Git Folder and follow the notebook from top to bottom. The first cell auto-detects your username and configures the target catalog and schema.

### 3. Deploy the Bundle

Lab 1 walks you through each step, but at a high level the deployment is:

1. **Configure variables** — the lab writes a `variable-overrides.json` file scoping the deployment to your user-specific schema (e.g. `sdp_meta_lab.sdp_meta_<your_username>`).
2. **Prepare the workspace** — create the catalog, schema, and UC volume if they don't exist.
3. **Stage test data** — copy sample CSVs to the UC volume so serverless pipelines can read them.
4. **Generate onboarding config** — populate the onboarding JSON from templates with your schema names.
5. **Deploy** — run `databricks bundle deploy --target dev` to create the pipeline and jobs.
6. **Onboard** — run the onboarding job to write dataflowspec rows.
7. **Run the pipeline** — start the bronze+silver Lakeflow Declarative Pipeline.

### 4. Continue with Labs 2 and 3

Each subsequent lab builds on the previous one. Labs 2 and 3 modify the onboarding configuration to enable new pipeline features, then redeploy and refresh.

## Key Bundle Variables

All variables are defined in `resources/variables.yml`. The most important ones:

| Variable | Purpose | Default |
| --- | --- | --- |
| `uc_catalog_name` | Target Unity Catalog catalog | `sdp_meta_lab` |
| `sdp_meta_schema` | Schema for dataflowspec metadata tables | *(set per user)* |
| `bronze_target_schema` | Schema where bronze tables land | `default` |
| `silver_target_schema` | Schema where silver tables land | `default` |
| `layer` | Layer to onboard: `bronze`, `silver`, or `bronze_silver` | `bronze_silver` |
| `sdp_meta_dependency` | SDP-Meta package to install | `databricks-labs-sdp-meta==0.1.0` |
| `serverless` | Run pipelines on serverless compute | `true` |

## Troubleshooting

* **Variable overrides not found** — make sure you have run the configuration cell in Lab 1 (Step 3) before opening Labs 2 or 3. The overrides file is written to `.databricks/bundle/dev/variable-overrides.json`.
* **Catalog or schema does not exist** — run the "Prepare Workspace" cell in Lab 1 to create the catalog, schema, and volume.
* **Pipeline fails to install sdp-meta** — verify `sdp_meta_dependency` in `resources/variables.yml` points to a valid PyPI coordinate or volume wheel path.
* **Serverless cannot read workspace files** — the onboarding job stages all config files to a UC Volume automatically. If you see path errors, re-run the `stage_conf` task.
* **Permission errors on pipeline or job** — ensure you have permission to create jobs and pipelines in your workspace, and that you own or have write access to the target catalog and schema.