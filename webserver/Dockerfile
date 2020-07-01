FROM nginx:1.12-alpine
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"

COPY docker-nginx-proxy.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
