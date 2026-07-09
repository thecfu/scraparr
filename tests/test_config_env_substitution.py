"""Tests for environment variable substitution in config loading."""

import os
import tempfile

import pytest
import yaml
from unittest.mock import patch

from scraparr.config_loader import (
    MissingEnvVarError,
    substitute_env_vars,
    coerce_config_types,
    load_yaml_config,
    load_yaml_config_safe,
    deep_merge,
)


class TestSubstituteEnvVars:
    """Test environment variable substitution."""

    def test_simple_substitution(self):
        """Substitute ${VAR} with env var value."""
        with patch.dict(os.environ, {"API_KEY": "secret123"}):
            result = substitute_env_vars({"api_key": "${API_KEY}"})
            assert result == {"api_key": "secret123"}

    def test_multiple_vars_in_string(self):
        """Substitute multiple vars in one string."""
        with patch.dict(os.environ, {"HOST": "localhost", "PORT": "8989"}):
            result = substitute_env_vars({"url": "http://${HOST}:${PORT}/api"})
            assert result == {"url": "http://localhost:8989/api"}


    def test_file_suffix_not_used_for_yaml_substitution(self):
        """YAML ${VAR} substitution only reads VAR, not VAR_FILE."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('file-secret\n')
            f.flush()
            with patch.dict(os.environ, {"API_KEY_FILE": f.name}, clear=True):
                with pytest.raises(MissingEnvVarError) as exc_info:
                    substitute_env_vars({"api_key": "${API_KEY}"})
            os.unlink(f.name)
        assert exc_info.value.var_name == "API_KEY"

    def test_default_value_when_missing(self):
        """Use default when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars({"host": "${MISSING:-localhost}"})
            assert result == {"host": "localhost"}

    def test_env_var_overrides_default(self):
        """Env var value takes precedence over default."""
        with patch.dict(os.environ, {"HOST": "server.local"}):
            result = substitute_env_vars({"host": "${HOST:-localhost}"})
            assert result == {"host": "server.local"}

    def test_missing_required_var_raises_error(self):
        """Missing required env var raises MissingEnvVarError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(MissingEnvVarError) as exc_info:
                substitute_env_vars({"key": "${REQUIRED}"})
            assert exc_info.value.var_name == "REQUIRED"

    def test_nested_dict_and_list(self):
        """Substitute in nested dicts and lists."""
        with patch.dict(os.environ, {"KEY": "secret", "VAL": "item"}):
            config = {"service": {"api_key": "${KEY}"}, "items": ["${VAL}", "static"]}
            result = substitute_env_vars(config)
            assert result["service"]["api_key"] == "secret"
            assert result["items"] == ["item", "static"]

    @pytest.mark.parametrize("value,expected_type", [
        (8989, int), (1.5, float), (True, bool), (None, type(None)),
    ])
    def test_non_string_types_unchanged(self, value, expected_type):
        """Non-string types pass through unchanged."""
        result = substitute_env_vars({"key": value})
        assert result["key"] == value
        assert isinstance(result["key"], expected_type)

    def test_dollar_without_braces_unchanged(self):
        """$VAR without braces is NOT substituted."""
        result = substitute_env_vars({"price": "$100"})
        assert result == {"price": "$100"}


class TestLoadYamlConfig:
    """Test YAML config loading."""

    def test_load_with_substitution(self):
        """Load YAML and substitute env vars."""
        with patch.dict(os.environ, {"SECRET": "mysecret"}):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write("api_key: ${SECRET}\n")
                f.flush()
                result = load_yaml_config(f.name)
                os.unlink(f.name)
            assert result == {"api_key": "mysecret"}

    def test_empty_config_returns_empty_dict(self):
        """Empty config returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            result = load_yaml_config(f.name)
            os.unlink(f.name)
        assert result == {}

    def test_file_not_found_raises(self):
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_yaml_config("/nonexistent/config.yaml")

    def test_invalid_yaml_raises(self):
        """Raise YAMLError for malformed YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [")
            f.flush()
            with pytest.raises(yaml.YAMLError):
                load_yaml_config(f.name)
            os.unlink(f.name)

    def test_safe_returns_empty_on_missing(self):
        """load_yaml_config_safe returns empty dict when file not found."""
        result = load_yaml_config_safe("/nonexistent/config.yaml")
        assert result == {}


class TestDeepMerge:
    """Test deep_merge function."""

    def test_override_wins(self):
        """Override values take priority over base."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        """Recursively merge nested dicts, override wins."""
        base = {"sonarr": {"url": "http://old", "api_key": "key1"}}
        override = {"sonarr": {"url": "http://new"}}
        result = deep_merge(base, override)
        assert result == {"sonarr": {"url": "http://new", "api_key": "key1"}}

    def test_none_preserves_base(self):
        """None in override means 'not set', preserves base value."""
        base = {"sonarr": {"url": "http://localhost", "api_key": "key"}}
        override = {"sonarr": None, "radarr": {"url": "http://radarr"}}
        result = deep_merge(base, override)
        assert result["sonarr"] == {"url": "http://localhost", "api_key": "key"}
        assert result["radarr"] == {"url": "http://radarr"}


class TestTypeCoercion:
    """Test type conversion for int/bool fields."""

    def test_int_fields_coerced(self):
        """Integer fields (interval, port, workers, within) are coerced."""
        config = {
            'sonarr': {'interval': '30', 'within': '7'},
            'general': {'port': '8080', 'workers': '4'}
        }
        result = coerce_config_types(config)
        assert result['sonarr']['interval'] == 30
        assert result['sonarr']['within'] == 7
        assert result['general']['port'] == 8080
        assert result['general']['workers'] == 4

    @pytest.mark.parametrize("value,expected", [
        ('true', True), ('True', True), ('TRUE', True),
        ('yes', True), ('1', True),
        ('false', False), ('False', False), ('FALSE', False),
        ('no', False), ('0', False), ('anything', False),
    ])
    def test_bool_field_coerced(self, value, expected):
        """Boolean field 'detailed' is coerced from various string values."""
        config = {'sonarr': {'detailed': value}}
        result = coerce_config_types(config)
        assert result['sonarr']['detailed'] is expected

    def test_non_coercible_fields_unchanged(self):
        """Fields not in INT_FIELDS/BOOL_FIELDS stay as strings."""
        config = {'sonarr': {'url': 'http://test', 'api_key': 'secret'}}
        result = coerce_config_types(config)
        assert result['sonarr']['url'] == 'http://test'
        assert result['sonarr']['api_key'] == 'secret'

    def test_already_typed_values_unchanged(self):
        """Values that are already int/bool pass through unchanged."""
        config = {'sonarr': {'interval': 30, 'detailed': True}}
        result = coerce_config_types(config)
        assert result['sonarr']['interval'] == 30
        assert result['sonarr']['detailed'] is True


class TestEnvVarParsing:
    """Test environment variable parsing."""

    @pytest.mark.parametrize("env_key,prefix,expected", [
        ('SONARR_URL', 'SONARR_', ('url', None)),
        ('SONARR_API_KEY', 'SONARR_', ('api_key', None)),
        ('SONARR_PROD_URL', 'SONARR_', ('url', 'prod')),
        ('SONARR_PROD_API_KEY', 'SONARR_', ('api_key', 'prod')),
        ('SONARR_MY_PROD_URL', 'SONARR_', ('url', 'my_prod')),
        ('SONARR_FOOBAR', 'SONARR_', None),
        ('RADARR_URL', 'SONARR_', None),
    ])
    def test_parse_service_field(self, env_key, prefix, expected):
        """Parse env var to extract field name and optional alias."""
        from scraparr.parser import _parse_service_field
        assert _parse_service_field(env_key, prefix) == expected

    def test_parse_general_and_auth(self):
        """Parse general and auth fields from env vars."""
        from scraparr.parser import _parse_mapping
        general = _parse_mapping(
            {'GENERAL_PORT': '8080', 'GENERAL_LOG_LEVEL': 'DEBUG'},
            {'GENERAL_PORT': 'port', 'GENERAL_LOG_LEVEL': 'log_level'}
        )
        assert general == {'port': '8080', 'log_level': 'DEBUG'}
        assert _parse_mapping({}, {'GENERAL_PORT': 'port'}) is None

        auth = _parse_mapping(
            {'AUTH_USERNAME': 'admin', 'AUTH_TOKEN': 'secret'},
            {'AUTH_USERNAME': 'username', 'AUTH_TOKEN': 'token'}
        )
        assert auth == {'username': 'admin', 'token': 'secret'}

    def test_parse_service_file_env_var(self):
        """Parse SONARR_API_KEY_FILE by reading the pointed file."""
        from scraparr.parser import parse_env_config
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('secret-from-file\n')
            f.flush()
            with patch.dict(os.environ, {'SONARR_API_KEY_FILE': f.name}, clear=True):
                env_config = parse_env_config()
            os.unlink(f.name)

        assert env_config['sonarr'] == {'api_key': 'secret-from-file'}

    def test_parse_general_file_env_var(self):
        """Parse GENERAL_*_FILE by reading the pointed file."""
        from scraparr.parser import parse_env_config
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('9090\n')
            f.flush()
            with patch.dict(os.environ, {'GENERAL_PORT_FILE': f.name}, clear=True):
                env_config = parse_env_config()
            os.unlink(f.name)

        assert env_config['general'] == {'port': '9090'}


class TestConfigMergeIntegration:
    """Integration tests for YAML + env var merge behavior."""

    def test_partial_env_override(self):
        """Env var overrides single field while YAML provides the rest."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {'SONARR_URL': 'http://override:8989'}, clear=True):
            env_config = parse_env_config()
            assert env_config['sonarr'] == {'url': 'http://override:8989'}

        yaml_config = {'sonarr': {'url': 'http://yaml:8989', 'api_key': 'yaml-key'}}
        result = deep_merge(yaml_config, env_config)
        assert result['sonarr']['url'] == 'http://override:8989'
        assert result['sonarr']['api_key'] == 'yaml-key'

    def test_general_partial_override_with_coercion(self):
        """GENERAL_PORT env var overrides and gets coerced to int."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {'GENERAL_PORT': '8080'}, clear=True):
            env_config = parse_env_config()

        yaml_config = {'general': {'port': 7100, 'workers': 5}}
        result = coerce_config_types(deep_merge(yaml_config, env_config))
        assert result['general']['port'] == 8080
        assert result['general']['workers'] == 5

    def test_add_service_via_env(self):
        """Add new service via env while keeping existing YAML services."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {
            'RADARR_URL': 'http://radarr:7878',
            'RADARR_API_KEY': 'radarr-key',
        }, clear=True):
            env_config = parse_env_config()

        yaml_config = {'sonarr': {'url': 'http://sonarr:8989', 'api_key': 'sonarr-key'}}
        result = deep_merge(yaml_config, env_config)
        assert result['sonarr']['api_key'] == 'sonarr-key'
        assert result['radarr']['api_key'] == 'radarr-key'


