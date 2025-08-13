# Use an official Python runtime as a parent image
# This specifies the exact Python version you need
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code to the working directory
COPY . .

# Make port 10000 available to the world outside this container
# Render uses this port to route traffic to your service
EXPOSE 10000

# Define the command to run your app using Gunicorn
# This command starts 4 worker processes to handle requests
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:10000", "app:app"]