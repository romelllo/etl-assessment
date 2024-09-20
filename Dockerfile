# Use an official Python runtime as a parent image
FROM python:3.10-slim
LABEL maintainer="Roman Novikov <romannovikov526@gmail.com>"

# Set the working directory in the container
WORKDIR /opt/etl_assessment

# Copy the requirements.txt file
COPY requirements.txt .
# Install the necessary Python packages
RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /opt/etl_assessment
COPY . .

ENTRYPOINT ["python3.10", "-u", "./src/app/main.py"]
