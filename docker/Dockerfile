FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./frontend/todolit.py /app/todolit.py

COPY ./templates/ templates/ 

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 3007

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3007", "todolit:app"]
