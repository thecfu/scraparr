"""
Module to handle the Metrics of the Jellyfin Service
"""

import time

import requests

import scraparr.metrics.jellyfin as jellyfin_metrics
from scraparr.connectors.module import ConnectorModule, _get_session
from scraparr.metrics.general import UP
from scraparr.connectors import util

QUERY = "SortBy=SortName%2CProductionYear&SortOrder=Ascending&Recursive=true"

class Module(ConnectorModule):
    """Module Class for Jellyfin"""

    def __init__(self, config):
        """Initialize the Module"""
        ConnectorModule.__init__(self, config, "jellyfin")
        self.within = config.get('within', 300)
        self.session_details = config.get('session_details', False)
        self.client_info = config.get('client_info', False)
        self.header = None

    def clear(self):
        """Clear the Metrics for the Service"""
        jellyfin_metrics.SESSIONS.remove_by_labels({"alias": self.alias})
        if self.session_details:
            jellyfin_metrics.SESSION_POSITION.remove_by_labels({"alias": self.alias})
            jellyfin_metrics.SESSION_DURATION.remove_by_labels({"alias": self.alias})
            jellyfin_metrics.SESSION_TRANSCODING.remove_by_labels({"alias": self.alias})
            jellyfin_metrics.SESSION_PAUSED.remove_by_labels({"alias": self.alias})
            jellyfin_metrics.SESSION_BITRATE.remove_by_labels({"alias": self.alias})
        if self.client_info:
            jellyfin_metrics.SESSION_CLIENT_INFO.remove_by_labels({"alias": self.alias})


    def get_header(self):
        """Translate the API Key into a Header for Jellyfin"""
        token = f"Mediabrowser Token={self.api_key}"
        self.header = {"Authorization": token}

    def get_number_of_devices(self):
        """Grab the Devices from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Devices", headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            return res.json()['TotalRecordCount']
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None


    def get_genres(self):
        """Grab the Genres from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Genres", headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            data = res.json()
            genre_names = {item["Name"]: {"total": 1} for item in data.get("Items", [])}
            return genre_names
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def get_number_of_user(self):
        """Grab the Users from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Users", headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            data = res.json()
            return len(data)
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def get_number_of_movies(self):
        """Grab the Movies from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Items?{QUERY}&IncludeItemTypes=Movie",
                              headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            return res.json()['TotalRecordCount']
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def get_number_of_series(self):
        """Grab the Series from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Items?{QUERY}&IncludeItemTypes=Series",
                              headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            return res.json()['TotalRecordCount']
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def get_infos(self):
        """Grab the Info from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/System/Info", headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            return res.json()
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def get_sessions(self):
        """Grab the Sessions from the Jellyfin Endpoint"""
        session = _get_session()
        try:
            res = session.get(f"{self.url}/Sessions?activeWithinSeconds={self.within}",
                              headers=self.header, timeout=10)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            UP.labels(self.alias, "jellyfin").set(1)
            return res.json()
        except requests.exceptions.RequestException as e:
            UP.labels(self.alias, "jellyfin").set(0)
            self.logger.debug(f"Request failed: {e}")
            return None

    def update_sessions(self, sessions):
        """Update the Sessions for the Jellyfin Service"""
        jellyfin_metrics.SESSIONS_T.labels(self.alias).set(len(sessions))
        if self.detailed:
            for session in sessions:
                user_id = session['UserId']
                user_name = session['UserName']
                jellyfin_metrics.SESSIONS.labels(self.alias, user_id, user_name).set(1)

    def _update_session_stream_metrics(self, session, now_playing):
        """Update the per-stream Gauges for a single session."""
        play_state = session.get('PlayState', {})
        method = play_state.get('PlayMethod', 'DirectPlay')
        is_transcoding = 1 if method == 'Transcode' else 0

        label_values = (
            self.alias,
            session.get('UserName', 'unknown'),
            session.get('DeviceName', 'unknown'),
            session.get('Client', 'unknown'),
            now_playing.get('Type', 'Unknown'),
            method,
        )
        values = {
            jellyfin_metrics.SESSION_POSITION: play_state.get('PositionTicks', 0) / 10_000_000,
            jellyfin_metrics.SESSION_DURATION: now_playing.get('RunTimeTicks', 0) / 10_000_000,
            jellyfin_metrics.SESSION_TRANSCODING: is_transcoding,
            jellyfin_metrics.SESSION_PAUSED: 1 if play_state.get('IsPaused', False) else 0,
            jellyfin_metrics.SESSION_BITRATE: (
                session.get('TranscodingInfo', {}).get('Bitrate', 0) if is_transcoding else 0
            ),
        }
        for gauge, value in values.items():
            gauge.labels(*label_values).set(value)

    def update_session_details(self, sessions):
        """Update per-session stream metrics and client info."""
        if not self.session_details:
            return

        for session in sessions:
            now_playing = session.get('NowPlayingItem')
            if not now_playing:
                continue

            self._update_session_stream_metrics(session, now_playing)

            if self.client_info:
                jellyfin_metrics.SESSION_CLIENT_INFO.labels(
                    self.alias,
                    session.get('UserName', 'unknown'),
                    session.get('DeviceName', 'unknown'),
                    session.get('Client', 'unknown'),
                    session.get('ApplicationVersion', 'unknown'),
                ).set(1)

    def scrape(self):
        """Scrape the Jellyfin Service"""
        initial_time = time.time()


        self.get_header()

        n_devices = self.get_number_of_devices()
        n_user = self.get_number_of_user()
        n_movies = self.get_number_of_movies()
        n_series = self.get_number_of_series()
        genres = self.get_genres()
        sessions = self.get_sessions()
        infos = self.get_infos()

        end_time = time.time()
        jellyfin_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        jellyfin_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        if any(x is None for x in (n_devices, n_user,
                                   n_movies, n_series,
                                   genres, sessions,
                                   infos,)):
            return None

        return{
            "n_devices": n_devices,
            "n_user": n_user,
            "n_movies": n_movies,
            "n_series": n_series,
            "genres": genres,
            "sessions": sessions,
            "infos": infos,
        }

    def update_metrics(self, data):
        """Update the Metrics for the Jellyfin Service"""
        jellyfin_metrics.NUMBER_OF_DEVICES.labels(self.alias).set(data["n_devices"])
        jellyfin_metrics.NUMBER_OF_USERS.labels(self.alias).set(data["n_user"])
        jellyfin_metrics.NUMBER_OF_MOVIES.labels(self.alias).set(data["n_movies"])
        jellyfin_metrics.NUMBER_OF_SERIES.labels(self.alias).set(data["n_series"])
        jellyfin_metrics.VERSION.labels(self.alias, data["infos"]["Version"]).set(1)
        (jellyfin_metrics.HAS_UPDATE.labels(self.alias)
         .set(1 if data["infos"]["HasUpdateAvailable"] else 0))

        util.total_with_label(
            [
                data["genres"],
                None,
                jellyfin_metrics.GENRES
            ],
            self.alias)
        self.update_sessions(data["sessions"])
        self.update_session_details(data["sessions"])
