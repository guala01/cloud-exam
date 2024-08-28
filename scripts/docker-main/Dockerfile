FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PGHOST=smoothly-blessed-dory-pdt.a1.pgedge.io
ENV PGUSER=app
ENV PGDATABASE=bdo_market_data
ENV PGSSLMODE=require


CMD ["python", "newmain.py"]
