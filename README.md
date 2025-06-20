# <img src="/.github/assets/logos/scraparr_logo.svg" alt="scraparr-logo" width="20%"> <img src="/.github/assets/logos/scraparr_only-text.png" alt="Scraparr" width="30%"> 
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
`docker run -v ./config.yaml:/scraparr/config/config.yaml -p 7100:7100 ghcr.io/thecfu/scraparr`

Docker Hub:
`docker run -v ./config.yaml:/scraparr/config/config.yaml -p 7100:7100 thegameprofi/scraparr`

> [!NOTE]  
> If your using any v1 Version check the Readme of the [v1 Branch](https://github.com/thecfu/scraparr/tree/v1#readme)

> [!NOTE]  
> If you want to access new features before they are released, use the `main` tag.
> 

### Kubernetes (Community-Maintained)

Deployment on Kubernetes is possible via the [imgios/scraparr](https://github.com/imgios/scraparr) Helm Chart, which simplifies the process into two steps:

1. Add the imgios/scraparr Helm Repository:

```shell
$ helm repo add imgios https://imgios.github.io/scraparr
```

2. Run the installation command:

```shell
$ helm install <release-name> imgios/scraparr \
--namespace scraparr \
--create-namespace \
--values values.yaml
```

See the [Helm Chart repository README](https://github.com/imgios/scraparr) for details on deployment and how to fill the values.

### Unraid Template (Community-Maintained)

A Unraid Template is available in the Repo of jordan-dalby: https://github.com/jordan-dalby/unraidtemplates <br />
> Note: This template is approved by TheCfU but is not monitored or maintained by us.

## Configuration

> [!NOTE]  
> If your using any v1 Version check the Readme of the [v1 Branch](https://github.com/thecfu/scraparr/tree/v1#readme)

> [!WARNING]  
> If using the Docker Variant you need to use the IP or configure & use the extra_host `host.docker.internal:host-gateway`

Scraparr can be configured either by using a [config.yaml](config.yaml) file or by setting environment variables.  
For environment variables, please refer to the [sample.env](sample.env) file. You can set them directly as environment options or create an `.env` file and import it using your container host.

> [!IMPORTANT]
> The environment variables don't support the configuration of Multiple Instances to use them you need to switch to the config

Make sure the configuration specifies the URLs and API keys for the *arr services you want to monitor.

### Config.yaml

Template for Service inside the config.yaml:

```yaml
sonarr:
  url: http://sonarr:8989
  api_key: key
  # alias: sonarr # Optional to Differentiate between multiple Services
  # api_version: v3 # Optional to use a different API Version
  # interval: 30 # Optional to set a different Interval in Seconds
  # detailed: true  # Get Data per Series
```

#### Multiple Instances

To Configure multiple Instances of the same Service you can configure them like this:

> [!CAUTION]  
> When using multiple Instances of the same Service you need to use the alias, else the metrics are getting overwritten

```yaml
sonarr:
  - url: http://sonarr:8989
    api_key: key
    alias: sonarr1
  - url: http://sonarr2:8989
    api_key: key
    alias: sonarr2
```

## Usage

Once the service is running, it will expose metrics at http://localhost:7100/metrics (default port). You can configure Prometheus to scrape these metrics by adding the following job to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'scraparr'
    static_configs:
      - targets: ['localhost:7100']
```

### Grafana Dashboards

The Main Dashboard is also available under Grafana Dashboards: [Scraparr](https://grafana.com/grafana/dashboards/22934)

For example Grafana Dashboards have a look at [Dashboards](dashboards)

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request. Make sure to follow the contribution guidelines

> [!IMPORTANT]
> Please fork from the `dev` branch to include any un-released changes.

## 🚀 Stay Connected
* [Discord](https://discord.gg/z54hWyGcam)

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
