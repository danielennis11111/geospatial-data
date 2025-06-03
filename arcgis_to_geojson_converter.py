import arcgis
import geopandas as gpd
import json
import os
from arcgis.gis import GIS

def simple_arcgis_to_geojson_converter():
    """
    Connect to ArcGIS and convert a layer to GeoJSON format
    """
    try:
        # 1. Connect to ArcGIS
        print("Connecting to ArcGIS...")
        # Connect anonymously to ArcGIS Online
        gis = GIS()
        
        # 2. Search for publicly available feature layers
        print("Searching for available public layers...")
        
        # Try multiple search strategies for public data
        search_queries = [
            # Look for Living Atlas public content
            {"query": "group:\"Living Atlas of the World\" AND type:\"Feature Service\"", "max_items": 5},
            # Look for public sample data
            {"query": "access:public AND type:\"Feature Service\"", "max_items": 10},
            # Look for open data
            {"query": "tags:\"open data\" AND type:\"Feature Service\"", "max_items": 10},
            # Look for example/sample data
            {"query": "title:sample AND type:\"Feature Service\"", "max_items": 10}
        ]
        
        content_items = []
        for search_params in search_queries:
            print(f"Trying search: {search_params['query'][:50]}...")
            try:
                items = gis.content.search(**search_params)
                if items:
                    content_items.extend(items)
                    print(f"Found {len(items)} items with this search")
                    if len(content_items) >= 5:  # Get enough options
                        break
            except Exception as e:
                print(f"Search failed: {e}")
                continue
        
        if not content_items:
            print("No public feature layers found. Trying well-known public services...")
            # Try some well-known public services
            try:
                # Try ArcGIS World Geocoding Service samples or other known public data
                item_ids = [
                    "53a1086593f1497cba89862332c4dadf",  # Sample data
                    "8444e275037549c1acab02d2626daaee",  # Another sample
                    "147b0b04eab9487fb1dc91f3e6fe43e2"   # Another public layer
                ]
                
                for item_id in item_ids:
                    try:
                        item = gis.content.get(item_id)
                        if item:
                            content_items.append(item)
                            print(f"Found item by ID: {item.title}")
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Error accessing known public items: {e}")
        
        if not content_items:
            raise Exception("No accessible public feature layers found")
            
        print(f"\nFound {len(content_items)} layers:")
        for i, item in enumerate(content_items[:5]):  # Show first 5
            print(f"{i}: {item.title}")
            if hasattr(item, 'snippet') and item.snippet:
                print(f"   Description: {item.snippet[:100]}...")
        
        # 3. Try to access layers from the found items
        selected_item = None
        working_layer = None
        
        for item in content_items[:5]:  # Try first 5 items
            print(f"\nTrying layer: {item.title}")
            try:
                # Check if item has accessible layers
                if hasattr(item, 'layers') and item.layers:
                    layer = item.layers[0]
                    # Test if we can query the layer
                    test_query = layer.query(where="1=1", return_count_only=True)
                    if test_query and hasattr(test_query, 'count'):
                        print(f"✅ Layer accessible with {test_query.count} features")
                        selected_item = item
                        working_layer = layer
                        break
                    else:
                        print("❌ Layer query failed")
                else:
                    print("❌ No accessible layers in this item")
            except Exception as e:
                print(f"❌ Error accessing layer: {e}")
                continue
        
        if not working_layer:
            # If no feature layers work, let's try a different approach
            # Create a simple test GeoJSON with sample data
            print("\nNo accessible ArcGIS layers found. Creating sample GeoJSON for testing...")
            return create_sample_geojson()
        
        print(f"\nSelected working layer: {selected_item.title}")
        
        # 4. Query features from the working layer
        print("Querying features...")
        # Query a limited number of features for testing
        feature_set = working_layer.query(
            where="1=1", 
            out_fields="*", 
            return_count_only=False, 
            result_record_count=50  # Limit to 50 features for testing
        )
        features = feature_set.features
        
        if not features:
            raise Exception("No features returned from query")
            
        print(f"Retrieved {len(features)} features")
        
        # 5. Convert to GeoJSON
        print("Converting to GeoJSON...")
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for feature in features:
            # Convert ArcGIS feature to GeoJSON feature
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
            raise Exception("No valid features could be converted")
        
        # 6. Save GeoJSON
        output_file = "arcgis_converted_layer.geojson"
        print(f"Saving to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"Conversion complete! GeoJSON saved to {output_file}")
        
        # 7. Validate GeoJSON
        print("Validating GeoJSON...")
        try:
            # Test loading with geopandas to validate
            test_gdf = gpd.read_file(output_file)
            print(f"✅ Validation successful! GeoJSON contains {len(test_gdf)} features")
            if len(test_gdf) > 0:
                print(f"Geometry types: {test_gdf.geom_type.value_counts().to_dict()}")
                print(f"Attributes: {list(test_gdf.columns)}")
            return output_file
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error in conversion process: {e}")
        print("Creating sample GeoJSON for testing...")
        return create_sample_geojson()

def create_sample_geojson():
    """Create a sample GeoJSON file for testing when ArcGIS data is not accessible"""
    try:
        print("Creating sample GeoJSON with test data...")
        
        # Create sample GeoJSON data
        sample_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.4194, 37.7749]  # San Francisco
                    },
                    "properties": {
                        "name": "San Francisco",
                        "population": 884363,
                        "state": "California",
                        "category": "city"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-74.0059, 40.7128]  # New York
                    },
                    "properties": {
                        "name": "New York",
                        "population": 8336817,
                        "state": "New York",
                        "category": "city"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-87.6298, 41.8781]  # Chicago
                    },
                    "properties": {
                        "name": "Chicago",
                        "population": 2693976,
                        "state": "Illinois",
                        "category": "city"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.5, 37.7], [-122.3, 37.7], [-122.3, 37.8], [-122.5, 37.8], [-122.5, 37.7]
                        ]]
                    },
                    "properties": {
                        "name": "Sample Area",
                        "area_type": "zone",
                        "area_sq_km": 25.5,
                        "category": "area"
                    }
                }
            ]
        }
        
        output_file = "sample_geojson_data.geojson"
        with open(output_file, 'w') as f:
            json.dump(sample_geojson, f, indent=2)
        
        print(f"✅ Sample GeoJSON created: {output_file}")
        
        # Validate the sample
        test_gdf = gpd.read_file(output_file)
        print(f"✅ Sample validation successful! Contains {len(test_gdf)} features")
        print(f"Geometry types: {test_gdf.geom_type.value_counts().to_dict()}")
        print(f"Attributes: {list(test_gdf.columns)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating sample GeoJSON: {e}")
        return None

