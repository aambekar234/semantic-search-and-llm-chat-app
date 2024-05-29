# LLM Service
This service is a FAST API application intended to provide chat interface and semantic search for the frontend application. 

This service relies on chromadb service for document/context retrival. You must first run the chromadb_service before attempting to run this one. 

For the chatbase interaction LLAMA-2-7B model is used in conjunction with langchain framework. The chat agent implements document-retriever and langchain's BufferMemory to provide conversational context to the LLM model. 
For handling multiple users simultaneosly and provide seamless chat experience this service uses websockets. Distinct instances of each user websockets are managed and maintanied in the memory to achieve this. 

## How to run the llm-service?

Download the llm model first by running download_model.py script
`python download_model.py`

Build Docker file
`docker build -t llm-service-image .`

Run docker container
Note: It is important to run below command from inside llm_service directory to correctly mount the model directory. 

`docker run -d -p 8001:8000 -v $(pwd)/model:/llm_service/model --name llm-service llm-service-image:latest`

Running the service without docker

`uvicorn app.main:app --host 0.0.0.0 --port 8001`
