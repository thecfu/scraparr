"""
Constants for Scraparr.
"""

ACTIVE_CONNECTORS = [
    'sonarr', 'radarr', 'prowlarr',
    'bazarr', 'readarr', 'jellyseerr',
    'overseerr', 'whisparr', 'jellyfin',
]

API_VERSIONS = {
    "sonarr": "v3", "radarr": "v3",
    "prowlarr": "v1", "bazarr": "dummy",
    "readarr": "v1", "jellyseerr": "v1",
    "overseerr": "v1", "whisparr": "v3",
    "jellyfin": "dummy",
}

BEAUTIFUL_CONNECTORS = ", ".join(ACTIVE_CONNECTORS[:-1]) + " or " + ACTIVE_CONNECTORS[-1]

# Optional ENV variables for connectors
OPTIONAL_FIELDS = [
    'alias', 'api_version', 'interval',
    'detailed', 'within',
]
