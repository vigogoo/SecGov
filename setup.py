#!/usr/bin/env python
# coding: utf-8

# **All Imports**

# In[ ]:


import requests
import urllib.request
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
from IPython.display import display, HTML,IFrame

# vars
import sec_variables as sec_vars


# opts = Options()
# opts.use_chromium = True
# opts.headless = True
# opts.add_argument("disable-gpu")
# opts.add_argument("--log-level=3")

logging.basicConfig(filename='v.log', filemode='w', level=logging.ERROR, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')



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

def sec_gov_print(message,severity=5):
    if severity == 5:
        css = "ansi-green-fg"
    else:
        css = "ansi-red-intense-fg ansi-bold"
    
    style = "border-width: 1px;border-style: solid;border-color: 42A5F5;width: 100%;padding: 5px;"

    display(HTML( f'<span style={style} class="{css}"> {message}</span>'))
       
    
def clean_soup(soup):
    for tag in soup(): 
        if tag.attribute in ["class", "style"]:         
            del tag[attribute] 
    return soup

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
                sec_gov_print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
                logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
                return False
        #exit() we want the script to continue
    return BeautifulSoup(r.text, 'html.parser')


def check_if_target_in_filetype(target,filetype="10-K"):
    if filetype == "10-K":
        return target in sec_vars.items_10_K
    else:
        return target in sec_vars.items_10_Q_part_I
#add part two later


def get_date_string(filing_date_start,filing_date_end=None):
#   2017-02-10 --- 2022-02-10
#   start_date --- end_date
    today = date.today()
    five_years_ago = today - datetime.timedelta(days=3*365)
    default_end_date = today.strftime("%Y-%m-%d")
    default_start_date = five_years_ago.strftime("%Y-%m-%d")
    
    if filing_date_start and not filing_date_end:
        return  (filing_date_start,default_end_date)
    elif not filing_date_start and  filing_date_end:
        return  (default_start_date,filing_date_end)
    elif filing_date_start and filing_date_end:
        return  (filing_date_start,filing_date_end)
    else:
        return (default_start_date,default_end_date)



def get_generic_marketdata(url):
    
    # headers = {
    #     'User-Agent': generate_random_names(),
    #     'Accept-Encoding':'gzip, deflate',
    #     'Host': 'www.sec.gov'
    #     }
    headers = {
    'accept-encoding':'gzip, deflate',
    'host': 'www.sec.gov',
    'authority': 'efts.sec.gov',
    'accept': 'application/json, text/javascript, */*; q=0.01,gzip,deflate',
    'content-type': 'text/html; charset=UTF-8',
    'sec-ch-ua-mobile': '?0',
    'user-agent': generate_random_names(),
    'origin': 'https://www.sec.gov',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.sec.gov/',
    }

    #r = requests.post(url, headers=headers)
    #r = requests.get(url,headers=headers,allow_redirects=True)
    r = urllib.request.Request(url,headers=headers)
    
   
    # if r.status != 200:
    #     # retry 3 times
    #     r = urllib.request.Request(url,headers=headers)
    #     if r.status != 200:
    #         r = urllib.request.Request(url,headers=headers)
    #         if r.status != 200:
    #             sec_gov_print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
    #             logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
    #             return False
        #exit() we want the script to continue
    with urllib.request.urlopen(r) as f:
        soup = f.read()
    #return BeautifulSoup(r.text, 'lxml') 
    return soup



def get_item_2(results,form_data):


    
    #ITEM_DATA_URL = get_search_results(SEARCH_URL)
    ITEM_DATA_URL = results['file_path']
    print(ITEM_DATA_URL)
    if not ITEM_DATA_URL:
        print('No Results returned for that criteria')
    else:
        
    
        # with open('https://www.sec.gov/Archives/edgar/data/789019/000156459021039151/0001564590-21-039151.txt') as fp:
        #     soup = BeautifulSoup(fp, 'html.parser')

        soup = get_generic_marketdata(ITEM_DATA_URL)
        soup = soup.decode("utf-8","ignore")
        soup = BeautifulSoup(soup,"lxml")
        #soup.prettify("utf-8")
        soup = clean_soup(soup)
 
      
        all_links = []
        item_2_candidates = []
        item_3_candidates = []

        target = form_data['target']
        next_target = form_data['next_target']
        target = target.replace("2.","").replace("Item","").strip()
        file_type = form_data["filing_type"]
        target_name = get_target_name(target)
        next_target_name = get_target_name(next_target)
        print(f'from {target}{target_name} to {next_target}{next_target_name}')
  

        target_candidates = soup.find_all("a",string=re.compile(f'{target_name}|Item {target}.|Item {target}|Item&bnsp;{target}|Item&#160;{target}|Item{target}|Item',flags=re.IGNORECASE))
        next_target_candidates = soup.find_all("a",string=re.compile(f'{next_target_name}|Item {next_target}.|Item {next_target}|Item&bnsp;{next_target}|Item&#160;{next_target}|Item{next_target}|Item',flags=re.IGNORECASE))
        print(target_candidates)
        print(next_target_candidates)

        # print(doc_links)
        # for posn, link in enumerate(doc_links):
        #     if link.string is None:
        #         link.string = ""
        #     if link.has_attr('href'):next_target_name
        #         if  len(link.string) > 5 and "Table of Contents" not in link.string:
        #             all_links.append((posn,link['href'],link.string))
        #             print(link.string)
        #             if (start := re.compile(get_target_name(target,file_type),flags=re.IGNORECASE).search(link.string)):
        #                 print('start',start)

                    
        #                 item = (posn,link['href'],link.string)
        #                 item_2_candidates.append(item)
        #             if (end :=  re.compile(next_target['name'],flags=re.IGNORECASE).search(link.string)):
        #                 item = (posn,link['href'],link.string)
        #                 item_3_candidates.append(item)
        #                 all_links.append(item)
        #                 print('next',next_target['name'])
        #         else:
        #             all_links.append((posn,link['href'],"DO NOT USE**"+link.string))
        
        
        


        for link in all_links:
            print(link)
        print('Candidates')
        print(item_2_candidates)
    # Candidates
    #[(9, '#ITEM_2_MANAGEMENTS_DISCUSSION_ANALYSIS_F', 'Management’s Discussion and Analysis of Financial Condition and Results of Operations')]
    # For each candidate the paragraph in between this href and next href using doc_links
        soup = str(clean_soup(soup))
        #str(soup.html)
        for candidate in item_2_candidates:
            # the first match is for TOC so get the second match only
            # get the candidate with highest start value
            # candidate[1] is href = posn,link['href'],link.string
            item_2_href_matchObj = re.finditer(candidate[1].replace("#",""), soup, flags=re.IGNORECASE)
            
            item_2_href_matchObj = list(item_2_href_matchObj)
            #    print('item_2_href_matchObj',item_2_href_matchObj)
            if len(item_2_href_matchObj)> 1:
                #get object with hhighest start value
                item_2_obj = item_2_href_matchObj[-1]
                for obj in item_2_href_matchObj:
                    if obj.start() >  item_2_obj.start():
                        item_2_obj = obj
                
                # print('item_2_obj\n',item_2_obj)

                item_3_obj = all_links[candidate[0]+1] # get the next link
                # print(f'end link \n{item_3_obj[1]} vrs \ncandidate\n{candidate[1]}')
                #confirm this link is different else take the next one 
                if item_3_obj[1] != candidate[1] and "DO NOT USE" not in item_3_obj[1] :
                    item_3_href_matchObj = re.finditer(item_3_obj[1].replace("#","") , soup, flags=re.IGNORECASE)
                else:

                    item_3_obj = all_links[candidate[0]+2]
                    item_3_href_matchObj = re.finditer(item_3_obj[1].replace("#","") , soup, flags=re.IGNORECASE)

                # print(f'end link \n{item_3_obj} vrs \ncandidate\n{candidate}')
                item_3_href_matchObj = list(item_3_href_matchObj)
                # print('item_3_href_matchObj\n',item_3_href_matchObj)
                if len(item_3_href_matchObj)> 1:
                    # the first match is for TOC so get the second match only
                    # sort by start
                    item_3_obj = item_3_href_matchObj[-1]
                    # print(f'end candidate before\n{item_3_obj} ')
                    for obj in item_3_href_matchObj:
                        # print(f'{obj.start()} verses  {item_3_obj.start()}')
                        if obj.start() >  item_3_obj.start():
                            item_3_obj = obj
                    # print('item_3_obj\n',item_3_obj)
                    
                    # print(f'{item_2_obj.start()}:{item_3_obj.start()}')
                    results_html = soup[item_2_obj.start()-10:item_3_obj.start()]
                    results_html = results_html.encode("ascii",errors="ignore")
                    results_html = results_html.decode("utf-8","ignore")
                    
                    #print(results_html)
                    display(HTML(results_html))

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
    "startdt":str(date_strings[0]),
    "enddt":str(date_strings[1])
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
                sec_gov_print(f"FATAL ERROR: 3 retries failed to retrieve information from url:\n{url}")
                logging.error(f'FATAL ERROR! 3 retries failed to retrieve information from url:\n{url}')
                return False


    response_data = json.loads(r.text)
    
    total_results = response_data.get('hits',{}).get('total',{}).get('value',0)

    clean_results = []
    sec_gov_print(f"TOTAL SEARCH RESULTS: {total_results}")
    exe = 0
    if total_results > 0:

    #user passed limits
        limit = min(max_results_needed,total_results)
    #     add results to total results
        
        results = response_data.get('hits',{}).get('hits',{})
        for result in results:
        # print(results)
            source = result.get('_source',{})
            #print(source)

    #     clean data avoid exhibit files
            if "ex" not in source.get('file_type',"ex").lower() and "10-" in source.get('file_type'):
                filing_no = source.get('adsh').replace("-","")
                adsh = source.get('adsh')
                ticker = source.get('ciks')[0]
                index_page = str(FILE_BASE_URL) +  str(ticker) + "/" + str(filing_no)
                file_name = result.get('_id','').split(":")[-1]
                cik_without_zeros = source.get('ciks')[0]
                while cik_without_zeros[0] == "0":
                    cik_without_zeros=cik_without_zeros[1:]

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
                    'index_page': index_page,
                    'txt_file_path': "https://www.sec.gov/Archives/edgar/data/"+cik_without_zeros+'/'+filing_no+'/'+adsh+'.txt'
                }
                clean_results.append(data)
            else:
                exe += 1
        
        sec_gov_print(f'Exhibits Records (exe) Ignored: {exe}')
        df = pd.DataFrame.from_dict(clean_results, orient='columns')
        df.sort_values(by=['file_date'], inplace=True, ascending=False)
        return df[:limit]



