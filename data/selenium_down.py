from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup
import re
from ordered_set import OrderedSet
data = []

def fj(URL):
    options = Options()
    options.add_argument("--headless=new")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # driver.get("https://codeforces.com")
    Link_to_case = URL
    driver.get(Link_to_case)
    # driver.maximize_window()
    driver.implicitly_wait(1)
    link = driver.find_element("xpath", "//input[@value= 'Get this document in PDF']")
    # print(len(links))
    print(link)
    link.click()

for year in range(1950,1956):
    Year_URL = f"https://indiankanoon.org/browse/supremecourt/{year}/"


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
                    links = f'https://indiankanoon.org//doc/{number}/'
                    Link_container.append(links)
                    numbers.append(number)

            for URL in Link_container:
                fj(URL)
