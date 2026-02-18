import streamlit as st
from lxml import etree
import os
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Mock data with multiple image variations
images = [
    "https://example.com/image1a.jpg",
    "https://example.com/image1b.jpg",
    "https://example.com/image2a.jpg",
    "https://example.com/image2b.jpg",
]

# Function to parse XML and handle errors
def parse_xml(xml_content):
    try:
        tree = etree.fromstring(xml_content.encode('utf-8'))
        return tree
    except etree.XMLSyntaxError as e:
        logging.error(f"XML Syntax Error: {e}")
        st.error("There was an error parsing the XML data.")
        return None

# Main Streamlit Application
def main():
    st.title("My Streamlit App")

    xml_data = st.text_area("Input XML Data:")
    if st.button("Parse XML"):
        tree = parse_xml(xml_data)
        if tree is not None:
            st.success("XML parsed successfully!")
            # Example usage with the mock data
            image_choice = random.choice(images)
            st.image(image_choice)
        else:
            st.error("Failed to parse XML.")

if __name__ == "__main__":
    main()