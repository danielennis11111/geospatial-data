#!/usr/bin/env python3
"""
Tract-Level Digital Equity Analysis - Pattern Recognition & Clustering
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load and prepare tract-level data for analysis"""
    print("📊 LOADING TRACT-LEVEL DATA")
    print("=" * 40)
    
    gdf = gpd.read_file('specific_layer_analysis.geojson')
    print(f"✅ Loaded {len(gdf)} census tracts")
    
    # Create tract identifiers
    gdf['tract_id'] = gdf['geoid'].astype(str)
    gdf['county_code'] = gdf['countyfp'].astype(str)
    
    # Key variables for analysis
    key_vars = [
        'any_computing_device', 'desktop_or_laptop', 'internet_subscription',
        'broadband_any', 'broadband_fixed', 'pct_smartphone_only', 
        'pct_no_computer', 'pct_households_no_internet'
    ]
    
    # Clean and validate data
    for var in key_vars:
        if var in gdf.columns:
            gdf[var] = pd.to_numeric(gdf[var], errors='coerce')
    
    print(f"📋 Key variables identified: {len([v for v in key_vars if v in gdf.columns])}")
    return gdf, key_vars

def analyze_tract_patterns(gdf, key_vars):
    """Identify patterns at the tract level"""
    print(f"\n🔍 TRACT-LEVEL PATTERN ANALYSIS")
    print("=" * 40)
    
    # Available variables
    available_vars = [var for var in key_vars if var in gdf.columns and gdf[var].notna().sum() > 0]
    
    print(f"📈 Analyzing {len(available_vars)} variables across {len(gdf)} tracts\n")
    
    patterns = {}
    
    # 1. Distribution Analysis
    print("📊 DISTRIBUTION PATTERNS:")
    for var in available_vars[:5]:  # Focus on top 5 variables
        data = gdf[var].dropna()
        if len(data) > 10:
            # Calculate distribution metrics
            q25, q50, q75 = data.quantile([0.25, 0.5, 0.75])
            skewness = stats.skew(data)
            
            print(f"\n{var.replace('_', ' ').title()}:")
            print(f"  • Quartiles: Q1={q25:.1f}%, Q2={q50:.1f}%, Q3={q75:.1f}%")
            print(f"  • Skewness: {skewness:.2f} ({'right-skewed' if skewness > 0.5 else 'left-skewed' if skewness < -0.5 else 'normal'})")
            
            # Identify outliers
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            if len(outliers) > 0:
                print(f"  • Outliers: {len(outliers)} tracts ({len(outliers)/len(data)*100:.1f}%)")
                if len(outliers) <= 5:
                    outlier_tracts = gdf[gdf[var].isin(outliers)]['tract_id'].tolist()
                    print(f"    Tract IDs: {', '.join(outlier_tracts[:3])}{'...' if len(outlier_tracts) > 3 else ''}")
            
            patterns[var] = {
                'mean': data.mean(),
                'std': data.std(),
                'skewness': skewness,
                'outliers': len(outliers)
            }
    
    return patterns

def correlation_analysis(gdf, key_vars):
    """Analyze correlations between variables"""
    print(f"\n🔗 CORRELATION ANALYSIS")
    print("=" * 40)
    
    # Get numeric data
    available_vars = [var for var in key_vars if var in gdf.columns]
    correlation_data = gdf[available_vars].select_dtypes(include=[np.number])
    
    # Calculate correlation matrix
    corr_matrix = correlation_data.corr()
    
    print("📊 Strong Correlations (|r| > 0.7):")
    strong_correlations = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            var1 = corr_matrix.columns[i]
            var2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            
            if abs(corr_value) > 0.7 and not pd.isna(corr_value):
                direction = "📈 Positive" if corr_value > 0 else "📉 Negative"
                print(f"  • {var1} ↔ {var2}: r = {corr_value:.3f} {direction}")
                strong_correlations.append((var1, var2, corr_value))
    
    # Identify unexpected correlations
    print(f"\n🎯 Notable Relationships:")
    
    # Broadband vs computing devices
    if 'broadband_fixed' in correlation_data.columns and 'any_computing_device' in correlation_data.columns:
        corr = correlation_data['broadband_fixed'].corr(correlation_data['any_computing_device'])
        print(f"  • Fixed Broadband ↔ Computing Devices: r = {corr:.3f}")
    
    # Smartphone dependency vs broadband
    if 'pct_smartphone_only' in correlation_data.columns and 'broadband_fixed' in correlation_data.columns:
        corr = correlation_data['pct_smartphone_only'].corr(correlation_data['broadband_fixed'])
        print(f"  • Smartphone-Only ↔ Fixed Broadband: r = {corr:.3f}")
    
    return corr_matrix, strong_correlations

