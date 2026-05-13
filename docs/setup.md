# Setup

## Python

Preferred local workflow in this workspace uses the existing conda environment:

```bash
/home/ubuntu/miniconda3/bin/conda activate geoshield
PYTHONPATH=src python -m unittest discover -s tests
```

If creating a fresh environment:

```bash
conda create -n geoshield-mllm python=3.11
conda activate geoshield-mllm
pip install -e ".[dev,providers]"
pytest
```

The repository targets Python 3.11+, but the current `/home/ubuntu/miniconda3/envs/geoshield` environment is Python 3.10 and is sufficient for the initial pure-unit scaffold validation.

## Environment

Copy `.env.example` to `.env` and fill only the credentials needed for a run. Never commit `.env`, OAuth tokens, or service account JSON.

## Google Drive OAuth

Create an OAuth desktop client in Google Cloud, download the client secrets as `credentials.json`, and set `GOOGLE_DRIVE_OAUTH_CLIENT_SECRETS=credentials.json`. The backend can run the installed-app OAuth flow when credentials are available.

## Service Account

Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON path. Share the target Drive folder with the service account email or use an appropriate shared drive setup. Service account quota and ownership behavior depends on the Google Workspace/Drive configuration, so confirm the target deployment before large uploads.

## GitHub CLI

```bash
gh auth login
gh repo view fycorex/Geoshield-mllm
```

If the token is expired, run `gh auth login -h github.com` again.

## Common Failures

- `invalid_grant`: delete the local OAuth token and reauthenticate.
- `403 insufficientFilePermissions`: share the Drive folder with the authenticated principal.
- `404 file not found`: check whether the folder lives in My Drive vs a shared drive.
- Provider API parse failure: preserve raw response and inspect normalized parse error fields.
