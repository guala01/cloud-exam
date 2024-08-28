FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scw_scrape.py .

CMD ["python", "scw_scrape.py"]
