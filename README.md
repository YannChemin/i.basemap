# i.basemap - GRASS GIS Web Map Server Module

A comprehensive GRASS GIS module for downloading and importing base map data from **25 freely available web map servers** with robust error handling, randomized downloads, and automatic mosaicing.

## 🌟 Features

- **🗺️ 25 Data Sources**: Comprehensive catalog of web mapping services
- **🎲 Randomized Downloads**: Prevents rate limiting by randomizing tile order
- **🔄 Retry Logic**: 3 attempts per tile with timeouts for reliability
- **⚡ Fast Processing**: Basic image validation for speed
- **🎯 Accurate Coordinates**: Fixed tile coordinate calculation
- **🌍 Multiple Standards**: Support for XYZ tiles and WMS services
- **📊 Metadata Support**: Automatic attribution and source information
- **🗂️ Region Integration**: Seamless integration with GRASS computational region

## 📋 Available Data Sources

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

## 🚀 Quick Start

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

## 📖 Usage Examples

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

## ⚙️ Technical Details

### Processing Workflow

1. **Coordinate Transformation**: Converts projected coordinates to lat/lon for XYZ tiles
2. **Tile Download**: Downloads individual tiles with randomized order
3. **Georeferencing**: Creates world files for each tile
4. **Mosaicing**: Combines tiles using GDAL VRT with cubic resampling
5. **Import**: Imports mosaiced result into GRASS with automatic reprojection

### Coordinate System Support

- **Input**: Supports projected or geographic coordinates
- **Transformation**: Automatic conversion to lat/lon for XYZ tiles
- **Output**: Reprojects to current GRASS location projection
- **World Files**: Created in UTM zone 44N (EPSG:32644) for accurate georeferencing

### Performance Features

- **Dynamic Zoom**: Automatic zoom level selection based on region resolution
- **Overlap Buffer**: 10% bbox expansion + 1-tile overlap
- **Memory Efficient**: Temporary file cleanup
- **Error Recovery**: Graceful handling of network issues

## 🛠️ Dependencies

### Required
- **GRASS GIS 8.5+**: For core functionality
- **curl**: For tile downloads
- **gdal**: For VRT creation and import

### Optional
- **pyproj**: For coordinate transformation (auto-installed if needed)

## 📁 Project Structure

```
i.basemap/
├── i.basemap.py          # Main module script
├── i.basemap.md          # Markdown documentation
├── i.basemap.html         # HTML documentation
├── README.md              # This file
├── Makefile              # Build configuration
└── PKG                   # Package metadata
```

## 🔧 Development

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

### Installation

```bash
# Install to GRASS
sudo cp i.basemap.py /usr/local/grass85/scripts/i.basemap
sudo chmod +x /usr/local/grass85/scripts/i.basemap

# Update development version
cp i.basemap.py /usr/local/grass85/scripts/i.basemap
```

## 🐛 Troubleshooting

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

## 📄 License

Copyright (C) 2025 by the GRASS Development Team

This program is free software under the GNU General Public License (>=v2). 
Read the file COPYING that comes with GRASS for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- **Documentation**: See `i.basemap.md` and `i.basemap.html`
- **GRASS Help**: `g.manual i.basemap`
- **Issues**: Report bugs and feature requests to GRASS development team

## 🔗 Related Modules

- `r.in.gdal` - Import raster data using GDAL
- `r.in.wms` - Download web mapping services
- `g.region` - Manage computational region
- `g.proj` - Manage projection information

---

**i.basemap** - Your gateway to comprehensive web mapping data in GRASS GIS! 🗺️✨
