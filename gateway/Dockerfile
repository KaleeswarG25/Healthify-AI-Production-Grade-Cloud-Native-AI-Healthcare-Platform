FROM nginx:1.29-alpine

RUN mkdir -p \
    /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /var/log/nginx \
    /tmp/nginx \
    && chown -R nginx:nginx \
    /var/cache/nginx \
    /var/log/nginx \
    /tmp/nginx

COPY nginx.conf /etc/nginx/nginx.conf

USER nginx

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]