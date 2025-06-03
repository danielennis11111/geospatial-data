#!/usr/bin/env python3
"""
Explore all sublayers in the ACS 2023 Arizona Tracts item
to find the correct layer with household data
"""

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import warnings
warnings.filterwarnings('ignore')

# Import credentials
try:
    from config import ARCGIS_CONFIG
    ARCGIS_ORG_URL = ARCGIS_CONFIG['url']
    ARCGIS_USERNAME = ARCGIS_CONFIG['username']
    ARCGIS_PASSWORD = ARCGIS_CONFIG['password']
except ImportError:
    print("❌ config.py not found. Please ensure your ArcGIS credentials are set up.")
    exit(1)
except KeyError as e:
    print(f"❌ Missing configuration key: {e}")
    exit(1)

def explore_sublayers():
    """Explore all sublayers to find household data"""
    print("🔍 EXPLORING ACS 2023 ARIZONA TRACTS SUBLAYERS")
    print("=" * 50)
    
    try:
        # Connect to ArcGIS
        gis = GIS(ARCGIS_ORG_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD)
        print(f"✅ Connected as: {gis.properties.user.fullName}")
        
        # Get the item
        item_id = "5270c859f0d44cc089385f42afe8d469"
        item = gis.content.get(item_id)
        print(f"📋 Item: {item.title}")
        print(f"🔗 URL: {item.url}")
        
        # Get all layers
        layers = item.layers
        print(f"\n📊 Found {len(layers)} sublayers:")
        
        for i, layer in enumerate(layers):
            print(f"\n🎯 Sublayer {i}:")
            print(f"  • Name: {layer.properties.name}")
            print(f"  • URL: {layer.url}")
            
            # Try to get field information
            try:
                fields = layer.properties.fields
                field_names = [field['name'] for field in fields]
                
                # Look for household-related fields
                household_fields = [name for name in field_names if any(keyword in name.lower() 
                                  for keyword in ['household', 'hh', 'housing', 'total_'])]
                
                print(f"  • Total fields: {len(field_names)}")
                if household_fields:
                    print(f"  • Household-related fields: {household_fields[:5]}{'...' if len(household_fields) > 5 else ''}")
                else:
                    print(f"  • Sample fields: {field_names[:5]}{'...' if len(field_names) > 5 else ''}")
                
                # Try to get a count
                try:
                    count_result = layer.query(where="1=1", return_count_only=True)
                    feature_count = count_result.features[0].attributes.get('count', 'Unknown') if count_result.features else 'Unknown'
                    print(f"  • Feature count: {feature_count}")
                except:
                    print(f"  • Feature count: Unable to query")
                    
            except Exception as e:
                print(f"  • Error getting field info: {e}")
        
        # Test a specific layer that might have household data
        print(f"\n🎯 TESTING SPECIFIC LAYERS:")
        test_layers = [0, 1, 2]  # Test first few layers
        
        for layer_id in test_layers:
            if layer_id < len(layers):
                layer = layers[layer_id]
                print(f"\n📋 Testing Layer {layer_id}: {layer.properties.name}")
                
                try:
                    # Try a small query to see data structure
                    result = layer.query(where="statefp = '04'", out_fields="*", result_record_count=1)
                    if result.features:
                        attributes = result.features[0].attributes
                        print(f"  • Sample attributes ({len(attributes)} total):")
                        for key, value in list(attributes.items())[:10]:
                            print(f"    - {key}: {value}")
                    else:
                        print(f"  • No features found")
                except Exception as e:
                    print(f"  • Error querying: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_sublayers() 