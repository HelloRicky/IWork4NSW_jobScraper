from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import urllib2
from math import ceil
from collections import defaultdict

## initial
START_PAGE=1

TIMEOUT = 20 # seconds, browser timetout
PAGESIZE=100

# all jobs
#prefix_url = "https://iworkfor.nsw.gov.au/jobs/all-keywords/all-agencies/all-organisations--entities/all-categories/all-locations/all-worktypes?pagesize={}&page=".format(str(PAGESIZE))

# job that over 100k
prefix_url = "https://iworkfor.nsw.gov.au/jobs/all-keywords/all-agencies/all-organisations--entities/all-categories/all-locations/all-worktypes?salaryrangeid=8,9,10,11,12,13,14&pagesize={}&page=".format(str(PAGESIZE))


## browser set up
CHROME_LOCATION = "C:/Users/rfzheng/Desktop/1/chromedriver_win32/chromedriver"
option = webdriver.ChromeOptions()
option.add_argument("-incognito")




def main(bln_allPages=False):

  ## first page
  soup, links = bundle_work(START_PAGE)
  
  ## get reset of page
  if bln_allPages:
    # get max page number
    max_page_num = get_max_page(soup)

    for i in range(START_PAGE + 1, max_page_num + 1):
      soup, links = bundle_work(i)

  return soup, links

def get_max_page(soup):
  ## get total number of jobs and total number of pages
  id_val = "TotalJob"
  content = soup.find("div", id=id_val)
  txt = str(content.get_text()).strip()
  
  total_result = int(txt.split()[0])
  total_page = int(ceil(total_result/(1.0*PAGESIZE)))

  return total_result, total_page
  





## helper functions:
  
def open_browser(url):

  soup = None
  class_val = "div.box-sec2"

  ## new browser
  browser = webdriver.Chrome(CHROME_LOCATION, chrome_options=option)
  #browser = webdriver.PhantomJS('C:/Users/rfzheng/Desktop/1/phantomjs-2.1.1-windows/bin/phantomjs')
  
  browser.get(url)
  
  try:
    WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, class_val)))
    print("Page is ready!")
    
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    browser.quit()  
    
  except TimeoutException:
      print("Loading took too much time!")
      browser.quit()
  
  return soup

def save_result():
  pass

def parse_title():
  pass

def pasrse_table():
  pass


def open_child_job(url):

  ## pattern
  pat_title = ("h1", "job-detail-title")
  
  html = urllib2.urlopen(url)
  soup = BeautifulSoup(html, "lxml")
  result = defaultdict()

  ## title
  job_title = str((soup.find(pat_title[0], class_=pat_title[1]).contents)[0])
  job_title = job_title.replace("\r\n", "").strip() # refine string

  result['job_title'] = job_title
  result['url_link'] = url
  
  ## table
  table = soup.find("table", class_ = "table table-striped")
  for row in table.findAll("tr"):
    ###th, td
    rows.append(row)
  
  print(job_title)
  

def bundle_work(page_num):
  url = prefix_url + str(page_num)
  soup = open_browser(url)
  if soup == None:
    print("Fail to open browser:", url)
    return

  links = find_job_list(soup)

  for l in links:
    open_child_job(l)
  
  return soup, links


def find_job_list(soup):
  
  ## get all the job list for current page
  class_val = "box-sec2-left"
  jobs = soup.find_all("div", class_ = class_val)
  links = []
  for job in jobs:
    # find href link and append result
    j = job.find("a", href=True)
    links.append(j['href'])
    
  return links
  


if __name__ == "__main__":
  soup, links = main()
