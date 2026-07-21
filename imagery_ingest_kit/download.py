"""Download and normalize STAC item assets to a local directory structure."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional, Sequence

import requests
from pystac import Item

DEFAULT_ASSET_KEYS = ("visual", "thumbnail")


def local_path_for(item: Item, root) -> Path:
    """Compute the local directory an item's assets should be saved under.

    Layout: {root}/{collection}/{item_id}/
    """
    collection = item.collection_id or "unknown-collection"
    return Path(root) / collection / item.id


def download_item_assets(
    item: Item,
    root,
    asset_keys: Sequence[str] = DEFAULT_ASSET_KEYS,
    session: Optional[requests.Session] = None,
) -> List[Path]:
    """Download the requested assets for a single STAC item.

    Only assets present on the item are downloaded; missing keys are skipped
    rather than raising, since asset naming varies across collections and
    providers.
    """
    session = session or requests.Session()
    out_dir = local_path_for(item, root)
    out_dir.mkdir(parents=True, exist_ok=True)

    saved: List[Path] = []
    for key in asset_keys:
        asset = item.assets.get(key)
        if asset is None:
            continue
        dest = out_dir / Path(asset.href).name
        _download_to(session, asset.href, dest)
        saved.append(dest)
    return saved


def _download_to(session: requests.Session, url: str, dest: Path) -> None:
    with session.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp.raw, f)
