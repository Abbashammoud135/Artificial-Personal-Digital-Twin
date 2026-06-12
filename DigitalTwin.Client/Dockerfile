# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm config set fetch-retry-maxtimeout 600000 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retries 5 && \
    npm ci

# Copy application files
COPY . .

# Declare build-time arguments
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the production application
RUN npm run build

# Run stage
FROM nginx:stable-alpine

# Copy built files to Nginx web root
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
