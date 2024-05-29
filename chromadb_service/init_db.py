import os
import time
import shutil
from git import Repo
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils.batch_utils import create_batches


class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        # embed the documents somehow
        return self.model.encode(input).tolist()


def delete_directory(directory_uri):
    """
    Deletes a directory and all its contents.

    Parameters:
    directory_uri (str): The URI of the directory to be deleted.

    Returns:
    None
    """
    try:
        if os.path.exists(directory_uri):
            shutil.rmtree(directory_uri)
            print(
                f"Directory '{directory_uri}' and all its contents have been deleted."
            )
        else:
            print(f"Directory '{directory_uri}' does not exist.")
    except Exception as e:
        print(f"An error occurred while deleting the directory: {e}")


def clone_repository(repo_url, clone_dir):
    # Clone the repository
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists. Skipping clone.")
        repo = Repo(clone_dir)
        repo.git.lfs("pull")
    else:
        print(f"Cloning repository {repo_url} into {clone_dir}")
        repo = Repo.clone_from(repo_url, clone_dir)
        repo.git.lfs("pull")


def create_document(row):
    product_id = row["product_id"]
    document = row["product_title"]
    metadata = {
        "product_title": row["product_title"],
        "product_id": row["product_id"],
        "product_brand": row["product_brand"],
        "product_color": row["product_color"],
        "product_description": row["product_description"],
        "product_bullet_point": row["product_bullet_point"],
    }
    return product_id, document, metadata


def insert_documents(df, collection_name, emb_fn):
    model_name = "multi-qa-mpnet-base-dot-v1"
    client = chromadb.PersistentClient(path=database_dir)
    ef = CustomEmbeddingFunction(model_name)

    collection = client.get_or_create_collection(
        name=collection_name, embedding_function=emb_fn
    )
    results = df.apply(create_document, axis=1)
    product_ids, documents, metadatas = zip(*results)

    batches = create_batches(
        api=client,
        ids=list(product_ids),
        documents=list(documents),
        metadatas=list(metadatas),
    )

    for batch in batches:
        print(f"Adding batch of size {len(batch[0])} to collection {collection_name}.")
        collection.add(ids=batch[0], documents=batch[3], metadatas=batch[2])


def process_data(product_dataset_file):
    df = pd.read_parquet(product_dataset_file)
    # Replace NaN values with None
    df = df.fillna("")
    df_us = df[df["product_locale"] == "us"]
    df_es = df[df["product_locale"] == "es"]
    df_jp = df[df["product_locale"] == "jp"]

    emb_fn = CustomEmbeddingFunction("multi-qa-mpnet-base-dot-v1")

    print("Inserting us documents into collections...")
    insert_documents(df_us, "us_products", emb_fn)
    print("Inserting es documents into collections...")
    insert_documents(df_es, "es_products", emb_fn)
    print("Inserting jp documents into collections...")
    insert_documents(df_jp, "jp_products", emb_fn)


def main():
    start_time = time.time()
    repo_url = "https://github.com/jeancsil/amazon-esci-data.git"
    clone_dir = "amazon-esci-data"

    clone_repository(repo_url, clone_dir)
    product_dataset_file = f"./{clone_dir}/shopping_queries_dataset/shopping_queries_dataset_products.parquet"

    # delete if exisiting database file exists
    delete_directory(database_dir)
    os.makedirs(database_dir, exist_ok=True)
    print(f"Database directory created at {database_dir}")
    print("Processing dataset files...")
    process_data(product_dataset_file)
    print("Dataset processing complete.")
    total_time = time.time() - start_time
    print("Database initialization complete.")
    print(f"Total time taken: {total_time} seconds.")


database_dir = "./database"

if __name__ == "__main__":
    main()
