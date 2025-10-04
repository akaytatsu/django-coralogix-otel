# Quick setup script for testing

echo "Setting up Django Coralogix OpenTelemetry package..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install test dependencies
pip install -e .[dev]

echo "Setup complete! You can now:"
echo "1. Test the package: python -c 'import django_coralogix_otel; print(django_coralogix_otel.__version__)'"
echo "2. Run tests: pytest"
echo "3. Build for PyPI: python -m build"