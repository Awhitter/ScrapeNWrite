import streamlit as st
from openai import OpenAI
import os
import sys
import site
import logging
import traceback
import markdown
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Add the user-specific site-packages directory to Python path
user_site_packages = site.getusersitepackages()
sys.path.append(user_site_packages)

try:
    from prompts import generate_prompt
    from spider_graph import spider_graph_analysis, download_nltk_data
    import sqlite3
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    logger.error(traceback.format_exc())
    st.error("An error occurred while importing required modules. Please check the logs for more information.")

def export_content(content, format_type):
    """Export content in various formats"""
    if format_type == "markdown":
        return content
    elif format_type == "txt":
        # Strip markdown formatting
        return re.sub(r'[#*`]', '', content)
    elif format_type == "html":
        return markdown.markdown(content)
    return content

def display_export_options(result):
    """Display export options for the generated content"""
    st.markdown("---")
    st.markdown("### 📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Choose format",
            ["markdown", "txt", "html"]
        )
    
    with col2:
        if st.button("📄 Export"):
            exported_content = export_content(result, export_format)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_export_{timestamp}.{export_format}"
            
            st.download_button(
                label="💾 Download File",
                data=exported_content,
                file_name=filename,
                mime=f"text/{export_format}"
            )

def main(port=8080):
    try:
        st.set_page_config(
            page_title="Advanced AI Content Assistant",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
            <style>
            .sidebar .sidebar-content {
                background-color: #f8f9fa;
            }
            .stButton>button {
                width: 100%;
                background-color: #5C4B9B;
                color: white;
            }
            .stButton>button:hover {
                background-color: #4a3b89;
            }
            .export-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Download NLTK data - moved after page config
        if not download_nltk_data():
            st.error("Failed to set up required dependencies. Please check the logs for more information.")
            return

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

        # Sidebar with new logo
        st.sidebar.image(
            "https://res.cloudinary.com/dq9xmts6p/image/upload/v1730402341/248790683_95bb6dd3-81dc-417b-913d-70f31924595a_ufoyzn.svg",
            width=150
        )
        st.sidebar.title("Content Assistant")

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

        # Enhanced input section
        input_type = st.radio(
            "Choose input type",
            ["Text/URLs", "File Upload"],
            horizontal=True
        )
        
        if input_type == "Text/URLs":
            urls = st.text_area("Enter URLs (one per line)")
            text_content = st.text_area("Or enter text content directly")
        else:  # File Upload
            uploaded_file = st.file_uploader(
                "Upload your content file",
                type=['txt', 'md']
            )
            if uploaded_file:
                text_content = uploaded_file.getvalue().decode()
                urls = ""
            else:
                text_content = ""
                urls = ""

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
                    try:
                        spider_graph_results = spider_graph_analysis(urls, text_content)
                        
                        st.subheader("Spider Graph Analysis")
                        st.text(spider_graph_results)
                        
                        prompt = generate_prompt(task, urls, text_content, audience, topic, timeframe, emphasis_areas, spider_graph_results)
                        
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
                        
                        # Display export options
                        display_export_options(result)
                        
                    except Exception as e:
                        logger.error(f"An error occurred during content generation: {str(e)}")
                        logger.error(traceback.format_exc())
                        st.error(f"An error occurred during content generation. Please check the logs for more information.")

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
                "Max Tokens": max_tokens,
                "Port": port
            })

        conn.close()

    except Exception as e:
        logger.error(f"An error occurred in the main app: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("""
        An unexpected error occurred. Please try the following:
        1. Make sure you have Python 3.7+ installed
        2. Run: pip install nltk requests beautifulsoup4
        3. Check the logs for more information
        """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    main(port=port)
