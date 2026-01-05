# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package.json package-lock.json* yarn.lock* ./

# Install dependencies
# Using npm install instead of npm ci to handle lock file mismatches
RUN npm install

# Copy UI source code
COPY public/ ./public/
COPY src/ ./src/

# Set the environment variable before building
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

