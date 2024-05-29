# SEMANTIC-SEARCH-AND-LLM-CHAT-APP
This project aims to implement semantic search and llm chat with RAG pipeline. The chromadb_service acts a database source while llm_service acts as API service. 

## How to run the project
First install dependencies
`pip install requirements.txt`

Afterwords, run each services sequentially in following way. 

### 1. chromadb_service
Please check the instructions in the chromadb_service project directory

### 2. llm_service
Please check the instructions in the llm_service project directory

### 3. UI
Please run below command to start the frontend service
`streamlit run UI/1_Product_Chat.py`