FROM haproxy:1.7

COPY haproxy-entrypoint.sh /

RUN chmod +x /haproxy-entrypoint.sh

EXPOSE 6379
EXPOSE 9000

# Telegraf
COPY telegraf/telegraf  /usr/bin/
COPY telegraf/telegraf.conf  /
RUN chmod +x /usr/bin/telegraf

ENTRYPOINT [ "/haproxy-entrypoint.sh" ]

CMD [ "haproxy", "-f", "/etc/haproxy/haproxy.cfg" ]
