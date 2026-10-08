#!/usr/bin/env python3

# i.basemap - GRASS GIS addon for importing web map basemaps
# Copyright (C) 2024 GRASS Development Team
# Author: Your Name <your.email@example.com>
# Purpose: Import basemaps from various web map services
# Keywords: raster, import, web, basemap

#%module
#% description: Import basemaps from various web map services
#% keyword: raster
#% keyword: import
#% keyword: web
#% keyword: basemap
#%end

#%option G_OPT_F_OUTPUT
#% key: output
#% type: string
#% required: yes
#% description: Name for output raster map(s)
#%end

#%option
#% key: server
#% type: string
#% required: no
#% options: Google_Satellite,OpenStreetMap,Bing_Aerial,ESRI_WorldImagery,USGS_Topo,Google_Terrain,Google_Hybrid,Bing_Roads,Stamen_Terrain,Stamen_Toner,Stamen_Watercolor,OpenTopoMap,OSM_Humanitarian,Natural_Earth,USGS_NAIP,USGS_3DEP,USGS_Hydro,Copernicus_Sentinel,Landsat,MODIS
#% answer: OpenStreetMap
#% description: Web map server to use
#%end

#%option
#% key: url
#% type: string
#% required: no
#% description: Custom URL template for XYZ tiles (use {x}, {y}, {z} or {quadkey})
#%end

#%option
#% key: maxcols
#% type: integer
#% required: no
#% answer: 1024
#% description: Maximum width of output map in pixels
#%end

#%option
#% key: maxrows
#% type: integer
#% required: no
#% answer: 1024
#% description: Maximum height of output map in pixels
#%end

#%option
#% key: srs
#% type: string
#% required: no
#% answer: EPSG:3857
#% description: Spatial reference system for the output
#%end

#%option
#% key: format
#% type: string
#% required: no
#% options: png,jpeg
#% answer: png
#% description: Output format for downloaded tiles
#%end

#%option
#% key: composite_levels
#% type: integer
#% required: no
#% options: 1-256
#% answer: 256
#% description: Number of color levels per RGB channel used by r.composite (256 = lossless for 8-bit imagery)
#%end

#%option
#% key: zoom
#% type: string
#% required: no
#% answer: auto
#% description: Tile zoom level (0-20), or auto to match the region resolution
#%end

#%option
#% key: api_key
#% type: string
#% required: no
#% description: API key for servers that require one (e.g. Stamen styles hosted by Stadia Maps)
#%end

#%flag
#% key: l
#% description: List available web map servers
#%end

#%flag
#% key: c
#% description: Use current computational region
#%end

#%flag
#% key: r
#% description: Reproject to current location's projection
#%end

#%flag
#% key: o
#% description: Overwrite existing maps
#%end

#%flag
#% key: b
#% description: Keep separate red/green/blue band maps instead of a single composite
#%end

import sys
import os
import math
import subprocess
import tempfile
import random
from osgeo import gdal

USER_AGENT = "i.basemap/1.1 (GRASS GIS addon; https://grass.osgeo.org)"

# Try to import grass.script
try:
    import grass.script as gs
    GRASS_AVAILABLE = True
except ImportError:
    GRASS_AVAILABLE = False
    gs = None

