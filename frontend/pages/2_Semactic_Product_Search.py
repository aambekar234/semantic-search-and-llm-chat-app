import os
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import time

# set page related configurations
st.set_page_config(
    page_title="LLM-RAG-DEMO",
    page_icon="🧊",
)
st.title("🔍 Semantic Product Search")


# llm_service search api endpoint
API_URL = "http://127.0.0.1:8001/search"
query = st.text_input("Enter your search query:")

locale = st.sidebar.selectbox("Select Locale", ["us", "es", "jp"])

if st.button("Search"):
    if query:
        # Make a request to the FastAPI endpoint
        start = time.time()
        response = requests.post(API_URL, json={"text": query, "locale": locale})
        total_time = time.time() - start

        if response.status_code == 200:
            # Parse the JSON response
            products = response.json()

            # Convert to DataFrame for display
            df = pd.DataFrame(products)

            # Display the results in a table
            st.write(f"Query took {total_time:.3f} seconds. Top 5 Search Results:")

            # Construct and display the markdown for each product
            for _, row in df.iterrows():

                product_markdown = f"#### Title: {row['product_title']}\n"
                product_markdown += f"##### Product ID: {row['product_id']}\n"
                product_markdown += (
                    f"###### Description: {row['product_description']}\n"
                )
                product_markdown += f"###### Features: {row['product_bullet_point']}\n"
                product_markdown += f"###### Brand: {row['product_brand']}\n"
                product_markdown += f"###### Color: {row['product_color']}\n"
                st.markdown(product_markdown)
                st.markdown("---")
        else:
            st.error("Error retrieving search results.")
    else:
        st.warning("Please enter a search query.")