def identify_digital_clusters(gdf, key_vars):
    """Identify clusters of similar tracts using unsupervised learning"""
    print(f"\n🎯 DIGITAL EQUITY CLUSTERING")
    print("=" * 40)
    
    # Prepare data for clustering
    cluster_vars = ['any_computing_device', 'broadband_fixed', 'pct_smartphone_only']
    cluster_vars = [var for var in cluster_vars if var in gdf.columns]
    
    if len(cluster_vars) < 2:
        print("❌ Insufficient variables for clustering")
        return None
    
    # Get clean data
    cluster_data = gdf[cluster_vars].dropna()
    if len(cluster_data) < 10:
        print("❌ Insufficient clean data for clustering")
        return None
    
    print(f"📊 Clustering {len(cluster_data)} tracts using {len(cluster_vars)} variables")
    
    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(cluster_data)
    
    # K-means clustering
    optimal_k = min(5, len(cluster_data) // 10)  # Reasonable number of clusters
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Add clusters back to data
    cluster_data['cluster'] = clusters
    cluster_data['tract_id'] = gdf.loc[cluster_data.index, 'tract_id']
    
    print(f"\n🏷️ CLUSTER PROFILES (K={optimal_k}):")
    
    cluster_profiles = {}
    for cluster_id in range(optimal_k):
        cluster_tracts = cluster_data[cluster_data['cluster'] == cluster_id]
        print(f"\n📍 Cluster {cluster_id} ({len(cluster_tracts)} tracts):")
        
        profile = {}
        for var in cluster_vars:
            mean_val = cluster_tracts[var].mean()
            print(f"  • {var.replace('_', ' ').title()}: {mean_val:.1f}%")
            profile[var] = mean_val
        
        # Characterize cluster
        if 'broadband_fixed' in profile:
            if profile['broadband_fixed'] > 80:
                category = "🟢 High Digital Access"
            elif profile['broadband_fixed'] > 60:
                category = "🟡 Moderate Digital Access"
            else:
                category = "🔴 Low Digital Access"
            print(f"  → {category}")
        
        cluster_profiles[cluster_id] = {
            'profile': profile,
            'count': len(cluster_tracts),
            'tract_ids': cluster_tracts['tract_id'].tolist()[:5]  # Sample tract IDs
        }
    
    return cluster_profiles

def geographic_relationship_analysis(gdf, key_vars):
    """Analyze geographic relationships and spatial patterns"""
    print(f"\n🗺️ GEOGRAPHIC RELATIONSHIP ANALYSIS")
    print("=" * 40)
    
    # County-level variations
    print("📍 COUNTY-LEVEL VARIATIONS:")
    
    if 'namelsadco' in gdf.columns and 'broadband_fixed' in gdf.columns:
        county_stats = gdf.groupby('namelsadco').agg({
            'broadband_fixed': ['mean', 'std', 'count'],
            'any_computing_device': 'mean',
            'pct_smartphone_only': 'mean'
        }).round(2)
        
        # Flatten column names
        county_stats.columns = ['_'.join(col).strip() for col in county_stats.columns]
        
        # Sort by broadband access
        county_stats = county_stats.sort_values('broadband_fixed_mean')
        
        print("\n🏆 Counties Ranked by Broadband Access:")
        for county, row in county_stats.head(10).iterrows():
            if pd.notna(row['broadband_fixed_mean']):
                variance = "high variance" if row['broadband_fixed_std'] > 15 else "low variance"
                print(f"  • {county}: {row['broadband_fixed_mean']:.1f}% avg, σ={row['broadband_fixed_std']:.1f} ({variance})")
    
    # Identify geographic patterns
    print(f"\n🔍 GEOGRAPHIC PATTERNS:")
    
    # Rural vs Urban patterns (using tract density as proxy)
    if 'broadband_fixed' in gdf.columns:
        # Calculate approximate tract density (simple heuristic)
        gdf['tract_density_proxy'] = 1 / (gdf.index + 1)  # Simple proxy
        
        # Urban/rural classification based on broadband access distribution
        urban_threshold = gdf['broadband_fixed'].quantile(0.75)
        rural_threshold = gdf['broadband_fixed'].quantile(0.25)
        
        urban_tracts = gdf[gdf['broadband_fixed'] >= urban_threshold]
        rural_tracts = gdf[gdf['broadband_fixed'] <= rural_threshold]
        
        if len(urban_tracts) > 0 and len(rural_tracts) > 0:
            print(f"\n🏙️ High-Access Areas (likely urban, n={len(urban_tracts)}):")
            print(f"  • Avg Broadband: {urban_tracts['broadband_fixed'].mean():.1f}%")
            print(f"  • Avg Computing Devices: {urban_tracts['any_computing_device'].mean():.1f}%")
            
            print(f"\n🌾 Low-Access Areas (likely rural, n={len(rural_tracts)}):")
            print(f"  • Avg Broadband: {rural_tracts['broadband_fixed'].mean():.1f}%")
            print(f"  • Avg Computing Devices: {rural_tracts['any_computing_device'].mean():.1f}%")
            
            # Statistical test for difference
            t_stat, p_value = stats.ttest_ind(
                urban_tracts['broadband_fixed'].dropna(), 
                rural_tracts['broadband_fixed'].dropna()
            )
            print(f"  • Statistical significance: p = {p_value:.4f} {'(significant)' if p_value < 0.05 else '(not significant)'}")

def identify_priority_tracts(gdf, key_vars):
    """Identify specific tracts needing priority intervention"""
    print(f"\n🚨 PRIORITY TRACT IDENTIFICATION")
    print("=" * 40)
    
    # Multi-criteria scoring for priority
    priority_vars = ['broadband_fixed', 'any_computing_device', 'pct_smartphone_only']
    available_priority_vars = [var for var in priority_vars if var in gdf.columns]
    
    if len(available_priority_vars) >= 2:
        # Create priority score (lower = higher priority)
        gdf['priority_score'] = 0
        
        if 'broadband_fixed' in gdf.columns:
            # Lower broadband = higher priority
            gdf['priority_score'] += (100 - gdf['broadband_fixed'].fillna(50)) * 0.4
        
        if 'any_computing_device' in gdf.columns:
            # Lower device access = higher priority
            gdf['priority_score'] += (100 - gdf['any_computing_device'].fillna(50)) * 0.3
        
        if 'pct_smartphone_only' in gdf.columns:
            # Higher smartphone dependency = higher priority
            gdf['priority_score'] += gdf['pct_smartphone_only'].fillna(10) * 0.3
        
        # Get top priority tracts
        top_priority = gdf.nlargest(10, 'priority_score')
        
        print("🎯 TOP 10 PRIORITY TRACTS FOR INTERVENTION:")
        for i, (idx, tract) in enumerate(top_priority.iterrows()):
            print(f"\n{i+1}. Tract {tract['tract_id']} (County: {tract.get('namelsadco', 'Unknown')}):")
            print(f"   • Priority Score: {tract['priority_score']:.1f}")
            if 'broadband_fixed' in tract:
                print(f"   • Broadband Access: {tract['broadband_fixed']:.1f}%")
            if 'any_computing_device' in tract:
                print(f"   • Computing Devices: {tract['any_computing_device']:.1f}%")
            if 'pct_smartphone_only' in tract:
                print(f"   • Smartphone-Only: {tract['pct_smartphone_only']:.1f}%")
        
        return top_priority
    
    return None

def main():
    """Main analysis function"""
    print("🎯 TRACT-LEVEL DIGITAL EQUITY ANALYSIS")
    print("=" * 50)
    
    # Load and prepare data
    gdf, key_vars = load_and_prepare_data()
    
    # Comprehensive tract-level analysis
    patterns = analyze_tract_patterns(gdf, key_vars)
    corr_matrix, strong_corrs = correlation_analysis(gdf, key_vars)
    cluster_profiles = identify_digital_clusters(gdf, key_vars)
    geographic_relationship_analysis(gdf, key_vars)
    priority_tracts = identify_priority_tracts(gdf, key_vars)
    
    # Summary insights
    print(f"\n🎯 KEY TRACT-LEVEL INSIGHTS:")
    print("=" * 40)
    print(f"✅ Analyzed {len(gdf)} individual census tracts")
    print(f"✅ Identified {len(strong_corrs)} strong variable correlations")
    if cluster_profiles:
        print(f"✅ Discovered {len(cluster_profiles)} distinct digital equity clusters")
    if priority_tracts is not None:
        print(f"✅ Identified top 10 priority tracts for intervention")
    
    print(f"\n🎯 This tract-level analysis reveals granular patterns for targeted policy intervention!")

if __name__ == "__main__":
    main() 