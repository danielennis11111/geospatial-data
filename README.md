# Geospatial Data Analysis - Arizona Digital Equity Project

A comprehensive ArcGIS to GeoJSON converter with advanced geospatial analysis capabilities for Arizona census data. This project helps test geospatial data exploration and provides detailed digital equity analysis across Arizona's 1,765 census tracts.

## Project Overview

This tool evolved from a simple ArcGIS to GeoJSON converter into a sophisticated geospatial intelligence system for analyzing digital equity patterns in Arizona, processing data for 2.8 million households across all 15 counties.

## Key Features

- **Complete ArcGIS to GeoJSON Pipeline**: Convert real ArcGIS organizational data
- **Comprehensive Digital Equity Analysis**: Broadband access, computing devices, smartphone dependency
- **Advanced Statistical Analysis**: K-means clustering, correlation analysis, priority scoring
- **Household Count Investigation**: Methodology comparison between 2020 Census and 2023 ACS
- **County and Tract-Level Intelligence**: Actionable insights for policy intervention

## Major Analysis Results

### Statewide Digital Equity Findings
- **2.8M households analyzed** across all Arizona census tracts
- **71.5% fixed broadband access** (household-weighted average)
- **184 census tracts** identified as needing urgent intervention
- **Strong income-broadband correlation** (r = -0.707)
- **Apache County** shows worst access patterns (66.7% computing devices)

### Methodological Investigation
- **Household Count Discrepancy**: 2020 Census (2.97M) vs 2023 ACS (2.796M)
- **COVID-19 Impact Analysis**: Disrupted household formation patterns
- **Data Quality Assessment**: Complete coverage validation across all tracts

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure ArcGIS Credentials**
   - Copy `config_template.py` to `config.py`
   - Add your ArcGIS organizational credentials

## Key Scripts

### Data Collection & Conversion
- `get_all_arizona_tracts.py` - Fetch complete Arizona census tract dataset
- `arcgis_to_geojson_converter.py` - Core conversion functionality
- `connect_my_arcgis.py` - Organizational authentication

### Analysis & Intelligence
- `complete_arizona_household_analysis.py` - Full statewide household analysis
- `tract_level_analysis.py` - Advanced clustering and correlation analysis
- `investigate_household_discrepancy.py` - Methodological investigation
- `enhanced_analysis.py` - Priority area identification

### Utilities
- `explore_sublayers.py` - ArcGIS layer exploration
- `demo.py` - Basic functionality demonstration
- `test_queries.py` - Natural language query testing

## Usage Examples

### Complete Arizona Analysis
```bash
python get_all_arizona_tracts.py          # Fetch all 1,765 tracts
python complete_arizona_household_analysis.py  # Comprehensive analysis
```

### Advanced Digital Equity Analysis
```bash
python tract_level_analysis.py            # ML clustering analysis
python investigate_household_discrepancy.py    # Methodological investigation
```

### Natural Language Queries
The tool supports queries like:
- "How many households are in Arizona?"
- "Which counties have the worst broadband access?"
- "What are the priority areas for digital equity intervention?"

## Data Sources

- **ArcGIS API**: Arizona's organizational portal (`azgeo.maps.arcgis.com`)
- **ACS 2023**: 5-year estimates for digital equity variables
- **Census Tracts**: Complete Arizona coverage (1,765 tracts)
- **Household Data**: 2.8M households across 15 counties

## Technical Achievements

- **Production-Ready Pipeline**: Real organizational data processing
- **Statistical Rigor**: Correlation analysis, clustering, significance testing
- **Policy Intelligence**: Tract-level priority scoring for intervention
- **Data Quality**: Comprehensive validation and cross-verification

## Key Findings for Policy

### Priority Intervention Areas
1. **Apache County**: 5 of top 10 priority tracts
2. **Tract 04001942600**: Only 2.9% broadband access
3. **Urban vs Rural**: 89.8% vs 46.2% broadband access (p < 0.0001)
4. **Total Priority Households**: 354,998 affected by digital divide

### Methodological Insights
- **ACS vs Census**: 173K household discrepancy due to methodology
- **COVID Impact**: Disrupted household formation 2020-2023
- **Survey Limitations**: Sample-based estimates vs complete enumeration

## Requirements
- Python 3.8+
- ArcGIS API for Python
- GeoPandas, Pandas, NumPy
- SciPy, Scikit-learn (for advanced analysis)
- Matplotlib, Seaborn (for visualization)

## Contributing

This project demonstrates the evolution from basic data conversion to production-ready geospatial intelligence for policy decision-making.

## Documentation

See `TESTING_SUMMARY.md` for detailed development history and `instructions.txt` for original project specifications.
