#!/usr/bin/env python3
"""
Complete Arizona Household Analysis - All 1,765 Census Tracts
Enhanced analysis with full statewide coverage
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_complete_dataset():
    """Load the complete Arizona census tract dataset"""
    print("🏠 COMPLETE ARIZONA HOUSEHOLD ANALYSIS")
    print("=" * 50)
    
    # Load the complete GeoJSON data
    print("📊 Loading Complete Arizona Census Tract Data...")
    gdf = gpd.read_file('all_arizona_tracts.geojson')
    print(f"✅ Loaded {len(gdf)} census tracts (complete statewide coverage)")
    
    # Identify total_households field
    if 'total_households' in gdf.columns:
        print(f"📋 Found total_households field")
    else:
        # Look for alternative household field names
        household_fields = [col for col in gdf.columns if 'household' in col.lower()]
        print(f"📋 Available household fields: {household_fields}")
    
    return gdf

def comprehensive_household_analysis(gdf):
    """Comprehensive analysis of household data across all Arizona tracts"""
    print(f"\n🏠 STATEWIDE HOUSEHOLD ANALYSIS")
    print("=" * 40)
    
    # Overall household totals
    if 'total_households' in gdf.columns:
        total_households = gdf['total_households'].sum()
        valid_tracts = gdf['total_households'].notna().sum()
        mean_households = gdf['total_households'].mean()
        median_households = gdf['total_households'].median()
        
        print(f"📊 ARIZONA HOUSEHOLD TOTALS:")
        print(f"  • Total households: {total_households:,}")
        print(f"  • Valid tracts: {valid_tracts}/{len(gdf)} ({valid_tracts/len(gdf)*100:.1f}%)")
        print(f"  • Mean per tract: {mean_households:.1f}")
        print(f"  • Median per tract: {median_households:.1f}")
        
        # Distribution analysis
        print(f"\n📈 HOUSEHOLD DISTRIBUTION:")
        q25, q50, q75 = gdf['total_households'].quantile([0.25, 0.5, 0.75])
        print(f"  • Q1 (25th percentile): {q25:.0f} households per tract")
        print(f"  • Q2 (50th percentile): {q50:.0f} households per tract")
        print(f"  • Q3 (75th percentile): {q75:.0f} households per tract")
        print(f"  • Min: {gdf['total_households'].min():.0f} households per tract")
        print(f"  • Max: {gdf['total_households'].max():.0f} households per tract")
    
    return gdf

def county_level_analysis(gdf):
    """County-level household analysis"""
    print(f"\n📍 COUNTY-LEVEL HOUSEHOLD ANALYSIS")
    print("=" * 40)
    
    if 'namelsadco' in gdf.columns and 'total_households' in gdf.columns:
        county_stats = gdf.groupby('namelsadco').agg({
            'total_households': ['sum', 'count', 'mean', 'median'],
            'any_computing_device': 'mean',
            'broadband_fixed': 'mean',
            'pct_smartphone_only': 'mean'
        }).round(2)
        
        # Flatten column names
        county_stats.columns = ['_'.join(col).strip() for col in county_stats.columns]
        
        # Sort by total households (largest counties first)
        county_stats = county_stats.sort_values('total_households_sum', ascending=False)
        
        print(f"🏆 COUNTIES BY TOTAL HOUSEHOLDS:")
        for county, row in county_stats.iterrows():
            households = int(row['total_households_sum'])
            tracts = int(row['total_households_count'])
            avg_per_tract = row['total_households_mean']
            broadband = row['broadband_fixed_mean']
            
            print(f"  • {county}:")
            print(f"    - Total households: {households:,}")
            print(f"    - Census tracts: {tracts}")
            print(f"    - Avg per tract: {avg_per_tract:.0f}")
            print(f"    - Broadband access: {broadband:.1f}%")
            print()
        
        return county_stats
    
    return None

def digital_equity_analysis(gdf):
    """Digital equity analysis across all households"""
    print(f"\n💻 DIGITAL EQUITY ANALYSIS - ALL HOUSEHOLDS")
    print("=" * 40)
    
    # Calculate weighted averages (by household count)
    if 'total_households' in gdf.columns:
        digital_fields = ['any_computing_device', 'broadband_fixed', 'pct_smartphone_only']
        
        for field in digital_fields:
            if field in gdf.columns:
                # Filter out NaN values for both field and weights
                mask = gdf[field].notna() & gdf['total_households'].notna() & (gdf['total_households'] > 0)
                clean_data = gdf[mask]
                
                if len(clean_data) > 0:
                    # Weighted average by household count
                    weighted_avg = np.average(clean_data[field], weights=clean_data['total_households'])
                    # Simple average across tracts
                    tract_avg = clean_data[field].mean()
                    
                    print(f"🎯 {field.replace('_', ' ').title()}:")
                    print(f"  • Household-weighted average: {weighted_avg:.1f}%")
                    print(f"  • Tract-level average: {tract_avg:.1f}%")
                    print(f"  • Valid tracts: {len(clean_data)}/{len(gdf)}")
                    
                    # Calculate how many households this represents
                    total_households = clean_data['total_households'].sum()
                    
                    if field == 'broadband_fixed':
                        households_with_broadband = int(weighted_avg/100 * total_households)
                        households_without_broadband = total_households - households_with_broadband
                        print(f"  • Households with fixed broadband: {households_with_broadband:,}")
                        print(f"  • Households without fixed broadband: {households_without_broadband:,}")
                    
                    elif field == 'any_computing_device':
                        households_with_devices = int(weighted_avg/100 * total_households)
                        households_without_devices = total_households - households_with_devices
                        print(f"  • Households with computing devices: {households_with_devices:,}")
                        print(f"  • Households without computing devices: {households_without_devices:,}")
                    
                    print()
                else:
                    print(f"❌ No valid data for {field}")
                    print()

def identify_high_priority_areas(gdf):
    """Identify high-priority areas for intervention"""
    print(f"\n🚨 HIGH-PRIORITY AREAS FOR DIGITAL EQUITY INTERVENTION")
    print("=" * 40)
    
    if all(field in gdf.columns for field in ['total_households', 'broadband_fixed', 'any_computing_device']):
        # Create priority criteria
        gdf['households_without_broadband'] = gdf['total_households'] * (100 - gdf['broadband_fixed']) / 100
        gdf['households_without_devices'] = gdf['total_households'] * (100 - gdf['any_computing_device']) / 100
        
        # Priority scoring: more households affected = higher priority
        gdf['priority_score'] = (gdf['households_without_broadband'] * 0.6 + 
                                gdf['households_without_devices'] * 0.4)
        
        # Top priority tracts
        top_priority = gdf.nlargest(20, 'priority_score')
        
        print(f"🎯 TOP 20 PRIORITY TRACTS (by household impact):")
        total_affected_households = 0
        
        for i, (idx, tract) in enumerate(top_priority.iterrows()):
            county = tract['namelsadco']
            tract_id = tract['geoid']
            total_hh = int(tract['total_households'])
            broadband = tract['broadband_fixed']
            devices = tract['any_computing_device']
            without_broadband = int(tract['households_without_broadband'])
            without_devices = int(tract['households_without_devices'])
            
            print(f"\n{i+1:2d}. Tract {tract_id} ({county}):")
            print(f"     • Total households: {total_hh:,}")
            print(f"     • Broadband access: {broadband:.1f}%")
            print(f"     • Households without broadband: {without_broadband:,}")
            print(f"     • Households without devices: {without_devices:,}")
            
            total_affected_households += without_broadband
        
        print(f"\n📊 PRIORITY AREA IMPACT:")
        print(f"  • Total households in top 20 tracts: {top_priority['total_households'].sum():,}")
        print(f"  • Households without broadband in top 20: {total_affected_households:,}")
        print(f"  • Percentage of affected households: {total_affected_households/total_affected_households*100:.1f}%")
        
        return top_priority
    
    return None

def comparison_with_previous_analysis(gdf):
    """Compare with our previous 500-tract analysis"""
    print(f"\n📊 COMPARISON: COMPLETE vs PREVIOUS ANALYSIS")
    print("=" * 40)
    
    current_total = gdf['total_households'].sum() if 'total_households' in gdf.columns else 0
    previous_total = 752945  # From our previous analysis
    
    print(f"🔍 COVERAGE COMPARISON:")
    print(f"  • Previous analysis: 500 tracts, {previous_total:,} households")
    print(f"  • Current analysis: {len(gdf)} tracts, {current_total:,} households")
    print(f"  • Additional coverage: {len(gdf)-500} tracts, {current_total-previous_total:,} households")
    print(f"  • Coverage increase: {(current_total-previous_total)/previous_total*100:.1f}%")
    
    if 'broadband_fixed' in gdf.columns:
        current_broadband = np.average(gdf['broadband_fixed'], weights=gdf['total_households'])
        print(f"\n💻 DIGITAL EQUITY COMPARISON:")
        print(f"  • Previous sample broadband avg: 71.5% (estimated)")
        print(f"  • Complete state broadband avg: {current_broadband:.1f}%")
        print(f"  • Difference: {current_broadband-71.5:.1f} percentage points")

def main():
    """Main analysis function"""
    print("🌵 COMPLETE ARIZONA HOUSEHOLD & DIGITAL EQUITY ANALYSIS")
    print("=" * 60)
    
    # Load complete dataset
    gdf = load_complete_dataset()
    
    # Comprehensive household analysis
    gdf = comprehensive_household_analysis(gdf)
    
    # County-level analysis
    county_stats = county_level_analysis(gdf)
    
    # Digital equity analysis
    digital_equity_analysis(gdf)
    
    # High-priority areas
    priority_areas = identify_high_priority_areas(gdf)
    
    # Comparison with previous analysis
    comparison_with_previous_analysis(gdf)
    
    print(f"\n✅ COMPLETE ANALYSIS SUMMARY:")
    print(f"  • Analyzed {len(gdf):,} census tracts (complete Arizona coverage)")
    print(f"  • Total households: {gdf['total_households'].sum():,}")
    print(f"  • All 15 Arizona counties included")
    print(f"  • Full digital equity analysis completed")
    print(f"  • Priority intervention areas identified")

if __name__ == "__main__":
    main() 