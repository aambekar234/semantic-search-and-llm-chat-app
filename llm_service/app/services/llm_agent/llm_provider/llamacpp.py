import os
import re
from operator import itemgetter
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


class LlamaCpp_Provider:
    """LlamaCpp provider class for chat interaction.
    This class orchestrates the RAG and prompt templates for the chat interaction."""

    def __init__(self):
        try:
            self.model = None
            self._load_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError("Error loading llamacpp model..")

    def _get_model_path(self):
        try:
            return os.environ["model_path"]
        except:
            raise Exception("Model path not found in environment variables")

    def _load_model(self):
        """
        Loads the LlamaCpp model with the specified parameters.

        Parameters:
        - model_path (str): The path to the model.
        - n_gpu_layers (int): The number of GPU layers.
        - n_batch (int): The batch size.
        - n_ctx (int): The context size.
        - temperature (float): The temperature for sampling.
        - f16_kv (bool): Whether to use float16 for key-value tensors.
        - callback_manager (CallbackManager): The callback manager.
        - verbose (bool): Whether to enable verbose mode.

        Returns:
        - None
        """
        self.model = LlamaCpp(
            model_path=self._get_model_path(),
            n_gpu_layers=1,
            n_batch=512,
            n_ctx=0,
            temperature=0.0,
            f16_kv=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=False,
        )

    def _get_prompt_rag_template(self):
        """Returns the prompt template for the RAG specifc chain."""

        template_str = """<s>[INST] <<SYS>>
        You are an AI assistant chatbot for a online store customer service. You answer professional user questions about products and services.
        You will be presented with product catalogues that store has in the context. Answer the user question appropriately based on this context.
        You must strive to write complete and accurate answers. If you don't know the answer, just say that you don't know. 
        Your tone must be professional. You must generate output in the markdown-format.
        <</SYS>>
        context:
        {context}
        user question:
        {user_question} [/INST]
        """

        prompt = PromptTemplate(
            input_variables=["user_question", "context"],
            template=template_str,
        )

        return prompt

    def _get_prompt_chat_template(self):
        """Returns the prompt template for the regular chat specific chain."""

        template_str = """<s>[INST] <<SYS>>
        You are an AI assistant chatbot for a online store customer service. You answer professional user questions about products and services.
        You will be provided chat history. You may use the chat history whenever necessary to answer the user questions.
        If you don't know the answer, just say that you don't know.
        Your tone must be professional. You must generate output in the markdown-format.
        <</SYS>>
        chat history:
        {history}
        
        question:
        {user_question} [/INST]
        """

        prompt = PromptTemplate(
            input_variables=["user_question", "history"],
            template=template_str,
        )

        return prompt

    async def chat(self, user_question: str, memory, websocket=None):
        """
        Perform a chat interaction LLM.

        Args:
            user_question (str): The user's question or input.
            context: The context information for the conversation.
            memory: The memory information for the conversation.
            websocket: (optional) The WebSocket connection for streaming responses.

        Returns:
            The response from the LLM.

        Raises:
            Any exceptions that occur during the chat interaction.
        """

        chat_pipeline = self._get_chat_pipeline(memory)
        if websocket is None:
            return await self.chat_pipeline.ainvoke(user_question)
        else:
            return await self._stream_response(
                chat_pipeline, user_question, None, websocket
            )

    async def rag_chat(
        self,
        user_question: str,
        context,
        memory,
        websocket=None,
    ):
        """
        Perform a chat interaction LLM using RAG pipeline.

        Args:
            user_question (str): The user's question or input.
            context: The context information for the conversation.
            memory: The memory information for the conversation.
            websocket: (optional) The WebSocket connection for streaming responses.

        Returns:
            The response from the LLM.

        Raises:
            Any exceptions that occur during the chat interaction.
        """
        rag_pipeline = self._get_rag_pipeline(context, memory)
        if websocket is None:
            return await rag_pipeline.ainvoke(user_question)
        else:
            return await self._stream_response(
                rag_pipeline, user_question, context, websocket
            )

    async def _stream_response(self, llm, query, context, websocket):
        """
        Stream the response from the llm to the websocket.

        Args:
            llm (LLM): The LLM provider object. This can be either the chat or rag pipeline.
            query (str): The query to be sent to the llm.
            context (str): The context to be included in the response.
            websocket (WebSocket): The websocket to send the response to.

        Returns:
            str: The complete response from the LLM.
        """
        chunk_response = ""
        response = ""

        # Streaming the response using the chain astream method from langchain
        async for chunk in llm.astream(query):
            content = chunk
            if content is not None:
                response += content
                chunk_response += content
                if "\n" in chunk_response:
                    await websocket.send_json(
                        {"type": "chunk_response", "output": chunk_response}
                    )
                    chunk_response = ""

        if chunk_response:
            await websocket.send_json(
                {"type": "chunk_response", "output": chunk_response}
            )

        if context:
            response += context
            chunks = context.split("\n")
            for chunk in chunks:
                await websocket.send_json({"type": "chunk_response", "output": chunk})
        await websocket.send_json({"type": "end", "output": ""})
        return response

    def _get_rag_pipeline(self, context, memory):
        """
        Returns a pipeline for generating a response using the RAG (Retrieval-Augmented Generation) model.

        Args:
            context (str): The context or conversation history.
            memory (dict): The memory or additional information.

        Returns:
            rag_chain (Pipeline): The RAG pipeline for generating a response.
        """
        rag_chain = (
            {"user_question": RunnablePassthrough(), "context": lambda x: context}
            | self._get_prompt_rag_template()
            | self.model
            | StrOutputParser()
        )

        return rag_chain

    def _get_chat_pipeline(self, memory):
        """
        Returns the chat pipeline for the LLM agent.

        Args:
            memory: An instance of the memory class.

        Returns:
            rag_chain: The chat pipeline for the LLM agent.
        """
        rag_chain = (
            {
                "user_question": RunnablePassthrough(),
                "history": RunnableLambda(memory.load_memory_variables)
                | itemgetter("history"),
            }
            | self._get_prompt_chat_template()
            | self.model
            | StrOutputParser()
        )

        return rag_chain
