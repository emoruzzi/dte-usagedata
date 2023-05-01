FROM python:3.9

# ENV DTE_UUID ""

# ENV INFLUX_MEASUREMENT "dte"
# ENV INFLUX_BUCKET "dte"
# ENV INFLUX_ORG "home"
# ENV INFLUX_TOKEN ""
# ENV INFLUX_URL "http://127.0.0.1:8086/"

RUN mkdir /app

COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY config.ini /app/config.ini
RUN pip install --no-cache-dir -r /app/requirements.txt

VOLUME [ "/app" ]
CMD ["python", "/app/app.py"]
