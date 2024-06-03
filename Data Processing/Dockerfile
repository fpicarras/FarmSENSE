# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /pic-server

# Copy the current directory contents into the container at /app
COPY . /pic-server

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "server.py"]
