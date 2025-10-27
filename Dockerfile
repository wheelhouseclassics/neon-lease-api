# Use official PHP 8 image
FROM php:8.2-cli

# Copy project files into /app
COPY . /app
WORKDIR /app

# Expose the port Render expects
EXPOSE 10000

# Start the PHP development server
CMD ["php", "-S", "0.0.0.0:10000", "-t", "/app"]

