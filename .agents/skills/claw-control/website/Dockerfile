# Claw Control Website / Landing Page
FROM node:22-alpine AS builder
WORKDIR /app

# Copy package files from website
COPY website/package*.json ./

# Install dependencies
RUN npm install

# Copy website source
COPY website/ ./

# Build the static site
RUN npm run build

# Production - serve with http-server
FROM node:22-alpine
RUN npm install -g http-server
COPY --from=builder /app/dist /app
WORKDIR /app

# Expose port
EXPOSE 8080

CMD ["sh", "-c", "http-server -p ${PORT:-8080} -c-1 --spa"]
