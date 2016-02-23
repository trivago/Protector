#!/usr/bin/env bash

# Here is how you would send and receive some sample data to the database:
# ========================================================================

# Add sample data
# curl -X POST -d '[{"name":"my.awesome.series.foo","columns":["val"],"points":[[23]]}]' 'http://influxdb:8086/db/metrics/series?u=root&p=root'
# Query the same data for testing
# curl -G 'http://influxdb:8086/db/metrics/series?u=root&p=root' --data-urlencode "q=select * from my.awesome.series.foo"

# Start protector
protector -c config.yaml --foreground
