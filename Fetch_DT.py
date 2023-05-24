#Code to fetch data for any given year by - Dhruv Talan
import requests
from bs4 import BeautifulSoup
import re
from ordered_set import OrderedSet

number=input("Enter the year you want to fetch the data for : ")
Year_URL=f"https://indiankanoon.org/browse/supremecourt/{number}/"

def multi_page(URL):
 url = OrderedSet()
 while True:
  if URL not in url:
   pass
  else:
   break
  url.add(URL)
  R = requests.get(URL)
  HtmlContent = R.content
  # HTML CONTENT HAI YEH RAW
  soup = BeautifulSoup(HtmlContent, 'html.parser')
  bottom_div = soup.find('div', {'class': 'bottom'})
  URL = "https://indiankanoon.org" + bottom_div.find_all('a')[-1]['href']
 return url

def extract_number_from_href(href):
  pattern = r"/docfragment/(\d+)/"
  match = re.search(pattern, href)
  if match:
   number = match.group(1)
   return number
  else:
   return None




R=requests.get(Year_URL)
Htmlcontent=R.content
soup=BeautifulSoup(Htmlcontent,'html.parser')
Months_URL=[]
for div in soup.find_all('div',{'class':'browselist'}):
 Months_URL.append("https://indiankanoon.org"+div.find('a')['href'].replace(" ","%20"))


for start_URL in Months_URL:
 urls = list(multi_page(start_URL))
 for URL in urls:
  Link_container = []
  R = requests.get(URL)
  HtmlContent = R.content
  soup = BeautifulSoup(HtmlContent, 'html.parser')

  for div in soup.find_all('div', {'class': 'result_title'}):
   for link in div.find_all('a'):
    number = extract_number_from_href(link.get('href'))
    links = f'https://indiankanoon.org//doc/{number}/'
    Link_container.append(links)


  for URL in Link_container:
   R = requests.get(URL)
   HtmlContent = R.content
   soup = BeautifulSoup(HtmlContent, 'html.parser')
   page_div = soup.find("div", class_="judgments")
   ad_doc = page_div.find("div", class_="ad_doc")
   ad_doc.decompose()
   print(page_div.text)
