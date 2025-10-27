# Use official PHP 8 image
FROM php:8.2-cli

# Install Postgres client extensions
RUN apt-get update && apt-get install -y libpq-dev \
    && docker-php-ext-install pgsql pdo pdo_pgsql

# Copy project files into /app
COPY . /app
WORKDIR /app

EXPOSE 10000
CMD ["php", "-S", "0.0.0.0:10000", "-t", "/app"]
