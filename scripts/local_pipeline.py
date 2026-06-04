import json
from pathlib import Path
import pandas as pd
import sys


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def apply_dqe(df: pd.DataFrame, dqe: dict):
    """Evaluate simple DQE rules expressed as SQL-like conditions.

    Supported rule types: expect (aggregate), expect_or_drop (row filter), expect_or_fail (raise), expect_or_quarantine (not implemented)
    Conditions must be simple pandas-query compatible expressions.
    """
    results = {"expect": {}, "expect_or_drop": {}, "expect_or_fail": {}}

    # expect: aggregate rules, e.g., COUNT(*) > 0  -> handled as df.shape[0]
    for name, expr in dqe.get("expect", {}).items():
        if "COUNT(*)" in expr:
            # simple handler: COUNT(*) > 0
            res = df.shape[0]
            results["expect"][name] = eval(f"{res}{expr.split('COUNT(*)')[-1]}")
        else:
            # fallback: try pandas query and count
            try:
                q = df.query(expr)
                results["expect"][name] = q.shape[0] > 0
            except Exception:
                results["expect"][name] = False

    # expect_or_drop: drop rows that don't match condition
    df_before = df.shape[0]
    for name, expr in dqe.get("expect_or_drop", {}).items():
        try:
            df = df.query(expr)
            results["expect_or_drop"][name] = True
        except Exception:
            results["expect_or_drop"][name] = False

    # expect_or_fail: fail if condition not met
    for name, expr in dqe.get("expect_or_fail", {}).items():
        try:
            ok = df.query(expr).shape[0] > 0
            results["expect_or_fail"][name] = ok
            if not ok:
                raise AssertionError(f"DQE expect_or_fail '{name}' failed")
        except Exception as e:
            raise

    return df, results


def run_pipeline(conf_path: str, env: str = "dev") -> int:
    conf = load_json(conf_path)
    source_path = conf["source_details"].get(f"source_path_{env}")
    bronze_path = Path(conf.get("bronze_table_path_dev"))
    silver_path = Path(conf.get("silver_table_path_dev"))

    Path("data/bronze").mkdir(parents=True, exist_ok=True)
    Path("data/silver").mkdir(parents=True, exist_ok=True)

    # Read CSV (header) from source_path
    src_dir = Path(source_path)
    csv_files = list(src_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {src_dir}")
        return 2

    df_list = [pd.read_csv(p) for p in csv_files]
    df = pd.concat(df_list, ignore_index=True)

    # Bronze: write parquet
    bronze_path.mkdir(parents=True, exist_ok=True)
    bronze_file = bronze_path / "part-0.parquet"
    df.to_parquet(bronze_file, index=False)

    # Apply bronze DQE
    bronze_dqe = load_json(conf.get("bronze_data_quality_expectations_json"))
    df_bronze, bronze_results = apply_dqe(df, bronze_dqe)
    print("Bronze DQE results:", bronze_results)

    # Silver transformations
    trans_path = conf.get("silver_transformation_json")
    trans = load_json(trans_path)
    # Simple single transformation support
    t = trans[0]
    select_cols = [c for c in t.get("select_exp") if " as " not in c]
    # perform where filters using pandas query when possible
    df_silver = df_bronze.copy()
    for cond in t.get("where_clause", []):
        try:
            df_silver = df_silver.query(cond)
        except Exception:
            # fallback skip
            pass

    # Keep only selected columns (ignore expressions)
    keep = [c for c in select_cols if c in df_silver.columns]
    df_silver = df_silver[keep]

    silver_path.mkdir(parents=True, exist_ok=True)
    silver_file = silver_path / "part-0.parquet"
    df_silver.to_parquet(silver_file, index=False)

    # Apply silver DQE
    silver_dqe = load_json(conf.get("silver_data_quality_expectations_json_dev"))
    df_silver_after, silver_results = apply_dqe(df_silver, silver_dqe)
    print("Silver DQE results:", silver_results)

    return 0


if __name__ == "__main__":
    conf_path = sys.argv[1] if len(sys.argv) > 1 else "conf/onboarding_csv.json"
    rc = run_pipeline(conf_path)
    if rc != 0:
        sys.exit(rc)
