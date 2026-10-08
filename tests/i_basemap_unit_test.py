"""Offline tests of i.basemap helpers: zoom choice, URL filling, server table."""

import importlib.util
import math
import string
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "i.basemap.py"
spec = importlib.util.spec_from_file_location("i_basemap", SCRIPT)
ib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ib)


def test_tile_resolution_at_equator():
    """Zoom 0 is one 256-pixel tile around the equator."""
    assert ib.tile_ground_resolution(0, 0) == pytest.approx(156543.03, rel=1e-6)


@pytest.mark.parametrize(
    ("res", "lat", "expected"),
    [
        (30.0, 32.0, 13),  # Landsat-like resolution
        (2.0, 32.2, 16),  # 2.02 m at zoom 16 is within the 5 % tolerance
        (0.5, 32.2, 18),
        (0.3, 48.0, 19),
        (1000.0, 0.0, 8),
    ],
)
def test_choose_zoom_matches_resolution(res, lat, expected):
    zoom, capped = ib.choose_zoom(res, lat, 20)
    assert zoom == expected
    assert not capped
    assert ib.tile_ground_resolution(zoom, lat) <= res * ib.ZOOM_TOLERANCE
    assert ib.tile_ground_resolution(zoom - 1, lat) > res * ib.ZOOM_TOLERANCE


def test_choose_zoom_is_capped_by_server():
    """A 0.5 m region on a server stopping at 16 gets 16, flagged as capped."""
    assert ib.choose_zoom(0.5, 32.2, 16) == (16, True)


def test_format_tile_url_fills_every_placeholder():
    url = ib.format_tile_url(
        "https://tile-{s}.example.org/{z}/{x}/{y}.png?key={api_key}", 5, 7, 4, "K"
    )
    assert url in {
        f"https://tile-{s}.example.org/4/5/7.png?key=K" for s in "abc"
    }


def test_format_tile_url_quadkey():
    """Bing quadkey of tile (3, 5) at zoom 3."""
    url = ib.format_tile_url("https://ecn.t3.tiles.virtualearth.net/tiles/a{quadkey}.jpeg", 3, 5, 3)
    assert url.endswith("/a213.jpeg")


def test_server_templates_use_known_fields_only():
    known = {"x", "y", "z", "s", "api_key", "quadkey"}
    for name, server in ib.WEB_MAP_SERVERS.items():
        fields = {f for _, f, _, _ in string.Formatter().parse(server["url"]) if f}
        assert fields <= known, name
        assert 0 <= server["max_zoom"] <= 20, name


def test_servers_are_distinct():
    """No server is another one under a different name."""
    urls = [server["url"] for server in ib.WEB_MAP_SERVERS.values()]
    assert len(urls) == len(set(urls))


def test_parser_options_list_every_server():
    text = SCRIPT.read_text()
    line = next(l for l in text.splitlines() if l.startswith("#% options: Google_Satellite"))
    assert set(line.split(": ", 1)[1].split(",")) == set(ib.WEB_MAP_SERVERS)


def test_zoom_tolerance_keeps_mid_latitude_2m_at_16():
    """The tolerance exists for this case: 2.02 m pixels for a 2 m region."""
    assert 2.0 < ib.tile_ground_resolution(16, 32.2) < 2.0 * ib.ZOOM_TOLERANCE
    assert math.isclose(ib.tile_ground_resolution(17, 32.2) * 2,
                        ib.tile_ground_resolution(16, 32.2))
