# use python image version 3.8
FROM python:3.8-slim as build-stage

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
	build-essential gcc 

# set workdir
WORKDIR /usr/src/app

# set python virtual environment
RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

# copy requirements only then install the requirements
COPY requirements.txt .

# install requirements
RUN pip3 install -r requirements.txt

# second stage
FROM python:3.8-slim

# make a new user for least privilege
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

# make a new directory and set permission to python user
RUN mkdir /usr/src/app && chown python:python /usr/src/app
WORKDIR /usr/src/app

# copy as a new user
COPY --chown=python:python --from=build-stage /usr/src/app/venv ./venv
COPY --chown=python:python . .

# run as user group
USER 999

# run the webapp
ENV PATH="/usr/src/app/venv/bin:$PATH"
ENV DEBUG=0

CMD gunicorn wsgi:app --bind 0.0.0.0:5000