#!/usr/bin/env python3
"""
ArcGIS to GeoJSON Converter - Connect to Your Account
This script connects to your ArcGIS account and converts your layers
"""

import arcgis
import geopandas as gpd
import json
import os
from arcgis.gis import GIS
from arcgis_to_geojson_converter import test_nl_query

def connect_to_my_arcgis():
    """Connect to user's ArcGIS account using credentials from config.py"""
    try:
        # Import configuration
        try:
            from config import ARCGIS_CONFIG, CONVERSION_CONFIG
        except ImportError:
            print("❌ Error: config.py not found or not properly configured")
            print("Please edit config.py with your ArcGIS credentials")
            return None, None
        
        # Check if credentials are provided
        if not ARCGIS_CONFIG.get('username') or not ARCGIS_CONFIG.get('password'):
            print("❌ Error: Please add your ArcGIS username and password to config.py")
            print("Edit the config.py file and fill in:")
            print("  'username': 'your_arcgis_username'")
            print("  'password': 'your_arcgis_password'")
            return None, None
        
        print("🔐 Connecting to your ArcGIS account...")
        print(f"   URL: {ARCGIS_CONFIG['url']}")
        print(f"   Username: {ARCGIS_CONFIG['username']}")
        
        # Connect to ArcGIS with credentials
        gis = GIS(
            url=ARCGIS_CONFIG['url'],
            username=ARCGIS_CONFIG['username'],
            password=ARCGIS_CONFIG['password']
        )
        
        print(f"✅ Successfully connected to ArcGIS!")
        print(f"   Logged in as: {gis.users.me.username}")
        print(f"   Full name: {gis.users.me.fullName}")
        print(f"   Role: {gis.users.me.role}")
        
        return gis, CONVERSION_CONFIG
        
    except Exception as e:
        print(f"❌ Error connecting to ArcGIS: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your username and password in config.py")
        print("2. Verify you have access to ArcGIS Online")
        print("3. Check if your account requires two-factor authentication")
        return None, None

def search_my_layers(gis, config):
    """Search for layers in the user's ArcGIS account"""
    print("\n🔍 Searching for your layers...")
    
    all_items = []
    
    # Search using configured queries
    for query in config['search_queries']:
        if query and 'your_username' not in query:  # Skip placeholder queries
            print(f"   Searching: {query}")
            try:
                items = gis.content.search(query=query, max_items=20)
                if items:
                    all_items.extend(items)
                    print(f"   Found {len(items)} items")
                else:
                    print(f"   No items found")
            except Exception as e:
                print(f"   Search failed: {e}")
    
    # Search for specific item IDs
    for item_id in config.get('item_ids', []):
        if item_id:
            try:
                item = gis.content.get(item_id)
                if item:
                    all_items.append(item)
                    print(f"   Found item by ID: {item.title}")
            except Exception as e:
                print(f"   Error getting item {item_id}: {e}")
    
    # Remove duplicates
    unique_items = list({item.id: item for item in all_items}.values())
    
    # Filter for Feature Services/Layers
    feature_items = [item for item in unique_items if 
                    item.type in ['Feature Service', 'Feature Layer']]
    
    print(f"\n📋 Found {len(feature_items)} feature layers:")
    for i, item in enumerate(feature_items[:10]):  # Show first 10
        print(f"   {i}: {item.title}")
        print(f"      Type: {item.type}")
        if hasattr(item, 'snippet') and item.snippet:
            print(f"      Description: {item.snippet[:80]}...")
        print(f"      Owner: {item.owner}")
        print()
    
    return feature_items

def convert_my_layer(gis, items, config):
    """Convert a selected layer to GeoJSON"""
    if not items:
        print("❌ No feature layers found to convert")
        return None
    
    # Let user select a layer
    print("Which layer would you like to convert?")
    for i, item in enumerate(items[:10]):
        print(f"   {i}: {item.title}")
    
    try:
        choice = input(f"\nEnter layer number (0-{min(9, len(items)-1)}) or press Enter for first layer: ").strip()
        if choice == '':
            selected_idx = 0
        else:
            selected_idx = int(choice)
        
        if selected_idx < 0 or selected_idx >= len(items):
            print("Invalid selection, using first layer")
            selected_idx = 0
            
    except (ValueError, KeyboardInterrupt):
        print("Using first layer")
        selected_idx = 0
    
    selected_item = items[selected_idx]
    print(f"\n🎯 Selected: {selected_item.title}")
    
    try:
        # Access the layer
        if hasattr(selected_item, 'layers') and selected_item.layers:
            layer = selected_item.layers[0]
        else:
            print("❌ Selected item doesn't have accessible layers")
            return None
        
        # Test access
        print("Testing layer access...")
        count_query = layer.query(where="1=1", return_count_only=True)
        total_features = count_query.count if hasattr(count_query, 'count') else 0
        print(f"✅ Layer accessible with {total_features} total features")
        
        # Query features
        max_features = min(config['max_features'], total_features)
        print(f"Downloading {max_features} features...")
        
        feature_set = layer.query(
            where="1=1",
            out_fields="*",
            return_count_only=False,
            result_record_count=max_features
        )
        features = feature_set.features
        
        if not features:
            print("❌ No features returned from query")
            return None
        
        print(f"Retrieved {len(features)} features")
        
        # Convert to GeoJSON
        print("Converting to GeoJSON...")
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for feature in features:
            try:
                geojson_feature = {
                    "type": "Feature",
                    "geometry": dict(feature.geometry) if feature.geometry else None,
                    "properties": dict(feature.attributes) if feature.attributes else {}
                }
                geojson["features"].append(geojson_feature)
            except Exception as e:
                print(f"Warning: Skipping feature due to error: {e}")
                continue
        
        if not geojson["features"]:
            print("❌ No valid features could be converted")
            return None
        
        # Save GeoJSON
        output_file = config['output_file']
        print(f"Saving to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"✅ Conversion complete! GeoJSON saved to {output_file}")
        
        # Validate
        print("Validating GeoJSON...")
        try:
            test_gdf = gpd.read_file(output_file)
            print(f"✅ Validation successful!")
            print(f"   Features: {len(test_gdf)}")
            print(f"   Geometry types: {test_gdf.geom_type.value_counts().to_dict()}")
            print(f"   Attributes: {[col for col in test_gdf.columns if col != 'geometry']}")
            return output_file
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error converting layer: {e}")
        return None

def main():
    """Main function to connect to ArcGIS and convert layers"""
    print("🌍 ArcGIS to GeoJSON Converter - Your Account")
    print("=" * 50)
    
    # Connect to ArcGIS
    gis, config = connect_to_my_arcgis()
    if not gis:
        return
    
    # Search for layers
    items = search_my_layers(gis, config)
    if not items:
        print("❌ No feature layers found in your account")
        print("Try modifying the search queries in config.py")
        return
    
    # Convert a layer
    geojson_file = convert_my_layer(gis, items, config)
    
    if geojson_file:
        # Test natural language queries
        print(f"\n🤖 Testing Natural Language Queries on Your Data:")
        print("-" * 50)
        
        test_queries = [
            "How many features are in this dataset?",
            "What attributes does this dataset have?",
            "What geometry types are present?",
            "What are the bounds of this dataset?"
        ]
        
        for query in test_queries:
            print(f"\nQ: {query}")
            response = test_nl_query(geojson_file, query)
            print(f"A: {response}")
        
        print(f"\n✅ Success! Your ArcGIS data has been converted to GeoJSON")
        print(f"File: {geojson_file}")
    else:
        print(f"\n❌ Conversion failed")

if __name__ == "__main__":
    main() 