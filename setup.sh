#!/bin/bash

# Setup script for Fitness Recommendation Django Application
# This script will set up the environment and start the Django server

# Detect macOS and Apple Silicon
IS_MACOS=false
IS_APPLE_SILICON=false

if [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MACOS=true
    # Check for Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        IS_APPLE_SILICON=true
        echo "Detected macOS on Apple Silicon (M1/M2/M3)"
    else
        echo "Detected macOS on Intel processor"
    fi
else
    echo "Detected non-macOS system"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies based on platform
echo "Installing dependencies..."

# Common dependencies for all platforms
pip install django djangorestframework django-cors-headers numpy pandas scikit-learn psycopg2-binary

# TensorFlow installation based on platform
if [ "$IS_APPLE_SILICON" = true ]; then
    echo "Installing TensorFlow for Apple Silicon..."
    pip install tensorflow-macos tensorflow-metal
    
    echo "Note: If you encounter issues with TensorFlow on Apple Silicon, consider using Miniforge/Conda:"
    echo "  1. Install Miniforge from https://github.com/conda-forge/miniforge"
    echo "  2. Create a conda environment: conda create -n fitness python=3.9"
    echo "  3. Activate it: conda activate fitness"
    echo "  4. Install TensorFlow: conda install -c apple tensorflow-deps"
    echo "  5. Then: pip install tensorflow-macos tensorflow-metal"
elif [ "$IS_MACOS" = true ]; then
    echo "Installing TensorFlow for macOS Intel..."
    pip install tensorflow
else
    echo "Installing TensorFlow for Linux/Windows..."
    pip install tensorflow
fi

# Create ML model directory if it doesn't exist
mkdir -p ml_model

# PostgreSQL setup reminder
echo "---------------------------------------------"
echo "PostgreSQL Database Setup:"
echo "1. Make sure PostgreSQL is installed and running"
echo "2. Create the database: CREATE DATABASE fitness_db;"
echo "3. Set environment variables or update settings.py with your credentials"
echo ""
echo "Environment variables for PostgreSQL:"
echo "  DB_NAME=fitness_db"
echo "  DB_USER=postgres"
echo "  DB_PASSWORD=your_password"
echo "  DB_HOST=localhost"
echo "  DB_PORT=5432"
echo ""
echo "To use SQLite instead, uncomment the SQLite configuration in settings.py"
echo "---------------------------------------------"

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations recommendation nutrition tracking modelinfo
python manage.py migrate

# Create superuser if needed (uncomment and modify as needed)
# echo "Creating superuser..."
# python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Start the development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000

# Note: For production deployment, use a proper WSGI server like Gunicorn
# and a web server like Nginx
