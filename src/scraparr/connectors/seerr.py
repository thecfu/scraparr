"""Module to handle the Metrics of the Seerr Services"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor
from dateutil.parser import parse

from scraparr.connectors.util import get
from scraparr.metrics.general import UP


def _fetch_all_titles(requests_list, api_url, api_key, max_workers=10):
    """
    Fetch titles for all requests in parallel using ThreadPoolExecutor.

    Args:
        requests_list: List of request/issue dictionaries containing media info
        api_url: Base API URL (e.g., "http://seerr:5055/api/v1")
        api_key: API key for authentication
        max_workers: Maximum number of concurrent API calls (default 10)

    Returns:
        Dict mapping request_id -> (title, seasons)
    """
    def get_media_id(req):
        """Extract media ID from request, trying tmdbId, imdbId, tvdbId in order."""
        media = req.get("media", {})
        return media.get("tmdbId") or media.get("imdbId") or media.get("tvdbId") or 0

    def fetch_title(req):
        req_id = req.get("id")
        media_id = get_media_id(req)
        req_type = req.get("type") or req.get("media", {}).get("mediaType")

        try:
            if req_type == "movie":
                media = get(f"{api_url}/movie/{media_id}", api_key)
                title = media.get("title", media_id) if media else media_id
                seasons = 0
            else:
                media = get(f"{api_url}/tv/{media_id}", api_key)
                title = media.get("title", media_id) if media else media_id
                seasons = req.get("seasonCount", 0)
            return req_id, (title, seasons)
        except Exception as e:
            logging.warning("Failed to fetch title for request %s: %s", req_id, e)
            return req_id, (str(media_id), 0)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(fetch_title, requests_list)
        return dict(results)

class GetSeerr:
    """Class to handle the Metrics for jellyseerr and Overseerr"""

    def __init__(self, config, metrics):
        self.api_url = f"{config['url']}/api/{config['api_version']}"
        self.api_key = config['api_key']
        self.alias = config['alias']
        self.service = config.get('service', 'seerr')
        self.metrics = metrics

    def get_users(self):
        """Grab Users from the Seerr Endpoint"""

        alias = self.alias
        service = self.service

        users = []

        initial_time = time.time()
        res = self.fetch_paginated_results("user")
        end_time = time.time()

        if not res or "results" not in res:
            UP.labels(alias, service).set(0)
            return []

        UP.labels(alias, service).set(1)
        self.metrics.LAST_SCRAPE.labels(alias).set(end_time)
        self.metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

        for res_user in res["results"]:
            user = {"username": res_user["displayName"],
                    "requests": res_user["requestCount"]}
            users.append(user)

        return users

    def get_requests(self):
        """Grab Requests from the Seerr Endpoint"""

        alias, service = self.alias, self.service
        requests = []

        initial_time = time.time()
        res = self.fetch_paginated_results("request")
        end_time = time.time()

        if not res or "results" not in res:
            UP.labels(alias, service).set(0)
            return []
        if len(res["results"]) == 0:
            UP.labels(alias, service).set(1)
            self.metrics.LAST_SCRAPE.labels(alias).set(end_time)
            self.metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
            return [{}]  # Return a single empty dict to indicate a successful scrape

        self.metrics.LAST_SCRAPE.labels(alias).set(end_time)
        self.metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

        # Fetch all titles in parallel
        titles = _fetch_all_titles(res["results"], self.api_url, self.api_key)

        # Process the Requests
        for res_request in res["results"]:
            title, seasons = titles.get(res_request["id"], ("Unknown", 0))
            request = {
                "requested": parse(res_request["createdAt"]).timestamp(),
                "type": res_request["type"],
                "status": self.map_status(res_request),
                "title": title,
            }
            if seasons > 0:
                request["seasons"] = seasons

            requests.append(request)

        return requests

    @staticmethod
    def map_status(res_request):
        """Map the request status to a readable format"""

        status_map = {
            1: "Pending",
            3: "Declined",
            4: "Failed",
        }
        if res_request["status"] in status_map:
            return status_map[res_request["status"]]

        if res_request["status"] == 2:
            media_status = res_request["media"].get("status", 0)
            return {
                2: "Pending",
                3: "Processing",
                4: "Partially",
                5: "Available",
                6: "Blacklisted",
            }.get(media_status, "Unknown")

        return "Unknown"

    def get_issues(self):
        """Grab Issues from the Seerr Endpoint"""

        alias, service = self.alias, self.service
        issues = []

        initial_time = time.time()
        res = self.fetch_paginated_results("issue")
        end_time = time.time()

        if not res or "results" not in res:
            UP.labels(alias, service).set(0)
            return []
        if len(res["results"]) == 0:
            UP.labels(alias, service).set(1)
            self.metrics.LAST_SCRAPE.labels(alias).set(end_time)
            self.metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
            return [{}] # Return a single empty dict to indicate a successful scrape

        UP.labels(alias, service).set(1)
        self.metrics.LAST_SCRAPE.labels(alias).set(end_time)
        self.metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

        # Fetch all titles in parallel
        titles = _fetch_all_titles(res["results"], self.api_url, self.api_key)

        for res_issue in res["results"]:
            title, _ = titles.get(res_issue["id"], ("Unknown", 0))
            issue = {
                "created": parse(res_issue["createdAt"]).timestamp(),
                "updated": parse(res_issue["updatedAt"]).timestamp(),
                "status": self.map_issue_status(res_issue["status"]),
                "type": self.map_issue_type(res_issue["issueType"]),
                "mediaType": res_issue["media"]["mediaType"],
                "title": title,
            }
            issues.append(issue)

        return issues

    def fetch_paginated_results(self, endpoint):
        """Handles API pagination for endpoints like 'issue' or 'request'"""
        res = get(f"{self.api_url}/{endpoint}?take=20", self.api_key)
        if not res or "pageInfo" not in res:
            return {}

        total_pages = res["pageInfo"].get("pages", 1)
        for page in range(2, total_pages + 1):
            skip = 20 * page
            more = get(f"{self.api_url}/{endpoint}?take=20&skip={skip}", self.api_key)
            if not more or "results" not in more:
                logging.error("Failed to get more %ss, but expected more for %s",
                              endpoint, self.alias)
                return {}
            res["results"].extend(more["results"])

        return res

    @staticmethod
    def map_issue_status(status):
        """Maps issue status codes to readable strings"""
        return {1: "Open", 2: "Closed"}.get(status, "Unknown")

    @staticmethod
    def map_issue_type(issue_type):
        """Maps issue type codes to readable strings"""
        return {
            1: "Video",
            2: "Audio",
            3: "Subtitle",
        }.get(issue_type, "Other")

    def get(self):
        """Function to get all the Data"""

        users = self.get_users()
        requests = self.get_requests()
        issues = self.get_issues()

        return users, requests, issues

class UpdateSeerr:
    """Class to handle the Metrics for jellyseerr and Overseerr"""

    def __init__(self, detailed, alias, metrics):
        self.detailed = detailed
        self.alias = alias
        self.metrics = metrics

    def update_users(self, users):
        """Update the User Metrics"""

        alias = self.alias

        for user in users:
            self.metrics.USER_REQUEST_COUNT.labels(alias, user["username"]).set(user["requests"])

        self.metrics.USER_COUNT.labels(alias).set(len(users))

    def update_requests(self, requests):
        """Update the Request Metrics"""

        alias = self.alias

        request_status = {}
        request_count = {}
        requested_seasons = 0

        for request in requests:
            request_status[request["status"]] = request_status.get(request["status"], 0) + 1
            request_count[request["type"]] = request_count.get(request["type"], 0) + 1
            requested_seasons += request.get("seasons", 0)

            if self.detailed:
                (self.metrics.REQUEST_TIMESTAMP
                 .labels(alias, request["title"])
                 .set(request["requested"]))
                if "seasons" in request and request["seasons"] > 0:
                    (self.metrics.REQUEST_SEASONS
                     .labels(alias, request["title"])
                     .set(request.get("seasons", 0)))

        for status, count in request_status.items():
            self.metrics.REQUEST_STATUS.labels(alias, status).set(count)
        self.metrics.REQUEST_TV.labels(alias).set(request_count.get("tv", 0))
        self.metrics.REQUEST_MOVIE.labels(alias).set(request_count.get("movie", 0))
        self.metrics.REQUEST_COUNT.labels(alias).set(len(requests))
        self.metrics.REQUEST_SEASONS_T.labels(alias).set(requested_seasons)

    def update_issues(self, issues):
        """Update the Issue Metrics"""

        alias = self.alias

        issue_status = {}
        issue_type = {}
        issue_media_type = {}
        issue_and_media_type = {}
        issue_title = {}

        for issue in issues:
            issue_status[issue["status"]] = issue_status.get(issue["status"], 0) + 1
            issue_type[issue["type"]] = issue_type.get(issue["type"], 0) + 1
            issue_media_type[issue["mediaType"]] = issue_media_type.get(issue["mediaType"], 0) + 1
            key = (issue["type"], issue["mediaType"])
            issue_and_media_type[key] = issue_and_media_type.get(key, 0) + 1

            if self.detailed:
                issue_title[issue["title"]] = issue_title.get(issue["title"], 0) + 1
                self.metrics.ISSUE_CREATED.labels(alias, issue["title"]).set(issue["created"])
                self.metrics.ISSUE_UPDATED.labels(alias, issue["title"]).set(issue["updated"])

        for status, count in issue_status.items():
            self.metrics.ISSUE_STATUS.labels(alias, status).set(count)
        for issue_type, count in issue_type.items():
            self.metrics.ISSUE_TYPE.labels(alias, issue_type).set(count)
        for media_type, count in issue_media_type.items():
            self.metrics.ISSUE_MEDIA_TYPE.labels(alias, media_type).set(count)
        for (issue_type, media_type), count in issue_and_media_type.items():
            self.metrics.ISSUE_AND_MEDIA_TYPE.labels(alias, issue_type, media_type).set(count)
        for title, count in issue_title.items():
            self.metrics.ISSUE_TITLE.labels(alias, title).set(count)

        self.metrics.ISSUE_COUNT.labels(alias).set(len(issues))

    def update(self, data):
        """Update the Metrics for the Seerr Services"""

        users = data["users"]
        requests = data["requests"]
        issues = data["issues"]

        self.update_users(users)
        if requests[0] != {}:
            self.update_requests(requests)
        else:
            self.metrics.REQUEST_COUNT.labels(self.alias).set(0)
        if issues[0] != {}:
            self.update_issues(issues)
        else:
            self.metrics.ISSUE_COUNT.labels(self.alias).set(0)
