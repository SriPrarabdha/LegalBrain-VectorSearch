import requests
from bs4 import BeautifulSoup
import re
from ordered_set import OrderedSet
data = []

with open('D:/FU/1950-1955/Json.txt','w') as f1:  #PATH
 def download_pdf(url, filename):
  response = requests.get(url)
  with open(filename, "wb") as f:
   f.write(response.content)
   f.close()

 for Year in range(1950, 1956):
  #ENTER THE YEAR RANGE
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
   i = i + 1;
   for URL in urls:
    Link_container = []
    numbers = []
    R = requests.get(URL)
    HtmlContent = R.content
    soup = BeautifulSoup(HtmlContent, 'html.parser')

    for div in soup.find_all('div', {'class': 'result_title'}):
     for link in div.find_all('a'):
      number = extract_number_from_href(link.get('href'))
      links = f'https://indiankanoon.org//doc/{number}/'  #ORIGINAL FUNCTIONS
      Link_container.append(links)
      numbers.append(number)

    for URL, no in zip(Link_container, numbers):
     R = requests.get(URL)
     HtmlContent = R.content
     soup = BeautifulSoup(HtmlContent, 'html.parser')
     page_div = soup.find("div", class_="judgments")
     tagline = page_div.find("div", class_="doc_title").text
     URL += '?type=pdf'
     code = f"{no}_{tagline}_{i}_{Year}@"  #REFRENCE FILE
     filename = f"D:/FU/1950-1955/{no}.pdf"
     download_pdf(URL, filename)  #FUNCTION CALLED
     f1.write(code)
 f1.close()