# Web map server configurations
WEB_MAP_SERVERS = {
    'Google_Satellite': {
        'name': 'Google Satellite',
        'url': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'type': 'xyz',
        'max_zoom': 20,
        'format': 'jpeg'
    },
    'OpenStreetMap': {
        'name': 'OpenStreetMap',
        'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        'type': 'xyz',
        'max_zoom': 19,
        'format': 'png'
    },
    'Bing_Aerial': {
        'name': 'Bing Aerial',
        'url': 'https://ecn.t3.tiles.virtualearth.net/tiles/a{quadkey}.jpeg?g=1',
        'type': 'quadkey',
        'max_zoom': 19,
        'format': 'jpeg'
    },
    'ESRI_WorldImagery': {
        'name': 'ESRI World Imagery',
        'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 19,
        'format': 'jpeg'
    },
    'USGS_Topo': {
        'name': 'USGS Topographic Maps',
        'url': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'png'
    },
    'Google_Terrain': {
        'name': 'Google Terrain',
        'url': 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
        'type': 'xyz',
        'max_zoom': 15,
        'format': 'png'
    },
    'Google_Hybrid': {
        'name': 'Google Hybrid',
        'url': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        'type': 'xyz',
        'max_zoom': 20,
        'format': 'jpeg'
    },
    'Bing_Roads': {
        'name': 'Bing Road Maps',
        'url': 'https://ecn.t3.tiles.virtualearth.net/tiles/r{quadkey}.png?g=1',
        'type': 'quadkey',
        'max_zoom': 19,
        'format': 'png'
    },
    'Stamen_Terrain': {
        'name': 'Stamen Terrain (Stadia Maps, API key required)',
        'url': 'https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png?api_key={api_key}',
        'type': 'xyz',
        'max_zoom': 18,
        'format': 'png'
    },
    'Stamen_Toner': {
        'name': 'Stamen Toner (Stadia Maps, API key required)',
        'url': 'https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}.png?api_key={api_key}',
        'type': 'xyz',
        'max_zoom': 20,
        'format': 'png'
    },
    'Stamen_Watercolor': {
        'name': 'Stamen Watercolor (Stadia Maps, API key required)',
        'url': 'https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg?api_key={api_key}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'jpeg'
    },
    'OpenTopoMap': {
        'name': 'OpenTopoMap',
        'url': 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
        'type': 'xyz',
        'max_zoom': 17,
        'format': 'png'
    },
    'OSM_Humanitarian': {
        'name': 'Humanitarian OpenStreetMap',
        'url': 'https://tile-{s}.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        'type': 'xyz',
        'max_zoom': 20,
        'format': 'png'
    },
    'Natural_Earth': {
        'name': 'National Geographic World Map',
        'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'png'
    },
    'USGS_NAIP': {
        'name': 'USGS Imagery Only (NAIP orthoimagery, United States)',
        'url': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'jpeg'
    },
    'USGS_3DEP': {
        'name': 'USGS 3DEP shaded relief (rendered, not elevation values)',
        'url': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSShadedReliefOnly/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 13,
        'format': 'jpeg'
    },
    'USGS_Hydro': {
        'name': 'USGS Hydrography',
        'url': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'png'
    },
    'Copernicus_Sentinel': {
        'name': 'Sentinel-2 cloudless 2023 (EOX, CC BY-NC-SA 4.0)',
        'url': 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2023_3857/default/g/{z}/{y}/{x}.jpg',
        'type': 'xyz',
        'max_zoom': 15,
        'format': 'jpeg'
    },
    'Landsat': {
        'name': 'Landsat WELD annual true colour (NASA GIBS)',
        'url': 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/Landsat_WELD_CorrectedReflectance_TrueColor_Global_Annual/default/default/GoogleMapsCompatible_Level12/{z}/{y}/{x}.jpg',
        'type': 'xyz',
        'max_zoom': 12,
        'format': 'jpeg'
    },
    'MODIS': {
        'name': 'Blue Marble Next Generation, MODIS composite (NASA GIBS)',
        'url': 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
        'type': 'xyz',
        'max_zoom': 8,
        'format': 'jpeg'
    }
}

def list_servers():
    """List all available web map servers"""
    gs.message("=" * 80)
    gs.message("Available Web Map Servers:")
    gs.message("=" * 80)
    for server_id, server_info in WEB_MAP_SERVERS.items():
        gs.message(f"  {server_id}: {server_info['name']}")
        gs.message(f"    URL: {server_info['url']}")
        gs.message(f"    Type: {server_info['type']}")
        gs.message(f"    Max Zoom: {server_info['max_zoom']}")
        gs.message(f"    Format: {server_info['format']}")
        gs.message("")
    gs.message("=" * 80)

