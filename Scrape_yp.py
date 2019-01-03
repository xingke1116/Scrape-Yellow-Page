from bs4 import BeautifulSoup
import requests
import unicodedata
import time
import csv
import re

'''
Scraping Yellow Page Business Card
v1.1
1/3/2019
'''

'''
INPUT PARAMETERS
'''
SEARCH_TERM = "sushi"
# GEO_CITY can be omitted if want to search for the entire state, e.g. GEO_CITY = ""
GEO_CITY = "chicago"
GEO_STATE = "IL"
START_PAGE = "1"
# OUT_PUT_FILE can be omitted, e.g. OUT_PUT_FILE = ""
# if OUT_PUT_FILE is omitted, file name will be SEARCH_TERM + GEO_CITY + GEO_STATE
OUT_PUT_FILE = "YP_scrape_results"
OUT_PUT_PATH = "C:/Users/xingk/Desktop/Booty Bay/"

'''
making functions for scaping
'''
# if null blank else scape for text
def grab_text (cards,attr):
    return None if cards.find(class_=attr) is None else cards.find(class_=attr).text

# if null blank else scape for url
def grab_url (cards,attr):
    return None if cards.find(class_=attr,href=True) is None else cards.find(class_=attr,href=True)['href']

# if null blank, if none standard address, then text, else standard address
def grab_address (address,street):
    if address is None:
        return None
    if (street is None and address is not None):
        return address
    else:
        return address.replace(street, "")

# get ready for everything
def get_ready (first_url):
    # open url with request
    raw_page = requests.get(first_url)
    # parse html
    hot_soup = BeautifulSoup(raw_page.content, "html5lib")
    return hot_soup

# go through each result
def make_a_list_of_result (cold_soup):
    page_result = []
    for i in cold_soup:
        df = {}
        df["name"] = grab_text(i,'business-name')
        temp_street = grab_text(i,'street-address')
        df["address"] = temp_street
        temp_city_zip = grab_text(i,'adr')
        df["city"] = grab_address(temp_city_zip,temp_street)
        df["phone"] = grab_text(i,'phones phone primary')
        df["website"] = grab_url(i,'track-visit-website')
        page_result.append(df)
    return page_result

# normalize unicode in the result
def normalize_unicode (result):
    for i in range(len(result)):
        if result[i]['city'] is None:
            result[i]['city'] = None
        else:
            result[i]['city'] = unicodedata.normalize("NFKD", result[i]['city'])

'''
now scraping
'''
# generate url
def city_check ():
    if GEO_CITY == "":
        return GEO_STATE
    else:
        return GEO_CITY + "%2C%20" + GEO_STATE

GEO_INFO = city_check ()

# standard page url format
start_url = "https://www.yellowpages.com/search?search_terms=" + SEARCH_TERM + \
            "&geo_location_terms=" + GEO_INFO + "&page=" + START_PAGE

# create output fie
def output_check ():
    if OUT_PUT_FILE == "" and GEO_INFO == "":
        return OUT_PUT_PATH + SEARCH_TERM + "_" + GEO_STATE + ".csv"
    if OUT_PUT_FILE == "" and len(GEO_CITY) > 0:
        return OUT_PUT_PATH + SEARCH_TERM + "_" + GEO_CITY + "_" + GEO_STATE + ".csv"
    else:
        return OUT_PUT_PATH + OUT_PUT_FILE + ".csv"

OUT_PUT = output_check ()

# make a empty list ready for results
page_result = [{'name':None,'address':None,'city':None,'phone':None,'website':None}]

# creat the empty output file
keys = page_result[0].keys()
with open(OUT_PUT, "w") as ooo:
    writer = csv.DictWriter(ooo, keys, lineterminator='\n')
    writer.writeheader()
print("Empty output csv file has been created at " + OUT_PUT_PATH)

## to save results as csv file
def append_csv (result):
    keys = result[0].keys()
    with open(OUT_PUT, "a") as ooo:
        writer = csv.DictWriter(ooo, keys, lineterminator='\n')
        writer.writerows(result)

# loop through pages scraping results
while True:
    print("Now scraping ", re.findall(r'page=[0-9]{1,}', start_url)[0].replace("=", " "))
    hot_soup = get_ready(start_url)
    content_list = hot_soup.find_all(class_='v-card')
    page_result = make_a_list_of_result(content_list)
    normalize_unicode(page_result)
    append_csv(page_result)
    print(len(page_result), "results from", re.findall(r'page=[0-9]{1,}', start_url)[0].replace("=", " "),
          "have been saved to", OUT_PUT)
    try:
        start_url = "https://www.yellowpages.com" + grab_url(hot_soup,'next ajax-page')
        print("Process will be paused for 180 seconds")
        time.sleep(3)
    except:
        print("Process finished!")
        break




