FROM python:3.12.0rc2-alpine3.18
LABEL maintainer="github.com/d-skowronski"

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app

ENV PYTHONUNBUFFERED 1
ENV PATH="/py/bin:$PATH"

WORKDIR /app
EXPOSE 8000

RUN apk add --update --no-cache gcc musl-dev jpeg-dev zlib-dev libjpeg libffi-dev libpq-dev&& \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools wheel && \
    /py/bin/pip install --use-pep517 -r /tmp/requirements.txt && \
    rm -rf /tmp

RUN echo "0     *       *       *       *       /py/bin/python /app/manage.py remove_expired_links > /proc/1/fd/1" >> /var/spool/cron/crontabs/root
