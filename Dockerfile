# Use an appropriate base image for your Python application
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy your Python application code into the container
COPY app.py /app
COPY requirements.txt /app

# Install the necessary dependencies
RUN pip install -r requirements.txt

# Expose the port that your application listens on
EXPOSE 8010

# Run your Python application
CMD ["python", "app.py"]