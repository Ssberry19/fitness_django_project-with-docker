# Django Fitness App - Docker Deployment Guide

This guide provides detailed instructions for deploying the Django Fitness Recommendation application using Docker and Docker Compose with PostgreSQL and Nginx.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- Basic knowledge of Docker and containerization

## Project Structure

The containerized application consists of three services:

1. **Web (Django)**: The Django application running with Gunicorn
2. **DB (PostgreSQL)**: The PostgreSQL database
3. **Nginx**: Web server for serving static files and as a reverse proxy

## Quick Start

1. **Clone the repository or extract the zip file**

2. **Create a .env file in the project root**

   ```bash
   # Create .env file with required environment variables
   cat > .env << EOL
   # Django settings
   SECRET_KEY=your-secret-key-here
   DEBUG=0
   ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   
   # Database settings
   DB_NAME=fitness_db
   DB_USER=postgres
   DB_PASSWORD=your-secure-password
   DB_HOST=db
   DB_PORT=5432
   
   # Superuser settings (optional)
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_PASSWORD=admin-password
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   EOL
   ```

3. **Build and start the containers**

   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Web application: http://localhost
   - API endpoints: http://localhost/api/

## Detailed Setup

### Environment Variables

The `.env` file contains all configuration needed for the application:

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | - |
| DEBUG | Debug mode (1=True, 0=False) | 0 |
| ALLOWED_HOSTS | List of allowed hosts | localhost 127.0.0.1 [::1] |
| DB_NAME | PostgreSQL database name | fitness_db |
| DB_USER | PostgreSQL username | postgres |
| DB_PASSWORD | PostgreSQL password | - |
| DB_HOST | PostgreSQL hostname | db |
| DB_PORT | PostgreSQL port | 5432 |
| DJANGO_SUPERUSER_* | Optional superuser credentials | - |

### Docker Compose Commands

**Start the application**
```bash
docker-compose up -d
```

**View logs**
```bash
docker-compose logs -f
```

**Stop the application**
```bash
docker-compose down
```

**Stop and remove volumes**
```bash
docker-compose down -v
```

**Rebuild containers**
```bash
docker-compose up -d --build
```

### Database Management

**Create database backup**
```bash
docker-compose exec db pg_dump -U postgres fitness_db > backup.sql
```

**Restore database from backup**
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres fitness_db
```

**Access PostgreSQL shell**
```bash
docker-compose exec db psql -U postgres fitness_db
```

## Directory Volumes

The Docker setup uses several volumes for data persistence:

- **postgres_data**: PostgreSQL database files
- **static_volume**: Django static files
- **media_volume**: Django media files

## Customization

### Scaling the Application

To scale the web service:

```bash
docker-compose up -d --scale web=3
```

Note: Additional configuration for load balancing would be required.

### Custom PostgreSQL Configuration

To customize PostgreSQL, create a `postgresql.conf` file and mount it in the `docker-compose.yml`:

```yaml
volumes:
  - ./postgresql.conf:/etc/postgresql/postgresql.conf
command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

### SSL/TLS Configuration

For HTTPS support, update the Nginx configuration:

1. Add SSL certificates to the Nginx container
2. Update the Nginx configuration to use SSL
3. Change the exposed port to 443

## Troubleshooting

### Container Won't Start

Check logs for errors:
```bash
docker-compose logs web
```

### Database Connection Issues

Verify PostgreSQL is running:
```bash
docker-compose ps
```

Check connection from web container:
```bash
docker-compose exec web python -c "import psycopg2; psycopg2.connect(dbname='fitness_db', user='postgres', password='your-password', host='db')"
```

### Static Files Not Loading

Verify static files were collected:
```bash
docker-compose exec web python manage.py collectstatic --dry-run
```

Check Nginx configuration and logs:
```bash
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf
docker-compose logs nginx
```

## Production Deployment

For production deployment, additional steps are recommended:

1. Use a proper domain name in ALLOWED_HOSTS
2. Configure SSL/TLS certificates
3. Set up a proper backup strategy
4. Consider using Docker Swarm or Kubernetes for orchestration
5. Implement monitoring and alerting

## Security Considerations

- Never commit the `.env` file to version control
- Use strong, unique passwords for the database
- Regularly update Docker images for security patches
- Consider using Docker secrets for sensitive information
- Implement proper network security rules

## Performance Optimization

- Configure PostgreSQL for optimal performance
- Implement caching (Redis or Memcached)
- Use a CDN for static files in production
- Configure Gunicorn workers based on available CPU cores

## Maintenance

### Updating the Application

1. Pull the latest code
2. Rebuild the containers:
   ```bash
   docker-compose up -d --build
   ```

### Database Migrations

Run migrations after code updates:
```bash
docker-compose exec web python manage.py migrate
```

### Backup Strategy

Set up regular automated backups:
```bash
# Example cron job for daily backups
0 0 * * * docker-compose exec db pg_dump -U postgres fitness_db > /path/to/backups/fitness_db_$(date +\%Y\%m\%d).sql
```
