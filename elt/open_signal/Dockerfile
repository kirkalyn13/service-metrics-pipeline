FROM python:3.8-slim

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY extract_load.py .

CMD ["python", "extract_load.py"]