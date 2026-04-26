import requests
import json

def test_allorigins():
    url = "https://www.linkedin.com/in/kavirajan05/"
    api_url = f"https://api.allorigins.win/get?url={url}"
    resp = requests.get(api_url)
    data = resp.json()
    print("Status:", resp.status_code)
    print("Contents:", data.get('contents', '')[:500])

if __name__ == "__main__":
    test_allorigins()
