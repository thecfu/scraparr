"""Module to handle the Metrics of the Seerr Services"""

import time
import logging
from dateutil.parser import parse

from scraparr.connectors.module import ConnectorModule
from scraparr.connectors.util import get
from scraparr.metrics.general import UP

class Seerr(ConnectorModule):
    """Class to handle the Metrics for jellyseerr and Overseerr"""

    def __init__(self, config, metrics, service):
        ConnectorModule.__init__(self, config, service)
        self.metrics = metrics
        self.url = f"{config['url']}/api/{config['api_version']}"

    def clear(self):
        """Clear the Metrics for the Service"""
        self.metrics.REQUEST_TIMESTAMP.remove_by_labels({"alias": self.alias})
        self.metrics.REQUEST_SEASONS.remove_by_labels({"alias": self.alias})
        self.metrics.ISSUE_TITLE.remove_by_labels({"alias": self.alias})
        self.metrics.ISSUE_CREATORS.remove_by_labels({"alias": self.alias})
        self.metrics.ISSUE_UPDATES.remove_by_labels({"alias": self.alias})
        self.metrics.ISSUE_TITLE.remove_by_labels({"alias": self.alias})

    def scrape(self):
        """Scrape the Seerr Service"""

        initial_time = time.time()
        users, requests, issues = self.get()
        end_time = time.time()

        self.metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        self.metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        if not users or not requests or not issues:
            logging.error("No Data found for %s %s, assuming Failure", self.service, self.alias)
            return {}

        return {"users": users, "requests": requests, "issues": issues}

    def get_users(self):
        """Grab Users from the Seerr Endpoint"""

        users = []

        res = self.fetch_paginated_results("user")

        if not res or "results" not in res:
            UP.labels(self.alias, self.service).set(0)
            return []

        UP.labels(self.alias, self.service).set(1)

        for res_user in res["results"]:
            user = {"username": res_user["displayName"],
                    "requests": res_user["requestCount"]}
            users.append(user)

        return users

    def get_title(self, req):
        """Grab the Title from the Seerr Endpoint"""

        if req["media"]["tmdbId"]:
            media_id = req["media"]["tmdbId"]
        elif req["media"]["imdbId"]:
            media_id = req["media"]["imdbId"]
        elif req["media"]["tvdbId"]:
            media_id = req["media"]["tvdbId"]
        else:
            media_id = 0

        if req["type"] == "movie":
            media = get(f"{self.url}/movie/{media_id}", self.api_key)
            seasons = 0
            title = media.get("title", media_id)
        else:
            media = get(f"{self.url}/tv/{media_id}", self.api_key)
            seasons = req.get("seasonCount", 0)
            title = media.get("title", media_id)

        return [title, seasons]

    def get_requests(self):
        """Grab Requests from the Seerr Endpoint"""

        requests = []

        res = self.fetch_paginated_results("request")

        if not res or "results" not in res:
            UP.labels(self.alias, self.service).set(0)
            return []
        UP.labels(self.alias, self.service).set(1)
        if len(res["results"]) == 0:
            return [{}]  # Return a single empty dict to indicate a successful scrape

        # Process the Requests
        for res_request in res["results"]:
            request = {
                "requested": parse(res_request["createdAt"]).timestamp(),
                "type": res_request["type"],
                "status": self.map_status(res_request),
            }

            title, seasons = self.get_title(res_request)
            request["title"] = title
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

        issues = []

        res = self.fetch_paginated_results("issue")

        if not res or "results" not in res:
            UP.labels(self.alias, self.service).set(0)
            return []
        UP.labels(self.alias, self.service).set(1)
        if len(res["results"]) == 0:
            return [{}] # Return a single empty dict to indicate a successful scrape

        for res_issue in res["results"]:
            res_issue["type"] = res_issue["media"]["mediaType"]

            issue = {
                "created": parse(res_issue["createdAt"]).timestamp(),
                "updated": parse(res_issue["updatedAt"]).timestamp(),
                "status": self.map_issue_status(res_issue["status"]),
                "type": self.map_issue_type(res_issue["issueType"]),
                "mediaType": res_issue["media"]["mediaType"],
                "title": self.get_title(res_issue)[0],
            }
            issues.append(issue)

        return issues

    def fetch_paginated_results(self, endpoint):
        """Handles API pagination for endpoints like 'issue' or 'request'"""
        res = get(f"{self.url}/{endpoint}?take=20", self.api_key)
        if not res or "pageInfo" not in res:
            return {}

        total_pages = res["pageInfo"].get("pages", 1)
        for page in range(2, total_pages + 1):
            skip = 20 * page
            more = get(f"{self.url}/{endpoint}?take=20&skip={skip}", self.api_key)
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

    def update_users(self, users):
        """Update the User Metrics"""

        alias = self.alias

        for user in users:
            self.metrics.USER_REQUEST_COUNT.labels(alias, user["username"]).set(user["requests"])

        self.metrics.USER_COUNT.labels(alias).set(len(users))

    def update_requests(self, requests):
        """Update the Request Metrics"""

        request_status = {}
        request_count = {}
        requested_seasons = 0

        for request in requests:
            request_status[request["status"]] = request_status.get(request["status"], 0) + 1
            request_count[request["type"]] = request_count.get(request["type"], 0) + 1
            requested_seasons += request.get("seasons", 0)

            if self.detailed:
                (self.metrics.REQUEST_TIMESTAMP
                 .labels(self.alias, request["title"])
                 .set(request["requested"]))
                if "seasons" in request and request["seasons"] > 0:
                    (self.metrics.REQUEST_SEASONS
                     .labels(self.alias, request["title"])
                     .set(request.get("seasons", 0)))

        for status, count in request_status.items():
            self.metrics.REQUEST_STATUS.labels(self.alias, status).set(count)
        self.metrics.REQUEST_TV.labels(self.alias).set(request_count.get("tv", 0))
        self.metrics.REQUEST_MOVIE.labels(self.alias).set(request_count.get("movie", 0))
        self.metrics.REQUEST_COUNT.labels(self.alias).set(len(requests))
        self.metrics.REQUEST_SEASONS_T.labels(self.alias).set(requested_seasons)

    def update_issues(self, issues):
        """Update the Issue Metrics"""

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
                self.metrics.ISSUE_CREATED.labels(self.alias, issue["title"]).set(issue["created"])
                self.metrics.ISSUE_UPDATED.labels(self.alias, issue["title"]).set(issue["updated"])

        for status, count in issue_status.items():
            self.metrics.ISSUE_STATUS.labels(self.alias, status).set(count)
        for issue_type, count in issue_type.items():
            self.metrics.ISSUE_TYPE.labels(self.alias, issue_type).set(count)
        for media_type, count in issue_media_type.items():
            self.metrics.ISSUE_MEDIA_TYPE.labels(self.alias, media_type).set(count)
        for (issue_type, media_type), count in issue_and_media_type.items():
            self.metrics.ISSUE_AND_MEDIA_TYPE.labels(self.alias, issue_type, media_type).set(count)
        for title, count in issue_title.items():
            self.metrics.ISSUE_TITLE.labels(self.alias, title).set(count)

        self.metrics.ISSUE_COUNT.labels(self.alias).set(len(issues))

    def update_metrics(self, data):
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
