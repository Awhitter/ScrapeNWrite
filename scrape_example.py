import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Function to fetch and parse content
def fetch_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract the main content (adjust selector as needed)
    main_content = soup.find('div', {'id': 'mw-content-text'})
    return main_content.get_text() if main_content else ""

# Initialize OpenAI API
llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

# Set up the summarization prompt
prompt = "Summarize the main applications of artificial intelligence based on the following content:"
source = "https://en.wikipedia.org/wiki/Artificial_intelligence"

# Fetch the content
content = fetch_content(source)

# Split the content into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=200,
    length_function=len
)
chunks = text_splitter.split_text(content)

# Convert chunks to Document objects
docs = [Document(page_content=chunk) for chunk in chunks]

# Create a summarization chain
chain = load_summarize_chain(llm, chain_type="map_reduce")

# Run the summarization
summary = chain.run(docs)

# Print the summary
print(summary)