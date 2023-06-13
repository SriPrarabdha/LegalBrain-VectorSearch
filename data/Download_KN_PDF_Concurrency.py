import requests
from bs4 import BeautifulSoup
import re
from ordered_set import OrderedSet
from concurrent.futures import ThreadPoolExecutor

data = []
base_path = "C:/TensorLabsAI/Judgment Data/1963Data/"
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
def download_pdf(session, url, filename):
    response = session.get(url,headers=headers)
    with open(filename, "wb") as f:
        f.write(response.content)

def extract_number_from_href(href):
    pattern = r"/docfragment/(\d+)/"
    match = re.search(pattern, href)
    if match:
        return match.group(1)
    else:
        return None

def multi_page(session, URL):
    url = OrderedSet()
    while True:
        if URL not in url:
            pass
        else:
            break
        url.add(URL)
        response = session.get(URL)
        HtmlContent = response.content
        soup = BeautifulSoup(HtmlContent, 'html.parser')
        bottom_div = soup.find('div', {'class': 'bottom'})
        if bottom_div is not None:
            if bottom_div.find('a') is not None:
                URL = "https://indiankanoon.org" + bottom_div.find_all('a')[-1]['href']
    return url

def fetch_pdf(Year):
    print(Year)
    Year_URL = f"https://indiankanoon.org/browse/supremecourt/{Year}/"
    session = requests.Session()
    R = session.get(Year_URL)
    Htmlcontent = R.content
    soup = BeautifulSoup(Htmlcontent, 'html.parser')
    Months_URL = []
    for div in soup.find_all('div', {'class': 'browselist'}):
        Months_URL.append("https://indiankanoon.org" + div.find('a')['href'].replace(" ", "%20"))

    i = 0
    for start_URL in Months_URL:
        urls = list(multi_page(session, start_URL))
        i += 1
        link_container = []
        numbers = []
        for URL in urls:
            R = session.get(URL)
            HtmlContent = R.content
            soup = BeautifulSoup(HtmlContent, 'html.parser')

            for div in soup.find_all('div', {'class': 'result_title'}):
                for link in div.find_all('a'):
                    number = extract_number_from_href(link.get('href'))
                    links = f'https://indiankanoon.org//doc/{number}/'
                    link_container.append(links)
                    numbers.append(number)

        with ThreadPoolExecutor(max_workers=1) as executor:
            results = []
            for URL, no in zip(link_container, numbers):
                R = session.get(URL,headers=headers)
                HtmlContent = R.content
                soup = BeautifulSoup(HtmlContent, 'html.parser')
                page_div = soup.find("div", class_="judgments")
                tagline = page_div.find("div", class_="doc_title").text
                URL += '?type=pdf'
                code = f"{no}_{tagline}_{i}_{Year}@"  # REFERENCE FILE
                filename = f"{base_path}{no}.pdf"
                results.append(executor.submit(download_pdf, session, URL, filename))
                data.append(code)

            # Wait for all the download tasks to complete
            for result in results:
                result.result()

if __name__ == '__main__':
    with open(f'{base_path}Json.txt', 'w') as f1:
        year_range = range(1963, 1964)
        for Year in year_range:
            fetch_pdf(Year)

        for item in data:
            f1.write(item + '@')

    print("All PDFs downloaded successfully.")
