# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 16:46:31 2018

@author: Maxence
"""

#########################################################################
#                                                                       #
#               Librairies in order to make requests                    #
#               and retrieve data from .html files                      #
#                                                                       #
#########################################################################

import urllib.request as urllib2
from bs4 import BeautifulSoup
import sqlite3
import datetime


#########################################################################
#                                                                       #
#           Main code for webscrapping and downloading file             #
#                                                                       #
#########################################################################

DATABASE_FILE_PATH = "data/business_week_historic.db"

def init_database():
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    try:
        conn.execute('''CREATE TABLE download_historic
             (Date, Name)''')
    except:
        pass # The database is already created
    conn.commit()
    conn.close()


def store_data(Name):
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        data = (now, Name)
        conn.execute("INSERT INTO download_historic VALUES (?,?)", data)
    except:
        print('Error while storing datas')
    
    conn.commit()
    conn.close()

def is_present(Name):
    
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.execute("SELECT COUNT(1) FROM download_historic WHERE Name=\""+Name+"\"").fetchall()
    nbr_occurence = cursor[0][0]
    conn.close()
    
    return True if nbr_occurence != 0 else False


def download_file(download_url, file_name, path):
    response = urllib2.urlopen(download_url)
    file = open(path+"/"+file_name, 'wb')
    file.write(response.read())
    file.close()


def download_last_issue():
    # We first have to go to the download page of the last issue
    
    # This trick of header helps to get a response, otherwise the server ignores the request
    
    site_global = "http://emagazinepdf.com/?s=bloomberg"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    req = urllib2.Request(site_global, headers=hdr)
    page = urllib2.urlopen(req)
    
    
    soup = BeautifulSoup(page, "lxml")
    
    url_last_bloomberg_buisness = ""
    
    # We then look for the most recent Bloomberg Buissnessweek USA and not Middle East edition
    
    articles = soup.find_all('article')
    for article in articles:
        h2 = article.find('h2', class_='cb-post-title')
        if("Middle East" not in h2.text):
            url_last_bloomberg_buisness = h2.find('a').get('href')
            break
    
    
    
    
    # And then proceed to the download
    
    req = urllib2.Request(url_last_bloomberg_buisness, headers=hdr)
    page = urllib2.urlopen(req)
    
    soup = BeautifulSoup(page, "lxml")
    div = soup.find('div', class_='vk-att-item')
    a = div.find('a')
    file_name = a.text[1:]
    url_download = a.get('href')
    
    init_database()
    
    if(is_present(file_name) == False):
        
        store_data(file_name)
    
        req = urllib2.Request(url_download, headers=hdr)
        page = urllib2.urlopen(req)
        
        # Downloading the file
        path = "data/business_week_issues"
        download_file(url_download, file_name, path)
        
        return file_name
    else:
        return "Error"