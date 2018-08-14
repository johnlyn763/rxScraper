from bs4 import BeautifulSoup
import bs4 
from datetime import datetime
import sys
import requests
import json

print (sys.version)

url = "https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm"

navigate_root = "https://www.accessdata.fda.gov/scripts/drugshortages/"

result = requests.get(url)
html = result.content

soup = BeautifulSoup(html, 'html.parser')

shortages=[]
the_div = soup.find("div", {"id":"tabs-1"})
table = soup.find("table")

# Get the basic list of shortages (headers)
for shortage in table.findAll("tr"):
    if not shortage.text.startswith("\nGeneric Name"):
        header = []
        link= shortage.find('td').find('a').findNextSibling().get('href')
        header.append(link)
        for col in shortage.find_all(['th','td']):
            header.append(' '.join(col.text.split()))
        shortages.append(header)  # <==== todo: add nice names, using dict 
        # [0] Shortage Details URL
        # [1] Shortage Generic Name
        # [2] Shortage Status
        # [3] Shortage Revision Date

# Get details for each row of shortages
for shortage in shortages:
    print("Working on %s - %s" % (shortage[1], shortage[2]))
    url = navigate_root + shortage[0].replace(' ','%20')
    result = requests.get(url)

    html = result.content
    soup = BeautifulSoup(html, 'html.parser')
    
    for si in soup.find("p",{"style":"margin-left:15px;"}).find_all("span"):
        if isinstance(si, bs4.element.Tag):
            if (si.text.upper().find("POSTED:") > -1) or (si.text.upper().find("CATEGORIES:") > -1):
                header.append(' '.join(si.nextSibling.split()))

    tt = soup.find(id="accordion")
    products = []
    if not tt is None and len(tt) > 0:
        for x in tt.find_all("h3"):
            thisCompany = x.text
            products = []
            if not x.nextSibling.nextSibling.find("table") is None:
                for shortageTable in x.nextSibling.nextSibling.find("table"):
                    if not isinstance(shortageTable, bs4.element.NavigableString):
                        for row in shortageTable.find_all("tr"):
                            if row.contents[1].text != "Presentation":
                                product = {"supplier": ' '.join(thisCompany.split()), 
                                            "presentation": row.contents[1].text, 
                                            "availability": ' '.join(row.contents[3].text.split()),
                                            "relatedInfo" : ' '.join(row.contents[5].text.split()),
                                            "shortageReason" : ' '.join(row.contents[7].text.split())
                                            }
                                products.append(product)
                if len(products) > 0:
                    shortage.append(products)

    # next step: put it all into JSON doc
    if not tt is None and len(tt) > 0:
        # outJSON = json.dumps(shortage)
        with open(datetime.now().strftime("FDA_shortage_%Y%m%d_%H%M%S.json"), 'w') as f:
            json.dump(shortage, f)

