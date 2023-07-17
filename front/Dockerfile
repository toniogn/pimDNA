# Pull official node base image
FROM node:18.16 AS builder

# Set working directory
WORKDIR /app/front

# Copies package.json and package-lock.json to Docker environment
COPY package.json ./
COPY yarn.lock ./

# Installs all node packages
RUN yarn

# Copies everything over to Docker environment and start app
COPY . .
RUN yarn build

# Production server stage
FROM nginx:1.25.1 AS production
COPY --from=builder /app/front/build /usr/share/nginx/html
COPY nginx.default.conf /etc/nginx/conf.d/default.conf