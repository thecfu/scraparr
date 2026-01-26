"""
Config loading with environment variable substitution.

Supports ${VAR_NAME} and ${VAR_NAME:-default} syntax in YAML string values.
"""

import logging
import os
import re
from typing import Any

import yaml

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


def _substitute_string(value: str, config_path: str) -> str:
    """Substitute ${VAR} patterns in a string."""
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default_value = match.group(2)

        env_value = os.environ.get(var_name)
        if env_value is not None:
            return env_value

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


def load_yaml_config(file_path: str) -> dict:
    """Load YAML config file with environment variable substitution."""
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if config is None:
        return {}

    return substitute_env_vars(config)
