"""
Config loading with environment variable substitution.

Supports ${VAR_NAME} and ${VAR_NAME:-default} syntax in YAML string values.
"""

import logging
import os
import re
from typing import Any, List

import yaml

from scraparr.const import BOOL_FIELDS, INT_FIELDS

# Matches ${VAR_NAME} or ${VAR_NAME:-default}
ENV_VAR_PATTERN = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}')


class MissingEnvVarError(Exception):
    """Raised when a required environment variable is not set."""

    def __init__(self, var_name: str, config_path: str = ""):
        self.var_name = var_name
        self.config_path = config_path
        if config_path:
            message = f"Environment variable '{var_name}' is not set (in config: {config_path})"
        else:
            message = f"Environment variable '{var_name}' is not set"
        super().__init__(message)


def _parse_bool(value: str) -> bool:
    """Parse boolean from string."""
    return value.lower() in ('true', '1', 'yes')


def _coerce_value(key: str, value: Any) -> Any:
    """Coerce string values to appropriate types based on field name."""
    if not isinstance(value, str):
        return value
    if key in INT_FIELDS:
        return int(value)
    if key in BOOL_FIELDS:
        return _parse_bool(value)
    return value


def _substitute_string(value: str, config_path: str) -> str:
    """Substitute ${VAR} patterns in a string."""
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default_value = match.group(2)

        env_value = os.environ.get(var_name)
        if env_value is not None:
            return env_value

        env_file = os.environ.get(f"{var_name}_FILE")
        if env_file is not None:
            with open(env_file, 'r', encoding='utf-8') as f:
                return f.read().rstrip('\r\n')

        if default_value is not None:
            logging.debug("Env var '%s' not set, using default (config: %s)", var_name, config_path)
            return default_value

        raise MissingEnvVarError(var_name, config_path)

    return ENV_VAR_PATTERN.sub(replacer, value)


def substitute_env_vars(config: Any, _path: str = "") -> Any:
    """Recursively substitute ${VAR} patterns in string values."""
    if isinstance(config, dict):
        return {
            key: substitute_env_vars(value, f"{_path}.{key}" if _path else key)
            for key, value in config.items()
        }

    if isinstance(config, list):
        return [
            substitute_env_vars(item, f"{_path}[{i}]")
            for i, item in enumerate(config)
        ]

    if isinstance(config, str):
        return _substitute_string(config, _path)

    return config


def coerce_config_types(config: Any) -> Any:
    """Recursively coerce string values to appropriate types based on field names."""
    if isinstance(config, dict):
        return {
            key: _coerce_value(key, coerce_config_types(value))
            for key, value in config.items()
        }

    if isinstance(config, list):
        return [coerce_config_types(item) for item in config]

    return config


def load_yaml_config(file_path: str) -> dict:
    """Load YAML config file with environment variable substitution.

    Note: Type coercion should be done after merging with env config.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if config is None:
        return {}

    return substitute_env_vars(config)


def load_yaml_config_safe(file_path: str) -> dict:
    """Load YAML config, returning empty dict if file not found."""
    try:
        return load_yaml_config(file_path)
    except FileNotFoundError:
        return {}


def _merge_list_by_alias(base_list: List[dict], aliases_dict: dict) -> List[dict]:
    """Merge a list of configs (from YAML) with an alias-keyed dict (from env).

    Matches items by 'alias' field and merges. New aliases are appended.
    """
    result = []
    seen_aliases = set()

    # Merge existing items
    for item in base_list:
        if isinstance(item, dict) and 'alias' in item:
            alias = item['alias']
            seen_aliases.add(alias)
            if alias in aliases_dict:
                # Merge env override into this item
                result.append(deep_merge(item, aliases_dict[alias]))
            else:
                result.append(item)
        else:
            result.append(item)

    # Add new instances from env that weren't in YAML
    for alias, fields in aliases_dict.items():
        if alias not in seen_aliases:
            new_item = dict(fields)
            new_item['alias'] = alias
            result.append(new_item)

    return result


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge dicts. Override values take priority. None = not set (preserves base).

    Special handling for multi-instance configs:
    - If override has '_aliases' key, it's a multi-instance env config
    - If base is a list (multi-instance YAML), merge by alias
    """
    result = base.copy()

    for key, override_value in override.items():
        if override_value is None:
            # None means "not set" in override, preserve base value
            continue

        # Check for multi-instance env config (has _aliases marker)
        if isinstance(override_value, dict) and '_aliases' in override_value:
            aliases_dict = override_value['_aliases']
            if key in result and isinstance(result[key], list):
                # YAML has list, env has aliases - merge by alias
                result[key] = _merge_list_by_alias(result[key], aliases_dict)
            elif key not in result or result[key] is None:
                # No YAML config - convert aliases to list
                result[key] = [
                    {**fields, 'alias': alias}
                    for alias, fields in aliases_dict.items()
                ]
            # else: YAML has single instance, env has multi - keep YAML (don't replace)
            continue

        if key in result and isinstance(result[key], dict) and isinstance(override_value, dict):
            # Recursively merge nested dicts
            result[key] = deep_merge(result[key], override_value)
        elif key in result and isinstance(result[key], list):
            # Base is list but override is not _aliases - preserve list
            continue
        else:
            # Override takes priority
            result[key] = override_value

    return result


def validate_service_config(service: str, config) -> list:
    """Validate service config has required fields (url and api_key).

    Args:
        service: Service name (e.g., 'sonarr')
        config: Service config - dict for single instance, list for multi-instance, or None

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if config is None:
        return errors

    configs = [config] if isinstance(config, dict) else config
    for i, cfg in enumerate(configs):
        if not isinstance(cfg, dict):
            continue
        alias = cfg.get('alias', f'instance {i}')
        if not cfg.get('url'):
            errors.append(f"{service} ({alias}): missing 'url'")
        if not cfg.get('api_key'):
            errors.append(f"{service} ({alias}): missing 'api_key'")
    return errors