class TestMultiInstanceAliasEnvVars:
    """Test multi-instance alias-based env vars."""

    def test_parse_alias_env_vars(self):
        """Parse SONARR_PROD_URL as alias 'prod'."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {
            'SONARR_PROD_URL': 'http://prod:8989',
            'SONARR_PROD_API_KEY': 'prod-key',
            'SONARR_DEV_URL': 'http://dev:8989',
            'SONARR_DEV_API_KEY': 'dev-key',
        }, clear=True):
            env_config = parse_env_config()
            aliases = env_config['sonarr']['_aliases']
            assert aliases['prod'] == {'url': 'http://prod:8989', 'api_key': 'prod-key'}
            assert aliases['dev'] == {'url': 'http://dev:8989', 'api_key': 'dev-key'}

    def test_single_instance_no_aliases(self):
        """SONARR_URL (no alias) returns single-instance config."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {
            'SONARR_URL': 'http://sonarr:8989',
            'SONARR_API_KEY': 'key',
        }, clear=True):
            env_config = parse_env_config()
            assert env_config['sonarr'] == {'url': 'http://sonarr:8989', 'api_key': 'key'}
            assert '_aliases' not in env_config['sonarr']

    def test_alias_takes_precedence_over_single(self):
        """If any alias vars exist, use multi-instance mode."""
        from scraparr.parser import parse_env_config
        with patch.dict(os.environ, {
            'SONARR_URL': 'http://single:8989',  # Ignored
            'SONARR_PROD_URL': 'http://prod:8989',
            'SONARR_PROD_API_KEY': 'prod-key',
        }, clear=True):
            env_config = parse_env_config()
            assert '_aliases' in env_config['sonarr']

    def test_merge_aliases_with_yaml_list(self):
        """Merge env aliases into YAML list by matching alias field."""
        yaml_config = {
            'sonarr': [
                {'url': 'http://yaml-prod:8989', 'api_key': 'yaml-key', 'alias': 'prod'},
                {'url': 'http://yaml-dev:8989', 'api_key': 'dev-key', 'alias': 'dev'},
            ]
        }
        env_config = {'sonarr': {'_aliases': {'prod': {'url': 'http://env-prod:8989'}}}}
        result = deep_merge(yaml_config, env_config)

        assert isinstance(result['sonarr'], list)
        prod = next(s for s in result['sonarr'] if s.get('alias') == 'prod')
        assert prod['url'] == 'http://env-prod:8989'
        assert prod['api_key'] == 'yaml-key'

    def test_env_adds_new_alias_to_yaml_list(self):
        """Env can add new instance to YAML list via new alias."""
        yaml_config = {'sonarr': [{'url': 'http://prod:8989', 'alias': 'prod'}]}
        env_config = {'sonarr': {'_aliases': {'staging': {'url': 'http://staging:8989'}}}}
        result = deep_merge(yaml_config, env_config)

        assert len(result['sonarr']) == 2
        aliases = [s['alias'] for s in result['sonarr']]
        assert 'prod' in aliases and 'staging' in aliases

    def test_env_only_multi_instance(self):
        """Multi-instance config works with env only (no YAML)."""
        env_config = {'sonarr': {'_aliases': {
            'prod': {'url': 'http://prod:8989'},
            'dev': {'url': 'http://dev:8989'},
        }}}
        result = deep_merge({}, env_config)
        assert isinstance(result['sonarr'], list)
        assert len(result['sonarr']) == 2


