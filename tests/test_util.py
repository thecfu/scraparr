"""Tests for the util module connection pooling."""

import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import util


class TestGetSession:
    """Tests for _get_session() thread-local session management."""

    def test_returns_session_instance(self):
        """_get_session() returns a requests.Session instance."""
        session = util._get_session()
        assert isinstance(session, requests.Session)

    def test_same_thread_gets_same_session(self):
        """Same thread gets the same session instance (reuse verification)."""
        session1 = util._get_session()
        session2 = util._get_session()
        assert session1 is session2

    def test_different_threads_get_different_sessions(self):
        """Different threads get different session instances (thread safety)."""
        sessions = {}

        def get_session_in_thread(thread_id):
            sessions[thread_id] = util._get_session()

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

    def test_threadpool_workers_get_different_sessions(self):
        """ThreadPoolExecutor workers each get their own session."""
        import time
        session_ids = []

        def get_session_id():
            session_id = id(util._get_session())
            time.sleep(0.05)  # Hold thread to force parallel execution
            return session_id

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(get_session_id) for _ in range(4)]
            session_ids = [f.result() for f in futures]

        # Workers running in parallel should have different sessions
        assert len(set(session_ids)) > 1


class TestUtilGet:
    """Tests for util.get() using session-based requests."""

    @patch.object(util, '_get_session')
    def test_uses_session_get(self, mock_get_session):
        """util.get() uses session.get() instead of requests.get()."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = util.get('http://test/api', 'test-key')

        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with(
            'http://test/api',
            headers={'X-Api-Key': 'test-key'},
            timeout=20
        )
        assert result == {'data': 'test'}

    @patch.object(util, '_get_session')
    def test_handles_401_unauthorized(self, mock_get_session):
        """util.get() logs error and returns empty dict on 401."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = util.get('http://test/api', 'bad-key')

        assert result == {}

    @patch.object(util, '_get_session')
    def test_handles_404_not_found(self, mock_get_session):
        """util.get() logs error and returns empty dict on 404."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = util.get('http://test/api', 'key')

        assert result == {}

    @patch.object(util, '_get_session')
    def test_handles_request_exception(self, mock_get_session):
        """util.get() catches RequestException and returns empty dict."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_get_session.return_value = mock_session

        result = util.get('http://test/api', 'key')

        assert result == {}

    @patch.object(util, '_get_session')
    def test_handles_timeout_exception(self, mock_get_session):
        """util.get() catches Timeout and returns empty dict."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout("Timed out")
        mock_get_session.return_value = mock_session

        result = util.get('http://test/api', 'key')

        assert result == {}
