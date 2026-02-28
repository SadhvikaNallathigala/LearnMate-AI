# Use a slim version of Python for faster builds
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for some AI libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files
COPY . . 

# Streamlit's default port is 8501, but Render likes 10000 or custom. 
# We'll stick to 8501 and tell Render to look there.
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
