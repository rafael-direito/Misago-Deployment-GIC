FROM docker.io/bitnami/minideb:buster
LABEL maintainer "Bitnami <containers@bitnami.com>"

ENV HOME="/" \
    OS_ARCH="amd64" \
    OS_FLAVOUR="debian-10" \
    OS_NAME="linux"

COPY prebuildfs /
# Install required system packages and dependencies
RUN install_packages acl ca-certificates curl gzip libc6 libssl1.1 procps tar
RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "wait-for-port" "1.0.0-1" --checksum 07c4678654b01811f22b5bb65a8d6f8e253abd4524ebb3b78c7d3df042cf23bd
RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "redis" "6.0.5-0" --checksum 80451a0be0556febde7a77bdcc98d2c2429495007b3ed1d042fb45d4c7a10424
RUN . /opt/bitnami/scripts/libcomponent.sh && component_unpack "gosu" "1.12.0-1" --checksum 51cfb1b7fd7b05b8abd1df0278c698103a9b1a4964bdacd87ca1d5c01631d59c
RUN apt-get update && apt-get upgrade -y && apt install wget -y && apt install sudo -y && apt install nano -y && \
    rm -r /var/lib/apt/lists /var/cache/apt/archives
RUN ln -s /opt/bitnami/scripts/redis/entrypoint.sh /entrypoint.sh
RUN ln -s /opt/bitnami/scripts/redis/run.sh /run.sh

COPY rootfs /
RUN /opt/bitnami/scripts/redis/postunpack.sh
ENV BITNAMI_APP_NAME="redis" \
    BITNAMI_IMAGE_VERSION="6.0.5-debian-10-r28" \   
    PATH="/opt/bitnami/common/bin:/opt/bitnami/redis/bin:$PATH"

#USER 1001

# Telegraf
COPY telegraf/telegraf  /usr/bin/
COPY telegraf/telegraf.conf  /
RUN chmod +x /usr/bin/telegraf


## Copy Filebeat
#RUN mkdir filebeat
#COPY filebeat /filebeat/ 
#RUN cd filebeat && ./filebeat modules enable redis

EXPOSE 6379

ENTRYPOINT [ "/opt/bitnami/scripts/redis/entrypoint.sh" ]
CMD [ "/opt/bitnami/scripts/redis/run.sh" ]
