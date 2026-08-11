#!/bin/sh
set -eu
mkdir -p /etc/nginx/tls
openssl req -x509 -newkey rsa:2048 -nodes -days 2 \
  -keyout /etc/nginx/tls/server.key -out /etc/nginx/tls/server.crt \
  -subj '/CN=localhost' >/dev/null 2>&1
exec nginx -g 'daemon off;'
