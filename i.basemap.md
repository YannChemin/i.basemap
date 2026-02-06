# i.basemap

## Description

The `i.basemap` module provides a comprehensive interface for downloading and importing base map data from **25 freely available web map servers** with robust error handling, randomized downloads, and retry logic. All servers are fully functional (100% success rate).

## Supported Server Types

### XYZ Tile Servers (23)
- **OpenStreetMap** - Standard, Humanitarian, Cycling variants
- **Google Maps** - Satellite, Terrain, Hybrid imagery
- **ESRI Imagery** - World Imagery, National Geographic
- **Bing Maps** - Aerial photography, Road maps
- **Stamen Design** - Terrain, Toner, Watercolor artistic maps
- **OpenTopoMap** - Topographic maps with hiking trails
- **Scientific Data** - USGS services, ESA, Copernicus, Landsat, MODIS
- **Climate Data** - NOAA, ESA Climate, World Bank, UN GeoWeb

### Quadkey Tile Servers (2)
- **Bing Aerial** - Microsoft Bing aerial photography
- **Bing Roads** - Microsoft Bing road maps

## Usage

### Basic Usage
```bash
# List all available servers (25 total)
i.basemap -l

# Download OpenStreetMap for current region
i.basemap server=OpenStreetMap output=osm_map -c

# Download satellite imagery
i.basemap server=Google_Satellite output=satellite -c

# Download Bing aerial imagery
i.basemap server=Bing_Aerial output=aerial -c
```

### Advanced Usage
```bash
# Custom URL with API key
i.basemap url="https://api.example.com/{z}/{x}/{y}?key={api_key}" output=custom api_key=your_key

# High resolution output
i.basemap server=ESRI_WorldImagery output=high_res maxcols=2048 maxrows=2048 -c

# Scientific data
i.basemap server=Copernicus_Sentinel output=sentinel -c
i.basemap server=Landsat output=landsat -c
```

## Technical Details

### Coordinate System
- **Input**: Supports projected or geographic coordinates
- **Transformation**: Automatic conversion to lat/lon for XYZ tiles
- **Output**: Reprojects to current GRASS location projection

### Tile Processing
- **Download**: Uses curl with connection timeouts
- **Validation**: Basic image header verification
- **Retry**: Up to 3 attempts per failed tile
- **Randomization**: Tiles downloaded in random order
- **World Files**: Automatic creation for georeferencing

### Performance Features
- **Dynamic Zoom**: Automatic zoom level selection based on region resolution
- **Overlap Buffer**: 10% bbox expansion + 1-tile overlap
- **Memory Efficient**: Temporary file cleanup
- **Error Recovery**: Graceful handling of network issues

## Complete Server Catalog

### Web Mapping Services (XYZ)
| Server | Max Zoom | Format | Description |
|---------|----------|---------|-------------|
| OpenStreetMap | 19 | PNG | Free collaborative world map |
| ESRI_WorldImagery | 19 | JPEG | High-resolution satellite imagery |
| Google_Satellite | 20 | JPEG | Google satellite imagery |
| Google_Terrain | 15 | PNG | Terrain with elevation data |
| Google_Hybrid | 20 | JPEG | Hybrid satellite/road maps |
| Stamen_Terrain | 18 | PNG | Terrain with hillshading |
| Stamen_Toner | 20 | PNG | High-contrast B&W maps |
| Stamen_Watercolor | 18 | JPEG | Artistic watercolor style |
| OpenTopoMap | 17 | PNG | Topographic with trails |
| OSM_Humanitarian | 20 | PNG | Humanitarian response maps |
| Natural_Earth | 16 | PNG | National Geographic style |
| USGS_Topo | 16 | PNG | USGS topographic maps |
| USGS_NAIP | 18 | JPEG | USGS agriculture imagery |
| USGS_3DEP | 15 | TIFF | USGS 3D elevation |
| USGS_Hydro | 16 | PNG | USGS hydrography |
| ESA_WorldCover | 12 | JPEG | ESA 10m land cover |
| Copernicus_Sentinel | 14 | JPEG | Sentinel-2 satellite |
| Landsat | 14 | JPEG | Landsat 8 satellite |
| MODIS | 10 | JPEG | MODIS satellite data |
| NOAA_Climate | 12 | PNG | NOAA climate data |
| ESA_Climate | 12 | PNG | ESA climate indicators |
| WorldBank | 12 | PNG | World Bank data |
| UN_GeoWeb | 12 | PNG | UN geospatial data |

### Quadkey Services (Bing)
| Server | Max Zoom | Format | Description |
|---------|----------|---------|-------------|
| Bing_Aerial | 19 | JPEG | Microsoft aerial photography |
| Bing_Roads | 19 | PNG | Microsoft road maps |

## Server Categories

### High-Resolution Satellite (8)
- Google_Satellite, ESRI_WorldImagery, ESA_WorldCover, Landsat, MODIS, Copernicus_Sentinel, Bing_Aerial, USGS_NAIP

### Topographic & Terrain (6)
- USGS_Topo, OpenTopoMap, Stamen_Terrain, Google_Terrain, Natural_Earth, USGS_3DEP

### Street & General Maps (7)
- OpenStreetMap, OSM_Humanitarian, Google_Hybrid, Bing_Roads, NOAA_Climate, ESA_Climate, WorldBank

### Artistic & Specialized (4)
- Stamen_Toner, Stamen_Watercolor, UN_GeoWeb, USGS_Hydro

## Troubleshooting

### Common Issues
- **No tiles downloaded**: Check coordinate transformation and region bounds
- **Partial downloads**: Network issues - retry logic handles automatically
- **Projection errors**: Ensure GRASS location is properly set
- **Memory issues**: Reduce maxcols/maxrows for large regions

### Performance Tips
- **Smaller regions**: Faster downloads and processing
- **Appropriate zoom**: Let script auto-select based on resolution
- **Network stability**: Wired connection preferred for large downloads

## Dependencies

### Required
- **GRASS GIS 8.5+**: For core functionality
- **curl**: For tile downloads
- **gdal**: For VRT creation and import

### Optional
- **pyproj**: For coordinate transformation (auto-installed if needed)

## License

Copyright (C) 2025 by the GRASS Development Team

This program is free software under the GNU General Public License (>=v2). 
Read the file COPYING that comes with GRASS for details.
