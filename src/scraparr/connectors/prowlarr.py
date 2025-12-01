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


    def scrape(self):
        """Scrape the Prowlarr Service"""

        data = {
            'indexer': self.get_indexers(),
            'applications': self.get_applications()
        }

        system = get(f"{self.url}/system/status", self.api_key)

        if data['indexer'] == {} or data['applications'] == {} or system == {}:
            return {}

        return {"data": data, "system": { "status": system}}

    def update_metrics(self, data):
        """Update the Metrics for the Prowlarr Service"""

        self.update_system_data(data["system"])
        self.analyse_indexers(data["data"]['indexer'])
        self.analyse_applications(data["data"]['applications'])
