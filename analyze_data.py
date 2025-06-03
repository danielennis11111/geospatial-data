#!/usr/bin/env python3
import geopandas as gpd

# Load the converted data
gdf = gpd.read_file('my_arcgis_layer.geojson')
print('🏛️ MARICOPA COUNTY LIBRARY LOCATIONS')
print('=' * 40)
print(f'Total libraries: {len(gdf)}')
print(f'Attributes: {list(gdf.columns)}')
print()
print('📍 Library Names:')
for i, row in gdf.iterrows():
    if 'Library' in row:
        print(f'  • {row["Library"]}')
print()
print('📊 Data Quality Check:')
print(f'  • Features with geometry: {gdf.geometry.notna().sum()}')
print(f'  • Features with coordinates: {gdf["X"].notna().sum()}')
print(f'  • Coordinate bounds: X({gdf["X"].min():.3f} to {gdf["X"].max():.3f}), Y({gdf["Y"].min():.3f} to {gdf["Y"].max():.3f})') 