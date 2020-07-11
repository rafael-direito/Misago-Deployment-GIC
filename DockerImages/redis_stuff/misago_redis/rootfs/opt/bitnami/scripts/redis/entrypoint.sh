#!/bin/bash

export ALLOW_EMPTY_PASSWORD=yes
# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail
#set -o xtrace

# Load libraries
. /opt/bitnami/scripts/libbitnami.sh
. /opt/bitnami/scripts/libredis.sh

# Load Redis environment variables
eval "$(redis_env)"

print_welcome_page

if [[ "$*" = *"/opt/bitnami/scripts/redis/run.sh"* || "$*" = *"/run.sh"* ]]; then
    info "** Starting Redis setup **"
    /opt/bitnami/scripts/redis/setup.sh
    info "** Redis setup finished! **"
fi

# Telegraf
# save ip in an environment variable
export HOST_TAG=$HOST_MONITORING_TAG$(awk 'END{print $1}' /etc/hosts)
# Run metric collector - telegraf
eval "/usr/bin/telegraf --config /telegraf.conf &"

echo ""
exec "$@"
