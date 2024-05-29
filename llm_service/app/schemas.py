from pydantic import BaseModel


class UserQuery(BaseModel):
    """
    Represents a user query.

    Attributes:
        text (str): The text of the user query.
    """

    text: str


class Search_Schema(BaseModel):
    """
    Represents a search schema.

    Attributes:
        text (str): The text to search.
        locale (str): The locale for the search (default is "us").
    """

    text: str
    locale: str = "us"


class ProductSchema(BaseModel):
    """
    Represents a product schema.

    Attributes:
        product_id (str): The ID of the product.
        product_title (str): The title of the product.
        product_description (str, optional): The description of the product (default is None).
        product_bullet_point (str, optional): The bullet point of the product (default is None).
        product_brand (str, optional): The brand of the product (default is None).
        product_color (str, optional): The color of the product (default is None).
    """

    product_id: str
    product_title: str
    product_description: str = None
    product_bullet_point: str = None
    product_brand: str = None
    product_color: str = None
