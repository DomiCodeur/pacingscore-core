# Builder stage
FROM node:18-alpine AS builder
WORKDIR /app

# Build args for environment generation
ARG SUPABASE_URL
ARG SUPABASE_ANON_KEY
ARG TMDB_API_KEY
ARG API_URL=/api
ENV SUPABASE_URL=${SUPABASE_URL}
ENV SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
ENV TMDB_API_KEY=${TMDB_API_KEY}
ENV API_URL=${API_URL}

COPY package*.json ./
RUN npm install --silent
COPY . .
RUN npm run build

# Runner stage
FROM nginx:alpine
# Copier la configuration nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copier les fichiers buildés
COPY --from=builder /app/dist/pacingscore-frontend /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
