# Use Python 3.11-slim as requested
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the pipeline script
CMD ["python", "run_pipeline.py"]
