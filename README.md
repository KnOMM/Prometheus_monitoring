# Prometheus monitoring

## Preparation
### docker-compose.yml
It can be any name, but best practice is *docker-compose.yml* file
```commandLine
vim docker-compose.yml
```
The content of the file:
```commandLine
version: '3.8'

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data: {}

services:
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - 9100:9100
    networks:
      - monitoring

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - 9090:9090
    networks:
      - monitoring
```
It's our initial configuration for docker containers
### prometheus.yml
It's our config file for prometheus that was mentioned in docker-compose.yml
```commandLine
vim prometheus.yml
```
Basic config for Prometheus:
```commandLine
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 1m
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```
### Run with docker
```
docker compose up -d
```
### Check
Depends on the setup
if you use your local machine simple curl to localhost will suffice:
```
curl localhost:9100/metrics
```
## Queries
Memory:
```
((1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100)
```
CPU:
```
100 - avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100
```
Disk:
```
100 - ((node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} * 100) / node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"})
```
Load:
```
node_load1 
```
Network:
```
irate(node_network_transmit_bytes_total{device="eth0"}[5m])*8
irate(node_network_receive_bytes_total{device="eth0"}[5m])*8
```
## Adding Grafana
Update docker-compose.yml
Add to the end:
```
grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - 3000:3000
    networks:
      - monitoring
```
update a volume section so it is like that:
```
volumes:
  prometheus_data: {}
  grafana_data: {}
  ```
> **_NOTE:_**  Indentation matters - it's yml

### Run with docker
```
docker compose up -d
```
### Check
Go to *localhost:3000/login* to see Grafana login page.
Credentials: ***admin/admin***

## Export NGINX metrics
Ensure the nginx is installed
```
sudo apt install nginx
```

### Add settings to create metrics endpoint
file to create: */etc/nginx/conf.d/status.conf*

```
server {
listen 8081;

    server_name _;

    location /metrics {
        stub_status on;
    }
}
```
Don't forget to restart the service:
```
sudo systemctl restart nginx.service
```
Possible output:
```
Active connections: 1
server accepts handled requests
3 3 3
Reading: 0 Writing: 1 Waiting: 0 
```
### Stop prometheus container
We need to update prometheus config, but before
```
sudo docker stop prometheus
```
Update *prometheus.yml* file
```
- job_name: 'nginx exporter'
    scrape_interval: 5s
    static_configs:
      - targets: ['nginx_exporter:9113']
```
###  Add NGINX exporter
Add to the end of the *docker-compose.yml*
```
  nginx_exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: nginx_exporter
    command:
      - '-nginx.scrape-uri=http://192.168.180.X:8081/metrics'
    ports:
      - 9113:9113
    networks:
      - monitoring
```

Start the stack again
```
docker compose up -d
```
