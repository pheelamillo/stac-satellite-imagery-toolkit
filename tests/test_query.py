from unittest.mock import MagicMock, patch

from imagery_ingest_kit.query import SceneQuery, search_scenes, summarize_item


def _fake_item(item_id="scene-1", cloud_cover=5.0):
    item = MagicMock()
    item.id = item_id
    item.datetime = None
    item.collection_id = "sentinel-2-l2a"
    item.properties = {"eo:cloud_cover": cloud_cover}
    item.assets = {"visual": MagicMock(href="https://example.com/visual.tif")}
    return item


@patch("imagery_ingest_kit.query.Client")
def test_search_scenes_builds_expected_query(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.open.return_value = mock_client
    mock_search = MagicMock()
    mock_search.items.return_value = iter([_fake_item()])
    mock_client.search.return_value = mock_search

    query = SceneQuery(
        collections=["sentinel-2-l2a"],
        bbox=[-162.6, 66.0, -162.3, 66.3],
        start_date="2024-06-01",
        end_date="2024-08-31",
        max_cloud_cover=20.0,
        max_items=5,
    )
    results = list(search_scenes(query, stac_api_url="https://example.com/stac"))

    mock_client_cls.open.assert_called_once_with("https://example.com/stac")
    mock_client.search.assert_called_once_with(
        collections=["sentinel-2-l2a"],
        bbox=[-162.6, 66.0, -162.3, 66.3],
        datetime="2024-06-01/2024-08-31",
        query={"eo:cloud_cover": {"lt": 20.0}},
        max_items=5,
    )
    assert len(results) == 1
    assert results[0].id == "scene-1"


def test_summarize_item():
    item = _fake_item(cloud_cover=12.5)
    summary = summarize_item(item)
    assert summary == {
        "id": "scene-1",
        "datetime": None,
        "cloud_cover": 12.5,
        "collection": "sentinel-2-l2a",
        "assets": ["visual"],
    }
