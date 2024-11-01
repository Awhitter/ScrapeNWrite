import streamlit as st
from openai import OpenAI
import os
import sys
import site
import logging
import traceback
import re
from datetime import datetime
from io import BytesIO
import plotly.graph_objects as go

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

def display_spider_graph(spider_results):
    """Create an interactive spider graph visualization using Plotly"""
    try:
        # Extract metrics from the spider graph results
        metrics = {
            "Key Points": len(re.findall(r'- ', spider_results)),  # Count bullet points
            "Tone": 1 if "Positive" in spider_results else (-1 if "Negative" in spider_results else 0),
            "Sentence Length": float(re.search(r'Average sentence length: (\d+\.?\d*)', spider_results).group(1)),
            "Paragraph Length": float(re.search(r'Average paragraph length: (\d+\.?\d*)', spider_results).group(1)),
            "Paragraphs": float(re.search(r'Number of paragraphs: (\d+)', spider_results).group(1))
        }
        
        # Create the spider graph
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line=dict(color='#5C4B9B')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[min(values), max(values)]
                )
            ),
            showlegend=False,
            height=400,  # Fixed height
            margin=dict(l=40, r=40, t=20, b=20),  # Reduced margins
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Display the graph
        st.plotly_chart(fig, use_container_width=True)
        
        # Display the text analysis below the graph
        st.markdown("### Detailed Analysis")
        st.text(spider_results)
        
    except Exception as e:
        logger.error(f"Error in spider graph visualization: {str(e)}")
        st.warning("Unable to display visualization. Showing raw analysis:")
        st.text(spider_results)

def export_content(content, format_type):
    """Export content in various formats"""
    try:
        if format_type in ["txt", "markdown"]:
            return content.encode('utf-8')
        elif format_type == "pdf":
            try:
                import pdfkit
                options = {
                    'page-size': 'A4',
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm',
                    'encoding': "UTF-8",
                }
                return pdfkit.from_string(content, False, options=options)
            except Exception as e:
                st.error(f"PDF export failed: {str(e)}. Make sure wkhtmltopdf is installed.")
                return None
        elif format_type == "mp3":
            try:
                from gtts import gTTS
                audio = BytesIO()
                tts = gTTS(text=re.sub(r'[#*`]', '', content), lang='en')
                tts.write_to_fp(audio)
                audio.seek(0)
                return audio.read()
            except Exception as e:
                st.error(f"MP3 export failed: {str(e)}")
                return None
        elif format_type == "docx":
            try:
                from docx import Document
                doc = Document()
                doc.add_paragraph(content)
                docx = BytesIO()
                doc.save(docx)
                docx.seek(0)
                return docx.read()
            except Exception as e:
                st.error(f"DOCX export failed: {str(e)}")
                return None
    except Exception as e:
        logger.error(f"Export error for format {format_type}: {str(e)}")
        st.error(f"Export failed: {str(e)}")
        return None
    
    return None

def display_export_options(result):
    """Display simplified export options"""
    st.markdown("### 📤 Export Options")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        export_format = st.selectbox(
            "Format",
            ["markdown", "txt", "pdf", "docx", "mp3"]
        )
    
    with col2:
        st.markdown("#")  # Spacing
        if st.button("💾 Export", type="primary", use_container_width=True):
            with st.spinner(f"Preparing {export_format.upper()}..."):
                exported_content = export_content(result, export_format)
                if exported_content is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"content_export_{timestamp}.{export_format}"
                    
                    mime_types = {
                        "txt": "text/plain",
                        "pdf": "application/pdf",
                        "mp3": "audio/mpeg",
                        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "markdown": "text/markdown"
                    }
                    
                    st.download_button(
                        "📥 Download",
                        data=exported_content,
                        file_name=filename,
                        mime=mime_types.get(export_format, "text/plain"),
                        use_container_width=True
                    )
                    st.success(f"✅ {export_format.upper()} export ready!")

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
            .stTabs [data-baseweb="tab"] {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            .stTabs [data-baseweb="tab-panel"] {
                padding: 1rem 0;
            }
            .stButton > button {
                width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Download NLTK data
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

        # Model selection
        model = "gpt-4o-2024-08-06"

        st.title("Advanced AI Content Assistant")

        # Input section
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

        max_tokens = 16000

        if st.button("Generate Content"):
            if not urls and not text_content:
                st.error("Please enter at least one URL or some text content.")
            else:
                try:
                    tab1, tab2 = st.tabs(["Analysis", "Generated Content"])
                    
                    with tab1:
                        with st.spinner("Analyzing content..."):
                            spider_results = spider_graph_analysis(urls, text_content)
                            display_spider_graph(spider_results)
                    
                    with tab2:
                        with st.spinner("Generating content..."):
                            prompt = generate_prompt(task, urls, text_content, audience, topic, timeframe, emphasis_areas, spider_results)
                            response = client.chat.completions.create(
                                model=model,
                                messages=[
                                    {"role": "system", "content": "You are a highly skilled AI content analyst and creator..."},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=max_tokens
                            )
                            
                            result = response.choices[0].message.content.strip()
                            
                            # Save to database
                            c.execute("INSERT INTO analysis_results (task, urls, audience, result) VALUES (?, ?, ?, ?)",
                                      (task, urls, audience, result))
                            conn.commit()
                            
                            st.markdown(result)
                            display_export_options(result)
                            
                except Exception as e:
                    logger.error(f"An error occurred: {str(e)}")
                    logger.error(traceback.format_exc())
                    st.error("An error occurred. Please check the logs for more information.")

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
