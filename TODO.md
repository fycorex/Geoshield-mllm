# TODO

## Now

- [x] Bootstrap repository structure, docs, configs, package, and tests.
- [x] Add dry-run storage, provider normalization, metrics, reporting, and CLI foundations.
- [ ] Authenticate `gh` before pushing to GitHub.
- [ ] Add real dataset source paths and freeze first pilot manifests.

## Next

- [ ] Implement real GeoShield fork integration or a reproducible wrapper around `fycorex/geoshield`.
- [ ] Add credential-backed smoke tests for Google Drive in a private environment.
- [ ] Add TechUtopia, optional first-party OpenAI, Gemini, Anthropic, and DashScope live provider smoke tests with tiny budgets.
- [ ] Generate the first `gsv_100_pilot` and `im2gps3k_100_pilot` manifests.

## Later

- [ ] Run `pilot_baseline_techutopia`.
- [ ] Run `pilot_cross_provider`.
- [ ] Run `main_budget_sweep` at or below 1000 total images.
- [ ] Use measured failure modes to design MLLM-aware defenses.