class TestServiceConfigValidation:
    """Test post-merge validation of required fields."""

    def test_valid_config_no_errors(self):
        """Complete config with url and api_key returns no errors."""
        from scraparr.config_loader import validate_service_config
        config = {'url': 'http://sonarr:8989', 'api_key': 'test-key'}
        errors = validate_service_config('sonarr', config)
        assert errors == []

    def test_missing_url_returns_error(self):
        """Config missing url returns error."""
        from scraparr.config_loader import validate_service_config
        config = {'api_key': 'test-key'}
        errors = validate_service_config('sonarr', config)
        assert len(errors) == 1
        assert "missing 'url'" in errors[0]

    def test_missing_api_key_returns_error(self):
        """Config missing api_key returns error."""
        from scraparr.config_loader import validate_service_config
        config = {'url': 'http://sonarr:8989'}
        errors = validate_service_config('sonarr', config)
        assert len(errors) == 1
        assert "missing 'api_key'" in errors[0]

    def test_missing_both_returns_two_errors(self):
        """Config missing both url and api_key returns two errors."""
        from scraparr.config_loader import validate_service_config
        config = {'alias': 'test'}
        errors = validate_service_config('sonarr', config)
        assert len(errors) == 2

    def test_none_config_returns_no_errors(self):
        """None config (service not configured) returns no errors."""
        from scraparr.config_loader import validate_service_config
        errors = validate_service_config('sonarr', None)
        assert errors == []

    def test_multi_instance_list_validates_each(self):
        """Multi-instance config (list) validates each instance."""
        from scraparr.config_loader import validate_service_config
        config = [
            {'url': 'http://prod:8989', 'api_key': 'key1', 'alias': 'prod'},
            {'url': 'http://dev:8989', 'alias': 'dev'},  # missing api_key
        ]
        errors = validate_service_config('sonarr', config)
        assert len(errors) == 1
        assert 'dev' in errors[0]
        assert "missing 'api_key'" in errors[0]

    def test_error_includes_alias(self):
        """Error message includes the alias for identification."""
        from scraparr.config_loader import validate_service_config
        config = {'alias': 'production', 'url': 'http://sonarr:8989'}
        errors = validate_service_config('sonarr', config)
        assert 'production' in errors[0]
