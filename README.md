# <img src="https://scraparr.thecfu.de/scraparr_logo.svg" alt="scraparr-logo" width="20%"> <img src="https://scraparr.thecfu.de/scraparr_only-text.png" alt="Scraparr" width="30%"> 
### A Exporter for the *arr Suite

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)]()<br>

---

## Overview

Scraparr is a Prometheus exporter for the *arr Suite. It can call the API's of multiple Services and translate it into Prometheus readable metrics.
Currently supported Services are:
- Radarr
- Sonarr

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/TheCfU/scraparr.git
    cd scraparr
    ```

2. Build the Docker image:
    ```sh
    docker build -t scraparr .
    ```

3. Configure:
    Edit the config.cnf file to your needs. <br />
    Especially the API keys and URL of the Services you want to monitor.

4. Run the Docker container:
    ```sh
    docker run -d -p 7100:7100 -v ./config.cnf:/scraparr/config.cnf scraparr
    ```

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