FROM python:3.8-slim

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /app/start.sh

COPY extract_load.py .

RUN echo "0 3 * * * python /app/extract_load.py" | crontab

CMD ["python", "extract_load.py"]