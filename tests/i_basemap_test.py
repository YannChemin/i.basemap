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
