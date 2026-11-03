FROM python:3.11-slim

# Install GCC for compiling the C binary
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Compile the C binary
RUN gcc student_record_management.c -o student_record_management

# Expose web server port
EXPOSE 5000

# Start production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
