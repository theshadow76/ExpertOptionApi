# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install websocket simplejson pandas

# Run setup.py to install your library
RUN python setup.py install

# Run when the container launches
CMD ["python", "expert.py"]
