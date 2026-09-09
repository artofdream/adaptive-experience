FROM nginx:1.27-alpine@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
# #409: keep the #331 nginx digest pin; rebuild so libexpat/expat is >= 2.8.4-r0
# (CVE-2026-76956 / CVE-2026-76957). Alpine 3.21+ publishes that security update.
RUN apk add --no-cache --upgrade openssl \
    && { apk add --no-cache --upgrade "libexpat>=2.8.4-r0" || apk add --no-cache --upgrade "expat>=2.8.4-r0"; }
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-alb.conf /etc/nginx/nginx-alb.conf
COPY ui /usr/share/nginx/html
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod 0555 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
