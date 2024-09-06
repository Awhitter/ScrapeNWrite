import streamlit as st
from openai import OpenAI
import os
import sys
import site
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Add the user-specific site-packages directory to Python path
user_site_packages = site.getusersitepackages()
sys.path.append(user_site_packages)

from prompts import generate_prompt
from spider_graph import spider_graph_analysis, download_nltk_data
import sqlite3

# Health check route
def health_check():
    return "OK"

# Main Streamlit app
def main():
    try:
        # Download NLTK data
        download_nltk_data()

        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize database
        conn = sqlite3.connect('content_analysis.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_results
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      task TEXT,
                      urls TEXT,
                      audience TEXT,
                      result TEXT)''')
        conn.commit()

        st.set_page_config(page_title="Advanced AI Content Assistant", layout="wide")

        st.sidebar.title("Advanced AI Content Assistant")
        st.sidebar.image("https://your-logo-url-here.com", width=200)

        # Main task selection
        task = st.sidebar.selectbox("Choose a task", [
            "Tone and Style Analysis",
            "Write a Factual Wikipedia-like Paper",
            "Write Tweets from Content",
            "Write a Blog Post Outline",
            "Turn Content into a Listicle",
            "Write an Instagram Post"
        ])

        # User inputs
        audience = st.sidebar.text_input("Target Audience (required)")
        topic = st.sidebar.text_input("Topic (optional)")
        timeframe = st.sidebar.text_input("Timeframe (optional)")

        # Areas of emphasis
        emphasis_areas = st.sidebar.multiselect("Areas of Emphasis", [
            "Capturing all concrete info",
            "A few quotes or phrases",
            "Getting style and tone",
            "Format",
            "Marketing and copywriting",
            "Get for LLM (non-human, massive info density)"
        ])

        # Model selection (fixed to gpt-4o-2024-08-06)
        model = "gpt-4o-2024-08-06"

        st.title("Advanced AI Content Assistant")

        # Input for URLs and text content
        urls = st.text_area("Enter URLs (one per line)")
        text_content = st.text_area("Or enter text content directly")

        max_tokens = 16000  # Increased to 16000

        if st.button("Generate Content"):
            if not client.api_key:
                st.error("Please set your OpenAI API key as an environment variable.")
            elif not audience:
                st.error("Please specify the target audience.")
            elif not (urls or text_content):
                st.error("Please enter at least one URL or some text content.")
            else:
                with st.spinner("Analyzing content..."):
                    spider_graph_results = spider_graph_analysis(urls, text_content)
                    
                    st.subheader("Spider Graph Analysis")
                    st.text(spider_graph_results)
                    
                    prompt = generate_prompt(task, urls, text_content, audience, topic, timeframe, emphasis_areas, spider_graph_results)
                    
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": "You are a highly skilled AI content analyst and creator. Your task is to provide detailed, specific, and comprehensive content based on the given inputs. Each output should build upon previous analyses and results, creating a coherent and in-depth final product."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=max_tokens
                        )
                        
                        result = response.choices[0].message.content.strip()
                        
                        # Save result to database
                        c.execute("INSERT INTO analysis_results (task, urls, audience, result) VALUES (?, ?, ?, ?)",
                                  (task, urls, audience, result))
                        conn.commit()
                        
                        st.subheader("Generated Content")
                        st.markdown(result)
                        
                    except Exception as e:
                        logger.error(f"An error occurred: {str(e)}")
                        logger.error(traceback.format_exc())
                        st.error(f"An error occurred: {str(e)}")

        st.sidebar.markdown("---")
        st.sidebar.markdown("© 2023 HLT. All rights reserved.")

        # Debug Information
        if st.sidebar.checkbox("Show Debug Info"):
            st.sidebar.json({
                "Task": task,
                "Model": model,
                "URLs": urls,
                "Text Content": text_content,
                "Audience": audience,
                "Topic": topic,
                "Timeframe": timeframe,
                "Emphasis Areas": emphasis_areas,
                "Max Tokens": max_tokens
            })

        conn.close()

    except Exception as e:
        logger.error(f"An error occurred in the main app: {str(e)}")
        logger.error(traceback.format_exc())
        st.error(f"An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()