# Stage 1: Build React static assets
FROM node:20-alpine as builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm ci

# Copy all source assets
COPY . .
# Compile and build the code
RUN npm run build

# Stage 2: Serve compiled assets using Nginx container
FROM nginx:stable-alpine

# Copy compiled assets from builder stage
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html
# Inject custom nginx configuration rules
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
