# Chromadb Service
Chromadb service is a vectorestore database service which uses [amazon-esci](https://github.com/amazon-science/esci-data) product dataset as source. The product titles are converted into vector-embeddings and product object is saved as a metadata for every row. Separate collection is made for each product locale in the dataset. 

The embedding vectors are computed using sentence-transformer library and using `multi-qa-mpnet-base-dot-v1` model.
The dataset can be initialized by running init_db.py script first. This process takes around 1-2 hours as the orginal dataset has around 2 million rows. 

## How to run the chromadb service?
There are two ways for running this service
1. Running the service with precomputed database file (quicker)
2. Running the service by computing the database file on your local machine. This process should take around 1-2 hours depending on your machine configuration. The resulting artifact should be of size 20 GB. 

## Method 1
First download the precomputed database.zip file (14GB) from this [link](https://mega.nz/file/NjUklQgA#cizPwg-wSu9zttUdRKGqo_FdQX3f5loLzJN25C77Amc). <br>
Unzip the downloaded file in the service project directory (chromadb_service). You must have database folder/directory now inside your chromadb-service folder. 
Your directory structure should look like this. 

```plaintext
chromadb_service/
├── README.md
├── Dockerfile
├── init_db.py
├── requirements.txt
├── database/
│   ├── chroma.sqlite3
│   └── indexing_files...
```

## Method 2
To compute the vectors locally on your machine please run below command. 

`python init_db.py`


### Build the docker file

`docker build -t chromadb-image .`

### Run the docker container

Start the chromadb service on port 8005. <br>
**Note: It is important to run below command from inside chromadb_service directory to correctly mount the database.**

`docker run -d -p 8005:8000 -v $(pwd)/database:/app/database --name chromadb-service chromadb-image:latest`

### Running the service without docker

`chroma run --path ./database --host 0.0.0.0 --port 8005`