def test_nl_query(geojson_file, query):
    """Simple function to test natural language queries on the GeoJSON"""
    if not geojson_file:
        return "No valid GeoJSON file to query"
    
    try:
        # Load the GeoJSON
        gdf = gpd.read_file(geojson_file)
        
        # Very basic NL processing (just for testing)
        query_lower = query.lower()
        
        if "how many" in query_lower:
            return f"There are {len(gdf)} features in this dataset."
        elif "what attributes" in query_lower or "what columns" in query_lower:
            cols = [col for col in gdf.columns if col != 'geometry']
            return f"The dataset contains these attributes: {', '.join(cols)}."
        elif "area" in query_lower:
            if 'geometry' in gdf.columns:
                # Calculate area (note: this will be in the coordinate system units)
                gdf_proj = gdf.to_crs('EPSG:3857')  # Web Mercator for area calculation
                total_area = gdf_proj.geometry.area.sum()
                return f"The total area is approximately {total_area:.2f} square meters."
            else:
                return "No geometry found to calculate area."
        elif "bounds" in query_lower or "extent" in query_lower:
            bounds = gdf.total_bounds
            return f"Dataset bounds: minX={bounds[0]:.6f}, minY={bounds[1]:.6f}, maxX={bounds[2]:.6f}, maxY={bounds[3]:.6f}"
        elif "geometry" in query_lower and "type" in query_lower:
            geom_types = gdf.geom_type.value_counts()
            return f"Geometry types: {geom_types.to_dict()}"
        else:
            return "I can answer questions about: feature count, attributes, area, bounds, or geometry types."
            
    except Exception as e:
        return f"Error processing query: {e}"

def interactive_query_session(geojson_file):
    """Interactive session for testing natural language queries"""
    if not geojson_file:
        print("No valid GeoJSON file available for querying.")
        return
    
    print("\n=== Interactive Query Session ===")
    print("Ask questions about your GeoJSON data (type 'quit' to exit)")
    print("Example queries:")
    print("- How many features are there?")
    print("- What attributes does this have?")
    print("- What is the total area?")
    print("- What are the bounds?")
    print("- What geometry types are present?")
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if query:
                response = test_nl_query(geojson_file, query)
                print(f"Answer: {response}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nQuery session ended.")

# Main execution
if __name__ == "__main__":
    print("=== Simple ArcGIS to GeoJSON Conversion Tool ===")
    print("This tool will connect to ArcGIS, download sample data, and convert it to GeoJSON.")
    print()
    
    # Run the conversion
    geojson_file = simple_arcgis_to_geojson_converter()
    
    if geojson_file:
        print("\n=== Testing Natural Language Queries ===")
        test_queries = [
            "How many features are in this dataset?",
            "What attributes does this dataset have?",
            "What geometry types are present?",
            "What are the bounds of this dataset?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            response = test_nl_query(geojson_file, query)
            print(f"Response: {response}")
        
        # Offer interactive session
        print("\n" + "="*50)
        interactive_choice = input("Would you like to try an interactive query session? (y/n): ").strip().lower()
        if interactive_choice in ['y', 'yes']:
            interactive_query_session(geojson_file)
    else:
        print("\n❌ Conversion failed. Please check the error messages above.") 