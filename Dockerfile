FROM python:3-alpine AS base
# Image to Build Dependencies
FROM base AS builder

WORKDIR /app

COPY ./requirements.txt /app

# Build Dependencies
RUN apk --no-cache add gcc musl-dev libffi-dev openssl-dev libxml2-dev libxslt-dev file llvm-dev make g++

# Python Dependencies
RUN pip install --no-cache-dir --prefix=/install gunicorn
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime Environment Image
FROM base


WORKDIR /app
# Runtime Dependencies
RUN apk --no-cache add libxml2 libxslt
COPY --from=builder /install /usr/local
COPY . /app/

RUN mkdir /app/data

EXPOSE 1337
CMD gunicorn feetter:app --bind 0.0.0.0:1337 --worker-class sanic.worker.GunicornWorker
