import shutil
from pathlib import Path
import pandas as pd
import pytest

from scripts.local_pipeline import run_pipeline


def setup_module(module):
    # clean output dirs
    shutil.rmtree("data/bronze", ignore_errors=True)
    shutil.rmtree("data/silver", ignore_errors=True)


def test_run_local_pipeline():
    rc = run_pipeline("conf/onboarding_csv.json", env="dev")
    assert rc == 0

    bronze_file = Path("data/bronze/part-0.parquet")
    silver_file = Path("data/silver/part-0.parquet")
    assert bronze_file.exists()
    assert silver_file.exists()

    # verify silver content
    df = pd.read_parquet(silver_file)
    assert not df.empty
    assert set(["id", "name", "email"]).issubset(df.columns)
