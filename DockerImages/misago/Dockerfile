
FROM python:3.7

ENV PYTHONUNBUFFERED 1
ENV IN_MISAGO_DOCKER 1

# Install dependencies in one single command/layer
RUN apt-get update && apt-get install -y \
    vim \
    libffi-dev \
    libssl-dev \
    sqlite3 \
    libjpeg-dev \
    libopenjp2-7-dev \
    locales \
    cron \
    postgresql-client \
    gettext

# Add requirements and install them. We do this unnecessasy rebuilding.
ADD requirements.txt /
ADD requirements-plugins.txt /

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-plugins.txt

WORKDIR /srv/misago

# Telegraf
COPY telegraf/telegraf  /usr/bin/
COPY telegraf/telegraf.conf  /
RUN chmod +x /usr/bin/telegraf

EXPOSE 80

# Add and configure entrypoint and command
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

