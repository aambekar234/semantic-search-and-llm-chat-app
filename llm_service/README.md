# LLM Service
This service is a FAST API REST service application. This application is intended to provide chat interface for the frontend application. This service also provides semantic search endpoint for document retrival based for user query context. 

This service relies on chromadb service for document/context retrival. You must first run the chroma docker container before starting this service. 

For the chatbased interaction LLAMA-2 7B model is used in conjunction with lanchain framework. The chat agent implemetes context retriver for document context retriever and also the langchain's BufferMemory to keep track of individual user interactions. 
For handling multiple users simultaneosly and provide seamless chat experience this service uses websockets for the user communication. Distinct instances for each user websockets are managed and maintanied in the memory. 

## How to run this service?
install dependencies by running below commands
`ENV CMAKE_ARGS="-DLLAMA_METAL=on"`
`ENV FORCE_CMAKE=1`
`pip install requirements.txt`

Download llm model by running download_model.py script
`python download_model.py`

Build Docker file
`docker build -t llm-service-image .`

Run docker container. 
`docker run -d -p 8001:8000 -v $(pwd)/model:/llm_service/model --name llm-service llm-service-image:latest`


