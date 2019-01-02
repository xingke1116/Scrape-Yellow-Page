from bs4 import BeautifulSoup
import requests
import unicodedata
import time
import csv

### Scraping Yellow Page Business Card
### v0.9
### 12/28/2018

## parameters
SEARCH_TERM = "sushi"
GEO_CITY = "Chicago"
GEO_STATE = "IL"
START_PAGE = "1"

OUT_PUT_FILE = "test_results.csv"
OUT_PUT = "C:/Users/xingk/Desktop/Booty Bay/" + OUT_PUT_FILE

## making functions for scaping
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

# get ready for everything
def get_ready (first_url):
    # open url with request
    raw_page = requests.get(first_url)
    # parse html
    hot_soup = BeautifulSoup(raw_page.content, "html5lib")
    return hot_soup

## scraping everything
# standard page url format
start_url = "https://www.yellowpages.com/search?search_terms=" + SEARCH_TERM + \
            "&geo_location_terms=" + GEO_CITY + "%2C%20" + GEO_STATE + "&page=" + START_PAGE

# make a empty list ready for results
accum_result = []

# loop through pages scraping results
while True:
    hot_soup = get_ready(start_url)
    content_list = hot_soup.find_all(class_='v-card')
    page_result = make_a_list_of_result(content_list)
    accum_result.extend(page_result)
    time.sleep(180)
    try:
        start_url = "https://www.yellowpages.com" + grab_url(hot_soup,'next ajax-page')
    except:
        break

for i in range(len(accum_result)):
    if accum_result[i]['city'] is None:
        accum_result[i]['city'] = None
    else:
        accum_result[i]['city'] = unicodedata.normalize("NFKD", accum_result[i]['city'])

## save results as csv file
keys = accum_result[0].keys()
with open(OUT_PUT, "w") as ooo:
    writer = csv.DictWriter(ooo, keys,lineterminator='\n')
    writer.writeheader()
    writer.writerows(accum_result)
