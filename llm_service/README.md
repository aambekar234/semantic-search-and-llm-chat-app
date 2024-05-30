# LLM Service
This service is a FAST API application intended to provide chat interface and semantic search for the frontend. 

This service relies on chromadb_service for document/context retrival. You must run the chromadb_service first before attempting to run this one. 

For the chatbase interaction LLAMA-2-7B model is used in conjunction with langchain framework. The chat agent implements document-retriever and langchain's BufferMemory to provide conversational context to the LLM model. <br>
For handling multiple users simultaneosly and provide seamless chat experience this service uses websockets. Distinct instances of each user websockets are managed and maintanied in the memory to achieve this. 

For the simplicity of a demo, the arguments to the scripts are stored in .env file. This file is loaded as a environment variable file during the run. You may change the model, application port etc by modifying the .env file. 

## How to run the llm-service?

Download the llm model first by running download_model.py script <br>
`python download_model.py`

### Running the service locally

**It is recommended to run the service without docker to avoid high latencies on local machine** <br>
Docker run is provided for the cloud deployments. 

make sure you are in correcr dir <br>
`cd llm_service`
run the service <br>
`uvicorn app.main:app --host 0.0.0.0 --port 8001`

### Docker run

Build Docker file <br>
`docker build -t llm-service-image .`
 
Run docker container <br>
**Note: It is important to run below command from within the llm_service directory to correctly mount the model directory.** <br>

`docker run -d -p 8001:8000 -v $(pwd)/model:/llm_service/model --name llm-service llm-service-image:latest`

Running the service without docker

`uvicorn app.main:app --host 0.0.0.0 --port 8001`
