#!/usr/bin/env python3
"""
Fetch ALL Arizona Census Tracts with Household Data
Using ArcGIS API to get complete dataset beyond the 500 tract limit
"""

import json
import geopandas as gpd
import pandas as pd
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
    print("Please ensure config.py has the correct ARCGIS_CONFIG structure.")
    exit(1)

def connect_to_arcgis():
    """Connect to ArcGIS organization"""
    print("🔗 CONNECTING TO ARCGIS")
    print("=" * 40)
    
    try:
        gis = GIS(ARCGIS_ORG_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD)
        print(f"✅ Connected as: {gis.properties.user.fullName}")
        print(f"📍 Organization: {gis.properties.name}")
        print(f"👤 Role: {gis.properties.user.role}")
        return gis
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def get_all_arizona_tracts(gis):
    """Get ALL Arizona census tracts with household data"""
    print(f"\n📊 FETCHING ALL ARIZONA CENSUS TRACTS")
    print("=" * 40)
    
    # Use the known item ID and sublayer
    item_id = "5270c859f0d44cc089385f42afe8d469"
    sublayer_id = 10  # "Percent with a fixed broadband subscription by tract"
    
    try:
        # Get the item
        item = gis.content.get(item_id)
        print(f"📋 Found item: {item.title}")
        
        # Access the specific sublayer
        layers = item.layers
        if sublayer_id >= len(layers):
            print(f"❌ Sublayer {sublayer_id} not found. Available layers: {len(layers)}")
            return None
            
        feature_layer = layers[sublayer_id]
        
        print(f"🎯 Target layer: {feature_layer.properties.name}")
        print(f"📍 Layer URL: {feature_layer.url}")
        
        # Query ALL features with pagination if necessary
        print("🔄 Querying all features...")
        
        all_features = []
        offset = 0
        batch_size = 1000  # Query in batches of 1000
        
        while True:
            # Query with offset for pagination
            query_result = feature_layer.query(
                where="statefp = '04'",  # Arizona state FIPS code
                out_fields="*",
                return_geometry=True,
                result_offset=offset,
                result_record_count=batch_size
            )
            
            batch_features = query_result.features
            if not batch_features:
                break
                
            all_features.extend(batch_features)
            print(f"📥 Retrieved {len(batch_features)} features (total: {len(all_features)})")
            
            # If we got fewer than batch_size, we've reached the end
            if len(batch_features) < batch_size:
                break
                
            offset += batch_size
        
        print(f"✅ Total features retrieved: {len(all_features)}")
        
        # Convert to GeoJSON format
        print("🔄 Converting to GeoJSON format...")
        
        geojson_features = []
        for feature in all_features:
            geojson_feature = {
                "type": "Feature",
                "geometry": feature.geometry if hasattr(feature, 'geometry') else None,
                "properties": feature.attributes if hasattr(feature, 'attributes') else {}
            }
            geojson_features.append(geojson_feature)
        
        # Create complete GeoJSON
        complete_geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        # Save to file
        output_file = "all_arizona_tracts.geojson"
        print(f"💾 Saving to {output_file}...")
        
        with open(output_file, 'w') as f:
            json.dump(complete_geojson, f)
        
        print(f"✅ Complete dataset saved to {output_file}")
        
        # Load as GeoDataFrame for analysis
        gdf = gpd.read_file(output_file)
        print(f"📊 Loaded GeoDataFrame with {len(gdf)} features")
        
        # Display basic info about the dataset
        print(f"\n📋 DATASET OVERVIEW:")
        print(f"  • Total census tracts: {len(gdf)}")
        print(f"  • Total columns: {len(gdf.columns)}")
        
        # Check for household fields
        household_fields = [col for col in gdf.columns if 'household' in col.lower()]
        if household_fields:
            print(f"  • Household fields found: {len(household_fields)}")
            for field in household_fields:
                if gdf[field].dtype in ['int64', 'float64']:
                    total = gdf[field].sum()
                    print(f"    - {field}: {total:,}")
        
        return gdf
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def analyze_complete_dataset(gdf):
    """Analyze the complete Arizona census tract dataset"""
    print(f"\n🔍 COMPLETE ARIZONA ANALYSIS")
    print("=" * 40)
    
    # County-level summary
    if 'namelsadco' in gdf.columns:
        print(f"📍 Counties represented:")
        county_counts = gdf['namelsadco'].value_counts()
        for county, count in county_counts.items():
            print(f"  • {county}: {count} tracts")
        print(f"  • Total counties: {len(county_counts)}")
    
    # Household analysis
    if 'total_households' in gdf.columns:
        total_households = gdf['total_households'].sum()
        valid_tracts = gdf['total_households'].notna().sum()
        print(f"\n🏠 STATEWIDE HOUSEHOLD TOTALS:")
        print(f"  • Total households: {total_households:,}")
        print(f"  • Valid tracts: {valid_tracts}/{len(gdf)}")
        print(f"  • Average per tract: {total_households/valid_tracts:.1f}")
        print(f"  • Coverage: {valid_tracts/len(gdf)*100:.1f}% of tracts")
    
    # Digital equity metrics across all tracts
    digital_fields = ['any_computing_device', 'broadband_fixed', 'pct_smartphone_only']
    available_fields = [field for field in digital_fields if field in gdf.columns]
    
    if available_fields:
        print(f"\n💻 STATEWIDE DIGITAL EQUITY (All Tracts):")
        for field in available_fields:
            if gdf[field].dtype in ['int64', 'float64']:
                mean_val = gdf[field].mean()
                median_val = gdf[field].median()
                min_val = gdf[field].min()
                max_val = gdf[field].max()
                print(f"  • {field.replace('_', ' ').title()}:")
                print(f"    - Mean: {mean_val:.1f}%")
                print(f"    - Median: {median_val:.1f}%")
                print(f"    - Range: {min_val:.1f}% - {max_val:.1f}%")
    
    return gdf

def main():
    """Main execution function"""
    print("🌵 COMPLETE ARIZONA CENSUS TRACT ANALYSIS")
    print("=" * 50)
    
    # Connect to ArcGIS
    gis = connect_to_arcgis()
    if not gis:
        return
    
    # Get all Arizona tracts
    gdf = get_all_arizona_tracts(gis)
    if gdf is None:
        return
    
    # Analyze complete dataset
    analyze_complete_dataset(gdf)
    
    print(f"\n✅ Complete analysis finished!")
    print(f"📁 Full dataset saved as: all_arizona_tracts.geojson")

if __name__ == "__main__":
    main() 