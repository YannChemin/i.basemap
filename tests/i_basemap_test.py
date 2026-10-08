"""Tests of i.basemap in projected, non-UTM projects.

These tests download a few XYZ tiles and are skipped without network access.
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

import grass.script as gs

SCRIPT = Path(__file__).resolve().parents[1] / "i.basemap.py"


def _online(host="mt1.google.com", port=443):
    try:
        socket.create_connection((host, port), timeout=5).close()
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not _online(), reason="needs network access")


@pytest.fixture
def lambert93_session(tmp_path):
    """Temporary project in RGF93 / Lambert-93 (EPSG:2154), not UTM."""
    project = tmp_path / "l93"
    gs.create_project(project, epsg="2154")
    with gs.setup.init(project, env=os.environ.copy()) as session:
        # 500 m x 500 m over the Chateaudun runway (48.056 N, 1.375 E).
        gs.run_command(
            "g.region", n=6774500, s=6774000, e=579300, w=578800, res=1,
            env=session.env,
        )
        yield session


def run_basemap(session, **kwargs):
    args = [sys.executable, str(SCRIPT), "-c"]
    args += [f"{key}={value}" for key, value in kwargs.items()]
    subprocess.run(args, check=True, env=session.env, capture_output=True)


@pytest.mark.parametrize("server", ["Google_Satellite", "OpenStreetMap"])
def test_lambert93_region_is_fully_covered(lambert93_session, server):
    """Tiles must be fetched for the region, not for its coordinates misread
    as Web Mercator, and neither black pixels nor palette indices may turn
    into NULL."""
    run_basemap(lambert93_session, server=server, output="bm")
    for band in ("r", "g", "b"):
        stats = gs.parse_command(
            "r.univar", map=f"bm.{band}", flags="g", env=lambert93_session.env
        )
        assert int(stats["null_cells"]) == 0
        assert int(stats["n"]) == 500 * 500
        assert float(stats["max"]) > float(stats["min"])


def run_basemap_result(session, **kwargs):
    args = [sys.executable, str(SCRIPT), "-c"]
    args += [f"{key}={value}" for key, value in kwargs.items()]
    return subprocess.run(args, env=session.env, capture_output=True, text=True)


def test_auto_zoom_follows_region_resolution(lambert93_session):
    """A 0.5 m region gets zoom 18 tiles, not the former fixed maximum of 16."""
    gs.run_command("g.region", res=0.5, env=lambert93_session.env)
    result = run_basemap_result(lambert93_session, server="Google_Satellite", output="bm")
    assert result.returncode == 0, result.stderr
    assert "zoom level 18" in result.stderr


def test_zoom_above_server_maximum_fails(lambert93_session):
    result = run_basemap_result(lambert93_session, server="USGS_3DEP", output="bm", zoom=16)
    assert result.returncode != 0
    assert "highest level" in result.stderr


def test_api_key_is_required(lambert93_session):
    result = run_basemap_result(lambert93_session, server="Stamen_Toner", output="bm")
    assert result.returncode != 0
    assert "api_key" in result.stderr


@pytest.mark.parametrize(
    "server", ["OSM_Humanitarian", "Copernicus_Sentinel", "Landsat", "MODIS"]
)
def test_replaced_servers_download(lambert93_session, server):
    """Servers whose templates were broken or mislabelled now deliver tiles."""
    gs.run_command("g.region", res=100, flags="a", env=lambert93_session.env)
    result = run_basemap_result(lambert93_session, server=server, output="bm")
    assert result.returncode == 0, result.stderr
    stats = gs.parse_command("r.univar", map="bm.r", flags="g", env=lambert93_session.env)
    assert int(stats["n"]) > 0
