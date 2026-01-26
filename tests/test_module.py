"""Tests for the module connection pooling."""

import threading
from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import module


class TestGetSession:
    """Tests for _get_session() thread-local session management."""

    def test_returns_session_instance(self):
        """_get_session() returns a requests.Session instance."""
        session = module._get_session()
        assert isinstance(session, requests.Session)

    def test_same_thread_gets_same_session(self):
        """Same thread gets the same session instance (reuse verification)."""
        session1 = module._get_session()
        session2 = module._get_session()
        assert session1 is session2

    def test_different_threads_get_different_sessions(self):
        """Different threads get different session instances (thread safety)."""
        sessions = {}

        def get_session_in_thread(thread_id):
            sessions[thread_id] = module._get_session()

        threads = []
        for i in range(3):
            t = threading.Thread(target=get_session_in_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All sessions should be different objects
        session_ids = [id(s) for s in sessions.values()]
        assert len(set(session_ids)) == 3


class TestConnectorModuleGet:
    """Tests for ConnectorModule.get() using session-based requests."""

    def setup_method(self):
        """Create a concrete implementation of ConnectorModule for testing."""
        # Create a concrete subclass since ConnectorModule is abstract
        class TestModule(module.ConnectorModule):
            def scrape(self):
                return {}
            def update_metrics(self, data):
                pass
            def clear(self):
                pass

        config = {
            'url': 'http://test',
            'api_key': 'test-key',
            'api_version': 'v3',
            'alias': 'test_module',
            'detailed': False
        }
        self.module = TestModule(config, 'test')

    @patch.object(module, '_get_session')
    def test_uses_session_get(self, mock_get_session):
        """ConnectorModule.get() uses session.get() instead of requests.get()."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.get('/endpoint')

        mock_get_session.assert_called()
        mock_session.get.assert_called_once_with(
            'http://test/endpoint',
            headers={'X-Api-Key': 'test-key'},
            timeout=20
        )
        assert result == {'data': 'test'}

    @patch.object(module, '_get_session')
    def test_handles_401_unauthorized(self, mock_get_session):
        """ConnectorModule.get() returns empty dict on 401."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.get('/endpoint')

        assert result == {}

    @patch.object(module, '_get_session')
    def test_handles_404_not_found(self, mock_get_session):
        """ConnectorModule.get() returns empty dict on 404."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.get('/endpoint')

        assert result == {}

    @patch.object(module, '_get_session')
    def test_handles_request_exception(self, mock_get_session):
        """ConnectorModule.get() catches RequestException and returns empty dict."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_get_session.return_value = mock_session

        result = self.module.get('/endpoint')

        assert result == {}

    @patch.object(module, '_get_session')
    def test_handles_timeout_exception(self, mock_get_session):
        """ConnectorModule.get() catches Timeout and returns empty dict."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout("Timed out")
        mock_get_session.return_value = mock_session

        result = self.module.get('/endpoint')

        assert result == {}

    @patch.object(module, '_get_session')
    def test_endpoint_with_leading_slash(self, mock_get_session):
        """Endpoint with leading slash is handled correctly."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        self.module.get('/test/endpoint')

        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == 'http://test/test/endpoint'

    @patch.object(module, '_get_session')
    def test_endpoint_without_leading_slash(self, mock_get_session):
        """Endpoint without leading slash is handled correctly."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        self.module.get('test/endpoint')

        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == 'http://test/test/endpoint'


class TestConnectorModulePost:
    """Tests for ConnectorModule.post() using session-based requests."""

    def setup_method(self):
        """Create a concrete implementation of ConnectorModule for testing."""
        class TestModule(module.ConnectorModule):
            def scrape(self):
                return {}
            def update_metrics(self, data):
                pass
            def clear(self):
                pass

        config = {
            'url': 'http://test',
            'api_key': 'test-key',
            'api_version': 'v3',
            'alias': 'test_module',
            'detailed': False
        }
        self.module = TestModule(config, 'test')

    @patch.object(module, '_get_session')
    def test_uses_session_post(self, mock_get_session):
        """ConnectorModule.post() uses session.post() instead of requests.post()."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 1}
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.post('/endpoint', {'data': 'test'})

        mock_get_session.assert_called()
        mock_session.post.assert_called_once_with(
            'http://test/endpoint',
            headers={'X-Api-Key': 'test-key'},
            json={'data': 'test'},
            timeout=20
        )
        assert result == {'id': 1}

    @patch.object(module, '_get_session')
    def test_handles_request_exception(self, mock_get_session):
        """ConnectorModule.post() catches RequestException and returns empty dict."""
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_get_session.return_value = mock_session

        result = self.module.post('/endpoint', {'data': 'test'})

        assert result == {}
