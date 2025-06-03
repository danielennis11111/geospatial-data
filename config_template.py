"""
Configuration template for ArcGIS to GeoJSON Converter

Copy this file to 'config.py' and fill in your ArcGIS credentials and settings.
"""

# ArcGIS Connection Settings
ARCGIS_CONFIG = {
    # For ArcGIS Online
    'url': 'https://www.arcgis.com',
    'username': 'your_username_here',
    'password': 'your_password_here',
    
    # Or for Enterprise/Portal
    # 'url': 'https://your-portal.domain.com/portal',
    # 'username': 'your_username',
    # 'password': 'your_password',
    
    # Or use token-based authentication
    # 'token': 'your_api_token_here',
    
    # Or use OAuth (recommended for production)
    # 'client_id': 'your_client_id',
    # 'client_secret': 'your_client_secret'
}

# Search and Conversion Settings
CONVERSION_CONFIG = {
    # Maximum number of features to download (for testing)
    'max_features': 1000,
    
    # Search parameters for finding layers
    'search_queries': [
        # Example searches - modify these for your data
        'owner:your_username',
        'tags:your_tag_here',
        'title:specific_layer_name',
        'group:your_group_id'
    ],
    
    # Specific item IDs if you know them
    'item_ids': [
        # 'item_id_1_here',
        # 'item_id_2_here'
    ],
    
    # Output settings
    'output_file': 'converted_layer.geojson',
    'include_metadata': True
}

# Example usage in your script:
"""
from config import ARCGIS_CONFIG, CONVERSION_CONFIG
from arcgis.gis import GIS

# Connect using your credentials
gis = GIS(
    url=ARCGIS_CONFIG['url'],
    username=ARCGIS_CONFIG['username'],
    password=ARCGIS_CONFIG['password']
)

# Search for your layers
items = gis.content.search(
    query=CONVERSION_CONFIG['search_queries'][0],
    max_items=10
)
""" 