# Start with Python 3.14 already installed
FROM python:3.14-slim

# Set working directory inside container
WORKDIR /app

# Install UV package manager
RUN pip install uv

# Copy dependency file first (for caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system -e .

# Copy the rest of your code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
