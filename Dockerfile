FROM python:3.13

WORKDIR /app

COPY requirements-server.txt .

RUN pip install --no-cache-dir -r requirements-server.txt

COPY custom_components/casambi_mqtt/entities/ custom_components/casambi_mqtt/entities/
COPY server.py .

CMD ["python", "server.py"]
