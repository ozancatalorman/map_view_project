# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/map_view_app/src/requirements.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variable
ENV NAME map_view_app

# Run app.py when the container launches
CMD ["python", "/app/map_view_app/src/app.py"]