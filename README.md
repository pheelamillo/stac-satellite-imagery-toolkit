# imagery-ingest-kit

Utilities for ingesting STAC-cataloged satellite imagery into geospatial processing workflows. Provides a small Python library and CLI for querying STAC APIs, filtering optical scenes (e.g. Landsat, Sentinel-2) by bounding box, date range, and cloud cover, and downloading matching assets into a consistent local directory layout.

## Status

Early stage. The core query and download paths are implemented and unit tested; the interface may still change.

## Install

```bash
pip install -r requirements.txt
```

## Usage

As a library:

```python
from imagery_ingest_kit import SceneQuery, search_scenes, summarize_item

query = SceneQuery(
    collections=["sentinel-2-l2a"],
    bbox=[-162.6, 66.0, -162.3, 66.3],
    start_date="2024-06-01",
    end_date="2024-08-31",
    max_cloud_cover=20.0,
    max_items=10,
)

for item in search_scenes(query):
    print(summarize_item(item))
```

From the command line:

```bash
python -m imagery_ingest_kit.cli \
    --collection sentinel-2-l2a \
    --bbox -162.6 66.0 -162.3 66.3 \
    --start 2024-06-01 \
    --end 2024-08-31 \
    --max-cloud-cover 20 \
    --download-to ./data
```

By default, queries run against the public [Element84 Earth Search](https://earth-search.aws.element84.com/v1) STAC API, which indexes Landsat Collection 2 and Sentinel-2 L2A. A different STAC API can be supplied with `--stac-api` / `stac_api_url`.

Downloaded assets are saved under `{root}/{collection}/{item_id}/`, so a Sentinel-2 scene lands at e.g. `data/sentinel-2-l2a/S2A_.../visual.tif`.

## Development

```bash
pip install -r requirements.txt pytest
pytest
```

Tests run fully offline against mocked STAC/HTTP responses.

## License

GPL-3.0 — see LICENSE.
