#!/bin/sh
set -eu

if [ "${AEA_GATEWAY_MODE:-}" = "alb" ]; then
  RESOLVER_FOUND=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf || true)
  RESOLVER="${AEA_RESOLVER:-${RESOLVER_FOUND:-10.40.0.2 169.254.169.253}}"
  : "${AEA_BFF_UPSTREAM:=http://bff.aea-pilot.internal:8080}"
  : "${AEA_AGENT_UPSTREAM:=http://agent-runner.aea-pilot.internal:8080}"
  : "${AEA_GRAFANA_UPSTREAM:=http://grafana.aea-pilot.internal:3000}"
  sed -e "s|__RESOLVER__|${RESOLVER}|g" \
      -e "s|__BFF_UPSTREAM__|${AEA_BFF_UPSTREAM}|g" \
      -e "s|__AGENT_UPSTREAM__|${AEA_AGENT_UPSTREAM}|g" \
      -e "s|__GRAFANA_UPSTREAM__|${AEA_GRAFANA_UPSTREAM}|g" \
      /etc/nginx/nginx-alb.conf > /etc/nginx/nginx.conf
  exec nginx -g 'daemon off;'
fi

mkdir -p /etc/nginx/tls
openssl req -x509 -newkey rsa:2048 -nodes -days 2 \
  -keyout /etc/nginx/tls/server.key -out /etc/nginx/tls/server.crt \
  -subj '/CN=localhost' >/dev/null 2>&1
exec nginx -g 'daemon off;'
