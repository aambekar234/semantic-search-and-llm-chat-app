# Chromadb Service
Chromadb service is a vectorestore database. The database contains the amazon esci dataset. The product titles are converted into embeddings and product object is saved as a metadata for every row. 

The embeddings are calculated using sentence-transformer library and using `multi-qa-mpnet-base-dot-v1` model.
The dataset can be initialized by running init_db.py script first. This process takes around 1-2 hours as the orginal dataset has around 2 million rows. 

## How to run the chromadb service
There are two ways for running this service
1. Running the service with precomputed database file (quicker)
2. Running the service by computing the database file by using init_db.py

## Method 1
For quickly running the app use git-lfs to download precomputed database files. Once done use following command to stitch back the database files together.
`cd precomputed_database`
`cat database-part-* > database.zip`

Once done, unzip the database.zip file

### Build the docker file

build docker file
`docker build -t chromadb-image .`

### Run the docker container

start the chromadb service on port 8001
`docker run -d -p 8005:8000 -v $(pwd)/precomputed_database/database:/app/database --name chromadb-service chromadb-image:latest`

## Method 2
First install the dependencies from the parent requirements.txt file
`pip install -r requirements.txt`

Then run init_db.py
`python init_db.py`

### Build the docker file
build docker file

`docker build -t chromadb-image .`

### Run the docker container
`docker run -d -p 8005:8000 -v $(pwd)/database:/app/database --name chromadb-service chromadb-image:latest`