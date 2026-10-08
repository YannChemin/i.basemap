## DESCRIPTION

*i.basemap* downloads base map tiles from public web map servers for the
current computational region and imports them as raster maps. The tiles
are mosaicked, reprojected from Web Mercator to the project's coordinate
reference system and resampled to the computational region.

The **server** option selects one of 20 predefined servers (list them with
**-l**); **url** gives a custom XYZ or quadkey template instead.

### Servers

| Server | Max zoom | Content |
|---|---|---|
| Google_Satellite | 20 | Google satellite and aerial imagery |
| Google_Hybrid | 20 | Google imagery with labels and roads |
| Google_Terrain | 15 | Google terrain map |
| ESRI_WorldImagery | 19 | ESRI World Imagery |
| Bing_Aerial | 19 | Microsoft Bing aerial imagery (quadkey) |
| Bing_Roads | 19 | Microsoft Bing road map (quadkey) |
| OpenStreetMap | 19 | OpenStreetMap standard style |
| OSM_Humanitarian | 20 | OpenStreetMap humanitarian style |
| OpenTopoMap | 17 | Topographic map from OpenStreetMap and SRTM |
| Natural_Earth | 16 | ESRI National Geographic world map |
| Stamen_Terrain | 18 | Stamen terrain, hosted by Stadia Maps (**api_key** required) |
| Stamen_Toner | 20 | Stamen toner, hosted by Stadia Maps (**api_key** required) |
| Stamen_Watercolor | 16 | Stamen watercolor, hosted by Stadia Maps (**api_key** required) |
| USGS_Topo | 16 | USGS topographic map (United States) |
| USGS_NAIP | 16 | USGS Imagery Only basemap, NAIP orthoimagery (United States) |
| USGS_3DEP | 13 | USGS 3DEP shaded relief, a rendering, not elevation values |
| USGS_Hydro | 16 | USGS hydrography (United States) |
| Copernicus_Sentinel | 15 | Sentinel-2 cloudless 2023 mosaic by EOX (CC BY-NC-SA 4.0) |
| Landsat | 12 | Landsat WELD annual true colour, NASA GIBS |
| MODIS | 8 | Blue Marble Next Generation, MODIS composite, NASA GIBS |

Each server has its own terms of use and attribution requirements; the
user is responsible for respecting them.

### Zoom level

With **zoom**=*auto* (the default), the zoom level is the coarsest one
whose tile pixel is no larger than the region resolution (with a 5 %
tolerance, so that a 2 m region at mid latitudes uses zoom 16, whose
pixels are about 2.0 m). It is capped at the server's highest level, with a
warning when the region is finer than the server can deliver. A number
from 0 to 20 forces the zoom level; a level above the server's highest one
is an error.

A Web Mercator tile pixel at zoom *z* and latitude *φ* covers
40,075,017 · cos *φ* / (256 · 2^*z*) m: about 2.0 m at zoom 16 and 0.5 m
at zoom 18 at 32° N.

### Output

By default the red, green and blue bands are combined by *r.composite*.
With **-b** the bands are kept as separate maps. Areas without tiles are
NULL; black pixels are kept.

## NOTES

The region extent is converted to WGS 84 with *g.region* **-b**, so any
projected or geographic coordinate reference system selects the right
tiles. Tiles are downloaded with *curl* in random order, with a
descriptive User-Agent and up to three attempts per tile; HTTP errors are
treated as failed tiles. Each tile is georeferenced by a world file whose
origin is the centre of its upper-left pixel, mosaicked into a virtual
raster with an alpha band, and imported with *r.import*.

More than 2,500 tiles trigger a warning: tile servers limit bulk
downloads. A smaller region or a lower zoom level reduces the number of
tiles by four per level.

Template fields for **url**: `{x}`, `{y}`, `{z}`, `{quadkey}`, `{s}` (a
subdomain, a, b or c) and `{api_key}`.

## EXAMPLES

List the servers:

```sh
i.basemap -l
```

Aerial imagery at 0.5 m (zoom 18) for the current region:

```sh
g.region n=3558300 s=3557300 w=515000 e=516000 res=0.5
i.basemap server=Google_Satellite output=aerial
```

A fixed zoom level and separate bands:

```sh
i.basemap server=ESRI_WorldImagery output=esri zoom=17 -b
```

A server requiring an API key:

```sh
i.basemap server=Stamen_Terrain output=terrain api_key=MY_STADIA_KEY
```

A custom XYZ template:

```sh
i.basemap url="https://tile.example.org/{z}/{x}/{y}.png" output=custom
```

## SEE ALSO

*[r.composite](https://grass.osgeo.org/grass-stable/manuals/r.composite.html),
[r.import](https://grass.osgeo.org/grass-stable/manuals/r.import.html),
[r.in.wms](https://grass.osgeo.org/grass-stable/manuals/r.in.wms.html)*

## AUTHORS

Yann Chemin
