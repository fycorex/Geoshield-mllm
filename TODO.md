# TODO

## Now

- [x] Bootstrap repository structure, docs, configs, package, and tests.
- [x] Add dry-run storage, provider normalization, metrics, reporting, and CLI foundations.
- [x] Download ignored local pilot data and freeze `gsv_100_pilot`.
- [x] Download official IM2GPS3K images/metadata and freeze `im2gps3k_100_pilot`.
- [ ] Authenticate `gh` before pushing to GitHub.
- [ ] Implement 2-5 image TechUtopia smoke eval on `im2gps3k_100_pilot`.
- [ ] Acquire or reconstruct a paper-matching GSV benchmark before paper-aligned Street View claims.

## Next

- [ ] Implement real GeoShield fork integration or a reproducible wrapper around `fycorex/geoshield`.
- [ ] Add credential-backed smoke tests for Google Drive in a private environment.
- [ ] Add TechUtopia, optional first-party OpenAI, Gemini, Anthropic, and DashScope live provider smoke tests with tiny budgets.
- [x] Generate the first `gsv_100_pilot` and `im2gps3k_100_pilot` manifests.

## Later

- [ ] Run `pilot_baseline_techutopia`.
- [ ] Run `pilot_cross_provider`.
- [ ] Run `main_budget_sweep` at or below 1000 total images.
- [ ] Use measured failure modes to design MLLM-aware defenses.
