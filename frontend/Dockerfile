# Stage 1: Build the application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and tsconfig.json first to leverage Docker caching
COPY package.json tsconfig.json ./

# Install dependencies (using npm install instead of npm ci since package-lock.json isn't available)
RUN npm install

# Copy the rest of the application code
COPY public/ ./public/
COPY src/ ./src/

# Build the application
RUN npm run build

# Stage 2: Create a production image using Nginx to serve static files
FROM nginx:alpine

# Copy the build files from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]