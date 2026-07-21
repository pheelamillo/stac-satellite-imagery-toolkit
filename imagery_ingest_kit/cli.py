"""Command-line interface for imagery-ingest-kit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from .download import download_item_assets
from .query import DEFAULT_STAC_API, SceneQuery, search_scenes, summarize_item


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imagery-ingest-kit",
        description=(
            "Query a STAC API for optical satellite imagery and optionally "
            "download matching assets."
        ),
    )
    parser.add_argument(
        "--collection",
        action="append",
        dest="collections",
        required=True,
        help="STAC collection ID to search (repeatable), e.g. sentinel-2-l2a",
    )
    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("MINX", "MINY", "MAXX", "MAXY"),
        required=True,
        help="Bounding box in WGS84 degrees",
    )
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD")
    parser.add_argument("--max-cloud-cover", type=float, default=20.0)
    parser.add_argument("--max-items", type=int, default=10)
    parser.add_argument("--stac-api", default=DEFAULT_STAC_API)
    parser.add_argument(
        "--download-to",
        type=Path,
        default=None,
        help="If set, download matching assets under this directory",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    query = SceneQuery(
        collections=args.collections,
        bbox=args.bbox,
        start_date=args.start,
        end_date=args.end,
        max_cloud_cover=args.max_cloud_cover,
        max_items=args.max_items,
    )
    items = list(search_scenes(query, stac_api_url=args.stac_api))
    print(json.dumps([summarize_item(i) for i in items], indent=2))

    if args.download_to is not None:
        for item in items:
            saved = download_item_assets(item, args.download_to)
            for path in saved:
                print(f"saved: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
