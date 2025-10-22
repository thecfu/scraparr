FROM python:3.14-alpine

# Copy the current directory contents into the container at /app
COPY src /

# Set the working directory
WORKDIR /scraparr

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy lib and install them
COPY lib /lib

RUN pip install /lib/client_python

# Make port 7100 available to the world outside this container
EXPOSE 7100

WORKDIR /

# Define Entry point
ENTRYPOINT ["python", "-um", "scraparr.scraparr"]
