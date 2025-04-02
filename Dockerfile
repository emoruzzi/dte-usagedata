FROM python:3.9

RUN mkdir /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


COPY app.py /app/app.py
COPY config.ini /app/config.ini.template


COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default environment variables
ENV DTE_UUID=""
ENV INFLUXDB_URL=""
ENV INFLUXDB_TOKEN=""
ENV INFLUXDB_ORG=""
ENV INFLUXDB_BUCKET=""
ENV INFLUX_ELECTRIC_MEASUREMENT="dte_electric"
ENV INFLUX_GAS_MEASUREMENT="dte_gas"
# Default to run once (0 = run once and exit)
ENV INTERVAL="0"

WORKDIR /app
VOLUME [ "/app" ]

ENTRYPOINT ["/app/entrypoint.sh"]
