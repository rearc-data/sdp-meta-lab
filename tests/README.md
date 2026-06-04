# Tests

Test files for pipeline validation and verification.

## Files

### test_pipeline.py
Pipeline validation tests covering:
- Metadata configuration syntax validation
- Schema compatibility checks
- Autoloader path accessibility
- Transformation idempotency
- Data quality expectations

## Test Categories

### Configuration Tests
- Validate JSON syntax in `conf/` files
- Verify required fields in onboarding.json
- Check consistency across metadata files

### Integration Tests
- Verify cloud storage connectivity
- Test schema location accessibility
- Validate IAM permissions

### Data Quality Tests
- Run sample transformations
- Validate data quality expectations
- Check for schema mismatches

## Running Tests

```bash
pytest tests/
pytest tests/test_pipeline.py -v
```

## Writing Tests

New tests should:
1. Follow pytest conventions
2. Be idempotent (safe to run multiple times)
3. Use fixtures for setup/teardown
4. Include clear docstrings
5. Mock external dependencies where possible

## See Also

- [pytest Documentation](https://docs.pytest.org/)
- [dlt-meta Testing Guide](https://databrickslabs.github.io/dlt-meta/demo/)
