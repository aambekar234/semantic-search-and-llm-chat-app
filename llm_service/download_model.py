import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(".env")
import requests
import sys
from tqdm import tqdm


def download_model(model_url, destination):
    """
    Downloads a model from the given URL and saves it to the specified destination.

    Args:
        model_url (str): The URL of the model to download.
        destination (str): The path where the downloaded model should be saved.

    Raises:
        SystemExit: If the model download is incomplete.

    """
    response = requests.get(model_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kilobyte
    progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)

    with open(destination, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

    if os.path.getsize(destination) != total_size:
        print("ERROR: Model download was incomplete.")
        sys.exit(1)


if __name__ == "__main__":
    model_url = os.environ["model_download_url"]
    destination = os.environ["model_path"]
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    download_model(model_url, destination)
