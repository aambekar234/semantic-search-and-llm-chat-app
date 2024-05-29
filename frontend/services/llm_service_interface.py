import requests
import websockets
import json


class LLM_Service_Interface:
    def __init__(self, session_id=0, chat_interface_url="ws://127.0.0.1:8001/ws"):
        self.session_id = session_id
        self.chat_interface_url = chat_interface_url

    async def chat_ws(self, user_query, locale, st):
        """
        Establishes a WebSocket connection to the chat interface and sends user queries.

        Args:
            user_query (str): The user's query.
            locale (str): The locale for the chat interface. This changes the db-collections used for search at backend.
            st: The Streamlit object for displaying output.

        Returns:
            str: The response received from the chat interface.
        """

        url = f"{self.chat_interface_url}"
        response = ""
        async with websockets.connect(url) as websocket:
            await websocket.send(
                f"start {json.dumps({'text': user_query, 'locale': locale, 'user_session_id': self.session_id})}"
            )
            try:
                while True:
                    data = await websocket.recv()
                    data = json.loads(data)
                    if data["type"] == "end":
                        break
                    elif data["type"] == "chunk_response" and data["output"] != None:
                        response += f"\n{data['output']}"
                        st.markdown(data["output"])
                    elif data["type"] == "error":
                        st.error(data["output"])
            except RuntimeError:
                print("RuntimeError occurred.")
                st.error("RuntimeError error occurred.")
            return response
