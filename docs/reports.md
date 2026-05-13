# Reports

Each run report contains objective, exact configs, dataset summary, model summary, attack settings, prompt version, geocoder backend, storage paths, main metrics, subgroup metrics, qualitative failure cases, parsing/refusal/error notes, and interpretation notes.

## Files

- `run_card.json`: machine-readable run metadata.
- `run_card.md`: human-readable run metadata.
- `summary.json`: aggregate metrics.
- `docs/results/<run_id>/README.md`: run report.
- `docs/results/index.md`: result index.
- `docs/results/latest.md`: pointer or copy of the latest run summary.

## Metrics

Distance uses haversine kilometers. Threshold accuracies are computed at 1 km, 25 km, 200 km, 750 km, and 2500 km. Parse success, refusal, and geocode fallback rates are reported for every provider/model where possible.

## Subgroups

Break down metrics by dataset, tag, provider, model, and clean/protected variant. Do not hide subgroups with high parse failure; report the failure rate next to accuracy.

## Failure Cases

Qualitative sections should include representative successes and failures with item ids, ground truth metadata, predicted location text, distance, tags, and artifact paths. Do not include large images directly in git.

## Index Updates

After generating a run report, add an entry to `docs/results/index.md` and update `docs/results/latest.md` to point to the newest run.

