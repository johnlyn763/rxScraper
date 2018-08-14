from bs4 import BeautifulSoup
from datetime import datetime
import sys
import requests
import json

def bulletedListInfo(theSoup, theDiv):
    divContents = theSoup.find("div", {"id":theDiv})
    items = []
    if divContents:
        if divContents.find("ul").contents[1].find("ul"):
            for singleItem in divContents.find("ul").contents[1].find("ul"):
                items.append(singleItem.text)
    return items        

def numberedListInfo(theSoup, theDiv):
    divContents = theSoup.find("div", {"id":theDiv})
    items = []
    if divContents:
        if divContents.find("ul").contents[1].find("ol"):
            for singleItem in divContents.find("ul").contents[1].find("ol"):
                items.append(singleItem.text)
    return items

print (sys.version)


# TODO:
# https://www.ashp.org/Drug-Shortages/Current-Shortages/Drug-Shortage-Detail.aspx?id=200
# use this one for References dev:
# https://www.ashp.org/drug-shortages/current-shortages/Drug-Shortage-Detail.aspx?id=282


url= "https://www.ashp.org/Drug-Shortages/Current-Shortages/Drug-Shortages-List?page=All"
navigate_root = "https://www.ashp.org/Drug-Shortages/Current-Shortages/"

result = requests.get(url)
html = result.content

soup = BeautifulSoup(html, 'html.parser')

shortages=[]
table = soup.find("table", {"id":"1_dsGridView"})

# Get the basic list of shortages (headers)
for shortage in table.findAll("tr"):
    if not shortage.text.startswith("\nGeneric Name"):
        header = []
        link = shortage.find('a').get('href')
        header.append(link)
        for col in shortage.find_all(['th','td']):
            header.append(col.text)
        shortages.append(header)
        # [0] Shortage Details URL
        # [1] Shortage Generic Name
        # [2] Shortage Status
        # [3] Shortage Revision Date

# Get details for each row of shortages
for shortage in shortages:
    print("Working on %s - %s" % (shortage[1], shortage[2]))
    url = navigate_root + shortage[0]
    result = requests.get(url)
    html = result.content
    soup = BeautifulSoup(html, 'html.parser')

    # DIVs:
    affectedProds = bulletedListInfo(soup,"1_Affected")
    shortageReasons = bulletedListInfo(soup,"1_Reason")
    availableProds = bulletedListInfo(soup,"1_Avaliable")
    resupplyDates = bulletedListInfo(soup,"1_Resupply")
    implications = bulletedListInfo(soup,"1_Implications")
    safety = bulletedListInfo(soup,"1_Safety")
    alternatives = bulletedListInfo(soup,"1_Alternatives")
    references = numberedListInfo(soup,"1_References")

    # next step: put it all into JSON doc
    shortageOut = {"shortageName" : shortage[1],
                   "shortageStatus" : shortage[2],
                   "shortageRevisionDate" : shortage[3],
                   "shortageAshpURL" : url,
                   "fileCreateDate" : datetime.now().strftime("%c"),
                   "affectedProds": affectedProds,
                   "shortageReasons":shortageReasons,
                   "availableProds":availableProds,
                   "resupplyDates": resupplyDates,
                   "implications": implications,
                   "safety": safety,
                   "alternatives": alternatives,
                   "references": references}

    # outJSON = json.dumps(shortageOut)
    with open(datetime.now().strftime("ASHP_shortage_%Y%m%d_%H%M%S.json"), 'w') as f:
        json.dump(shortageOut, f)

