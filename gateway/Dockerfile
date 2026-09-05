FROM nginx:1.29-alpine

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

USER nginx

CMD ["nginx", "-g", "daemon off;"]