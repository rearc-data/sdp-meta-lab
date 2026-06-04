# Scripts

Utility scripts for pipeline management and deployment.

## Files

### setup_pipeline.py
Pipeline initialization and validation script:
- Validates metadata configuration syntax
- Checks cloud storage accessibility
- Sets up Unity Catalog structures
- Initializes database/schema

```bash
python setup_pipeline.py validate conf/onboarding.json
python setup_pipeline.py setup --env dev
```

### deploy.sh
Deployment helper script:
- Uploads notebooks to Databricks workspace
- Creates/updates workflows
- Deploys configuration files

```bash
./deploy.sh --env dev
```

## Adding New Scripts

New utility scripts should:
1. Include clear usage documentation
2. Support `--env` parameter for dev/prod environments
3. Include error handling and logging
4. Be idempotent where possible

## See Also

- [dlt-meta CLI](https://databrickslabs.github.io/dlt-meta/getting_started/dltmeta_cli/)
