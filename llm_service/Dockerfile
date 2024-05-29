# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables. These are used by the llama library
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
ENV FORCE_CMAKE=1

# Set the working directory in the container
WORKDIR /llm_service

# Install build tools and cmake
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements file into the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app ./app

# set docker specifc env variables
ENV db_host="host.docker.internal"
ENV db_port=8005
ENV embedding_model_name="multi-qa-mpnet-base-dot-v1"
ENV model_path="./model/model.gguf"

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]