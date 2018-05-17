"""
Author: Ricky ZHENG

use this program to scrap open position in IWORKNSW
aim for $100k+ positions in NSW

Technique invovled:
  - webscrapping with BeautifulSoup
  - Selenium for headerless browser simulation
  - use multiple ip with proxie (anonmous, Elite)
  - use multiple user-agents to avoid ban from frequent scrapping

"""
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from collections import defaultdict
from bs4 import BeautifulSoup
import scrapy_helper as schp
from math import ceil
import requests
import random
import time
import csv

## initial
START_PAGE=1

TIMEOUT = 20 # seconds, browser timetout
PAGESIZE=100

## delay for crawling child pages, random ranges(A, B)
DELAY_A = 5			
DELAY_B = 12

# all jobs
#prefix_url = "https://iworkfor.nsw.gov.au/jobs/all-keywords/all-agencies/all-organisations--entities/all-categories/all-locations/all-worktypes?pagesize={}&page=".format(str(PAGESIZE))

# job that over 100k
prefix_url = "https://iworkfor.nsw.gov.au/jobs/all-keywords/all-agencies/all-organisations--entities/all-categories/all-locations/all-worktypes?salaryrangeid=8,9,10,11,12,13,14&pagesize={}&page=".format(str(PAGESIZE))


## browser set up
#CHROME_LOCATION = "C:/Users/rfzheng/Desktop/1/chromedriver_win32/chromedriver"
#CHROME_LOCATION = "/home/eutility2/Projects/chromedriver"
CHROME_LOCATION = "/Users/ricky/Projects/chromedriver"
option = webdriver.ChromeOptions()
option.add_argument("-incognito")




def main(bln_allPages=False):

  ## first page
  print("working on page", START_PAGE, end="...")
  final_data, soup, links = bundle_work(START_PAGE)
  # save result
  save_result(final_data, '{}.csv'.format(START_PAGE))
  
  ## get reset of page
  if bln_allPages:
    # get max page number
    max_page_num = get_max_page(soup)

    for i in range(START_PAGE + 1, max_page_num + 1):
      print("working on page", i, end="...")
      final_data, soup, links = bundle_work(i)

      # save result
      save_result(final_data, '{}.csv'.format(i))
  return final_data, soup, links

def get_max_page(soup):
  ## get total number of jobs and total number of pages
  id_val = "TotalJob"
  content = soup.find("div", id=id_val)
  txt = str(content.get_text()).strip()
  
  total_result = int(txt.split()[0])
  total_page = int(ceil(total_result/(1.0*PAGESIZE)))

  return total_page
  





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
    # use different method with differnt os
    #soup = BeautifulSoup(html, "lxml")            #windows
    soup = BeautifulSoup(html, "html.parser")    #mac/linux


    browser.quit()  
    
  except TimeoutException:
      print("Loading took too much time!")
      browser.quit()
  
  return soup

def save_result(data, file_name):
  all_keys = set().union(*(d.keys() for d in data))
  with open(file_name, 'wb') as f:
  	dict_writer = csv.DictWriter(f, list(all_keys))
  	dict_writer.writeheader()
  	dict_writer.writerows(data)

def parse_title():
  pass

def pasrse_table():
  pass

def random_delay(a,b):
	time.sleep(random.uniform(a,b))
	return



def open_child_job(url, proxy_list, user_agent_list):

  ## pattern
  pat_title = ("h1", "job-detail-title")
  html=None

  ## retry requests with different combo (proxy and agent)
  for i in range(len(proxy_list)):
    try:
      headers = {'User-Agent': user_agent_list[i]}
      proxy = proxy_list[i]
      result = requests.get(url, headers=headers, proxies={"http":proxy, "https:":proxy})
      html = result.content
      #print("successful requests!")
      break
    except Exception, e:
      pass


  # use different method with differnt os
  soup = BeautifulSoup(html, "lxml")            #windows
  #soup = BeautifulSoup(html, "html.parser")    #mac/linux
  #soup = BeautifulSoup(html)

  result = defaultdict()

  ## title
  job_title = (soup.find(pat_title[0], class_=pat_title[1]).contents)[0]
  job_title = unicode(job_title)
  job_title = job_title.encode('ascii', 'ignore')
  job_title = job_title.replace("\r\n", "").strip() # refine string

  result['job_title'] = job_title
  result['url_link'] = url
  
  ## table
  table = soup.find("table", class_ = "table table-striped")
  for row in table.find_all("tr"):
    ###th, td
    th = (row.find("th").contents)[0]
    th = unicode(th)
    th = th.encode('ascii', 'ignore')
    th = th.replace("\r\n", "").strip() # refine string
    
    ## in case there is li element
    td = row.find("td")
    li = td.find_all("li")
    if li:
      li = filter(None, li)
      td_vals = [(l.contents)[0] for l in li if l.contents]
      td = '||'.join(td_vals)
    else:
      td = (td.contents)[0]

    td = unicode(td)
    td = td.encode('ascii', 'ignore')
    td = td.replace("\r\n", "").strip() # refine string

    result[th]=td
    
  print(job_title)
  return result

def bundle_work(page_num):
  url = prefix_url + str(page_num)
  soup = open_browser(url)
  final_data = []

  if soup == None:
    print("Fail to open browser:", url)
    return

  links = find_job_list(soup)

  ## get proxy and user-agent
  proxy_set = schp.get_proxies()
  agent_set = schp.get_useragents()


  for l in range(len(links)):
    #print(l)
  	#random_delay(DELAY_A, DELAY_B)

    ## random choose one from both set, 
    ## provide 3 sample for invalid set backup
    proxy = random.sample(proxy_set, 3)
    user_agent = random.sample(agent_set, 3)

    print(l+1, "/", len(links), end=" ")
    link = links[l]
    result = open_child_job(link, proxy, user_agent)
    final_data.append(result)
  
  return final_data, soup, links


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
  final_data, soup, links = main()
