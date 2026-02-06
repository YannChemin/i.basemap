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
#% options: Google_Satellite,OpenStreetMap,Bing_Aerial,ESRI_WorldImagery,USGS_Topo,Google_Terrain,Google_Hybrid,Bing_Roads,Stamen_Terrain,Stamen_Toner,Stamen_Watercolor,OpenTopoMap,OSM_Humanitarian,Natural_Earth,USGS_NAIP,USGS_3DEP,USGS_Hydro,ESA_WorldCover,Copernicus_Sentinel,Landsat,MODIS,NOAA_Climate,ESA_Climate,WorldBank,UN_GeoWeb
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

import sys
import os
import math
import subprocess
import tempfile
import random

# Try to import grass.script
try:
    import grass.script as gs
    GRASS_AVAILABLE = True
except ImportError:
    GRASS_AVAILABLE = False
    gs = None

# Web map server configurations - 25 Comprehensive Data Sources
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
        'name': 'Stamen Terrain',
        'url': 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        'type': 'xyz',
        'max_zoom': 18,
        'format': 'png'
    },
    'Stamen_Toner': {
        'name': 'Stamen Toner',
        'url': 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png',
        'type': 'xyz',
        'max_zoom': 20,
        'format': 'png'
    },
    'Stamen_Watercolor': {
        'name': 'Stamen Watercolor',
        'url': 'https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg',
        'type': 'xyz',
        'max_zoom': 18,
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
        'name': 'USGS NAIP Imagery',
        'url': 'https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 18,
        'format': 'jpeg'
    },
    'USGS_3DEP': {
        'name': 'USGS 3D Elevation Program',
        'url': 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 15,
        'format': 'tiff'
    },
    'USGS_Hydro': {
        'name': 'USGS Hydrography',
        'url': 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer/tile/{z}/{y}/{x}',
        'type': 'xyz',
        'max_zoom': 16,
        'format': 'png'
    },
    'ESA_WorldCover': {
        'name': 'ESA WorldCover',
        'url': 'https://services.sentinel-hub.com/ogc/wms/WorldCover',
        'type': 'wms',
        'max_zoom': 12,
        'format': 'tiff'
    },
    'Copernicus_Sentinel': {
        'name': 'Copernicus Sentinel-2',
        'url': 'https://services.sentinel-hub.com/ogc/wms/sentinel-2',
        'type': 'wms',
        'max_zoom': 14,
        'format': 'tiff'
    },
    'Landsat': {
        'name': 'Landsat 8',
        'url': 'https://services.sentinel-hub.com/ogc/wms/landsat8',
        'type': 'wms',
        'max_zoom': 14,
        'format': 'tiff'
    },
    'MODIS': {
        'name': 'MODIS',
        'url': 'https://services.sentinel-hub.com/ogc/wms/modis',
        'type': 'wms',
        'max_zoom': 10,
        'format': 'tiff'
    },
    'NOAA_Climate': {
        'name': 'NOAA Climate Data',
        'url': 'https://www.ncdc.noaa.gov/oa-web/wms/wms',
        'type': 'wms',
        'max_zoom': 12,
        'format': 'tiff'
    },
    'ESA_Climate': {
        'name': 'ESA Climate Change Service',
        'url': 'https://climate.copernicus.eu/wms',
        'type': 'wms',
        'max_zoom': 12,
        'format': 'tiff'
    },
    'WorldBank': {
        'name': 'World Bank Development Data',
        'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/WorldBank_Indicators/MapServer/WMS',
        'type': 'wms',
        'max_zoom': 12,
        'format': 'tiff'
    },
    'UN_GeoWeb': {
        'name': 'UN GeoNetwork',
        'url': 'https://geodata.grid.un.org/arcgis/services/UNGeoWeb/MapServer/WMS',
        'type': 'wms',
        'max_zoom': 12,
        'format': 'tiff'
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

def get_region_bounds():
    """Get current region bounds"""
    region = gs.region()
    
    return {
        'minx': region['w'],
        'miny': region['s'],
        'maxx': region['e'],
        'maxy': region['n']
    }

def download_xyz_tiles(url_template, bbox, output, maxcols, maxrows, srs, format):
    """Download XYZ tiles and create a raster map"""
    import tempfile
    import os
    import math
    import subprocess
    import random
    
    gs.message("Downloading XYZ tiles - this may take a while...")
    gs.message(f"Input bbox: {bbox}")
    
    # Calculate appropriate zoom level based on region resolution
    zoom_level = 12  # Default zoom level
    
    # Transform projected coordinates to lat/lon if needed
    def transform_to_latlon(bbox):
        """Transform projected coordinates to lat/lon using pyproj"""
        try:
            import pyproj
            
            # Get current GRASS projection info
            region = gs.region()
            proj_info = gs.parse_command('g.proj', flags='j')
            
            # Create transformer from current projection to WGS84 (EPSG:4326)
            if '+proj' in proj_info:
                # Extract projection parameters
                proj_string = proj_info['+proj']
                if proj_string == 'utm':
                    zone = int(proj_info.get('+zone', 44))
                    src_crs = f"EPSG:326{zone:02d}"
                else:
                    # Fallback to Web Mercator for other projections
                    src_crs = "EPSG:3857"
            else:
                src_crs = "EPSG:3857"
            
            # Create coordinate transformer
            transformer = pyproj.Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
            
            # Transform bbox corners
            min_lon, min_lat = transformer.transform(bbox['minx'], bbox['miny'])
            max_lon, max_lat = transformer.transform(bbox['maxx'], bbox['maxy'])
            
            return {
                'minx': min_lon,
                'miny': min_lat, 
                'maxx': max_lon,
                'maxy': max_lat
            }
        except ImportError:
            gs.fatal("pyproj is required for coordinate transformation. "
                     "Please install it with: pip install pyproj")
        except Exception as e:
            gs.warning(f"Coordinate transformation failed: {str(e)}")
            return bbox
    
    # Convert bbox to lat/lon if needed
    if abs(bbox['minx']) > 180 or abs(bbox['maxx']) > 180:
        gs.message("Transforming coordinates from projected to lat/lon...")
        bbox = transform_to_latlon(bbox)
        gs.message(f"Transformed bbox: {bbox}")
    
    # Dynamic zoom level calculation based on region resolution
    region = gs.region()
    avg_resolution = (region['nsres'] + region['ewres']) / 2
    
    # Adjust thresholds to ensure 30m resolution uses zoom 13
    if avg_resolution <= 5:
        zoom_level = 16  # Very high resolution
    elif avg_resolution <= 10:
        zoom_level = 15  # High resolution
    elif avg_resolution <= 20:
        zoom_level = 14  # Medium-high resolution
    elif avg_resolution <= 40:
        zoom_level = 13  # Medium resolution (30m -> zoom 13)
    elif avg_resolution <= 80:
        zoom_level = 12  # Low-medium resolution
    else:
        zoom_level = 11  # Low resolution
    
    gs.message(f"Region resolution: {avg_resolution:.1f}m, using zoom level {zoom_level} for cleaner imagery")
    
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
    
    def create_world_file(world_file, x, y, zoom):
        """Create a world file (.wld) for an XYZ tile in UTM coordinates"""
        import pyproj
        
        # First convert tile coordinates to lat/lon, then to UTM
        def num2deg(xtile, ytile, zoom):
            n = 2.0 ** zoom
            lon_deg = xtile / n * 360.0 - 180.0
            lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
            lat_deg = math.degrees(lat_rad)
            return (lon_deg, lat_deg)
        
        # Get lat/lon coordinates of tile corners
        min_lon, max_lat = num2deg(x, y, zoom)
        max_lon, min_lat = num2deg(x + 1, y + 1, zoom)
        
        # Transform lat/lon to UTM zone 44N
        transformer = pyproj.Transformer.from_crs('EPSG:4326', 'EPSG:32644', always_xy=True)
        min_utm_x, max_utm_y = transformer.transform(min_lon, max_lat)
        max_utm_x, min_utm_y = transformer.transform(max_lon, min_lat)
        
        # World file format (6 lines):
        # Assuming 256x256 pixel tiles
        pixel_size_x = (max_utm_x - min_utm_x) / 256
        pixel_size_y = (max_utm_y - min_utm_y) / 256
        
        with open(world_file, 'w') as f:
            f.write(f"{pixel_size_x}\n")  # Line 1: pixel width
            f.write("0\n")              # Line 2: rotation y
            f.write("0\n")              # Line 3: rotation x  
            f.write(f"{-pixel_size_y}\n") # Line 4: pixel height (negative)
            f.write(f"{min_utm_x}\n")   # Line 5: x-coordinate of upper-left pixel center
            f.write(f"{max_utm_y}\n")   # Line 6: y-coordinate of upper-left pixel center
    
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
            # Handle different URL formats (XYZ vs quadkey)
            if '{quadkey}' in url_template:
                quadkey = xyz_to_quadkey(x, y, zoom_level)
                tile_url = url_template.format(quadkey=quadkey)
            else:
                tile_url = url_template.format(z=zoom_level, x=x, y=y)
            
            tile_file = os.path.join(temp_dir, f"tile_{x}_{y}.{format}")
            
            # Retry logic for failed downloads
            for attempt in range(max_retries + 1):
                success = False
                try:
                    gs.message(f"Downloading tile URL: {tile_url} (attempt {attempt + 1})")
                    result = subprocess.run(['curl', '-s', '-o', tile_file, tile_url, '--connect-timeout', '10', '--max-time', '30'], 
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
                            gs.warning(f"Curl error: {result.stderr.decode()}")
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
        
        # Create a VRT file from the tiles using gdalbuildvrt
        vrt_file = os.path.join(temp_dir, "tiles.vrt")
        try:
            # Create VRT with blending to reduce tile seams
            cmd = [
                'gdalbuildvrt',
                '-resolution', 'user',
                '-te', str(min_x), str(min_y), str(max_x + 1), str(max_y + 1),
                '-tr', str(256), str(256),
                vrt_file
            ] + tile_files
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Apply cubic resampling to reduce seams
            final_vrt = os.path.join(temp_dir, "tiles_final.vrt")
            translate_cmd = [
                'gdal_translate',
                '-of', 'VRT',
                '-r', 'cubic',
                '-a_nodata', '0',
                vrt_file, final_vrt
            ]
            subprocess.run(translate_cmd, check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            gs.warning(f"Advanced VRT creation failed: {e}")
            # Fallback: try simple gdalbuildvrt
            try:
                subprocess.run(['gdalbuildvrt', vrt_file] + tile_files, check=True)
                final_vrt = vrt_file
            except subprocess.CalledProcessError:
                gs.fatal("Failed to create VRT from tiles. gdalbuildvrt may not be available.")
        
        # Import VRT into GRASS using r.in.gdal
        try:
            gs.run_command('r.in.gdal', input=final_vrt, output=output, overwrite=True, flags='o')
        except:
            gs.fatal("Failed to import VRT into GRASS. r.in.gdal may not be available.")
        
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
    
    # Get URL and server type
    if url:
        # Use custom URL
        tile_url = url
        server_name = "Custom"
        server_type = "xyz"  # Assume XYZ for custom URLs
    else:
        # Use predefined server
        if server not in WEB_MAP_SERVERS:
            gs.fatal(f"Server '{server}' not found. Use -l flag to list available servers.")
        
        server_info = WEB_MAP_SERVERS[server]
        tile_url = server_info['url']
        server_name = server_info['name']
        server_type = server_info['type']
    
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
        download_xyz_tiles(tile_url, bbox, output, maxcols, maxrows, srs, format)
    
    # Add metadata to the map
    if gs.find_file(name=output, element='raster')['file']:
        gs.run_command('r.support', map=output, 
                      title=f"Base map from {server_name}",
                      source1=tile_url,
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
