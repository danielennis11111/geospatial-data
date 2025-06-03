#!/usr/bin/env python3
"""
Convert specific ArcGIS layer and perform geospatial analysis
"""

import arcgis
import geopandas as gpd
import pandas as pd
import numpy as np
import json
from arcgis.gis import GIS
from config import ARCGIS_CONFIG

def connect_and_get_specific_layer():
    """Connect to ArcGIS and get the specific layer"""
    try:
        # Connect to ArcGIS
        print("🔐 Connecting to ArcGIS...")
        gis = GIS(
            url=ARCGIS_CONFIG['url'],
            username=ARCGIS_CONFIG['username'],
            password=ARCGIS_CONFIG['password']
        )
        print(f"✅ Connected as: {gis.users.me.username}")
        
        # Get the specific item
        item_id = "5270c859f0d44cc089385f42afe8d469"
        sublayer_index = 38
        
        print(f"🎯 Getting specific layer: {item_id}, sublayer {sublayer_index}")
        item = gis.content.get(item_id)
        
        if not item:
            raise Exception(f"Could not find item with ID: {item_id}")
        
        print(f"📋 Found item: {item.title}")
        print(f"   Type: {item.type}")
        print(f"   Owner: {item.owner}")
        if hasattr(item, 'snippet') and item.snippet:
            print(f"   Description: {item.snippet}")
        
        # Access the specific sublayer
        if hasattr(item, 'layers') and item.layers:
            if sublayer_index < len(item.layers):
                layer = item.layers[sublayer_index]
                print(f"✅ Accessing sublayer {sublayer_index}: {layer.properties.name}")
            else:
                print(f"Available sublayers: {len(item.layers)}")
                for i, lyr in enumerate(item.layers):
                    print(f"   {i}: {lyr.properties.name}")
                # Use the last available layer if sublayer index is out of range
                layer = item.layers[-1]
                print(f"Using last available layer: {layer.properties.name}")
        else:
            raise Exception("Item doesn't have accessible layers")
        
        return gis, layer
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def convert_layer_to_geojson(layer, max_features=1000):
    """Convert the layer to GeoJSON with more features for analysis"""
    try:
        # Test access and get total count
        print("🔍 Analyzing layer structure...")
        count_query = layer.query(where="1=1", return_count_only=True)
        total_features = count_query.count if hasattr(count_query, 'count') else 0
        print(f"   Total features available: {total_features}")
        
        # Get field information
        if hasattr(layer, 'properties') and hasattr(layer.properties, 'fields'):
            fields = layer.properties.fields
            print(f"   Available fields: {len(fields)}")
            for field in fields[:10]:  # Show first 10 fields
                print(f"     • {field['name']} ({field['type']})")
        
        # Query features
        features_to_get = min(max_features, total_features) if total_features > 0 else max_features
        print(f"📥 Downloading {features_to_get} features...")
        
        feature_set = layer.query(
            where="1=1",
            out_fields="*",
            return_count_only=False,
            result_record_count=features_to_get
        )
        features = feature_set.features
        
        if not features:
            print("❌ No features returned")
            return None
        
        print(f"✅ Retrieved {len(features)} features")
        
        # Convert to GeoJSON
        print("🔄 Converting to GeoJSON...")
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        conversion_errors = 0
        for i, feature in enumerate(features):
            try:
                geojson_feature = {
                    "type": "Feature",
                    "geometry": dict(feature.geometry) if feature.geometry else None,
                    "properties": dict(feature.attributes) if feature.attributes else {}
                }
                geojson["features"].append(geojson_feature)
            except Exception as e:
                conversion_errors += 1
                if conversion_errors <= 3:  # Show first few errors
                    print(f"   Warning: Error converting feature {i}: {e}")
        
        if conversion_errors > 0:
            print(f"   Total conversion errors: {conversion_errors}")
        
        # Save GeoJSON
        output_file = "specific_layer_analysis.geojson"
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"💾 Saved to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

