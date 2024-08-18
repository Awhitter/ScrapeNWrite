import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Load environment variables
load_dotenv()

def fetch_content(url):
    try:
        # Add scheme if not present
        if not urlparse(url).scheme:
            url = 'https://' + url
        
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('body')
        return main_content.get_text() if main_content else ""
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""

def fetch_multiple_urls(urls):
    return {url: fetch_content(url) for url in urls}

def process_text(text, task, prompt, audience=None, topic=None):
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    if task == "summarize":
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        return chain.run(docs)
    elif task == "blog_content":
        prompt_template = PromptTemplate(
            input_variables=["text", "audience", "topic"],
            template=f"Based on the following text, generate engaging blog post content for {{audience}} about {{topic}}. Include great quotes, insights, and an outline of the most resonant points.\n\nText: {{text}}\n\nBlog Content:"
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        results = [chain.run(text=chunk, audience=audience, topic=topic) for chunk in chunks]
        return "\n\n".join(results)
    elif task == "quotes":
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="Extract the most impactful and insightful quotes from the following text:\n\nText: {text}\n\nQuotes:"
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        results = [chain.run(text=chunk) for chunk in chunks]
        return "\n\n".join(results)

def advanced_ai_assistant():
    while True:
        print("\nAdvanced AI Assistant")
        print("1. Analyze Single Web Page")
        print("2. Analyze Multiple Web Pages")
        print("3. Generate Blog Post Content")
        print("4. Extract Quotes")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            url = input("Enter the URL to analyze: ")
            task = input("Choose task (summarize/blog_content/quotes): ")
            content = fetch_content(url)
            if task == "blog_content":
                audience = input("Enter the target audience: ")
                topic = input("Enter the blog topic: ")
                result = process_text(content, task, "", audience, topic)
            else:
                result = process_text(content, task, "")
            print("\nResult:")
            print(result)
        elif choice == "2":
            urls = input("Enter the URLs to analyze (comma-separated): ").split(',')
            task = input("Choose task (summarize/blog_content/quotes): ")
            contents = fetch_multiple_urls(urls)
            combined_content = "\n\n".join(contents.values())
            if task == "blog_content":
                audience = input("Enter the target audience: ")
                topic = input("Enter the blog topic: ")
                result = process_text(combined_content, task, "", audience, topic)
            else:
                result = process_text(combined_content, task, "")
            print("\nResult:")
            print(result)
        elif choice == "3":
            urls = input("Enter the URLs for blog research (comma-separated): ").split(',')
            audience = input("Enter the target audience: ")
            topic = input("Enter the blog topic: ")
            contents = fetch_multiple_urls(urls)
            combined_content = "\n\n".join(contents.values())
            result = process_text(combined_content, "blog_content", "", audience, topic)
            print("\nBlog Post Content:")
            print(result)
        elif choice == "4":
            urls = input("Enter the URLs to extract quotes from (comma-separated): ").split(',')
            contents = fetch_multiple_urls(urls)
            combined_content = "\n\n".join(contents.values())
            result = process_text(combined_content, "quotes", "")
            print("\nExtracted Quotes:")
            print(result)
        elif choice == "5":
            print("Thank you for using the Advanced AI Assistant. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    advanced_ai_assistant()
