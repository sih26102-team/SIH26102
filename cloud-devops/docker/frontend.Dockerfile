FROM node:20-slim AS build
WORKDIR /app
COPY frontend-dashboard/package.json frontend-dashboard/package-lock.json* ./
RUN npm install
COPY frontend-dashboard/ .

# Inject variables during the build process
ARG VITE_USE_MOCK=true
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_USE_MOCK=$VITE_USE_MOCK
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]