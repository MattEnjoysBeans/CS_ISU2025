import requests
import json

def searchQuery(arg):
    url = "https://google.serper.dev/search"

    payload = {
    "q": arg
    }
    headers = {
    'X-API-KEY': '10a78323c5cfc2f092fb4061be145a3599cc2435',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    searchResults = response.json()
    for result in searchResults.get("organic", []):
        resultTitle = result.get("title")
        resultLink = result.get("link")
        return [resultTitle, resultLink]
