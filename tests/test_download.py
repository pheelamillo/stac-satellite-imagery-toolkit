from unittest.mock import MagicMock

from imagery_ingest_kit.download import download_item_assets, local_path_for


def _fake_item():
    item = MagicMock()
    item.id = "scene-1"
    item.collection_id = "sentinel-2-l2a"
    item.assets = {
        "visual": MagicMock(href="https://example.com/data/scene-1_visual.tif"),
    }
    return item


def test_local_path_for(tmp_path):
    item = _fake_item()
    path = local_path_for(item, tmp_path)
    assert path == tmp_path / "sentinel-2-l2a" / "scene-1"


def test_download_item_assets_skips_missing_keys(tmp_path):
    item = _fake_item()
    session = MagicMock()
    resp = MagicMock()
    resp.__enter__.return_value = resp
    resp.raise_for_status.return_value = None
    resp.raw.read.side_effect = [b"fake-bytes", b""]
    session.get.return_value = resp

    saved = download_item_assets(
        item, tmp_path, asset_keys=("visual", "nonexistent"), session=session
    )

    assert len(saved) == 1
    assert saved[0].name == "scene-1_visual.tif"
