# This dockerfile is only meant for local development of Misago
# If you are looking for a proper docker setup for running Misago in production,
# please use misago-docker instead
FROM python:3.7

COPY [ "lifecycle.py", "/"]

# Install dependencies in one single command/layer
#RUN apt-get update && apt-get install -y \
#    vim

RUN pip install --upgrade pip && \
    pip install locust==1.1              

WORKDIR /

EXPOSE 8089

# Add and configure entrypoint and command
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

