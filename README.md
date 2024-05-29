# SEMANTIC-SEARCH-AND-LLM-CHAT-APP
This project aims to implement a semantic search and RAG-powered LLM-chat application at scale. It consists of three main components:

	1.	Vector Store Database (chromadb_service): Manages and stores vector embeddings for efficient retrieval.
	2.	Backend LLM-Powered API Service (llm_service): Handles the core logic and interacts with the LLM model.
	3.	Frontend Application: Provides the user interface for interacting with the application.

The modular design allows each component to be independently scalable, enabling the system to handle large traffic volumes as needed.

For real-world deployment, it is recommended to adopt a distributed vector database solution instead of chromadb. Additionally, further enhancements will be necessary to make the application production-ready.

This project setup is just the beginning of creating a production-ready chat based application.

## How to run this project
Install dependencies (use python >= 3.10).
You will require to add environment variable CMAKE_ARGS for successful llma-cpp-python installation. For Apple Silicon Macbooks please use below command. Please check official documentation of llma-cpp-python for other platform specific instructions. [link](https://pypi.org/project/llama-cpp-python/)

`CMAKE_ARGS="-DLLAMA_METAL=on"` <br>
`pip install -r requirements.txt`

Afterwords, in following sequence run each service.

### 1. chromadb_service
This is a vector database service which creates, modifies and updates dataset entries.
Follow these instructions [here](./chromadb_service/README.md)

### 2. llm_service
This API service is powered by the llama-2-7B model for the chat interface and uses chromadb_service for context retrieval. 
Follow these instructions [here](./llm_service/README.md)

### 3. frontend
This is a froentend application (streamlit) which relies on llm_service  to make chat-bot and semantic search work.

To start the frontend app run below command.

`streamlit run frontend/1_Product_Chat.py`

Please reach out to me on [LinkedIn](https://www.linkedin.com/in/aambekar234/) for any questions related to implementation and techonlogies. Feel free to open pull-requests for further improvements. Thank you!