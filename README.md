# i.basemap - GRASS GIS web basemap import

*i.basemap* downloads tiles from public web map servers for the current
computational region and imports them as raster maps, reprojected to the
project's coordinate reference system. See `i.basemap.md` for the manual.

## Servers

20 predefined servers (`i.basemap -l`), plus custom XYZ or quadkey
templates with `url=`:

| Server | Max zoom | Content |
|---|---|---|
| Google_Satellite / Google_Hybrid / Google_Terrain | 20 / 20 / 15 | Google imagery, hybrid, terrain |
| ESRI_WorldImagery | 19 | ESRI World Imagery |
| Bing_Aerial / Bing_Roads | 19 | Microsoft Bing (quadkey) |
| OpenStreetMap / OSM_Humanitarian / OpenTopoMap | 19 / 20 / 17 | OpenStreetMap styles |
| Natural_Earth | 16 | ESRI National Geographic world map |
| Stamen_Terrain / Stamen_Toner / Stamen_Watercolor | 18 / 20 / 16 | Stamen styles on Stadia Maps (`api_key=` required) |
| USGS_Topo / USGS_Hydro | 16 | USGS topographic map, hydrography (US) |
| USGS_NAIP | 16 | USGS Imagery Only basemap, NAIP orthoimagery (US) |
| USGS_3DEP | 13 | USGS 3DEP shaded relief (a rendering, not elevations) |
| Copernicus_Sentinel | 15 | Sentinel-2 cloudless 2023, EOX (CC BY-NC-SA 4.0) |
| Landsat | 12 | Landsat WELD annual true colour, NASA GIBS |
| MODIS | 8 | Blue Marble Next Generation (MODIS composite), NASA GIBS |

## Usage

```sh
i.basemap -l                                         # list the servers
g.region n=3558300 s=3557300 w=515000 e=516000 res=0.5
i.basemap server=Google_Satellite output=aerial      # zoom=auto picks 18 (0.5 m)
i.basemap server=ESRI_WorldImagery output=esri zoom=17 -b
i.basemap server=Stamen_Terrain output=terrain api_key=MY_STADIA_KEY
```

`zoom=auto` (default) picks the coarsest zoom whose tile pixel matches the
region resolution, capped at the server's highest level. Output follows the
computational region; `-b` keeps separate bands instead of the
*r.composite* result. `maxcols`, `maxrows` and `srs` are not used by the
XYZ and quadkey servers.

## Changes on 2026-10-08

- `zoom=` option, and zoom selection from the region resolution (it was a
  fixed table that never went above 16).
- `api_key=` option and `{api_key}` / `{s}` template fields. The Stamen and
  OSM_Humanitarian templates used to crash on the unfilled `{s}`.
- Tile world files now give the centre of the upper-left pixel. They gave
  its corner, which shifted every mosaic by half a tile pixel to the west
  and north (about 1.2 m at zoom 16).
- Server table: Stamen moved to Stadia Maps. USGS_NAIP and USGS_3DEP (dead
  services, 404) were replaced by the USGS Imagery Only and Shaded Relief
  basemaps. Copernicus_Sentinel, Landsat and MODIS, which served Google or
  ESRI imagery, now serve EOX Sentinel-2 cloudless and NASA GIBS products.
  ESA_WorldCover (Google imagery) and NOAA_Climate, ESA_Climate, WorldBank
  and UN_GeoWeb (all OpenStreetMap) were removed.
- Warning above 2,500 tiles. Metadata (`r.support`) is now written to the
  maps actually produced (`.r/.g/.b`, bands or composite).

## Tests

```sh
PYTHONPATH=$(grass --config python_path) python3 -m pytest tests/
```

`tests/i_basemap_unit_test.py` runs offline. `tests/i_basemap_test.py`
downloads tiles and is skipped without network access.

## Dependencies

GRASS GIS 8.5+, curl, GDAL (Python bindings and `gdalbuildvrt`).

## License

Copyright (C) 2025 by the GRASS Development Team

This program is free software under the GNU General Public License (>=v2).
Read the file COPYING that comes with GRASS for details.
