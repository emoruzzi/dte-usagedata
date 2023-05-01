#!/usr/bin/env python
"""
DISCLAIMER:

This code is provided as is without warranty of any kind, either express or implied.
The authors shall not be held liable for any damages arising from the use of this code.

USE AT YOUR OWN RISK.

"""

import os
import datetime
import requests
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import xmltodict
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

# Get config variables
account = config.get('dte', 'uuid') if config.get('dte', 'uuid') else os.environ.get('DTE_UUID')
measurement = config.get('influx', 'measurement') if config.get('influx', 'measurement') else os.environ.get('INFLUX_MEASUREMENT')
bucket = config.get('influx', 'bucket') if config.get('influx', 'bucket') else os.environ.get('INFLUX_BUCKET')
org = config.get('influx', 'org') if config.get('influx', 'org') else os.environ.get('INFLUX_ORG')
token = config.get('influx', 'token') if config.get('influx', 'token') else os.environ.get('INFLUX_TOKEN')
url = config.get('influx', 'url') if config.get('influx', 'url') else os.environ.get('INFLUX_URL')

# Set user agent and DTE URL
user_agent = {'User-agent': 'Mozilla/5.0'}
DTE_URL = f"https://usagedata.dteenergy.com/link/{account}"


# Connect to InfluxDB client and write API
client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)
write_api = client.write_api(write_options=SYNCHRONOUS)


# Get data from DTE website and parse XML
r = requests.get(DTE_URL, headers=user_agent)

if r.status_code == 400:
    try:
        error_data = r.json()
    except ValueError:
        error_data = None

    if error_data is not None and 'error' in error_data:
        error = error_data['error']
        error_message = f"Error {error['statusCode']}: {error['message']} (code {error['code']})"
        raise ValueError(error_message)


# Extract electric readings
data = xmltodict.parse(r.content)
for line in data['feed']['entry']:
    if line["title"] == "Electric readings":
        data = line
        break;

if 'content' not in data or 'IntervalBlock' not in data['content']:
    raise ValueError("Unable to parse response, is {dte_account} the correct ID?")


# Write data to InfluxDB
for day in data['content']['IntervalBlock']:
    for hour in day['IntervalReading']:
        ts = hour['timePeriod']['start']
        v = hour['value']
        dt = datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
        
        p = influxdb_client.Point("dte").tag("account", account).field("watt", int(v)).time(dt)
        print(dt + ": " + str(p))
        write_api.write(bucket=bucket, record=p)
