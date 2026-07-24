"""Tests for the Komga connector."""

from unittest.mock import patch

from scraparr.const import ACTIVE_CONNECTORS, API_VERSIONS


def test_komga_registered_in_active_connectors():
    assert 'komga' in ACTIVE_CONNECTORS


def test_komga_api_version_set():
    assert API_VERSIONS.get('komga') == 'dummy'


def _make_module(detailed=False, exclude=None):
    config = {
        'url': 'http://komga:25600',
        'api_key': 'test-key',
        'alias': 'test',
        'api_version': 'dummy',
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


class TestWrapList:
    def test_wrap_plain_list(self):
        mod = _make_module()
        data = [{"id": "1"}, {"id": "2"}]
        result = mod._wrap_list(data)
        assert result == {"content": data, "totalElements": 2, "totalPages": 1}

    def test_wrap_already_paginated(self):
        mod = _make_module()
        data = _page_response([{"id": "1"}])
        result = mod._wrap_list(data)
        assert result == data

    def test_wrap_empty_list(self):
        mod = _make_module()
        result = mod._wrap_list([])
        assert result == {"content": [], "totalElements": 0, "totalPages": 1}


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
    def test_plain_list_response(self, mock_get):
        """Endpoints like /api/v1/libraries return plain arrays, not paginated objects."""
        mod = _make_module()
        mock_get.return_value = [{"id": "lib1", "name": "Comics"}, {"id": "lib2", "name": "Manga"}]

        result = mod._get_paged("/api/v1/libraries")
        assert result["content"] == [{"id": "lib1", "name": "Comics"}, {"id": "lib2", "name": "Manga"}]
        assert result["totalElements"] == 2
        assert result["totalPages"] == 1

    @patch('scraparr.connectors.komga.Module.get')
    def test_empty_response(self, mock_get):
        mod = _make_module()
        mock_get.return_value = {}

        result = mod._get_paged("/libraries")
        assert result == {}


class TestScrape:
    @patch('scraparr.connectors.komga.Module._get_paged')
    @patch('scraparr.connectors.komga.Module.get')
    def test_scrape_success(self, mock_get, mock_paged):
        mod = _make_module()

        mock_get.return_value = {"build": {"version": "1.0.0"}}

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
    @patch('scraparr.connectors.komga.Module.get')
    def test_scrape_failure_marks_down(self, mock_get, mock_paged):
        mod = _make_module()
        mock_get.return_value = {}
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


class TestUpdateMetrics:
    def test_update_server_metrics(self):
        mod = _make_module()
        server_info = {"build": {"version": "1.14.0"}}
        mod._update_server_metrics(server_info)
        import scraparr.metrics.komga as komga_metrics
        komga_metrics.VERSION.labels("test", "1.14.0")._mock_name = "VERSION"

    def test_update_library_metrics(self):
        mod = _make_module()
        libraries = _page_response([
            {"id": "lib1", "name": "Comics"},
            {"id": "lib2", "name": "Manga"},
        ])
        series = _page_response([
            {"id": "s1", "libraryId": "lib1", "name": "Batman",
             "booksCount": 5, "metadata": {"status": "ONGOING", "genres": ["Action"]}},
            {"id": "s2", "libraryId": "lib1", "name": "Superman",
             "booksCount": 3, "metadata": {"status": "ENDED", "genres": ["Action", "Sci-Fi"]}},
            {"id": "s3", "libraryId": "lib2", "name": "Naruto",
             "booksCount": 72, "metadata": {"status": "ENDED", "genres": ["Shonen"]}},
        ])

        mod._update_library_metrics(libraries, series)

    def test_update_series_status_counts(self):
        mod = _make_module()
        libraries = _page_response([
            {"id": "lib1", "name": "Comics"},
        ])
        series = _page_response([
            {"id": "s1", "name": "A", "libraryId": "lib1", "metadata": {"status": "ONGOING"}},
            {"id": "s2", "name": "B", "libraryId": "lib1", "metadata": {"status": "ONGOING"}},
            {"id": "s3", "name": "C", "libraryId": "lib1", "metadata": {"status": "ENDED"}},
        ], total_elements=3)
        mod._update_series_metrics(series, libraries)

    def test_update_book_media_counts(self):
        mod = _make_module()
        books = _page_response([
            {"id": "b1", "media": {"status": "READY"}},
            {"id": "b2", "media": {"status": "READY"}},
            {"id": "b3", "media": {"status": "ERROR"}},
        ], total_elements=3)
        mod._update_book_metrics(books)

    def test_update_metrics_full(self):
        mod = _make_module()
        data = {
            "server_info": {"build": {"version": "1.14.0"}},
            "libraries": _page_response([{"id": "lib1", "name": "Comics"}]),
            "series": _page_response([
                {"id": "s1", "libraryId": "lib1", "name": "Batman",
                 "booksCount": 5, "metadata": {"status": "ONGOING", "genres": []}},
            ]),
            "books": _page_response([{"id": "b1", "media": {"status": "READY"}}]),
            "collections": _page_response([{"id": "c1"}]),
            "readlists": _page_response([{"id": "r1"}]),
            "users": _page_response([{"id": "u1"}, {"id": "u2"}]),
        }
        mod.update_metrics(data)

    def test_exclude_library(self):
        config = {
            'url': 'http://komga:25600', 'api_key': 'test-key',
            'alias': 'test', 'api_version': 'dummy',
            'detailed': False, 'interval': 30,
            'exclude': ['Manga'],
        }
        from scraparr.connectors.komga import Module
        mod = Module(config)

        libraries = _page_response([
            {"id": "lib1", "name": "Comics"},
            {"id": "lib2", "name": "Manga"},
        ])
        series = _page_response([
            {"id": "s1", "libraryId": "lib1", "name": "X", "booksCount": 1,
             "metadata": {"status": "ONGOING", "genres": []}},
        ])
        mod._update_library_metrics(libraries, series)


class TestClear:
    def test_clear_does_not_raise(self):
        mod = _make_module()
        data = {
            "server_info": {"build": {"version": "1.0.0"}},
            "libraries": _page_response([{"id": "lib1", "name": "Comics"}]),
            "series": _page_response([
                {"id": "s1", "libraryId": "lib1", "name": "Batman",
                 "booksCount": 5, "metadata": {"status": "ONGOING", "genres": []}},
            ]),
            "books": _page_response([{"id": "b1", "media": {"status": "READY"}}]),
            "collections": _page_response([{"id": "c1"}]),
            "readlists": _page_response([{"id": "r1"}]),
            "users": _page_response([{"id": "u1"}]),
        }
        mod.update_metrics(data)
        mod.clear()


class TestDetailedMode:
    def test_detailed_series_metrics(self):
        mod = _make_module(detailed=True)
        libraries = _page_response([{"id": "lib1", "name": "Comics"}])
        series = _page_response([
            {"id": "s1", "libraryId": "lib1", "name": "Batman Returns",
             "booksCount": 10, "booksUnreadCount": 2,
             "booksReadCount": 5, "booksInProgressCount": 3,
             "metadata": {"status": "ONGOING", "genres": ["Action"]}},
        ], total_elements=1)
        mod._update_series_metrics(series, libraries)

    def test_detailed_library_genres(self):
        mod = _make_module(detailed=True)
        libraries = _page_response([{"id": "lib1", "name": "Comics"}])
        series = _page_response([
            {"id": "s1", "libraryId": "lib1", "name": "Batman",
             "booksCount": 5,
             "metadata": {"status": "ONGOING", "genres": ["Action", "Drama"]}},
            {"id": "s2", "libraryId": "lib1", "name": "Superman",
             "booksCount": 3,
             "metadata": {"status": "ENDED", "genres": ["Action", "Sci-Fi"]}},
        ])
        mod._update_library_metrics(libraries, series)

    def test_non_detailed_skips_per_series(self):
        mod = _make_module(detailed=False)
        libraries = _page_response([{"id": "lib1", "name": "Comics"}])
        series = _page_response([
            {"id": "s1", "libraryId": "lib1", "name": "Batman",
             "booksCount": 10, "booksUnreadCount": 2,
             "booksReadCount": 5, "booksInProgressCount": 3,
             "metadata": {"status": "ONGOING", "genres": ["Action"]}},
        ])
        mod._update_series_metrics(series, libraries)
