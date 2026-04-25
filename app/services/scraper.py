import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url: str) -> str:
    """
    Scrapes the website and extracts page title, meta description, standard headings, and paragraphs.
    Cleans the text and limits it to ~4000 words.
    """
    try:
        # Define headers to mimic a normal browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        # Adding a timeout constraint
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            tag.decompose()
            
        # Extract title
        title = soup.title.string if soup.title else "No Title Found"
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and 'content' in meta_tag.attrs:
            meta_desc = meta_tag['content']
            
        # Extract headings and paragraphs
        elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        content_lines = []
        for el in elements:
            text = el.get_text(strip=True)
            if text:
                content_lines.append(f"{el.name.upper()}: {text}")
                
        # Combine
        full_text = f"TITLE: {title}\n"
        if meta_desc:
            full_text += f"META DESCRIPTION: {meta_desc}\n"
        full_text += "\n".join(content_lines)
        
        # Clean up whitespace
        full_text = re.sub(r'\n+', '\n', full_text)
        
        # Limit the text to ~4000 words to be token-safe
        words = full_text.split()
        if len(words) > 4000:
            full_text = " ".join(words[:4000])
            
        return full_text
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to scrape website: {str(e)}")
