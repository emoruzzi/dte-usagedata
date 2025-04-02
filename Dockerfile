FROM python:3.9

RUN mkdir /app

COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY config.ini /app/config.ini
RUN pip install --no-cache-dir -r /app/requirements.txt

VOLUME [ "/app" ]
CMD ["python", "/app/app.py"]
