#Code to fetch data for any given year by - Dhruv Talan
import requests
from bs4 import BeautifulSoup
import re
from ordered_set import OrderedSet
data = []
for Year in range(1950, 2024):

 Year_URL = f"https://indiankanoon.org/browse/supremecourt/{Year}/"



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
   if bottom_div.find('a') is not None:
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


 R = requests.get(Year_URL)
 Htmlcontent = R.content
 soup = BeautifulSoup(Htmlcontent, 'html.parser')
 Months_URL = []
 for div in soup.find_all('div', {'class': 'browselist'}):
  Months_URL.append("https://indiankanoon.org" + div.find('a')['href'].replace(" ", "%20"))

 i = 0
 for start_URL in Months_URL:
  urls = list(multi_page(start_URL))
  for URL in urls:
   i = i + 1;
   Link_container = []
   numbers = []
   R = requests.get(URL)
   HtmlContent = R.content
   soup = BeautifulSoup(HtmlContent, 'html.parser')

   for div in soup.find_all('div', {'class': 'result_title'}):
    for link in div.find_all('a'):
     number = extract_number_from_href(link.get('href'))
     links = f'https://indiankanoon.org//doc/{number}/'
     Link_container.append(links)
     numbers.append(number)

   for URL, no in zip(Link_container, numbers):
    R = requests.get(URL)
    HtmlContent = R.content
    soup = BeautifulSoup(HtmlContent, 'html.parser')
    page_div = soup.find("div", class_="judgments")
    tagline = page_div.find("div", class_="doc_title").text
    ad_doc = page_div.find("div", class_="ad_doc")
    ad_doc.decompose()
    data.append({'id': no, 'date': f"{i}/{Year}", 'tagline': tagline})
print(data)
