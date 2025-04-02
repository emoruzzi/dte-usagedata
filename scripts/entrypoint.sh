#!/bin/bash
set -e

if [ ! -f /app/config.ini ]; then
  echo "No config.ini found, using template..."
  cp /app/config.ini.template /app/config.ini
fi

# Function to run the data collector
run_collector() {
  echo "Starting DTE Usage Data collector at $(date)..."

  if [ -n "$DTE_UUID" ]; then
    echo "Using DTE_UUID from environment variable"
  else
    echo "Using DTE_UUID from config.ini"
  fi

  if [ -n "$INFLUXDB_URL" ] || [ -n "$INFLUX_URL" ]; then
    echo "Using InfluxDB connection settings from environment variables"
  else
    echo "Using InfluxDB connection settings from config.ini"
  fi

  python /app/app.py

  echo "Data collection completed at $(date)"
}

# Check if INTERVAL is set (in seconds)
if [ -n "$INTERVAL" ] && [ "$INTERVAL" -gt 0 ]; then
  echo "Running in scheduled mode with ${INTERVAL} seconds interval"

  while true; do
    run_collector
    echo "Sleeping for ${INTERVAL} seconds until next run..."
    sleep ${INTERVAL}
  done
else
  echo "Running once"
  run_collector
fi
