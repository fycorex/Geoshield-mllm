# Setup

## Python

Preferred local workflow in this workspace uses the existing conda environment:

```bash
PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield-mllm/bin/python -m unittest discover -s tests
```

If creating a fresh environment:

```bash
export PATH="$HOME/miniconda3/bin:$PATH"
conda create -n geoshield-mllm python=3.11
conda run -n geoshield-mllm python -m pip install -U pip setuptools wheel
conda run -n geoshield-mllm python -m pip install -e ".[dev,providers]"
conda run -n geoshield-mllm python -m pytest
```

If `conda` is not on PATH, either use `/home/ubuntu/miniconda3/bin/conda` directly or run `export PATH="$HOME/miniconda3/bin:$PATH"` first.

The repository targets Python 3.11+. The current dedicated environment is `/home/ubuntu/miniconda3/envs/geoshield-mllm`.

The repository includes a small `setup.py` compatibility shim so older pip/setuptools combinations can perform editable installs when PEP 660 editable support is unavailable.

## Environment

Copy `.env.example` to `.env` and fill only the credentials needed for a run. Never commit `.env`, OAuth tokens, or service account JSON.

For TechUtopia, use a real API key and keep `TECHUTOPIA_BASE_URL=https://copilot.techutopia.cn/v1`. Optional provider-approved request headers can be supplied through `TECHUTOPIA_EXTRA_HEADERS_JSON`. Do not use fake browser impersonation to bypass access controls; blocked requests should be recorded and resolved through valid credentials, endpoint configuration, or provider support.

## Google Drive OAuth

Create an OAuth desktop client in Google Cloud, download the client secrets as `credentials.json`, and set `GOOGLE_DRIVE_OAUTH_CLIENT_SECRETS=credentials.json`. The backend can run the installed-app OAuth flow when credentials are available.

Run:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli drive-smoke-test \
  --auth-mode oauth \
  --oauth-client-secrets credentials.json
```

## Service Account

Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON path. Share the target Drive folder with the service account email or use an appropriate shared drive setup. Service account quota and ownership behavior depends on the Google Workspace/Drive configuration, so confirm the target deployment before large uploads.

Run:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli drive-smoke-test --auth-mode service-account
```

## GitHub CLI

```bash
gh auth login
gh repo view fycorex/Geoshield-mllm
```

If the token is expired, run `gh auth login -h github.com` again.

## Exact GSV/GSC Dataset

GeoShield's Street View benchmark must use the exact Location-Inference Google Street View dataset, not a random Street View proxy. The source repository is `https://github.com/njspyx/location-inference`.

The upstream README lists a `gdown` folder download for the dataset. The user explicitly permitted this official Drive-hosted dataset source on 2026-05-14. Install dataset helpers and download into ignored local storage:

```bash
conda run -n geoshield-mllm python -m pip install ".[datasets]"
conda run -n geoshield-mllm python scripts/download_exact_gsv.py
```

After download, extract `imgs_final.zip` if needed and generate `manifests/gsv_100_pilot.csv` only from that exact source:

```bash
unzip -q -o data/raw/location_inference_gsv/imgs_final.zip -d data/raw/location_inference_gsv
conda run -n geoshield-mllm python -m geoshield_mllm.cli prepare-dataset \
  configs/datasets/gsv_100_pilot.yaml \
  --availability-report docs/dataset_availability.md
```

## Common Failures

- `invalid_grant`: delete the local OAuth token and reauthenticate.
- `403 insufficientFilePermissions`: share the Drive folder with the authenticated principal.
- `404 file not found`: check whether the folder lives in My Drive vs a shared drive.
- Provider API parse failure: preserve raw response and inspect normalized parse error fields.
