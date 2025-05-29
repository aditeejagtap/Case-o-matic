# Use the official Python image with your version
FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Start the app
CMD ["flask", "run"]
