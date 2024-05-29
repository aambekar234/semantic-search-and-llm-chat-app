# SEMANTIC-SEARCH-AND-LLM-CHAT-APP
This project aims to implement semantic search and llm chat with RAG pipeline. The chromadb_service acts a database source while llm_service acts as API service. 

## How to run the project
Install dependencies.
You will require to add environment variable CMAKE_ARGS llma-cpp-python installation. For apple silicon Macbook please use below command. Please check official documents of llma-cpp-python for other platform specific arguments [link](https://pypi.org/project/llama-cpp-python/)

`CMAKE_ARGS="-DLLAMA_METAL=on"`
`pip install requirements.txt`

Afterwords, in following sequence run below services one after another. 

### 1. chromadb_service
This is a vector database service which creates, modifies and updates dataset entries.
Follow these instructions [here](./chromadb_service/README.md)

### 2. llm_service
This is an API services powered with llama-2-7B model for chat interface and uses chromadb_service for context retrieval. 
Follow these instructions [here](./llm_service/README.md)

### 3. frontend
This is a froentend services (streamlit) which uses llm_service endpoints to implement cha-bot and semantic search. 

To start the frontend run bekow command.

`streamlit run frontend/1_Product_Chat.py`

Please reach out to me on [LinkedIn](https://www.linkedin.com/in/aambekar234/) for any question related to implementations. Feel free to open pull-requests for further improvements. Thank you!