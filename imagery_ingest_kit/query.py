"""Query STAC catalogs for optical satellite imagery."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, Sequence

from pystac import Item
from pystac_client import Client

DEFAULT_STAC_API = "https://earth-search.aws.element84.com/v1"


@dataclass
class SceneQuery:
    """Parameters for a STAC scene search."""

    collections: Sequence[str]
    bbox: Sequence[float]
    start_date: str
    end_date: str
    max_cloud_cover: float = 20.0
    max_items: Optional[int] = None


def search_scenes(query: SceneQuery, stac_api_url: str = DEFAULT_STAC_API) -> Iterator[Item]:
    """Search a STAC API for scenes matching the given query.

    Parameters
    ----------
    query:
        Search parameters (collections, bounding box, date range, cloud cover).
    stac_api_url:
        Root URL of the STAC API to query. Defaults to the public Element84
        Earth Search API, which indexes Landsat Collection 2 and Sentinel-2 L2A.

    Yields
    ------
    pystac.Item
        Matching STAC items.
    """
    client = Client.open(stac_api_url)
    search = client.search(
        collections=list(query.collections),
        bbox=list(query.bbox),
        datetime=f"{query.start_date}/{query.end_date}",
        query={"eo:cloud_cover": {"lt": query.max_cloud_cover}},
        max_items=query.max_items,
    )
    yield from search.items()


def summarize_item(item: Item) -> dict:
    """Return a small, JSON-serializable summary of a STAC item."""
    return {
        "id": item.id,
        "datetime": item.datetime.isoformat() if item.datetime else None,
        "cloud_cover": item.properties.get("eo:cloud_cover"),
        "collection": item.collection_id,
        "assets": sorted(item.assets.keys()),
    }
