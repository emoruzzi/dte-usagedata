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
import argparse

parser = argparse.ArgumentParser(description='Process DTE Energy usage data')
parser.add_argument('--dry-run', action='store_true', help='Run without writing to InfluxDB')
args = parser.parse_args()

config = ConfigParser()
config.read('config.ini')

account = os.environ.get('DTE_UUID') or config.get('dte', 'uuid', fallback=None)
if not account:
    raise ValueError("DTE_UUID environment variable or uuid in config.ini is required")

electric_measurement = (os.environ.get('INFLUX_ELECTRIC_MEASUREMENT') or
                      config.get('influx', 'electric_measurement', fallback="dte_electric"))

gas_measurement = (os.environ.get('INFLUX_GAS_MEASUREMENT') or
                 config.get('influx', 'gas_measurement', fallback="dte_gas"))

bucket = (os.environ.get('INFLUX_BUCKET') or 
          os.environ.get('INFLUXDB_BUCKET') or 
          config.get('influx', 'bucket', fallback=None))
if not bucket:
    raise ValueError("INFLUX_BUCKET/INFLUXDB_BUCKET environment variable or bucket in config.ini is required")

org = (os.environ.get('INFLUX_ORG') or 
       os.environ.get('INFLUXDB_ORG') or 
       config.get('influx', 'org', fallback=None))
if not org:
    raise ValueError("INFLUX_ORG/INFLUXDB_ORG environment variable or org in config.ini is required")

token = (os.environ.get('INFLUX_TOKEN') or 
         os.environ.get('INFLUXDB_TOKEN') or 
         config.get('influx', 'token', fallback=None))
if not token:
    raise ValueError("INFLUX_TOKEN/INFLUXDB_TOKEN environment variable or token in config.ini is required")

url = (os.environ.get('INFLUX_URL') or 
       os.environ.get('INFLUXDB_URL') or 
       config.get('influx', 'url', fallback=None))
if not url:
    raise ValueError("INFLUX_URL/INFLUXDB_URL environment variable or url in config.ini is required")

user_agent = {'User-agent': 'Mozilla/5.0'}
DTE_URL = f"https://usagedata.dteenergy.com/link/{account}"


if not args.dry_run:
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    print("Connected to InfluxDB")
else:
    print("DRY RUN MODE: No data will be written to InfluxDB")


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


parsed_data = xmltodict.parse(r.content)

meters = {}
for entry in parsed_data['feed']['entry']:
    if entry.get('content', {}).get('UsagePoint') and 'ServiceCategory' in entry['content']['UsagePoint']:
        for link in entry.get('link', []):
            if link.get('@rel') == 'self' and 'UsagePoint/' in link.get('@href', ''):
                parts = link['@href'].split('/')
                idx = parts.index('UsagePoint')
                if idx + 1 < len(parts):
                    meter_id = parts[idx + 1]
                    kind = int(entry['content']['UsagePoint']['ServiceCategory']['kind'])
                    # 0 = electricity, 1 = gas, etc.
                    meter_type = 'electric' if kind == 0 else 'gas' if kind == 1 else f'unknown_{kind}'
                    meters[meter_id] = {
                        'type': meter_type,
                        'title': entry.get('title')
                    }

print(f"Found {len(meters)} meters: {meters}")

readings_data = {}
for entry in parsed_data['feed']['entry']:
    if entry.get('title') and ('readings' in entry.get('title', '').lower()):
        meter_id = None
        for link in entry.get('link', []):
            if link.get('@rel') == 'self' and 'UsagePoint/' in link.get('@href', ''):
                parts = link['@href'].split('/')
                idx = parts.index('UsagePoint')
                if idx + 1 < len(parts):
                    meter_id = parts[idx + 1]
                    break
        
        if meter_id and meter_id in meters:
            readings_data[meter_id] = entry

if not readings_data:
    raise ValueError(f"Unable to parse response, is {account} the correct ID?")


for meter_id, reading_entry in readings_data.items():
    meter_info = meters[meter_id]
    meter_type = meter_info['type']
    
    if meter_type == "electric":
        measurement_name = electric_measurement
    elif meter_type == "gas":
        measurement_name = gas_measurement
    else:
        print(f"Warning: Skipping unsupported meter type: {meter_type}")
        continue
    
    print(f"Processing {meter_type} meter {meter_id} using measurement '{measurement_name}'")
    
    field_name = "watt" if meter_type == "electric" else "ccf" if meter_type == "gas" else "value"
    
    if 'content' not in reading_entry or 'IntervalBlock' not in reading_entry['content']:
        print(f"Warning: Couldn't find readings for meter {meter_id} ({meter_type})")
        continue
    
    blocks = reading_entry['content']['IntervalBlock']
    if not isinstance(blocks, list):
        blocks = [blocks]
    
    for day in blocks:
        if 'IntervalReading' not in day:
            continue
        
        readings = day['IntervalReading']
        if not isinstance(readings, list):
            readings = [readings]
        
        for hour in readings:
            ts = hour['timePeriod']['start']
            v = hour['value']
            dt = datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
            
            reading_quality = None
            if 'ReadingQuality' in hour:
                reading_quality = hour.get('ReadingQuality', {}).get('quality')
                
            p = (influxdb_client.Point(measurement_name)
                .tag("account", account)
                .tag("meter_type", meter_type)
                .tag("meter_id", meter_id)
                .field(field_name, int(v)))
                
            if reading_quality is not None:
                p = p.field("quality", reading_quality)
                
            p = p.time(dt)
            
            quality_str = f" (quality: {reading_quality})" if reading_quality is not None else ""
            print(f"{dt}: {meter_type} meter {meter_id} = {v} {field_name}{quality_str}")

            if not args.dry_run:
                write_api.write(bucket=bucket, record=p)
