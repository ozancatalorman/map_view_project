# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY map_view_app /app

# Install any required packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variables
ENV NAME map_view_app

# Run app.py when the container launches
CMD ["python", "/app/src/app.py"]

