FROM nginx:1.27-alpine@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
RUN apk add --no-cache openssl
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-alb.conf /etc/nginx/nginx-alb.conf
COPY ui /usr/share/nginx/html
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod 0555 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
