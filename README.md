# i.basemap - GRASS GIS Web Map Server Module

A comprehensive GRASS GIS module for downloading and importing base map data from **25 freely available web map servers** with robust error handling, randomized downloads, and automatic mosaicing.

## Available Data Sources

### Web Mapping Services (23 XYZ + 2 Quadkey)
| Server | Type | Max Zoom | Format | Description |
|---------|------|----------|---------|-------------|
| OpenStreetMap | XYZ | 19 | PNG | Free collaborative world map |
| ESRI_WorldImagery | XYZ | 19 | JPEG | High-resolution satellite imagery |
| Google_Satellite | XYZ | 20 | JPEG | Google satellite imagery |
| Google_Terrain | XYZ | 15 | PNG | Terrain with elevation data |
| Google_Hybrid | XYZ | 20 | JPEG | Hybrid satellite/road maps |
| Bing_Aerial | Quadkey | 19 | JPEG | Microsoft aerial photography |
| Bing_Roads | Quadkey | 19 | PNG | Microsoft road maps |
| Stamen_Terrain | XYZ | 18 | PNG | Terrain with hillshading |
| Stamen_Toner | XYZ | 20 | PNG | High-contrast B&W maps |
| Stamen_Watercolor | XYZ | 18 | JPEG | Artistic watercolor style |
| OpenTopoMap | XYZ | 17 | PNG | Topographic with trails |
| OSM_Humanitarian | XYZ | 20 | PNG | Humanitarian response maps |
| Natural_Earth | XYZ | 16 | PNG | National Geographic style |
| USGS_Topo | XYZ | 16 | PNG | USGS topographic maps |
| USGS_NAIP | XYZ | 18 | JPEG | USGS agriculture imagery |
| USGS_3DEP | XYZ | 15 | TIFF | USGS 3D elevation |
| USGS_Hydro | XYZ | 16 | PNG | USGS hydrography |
| ESA_WorldCover | XYZ | 12 | JPEG | ESA 10m land cover |
| Copernicus_Sentinel | XYZ | 14 | JPEG | Sentinel-2 satellite |
| Landsat | XYZ | 14 | JPEG | Landsat 8 satellite |
| MODIS | XYZ | 10 | JPEG | MODIS satellite data |
| NOAA_Climate | XYZ | 12 | PNG | NOAA climate data |
| ESA_Climate | XYZ | 12 | PNG | ESA climate indicators |
| WorldBank | XYZ | 12 | PNG | World Bank data |
| UN_GeoWeb | XYZ | 12 | PNG | UN geospatial data |

## Quick Start

### Installation

```bash
# Copy to GRASS scripts directory
sudo cp i.basemap.py /usr/local/grass85/scripts/i.basemap
sudo chmod +x /usr/local/grass85/scripts/i.basemap
```

### Basic Usage

```bash
# Start GRASS GIS
grass

# List all available servers (25 total)
i.basemap -l

# Download OpenStreetMap for current region
i.basemap server=OpenStreetMap output=osm_map -c

# Download satellite imagery
i.basemap server=Google_Satellite output=satellite -c

# Download Bing aerial imagery
i.basemap server=Bing_Aerial output=aerial -c
```

## Usage Examples

### Basic Usage

```bash
# Use current computational region
i.basemap server=OpenStreetMap output=osm -c

# Specify custom output size
i.basemap server=ESRI_WorldImagery output=imagery maxcols=2048 maxrows=2048 -c

# Different map styles
i.basemap server=Stamen_Toner output=toner -c
i.basemap server=Stamen_Watercolor output=watercolor -c
```

### Advanced Usage

```bash
# Custom URL with API key
i.basemap url="https://api.example.com/{z}/{x}/{y}?key={api_key}" output=custom api_key=your_key

# High resolution scientific data
i.basemap server=Copernicus_Sentinel output=sentinel -c

# Climate data
i.basemap server=NOAA_Climate output=climate -c
```

## Technical Details

### Processing Workflow

1. **Coordinate Transformation**: Converts projected coordinates to lat/lon for XYZ tiles
2. **Tile Download**: Downloads individual tiles with randomized order
3. **Georeferencing**: Creates world files for each tile
4. **Mosaicing**: Combines tiles using GDAL VRT with cubic resampling
5. **Import**: Imports mosaiced result into GRASS with automatic reprojection

### Server Type Support

- **XYZ Tiles**: Standard slippy map tiles (OpenStreetMap, Google, ESRI, etc.)
- **Quadkey Tiles**: Bing Maps quadkey format (Bing Aerial, Bing Roads)
- **Automatic Detection**: Routes to appropriate handler based on server type

### Performance Features

- **Dynamic Zoom**: Automatic zoom level selection based on region resolution
- **Overlap Buffer**: 10% bbox expansion + 1-tile overlap
- **Memory Efficient**: Temporary file cleanup
- **Error Recovery**: Graceful handling of network issues

## Dependencies

### Required
- **GRASS GIS 8.5+**: For core functionality
- **curl**: For tile downloads
- **gdal**: For VRT creation and import
- **pyproj**: For coordinate transformation (auto-installed if needed)

## Project Structure

```
i.basemap/
├── i.basemap.py          # Main module script
├── i.basemap.md          # Markdown documentation
├── i.basemap.html         # HTML documentation
├── README.md              # This file
├── Makefile              # Build configuration
└── PKG                   # Package metadata
```

## Development

### Testing

```bash
# Test syntax
python3 -m py_compile i.basemap.py

# Test in GRASS environment
grass
i.basemap -l
```

### Installation

```bash
# Install to GRASS
sudo cp i.basemap.py /usr/local/grass85/scripts/i.basemap
sudo chmod +x /usr/local/grass85/scripts/i.basemap

# Update development version
cp i.basemap.py /usr/local/grass85/scripts/i.basemap
```

## Troubleshooting

### Common Issues

**No tiles downloaded**
```bash
# Check coordinate transformation
g.region -p
i.basemap server=OpenStreetMap output=test -c
```

**Partial downloads**
- Network issues - retry logic handles automatically
- Check internet connection
- Try smaller region

**Projection errors**
```bash
# Ensure GRASS location is properly set
g.proj -p
```

**Memory issues**
```bash
# Reduce output size
i.basemap server=OpenStreetMap output=osm maxcols=512 maxrows=512 -c
```

### Performance Tips

- **Smaller regions**: Faster downloads and processing
- **Appropriate zoom**: Let script auto-select based on resolution
- **Network stability**: Wired connection preferred for large downloads
- **Server selection**: Choose appropriate zoom level for your needs

## License

Copyright (C) 2025 by the GRASS Development Team

This program is free software under the GNU General Public License (>=v2). 
Read the file COPYING that comes with GRASS for details.

## Related Modules

- `r.in.gdal` - Import raster data using GDAL
- `r.in.wms` - Download web mapping services
- `g.region` - Manage computational region
- `g.proj` - Manage projection information
