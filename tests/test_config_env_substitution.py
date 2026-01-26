"""Tests for environment variable substitution in config loading."""

import os
import tempfile

import pytest
import yaml
from unittest.mock import patch

from scraparr.config_loader import (
    MissingEnvVarError,
    substitute_env_vars,
    load_yaml_config,
)


class TestSubstituteEnvVars:
    """Test environment variable substitution."""

    def test_simple_substitution(self):
        """Substitute ${VAR} with env var value."""
        with patch.dict(os.environ, {"API_KEY": "secret123"}):
            result = substitute_env_vars({"api_key": "${API_KEY}"})
            assert result == {"api_key": "secret123"}

    def test_partial_substitution(self):
        """Substitute multiple vars in one string."""
        with patch.dict(os.environ, {"HOST": "localhost", "PORT": "8989"}):
            result = substitute_env_vars({"url": "http://${HOST}:${PORT}/api"})
            assert result == {"url": "http://localhost:8989/api"}

    def test_default_value(self):
        """Use default when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MISSING", None)
            result = substitute_env_vars({"host": "${MISSING:-localhost}"})
            assert result == {"host": "localhost"}

    def test_env_var_overrides_default(self):
        """Env var value takes precedence over default."""
        with patch.dict(os.environ, {"HOST": "server.local"}):
            result = substitute_env_vars({"host": "${HOST:-localhost}"})
            assert result == {"host": "server.local"}

    def test_missing_var_raises_error(self):
        """Missing required env var raises MissingEnvVarError."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("REQUIRED", None)
            with pytest.raises(MissingEnvVarError) as exc_info:
                substitute_env_vars({"key": "${REQUIRED}"})
            assert exc_info.value.var_name == "REQUIRED"
            assert "key" in str(exc_info.value)

    def test_nested_dict(self):
        """Substitute in nested dicts."""
        with patch.dict(os.environ, {"KEY": "secret"}):
            config = {"sonarr": {"api_key": "${KEY}"}}
            result = substitute_env_vars(config)
            assert result["sonarr"]["api_key"] == "secret"

    def test_list_values(self):
        """Substitute in list values."""
        with patch.dict(os.environ, {"VAR": "value"}):
            result = substitute_env_vars({"items": ["${VAR}", "static"]})
            assert result == {"items": ["value", "static"]}

    @pytest.mark.parametrize("value,expected_type", [
        (8989, int),
        (1.5, float),
        (True, bool),
        (None, type(None)),
    ])
    def test_non_string_types_unchanged(self, value, expected_type):
        """Non-string types pass through unchanged."""
        result = substitute_env_vars({"key": value})
        assert result["key"] == value
        assert isinstance(result["key"], expected_type)

    def test_string_without_pattern_unchanged(self):
        """Plain strings without ${} pass through unchanged."""
        result = substitute_env_vars({"url": "http://localhost:8989"})
        assert result == {"url": "http://localhost:8989"}

    def test_dollar_without_braces_unchanged(self):
        """$VAR without braces is NOT substituted."""
        result = substitute_env_vars({"price": "$100"})
        assert result == {"price": "$100"}


class TestLoadYamlConfig:
    """Test YAML config loading with env var substitution."""

    def test_load_with_substitution(self):
        """Load YAML and substitute env vars."""
        with patch.dict(os.environ, {"SECRET": "mysecret"}):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write("api_key: ${SECRET}\n")
                f.flush()
                result = load_yaml_config(f.name)
                os.unlink(f.name)
            assert result == {"api_key": "mysecret"}

    def test_load_empty_config(self):
        """Empty config returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            result = load_yaml_config(f.name)
            os.unlink(f.name)
        assert result == {}

    def test_file_not_found(self):
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_yaml_config("/nonexistent/config.yaml")

    def test_invalid_yaml(self):
        """Raise YAMLError for malformed YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [")
            f.flush()
            with pytest.raises(yaml.YAMLError):
                load_yaml_config(f.name)
            os.unlink(f.name)

    def test_missing_env_var_raises_error(self):
        """Raise MissingEnvVarError for unset required var."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("REQUIRED", None)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write("key: ${REQUIRED}\n")
                f.flush()
                with pytest.raises(MissingEnvVarError):
                    load_yaml_config(f.name)
                os.unlink(f.name)


class TestBackwardsCompatibility:
    """Ensure existing configs without env vars work unchanged."""

    def test_config_without_env_vars(self):
        """Config with hardcoded values works unchanged."""
        config = {
            "sonarr": {
                "url": "http://sonarr:8989",
                "api_key": "hardcoded_key",
                "detailed": True,
                "interval": 30
            }
        }
        result = substitute_env_vars(config)
        assert result == config

    def test_mixed_hardcoded_and_env_vars(self):
        """Mix of hardcoded and env var values."""
        with patch.dict(os.environ, {"SONARR_KEY": "secret"}):
            config = {
                "sonarr": {
                    "url": "http://sonarr:8989",
                    "api_key": "${SONARR_KEY}"
                },
                "radarr": {
                    "url": "http://radarr:7878",
                    "api_key": "hardcoded"
                }
            }
            result = substitute_env_vars(config)
            assert result["sonarr"]["api_key"] == "secret"
            assert result["radarr"]["api_key"] == "hardcoded"
            assert result["sonarr"]["url"] == "http://sonarr:8989"