# **Form input for Task 1**
def get_target_name(target,file_type=None):
    print(target,file_type)
    if "2." in target: #PART 2
        #part 2
        return str(sec_vars.items_10_Q_part_II.get(target.replace("2.",""),None))
    elif file_type=="10-K":
        return str(sec_vars.items_10_K.get(target,None))
    elif file_type=="10-Q": 
        # it id 10-q part 1
        return str(sec_vars.items_10_Q_part_I.get(target,None))
    else :
        #print('he')
        dd=sec_vars.items_10_K.get(target,None)
        ee=sec_vars.items_10_Q_part_I.get(target,None)
        #print(ee,dd)
        if dd is not None and ee is not None:
           return dd #+ '|' + ee
        elif dd is None and ee is not None:
            return ee
        elif dd is not None and ee is None:
            return dd
        elif dd is None and ee is None:
            return None
        

def get_next_target(target,part=None,file_type=""):
    if part:
        if part == "Part I":
            part = 1
        else:
            part = 2


    if target in ["1B","6","7","7A","8","9","9A","9B","10","11","12","13","14"]:
        file_type = "10-K"
        # these are unique to it
    elif part:
        file_type = "10-Q"
        if target in ["1A","5"]:
            part = 2
            #these are unique to it
    
    a_list = list(sec_vars.items_10_K)
    b_list = list(sec_vars.items_10_Q_part_I)
    c_list = list(sec_vars.items_10_Q_part_II)
    #target_name= items_10_K.get(target,items_10_Q_part_I.get(target,items_10_Q_part_II.get(target,None)))
    #print(target_name)
    if file_type == "10-K" and target in a_list:
        idx =  a_list.index(target)
        if idx < len(a_list)-1 :
            return a_list[idx+1]
    elif file_type == "10-Q" :
        if part ==1 and target in b_list:
            idx =  b_list.index(target)
            if idx < len(b_list)-1:
                return b_list[idx+1]
        elif target in c_list :
            idx =  c_list.index(target)
            if idx < len(c_list)-1:
                return c_list[idx+1]
    return None # if at end of the list
    # if target in a_list:
    #     idx =  a_list.index(target)
    #     if idx < len(a_list)-1 :
    #         return a_list[idx+1]
    # if target in b_list:
    #     idx =  b_list.index(target)
    #     if idx < len(b_list)-1:
    #         return b_list[idx+1]
    # if target in c_list:
    #     idx =  c_list.index(target)
    #     if idx < len(c_list)-1:
    #         return c_list[idx+1]
    



        




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
        form['search_type'] = search_type.value
        form['part'] = "Part I."
        if form['search_type'] == "i":
            if "2." in form['target']:
                form['part'] = "Part II."
            #form['next_target'] = get_next_target(form['target'],form['part'],form['filing_type'])
            #     form['target'].replace('2.','Item ')
            # else:
            #     form['target'] = 'Item '+str(form['target'])

        #generate dynamic search url for queries
        
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
                
                print("FILING SUMMARY LINK",filing_summary_link, end="")
                index_page = links_dict.get('index_page')
                soup = request_data(filing_summary_link)
                tag = soup.find( lambda tag:tag.name.lower() == "shortname" and table_to_fetch.lower() in tag.text.lower() )
                
                if tag:
                    parent = tag.parent
                    table_link = index_page + '/' + parent.find('htmlfilename').text
                    table_full_ttl = parent.find('longname').text
                    print("table_link",table_link)
                    soup = request_data(table_link)
                    table_MN = pd.read_html(str(soup.table))[0]

                    print('FINANCIAL DATA TITLE:',table_full_ttl)
                    print('TABLE LINK:',table_link, end="")
                    display(table_MN)
                    
                else:
                    print(f"Document with title: {table_to_fetch} Not found")
            # If user was searching for a Particular Item in Document handler
            if form.get('search_type','').lower() == 'i' and results is not None:
                
                links_dict = results.to_dict('records')[0]
                print(links_dict)
                form['next_target'] = get_next_target(form['target'],form['part'],links_dict['file_type'])
                print(form, end="\n\n")
                if check_if_target_in_filetype(form['target'],links_dict['file_type']):
                    get_item_2(links_dict,form)
                else:
                    sec_gov_print(f"The requested document {links_dict['file_type']} is not found in most recent document{form['target']}.\nSelect another criteria.",10)
            
        # todo: end execution if results is none

    grid = GridspecLayout(8, 2)
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
        description='Date From:',
        disabled=False
    )

    date_to = wdgts.DatePicker(
        description='Date To:',
        disabled=False
    )

    btn_search = wdgts.Button(
        description='Search',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Search',
        icon='search' # (FontAwesome names without the `fa-` prefix)
    )
    # progress_bar = wdgts.IntProgress(
    # value=0,
    # min=0,
    # max=10,
    # description='Loading:',
    # bar_style='', # 'success', 'info', 'warning', 'danger' or ''
    # style={'bar_color': 'maroon'},
    # orientation='horizontal'
# )
    btn_search.on_click(get_inputs_task_1)
    grid[0,0] = ticker
    grid[1,0] = filing_type
    grid[2,0] = search_type
    grid[3,0] = doc_section
    grid[4,0] = date_from
    grid[5,0] = date_to
    grid[6,0:] = btn_search
    #grid[7,0:] = progress_bar
    return grid
    


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




