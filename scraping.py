from bs4 import BeautifulSoup
import requests

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
url='https://www.google.com/search?q=pizza&ie=utf-8&oe=utf-8&num=10'
html = requests.get(url,headers=headers)
print(html.status_code)

soup = BeautifulSoup(html.text, 'html.parser')
allData = soup.find_all("div",{"class":"gb_L"})