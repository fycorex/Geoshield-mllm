# Manifest Schema

Required columns:

- `item_id`: stable unique id within the manifest, non-null.
- `dataset_name`: source dataset family, non-null.
- `subset_name`: frozen subset name, non-null.
- `split_name`: source split or `unspecified`, non-null.
- `image_path`: local relative path or cache path, optional when `drive_path` is present.
- `drive_path`: Drive artifact path, optional when `image_path` is present.
- `latitude`: ground-truth latitude in decimal degrees, non-null.
- `longitude`: ground-truth longitude in decimal degrees, non-null.
- `tags`: pipe-separated or JSON-list tags from the allowed tag set, optional.

Optional columns:

- `city`
- `region`
- `country`
- `source_id`
- `license`
- `sha256`
- `width`
- `height`
- `notes`

At least one of `image_path` or `drive_path` must be present. Coordinates must be valid WGS84 latitude/longitude values.

