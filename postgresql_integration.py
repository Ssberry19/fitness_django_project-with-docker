"""
PostgreSQL Integration for Django Fitness Application

This file provides detailed instructions and code for integrating PostgreSQL with the Django fitness application.
"""

import os

# PostgreSQL configuration for Django settings.py
POSTGRESQL_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'fitness_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Installation commands for different platforms
INSTALLATION_COMMANDS = {
    'macos': """
# Install PostgreSQL using Homebrew
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Install Python adapter
pip install psycopg2-binary
""",
    'macos_m1': """
# Install PostgreSQL using Homebrew (M1 optimized)
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Install Python adapter (binary version works on M1)
pip install psycopg2-binary
""",
    'linux': """
# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Python adapter
pip install psycopg2-binary
""",
    'windows': """
# Install PostgreSQL from https://www.postgresql.org/download/windows/

# Install Python adapter
pip install psycopg2-binary
"""
}

# Database creation commands
DB_CREATION_COMMANDS = """
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE fitness_db;

# Create user (optional)
CREATE USER fitness_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fitness_db TO fitness_user;

# Exit PostgreSQL
\\q
"""

# Docker setup commands
DOCKER_COMMANDS = """
# Pull PostgreSQL image
docker pull postgres:14

# Run PostgreSQL container
docker run --name fitness-postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=fitness_db -p 5432:5432 -d postgres:14

# To connect to PostgreSQL in container
docker exec -it fitness-postgres psql -U postgres
"""

# Django migration commands
MIGRATION_COMMANDS = """
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
"""

# Environment variables setup
ENV_SETUP = """
# Create .env file
cat > .env << EOL
DB_NAME=fitness_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
EOL
"""

# Function to update Django settings.py for PostgreSQL
def update_django_settings(settings_path):
    """
    Updates Django settings.py file to use PostgreSQL instead of SQLite
    
    Args:
        settings_path: Path to settings.py file
    """
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Find the DATABASES configuration
    if 'django.db.backends.sqlite3' in content:
        # Replace SQLite configuration with PostgreSQL
        sqlite_config = r"DATABASES = {.*?'ENGINE': 'django.db.backends.sqlite3'.*?}"
        postgres_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'fitness_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}"""
        
        # Make sure os is imported
        if 'import os' not in content:
            content = 'import os\n' + content
        
        # Replace the database configuration
        import re
        content = re.sub(sqlite_config, postgres_config, content, flags=re.DOTALL)
    
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {settings_path} to use PostgreSQL")

# Function to update setup.sh script
def update_setup_script(setup_path):
    """
    Updates setup.sh to include PostgreSQL dependencies
    
    Args:
        setup_path: Path to setup.sh file
    """
    with open(setup_path, 'r') as f:
        content = f.read()
    
    # Add PostgreSQL dependencies
    if 'psycopg2-binary' not in content:
        # Find the pip install line
        pip_line = r"pip install django djangorestframework django-cors-headers"
        
        # Add psycopg2-binary
        new_pip_line = pip_line + " psycopg2-binary"
        content = content.replace(pip_line, new_pip_line)
        
        # Add PostgreSQL reminder
        migration_line = r"echo \"Running database migrations...\""
        postgres_reminder = """
# PostgreSQL setup reminder
echo "NOTE: Make sure PostgreSQL is running and the fitness_db database is created"
echo "If using the default SQLite database instead, no action is needed"
"""
        content = content.replace(migration_line, postgres_reminder + "\n" + migration_line)
    
    with open(setup_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {setup_path} to include PostgreSQL dependencies")

# Main function to integrate PostgreSQL
def integrate_postgresql(django_project_path):
    """
    Main function to integrate PostgreSQL with Django project
    
    Args:
        django_project_path: Path to Django project
    """
    settings_path = os.path.join(django_project_path, 'fitness_django', 'settings.py')
    setup_path = os.path.join(django_project_path, 'setup.sh')
    
    # Update settings.py
    update_django_settings(settings_path)
    
    # Update setup.sh
    update_setup_script(setup_path)
    
    print("PostgreSQL integration complete!")

if __name__ == "__main__":
    # Example usage
    integrate_postgresql('/path/to/fitness_django_project')
