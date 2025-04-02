# DTE Energy Usage Monitor to InfluxDB

[![Docker Build and Publish](https://github.com/0daft/dte-usagedata/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/0daft/dte-usagedata/actions/workflows/docker-publish.yml)

Docker container that fetches DTE Energy usage data and stores it in InfluxDB for visualization.

## Prerequisites

- Docker
- InfluxDB 2.x
- DTE Energy account with access to usage data

## Setup

1. Log in to your DTE Energy account
2. Generate an 'Energy Usage Data' link from [DTE's privacy policy page](https://www.dteenergy.com/us/en/quicklinks/customer-data-privacy-policy.html)
3. Extract the UUID from the link (format: `1234ABCD-5678-EFGH-IJKL-90ABCDEF1234`)

## Quick Start

```bash
# Run once
docker run -e DTE_UUID=your-uuid-here \
  -e INFLUXDB_URL=http://yourdb:8086 \
  -e INFLUXDB_TOKEN=your-token \
  -e INFLUXDB_ORG=your-org \
  -e INFLUXDB_BUCKET=your-bucket \
  0daft/dte-usagedata:latest

# Run on schedule (every 12 hours)
docker run -d --restart unless-stopped \
  -e DTE_UUID=your-uuid-here \
  -e INFLUXDB_URL=http://yourdb:8086 \
  -e INFLUXDB_TOKEN=your-token \
  -e INFLUXDB_ORG=your-org \
  -e INFLUXDB_BUCKET=your-bucket \
  -e INTERVAL=43200 \
  0daft/dte-usagedata:latest
```

## Docker Compose

A sample `docker-compose.yml` is included in the repository. To use it:

1. Edit the environment variables in the file
2. Run with `docker-compose up -d`

## Configuration Options

### Environment Variables (Recommended)

**DTE Settings:**
- `DTE_UUID`: Your DTE Energy UUID (**required**)

**InfluxDB Settings:**
- `INFLUXDB_URL`: InfluxDB URL (**required**)
- `INFLUXDB_TOKEN`: InfluxDB access token (**required**)
- `INFLUXDB_ORG`: InfluxDB organization (**required**)
- `INFLUXDB_BUCKET`: InfluxDB bucket (**required**)
- `INFLUXDB_MEASUREMENT`: Measurement name (default: "dte")

**Schedule Settings:**
- `INTERVAL`: Time in seconds between runs (default: 0)
  - `0`: Run once and exit
  - `43200`: Run every 12 hours
  - `86400`: Run every 24 hours

> Note: Both `INFLUXDB_` and `INFLUX_` prefixes are supported.

### Configuration File

Alternatively, create a `config.ini` file:

```ini
[dte]
uuid = "your-dte-uuid"

[influx]
measurement = "dte"
bucket = "your-bucket"
org = "your-org"
url = "http://influxdb:8086"
token = "your-token"
```

Mount it with Docker:
```bash
docker run -v /path/to/config.ini:/app/config.ini 0daft/dte-usagedata
```

## Data Structure

- **Measurement**: "dte" (configurable)
- **Tags**: `account=your-uuid`
- **Fields**: `watt=power_usage_value`
- **Timestamp**: time of reading

## Troubleshooting

- **InfluxDB connection issues**: Verify URL, token, org, and bucket
- **DTE data access problems**: Check UUID accuracy and access expiration
- **Missing data**: DTE may delay data by 24-48 hours

## Security Notes

- Keep your DTE UUID and InfluxDB token secure
- Use environment variables instead of hardcoding credentials
