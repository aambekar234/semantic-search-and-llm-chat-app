import os
import re
import chromadb
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings


class CustomEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function that uses SentenceTransformer to embed documents."""

    def __init__(self, model):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()


class DefChromaEF(Embeddings):
    """Default Chroma Embedding Function wrapper for CustomEmbeddingFunction."""

    def __init__(self, ef):
        self.ef = ef

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, query):
        return self.ef([query])[0]


class DB_Service:
    """
    A class that provides database services for semantic search and retrieval.
    """

    def __init__(self):
        self.model = SentenceTransformer(self._get_embedding_mode_name())
        self.emb_fn = CustomEmbeddingFunction(self.model)

        self.client = chromadb.HttpClient(
            host=os.environ["db_host"], port=os.environ["db_port"]
        )

        self.collection_names = {}
        self.collection_names["us"] = "us_products"
        self.collection_names["es"] = "es_products"
        self.collection_names["jp"] = "jp_products"

        self.collections = {}
        for locale in self.collection_names:
            self.collections[locale] = self.client.get_collection(
                name=self.collection_names[locale], embedding_function=self.emb_fn
            )

    def _get_embedding_mode_name(self):
        """
        Retrieves the embedding model name from environment variables.

        Returns:
            str: The embedding model name.

        Raises:
            Exception: If the embedding model name is not found in the environment variables.
        """
        try:
            return os.environ["embedding_model_name"]
        except:
            raise Exception("Embedding model name not found in environment variables..")

    def search(self, query: str, locale: str):
        """
        Searches the database for documents matching the query in the specified locale.

        Args:
            query (str): The search query.
            locale (str): The locale to search in.

        Returns:
            list: The list of matching documents.

        Raises:
            Error: If no documents are found.
            RuntimeError: If there is an error searching the database.
        """
        try:
            collection = self.collections[locale]
            response = collection.query(query_text=[query], top_k=10)
            documents = results["metadatas"][0]
            if documents:
                return documents
            raise Error("No documents found")
        except Exception as e:
            print(f"Error searching database: {e}")
            raise RuntimeError("Error searching database...")

    def clean_text(self, text):
        """
        Cleans the text by removing HTML tags, entities, markdown links, and URLs.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        # Remove HTML tags
        text = re.sub(r"<.*?>", "", text)
        # Replace HTML entities with a space
        text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
        # Remove markdown links
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        # Remove URLs
        text = re.sub(r"http\S+|www\S+", "", text)
        # Convert to lowercase
        text = text.lower()
        # Remove special characters (keep only alphanumeric and whitespace)
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text

    def format_docs(self, documents):
        """
        Formats the retrieved documents into a readable string.

        Args:
            documents (list): The list of retrieved documents.

        Returns:
            str: The formatted documents.
        """
        formatted_docs = "\nProduct catalogues:\n"
        for doc in documents:
            document = doc.metadata
            docstr = ""
            docstr += f"Product Id {document['product_id']}. \n"
            docstr += f"Title is {document['product_title']}. \n"
            docstr += f"It's color is {document['product_color']}. "
            docstr += f"It's Brand is {document['product_brand']}. "
            docstr += f"It's description says...\n {self.clean_text(document['product_description'])}.\n\n"

            formatted_docs += docstr

        return formatted_docs

    def get_retriever(self, locale: str, filter=None):
        """
        Creates a retriever object for the specified locale with an optional filter.

        Args:
            locale (str): The locale to create the retriever for.
            filter (dict, optional): The filter to apply to the retriever. Defaults to None.

        Returns:
            Retriever: The retriever object.

        Raises:
            RuntimeError: If there is an error creating the retriever.
        """
        try:
            db = Chroma(
                client=self.client,
                collection_name=self.collection_names[locale],
                embedding_function=DefChromaEF(self.emb_fn),
            )
            if filter:
                return db.as_retriever(search_kwargs={"k": 1, "filter": filter})
            return db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        except Exception as e:
            print(f"Error creating retriever: {e}")
            raise RuntimeError("Error creating retriever")
