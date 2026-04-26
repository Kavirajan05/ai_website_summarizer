import requests

def test_jina():
    url = "https://r.jina.ai/https://www.linkedin.com/in/kavirajan05/"
    resp = requests.get(url)
    print("Status:", resp.status_code)
    print("Content snippet:", resp.text[:1000])
    
if __name__ == "__main__":
    test_jina()