def get_server_url(server_name, layer=None, api_key=None):
    """Get the appropriate URL for the server"""
    if server_name not in WEB_MAP_SERVERS:
        gs.fatal(f"Server '{server_name}' not found. Use -l flag to list available servers.")
    
    server = WEB_MAP_SERVERS[server_name]
    return server['url']

def xyz_to_quadkey(x, y, zoom):
    """Convert XYZ tile coordinates to Bing quadkey format"""
    quadkey = ""
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadkey += str(digit)
    return quadkey

EARTH_CIRCUMFERENCE = 2 * math.pi * 6378137.0
# Accept a tile ground pixel up to 5 % coarser than the region resolution,
# so that a 2 m region at mid latitudes gets zoom 16 (about 2.0 m), not 17.
ZOOM_TOLERANCE = 1.05
# Above this many tiles a warning reminds of the servers' usage policies.
MANY_TILES = 2500


def tile_ground_resolution(zoom, lat_deg):
    """Ground size (m) of one pixel of a 256-pixel Web Mercator tile."""
    return EARTH_CIRCUMFERENCE * math.cos(math.radians(lat_deg)) / (256 * 2**zoom)


def choose_zoom(resolution_m, lat_deg, max_zoom):
    """Coarsest zoom whose ground pixel is no larger than the resolution.

    :param resolution_m: target ground resolution in metres
    :param lat_deg: latitude of the region centre
    :param max_zoom: highest zoom level served
    :return: tuple (zoom, capped), capped is True when the server's highest
        zoom is coarser than the resolution asks for
    """
    for zoom in range(0, max_zoom + 1):
        if tile_ground_resolution(zoom, lat_deg) <= resolution_m * ZOOM_TOLERANCE:
            return zoom, False
    return max_zoom, True


def format_tile_url(template, x, y, zoom, api_key=None):
    """Fill an XYZ or quadkey URL template for one tile.

    {s} is a load-balancing subdomain (a, b or c), {api_key} the user's key.
    """
    fields = {
        "x": x,
        "y": y,
        "z": zoom,
        "s": "abc"[(x + y) % 3],
        "api_key": api_key or "",
    }
    if "{quadkey}" in template:
        fields["quadkey"] = xyz_to_quadkey(x, y, zoom)
    return template.format(**fields)


def get_region_bounds():
    """Get current region bounds"""
    region = gs.region()
    
    return {
        'minx': region['w'],
        'miny': region['s'],
        'maxx': region['e'],
        'maxy': region['n']
    }

