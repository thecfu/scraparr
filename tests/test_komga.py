"""Tests for the Komga connector."""

from unittest.mock import patch

from scraparr.const import ACTIVE_CONNECTORS, API_VERSIONS


def test_komga_registered_in_active_connectors():
    assert 'komga' in ACTIVE_CONNECTORS


def test_komga_api_version_is_v1():
    assert API_VERSIONS.get('komga') == 'v1'


def _make_module(detailed=False, exclude=None):
    config = {
        'url': 'http://komga:25600',
        'api_key': 'test-key',
        'alias': 'test',
        'api_version': 'v1',
        'detailed': detailed,
        'interval': 30,
        'exclude': exclude if exclude is not None else [],
    }
    from scraparr.connectors.komga import Module
    return Module(config)


def _page_response(content, total_elements=None, total_pages=1, page_number=0):
    if total_elements is None:
        total_elements = len(content)
    return {
        "content": content,
        "totalElements": total_elements,
        "totalPages": total_pages,
        "number": page_number,
    }


class TestGetPaged:
    @patch('scraparr.connectors.komga.Module.get')
    def test_single_page(self, mock_get):
        mod = _make_module()
        items = [{"id": "1"}, {"id": "2"}]
        mock_get.return_value = _page_response(items, total_elements=2, total_pages=1)

        result = mod._get_paged("/libraries")
        assert result == _page_response(items, total_elements=2, total_pages=1)
        mock_get.assert_called_once_with("/libraries?page=0&size=500")

    @patch('scraparr.connectors.komga.Module.get')
    def test_multiple_pages(self, mock_get):
        mod = _make_module()
        page0 = _page_response([{"id": "1"}], total_elements=2, total_pages=2, page_number=0)
        page1 = _page_response([{"id": "2"}], total_elements=2, total_pages=2, page_number=1)
        mock_get.side_effect = [page0, page1]

        result = mod._get_paged("/series", fetch_all=True)
        assert result["totalElements"] == 2
        assert len(result["content"]) == 2
        assert result["content"] == [{"id": "1"}, {"id": "2"}]

    @patch('scraparr.connectors.komga.Module.get')
    def test_empty_response(self, mock_get):
        mod = _make_module()
        mock_get.return_value = {}

        result = mod._get_paged("/libraries")
        assert result == {}


class TestScrape:
    @patch('scraparr.connectors.komga.Module._get_paged')
    @patch('scraparr.connectors.komga.Module._get_base')
    def test_scrape_success(self, mock_get_base, mock_paged):
        mod = _make_module()

        mock_get_base.return_value = {"build": {"version": "1.0.0"}}

        libraries_resp = _page_response([{"id": "lib1", "name": "Comics"}])
        series_resp = _page_response([{"id": "s1", "name": "Batman", "libraryId": "lib1",
                                       "metadata": {"status": "ONGOING", "genres": []},
                                       "booksCount": 10, "booksUnreadCount": 2,
                                       "booksReadCount": 5, "booksInProgressCount": 3}])
        books_resp = _page_response([{"id": "b1", "media": {"status": "READY"}}])
        collections_resp = _page_response([{"id": "c1"}])
        readlists_resp = _page_response([{"id": "r1"}])
        users_resp = _page_response([{"id": "u1"}])

        mock_paged.side_effect = [
            libraries_resp, series_resp, books_resp,
            collections_resp, readlists_resp, users_resp,
        ]

        data = mod.scrape()
        assert data is not None
        assert data["server_info"] == {"build": {"version": "1.0.0"}}
        assert data["libraries"]["totalElements"] == 1
        assert data["series"]["totalElements"] == 1
        assert data["books"]["totalElements"] == 1
        assert data["collections"]["totalElements"] == 1
        assert data["readlists"]["totalElements"] == 1
        assert data["users"]["totalElements"] == 1

    @patch('scraparr.connectors.komga.Module._get_paged')
    @patch('scraparr.connectors.komga.Module._get_base')
    def test_scrape_failure_marks_down(self, mock_get_base, mock_paged):
        mod = _make_module()
        mock_get_base.return_value = {}
        mock_paged.return_value = {}

        data = mod.scrape()
        assert data is None


class TestSeriesMetricsExclude:
    def test_exclude_filters_series_by_library_name(self):
        import scraparr.metrics.komga as komga_metrics

        mod = _make_module(detailed=True, exclude=['Manga'])

        libraries_resp = _page_response([
            {"id": "lib1", "name": "Comics"},
            {"id": "lib2", "name": "Manga"},
        ])
        series_resp = _page_response([
            {"id": "s1", "name": "Batman", "libraryId": "lib1",
             "metadata": {"status": "ONGOING", "genres": []},
             "booksCount": 10, "booksUnreadCount": 2,
             "booksReadCount": 5, "booksInProgressCount": 3},
            {"id": "s2", "name": "Naruto", "libraryId": "lib2",
             "metadata": {"status": "ENDED", "genres": []},
             "booksCount": 20, "booksUnreadCount": 0,
             "booksReadCount": 20, "booksInProgressCount": 0},
        ])

        mod._update_series_metrics(series_resp, libraries_resp)

        assert komga_metrics.SERIES_COUNT.labels('test')._value.get() == 1
        assert komga_metrics.SERIES_STATUS_COUNT.labels('test', 'ONGOING')._value.get() == 1
        assert komga_metrics.SERIES_STATUS_COUNT.labels('test', 'ENDED')._value.get() == 0
        assert komga_metrics.SERIES_BOOKS_COUNT.labels(
            'test', 'Comics', 'batman')._value.get() == 10

        # Excluded library's series must not be emitted.
        excluded_samples = [
            sample for sample in komga_metrics.SERIES_BOOKS_COUNT.collect()[0].samples
            if sample.labels.get('library') == 'Manga'
        ]
        assert not excluded_samples

        # Cleanup for test isolation.
        komga_metrics.SERIES_COUNT.remove_by_labels({"alias": "test"})
        komga_metrics.SERIES_STATUS_COUNT.remove_by_labels({"alias": "test"})
        komga_metrics.SERIES_BOOKS_COUNT.remove_by_labels({"alias": "test"})
        komga_metrics.SERIES_BOOKS_UNREAD.remove_by_labels({"alias": "test"})
        komga_metrics.SERIES_BOOKS_READ.remove_by_labels({"alias": "test"})
        komga_metrics.SERIES_BOOKS_IN_PROGRESS.remove_by_labels({"alias": "test"})
