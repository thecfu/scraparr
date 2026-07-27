# Connectors

Each connector scrapes a specific service and exposes Prometheus metrics. All connectors share the [common configuration options](configuration.md#common-options). This page documents service-specific options, behaviors, and metrics.

A global metric `scraparr_services_up` (labels: `alias`, `scraparr_services`) is set to `1` on successful scrape and `0` on failure for every connector.

---

<details>
<summary><h2>Sonarr</h2> TV series management</summary>

**Default API version:** `v3`

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `episode_quality_stats` | bool | `true` | Fetch episode files per series to calculate quality breakdowns. Generates N extra API calls (one per series, parallelized). Disable for performance on large libraries. |
| `exclude` | list | `[]` | Root folder paths to exclude from metrics |

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `sonarr_last_scrape` | alias | all |
| `sonarr_scrape_duration` | alias | all |
| `sonarr_start_time` | alias | all |
| `sonarr_build_time` | alias | all |
| `sonarr_queue_count` | alias | all |
| `sonarr_queue_error` | alias | all |
| `sonarr_queue_warning` | alias | all |
| `sonarr_series` / `_total` | alias, path | all |
| `sonarr_episodes` / `_total` | alias, path | all |
| `sonarr_disk_size` / `_total` | alias, path | all |
| `sonarr_free_disk_size` | alias, path | all |
| `sonarr_available_disk_size` | alias, path | all |
| `sonarr_quality_episodes` / `_total` | alias, quality, path | all |
| `sonarr_genres_count` / `_total` | alias, genre, path | all |
| `sonarr_missing_episodes` / `_total` | alias, path | all |
| `sonarr_monitored_series` / `_total` | alias, path | all |
| `sonarr_unmonitored_series` / `_total` | alias, path | all |
| `sonarr_continuing_series` / `_total` | alias, path | all |
| `sonarr_upcoming_series` / `_total` | alias, path | all |
| `sonarr_ended_series` / `_total` | alias, path | all |
| `sonarr_deleted_series` / `_total` | alias, path | all |
| `sonarr_series_episodes` | alias, series | detailed |
| `sonarr_series_seasons` | alias, series | detailed |
| `sonarr_series_download_percentage` | alias, series | detailed |
| `sonarr_series_monitored` | alias, series | detailed |
| `sonarr_series_disk_size` | alias, series | detailed |
| `sonarr_series_missing_episodes` | alias, series | detailed |

</details>

---

<details>
<summary><h2>Radarr</h2> Movie management</summary>

**Default API version:** `v3`

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `exclude` | list | `[]` | Root folder paths to exclude from metrics |

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `radarr_last_scrape` | alias | all |
| `radarr_scrape_duration` | alias | all |
| `radarr_start_time` | alias | all |
| `radarr_build_time` | alias | all |
| `radarr_queue_count` | alias | all |
| `radarr_queue_error` | alias | all |
| `radarr_queue_warning` | alias | all |
| `radarr_movies` / `_total` | alias, path | all |
| `radarr_disk_size` / `_total` | alias, path | all |
| `radarr_free_disk_size` | alias, path | all |
| `radarr_available_disk_size` | alias, path | all |
| `radarr_quality_movies` / `_total` | alias, quality, path | all |
| `radarr_genres_count` / `_total` | alias, genre, path | all |
| `radarr_missing_movies` / `_total` | alias, path | all |
| `radarr_monitored_movies` / `_total` | alias, path | all |
| `radarr_unmonitored_movies` / `_total` | alias, path | all |
| `radarr_tba_movies` / `_total` | alias, path | all |
| `radarr_in_cinemas_movies` / `_total` | alias, path | all |
| `radarr_announced_movies` / `_total` | alias, path | all |
| `radarr_released_movies` / `_total` | alias, path | all |
| `radarr_deleted_movies` / `_total` | alias, path | all |
| `radarr_movie_missing` | alias, movie | detailed |
| `radarr_movie_files` | alias, movie | detailed |
| `radarr_movie_monitored` | alias, movie | detailed |
| `radarr_movie_disk_size` | alias, movie | detailed |

</details>

---

<details>
<summary><h2>Prowlarr</h2> Indexer management</summary>

**Default API version:** `v1`

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `prowlarr_last_scrape` | alias | all |
| `prowlarr_scrape_duration` | alias | all |
| `prowlarr_start_time` | alias | all |
| `prowlarr_build_time` | alias | all |
| `prowlarr_applications_total` | alias | all |
| `prowlarr_application_enabled_total` | alias | all |
| `prowlarr_application_sync_level_total` | alias, sync_level | all |
| `prowlarr_indexer_count` | alias, type | all |
| `prowlarr_indexer_count_total` | alias | all |
| `prowlarr_indexer_enabled_total` | alias | all |
| `prowlarr_indexer_privacy` | alias, type, privacy | all |
| `prowlarr_indexer_privacy_total` | alias, privacy | all |
| `prowlarr_vip_expiration` | alias, indexer | all |
| `prowlarr_queries_by_indexer` / `_total` | alias, indexer | all |
| `prowlarr_failed_queries_by_indexer` / `_total` | alias, indexer | all |
| `prowlarr_grabs_by_indexer` / `_total` | alias, indexer | all |
| `prowlarr_queries_by_user_agent` / `_total` | alias, user_agent | all |
| `prowlarr_grabs_by_user_agent` / `_total` | alias, user_agent | all |
| `prowlarr_queries_by_host` / `_total` | alias, host | all |
| `prowlarr_grabs_by_host` / `_total` | alias, host | all |
| `prowlarr_response_time_by_indexer_milliseconds` / `_total` | alias, indexer | all |
| `prowlarr_grab_response_time_by_indexer_milliseconds` / `_total` | alias, indexer | all |
| `prowlarr_application_enabled` | alias, application | detailed |
| `prowlarr_application_sync_level` | alias, application, sync_level | detailed |
| `prowlarr_indexer_enabled` | alias, type, indexer | detailed |
| `prowlarr_indexer_status` | alias, indexer, status | detailed |
| `prowlarr_indexer_healthy` | alias, indexer | detailed |

</details>

---

<details>
<summary><h2>Lidarr</h2> Music management</summary>

**Default API version:** `v1`

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `exclude` | list | `[]` | Root folder paths to exclude from metrics |

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `lidarr_last_scrape` | alias | all |
| `lidarr_scrape_duration` | alias | all |
| `lidarr_start_time` | alias | all |
| `lidarr_build_time` | alias | all |
| `lidarr_queue_count` | alias | all |
| `lidarr_queue_error` | alias | all |
| `lidarr_queue_warning` | alias | all |
| `lidarr_artists` / `_total` | alias, path | all |
| `lidarr_disk_size` / `_total` | alias, path | all |
| `lidarr_free_disk_size` | alias, path | all |
| `lidarr_available_disk_size` | alias, path | all |
| `lidarr_monitored_artists` / `_total` | alias, path | all |
| `lidarr_unmonitored_artists` / `_total` | alias, path | all |
| `lidarr_quality_tracks` / `_total` | alias, quality, path | all |
| `lidarr_release_type_count` / `_total` | alias, type, path | all |
| `lidarr_missing_releases` / `_total` | alias, path | all |
| `lidarr_monitored_releases` / `_total` | alias, path | all |
| `lidarr_unmonitored_releases` / `_total` | alias, path | all |
| `lidarr_continuing_artists` / `_total` | alias, path | all |
| `lidarr_inactive_artists` / `_total` | alias, path | all |
| `lidarr_artist_tracks` | alias, artist | detailed |
| `lidarr_artist_releases` | alias, artist | detailed |
| `lidarr_artist_monitored` | alias, artist | detailed |
| `lidarr_artist_disk_size` | alias, artist | detailed |
| `lidarr_artist_missing_releases` | alias, artist | detailed |

**Note:** Makes 2 extra API calls per artist (albums + track files). Missing releases are releases where `percentOfTracks` is not 100% on monitored releases.

</details>

---

<details>
<summary><h2>Readarr</h2> Book management</summary>

**Default API version:** `v1`

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `exclude` | list | `[]` | Root folder paths to exclude from metrics |

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `readarr_last_scrape` | alias | all |
| `readarr_scrape_duration` | alias | all |
| `readarr_start_time` | alias | all |
| `readarr_build_time` | alias | all |
| `readarr_free_disk_size` | alias, path | all |
| `readarr_available_disk_size` | alias, path | all |
| `readarr_queue_count` | alias | all |
| `readarr_queue_error` | alias | all |
| `readarr_queue_warning` | alias | all |
| `readarr_author_status` | alias, status | all |
| `readarr_author_rating_total` | alias | all |
| `readarr_book_genres` | alias, genre | all |
| `readarr_book_disk_size_total` | alias | all |
| `readarr_book_rating_total` | alias | all |
| `readarr_author_disk_size` | alias, author | detailed |
| `readarr_author_book_count` | alias, author | detailed |
| `readarr_author_rating` | alias, author | detailed |
| `readarr_book_disk_size` | alias, book | detailed |
| `readarr_book_rating` | alias, book | detailed |
| `readarr_book_percentage` | alias, book | detailed |

</details>

---

<details>
<summary><h2>Bazarr</h2> Subtitle management</summary>

**Default API version:** not used (direct `/api/` paths)

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `bazarr_last_scrape` | alias | all |
| `bazarr_scrape_duration` | alias | all |
| `bazarr_start_time` | alias | all |
| `bazarr_build_time` | alias | all |
| `bazarr_series_total` | alias | all |
| `bazarr_movies_total` | alias | all |
| `bazarr_wanted_episodes_total` | alias | all |
| `bazarr_wanted_movies_total` | alias | all |
| `bazarr_providers` | alias | all |
| `bazarr_provider_status` | alias, provider, status | all |
| `bazarr_wanted_episodes` | alias, series | detailed |
| `bazarr_wanted_movies` | alias, movie | detailed |

**Note:** Only counts series/movies that have a subtitle profile assigned (`profileId` is not null).

</details>

---

<details>
<summary><h2>Jellyfin</h2> Media server</summary>

**Default API version:** not used (direct API paths)

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `within` | int | `300` | Time window in seconds for active sessions |
| `session_details` | bool | `false` | Enable per-stream metrics (position, transcoding, bitrate) |
| `client_info` | bool | `false` | Enable client version info (requires `session_details: true`) |

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `jellyfin_last_scrape` | alias | all |
| `jellyfin_scrape_duration` | alias | all |
| `jellyfin_version` | alias, version | all |
| `jellyfin_has_update` | alias | all |
| `jellyfin_number_of_devices` | alias | all |
| `jellyfin_number_of_users` | alias | all |
| `jellyfin_number_of_movies` | alias | all |
| `jellyfin_number_of_series` | alias | all |
| `jellyfin_genres_total` | alias, genre | all |
| `jellyfin_sessions_total` | alias | all |
| `jellyfin_sessions` | alias, user_id, user_name | detailed |
| `jellyfin_session_position_seconds` | alias, username, device, client, type, method | session_details |
| `jellyfin_session_duration_seconds` | (same) | session_details |
| `jellyfin_session_transcoding` | (same) | session_details |
| `jellyfin_session_paused` | (same) | session_details |
| `jellyfin_session_bitrate_bits` | (same) | session_details |
| `jellyfin_session_client_info` | alias, username, device, client, client_version | client_info |

**Note:** Jellyfin uses `Authorization: Mediabrowser Token=` header format instead of `X-Api-Key`.

</details>

---

<details>
<summary><h2>Kavita</h2> Reading server for manga, comics, and books</summary>

**Default API version:** not used (direct `/api/` paths)

### Additional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `legacy_auth` | bool | `false` | Use JWT authentication instead of `x-api-key` header. Required for older Kavita versions. |

The `exclude` option accepts **library names or IDs** (not root folder paths like other connectors).

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `kavita_last_scrape` | alias | all |
| `kavita_scrape_duration` | alias | all |
| `kavita_api_key_expiration` | alias | all |
| `kavita_version` | alias, version | all |
| `kavita_is_docker` | alias | all |
| `kavita_series_count` | alias | all |
| `kavita_volume_count` | alias | all |
| `kavita_chapter_count` | alias | all |
| `kavita_total_files` | alias | all |
| `kavita_total_size_bytes` | alias | all |
| `kavita_total_genres` | alias | all |
| `kavita_total_tags` | alias | all |
| `kavita_total_people` | alias | all |
| `kavita_total_reading_time` | alias | all |
| `kavita_library_count` | alias | all |
| `kavita_library_series_count` | alias, library | all |
| `kavita_library_folder_watching` | alias, library | all |
| `kavita_library_scrobbling` | alias, library | all |
| `kavita_library_type` | alias, library, type | all |
| `kavita_library_total_pages` | alias, library | all |
| `kavita_library_total_word_count` | alias, library | all |
| `kavita_library_avg_reading_time_hours` | alias, library | all |
| `kavita_library_genre_count` | alias, library, genre | all |
| `kavita_library_format_count` | alias, library, format | all |
| `kavita_publication_status_count` | alias, status | all |
| `kavita_manga_format_count` | alias, format | all |
| `kavita_user_count` | alias | all |
| `kavita_file_extension_count` | alias, extension | all |
| `kavita_file_extension_size_bytes` | alias, extension | all |
| `kavita_series_pages` | alias, library, series | detailed |
| `kavita_series_word_count` | alias, library, series | detailed |
| `kavita_series_pages_read` | alias, library, series | detailed |
| `kavita_series_user_rating` | alias, library, series | detailed |
| `kavita_series_avg_hours_to_read` | alias, library, series | detailed |
| `kavita_series_min_hours_to_read` | alias, library, series | detailed |
| `kavita_series_max_hours_to_read` | alias, library, series | detailed |
| `kavita_series_format` | alias, library, series, format | detailed |

</details>

---

<details>
<summary><h2>Komga</h2> Media server for comics and manga</summary>

**Default API version:** not used (direct `/api/` paths, mixes v1 and v2)

The `exclude` option accepts **library names or IDs** (not root folder paths like other connectors).

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `komga_last_scrape` | alias | all |
| `komga_scrape_duration` | alias | all |
| `komga_version` | alias, version | all |
| `komga_library_count` | alias | all |
| `komga_library_series_count` | alias, library | all |
| `komga_library_books_count` | alias, library | all |
| `komga_series_count` | alias | all |
| `komga_series_status_count` | alias, status | all |
| `komga_book_count` | alias | all |
| `komga_book_media_status_count` | alias, status | all |
| `komga_collection_count` | alias | all |
| `komga_readlist_count` | alias | all |
| `komga_user_count` | alias | all |
| `komga_library_genre_count` | alias, library, genre | detailed |
| `komga_series_books_count` | alias, library, series | detailed |
| `komga_series_books_unread` | alias, library, series | detailed |
| `komga_series_books_read` | alias, library, series | detailed |
| `komga_series_books_in_progress` | alias, library, series | detailed |

</details>

---

<details>
<summary><h2>SABnzbd</h2> Usenet download client</summary>

**Default API version:** not used (single `/api` endpoint)

**Note:** SABnzbd passes the API key as a query parameter (`?apikey=`) instead of using headers.

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `sabnzbd_last_scrape` | alias | all |
| `sabnzbd_scrape_duration` | alias | all |
| `sabnzbd_queue_speed_bytes` | alias | all |
| `sabnzbd_queue_size_bytes` | alias | all |
| `sabnzbd_queue_remaining_bytes` | alias | all |
| `sabnzbd_queue_slots` | alias | all |
| `sabnzbd_queue_paused` | alias | all |
| `sabnzbd_disk_space_bytes` | alias | all |
| `sabnzbd_disk_space_total_bytes` | alias | all |
| `sabnzbd_history_total_bytes` | alias | all |
| `sabnzbd_history_day_bytes` | alias | all |
| `sabnzbd_history_week_bytes` | alias | all |
| `sabnzbd_history_month_bytes` | alias | all |
| `sabnzbd_history_failed_jobs` | alias | all |
| `sabnzbd_server_total_bytes` | alias, server | all |
| `sabnzbd_server_day_bytes` | alias, server | all |
| `sabnzbd_server_week_bytes` | alias, server | all |
| `sabnzbd_server_month_bytes` | alias, server | all |
| `sabnzbd_server_articles_tried` | alias, server | all |
| `sabnzbd_server_articles_success` | alias, server | all |

**Note:** SABnzbd does not have a `detailed` mode - all metrics are always exposed. All size values are in bytes.

</details>

---

<details>
<summary><h2>Seerr</h2> Media request management (Jellyseerr, Overseerr)</summary>

**Default API version:** `v1`

> **Deprecation notice:** The `jellyseerr` and `overseerr` connector names still work but are deprecated. Use `seerr` instead - it produces the same metrics with a `seerr_` prefix.

### Metrics

| Metric | Labels | Mode |
|--------|--------|------|
| `seerr_last_scrape` | alias | all |
| `seerr_scrape_duration` | alias | all |
| `seerr_user_total` | alias | all |
| `seerr_user_requests` | alias, user | all |
| `seerr_request_total` | alias | all |
| `seerr_request_tv` | alias | all |
| `seerr_request_movie` | alias | all |
| `seerr_request_status` | alias, status | all |
| `seerr_request_seasons_total` | alias | all |
| `seerr_issue_total` | alias | all |
| `seerr_issue_status` | alias, status | all |
| `seerr_issue_type` | alias, type | all |
| `seerr_issue_media_type` | alias, media_type | all |
| `seerr_issue_and_media_type` | alias, issue_type, media_type | all |
| `seerr_request_timestamp` | alias, request | detailed |
| `seerr_request_seasons` | alias, request | detailed |
| `seerr_issue_title` | alias, issue | detailed |
| `seerr_issue_created` | alias, issue | detailed |
| `seerr_issue_updated` | alias, issue | detailed |

**Note:** When `detailed` is enabled, title resolution makes parallel API calls to TMDB/TVDB endpoints for display names.

</details>

---

<details>
<summary><h2>Whisparr</h2> Adult content management</summary>

**Default API version:** `v3`

Shares the same codebase as Sonarr.

### Additional Options

Same as [Sonarr](#sonarr), including `episode_quality_stats` and `exclude`.

### Metrics

Same structure as Sonarr but with `whisparr_` prefix and uses "sites"/"scenes" terminology instead of "series"/"episodes".

</details>
