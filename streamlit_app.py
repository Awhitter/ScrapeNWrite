import streamlit as st
from openai import OpenAI
import os
from prompts import generate_prompt, generate_spider_graph_prompt
import sqlite3

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

task = st.sidebar.selectbox("Choose a task", [
    "Info Dense Extraction",
    "Summary Generation",
    "Deep Sentiment Analysis",
    "Headline and Copywriting Extraction",
    "Structure Capture",
    "Keyword Summarization"
])

model = st.sidebar.selectbox("Select AI Model", ["gpt-4", "gpt-3.5-turbo"])

st.title("Advanced AI Content Assistant")

col1, col2 = st.columns(2)

with col1:
    urls = st.text_area("Enter URLs (one per line)")
    audience = st.text_input("Target Audience")
    timeframe = st.text_input("Timeframe (optional)")

with col2:
    options = st.multiselect("Additional Analysis Options", [
        "Writing Style",
        "Audience Engagement",
        "Data Visualization",
        "SEO Optimization",
        "Content Strategy"
    ])

max_tokens = st.sidebar.slider("Max Tokens", 1000, 50000, 15000)

if st.button("Generate Content"):
    if not client.api_key:
        st.error("Please set your OpenAI API key as an environment variable.")
    elif not urls or not audience:
        st.error("Please enter URLs and specify the target audience.")
    else:
        with st.spinner("Analyzing content..."):
            prompt = generate_prompt(task, urls, audience, timeframe, options)
            
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a highly skilled AI content analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                
                result = response.choices[0].message.content.strip()
                
                # Save result to database
                c.execute("INSERT INTO analysis_results (task, urls, audience, result) VALUES (?, ?, ?, ?)",
                          (task, urls, audience, result))
                conn.commit()
                
                st.subheader("Analysis Result")
                st.markdown(result)
                
                st.subheader("Spider Graph Analysis")
                spider_prompt = generate_spider_graph_prompt([task, "Content Strategy", "SEO Optimization"], urls, audience)
                spider_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a highly skilled AI content analyst."},
                        {"role": "user", "content": spider_prompt}
                    ],
                    max_tokens=max_tokens // 2
                )
                st.markdown(spider_response.choices[0].message.content.strip())
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.markdown("© 2023 HLT. All rights reserved.")

# Debug Information
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.json({
        "Task": task,
        "Model": model,
        "URLs": urls,
        "Audience": audience,
        "Timeframe": timeframe,
        "Options": options,
        "Max Tokens": max_tokens
    })

conn.close()