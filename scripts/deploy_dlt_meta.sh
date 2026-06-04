#!/usr/bin/env bash
# Deploy helper for dlt-meta using the dlt-meta CLI recommended process.
# - Creates venv and installs required Python deps
# - Clones dlt-meta repo for local tooling
# - Optionally runs `databricks labs dlt-meta onboard` and `deploy`

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
DLT_META_DIR="$REPO_ROOT/vendor/dlt-meta"

usage() {
  cat <<EOF
Usage: $0 [--install-deps] [--onboard] [--deploy] [--all]

Options:
  --install-deps   Create venv and install python dependencies required for dlt-meta CLI
  --onboard        Run 'databricks labs dlt-meta onboard' (prompts interactively unless --file used)
  --deploy         Run 'databricks labs dlt-meta deploy'
  --all            Run install-deps, onboard, then deploy
  --file <path>    Use a local onboarding JSON file when invoking onboard/deploy
  -h, --help       Show this help
EOF
}

if [ "$#" -eq 0 ]; then
  usage
  exit 1
fi

ONBOARD_FILE=""
DO_INSTALL=false
DO_ONBOARD=false
DO_DEPLOY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-deps) DO_INSTALL=true; shift ;;
    --onboard) DO_ONBOARD=true; shift ;;
    --deploy) DO_DEPLOY=true; shift ;;
    --all) DO_INSTALL=true; DO_ONBOARD=true; DO_DEPLOY=true; shift ;;
    --file) ONBOARD_FILE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

echo "Repo root: $REPO_ROOT"

if $DO_INSTALL; then
  echo "Setting up Python virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  echo "Installing required Python packages"
  pip install "PyYAML>=6.0" setuptools databricks-sdk typer[all]==0.6.1
  echo "Python environment ready"
fi

# Ensure databricks CLI is available
if ! command -v databricks >/dev/null 2>&1; then
  echo "Warning: databricks CLI not found in PATH. Please install and authenticate."
  echo "See: https://docs.databricks.com/en/dev-tools/cli/index.html"
fi

# Clone dlt-meta repo if not present (local tooling)
if [ ! -d "$DLT_META_DIR" ]; then
  echo "Cloning dlt-meta into $DLT_META_DIR"
  mkdir -p "$(dirname "$DLT_META_DIR")"
  git clone https://github.com/databrickslabs/dlt-meta.git "$DLT_META_DIR"
fi

# Export PYTHONPATH so dlt-meta modules are importable when running commands locally
export PYTHONPATH="$DLT_META_DIR:$REPO_ROOT:$PYTHONPATH"

run_cli() {
  cmd=("databricks" "labs" "dlt-meta" "$1")
  if [ -n "$ONBOARD_FILE" ]; then
    # attempt to pass file flag if supported
    cmd+=("--file" "$ONBOARD_FILE")
  fi
  echo "+ ${cmd[*]}"
  "${cmd[@]}"
}

if $DO_ONBOARD; then
  echo "Running dlt-meta onboard"
  # Try to run onboard with file if provided; otherwise run interactive onboard
  if [ -n "$ONBOARD_FILE" ] && [ -f "$ONBOARD_FILE" ]; then
    run_cli onboard || run_cli onboard
  else
    run_cli onboard || true
  fi
fi

if $DO_DEPLOY; then
  echo "Running dlt-meta deploy"
  if [ -n "$ONBOARD_FILE" ] && [ -f "$ONBOARD_FILE" ]; then
    run_cli deploy || run_cli deploy
  else
    run_cli deploy || true
  fi
fi

echo "Done."
