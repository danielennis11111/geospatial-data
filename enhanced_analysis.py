#!/usr/bin/env python3
"""
Enhanced Digital Equity Analysis for Arizona Census Tracts
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

def analyze_digital_equity_data():
    """Perform comprehensive analysis of the digital equity data"""
    
    print("🌐 DIGITAL EQUITY ANALYSIS - ARIZONA CENSUS TRACTS")
    print("=" * 60)
    
    try:
        # Load the data
        gdf = gpd.read_file('specific_layer_analysis.geojson')
        print(f"📊 Analyzing {len(gdf)} Arizona census tracts\n")
        
        # === BROADBAND & INTERNET ACCESS ANALYSIS ===
        print("🌐 BROADBAND & INTERNET ACCESS ANALYSIS:")
        print("-" * 40)
        
        # Key digital equity metrics
        broadband_cols = ['any_computing_device', 'desktop_or_laptop', 'internet_subscription', 
                         'broadband_any', 'broadband_fixed']
        
        for col in broadband_cols:
            if col in gdf.columns:
                data = gdf[col].dropna()
                if len(data) > 0:
                    print(f"\n{col.replace('_', ' ').title()}:")
                    print(f"  • Mean: {data.mean():.1f}%")
                    print(f"  • Range: {data.min():.1f}% - {data.max():.1f}%")
                    print(f"  • Below 80%: {(data < 80).sum()} tracts ({(data < 80).mean()*100:.1f}%)")
                    print(f"  • Below 90%: {(data < 90).sum()} tracts ({(data < 90).mean()*100:.1f}%)")
        
        # === DIGITAL DIVIDE ANALYSIS ===
        print(f"\n🏘️ DIGITAL DIVIDE ANALYSIS:")
        print("-" * 40)
        
        # Find areas with significant digital divides
        if 'any_computing_device' in gdf.columns:
            low_access = gdf[gdf['any_computing_device'] < 80]['any_computing_device'].dropna()
            if len(low_access) > 0:
                print(f"\n🚨 Low Computer Access Areas (< 80% with any computing device):")
                print(f"  • {len(low_access)} tracts affected")
                print(f"  • Worst access: {low_access.min():.1f}% (GEOID: {gdf.loc[gdf['any_computing_device'].idxmin(), 'geoid']})")
                print(f"  • Average in low-access areas: {low_access.mean():.1f}%")
        
        # Smartphone-only households (indicates limited access)
        if 'pct_smartphone_only' in gdf.columns:
            smartphone_only = gdf['pct_smartphone_only'].dropna()
            if len(smartphone_only) > 0:
                high_smartphone_only = smartphone_only[smartphone_only > 20]
                print(f"\n📱 Smartphone-Only Households Analysis:")
                print(f"  • Average smartphone-only: {smartphone_only.mean():.1f}%")
                print(f"  • High dependency areas (>20%): {len(high_smartphone_only)} tracts")
                if len(high_smartphone_only) > 0:
                    print(f"  • Highest dependency: {smartphone_only.max():.1f}%")
        
        # === INCOME VS BROADBAND ANALYSIS ===
        print(f"\n💰 INCOME VS BROADBAND CORRELATION:")
        print("-" * 40)
        
        income_cols = ['income_under_20k', 'income_20k_75k', 'income_over_75k']
        broadband_col = 'broadband_fixed'
        
        if broadband_col in gdf.columns:
            broadband_data = gdf[broadband_col].dropna()
            
            for income_col in income_cols:
                if income_col in gdf.columns:
                    income_data = gdf[income_col].dropna()
                    
                    # Find common indices for correlation
                    common_idx = broadband_data.index.intersection(income_data.index)
                    if len(common_idx) > 10:  # Need sufficient data for correlation
                        correlation = broadband_data[common_idx].corr(income_data[common_idx])
                        print(f"  • {income_col.replace('_', ' ').title()} vs Fixed Broadband: r = {correlation:.3f}")
        
        # === GEOGRAPHIC PATTERNS ===
        print(f"\n🗺️ GEOGRAPHIC PATTERNS:")
        print("-" * 40)
        
        # Analyze by county
        if 'namelsadco' in gdf.columns and 'any_computing_device' in gdf.columns:
            county_analysis = gdf.groupby('namelsadco')['any_computing_device'].agg(['mean', 'count', 'std']).round(2)
            county_analysis = county_analysis.sort_values('mean')
            
            print("\n📍 Computing Device Access by County:")
            for county, row in county_analysis.head(10).iterrows():
                if pd.notna(row['mean']):
                    print(f"  • {county}: {row['mean']:.1f}% avg (n={row['count']} tracts)")
        
        # === EQUITY INSIGHTS ===
        print(f"\n⚖️ DIGITAL EQUITY INSIGHTS:")
        print("-" * 40)
        
        # Calculate digital equity score (composite metric)
        equity_cols = ['any_computing_device', 'internet_subscription', 'broadband_fixed']
        available_cols = [col for col in equity_cols if col in gdf.columns]
        
        if len(available_cols) >= 2:
            # Create composite digital equity score
            gdf['digital_equity_score'] = gdf[available_cols].mean(axis=1)
            
            equity_scores = gdf['digital_equity_score'].dropna()
            if len(equity_scores) > 0:
                print(f"\n🎯 Digital Equity Score (0-100, higher = better access):")
                print(f"  • Arizona Average: {equity_scores.mean():.1f}")
                print(f"  • Best tract: {equity_scores.max():.1f}")
                print(f"  • Worst tract: {equity_scores.min():.1f}")
                print(f"  • Standard deviation: {equity_scores.std():.1f}")
                
                # Identify equity categories
                high_equity = (equity_scores >= 90).sum()
                medium_equity = ((equity_scores >= 75) & (equity_scores < 90)).sum()
                low_equity = (equity_scores < 75).sum()
                
                print(f"\n📊 Equity Distribution:")
                print(f"  • High equity (≥90%): {high_equity} tracts ({high_equity/len(equity_scores)*100:.1f}%)")
                print(f"  • Medium equity (75-89%): {medium_equity} tracts ({medium_equity/len(equity_scores)*100:.1f}%)")
                print(f"  • Low equity (<75%): {low_equity} tracts ({low_equity/len(equity_scores)*100:.1f}%)")
        
        # === ACTIONABLE INSIGHTS ===
        print(f"\n🎯 ACTIONABLE INSIGHTS FOR POLICY:")
        print("-" * 40)
        
        # Identify priority areas for intervention
        if 'any_computing_device' in gdf.columns and 'broadband_fixed' in gdf.columns:
            low_access_tracts = gdf[
                (gdf['any_computing_device'] < 80) | (gdf['broadband_fixed'] < 70)
            ]
            
            print(f"\n🚨 Priority Areas for Digital Equity Investment:")
            print(f"  • {len(low_access_tracts)} census tracts need intervention")
            print(f"  • Represents {len(low_access_tracts)/len(gdf)*100:.1f}% of analyzed areas")
            
            if len(low_access_tracts) > 0:
                print(f"\n📋 Specific Recommendations:")
                print(f"  • Improve computing device access in {(gdf['any_computing_device'] < 80).sum()} tracts")
                print(f"  • Expand broadband infrastructure in {(gdf['broadband_fixed'] < 70).sum()} tracts")
                
                # Check smartphone dependency
                if 'pct_smartphone_only' in gdf.columns:
                    high_smartphone = (gdf['pct_smartphone_only'] > 25).sum()
                    print(f"  • Address smartphone-only dependency in {high_smartphone} tracts")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def create_summary_report():
    """Create a summary report of findings"""
    try:
        gdf = gpd.read_file('specific_layer_analysis.geojson')
        
        print(f"\n📄 EXECUTIVE SUMMARY - ARIZONA DIGITAL EQUITY")
        print("=" * 50)
        
        # Key statistics
        if 'any_computing_device' in gdf.columns:
            avg_computing = gdf['any_computing_device'].mean()
            print(f"• Average computing device access: {avg_computing:.1f}%")
        
        if 'broadband_fixed' in gdf.columns:
            avg_broadband = gdf['broadband_fixed'].mean()
            print(f"• Average fixed broadband access: {avg_broadband:.1f}%")
        
        if 'pct_smartphone_only' in gdf.columns:
            avg_smartphone_only = gdf['pct_smartphone_only'].mean()
            print(f"• Average smartphone-only households: {avg_smartphone_only:.1f}%")
        
        # Data quality
        total_tracts = len(gdf)
        print(f"• Total census tracts analyzed: {total_tracts}")
        
        # Missing data summary
        missing_data = gdf.isnull().sum().sum()
        total_data_points = len(gdf) * len(gdf.columns)
        completeness = (1 - missing_data / total_data_points) * 100
        print(f"• Data completeness: {completeness:.1f}%")
        
    except Exception as e:
        print(f"Error creating summary: {e}")

def main():
    """Main analysis function"""
    success = analyze_digital_equity_data()
    
    if success:
        create_summary_report()
        print(f"\n✅ COMPREHENSIVE DIGITAL EQUITY ANALYSIS COMPLETE!")
        print(f"🎯 This analysis provides actionable insights for Arizona digital equity policy")
    else:
        print(f"❌ Analysis failed")

if __name__ == "__main__":
    main() 