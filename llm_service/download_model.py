"""Script to download the llm model from the specified URL."""

import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(".env")

import requests
import sys


def download_model(model_url, destination):
    response = requests.get(model_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kilobyte
    with open(destination, "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)
    if os.path.getsize(destination) != total_size:
        print("ERROR: Model download was incomplete.")
        sys.exit(1)


if __name__ == "__main__":
    model_url = os.environ["model_download_url"]
    destination = os.environ["model_path"]
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    download_model(model_url, destination)
