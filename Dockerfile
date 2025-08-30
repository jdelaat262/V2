FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# workdir is where manage.py lives after COPY
WORKDIR /app

# install python deps
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# oopy only the django backend into the image
COPY backend/ /app/
COPY assets/ /app/assets/

# simple entrypoint that waits for DB (uncomment in compose if used)
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

# default command runs dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
