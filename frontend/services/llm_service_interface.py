import requests
import websockets
import json


class LLM_Service_Interface:
    def __init__(self, session_id=0, chat_interface_url="ws://127.0.0.1:8001/ws"):
        self.session_id = session_id
        self.chat_interface_url = chat_interface_url

    def chat(self, user_query):
        url = f"{self.chat_interface_url}"
        data = {"text": user_query}
        response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json().get("response")
        else:
            return f"Error: {response.status_code}, {response.text}"

    async def chat_ws(self, user_query, locale, st):
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
