#!/usr/bin/env python3
"""
Arizona Household Count Analysis from Census Tract Data
"""

import geopandas as gpd
import pandas as pd
import numpy as np

def analyze_household_counts():
    """Analyze household counts from Arizona census tract data"""
    print("🏠 ARIZONA HOUSEHOLD COUNT ANALYSIS")
    print("=" * 50)
    
    # Load the GeoJSON data
    print("📊 Loading Arizona Census Tract Data...")
    gdf = gpd.read_file('specific_layer_analysis.geojson')
    print(f"✅ Loaded {len(gdf)} census tracts")
    
    # Display all available fields to understand the data
    print(f"\n📋 Available Data Fields ({len(gdf.columns)} total):")
    for i, col in enumerate(gdf.columns):
        if col != 'geometry':  # Skip geometry field
            print(f"  {i+1:2d}. {col}")
    
    # Look for household-related fields
    household_fields = []
    for col in gdf.columns:
        if any(keyword in col.lower() for keyword in ['household', 'hh', 'housing', 'unit']):
            household_fields.append(col)
    
    print(f"\n🏠 Potential Household-Related Fields:")
    if household_fields:
        for field in household_fields:
            print(f"  • {field}")
        
        # Try to get total household counts
        for field in household_fields:
            if gdf[field].dtype in ['int64', 'float64']:
                total_households = gdf[field].sum()
                valid_tracts = gdf[field].notna().sum()
                print(f"\n📊 {field}:")
                print(f"  • Total: {total_households:,}")
                print(f"  • Valid tracts: {valid_tracts}/{len(gdf)}")
                print(f"  • Average per tract: {total_households/valid_tracts:.1f}")
    else:
        print("  (No obvious household fields found)")
    
    # Check for total population or housing unit fields that might help
    pop_fields = []
    for col in gdf.columns:
        if any(keyword in col.lower() for keyword in ['total', 'pop', 'population']):
            pop_fields.append(col)
    
    if pop_fields:
        print(f"\n👥 Population/Total Fields (may include household data):")
        for field in pop_fields[:10]:  # Show first 10
            if gdf[field].dtype in ['int64', 'float64']:
                total_value = gdf[field].sum()
                print(f"  • {field}: {total_value:,}")
    
    # Sample some actual data to understand the structure
    print(f"\n🔍 Sample Data from First Tract:")
    sample_tract = gdf.iloc[0]
    for col in gdf.columns:
        if col != 'geometry' and sample_tract[col] is not None:
            print(f"  • {col}: {sample_tract[col]}")
    
    return gdf

def calculate_households_from_percentages():
    """Try to calculate total households from percentage data"""
    print(f"\n🧮 CALCULATING HOUSEHOLDS FROM PERCENTAGE DATA")
    print("=" * 50)
    
    gdf = gpd.read_file('specific_layer_analysis.geojson')
    
    # Look for absolute count fields that we can use with percentages
    numeric_fields = gdf.select_dtypes(include=[np.number]).columns
    
    # Common census field patterns for household counts
    count_fields = []
    for field in numeric_fields:
        # Look for fields that might represent total counts
        if any(keyword in field.lower() for keyword in [
            'total_households', 'total_hh', 'households_total', 
            'total_housing_units', 'housing_units_total'
        ]):
            count_fields.append(field)
    
    print(f"📊 Potential Count Fields:")
    for field in count_fields:
        if field in gdf.columns:
            total = gdf[field].sum()
            print(f"  • {field}: {total:,}")
    
    # If we have percentage fields, try to reverse-engineer totals
    # Look for percentage fields related to computing/internet
    pct_fields = [col for col in gdf.columns if 'pct_' in col.lower() or 'percent' in col.lower()]
    if pct_fields:
        print(f"\n📈 Available Percentage Fields:")
        for field in pct_fields[:5]:
            print(f"  • {field}")
    
    # Try to find a field that represents total universe for percentages
    universe_fields = []
    for field in numeric_fields:
        # Fields with large values that could be universe counts
        if gdf[field].sum() > 50000:  # Arbitrary threshold for large totals
            universe_fields.append((field, gdf[field].sum()))
    
    universe_fields.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🌍 Potential Universe Fields (large totals):")
    for field, total in universe_fields[:10]:
        print(f"  • {field}: {total:,}")
    
    return gdf

if __name__ == "__main__":
    gdf = analyze_household_counts()
    calculate_households_from_percentages() 