def download_xyz_tiles(url_template, bbox, output, maxcols, maxrows, srs, format,
                       zoom="auto", max_zoom=20, api_key=None):
    """Download XYZ tiles and create a raster map"""
    import tempfile
    import os
    import math
    import subprocess
    import random
    
    gs.message("Downloading XYZ tiles - this may take a while...")
    gs.message(f"Input bbox: {bbox}")
    
    # XYZ tiles are indexed in WGS84 lat/lon. Take the region extent in WGS84
    # from g.region -b, which uses the project's full CRS definition (any
    # projection, not only UTM), instead of guessing the source CRS.
    region = gs.region()
    if gs.locn_is_latlong():
        bbox = {
            'minx': region['w'],
            'miny': region['s'],
            'maxx': region['e'],
            'maxy': region['n']
        }
    else:
        ll = gs.parse_command('g.region', flags='bg')
        try:
            bbox = {
                'minx': float(ll['ll_w']),
                'miny': float(ll['ll_s']),
                'maxx': float(ll['ll_e']),
                'maxy': float(ll['ll_n'])
            }
        except (KeyError, ValueError):
            gs.fatal("Unable to compute the WGS84 extent of the current region "
                     "(g.region -b). Check the project's CRS with g.proj -p.")
    gs.message(f"Region extent in WGS84: {bbox}")

    # Zoom level. With zoom=auto, the coarsest level whose ground pixel
    # matches the region resolution (in metres; in a lat/lon project the
    # resolution is converted at the region's centre latitude), capped at the
    # server's highest level.
    center_lat = (bbox['miny'] + bbox['maxy']) / 2
    avg_resolution = (region['nsres'] + region['ewres']) / 2
    if gs.locn_is_latlong():
        avg_resolution = (
            region['nsres'] * 111320.0
            + region['ewres'] * 111320.0 * math.cos(math.radians(center_lat))
        ) / 2
    if zoom == "auto":
        zoom_level, capped = choose_zoom(avg_resolution, center_lat, max_zoom)
        if capped:
            gs.warning(
                "The server's highest zoom level ({z}, {r:.2f} m) is coarser "
                "than the region resolution ({res:.2f} m); the output is "
                "resampled from it.".format(
                    z=zoom_level, r=tile_ground_resolution(zoom_level, center_lat),
                    res=avg_resolution))
    else:
        zoom_level = int(zoom)
        if zoom_level > max_zoom:
            gs.fatal("Zoom level {z} is above the server's highest level "
                     "({m}).".format(z=zoom_level, m=max_zoom))
    gs.message(
        "Region resolution: {res:.2f} m; zoom level {z} ({r:.2f} m per tile "
        "pixel).".format(res=avg_resolution, z=zoom_level,
                         r=tile_ground_resolution(zoom_level, center_lat)))

    # Expand bbox by 10% in all directions to ensure complete coverage
    def expand_bbox(bbox, expansion_factor=0.1):
        """Expand bounding box by given factor in all directions"""
        width = bbox['maxx'] - bbox['minx']
        height = bbox['maxy'] - bbox['miny']
        
        return {
            'minx': bbox['minx'] - width * expansion_factor,
            'miny': bbox['miny'] - height * expansion_factor,
            'maxx': bbox['maxx'] + width * expansion_factor,
            'maxy': bbox['maxy'] + height * expansion_factor
        }
    
    original_bbox = bbox.copy()
    bbox = expand_bbox(bbox)
    gs.message(f"Expanded bbox: {bbox}")
    
    # Convert bbox coordinates to Web Mercator (EPSG:3857) if needed
    # For now, assume input coordinates are in lat/lon
    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)
    
    def num2deg(xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lon_deg, lat_deg)

    def num2merc(xtile, ytile, zoom):
        """Convert tile coordinates to Web Mercator (EPSG:3857) meters"""
        lon_deg, lat_deg = num2deg(xtile, ytile, zoom)
        merc_x = lon_deg * 20037508.34 / 180.0
        merc_y = math.log(math.tan((90.0 + lat_deg) * math.pi / 360.0)) / (math.pi / 180.0)
        merc_y = merc_y * 20037508.34 / 180.0
        return (merc_x, merc_y)

    def create_world_file(world_file, x, y, zoom):
        """Create a world file (.wld) for an XYZ tile in Web Mercator coordinates

        XYZ tiles are natively served in Web Mercator (EPSG:3857), so the
        world file must be georeferenced in that CRS to match the tile
        pixel grid. Reprojection to the current GRASS location happens
        later, on import.
        """
        # Get Web Mercator coordinates of tile corners
        min_merc_x, max_merc_y = num2merc(x, y, zoom)
        max_merc_x, min_merc_y = num2merc(x + 1, y + 1, zoom)

        # World file format (6 lines):
        # Assuming 256x256 pixel tiles
        pixel_size_x = (max_merc_x - min_merc_x) / 256
        pixel_size_y = (max_merc_y - min_merc_y) / 256

        # Lines 5 and 6 hold the centre of the upper-left pixel, not the
        # tile corner: writing the corner shifts the mosaic by half a pixel
        # to the west and north.
        with open(world_file, 'w') as f:
            f.write(f"{pixel_size_x}\n")  # Line 1: pixel width
            f.write("0\n")              # Line 2: rotation y
            f.write("0\n")              # Line 3: rotation x
            f.write(f"{-pixel_size_y}\n") # Line 4: pixel height (negative)
            f.write(f"{min_merc_x + pixel_size_x / 2}\n")  # Line 5: x of upper-left pixel centre
            f.write(f"{max_merc_y - pixel_size_y / 2}\n")  # Line 6: y of upper-left pixel centre
    
    # Get tile coordinates for bbox with overlap
    min_x, min_y = deg2num(bbox['maxy'], bbox['minx'], zoom_level)
    max_x, max_y = deg2num(bbox['miny'], bbox['maxx'], zoom_level)
    
    # Add overlap buffer (1 extra tile around the edges)
    overlap = 1
    min_x = max(0, min_x - overlap)
    max_x = min(2**zoom_level - 1, max_x + overlap)
    min_y = max(0, min_y - overlap)
    max_y = min(2**zoom_level - 1, max_y + overlap)
    
    gs.message(f"Limited tile range: X({min_x}-{max_x}), Y({min_y}-{max_y})")
    n_tiles = (max_x - min_x + 1) * (max_y - min_y + 1)
    if n_tiles > MANY_TILES:
        gs.warning(
            "{n} tiles requested. Tile servers limit bulk downloads (see their "
            "usage policies); consider a smaller region or a lower zoom "
            "level.".format(n=n_tiles))
    
    # Create temporary directory for tiles
    temp_dir = tempfile.mkdtemp()
    tile_files = []
    
    try:
        # Create list of all tile coordinates and randomize order
        tile_coords = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tile_coords.append((x, y))
        
        # Randomize tile download order
        random.shuffle(tile_coords)
        gs.message(f"Randomized download order for {len(tile_coords)} tiles")
        
        # Download tiles using curl with retry logic
        max_retries = 2
        for x, y in tile_coords:
            tile_url = format_tile_url(url_template, x, y, zoom_level, api_key)
            
            tile_file = os.path.join(temp_dir, f"tile_{x}_{y}.{format}")
            
            # Retry logic for failed downloads
            for attempt in range(max_retries + 1):
                success = False
                try:
                    gs.message(f"Downloading tile URL: {tile_url} (attempt {attempt + 1})")
                    # -f: treat HTTP errors (e.g. 403 policy pages) as failures.
                    # A descriptive User-Agent is required by the OpenStreetMap
                    # tile usage policy.
                    result = subprocess.run(['curl', '-s', '-f', '-A', USER_AGENT,
                                             '-o', tile_file, tile_url,
                                             '--connect-timeout', '10', '--max-time', '30'], 
                                          capture_output=True, text=True)
                    
                    # Validate downloaded tile
                    if result.returncode == 0 and os.path.exists(tile_file):
                        file_size = os.path.getsize(tile_file)
                        if file_size > 0:
                            # Quick validation - check if it's a valid image
                            try:
                                with open(tile_file, 'rb') as f:
                                    header = f.read(10)
                                    if len(header) >= 4 and (header.startswith(b'\x89PNG') or 
                                                          header.startswith(b'\xFF\xD8\xFF') or 
                                                          header.startswith(b'GIF8')):
                                        # Valid image - create world file
                                        world_file = tile_file.replace('.png', '.wld').replace('.jpeg', '.wld')
                                        create_world_file(world_file, x, y, zoom_level)
                                        tile_files.append(tile_file)
                                        gs.message(f"Successfully downloaded tile {x},{y} ({file_size} bytes)")
                                        success = True
                                        break  # Success, exit retry loop
                                    else:
                                        gs.warning(f"Tile {x},{y} is not a valid image file (attempt {attempt + 1})")
                                        if os.path.exists(tile_file):
                                            os.remove(tile_file)
                            except Exception as e:
                                gs.warning(f"Error validating tile {x},{y}: {str(e)} (attempt {attempt + 1})")
                                if os.path.exists(tile_file):
                                    os.remove(tile_file)
                        else:
                            gs.warning(f"Tile {x},{y} is empty (0 bytes) (attempt {attempt + 1})")
                            if os.path.exists(tile_file):
                                os.remove(tile_file)
                    else:
                        gs.warning(f"Failed to download tile {x},{y}. Return code: {result.returncode} (attempt {attempt + 1})")
                        if result.stderr:
                            gs.warning(f"Curl error: {result.stderr}")
                        if os.path.exists(tile_file):
                            os.remove(tile_file)
                    
                    # If this was the last attempt and still failed, give up
                    if attempt == max_retries and not success:
                        gs.warning(f"Tile {x},{y} failed after {max_retries + 1} attempts - skipping")
                        
                except Exception as e:
                    gs.warning(f"Error downloading tile {x},{y}: {str(e)} (attempt {attempt + 1})")
                    if os.path.exists(tile_file):
                        os.remove(tile_file)
                    
                    # Last attempt failed
                    if attempt == max_retries:
                        gs.warning(f"Tile {x},{y} failed after {max_retries + 1} attempts - skipping")
        
        if not tile_files:
            gs.fatal("No tiles were downloaded successfully")
        
        gs.message(f"Downloaded {len(tile_files)} tiles")
        
        # Real-world Web Mercator extent of the tile grid (not tile indices)
        merc_min_x, merc_max_y = num2merc(min_x, min_y, zoom_level)
        merc_max_x, merc_min_y = num2merc(max_x + 1, max_y + 1, zoom_level)

        # Web Mercator tiles are equal-sized in projected meters at a given zoom
        earth_circumference = 2 * math.pi * 6378137.0
        pixel_size = (earth_circumference / (2 ** zoom_level)) / 256

        # Normalise every tile to a 3-band RGB GeoTIFF. Paletted PNG tiles
        # (e.g. OpenStreetMap) each carry their own palette, so mosaicking the
        # raw palette indices mixes colours; grey tiles must be widened too.
        rgb_tiles = []
        for tile_file in tile_files:
            src = gdal.Open(tile_file)
            if src is None:
                gs.warning(f"Cannot read tile {tile_file} - skipping")
                continue
            first = src.GetRasterBand(1)
            if src.RasterCount == 1 and first.GetColorTable() is not None:
                opts = gdal.TranslateOptions(format='GTiff', rgbExpand='rgb',
                                             outputSRS='EPSG:3857')
            elif src.RasterCount >= 3:
                opts = gdal.TranslateOptions(format='GTiff', bandList=[1, 2, 3],
                                             outputSRS='EPSG:3857')
            else:
                opts = gdal.TranslateOptions(format='GTiff', bandList=[1, 1, 1],
                                             outputSRS='EPSG:3857')
            rgb_file = os.path.splitext(tile_file)[0] + "_rgb.tif"
            gdal.Translate(rgb_file, src, options=opts)
            src = None
            rgb_tiles.append(rgb_file)
        if not rgb_tiles:
            gs.fatal("No readable tiles were downloaded")

        # Create a VRT file from the tiles using gdalbuildvrt. Areas without
        # a tile are flagged by an alpha band (-addalpha) rather than by a
        # nodata value, so genuinely black pixels are kept.
        vrt_file = os.path.join(temp_dir, "tiles.vrt")
        try:
            cmd = [
                'gdalbuildvrt',
                '-a_srs', 'EPSG:3857',
                '-addalpha',
                '-resolution', 'user',
                '-te', str(merc_min_x), str(merc_min_y), str(merc_max_x), str(merc_max_y),
                '-tr', str(pixel_size), str(pixel_size),
                vrt_file
            ] + rgb_tiles

            subprocess.run(cmd, check=True, capture_output=True)

            # Tag band color interpretation explicitly. gdalbuildvrt/gdal_translate
            # don't reliably propagate Red/Green/Blue from source PNG/JPEG tiles,
            # which otherwise makes r.import/r.in.gdal fall back to naming bands
            # <output>.1/.2/.3 instead of <output>.red/.green/.blue.
            band_colors = ['red', 'green', 'blue', 'alpha']
            n_bands = gdal.Open(vrt_file).RasterCount
            colorinterp = band_colors[:n_bands]

            # Apply cubic resampling to reduce seams
            final_vrt = os.path.join(temp_dir, "tiles_final.vrt")
            translate_cmd = [
                'gdal_translate',
                '-of', 'VRT',
                '-r', 'cubic',
                '-colorinterp', ','.join(colorinterp),
                vrt_file, final_vrt
            ]
            subprocess.run(translate_cmd, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            gs.warning(f"Advanced VRT creation failed: {e}")
            # Fallback: try simple gdalbuildvrt, then stamp the SRS and band
            # colors on afterwards
            try:
                subprocess.run(['gdalbuildvrt', '-a_srs', 'EPSG:3857',
                                '-addalpha', vrt_file] + rgb_tiles, check=True)
                band_colors = ['red', 'green', 'blue', 'alpha']
                n_bands = gdal.Open(vrt_file).RasterCount
                for i, color in enumerate(band_colors[:n_bands], start=1):
                    subprocess.run(['gdal_edit.py', '-colorinterp_' + str(i), color, vrt_file], check=True)
                final_vrt = vrt_file
            except subprocess.CalledProcessError:
                gs.fatal("Failed to create VRT from tiles. gdalbuildvrt may not be available.")

        # Import VRT into GRASS using r.import, which reprojects the
        # Web Mercator tiles into the current location's CRS
        try:
            gs.run_command('r.import', input=final_vrt, output=output, overwrite=True)
        except:
            gs.fatal("Failed to import VRT into GRASS. r.import may not be available.")

        # Turn the alpha band into NULLs on the colour bands, then drop it.
        # r.import names bands after their colour interpretation or index.
        for suffixes in (('red', 'green', 'blue', 'alpha'), ('1', '2', '3', '4')):
            bands = [f"{output}.{suffix}" for suffix in suffixes]
            if all(gs.find_file(name=b, element='raster')['file'] for b in bands):
                alpha = bands[3]
                for band in bands[:3]:
                    gs.mapcalc(f"{band} = if({alpha} == 0, null(), {band})",
                               overwrite=True, quiet=True)
                    gs.run_command('r.colors', map=band, color='grey', quiet=True)
                gs.run_command('g.remove', type='raster', name=alpha, flags='f',
                               quiet=True)
                break

        gs.message(f"Successfully created raster map '{output}' from {len(tile_files)} tiles")
        
    finally:
        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def download_wms_tiles(url_template, bbox, output, maxcols, maxrows, srs, format):
    """Download WMS tiles using GRASS r.in.wms"""
    gs.message("Downloading WMS data using GRASS r.in.wms...")
    gs.message(f"WMS URL: {url_template}")
    gs.message(f"Bounding box: {bbox}")
    
    # Build WMS parameters for r.in.wms
    wms_params = {
        'url': url_template,
        'layers': '0',  # Default layer - can be customized
        'output': output,
        'format': format,
        'maxcols': maxcols,
        'maxrows': maxrows,
        'wms_version': '1.1.1',
        'method': 'nearest',
        'flags': 'o'  # Overwrite
    }
    
    # Set region to current computational region (r.in.wms uses region, not bbox)
    if not gs.find_file('region', element='windows')['name']:
        gs.warning("No current region set, using default")
    
    try:
        gs.run_command('r.in.wms', **wms_params)
        gs.message(f"Successfully downloaded WMS data as '{output}'")
    except Exception as e:
        gs.fatal(f"Failed to download WMS data: {str(e)}")

def main():
    options, flags = gs.parser()
    
    # Handle flags
    if flags['l']:
        list_servers()
        return 0
    
    # Get parameters
    output = options['output']
    server = options['server']
    url = options['url']
    maxcols = int(options['maxcols'])
    maxrows = int(options['maxrows'])
    srs = options['srs']
    format = options['format']
    api_key = options['api_key']
    zoom = options['zoom'].strip().lower() or "auto"
    if zoom != "auto" and not (zoom.isdigit() and 0 <= int(zoom) <= 20):
        gs.fatal("zoom must be auto or an integer from 0 to 20, not <{}>.".format(zoom))

    # Get URL and server type
    if url:
        # Use custom URL
        tile_url = url
        server_name = "Custom"
        server_type = "xyz"  # Assume XYZ for custom URLs
        max_zoom = 20
    else:
        # Use predefined server
        if server not in WEB_MAP_SERVERS:
            gs.fatal(f"Server '{server}' not found. Use -l flag to list available servers.")
        
        server_info = WEB_MAP_SERVERS[server]
        tile_url = server_info['url']
        server_name = server_info['name']
        server_type = server_info['type']
        max_zoom = server_info['max_zoom']
    if '{api_key}' in tile_url and not api_key:
        gs.fatal("Server <{}> requires an API key: set api_key=.".format(
            server or "custom"))
    
    # Get bounding box
    if flags['c']:
        bbox = get_region_bounds()
    else:
        # Use default region or prompt user
        gs.message("Using current computational region...")
        bbox = get_region_bounds()
    
    gs.message(f"Downloading from {server_name}")
    gs.message(f"Output: {output}")
    gs.message(f"Format: {format}")
    gs.message(f"Max size: {maxcols}x{maxrows}")
    
    # Download based on server type
    if server_type.lower() == 'wms':
        download_wms_tiles(tile_url, bbox, output, maxcols, maxrows, srs, format)
    else:
        download_xyz_tiles(tile_url, bbox, output, maxcols, maxrows, srs, format,
                           zoom=zoom, max_zoom=max_zoom, api_key=api_key)

    # If the import produced separate red/green/blue band maps, by default
    # merge them into a single composite map named after the output basename
    # and remove the intermediate bands. Use -b to keep the three bands instead.
    # r.import/r.in.gdal name bands after GDAL's color interpretation when
    # available (<output>.red/.green/.blue), falling back to band index
    # (<output>.1/.2/.3) otherwise, so check for both.
    band_maps = None
    for suffixes in (('red', 'green', 'blue'), ('1', '2', '3')):
        candidate = [f"{output}.{suffix}" for suffix in suffixes]
        if all(gs.find_file(name=name, element='raster')['file'] for name in candidate):
            band_maps = candidate
            break

    if band_maps and not flags['b']:
        gs.message("Creating RGB composite and removing band maps...")
        gs.run_command('r.composite', red=band_maps[0], green=band_maps[1],
                        blue=band_maps[2], levels=options['composite_levels'],
                        output=output, overwrite=True)
        gs.run_command('g.remove', type='raster', name=band_maps, flags='f')

    # Add metadata to the maps produced: a single composite, the r.composite
    # true-colour maps <output>.r/.g/.b, or the separate bands (-b). The
    # source URL is recorded without the API key.
    produced = [name for name in
                [output] + [f"{output}.{suffix}" for suffix in
                            ("r", "g", "b", "red", "green", "blue", "1", "2", "3")]
                if gs.find_file(name=name, element='raster')['file']]
    for name in produced:
        gs.run_command('r.support', map=name,
                       title=f"Base map from {server_name}",
                       source1=tile_url.replace(api_key, "<api_key>") if api_key else tile_url,
                       description=f"Base map imported from {server_name}")

    gs.message(f"Successfully imported base map as '{output}'")

    return 0

if __name__ == "__main__":
    # Test mode when run directly (not in GRASS environment)
    if not GRASS_AVAILABLE:
        print("i.basemap - GRASS GIS addon for web map server access")
        print("This is a GRASS GIS addon and should be run within GRASS environment.")
        print("\nTesting server catalog...")
        list_servers()
        sys.exit(0)
    
    sys.exit(main())
