# ArcGIS to GeoJSON Converter

A simple tool to convert ArcGIS feature layers to GeoJSON format with basic natural language query capabilities.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional: Configure ArcGIS Credentials**
   - For public data, no credentials are needed
   - For private data, modify the script to include your ArcGIS credentials

## Usage

### Basic Conversion
Run the main script to test the conversion with public data:
```bash
python arcgis_to_geojson_converter.py
```

### What the Script Does
1. **Connects to ArcGIS Online** (using anonymous access for public data)
2. **Searches for available feature layers** (starts with Esri sample data)
3. **Downloads and converts** the first available layer to GeoJSON
4. **Validates** the output using GeoPandas
5. **Tests natural language queries** on the converted data

### Sample Output
- `arcgis_converted_layer.geojson` - The converted GeoJSON file
- Console output showing the conversion process and validation results

### Natural Language Queries
The tool supports basic queries like:
- "How many features are there?"
- "What attributes does this dataset have?"
- "What is the total area?"
- "What are the bounds?"
- "What geometry types are present?"

## Customizing for Your Data

To use with your own ArcGIS data:

1. **Add your credentials:**
   ```python
   gis = GIS("https://your-portal.com", "username", "password")
   ```

2. **Search for specific layers:**
   ```python
   content_items = gis.content.search("your search terms", item_type="Feature Layer")
   ```

3. **Access specific items by ID:**
   ```python
   item = gis.content.get("your-item-id")
   ```

## Requirements
- Python 3.8+
- ArcGIS API for Python
- GeoPandas
- Internet connection for ArcGIS Online access

## Troubleshooting

**Common Issues:**
- **No layers found:** Try different search terms or ensure you have access to the layers
- **Validation fails:** Check that the source data has valid geometries
- **Import errors:** Ensure all dependencies are installed correctly

**For private/enterprise data:**
- Ensure you have proper permissions
- Verify your ArcGIS Portal URL and credentials
- Check that the layer allows data export 