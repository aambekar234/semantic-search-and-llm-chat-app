FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port the service runs on
EXPOSE 8000

# Define the command to run the service
CMD ["chroma", "run", "--path", "./database", "--host", "0.0.0.0"]