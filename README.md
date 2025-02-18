# <img src="https://scraparr.thecfu.de/scraparr_logo.svg" alt="scraparr-logo" width="20%"> <img src="https://scraparr.thecfu.de/scraparr_only-text.png" alt="Scraparr" width="30%"> 
### A Exporter for the *arr Suite

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)]() [![Pylint](https://github.com/TheCfU/scraparr/actions/workflows/pylint.yml/badge.svg)](https://github.com/TheCfU/scraparr/actions/workflows/pylint.yml)<br>

---

Scraparr is a Prometheus exporter for the *arr suite (Sonarr, Radarr, Lidarr, etc.). It provides metrics that can be scraped by Prometheus to monitor and visualize the health and performance of your *arr applications.

## Features

- Exposes detailed *arr metrics
- Easy integration with Prometheus
- Lightweight and efficient
- Built for extensibility

## Installation

### Local Setup
1. Clone this repository:
```sh
git clone https://github.com/thecfu/scraparr.git
cd scraparr/src
```
2. Install dependencies:
```sh
pip install -r scraparr/requirements.txt
```

3. Run the exporter:
```sh
python -m scraparr.scraparr
```

### Docker Setup

You can either Clone the Repo and build the Docker Image locally or you can use the Image published in the Github Registry
You can also check the [Docker-Compose](compose.yaml).

Github Registry:
`docker run -v ./config.cnf:/scraparr/config.cnf -p 7100:7100 ghcr.io/thecfu/scraparr`

## Configuration

Scraparr needs's to be configured using a [config.cnf](config.cnf) file. Ensure the configuration specifies the URLs, API Version and API keys for the *arr services you want to monitor.

Template for Service inside the config.cnf:

```cnf
[SONARR]
url = http://localhost:8989
api_key = YOUR_KEY
api_version = v3
detailed = true
```

> [!NOTE]  
> If using the Docker Variant you need to use the IP or configure & use the extra_host `host.docker.internal:host-gateway`

## Usage

Once the service is running, it will expose metrics at http://localhost:7100/metrics (default port). You can configure Prometheus to scrape these metrics by adding the following job to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'scraparr'
    static_configs:
      - targets: ['localhost:7100']
```

### Grafana Dashboards

For example Grafana Dashboards have a look at [Dashboards](dashboards)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request. Make sure to follow the contribution guidelines.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

---
```
___________.__           _________   _____ ____ ___ 
\__    ___/|  |__   ____ \_   ___ \_/ ____\    |   \
  |    |   |  |  \_/ __ \/    \  \/\   __\|    |   /
  |    |   |   Y  \  ___/\     \____|  |  |    |  / 
  |____|   |___|  /\___  >\______  /|__|  |______/  
                \/     \/        \/                 
```
