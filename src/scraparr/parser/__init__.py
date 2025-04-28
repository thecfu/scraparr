"""Parses Scraparr configuration from environment or .env file."""

import os
import sys
from typing import Optional, Dict, Mapping
from dotenv import dotenv_values

from scraparr.const import ACTIVE_CONNECTORS, OPTIONAL_FIELDS

def _build_config(env: Mapping[str, str]) -> Dict[str, Optional[Dict[str, str]]]:
    config: Dict[str, Optional[Dict[str, str]]] = {
        'general': None,
        'auth': None,
    }
    for service in ACTIVE_CONNECTORS:
        try:
            prefix = service.upper()
            url = env.get(f'{prefix}_URL')
            api_key = env.get(f'{prefix}_API_KEY')

            if url and api_key:
                service_config = {
                    'url': url,
                    'api_key': api_key,
                    **{
                        field: int(val) if field == "interval"
                                           or field == "within"
                        else val
                        for field in OPTIONAL_FIELDS
                        if (val := env.get(f'{prefix}_{field.upper()}')) is not None
                    }
                }
                config[service] = service_config
            else:
                config[service] = None
        except ValueError as e:
            print(f"Error parsing environment variables for {service}: {e}")
            sys.exit(1)

    return config

def parse_dotenv_config(path: str = "/scraparr/.env") -> Dict[str, Optional[Dict[str, str]]]:
    """Parse configuration from a .env file at the given path."""
    return _build_config(dotenv_values(path))  # type: ignore

def parse_env_config() -> Dict[str, Optional[Dict[str, str]]]:
    """Parse configuration from the current environment variables."""
    return _build_config(os.environ)
