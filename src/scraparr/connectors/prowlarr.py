"""
Module to handle the Metrics of the Prowlarr Service
"""

import time
import re
from dateutil.parser import parse

from scraparr.connectors.module import ConnectorModule
from scraparr.connectors.util import get
from scraparr.metrics.general import UP
import scraparr.metrics.prowlarr as prowlarr_metrics

def check_health(health, res):
    """Check the Health of the Indexers"""
    for notification in health:
        if notification['source'] == 'IndexerStatusCheck':
            message = notification['message']
            status_match = re.search(r"Indexers (\w+)", message)
            status = status_match.group(1) if status_match else None

            # Extract the word(s) after the colon
            indexer_match = re.search(r": (.+)", message)
            indexers = indexer_match.group(1).split(', ') if indexer_match else None
            for indexer in res:
                if indexer['name'] in indexers:
                    indexer['status'] = status

class Module(ConnectorModule):
    """Module Class for Prowlarr"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "prowlarr")
        self.url = f"{self.url}/api/{self.api_version}"

    def clear(self):
        """Clear the Metrics of the Prowlarr Service"""
        prowlarr_metrics.VIP_EXPIRATION.remove_by_labels({"alias": self.alias})
        prowlarr_metrics.INDEXER_STATUS.remove_by_labels({"alias": self.alias})
        prowlarr_metrics.INDEXER_ENABLED.remove_by_labels({"alias": self.alias})

    def get_indexers(self):
        """Grab the Indexers from the Prowlarr Endpoint"""

        initial_time = time.time()
        res = get(f"{self.url}/indexer", self.api_key)
        end_time = time.time()

        if res == {}:
            UP.labels(self.alias, 'prowlarr').set(0)
        else:
            UP.labels(self.alias, 'prowlarr').set(1)
            prowlarr_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
            prowlarr_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

            status = get(f"{self.url}/indexerstatus", self.api_key)

            if status == {}:
                UP.labels(self.alias, 'prowlarr').set(0)
                return res

            # Create a dictionary for fast lookup
            stat_dict = {stat['indexerId']: stat for stat in status}

            # Update the status if the id matches
            for indexer in res:
                if indexer['id'] in stat_dict:
                    indexer['status'] = "disabled" if stat_dict[indexer['id']] else None

            health = get(f"{self.url}/health", self.api_key)

            if health == {}:
                UP.labels(self.alias, 'prowlarr').set(0)
                return res

            check_health(health, res)

        return res

    def get_applications(self):
        """Grab the Applications from the Prowlarr Endpoint"""

        res = get(f"{self.url}/applications", self.api_key)

        if res == {}:
            UP.labels(self.alias, 'prowlarr').set(0)
        else:
            UP.labels(self.alias, 'prowlarr').set(1)
        return res

    def update_system_data(self, data):
        """Update the System Data"""

        start_time = parse(data["status"]["startTime"]).timestamp()
        build_time = parse(data["status"]["buildTime"]).timestamp()
        prowlarr_metrics.START_TIME.labels(self.alias).set(start_time)
        prowlarr_metrics.BUILD_TIME.labels(self.alias).set(build_time)

    def analyse_applications(self, applications):
        """Analyse the Applications"""

        prowlarr_metrics.APPLICATION_COUNT.labels(self.alias).set(len(applications))
        enabled_t = 0
        sync_level_count = {}

        for application in applications:
            enabled = 1 if application["enable"] else 0
            enabled_t += enabled
            sync_level = application["syncLevel"]
            if sync_level in sync_level_count:
                sync_level_count[sync_level] += 1
            else:
                sync_level_count[sync_level] = 1

            if self.detailed:
                (prowlarr_metrics.APPLICATION_ENABLED
                 .labels(self.alias, application["name"])
                 .set(enabled))
                (prowlarr_metrics
                    .APPLICATION_SYNC_LEVEL
                    .labels(self.alias, application["name"], sync_level).set(1)
                )

        prowlarr_metrics.APPLICATION_ENABLED_T.labels(self.alias).set(enabled_t)
        for sync_level, count in sync_level_count.items():
            (prowlarr_metrics
                .APPLICATION_SYNC_LEVEL_T
                .labels(self.alias, sync_level).set(count)
            )

    def analyse_indexers(self, indexers):
        """Analyse the Indexers"""

        indexer_count = {
            "total": {
                "total": len(indexers),
                "enabled": 0,
                "private": 0,
                "public": 0,
                "semiPrivate": 0
            },
            "usenet": {"total": 0, "enabled": 0, "private": 0, "public": 0, "semiPrivate": 0},
            "torrent": {"total": 0, "enabled": 0, "private": 0, "public": 0, "semiPrivate": 0}
        }

        for indexer in indexers:
            enabled = 1 if indexer["enable"] else 0
            indexer_count["total"]["enabled"] += enabled
            indexer_count["total"][indexer["privacy"]] += 1

            indexer_count[indexer["protocol"]]["total"] += 1
            indexer_count[indexer["protocol"]]["enabled"] += enabled
            indexer_count[indexer["protocol"]][indexer["privacy"]] += 1

            name = indexer["name"]

            for field in indexer['fields']:
                if field['name'] == 'vipExpiration':
                    vip_expiration = field['value']
                    if vip_expiration:
                        vip_expiration = parse(vip_expiration).timestamp()
                        prowlarr_metrics.VIP_EXPIRATION.labels(self.alias, name).set(vip_expiration)
                    break

            if self.detailed:
                self.logger.debug(
                    f"Processing Indexer: {name} - {indexer['protocol']} - {indexer['privacy']}"
                )
                (prowlarr_metrics.INDEXER_ENABLED
                    .labels(self.alias, indexer["protocol"], name)
                    .set(enabled)
                )
                status = indexer.get("status", "healthy")
                if status == "healthy":
                    prowlarr_metrics.INDEXER_STATUS.labels(self.alias, name, "healthy").set(1)
                    prowlarr_metrics.INDEXER_HEALTHY.labels(self.alias, name).set(1)
                else:
                    prowlarr_metrics.INDEXER_STATUS.labels(self.alias, name, "healthy").set(0)
                    prowlarr_metrics.INDEXER_HEALTHY.labels(self.alias, name).set(0)

        for types, counts in indexer_count.items():
            if types == "total":
                (prowlarr_metrics.INDEXER_COUNT_T.labels(self.alias)
                 .set(counts["total"]))
                (prowlarr_metrics.INDEXER_ENABLED_T.labels(self.alias)
                 .set(counts["enabled"]))
                (prowlarr_metrics.INDEXER_PRIVACY_T.labels(self.alias, "private")
                 .set(counts["private"]))
                (prowlarr_metrics.INDEXER_PRIVACY_T.labels(self.alias, "public")
                 .set(counts["public"]))
                (prowlarr_metrics.INDEXER_PRIVACY_T
                    .labels(self.alias, "semi-private")
                    .set(counts["semiPrivate"])
                )
            else:
                (prowlarr_metrics.INDEXER_COUNT.labels(self.alias, types)
                 .set(counts["total"]))
                (prowlarr_metrics.INDEXER_ENABLED.labels(self.alias, types, "total")
                 .set(counts["enabled"]))
                (prowlarr_metrics.INDEXER_PRIVACY.labels(self.alias, types, "private")
                 .set(counts["private"]))
                (prowlarr_metrics.INDEXER_PRIVACY.labels(self.alias, types, "public")
                 .set(counts["public"]))
                (prowlarr_metrics.INDEXER_PRIVACY
                    .labels(self.alias, types, "semi-private")
                    .set(counts["semiPrivate"])
                )

    def get_indexerstats(self):
        """Grab the Indexerstats from the Prowlarr Endpoint"""

        res = get(f"{self.url}/indexerstats", self.api_key)

        return res

    def get_indexer_grabs(self, data):
        """Get the Grabs for the Indexers"""
        grabs = {}
        try:
            indexers = data.get('indexers', [])
            total_grab_response_time = 0
            indexer_count = 0

            for indexer in indexers:
                indexer_name = indexer.get('indexerName',
                                           f"Indexer_{indexer.get('indexerId', 'Unknown')}")
                grabs[indexer_name] = indexer.get('numberOfGrabs', 0)
                grab_response_time = indexer.get('averageGrabResponseTime', 0)

                self.logger.debug(f"Indexer: {indexer_name}, Grabs: {grabs[indexer_name]}")

                # Einzelne Metriken
                (prowlarr_metrics.GRABS_BY_INDEXER.labels(self.alias, indexer_name)
                 .set(grabs[indexer_name]))
                (prowlarr_metrics.GRAB_RESPONSE_TIME_BY_INDEXER.labels(self.alias, indexer_name)
                 .set(grab_response_time))

                total_grab_response_time += grab_response_time
                indexer_count += 1

        except (KeyError, TypeError) as e:
            self.logger.error("No Grab Data found for Prowlarr, assuming Failure", str(e))
            return {}

        total_grabs = sum(grabs.values())
        avg_grab_response_time = 0
        if indexer_count > 0:
            avg_grab_response_time = total_grab_response_time / indexer_count

        self.logger.debug(f"Total Grabs: {total_grabs}")
        self.logger.debug(f"Average Grab Response Time: {avg_grab_response_time}ms")

        # Total Metriken
        (prowlarr_metrics.GRABS_BY_INDEXER_T.labels(self.alias)
         .set(total_grabs))
        (prowlarr_metrics.GRAB_RESPONSE_TIME_BY_INDEXER_T.labels(self.alias)
         .set(avg_grab_response_time))

        return grabs

    def get_indexer_failed_queries(self, data):
        """Get the Failed Queries for the Indexers"""
        failed_queries = {}
        try:
            indexers = data.get('indexers', [])
            for indexer in indexers:
                indexer_name = indexer.get('indexerName',
                                           f"Indexer_{indexer.get('indexerId', 'Unknown')}")
                failed_queries[indexer_name] = indexer.get('numberOfFailedQueries', 0)
                self.logger.debug(f"Indexer: {indexer_name}, "
                                  f"Failed Queries: {failed_queries[indexer_name]}")

                (prowlarr_metrics.FAILED_QUERIES_BY_INDEXER.labels(self.alias, indexer_name)
                 .set(failed_queries[indexer_name]))

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing indexer failed queries: {e}")
            return {}

        total_failed_queries = sum(failed_queries.values())
        self.logger.debug(f"Total Failed Queries: {total_failed_queries}")

        prowlarr_metrics.FAILED_QUERIES_BY_INDEXER_T.labels(self.alias).set(total_failed_queries)

        return failed_queries

    def get_indexer_queries(self, data):
        """Get the Queries for the Indexers"""
        queries = {}
        try:
            indexers = data.get('indexers', [])
            total_response_time = 0
            indexer_count = 0

            for indexer in indexers:
                indexer_name = indexer.get('indexerName',
                                           f"Indexer_{indexer.get('indexerId', 'Unknown')}")
                queries[indexer_name] = indexer.get('numberOfQueries', 0)
                response_time = indexer.get('averageResponseTime', 0)

                # Per Indexer Metrics
                (prowlarr_metrics.QUERIES_BY_INDEXER.labels(self.alias, indexer_name)
                 .set(queries[indexer_name]))
                (prowlarr_metrics.RESPONSE_TIME_BY_INDEXER.labels(self.alias, indexer_name)
                 .set(response_time))

                total_response_time += response_time
                indexer_count += 1

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing indexer queries: {e}")
            return {}

        total_queries = sum(queries.values())
        avg_response_time = total_response_time / indexer_count if indexer_count > 0 else 0

        self.logger.debug(f"Total Queries: {total_queries}")
        self.logger.debug(f"Average Response Time: {avg_response_time}ms")

        # Total Metrics
        prowlarr_metrics.QUERIES_BY_INDEXER_T.labels(self.alias).set(total_queries)
        prowlarr_metrics.RESPONSE_TIME_BY_INDEXER_T.labels(self.alias).set(avg_response_time)

        return queries

    def get_user_agent_queries(self, data):
        """Get the Queries for the User Agents"""
        queries = {}
        try:
            user_agents = data.get('userAgents', [])
            for user_agent in user_agents:
                user_agent_name = user_agent.get('userAgent', 'Unknown')
                queries[user_agent_name] = user_agent.get('numberOfQueries', 0)
                self.logger.debug(f"User Agent: {user_agent_name}, "
                                  f"Queries: {queries[user_agent_name]}")

                (prowlarr_metrics.QUERIES_BY_USER_AGENT.labels(self.alias, user_agent_name)
                 .set(queries[user_agent_name]))

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing user agent queries: {e}")
            return {}

        total_queries = sum(queries.values())
        self.logger.debug(f"Total User Agent Queries: {total_queries}")

        prowlarr_metrics.QUERIES_BY_USER_AGENT_T.labels(self.alias).set(total_queries)

        return queries

    def get_user_agent_grabs(self, data):
        """Get the Grabs for the User Agents"""
        grabs = {}
        try:
            user_agents = data.get('userAgents', [])
            for user_agent in user_agents:
                user_agent_name = user_agent.get('userAgent', 'Unknown')
                grabs[user_agent_name] = user_agent.get('numberOfGrabs', 0)
                self.logger.debug(f"User Agent: {user_agent_name}, Grabs: {grabs[user_agent_name]}")

                (prowlarr_metrics.GRABS_BY_USER_AGENT.labels(self.alias, user_agent_name)
                 .set(grabs[user_agent_name]))

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing user agent grabs: {e}")
            return {}

        total_grabs = sum(grabs.values())
        self.logger.debug(f"Total User Agent Grabs: {total_grabs}")

        prowlarr_metrics.GRABS_BY_USER_AGENT_T.labels(self.alias).set(total_grabs)

        return grabs

    def get_host_queries(self, data):
        """Get the Queries for the Hosts"""
        queries = {}
        try:
            hosts = data.get('hosts', [])
            for host in hosts:
                host_name = host.get('host', 'Unknown')
                queries[host_name] = host.get('numberOfQueries', 0)
                self.logger.debug(f"Host: {host_name}, Queries: {queries[host_name]}")

                (prowlarr_metrics.QUERIES_BY_HOST.labels(self.alias, host_name)
                 .set(queries[host_name]))

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing host queries: {e}")
            return {}

        total_queries = sum(queries.values())
        self.logger.debug(f"Total Host Queries: {total_queries}")

        prowlarr_metrics.QUERIES_BY_HOST_T.labels(self.alias).set(total_queries)

        return queries

    def get_host_grabs(self, data):
        """Get the Grabs for the Hosts"""
        grabs = {}
        try:
            hosts = data.get('hosts', [])
            for host in hosts:
                host_name = host.get('host', 'Unknown')
                grabs[host_name] = host.get('numberOfGrabs', 0)
                self.logger.debug(f"Host: {host_name}, Grabs: {grabs[host_name]}")

                prowlarr_metrics.GRABS_BY_HOST.labels(self.alias, host_name).set(grabs[host_name])

        except (KeyError, TypeError) as e:
            self.logger.error(f"Error processing host grabs: {e}")
            return {}

        total_grabs = sum(grabs.values())
        self.logger.debug(f"Total Host Grabs: {total_grabs}")

        prowlarr_metrics.GRABS_BY_HOST_T.labels(self.alias).set(total_grabs)

        return grabs

    def scrape(self):
        """Scrape the Prowlarr Service"""

        system = get(f"{self.url}/system/status", self.api_key)
        data = {
           'indexer': self.get_indexers(),
           'applications': self.get_applications(),
           'indexerstats': self.get_indexerstats()
        }

        if data['indexer'] == {} or data['applications'] == {} or system == {}:
            return {}

        return {"data": data, "system": { "status": system}}

    def update_metrics(self, data):
        """Update the Metrics for the Prowlarr Service"""

        self.update_system_data(data["system"])
        self.analyse_indexers(data["data"]['indexer'])
        self.analyse_applications(data["data"]['applications'])
        self.get_indexer_grabs(data["data"]['indexerstats'])
        self.get_indexer_failed_queries(data["data"]['indexerstats'])
        self.get_indexer_queries(data["data"]['indexerstats'])
        self.get_user_agent_queries(data["data"]['indexerstats'])
        self.get_user_agent_grabs(data["data"]['indexerstats'])
        self.get_host_grabs(data["data"]['indexerstats'])
        self.get_host_queries(data["data"]['indexerstats'])
