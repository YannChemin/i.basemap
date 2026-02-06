# i.basemap - GRASS GIS Web Map Server Module

A comprehensive GRASS GIS module for downloading and importing base map data from **25 freely available web map servers** with robust error handling, randomized downloads, and automatic mosaicing.

## Data Sources

### Web Mapping Services (XYZ)
| Server | Max Zoom | Format | Description |
|---------|----------|---------|-------------|
| OpenStreetMap | 19 | PNG | Free collaborative world map |
| ESRI_WorldImagery | 19 | JPEG | High-resolution satellite imagery |
| Google_Satellite | 20 | JPEG | Google satellite imagery |
| Google_Terrain | 15 | PNG | Terrain with elevation data |
| Google_Hybrid | 20 | JPEG | Hybrid satellite/road maps |
| Bing_Aerial | 19 | JPEG | Microsoft aerial photography |
| Bing_Roads | 19 | PNG | Microsoft road maps |
| Stamen_Terrain | 18 | PNG | Terrain with hillshading |
| Stamen_Toner | 20 | PNG | High-contrast B&W maps |
| Stamen_Watercolor | 18 | JPEG | Artistic watercolor style |
| OpenTopoMap | 17 | PNG | Topographic with trails |
| OSM_Humanitarian | 20 | PNG | Humanitarian response maps |

### Scientific & Earth Observation (WMS)
| Server | Max Zoom | Format | Description |
|---------|----------|---------|-------------|
| USGS_Topo | 16 | PNG | USGS topographic maps |
| USGS_NAIP | 18 | JPEG | USGS agriculture imagery |
| USGS_3DEP | 15 | TIFF | USGS 3D elevation |
| USGS_Hydro | 16 | PNG | USGS hydrography |
| ESA_WorldCover | 12 | TIFF | ESA 10m land cover |
| Copernicus_Sentinel | 14 | TIFF | Sentinel-2 satellite |
| Landsat | 14 | TIFF | Landsat 8 satellite |
| MODIS | 10 | TIFF | MODIS satellite data |
| NOAA_Climate | 12 | TIFF | NOAA climate data |
| ESA_Climate | 12 | TIFF | ESA climate indicators |
| WorldBank | 12 | TIFF | World Bank data |
| UN_GeoWeb | 12 | TIFF | UN geospatial data |
| Natural_Earth | 16 | PNG | National Geographic maps |

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

# List all available servers
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

# WMS server with specific layer
i.basemap server=USGS_Topo output=topo layer=topo -c

# High resolution scientific data
i.basemap server=Copernicus_Sentinel output=sentinel layer=TRUE-COLOR-S2L1C -c

# Climate data
i.basemap server=NOAA_Climate output=climate layer=temperature -c
```

## Dependencies

### Required
- **GRASS GIS 8.5+**: For core functionality
- **curl**: For tile downloads
- **gdal**: For VRT creation and import

### Optional
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

# Test server listing (outside GRASS)
python3 i.basemap.py -l

# Test in GRASS environment
grass
i.basemap -l
```

## Related Modules

- `r.in.gdal` - Import raster data using GDAL
- `r.in.wms` - Download web mapping services
- `g.region` - Manage computational region
- `g.proj` - Manage projection information
