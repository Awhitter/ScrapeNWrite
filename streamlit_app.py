import streamlit as st
import os

# Set page config
st.set_page_config(page_title="Simple Streamlit App", layout="wide")

# Main content
st.title("Welcome to My Streamlit App")
st.write("This is a simple Streamlit app deployed on Railway.")

# Display environment variables (for debugging)
st.subheader("Environment Variables:")
for key, value in os.environ.items():
    st.text(f"{key}: {value}")

# Add a simple interactive element
name = st.text_input("Enter your name")
if name:
    st.write(f"Hello, {name}!")