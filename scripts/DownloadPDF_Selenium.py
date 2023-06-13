from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless=new")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# driver.get("https://codeforces.com")
Link_to_case = "https://indiankanoon.org/doc/1413471/"
driver.get(Link_to_case)
# driver.maximize_window()

link = driver.find_element("xpath", "//input[@value= 'Get this document in PDF']")
# print(len(links))
print(link)
link.click()

#run a loop over this code and download pdf of all judgments 

# Keep all those pdfs in a zip file or folder in your local machine do not push them to repo

# Use from PyPDF2 import PdfReader to read all those pdf

# Put togather the data in the JSON form as prescribed earlier

# data = [{"id" : 43242 , "tagline" : "  " , "date" :  ,"judgment" : " "}]