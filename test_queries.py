#!/usr/bin/env python3

import geopandas as gpd
import os
from arcgis_to_geojson_converter import test_nl_query

def test_geojson_queries():
    """Test natural language queries on existing GeoJSON data"""
    
    # Check if we have any GeoJSON files
    geojson_files = [f for f in os.listdir('.') if f.endswith('.geojson')]
    
    if not geojson_files:
        print("No GeoJSON files found. Please run the converter first.")
        return
    
    geojson_file = geojson_files[0]  # Use the first one found
    print(f"Testing natural language queries on: {geojson_file}")
    print("="*60)
    
    # Load and display basic info about the file
    try:
        gdf = gpd.read_file(geojson_file)
        print(f"Loaded GeoJSON with {len(gdf)} features")
        print(f"Columns: {list(gdf.columns)}")
        print(f"Geometry types: {gdf.geom_type.value_counts().to_dict()}")
        print()
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return
    
    # Test various natural language queries
    test_queries = [
        "How many features are in this dataset?",
        "What attributes does this dataset have?",
        "What geometry types are present?",
        "What are the bounds of this dataset?",
        "What is the total area?",
        "Tell me about the columns",
        "How many points are there?",
        "What's the extent of the data?"
    ]
    
    print("🔍 Testing Natural Language Queries:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\nQ: {query}")
        response = test_nl_query(geojson_file, query)
        print(f"A: {response}")
    
    # Interactive session
    print("\n" + "="*60)
    print("🎯 Interactive Query Session")
    print("Ask your own questions (type 'quit' to exit)")
    print("Examples: 'How many cities?', 'What's the biggest population?'")
    print("-" * 40)
    
    while True:
        try:
            user_query = input("\nYour question: ").strip()
            if user_query.lower() in ['quit', 'exit', 'q', '']:
                break
            if user_query:
                response = test_nl_query(geojson_file, user_query)
                print(f"Answer: {response}")
        except (KeyboardInterrupt, EOFError):
            break
    
    print("\n👋 Query session ended. Thank you!")

if __name__ == "__main__":
    test_geojson_queries() 