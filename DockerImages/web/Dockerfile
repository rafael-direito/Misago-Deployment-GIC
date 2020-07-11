FROM nginx:mainline-alpine


RUN apk update
RUN apk --no-cache add py3-setuptools
RUN apk --no-cache add py-pip
RUN python3 -m pip install cherrypy

# Copy 
COPY block_ips /

# Remove default configuration and add our custom Nginx configuration files
RUN rm /etc/nginx/conf.d/default.conf \
    && apk add --no-cache curl

RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
RUN apk update
RUN apk add filebeat


# Telegraf
COPY telegraf/telegraf  /usr/bin/
COPY telegraf/telegraf.conf  /
RUN chmod +x /usr/bin/telegraf

COPY ["./misago",  "/etc/nginx/sites-available/"]
COPY ./security.conf /etc/nginx/conf.d/

# Add and setup entrypoint
COPY entrypoint.sh /

# Copy Filebeat
COPY filebeat / 


#Healthcheck to make sure container is ready
HEALTHCHECK CMD curl --fail http://localhost:80 || exit 1


ENTRYPOINT ["/entrypoint.sh"]

VOLUME ["/var/run", "/etc/nginx/conf.d/", "/var/cache/nginx/"]

