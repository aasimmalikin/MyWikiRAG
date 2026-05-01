import requests
from datetime import date

BASE_URL = "https://en.wikipedia.org/api/rest_v1"
SEARCH_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "user-agent": "MywikiApp/1.0 (aasimmallikk@gmail.com)"
}

def search_articles(query, limit=5):
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "origin": "*"
    }
    response = requests.get(SEARCH_URL, params = params, headers= HEADERS)
    response.raise_for_status()
    return response.json()["query"]["search"]

def get_article_summary(title):
    encoded_title = title.replace(" ", "_")
    url = f"{BASE_URL}/page/summary/{requests.utils.quote(encoded_title)}"
    response = requests.get(url, headers = HEADERS)
    response.raise_for_status()
    return response.json()

def get_article_content(title, intro_only = False):
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": intro_only,
        "explaintext": True, 
        "titles": title,
        "format": "json",
        "origin": "*"
    }
    response = requests.get(SEARCH_URL, params = params, headers = HEADERS )
    response.raise_for_status()
    pages = response.json()["query"]["pages"]
    page = list(pages.values())[0]
    return page



def get_todays_featured_article():
    today = date.today()
    yyyy = today.strftime("%Y")
    mm = today.strftime("%m")
    dd = today.strftime("%d")
    url = f"{BASE_URL}/feed/featured/{yyyy}/{mm}/{dd}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("tfa")

def get_random_article():
    url = f"{BASE_URL}/page/random/summary"
    response = requests.get(url, headers = HEADERS)
    response.raise_for_status()
    return response.json()

def get_article_section(title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "sections",
        "format": "json",
        "origin": "*"
    }
    response = requests.get(SEARCH_URL, params = params, headers = HEADERS)
    response.raise_for_status()
    return response.json()["parse"]["sections"]

