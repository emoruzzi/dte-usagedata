# DTE Energy Usage Monitor to Influxdb

This is a simple Docker app that pulls data using DTE's usage data and writes it to InfluxDB 2.X.

## Getting Started

To start writing data to InfluxDB, you will need to generate the 'Energy Usage Data' link. Visit [DTE's customer data privacy policy page](https://www.dteenergy.com/us/en/quicklinks/customer-data-privacy-policy.html) to find out more about how to do this.

Once you have generated the link, configure either `environment variables` or the `config.ini` with the appropriate values for dte uuid and InfluxDB (v2).

## Usage

Once the config is set, you can run the Docker container using a scheduler such as `crontab`. The scheduler should run the container at the desired frequency, for example every 12 hours.

## Configuration

If using environment variablesz, the following can be set in order for the container to connect to InfluxDB:

- `DTE_UUID`: the UUID generated via DTE for your energy usage data
- `INFLUXDB_URL`: the URL of the InfluxDB instance
- `INFLUXDB_TOKEN`: a valid InfluxDB token
- `INFLUXDB_ORG`: the name of the InfluxDB organization
- `INFLUXDB_BUCKET`: the name of the InfluxDB bucket to write data to
- `INFLUX_MEASUREMENT`: the name of the InfluxDB measurement to write data to

Otherwise, fill out the template in config.ini.

## Example crontab configuration

Here is an example `crontab` configuration that runs the container every 12 hours:
```
0 */12 * * * docker run dte
```