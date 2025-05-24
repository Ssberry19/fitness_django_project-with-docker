# PostgreSQL Integration Guide for Fitness Recommendation App

This guide provides detailed instructions for integrating PostgreSQL with your Django fitness recommendation application.

## Prerequisites

- PostgreSQL installed on your system
- Django fitness recommendation application
- Basic knowledge of database management

## Installation Instructions by Platform

### macOS (including M1/M2/M3)

1. **Install PostgreSQL using Homebrew**:
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install PostgreSQL
   brew install postgresql@14
   
   # Start PostgreSQL service
   brew services start postgresql@14
   ```

2. **Verify Installation**:
   ```bash
   # Check PostgreSQL version
   postgres --version
   
   # Check if service is running
   brew services list | grep postgresql
   ```

### Linux

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y postgresql postgresql-contrib
   
   # Start PostgreSQL service
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

2. **Verify Installation**:
   ```bash
   # Check PostgreSQL version
   psql --version
   
   # Check if service is running
   sudo systemctl status postgresql
   ```

### Windows

1. **Install PostgreSQL**:
   - Download the installer from [PostgreSQL website](https://www.postgresql.org/download/windows/)
   - Run the installer and follow the prompts
   - Remember the password you set for the postgres user

2. **Verify Installation**:
   - Open Command Prompt and run:
   ```bash
   psql --version
   ```

## Database Setup

### Create Database and User

1. **Connect to PostgreSQL**:
   ```bash
   # macOS/Linux
   psql postgres
   
   # Windows (if psql is in your PATH)
   psql -U postgres
   ```

2. **Create Database**:
   ```sql
   CREATE DATABASE fitness_db;
   ```

3. **Create User (Optional)**:
   ```sql
   CREATE USER fitness_user WITH PASSWORD 'your_password';
   ```

4. **Grant Privileges**:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE fitness_db TO fitness_user;
   ```

5. **Exit PostgreSQL**:
   ```sql
   \q
   ```

### Using Docker (Alternative)

If you prefer using Docker:

```bash
# Pull PostgreSQL image
docker pull postgres:14

# Run PostgreSQL container
docker run --name fitness-postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=fitness_db -p 5432:5432 -d postgres:14

# Connect to PostgreSQL in container
docker exec -it fitness-postgres psql -U postgres
```

## Django Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Create .env file
cat > .env << EOL
DB_NAME=fitness_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
EOL
```

### Install django-environ (Optional)

For better environment variable handling:

```bash
pip install django-environ
```

Then update your `settings.py`:

```python
import environ

env = environ.Env()
environ.Env.read_env()  # Read .env file

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}
```

## Running Migrations

After setting up PostgreSQL and configuring Django:

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Fallback to SQLite

If you need to use SQLite instead:

1. Edit `settings.py` and uncomment the SQLite configuration:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. Comment out the PostgreSQL configuration.

## Common Issues and Solutions

### psycopg2 Installation Errors

If you encounter issues installing `psycopg2`:

```bash
# Try binary package instead
pip uninstall psycopg2
pip install psycopg2-binary
```

### Connection Refused

If you get "connection refused" errors:

1. Check if PostgreSQL is running:
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Verify PostgreSQL is listening on the expected port:
   ```bash
   sudo netstat -plunt | grep postgres
   ```

### Authentication Failed

If authentication fails:

1. Check your credentials in `.env` or `settings.py`
2. Verify the user exists and has proper permissions:
   ```sql
   \du  -- List users in PostgreSQL
   ```

### Database Does Not Exist

If the database doesn't exist:

1. Connect to PostgreSQL:
   ```bash
   psql postgres
   ```

2. List databases:
   ```sql
   \l
   ```

3. Create the database if it doesn't exist:
   ```sql
   CREATE DATABASE fitness_db;
   ```

## Performance Optimization

### Connection Pooling

For production environments, consider using connection pooling:

```bash
pip install django-db-connection-pool
```

Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'fitness_db'),
        # ... other settings ...
        'POOL_OPTIONS': {
            'POOL_SIZE': 20,
            'MAX_OVERFLOW': 10,
            'RECYCLE': 300,
        },
    }
}
```

### Indexing

For better performance with large datasets, add indexes to frequently queried fields:

```python
class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
```

## Backup and Restore

### Backup Database

```bash
pg_dump -U postgres -d fitness_db > fitness_backup.sql
```

### Restore Database

```bash
psql -U postgres -d fitness_db < fitness_backup.sql
```

## Conclusion

Your Django fitness recommendation application is now configured to use PostgreSQL, providing better performance, reliability, and scalability compared to SQLite. The application will use environment variables for database configuration, making it easy to switch between development and production environments.
