# syntax=docker/dockerfile:1
# Web de Trail Peñasagra: build con Node y servicio con Caddy.

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci --ignore-scripts
COPY . .
ARG PUBLIC_ORIGIN=http://localhost:8080
ENV PUBLIC_ORIGIN=${PUBLIC_ORIGIN}
RUN npm run build

FROM caddy:2.11-alpine AS runtime
COPY --from=build /app/dist /srv
