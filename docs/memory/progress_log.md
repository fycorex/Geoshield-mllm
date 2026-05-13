# Progress Log

## 2026-05-13T00:00:00Z

Summary: Began repository bootstrap for Geoshield-mllm. Confirmed local repo has no commits and `origin` points to `https://github.com/fycorex/Geoshield-mllm`. `gh` authentication is present but invalid.

Files changed: initial docs, configs, package scaffold, tests, and repo metadata.

Tests run: pending during bootstrap.

## 2026-05-13T00:20:00Z

Summary: Switched local validation guidance to the existing conda environment at `/home/ubuntu/miniconda3/envs/geoshield`. Network package installation is restricted, so tests were made runnable with standard `unittest` while remaining pytest-compatible.

Files changed: `docs/setup.md`, `README.md`, tests, memory docs.

Tests run: `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T00:05:00Z

Summary: Corrected provider assumptions after user clarification. GPT-4o and GPT-5 mini are now configured under TechUtopia OpenAI-compatible access at `https://copilot.techutopia.cn/v1`; first-party OpenAI remains optional.

Files changed: `.env.example`, eval configs, README, experiment protocol, TODO, memory docs.

Tests run: pending during bootstrap.
