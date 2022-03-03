#!/usr/bin/env python
# coding: utf-8

# **All Imports**

# In[ ]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# logging
import sys
import logging
import time

# from selenium.webdriver import Chrome
# from selenium.webdriver.chrome.options import Options
from datetime import date
import datetime
import json

# UI
import ipywidgets as wdgts
from ipywidgets import GridspecLayout


# In[ ]:


# opts = Options()
# opts.use_chromium = True
# opts.headless = True
# opts.add_argument("disable-gpu")
# opts.add_argument("--log-level=3")

logging.basicConfig(filename='v.log', filemode='w', level=logging.ERROR, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# try:
#     driver = Chrome(options=opts, executable_path='./chromedriver.exe') 
# except Exception as e:
#     logging.error(f'FATAL ERROR! {e}')
#     sys.exit()

# variables
BASE_URL = "https://www.sec.gov/edgar/search/#/"
FILE_BASE_URL = "https://www.sec.gov/Archives/edgar/data/" 
#form = {}


# In[ ]:


def generate_random_names():
    import random
    first_names = ['Madelyn','Lamb','Ty','Long','Janiya','Burke','Kameron','Mercer','August','Ibarra','Jabari','Hurley','Daniel','Green','Spencer','Small','Dougherty','Romero','Pittman','Frank','Gardner','Hays','Harrington','Olson']
    last_names = ['Vicente','Stevens','Leonard','Stokes','Judah','Frost','Sophie','Parsons','Sydnee','Ellison','Calvin','Calhoun','Konnor','Moriah','Elijah','Rachael','Rigoberto','Justus','Jordin','Elliot','Leon','Declan','Gianna','Yaritza']
    digits = [11,23,45,67,89,30,91,82,73,64,65,54,43,32,21,10]

    name = random.choice(first_names) +' '+ random.choice(last_names) 
     
    return name + ' ' + name.replace(' ','')+ str(random.choice(digits))+'@gmail.com'

def request_data(url,payload={}):
    headers = {
        'User-Agent': generate_random_names(),
        'Accept-Encoding':'gzip, deflate',
        'Host': 'www.sec.gov'
        }
    r = requests.get(url,headers=headers)

    if r.status_code != 200:
        # retry 3 times
        r = requests.get(url,headers=headers)
        if r.status_code != 200:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
                logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
                return False
        #exit() we want the script to continue
    return BeautifulSoup(r.text, 'html.parser')

def get_date_string(filing_date_start,filing_date_end=None):
#   2017-02-10 --- 2022-02-10
#   start_date --- end_date
    today = date.today()
    five_years_ago = today - datetime.timedelta(days=3*365)
    default_start_date = today.strftime("%Y-%m-%d")
    default_end_date = five_years_ago.strftime("%Y-%m-%d")
    
    if filing_date_start and not filing_date_end:
        return  (filing_date_start,filing_date_start)
    elif not filing_date_start and  filing_date_end:
        return  (filing_date_end,filing_date_end)
    elif filing_date_start and filing_date_end:
        return  (filing_date_start,filing_date_end)
    else:
        return (default_end_date,default_start_date)


# In[ ]:


def get_generic_marketdata(url):
    print('*****url in url*****',url)
    headers = {
        'User-Agent': generate_random_names(),
        'Accept-Encoding':'gzip, deflate',
        'Host': 'www.sec.gov'
        }
    r = requests.get(url,headers=headers)

    if r.status_code != 200:
        # retry 3 times
        r = requests.get(url,headers=headers)
        if r.status_code != 200:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
                logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
                return False
        #exit() we want the script to continue
    return BeautifulSoup(r.text, 'lxml') 


def get_search_results(form_data,max_results_needed=float('inf')):
    fd = form_data
#     clean date formats first
    date_strings = get_date_string( fd.get('filing_date_start'), fd.get('filing_date_end') )
#     check if user gave form filings to search by
    forms = fd.get('filing_type','') or "10-K,10-Q"
    url = "https://efts.sec.gov/LATEST/search-index"
    payload = json.dumps({
    "q":fd.get('target',''),
    "category":"custom",
    "entityName":fd.get('ticker',''),
    "forms":forms.split(','),
    "startdt":date_strings[0],
    "enddt":date_strings[1]
    })
    headers = {
      'authority': 'efts.sec.gov',
      'accept': 'application/json, text/javascript, */*; q=0.01',
      'content-type': 'application/json; charset=UTF-8',
      'sec-ch-ua-mobile': '?0',
      'user-agent': generate_random_names(),
      'origin': 'https://www.sec.gov',
      'sec-fetch-site': 'same-site',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': 'https://www.sec.gov/',
    }

    r = requests.post(url, headers=headers, data=payload)
    if r.status_code != 200:
        # retry 3 times
        r = requests.post(url, headers=headers, data=payload)
        if r.status_code != 200:
            r = requests.post(url, headers=headers, data=payload)
            if r.status_code != 200:
                print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
                logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
                return False

    response_data = json.loads(r.text)
    total_results = response_data.get('hits',{}).get('total',{}).get('value',0)

    clean_results = []
    print("Total results are:",total_results,end="\n\n")
    exe = 0
    if total_results > 0:

    #user passed limits
        limit = min(max_results_needed,total_results)
    #     add results to total results
        results = response_data.get('hits',{}).get('hits',{})
        for result in results:
            source = result.get('_source',{})

    #     clean data avoid exhibit files
            if "ex" not in source.get('file_type',"ex").lower():
                filing_no = source.get('adsh').replace("-","")
                ticker = source.get('ciks')[0]
                index_page = str(FILE_BASE_URL) +  str(ticker) + "/" + str(filing_no)
                file_name = result.get('_id','').split(":")[-1]
                data = {
                    'file_date' : source.get('file_date'),
                    'filing_no' : filing_no,
                    'file_type' : source.get('file_type'),
                    'file_name' : file_name,
                    'ticker' : ticker,
                    'period_ending' : source.get('period_ending'),
                    'display_names' : " ".join(source.get('display_names')),
                    'filing_summa_xml_path': index_page + "/" + 'FilingSummary.xml',
                    'file_path': index_page + "/" + file_name,
                    'index_page': index_page
                }
                clean_results.append(data)
            else:
                exe += 1
        
        print('Exhibits Records (exe) Ignored:',exe,end="\n\n")
        df = pd.DataFrame.from_dict(clean_results, orient='columns')
        df.sort_values(by=['file_date'], inplace=True, ascending=False)
        return df[:limit]
#     print("No Records for this search were found")
    return None
    
# Test function results
# get_search_results({'ticker': 'apple',
#  'filing_type': '',
#  'search_type': 'T',
#  'target': 'balance sheet',
#  'filing_date_start': '2020-01-01',
#  'filing_date_end': '2022-03-01'},3)


# **Form input for Task 1**

# In[ ]:


# def get_inputs_task_1(btn):
# #     form = {}
#     form['ticker'] = (ticker.value).strip()
#     form['filing_type'] = (filing_type.value).upper()
#     form['target'] = fin_statement.value
#     form['filing_date_start'] = date_from.value
#     form['filing_date_end'] = date_to.value
    #return form


    #return form


# In[ ]:


def create_task_1_UI():
    fin_type_options=[("Income Statement","Income"),("Balance Sheet","Balance Sheet"),("Statements of Cash Flow","Cash Flow"),("Statements of Convertible Preferred Stock and Stockholder’s Equity","Stockholder")]
    item_type_options = ["1","1A","1B","2","3","4","6","7","7A","8","9","9A","9B","10","11","12","13","14","2.1","2.1A","2.2","2.3","2.4","2.5"]
    def get_inputs_task_1(btn):
        form = {}
        form['ticker'] = (ticker.value).strip()
        form['filing_type'] = (filing_type.value).upper()
        form['target'] = doc_section.value
        form['filing_date_start'] = date_from.value
        form['filing_date_end'] = date_to.value
        form['search_type'] = 't'
        #generate dynamic search url for queries
        search_url = generate_search_url(form)

        #fetch all search results for query we need only one Result for task one
        results = get_search_results(form,1)
        if results is None:
            print("Your Search did not yield any results",end="\n\n")
        else:
            if form.get('search_type','').lower() == 't' and results is not None:
        #     fetch table
                table_to_fetch = form.get('target','')
                # get links to pages
                links_dict = results.to_dict('records')[0]
                filing_summary_link = links_dict.get('filing_summa_xml_path')
                
                print("FILING SUMMARY LINK",filing_summary_link, end="\n\n")
                index_page = links_dict.get('index_page')
                print(index_page,index_page)
                soup = get_generic_marketdata(filing_summary_link)
                tag = soup.find( lambda tag:tag.name.lower() == "shortname" and table_to_fetch.lower() in tag.text.lower() )
                
                if tag:
                    parent = tag.parent
                    table_link = index_page + '/' + parent.find('htmlfilename').text
                    table_full_ttl = parent.find('longname').text
                    print("table_link",table_link)
                    soup = get_generic_marketdata(table_link)
                    table_MN = pd.read_html(str(soup.table))[0]

                    print('FINANCIAL DATA TITLE:',table_full_ttl)
                    print('TABLE LINK:',table_link, end="\n\n")

                    display(table_MN)
                    
                else:
                    print(f"Document with title: {table_to_fetch} Not found")
            # If user was searching for a Particular Item in Document handler
            if form_inputs.get('search_type','').lower() == 'i' and results is not None:
                
                print(
                    f"Your searching for a particular Item in Part {form_inputs.get('item_part')} and Item number {form_inputs.get('target')}",
                    end="\n\n"
                )
                print(form_inputs, end="\n\n")
                links_dict = results.to_dict('records')[0]
                print(links_dict)
        # todo: end execution if results is none

    grid = GridspecLayout(7, 2)
    style = {'description_width': 'initial'}
    ticker = wdgts.Text(
        value='',
        placeholder='Enter..',
        description='Ticker/Entity Name:*',
        style=style,
        disabled=False
    )
    search_type = wdgts.Dropdown(
        options=[("Financial Statement","t"),("Item","i")],
        value="t",
        description='Required Information:*',
        style=style,
        disabled=False,
    )
   
    
    filing_type = wdgts.Combobox(
        placeholder='Enter..',
        options=["","10-Q","10-K","10-Q/A","10-QSB","10-QT","10-QT/A","10-QSB","10-QSB/A","10-QSB12B","10-K/A","10-K405","10-K405/A","10-KSB","10-KT","10-KT/A"],
        value='',
        description='Filing Type:',
        ensure_option=True,
        disabled=False
    )
    

    doc_section = wdgts.Dropdown(
        options=[("Income Statement","Income"),("Balance Sheet","Balance Sheet"),("Statements of Cash Flow","Cash Flow"),("Statements of Convertible Preferred Stock and Stockholder’s Equity","Stockholder")],
        value='Income',
        description='Document Section:*',
        ensure_option=True,
        disabled=False,
        style=style
    )
    def search_type_event_handler(change):
        doc_section.options = item_type_options if change.new == "i" else fin_type_options
        #display(filing_type)
    search_type.observe(search_type_event_handler, names='value')

    date_from = wdgts.DatePicker(
        description='Pick a Date:',
        disabled=False
    )

    date_to = wdgts.DatePicker(
        description='Pick a Date:',
        disabled=False
    )

    btn_search = wdgts.Button(
        description='Search',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Search',
        icon='search' # (FontAwesome names without the `fa-` prefix)
    )
    btn_search.on_click(get_inputs_task_1)
    grid[0,0] = ticker
    grid[1,0] = filing_type
    grid[2,0] = search_type
    grid[3,0] = doc_section
    grid[4,0] = date_from
    grid[5,0] = date_to
    grid[6,0:] = btn_search
    return grid
    


# In[ ]:


def get_inputs_tsk1():
    form = {}
    form['ticker'] = input('Enter Stock Ticker Symbol>>  ').strip()
    form['filing_type'] = input('Enter Filing Type Required (10-K,10-Q,etc)>>  ').upper()
#     Is the User search for a financial table or particular Item
    while True:
        form['search_type'] = input("Do you want to search for a Financial Table (T) or Particular Item in Document (I),Please Enter (T) or (I)>>  ").strip()
        if form['search_type'].lower() == 't' or form['search_type'].lower() == 'i':
            break
#     if searching for financial table or searching for particular item
    search_type = form['search_type'].lower()
    if search_type == 't':
        form['target'] = input('Enter Document Required>> ').strip()
    else:
        while True:
            form['item_part'] = input('Do you want to get an item in Part I (1) or Part II (2),Please Enter (1) or (2)>>  ').strip()
            if form['item_part'] == '1' or form['item_part'] == '2':
                break
#       get item number
        form['target'] = input('Enter Item Number>> ').strip()
    
    print('To enter ''Date of Filing'' only enter one date. To enter ''Date period'' enter 2 dates.  ')
    form['filing_date_start'] = input('Filed FROM Date: (YYYY-MM-DD)>>  ').strip() or None
    form['filing_date_end'] = input('Filed TO Date: (YYYY-MM-DD)>>  ').strip() or None
    return form



def generate_search_url(data):
    for key in data:
        if data[key] is None:
            data[key] = ''
    ''' get search results from sec.gov and save to excel file'''
    document = '%2522'+'%2520'.join(data.get('target').split(' '))+'%2522'
    date_strings = get_date_string( data.get('filing_date_start'), data.get('filing_date_end') )
    
    forms =  "10-K%252C10-Q"  if data['filing_type']=='' else  data['filing_type']
    SEARCH_URL = f"{BASE_URL}q={document}&category=custom&entityName={data.get('ticker')}&forms={forms}&startdt={date_strings[0]}&enddt={date_strings[1]}"
    print('SEARCH_URL',SEARCH_URL, end="\n\n")
    return SEARCH_URL


# **Form input for Task 2**

# In[ ]:


def get_inputs_tsk2():
    form = {}
#   default company names are None
    form['ticker'] = None
    form['filing_type'] = input('Enter Filing Type Required (10-K,10-Q,etc)>>  ')
    while True:
        form['item_part'] = input('Do you want to get an item in Part I (1) or Part II (2),Please Enter (1) or (2)>>  ').strip()
        if form['item_part'] == '1' or form['item_part'] == '2':
            break
            
#       get item number
    form['item_number'] = input('Enter Item Number>> ').strip()
    
#       keyword or phrase to search with the item number
    form['target'] = input('Enter keyword or phrase to search with the item number>> ').strip()
    
    print('To enter ''Date of Filing'' only enter one date. To enter ''Date period'' enter 2 dates.  ')
    form['filing_date_start'] = input('Filed FROM Date: (YYYY-MM-DD)>>  ').strip() or None
    form['filing_date_end'] = input('Filed TO Date: (YYYY-MM-DD)>>  ').strip() or None
    return form


# **Extractor function**

# In[ ]:


# dummy test content for the extractor

# contents = """
# (1) Index to Consolidated Financial Statements:
# Report of Ernst & Young LLP, Independent Registered Public Accounting Firm
# Consolidated Statements of Cash Flows for each of the three years ended December 31, 2021
# Consolidated Statements of Operations for each of the three years ended December 31, 2021
# Consolidated Statements of Comprehensive Income for each of the three years ended December 31, 2021
# Consolidated Balance Sheets as of December 31, 2020 and 2021
# Consolidated Statements of Stockholders’ Equity for each of the three years ended December 31, 2021
# Notes to Consolidated Financial Statements
# Report of Ernst & Young LLP, Independent Registered Public Accounting Firm
# (2 ) Indexiasz ad to Financial Statement Schedules
# All schedules have been omitted because the required information is included in the consolidated financial statements or the notes thereto, or because it is not required.
# (3) Index to Exhibits Kenya
# See exhibits listed under Part (b) below.


# """


# In[ ]:



def content_extractor(content,start_pt,start_pattern,end_pt,end_pattern,size=10):
    start_candidates = []
    end_candidates = []
    
#     get possible starting points in content
    possible_starts = [match for match in re.finditer(start_pt, content, flags=re.IGNORECASE)]
    
#     no starting point found
    if not possible_starts:
        return False
    
    
#  get start candidates
    for candidate in possible_starts:
        start = candidate.start()
        back_step = max(0,start-size)
        if (end := re.compile(start_pattern,flags=re.IGNORECASE).search(content,back_step,start)):
            start_candidates.append(end.start())

# no starting candidates found after cleaning  
    if not start_candidates:
        return False
    

#     if stopping point was passed
    if end_pt:
    #  get possible stopping point in content else ending point is end of content
        possible_endings = [match for match in re.finditer(end_pt, content, flags=re.IGNORECASE)]
        
        
    # get ending candidates if no ending candidates found get upto end of string
        for candidate in possible_endings:
            start = candidate.start()
            back_step = max(0,start-size)
            if (end := re.compile(end_pattern,flags=re.IGNORECASE).search(content,back_step,start)):
                end_candidates.append(end.start())

# There is a start but no end
    if not end_candidates:
        return content[start_candidates[0] - 1:]
    
    results = "\n\n"
#   catch if any case ending candidates are less than starting candidate
    try:
        for i,j in enumerate(start_candidates):
            results += content[j - 1:end_candidates[i] - 1] + "\n\n\n\n\n"
    except IndexError:
        index_breaked = len(end_candidates)
        results += content[start_candidates[index_breaked]:] + "\n\n\n\n\n"
        
    return results


# In[ ]:


# test constructor by calls
# print(content_extractor(
#     contents,
#     'Index to Consolidated Financial Statements',
#     '\(1\)|\( 1\)|\(1 \)|\(1.\)',
#     'Index to Exhibits Kenya|Index to Exhibits Uganda',
#     '\(3\)|\( 3\)|\(3 \)|\(3.\)',
#     size=10
# ))


      


# In[ ]:




