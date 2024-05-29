from .llm_provider.llamacpp import LlamaCpp_Provider
from langchain.memory import ConversationBufferMemory
from cachetools import TTLCache
import textwrap


class LLM_Agent:
    """
    LLM_Agent class represents an agent that interacts with the LLM (Language Model) service.

    Attributes:
        llm_provider (LlamaCpp_Provider): An instance of the LlamaCpp_Provider class.
        cache (TTLCache): Cache for LLM memory per user session.
        db_service: The database service used for retrieving data.
    """

    def __init__(self, db_service):
        """
        Initializes a new instance of the LLM_Agent class.

        Args:
            db_service: The database service used for retrieving data.
        """
        self.llm_provider = LlamaCpp_Provider()
        self.cache = TTLCache(maxsize=100000, ttl=3600 * 3)
        self.db_service = db_service

    def get_memory(self, user_session_id):
        """
        Retrieves the LLM memory for a given user session ID.

        Args:
            user_session_id: The ID of the user session.

        Returns:
            ConversationBufferMemory: The LLM memory for the user session.
        """
        try:
            return self.cache[user_session_id]
        except KeyError:
            self.cache[user_session_id] = ConversationBufferMemory(return_messages=True)
            return self.cache[user_session_id]

    async def user_query_classifier(self, user_query):
        """
        Classifies a user query into one of the predefined categories.

        Args:
            user_query: The user query to be classified.

        Returns:
            str: The label of the classification.
        """
        prompt = (
            "<s>[INST]<<SYS>>\n"
            "You are a AI Classifier for determining a user query either 'product-inquiry', 'product-followup' or 'general-question'. You answer only the label of the classification.\n"
            "Examples:\n"
            "query:What is its color?\n"
            "product-followup\n\n"
            "query:What type of television do you have?\n"
            "product-inquiry\n\n"
            "query:Hello how are you?\n"
            "general-question\n\n"
            "query:Do you have LED lamps?\n"
            "product-inquiry\n\n"
            "query:Are you open today?\n"
            "general-question\n\n"
            "query:What are its features?\n"
            "product-followup\n\n"
            "query:What is its brand?\n"
            "product-followup\n\n"
            "query:How can you help me?\n"
            "general-question\n"
            "<</SYS>>\n"
            "Determine below query. Answer in only provided format.\n"
            f"{user_query}\n"
            "[/INST]\n"
        )

        response = await self.llm_provider.model.ainvoke(prompt)
        return response.strip().lower()

    async def user_query_product_id_analyzer(self, user_query):
        """
        Analyzes a user query and returns the product identification number if found.

        Args:
            user_query: The user query to be analyzed.

        Returns:
            str: The product identification number if found, otherwise "false".
        """
        prompt = (
            "<s>[INST]<<SYS>>\n"
            "You are an AI query analyzer who returns the product identification number in the query. If no identification number is found you return false.\n"
            "Learn from the examples below:\n"
            "query:I want to purchase 50 inches TV\n"
            "false\n\n"
            "query:Do you have led lamps\n"
            "false\n\n"
            "query:Can you tell me about product BHOSUD123?\n"
            "ID:BHOSUD123\n\n"
            "query:Can you tell me about the television you have?\n"
            "false\n\n"
            "query:Do you have a product with Id 12746?\n"
            "ID:12746\n\n"
            "query:Are you open today?\n"
            "false\n\n"
            "query:Tell me about 128DFG\n"
            "ID:128DFG\n\n"
            "query:Can you tell me about television products?\n"
            "false\n\n"
            'query:I want to purchase a 27" or 27 inches TV\n'
            "false\n\n"
            "<</SYS>>\n"
            "Analyze the query below and answer in one word. Return false if no identification number is found. \n"
            f"{user_query}\n"
            "[/INST]\n"
        )

        response = await self.llm_provider.model.ainvoke(prompt)
        response_lower = response.strip().lower()

        if response_lower != "false":
            try:
                return response.split(":")[1]
            except:
                print("Error in product id extraction")

        return "false"

    async def run(self, user_query, locale, user_session_id, websocket):
        """
        Runs the LLM agent to process a user query.

        Args:
            user_query: The user query to be processed.
            locale: The locale for retrieving data.
            user_session_id: The ID of the user session.
            websocket: The websocket for communication.

        Returns:
            str: The response generated by the LLM agent.
        """
        memory = self.get_memory(user_session_id)
        label = await self.user_query_classifier(user_query)
        print(f"llm classified user query: {label}")

        if label == "product-followup" or label == "general-question":
            response = await self.llm_provider.chat(user_query, memory, websocket)
        else:
            product_id = await self.user_query_product_id_analyzer(user_query)
            filter = {"product_id": product_id}
            retriever = self.db_service.get_retriever(locale, filter)

            print(f"llm analyzed user query identification as: {product_id}")
            filter = None
            documents = []

            if product_id != "open-ended":
                filter = {"product_id": product_id}
                retriever = self.db_service.get_retriever(locale, filter)
                documents = await retriever.ainvoke("")

            if len(documents) == 0:
                retriever = self.db_service.get_retriever(locale)
                documents = await retriever.ainvoke(user_query)

            context = self.db_service.format_docs(documents)

            response = await self.llm_provider.rag_chat(
                user_query, context, memory, websocket
            )

        memory.save_context({"input": user_query}, {"output": response})
        return response
