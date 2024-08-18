import sys
import os
import site

# Add the user-specific site-packages directory to Python path
user_site_packages = site.getusersitepackages()
sys.path.append(user_site_packages)

import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import ssl
import logging

# Disable SSL certificate verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_nltk_data():
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    os.environ['NLTK_DATA'] = nltk_data_dir

    required_packages = ['punkt', 'stopwords', 'punkt_tab']
    
    for package in required_packages:
        try:
            nltk.data.find(f'tokenizers/{package}')
            logging.info(f"{package} already downloaded.")
        except LookupError:
            logging.info(f"Downloading {package}...")
            try:
                nltk.download(package, quiet=True)
                logging.info(f"{package} downloaded successfully.")
            except Exception as e:
                logging.error(f"Failed to download {package}: {str(e)}")
                return False
    
    logging.info("NLTK data download process completed.")
    return True

def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")
        return ""

def preprocess_text(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and word not in stop_words]
    return sentences, words

def extract_key_points(sentences, words, num_points=5):
    word_freq = Counter(words)
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_freq[word]
                else:
                    sentence_scores[sentence] += word_freq[word]
    
    key_points = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_points]
    return key_points

def analyze_tone(text):
    positive_words = set(['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful'])
    negative_words = set(['bad', 'poor', 'negative', 'terrible', 'awful', 'horrible'])
    
    words = word_tokenize(text.lower())
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"

def analyze_style(text):
    sentences = sent_tokenize(text)
    avg_sentence_length = sum(len(word_tokenize(sentence)) for sentence in sentences) / max(len(sentences), 1)
    
    paragraphs = text.split('\n\n')
    avg_paragraph_length = sum(len(sent_tokenize(paragraph)) for paragraph in paragraphs) / max(len(paragraphs), 1)
    
    return {
        "avg_sentence_length": avg_sentence_length,
        "avg_paragraph_length": avg_paragraph_length,
        "num_paragraphs": len(paragraphs)
    }

def spider_graph_analysis(urls, text_content):
    if not download_nltk_data():
        logging.error("Failed to download NLTK data. Aborting analysis.")
        return "Error: NLTK data download failed. Please check your internet connection and try again."

    all_text = text_content
    for url in urls.split('\n'):
        if url.strip():
            all_text += " " + scrape_content(url)
    
    sentences, words = preprocess_text(all_text)
    key_points = extract_key_points(sentences, words)
    tone = analyze_tone(all_text)
    style = analyze_style(all_text)
    
    summary = f"""
    Spider Graph Analysis Summary:
    
    1. Key Points:
    {' '.join(f'- {point}' for point in key_points)}
    
    2. Tone: {tone}
    
    3. Writing Style:
    - Average sentence length: {style['avg_sentence_length']:.2f} words
    - Average paragraph length: {style['avg_paragraph_length']:.2f} sentences
    - Number of paragraphs: {style['num_paragraphs']}
    
    4. Word Frequency (top 10):
    {' '.join(f'{word}: {count}' for word, count in Counter(words).most_common(10))}
    """
    
    return summary

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    text_content = "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans."
    
    print(f"Analyzing URL: {url}")
    print(f"Analyzing text: {text_content}")
    
    result = spider_graph_analysis(url, text_content)
    print(result)