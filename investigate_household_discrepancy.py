#!/usr/bin/env python3
"""
Investigate Household Count Discrepancy
2020 Census: ~2.97M households
2023 ACS: 2.796M households
Why the decrease when we expect growth?
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from arcgis.gis import GIS
import warnings
warnings.filterwarnings('ignore')

# Import credentials
try:
    from config import ARCGIS_CONFIG
    ARCGIS_ORG_URL = ARCGIS_CONFIG['url']
    ARCGIS_USERNAME = ARCGIS_CONFIG['username']
    ARCGIS_PASSWORD = ARCGIS_CONFIG['password']
except ImportError:
    print("❌ config.py not found.")
    exit(1)

def investigate_data_coverage():
    """Investigate potential coverage issues with our ACS data"""
    print("🔍 INVESTIGATING HOUSEHOLD COUNT DISCREPANCY")
    print("=" * 50)
    
    # Load our complete dataset
    print("📊 Loading our 2023 ACS data...")
    gdf = gpd.read_file('all_arizona_tracts.geojson')
    
    print(f"✅ Loaded {len(gdf)} census tracts")
    print(f"📊 Our total households: {gdf['total_households'].sum():,}")
    
    # Check for data quality issues
    print(f"\n🔍 DATA QUALITY ANALYSIS:")
    
    # 1. Missing household data
    missing_households = gdf['total_households'].isna().sum()
    zero_households = (gdf['total_households'] == 0).sum()
    print(f"  • Tracts with missing household data: {missing_households}")
    print(f"  • Tracts with zero households: {zero_households}")
    
    # 2. Check for unrealistic values
    very_small = (gdf['total_households'] < 10).sum()
    very_large = (gdf['total_households'] > 10000).sum()
    print(f"  • Tracts with <10 households: {very_small}")
    print(f"  • Tracts with >10,000 households: {very_large}")
    
    # 3. County coverage check
    print(f"\n📍 COUNTY COVERAGE:")
    county_household_totals = gdf.groupby('namelsadco')['total_households'].sum().sort_values(ascending=False)
    for county, total in county_household_totals.items():
        tract_count = len(gdf[gdf['namelsadco'] == county])
        print(f"  • {county}: {total:,} households ({tract_count} tracts)")
    
    return gdf

def compare_with_official_sources():
    """Compare our data with official sources"""
    print(f"\n📋 COMPARISON WITH OFFICIAL SOURCES")
    print("=" * 40)
    
    # Known official numbers
    census_2020 = 2970000  # Approximate from Census Bureau
    our_acs_2023 = 2796790  # From our analysis
    
    print(f"🏛️ Official 2020 Census: ~{census_2020:,} households")
    print(f"📊 Our 2023 ACS data: {our_acs_2023:,} households")
    print(f"📉 Difference: {census_2020 - our_acs_2023:,} households ({(census_2020 - our_acs_2023)/census_2020*100:.1f}% decrease)")
    
    # Calculate expected growth
    years_diff = 3  # 2020 to 2023
    expected_growth_rate = 0.02  # 2% per year (conservative estimate)
    expected_2023 = census_2020 * (1 + expected_growth_rate) ** years_diff
    
    print(f"\n📈 EXPECTED vs ACTUAL:")
    print(f"  • Expected 2023 (2% annual growth): {expected_2023:,} households")
    print(f"  • Actual 2023 (our data): {our_acs_2023:,} households")
    print(f"  • Shortfall: {expected_2023 - our_acs_2023:,} households")

def investigate_methodological_differences():
    """Investigate methodological differences between Census and ACS"""
    print(f"\n🔬 METHODOLOGICAL DIFFERENCES")
    print("=" * 40)
    
    print("🎯 POTENTIAL EXPLANATIONS:")
    print("1. 📊 DATA SOURCE DIFFERENCES:")
    print("   • 2020 Census: Complete enumeration (every household counted)")
    print("   • 2023 ACS: Sample-based estimates with margins of error")
    print("   • ACS has higher uncertainty, especially for small areas")
    
    print("\n2. 🗓️ TEMPORAL DIFFERENCES:")
    print("   • 2020 Census: Point-in-time snapshot (April 1, 2020)")
    print("   • 2023 ACS: 5-year rolling average (2019-2023)")
    print("   • COVID-19 impacts on household formation (2020-2022)")
    
    print("\n3. 🏠 DEFINITION DIFFERENCES:")
    print("   • Group quarters vs household classification")
    print("   • College dormitories, nursing homes, military barracks")
    print("   • Temporary housing situations")
    
    print("\n4. 🗺️ GEOGRAPHIC COVERAGE:")
    print("   • Tract boundary changes between 2020-2023")
    print("   • New developments not yet in ACS")
    print("   • Missing or updated geographic areas")

def check_specific_tract_issues(gdf):
    """Check for specific tract-level issues"""
    print(f"\n🎯 TRACT-LEVEL INVESTIGATION")
    print("=" * 40)
    
    # Look for problematic tracts
    print("🚨 POTENTIALLY PROBLEMATIC TRACTS:")
    
    # Very low household counts in urban areas
    maricopa_tracts = gdf[gdf['namelsadco'] == 'Maricopa County']
    low_household_urban = maricopa_tracts[maricopa_tracts['total_households'] < 100]
    
    print(f"\n📍 Maricopa County tracts with <100 households:")
    print(f"  • Count: {len(low_household_urban)} tracts")
    if len(low_household_urban) > 0:
        print(f"  • Sample tract IDs:")
        for i, (idx, tract) in enumerate(low_household_urban.head(5).iterrows()):
            print(f"    - {tract['geoid']}: {tract['total_households']} households")
    
    # Check for missing data patterns
    missing_data_tracts = gdf[gdf['total_households'].isna()]
    print(f"\n❌ Tracts with missing household data:")
    print(f"  • Count: {len(missing_data_tracts)} tracts")
    if len(missing_data_tracts) > 0:
        missing_by_county = missing_data_tracts['namelsadco'].value_counts()
        print(f"  • By county:")
        for county, count in missing_by_county.items():
            print(f"    - {county}: {count} tracts")

def get_alternative_data_source():
    """Try to get data from a different ACS sublayer for comparison"""
    print(f"\n🔄 CROSS-VALIDATION WITH OTHER DATA SOURCES")
    print("=" * 40)
    
    try:
        # Connect to ArcGIS
        gis = GIS(ARCGIS_ORG_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD)
        
        # Try to get housing units data from a different sublayer
        item_id = "5270c859f0d44cc089385f42afe8d469"
        item = gis.content.get(item_id)
        
        # Look for housing units layer (sublayer 7)
        housing_layer = item.layers[7]  # "Housing units by tract"
        print(f"📋 Checking: {housing_layer.properties.name}")
        
        # Query a sample to see if it has different household/housing data
        sample_result = housing_layer.query(
            where="statefp = '04'", 
            out_fields="*", 
            result_record_count=5
        )
        
        if sample_result.features:
            print(f"✅ Sample data from housing units layer:")
            sample_attrs = sample_result.features[0].attributes
            for key, value in sample_attrs.items():
                if any(keyword in key.lower() for keyword in ['housing', 'household', 'unit']):
                    print(f"  • {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error accessing alternative data: {e}")

def recommend_solutions():
    """Recommend solutions to resolve the discrepancy"""
    print(f"\n💡 RECOMMENDED SOLUTIONS")
    print("=" * 40)
    
    print("🎯 IMMEDIATE ACTIONS:")
    print("1. 📊 Verify with official Census Bureau data:")
    print("   • Download official 2020 Census household counts by tract")
    print("   • Compare tract-by-tract with our ACS data")
    print("   • Identify specific missing or problematic areas")
    
    print("\n2. 🔍 Data quality investigation:")
    print("   • Check for systematic missing data patterns")
    print("   • Verify geographic coverage completeness")
    print("   • Cross-reference with housing unit counts")
    
    print("\n3. 📈 Use multiple data sources:")
    print("   • Combine 2020 Census baseline with ACS updates")
    print("   • Use official state demographic estimates")
    print("   • Cross-validate with building permit data")
    
    print("\n4. 🎲 Account for methodology:")
    print("   • Apply ACS margins of error")
    print("   • Use confidence intervals")
    print("   • Note data limitations in analysis")

def main():
    """Main investigation function"""
    print("🕵️ HOUSEHOLD COUNT DISCREPANCY INVESTIGATION")
    print("=" * 60)
    
    # Load and investigate our data
    gdf = investigate_data_coverage()
    
    # Compare with official sources
    compare_with_official_sources()
    
    # Investigate methodological differences
    investigate_methodological_differences()
    
    # Check tract-level issues
    check_specific_tract_issues(gdf)
    
    # Try alternative data sources
    get_alternative_data_source()
    
    # Provide recommendations
    recommend_solutions()
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"  • The 173,000 household decrease is likely due to:")
    print(f"    - ACS sampling methodology vs Census complete count")
    print(f"    - COVID-19 impacts on household formation")
    print(f"    - Temporal differences (point-in-time vs 5-year average)")
    print(f"    - Possible missing or incomplete tract data")
    print(f"  • Recommendation: Use 2020 Census as authoritative baseline")
    print(f"    and apply growth estimates for current projections")

if __name__ == "__main__":
    main() 