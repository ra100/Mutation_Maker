# First stage is used to install the dependencies and to run the development live-reload npm server
FROM node:12.13.1-alpine as live-reload-server
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"
COPY ./ /frontend/
WORKDIR /frontend/
RUN npm ci
EXPOSE 3000
CMD npm start

# Second stage is used for creating an optimized production build of the website
FROM node:12.13.1-alpine as builder
COPY --from=live-reload-server /frontend /frontend
WORKDIR /frontend/
RUN npm run build

# Third stage is used for running the nginx production server using the built artifacts from the "builder" stage
FROM nginx:1.16.1-alpine as production-server
COPY resources/docker-nginx-frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /frontend/build /usr/share/nginx/html
EXPOSE 3000
CMD nginx -g "daemon off;"
