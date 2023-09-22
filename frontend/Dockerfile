# Use the official Python image as the base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /frontend

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Flask and other dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5000
EXPOSE 5000

# Define the command to start the application
CMD ["python", "app.py"]