def perform_geospatial_analysis(geojson_file):
    """Perform comprehensive geospatial analysis"""
    try:
        print("\n🔬 PERFORMING GEOSPATIAL ANALYSIS")
        print("=" * 50)
        
        # Load data
        gdf = gpd.read_file(geojson_file)
        print(f"📊 Loaded {len(gdf)} features for analysis")
        
        # Basic info
        print(f"\n📋 DATASET OVERVIEW:")
        print(f"   • Total features: {len(gdf)}")
        print(f"   • Geometry types: {dict(gdf.geom_type.value_counts())}")
        print(f"   • Coordinate system: {gdf.crs}")
        
        # Attribute analysis
        numeric_cols = gdf.select_dtypes(include=[np.number]).columns.tolist()
        if 'geometry' in numeric_cols:
            numeric_cols.remove('geometry')
        
        text_cols = gdf.select_dtypes(include=['object', 'string']).columns.tolist()
        if 'geometry' in text_cols:
            text_cols.remove('geometry')
        
        print(f"\n📈 ATTRIBUTE ANALYSIS:")
        print(f"   • Numeric fields: {len(numeric_cols)} - {numeric_cols[:5]}")
        print(f"   • Text fields: {len(text_cols)} - {text_cols[:5]}")
        
        # Numeric field statistics
        if numeric_cols:
            print(f"\n📊 NUMERIC FIELD STATISTICS:")
            for col in numeric_cols[:3]:  # Top 3 numeric fields
                if col in gdf.columns:
                    series = gdf[col].dropna()
                    if len(series) > 0:
                        print(f"   {col}:")
                        print(f"     Min: {series.min():.2f}, Max: {series.max():.2f}")
                        print(f"     Mean: {series.mean():.2f}, Median: {series.median():.2f}")
                        print(f"     Std Dev: {series.std():.2f}")
        
        # Spatial analysis
        print(f"\n🗺️ SPATIAL ANALYSIS:")
        
        # Bounds and extent
        bounds = gdf.total_bounds
        print(f"   • Bounding box: ")
        print(f"     West: {bounds[0]:.6f}, South: {bounds[1]:.6f}")
        print(f"     East: {bounds[2]:.6f}, North: {bounds[3]:.6f}")
        
        # Calculate area/length if possible
        if gdf.crs and gdf.crs.is_geographic:
            # Convert to projected CRS for area calculations
            print("   • Converting to projected coordinates for measurements...")
            try:
                # Use Web Mercator for approximate calculations
                gdf_proj = gdf.to_crs('EPSG:3857')
                
                if 'Polygon' in gdf.geom_type.values:
                    areas = gdf_proj[gdf_proj.geom_type == 'Polygon'].geometry.area
                    if len(areas) > 0:
                        print(f"   • Polygon areas (sq meters):")
                        print(f"     Min: {areas.min():.0f}, Max: {areas.max():.0f}")
                        print(f"     Total area: {areas.sum():.0f}")
                
                if 'LineString' in gdf.geom_type.values:
                    lengths = gdf_proj[gdf_proj.geom_type == 'LineString'].geometry.length
                    if len(lengths) > 0:
                        print(f"   • Line lengths (meters):")
                        print(f"     Min: {lengths.min():.0f}, Max: {lengths.max():.0f}")
                        print(f"     Total length: {lengths.sum():.0f}")
                        
            except Exception as e:
                print(f"   • Area/length calculation error: {e}")
        
        # Point clustering analysis (if points exist)
        if 'Point' in gdf.geom_type.values:
            points = gdf[gdf.geom_type == 'Point']
            if len(points) > 3:
                print(f"\n🎯 POINT PATTERN ANALYSIS:")
                print(f"   • Total points: {len(points)}")
                
                # Calculate centroids and spread
                coords = np.array([[geom.x, geom.y] for geom in points.geometry])
                centroid = coords.mean(axis=0)
                print(f"   • Centroid: ({centroid[0]:.6f}, {centroid[1]:.6f})")
                
                # Calculate distances from centroid
                distances = np.sqrt(((coords - centroid) ** 2).sum(axis=1))
                print(f"   • Distance from centroid:")
                print(f"     Mean: {distances.mean():.3f}, Max: {distances.max():.3f}")
        
        # Sample features
        print(f"\n🔍 SAMPLE FEATURES:")
        for i, (idx, row) in enumerate(gdf.head(3).iterrows()):
            print(f"   Feature {i+1}:")
            print(f"     Geometry: {row.geometry.geom_type if row.geometry else 'None'}")
            # Show some attribute values
            for col in gdf.columns[:3]:
                if col != 'geometry':
                    value = row[col]
                    if pd.notna(value):
                        if isinstance(value, str) and len(str(value)) > 50:
                            print(f"     {col}: {str(value)[:50]}...")
                        else:
                            print(f"     {col}: {value}")
        
        # Look for interesting patterns
        print(f"\n🔍 PATTERN DETECTION:")
        
        # Check for null values
        null_counts = gdf.isnull().sum()
        if null_counts.sum() > 0:
            print(f"   • Missing data detected:")
            for col, count in null_counts[null_counts > 0].items():
                if col != 'geometry':
                    print(f"     {col}: {count} missing values ({count/len(gdf)*100:.1f}%)")
        
        # Check for duplicates
        if len(numeric_cols) > 0:
            duplicates = gdf.duplicated(subset=numeric_cols[:3]).sum()
            print(f"   • Duplicate features: {duplicates}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def main():
    """Main function"""
    print("🌍 ArcGIS SPECIFIC LAYER ANALYSIS")
    print("=" * 40)
    
    # Connect and get layer
    gis, layer = connect_and_get_specific_layer()
    if not layer:
        return
    
    # Convert to GeoJSON
    geojson_file = convert_layer_to_geojson(layer, max_features=500)
    if not geojson_file:
        return
    
    # Perform analysis
    success = perform_geospatial_analysis(geojson_file)
    
    if success:
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📁 Data saved to: {geojson_file}")
        print(f"🎯 This layer is ready for advanced GIS analysis!")
    else:
        print(f"\n❌ Analysis failed")

if __name__ == "__main__":
    main() 