# Use the official Python image from the DockerHub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your bot runs on (if applicable, adjust if necessary)
EXPOSE 8080

# Define environment variable if needed
# ENV VARIABLE_NAME=value

# Run the application
CMD ["python", "robot.py"]