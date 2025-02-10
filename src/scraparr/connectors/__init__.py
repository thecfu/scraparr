import hashlib
import json
import logging
import concurrent.futures
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Connectors:
    def __init__(self):
        self.connectors = {}
        self.last_scrape = {}

    def add_connector(self, service, config):
        importer = self.load_connector(service)

        if importer:
            self.connectors[service] = {}
            self.connectors[service]["function"] = importer
            self.connectors[service]["config"] = config
            self.last_scrape[service] = None
        else:
            logging.error("Couldn't import Connector")

    def load_connector(self, service):
        try:
            return __import__(f"scraparr.connectors.{service}", fromlist=[service])
        except ImportError:
            logging.error("No connector found for %s", service)
            return None

    def get_hash(self, data):
        return hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()

    def scrape_service(self, service):
        config = self.connectors[service]["config"]
        scrape_data = {"data": self.connectors[service]["function"].scrape(config),
                       "system": self.get_system_data(service)}
        if scrape_data["data"] is not None and scrape_data["system"] is not None:
            new_hash = self.get_hash(scrape_data)
            if new_hash != self.last_scrape[service]:
                self.last_scrape[service] = new_hash
                self.connectors[service]["function"].update_metrics(scrape_data, config.get('detailed'))
                logging.info("%s metrics updated", service)
            else:
                logging.info("No changes detected in %s", service)
        else:
            logging.warning("% scrape failed", service)

    def get_system_data(self, service):
        def get(api_url):
            try:
                r = requests.get(api_url, headers={"X-Api-Key": api_key}, timeout=20)
                if r.status_code == 200:
                    return r.json()

                logging.error("Error: %s", r.status_code)
            except requests.exceptions.RequestException as e:
                logging.error("Error: %s", e)
            return None

        def root_folder():
            data = get(f"{url}/api/v3/rootfolder")
            if data:
                diskspace_data = get(f"{url}/api/v3/diskspace")
                if diskspace_data:
                    report = []
                    for disk in diskspace_data:
                        if any(disk["path"] == d["path"] for d in data):
                            report.append(disk)
                    return report
            return None

        def queue():
            return get(f"{url}/api/v3/queue/status")

        def status():
            return get(f"{url}/api/v3/system/status")

        url = self.connectors[service]["config"].get('url')
        api_key = self.connectors[service]["config"].get('api_key')
        return {'root_folder': root_folder(), 'queue': queue(), 'status': status()}

    def scrape(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.scrape_service, service): service for service in self.connectors}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error("Scrape failed for %s: %s", futures[future], e)
