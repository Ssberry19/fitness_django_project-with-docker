# macOS M1/M2/M3 Installation Guide for Fitness Recommendation App

This guide provides detailed instructions for installing and running the Fitness Recommendation Django application on Apple Silicon (M1/M2/M3) Macs.

## Prerequisites

- macOS running on Apple Silicon (M1, M2, or M3 chip)
- Python 3.9+ installed
- Terminal access

## Installation Options

### Option 1: Standard Installation (Recommended for Most Users)

1. **Extract the application zip file**
   ```bash
   unzip fitness_django_app.zip
   cd fitness_django_project
   ```

2. **Make the setup script executable**
   ```bash
   chmod +x setup.sh
   ```

3. **Run the setup script**
   ```bash
   ./setup.sh
   ```

   The setup script will automatically detect your Apple Silicon Mac and install the appropriate TensorFlow version (`tensorflow-macos`).

4. **Access the application**
   - Open your browser and navigate to: http://localhost:8000/api/

### Option 2: Conda Installation (Recommended for Best Performance)

For optimal TensorFlow performance on Apple Silicon, we recommend using Miniforge (Conda):

1. **Install Miniforge**
   ```bash
   # Download Miniforge installer
   curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh -o Miniforge3.sh
   
   # Make installer executable
   chmod +x Miniforge3.sh
   
   # Run installer
   ./Miniforge3.sh
   ```

2. **Create and activate a conda environment**
   ```bash
   # Create new environment
   conda create -n fitness python=3.9
   
   # Activate environment
   conda activate fitness
   ```

3. **Install TensorFlow dependencies**
   ```bash
   # Install Apple's TensorFlow dependencies
   conda install -c apple tensorflow-deps
   
   # Install TensorFlow for macOS
   pip install tensorflow-macos
   
   # Install Metal plugin for GPU acceleration
   pip install tensorflow-metal
   ```

4. **Install Django and other dependencies**
   ```bash
   cd fitness_django_project
   pip install django djangorestframework django-cors-headers numpy pandas scikit-learn
   ```

5. **Run the Django application**
   ```bash
   python manage.py makemigrations recommendation nutrition tracking modelinfo
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

## Troubleshooting

### TensorFlow Import Errors

If you encounter TensorFlow import errors, the application will automatically fall back to using the mock model implementation. This ensures the API will continue to function even without TensorFlow.

To fix TensorFlow issues:

1. **Verify Python architecture**
   ```bash
   python -c "import platform; print(platform.machine())"
   ```
   This should return `arm64` for Apple Silicon.

2. **Check TensorFlow installation**
   ```bash
   pip list | grep tensorflow
   ```
   You should see `tensorflow-macos` and optionally `tensorflow-metal`.

3. **Test TensorFlow import**
   ```bash
   python -c "import tensorflow as tf; print(tf.__version__)"
   ```

### Common Issues and Solutions

1. **"Cannot load library" errors**
   - Solution: Install using the Conda method (Option 2)

2. **"Illegal instruction" errors**
   - Solution: Ensure you're using the Apple Silicon version of Python and TensorFlow

3. **Performance issues**
   - Solution: Install `tensorflow-metal` for GPU acceleration

4. **"Symbol not found" errors**
   - Solution: Reinstall TensorFlow using Conda method (Option 2)

## Using the Application

Once the application is running:

1. **Access the API documentation**
   - Open your browser and navigate to: http://localhost:8000/api/

2. **Test the recommendation endpoint**
   - Use a tool like Postman or curl to send a POST request to:
   - http://localhost:8000/api/recommendation/
   - Include appropriate JSON data as described in the API documentation

3. **Explore other endpoints**
   - Nutrition: http://localhost:8000/api/nutrition/
   - Weight tracking: http://localhost:8000/api/weight-entries/
   - Model features: http://localhost:8000/api/model-features/

## Notes on Apple Silicon Performance

- The Metal plugin (`tensorflow-metal`) enables GPU acceleration on Apple Silicon
- Performance is significantly better with the Conda installation method
- The application includes automatic fallback to CPU processing if GPU acceleration is unavailable
- The mock model implementation ensures the API functions even without TensorFlow

## Additional Resources

- [TensorFlow for macOS Documentation](https://developer.apple.com/metal/tensorflow-plugin/)
- [Apple Machine Learning Documentation](https://developer.apple.com/machine-learning/)
- [Miniforge GitHub Repository](https://github.com/conda-forge/miniforge)
