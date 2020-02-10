import sys
from urllib.request import urlopen
from scrapy.http import TextResponse
import scrapy
import requests
import time
import json
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
import threading 
from scrapy_splash import SplashRequest

def scrap(link):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    try:
        response =  requests.get(link, verify=False)
    except:
        try:
           time.sleep(0.5)
           response =  requests.get(link, verify=False)
        except:
            try:
                time.sleep(0.5)
                response =  requests.get(link, verify=False)
            except:
                return


    response = TextResponse(body=response.content, url=link)
    dataOptions = response.css(".tv-chart-view::attr(data-options)").extract()

    print(dataOptions)

    tempJson = json.loads(dataOptions[0])
    contents = json.loads(tempJson['content'])
    sources = contents['panes'][0]['sources'];

    for s in sources:
        if s['type'] == 'StudyStrategy':
            source = s
            break

    if source is None:
        return

    trades = source['data']['reportData']['trades']

    orders = []
    id = 1  
    for t in trades:
        entry1 = t['e']
        entry2 = t['x']

        order={}
        order["id"] = id
        order["Contacts"] = t["q"]
        order["Profit"] = {}
        order["Profit"]["dollar"] = "$" + str(round(t["pf"],2))
        order["Profit"]["percentage"] = str(round(t["pfp"]*100,2)) + "%"

        order["Entry"] = {}
        order["Entry"]["Type"] = "Entry Long" if entry1["tp"] == "le" else "Entry Short"
        order["Entry"]["Signal"] = "Long" if entry1["c"] == "Long" else "Short"
        order["Entry"]["Price"] = entry1["p"]
        order["Entry"]["DateTime"] = time.strftime("%Y-%m-%d %H:%M", time.gmtime(entry1["tm"]/1000))

        order["Exit"] = {}
        order["Exit"]["Type"] = "Exit Long" if entry2["tp"] == "lx" else "Exit Short"
        order["Exit"]["Signal"] =  "Long" if entry2["c"] == "Long" else "Short"
        order["Exit"]["Price"] = entry2["p"]
        order["Exit"]["DateTime"] = time.strftime("%Y-%m-%d %H:%M", time.gmtime(entry2["tm"]/1000))
        
        orders.append(order)
        
        # print(order)
        id += 1

    f = open("orders.json", "w+")
    f.write(str(orders).replace("'","\""))
    print(orders)
    print('\n\nPlease wait one minute for next check\n\n')
    
    timer = threading.Timer(60.0, scrap, [link]) 
    timer.start()

print('starting...')
arguments = len(sys.argv) - 1
# link = "https://www.tradingview.com/chart/BTCUSD/rNOu4egQ-upwork/"
link = "https://www.tradingview.com/chart/ftkFTxnr/"

if(arguments > 0):
    scrap(sys.argv[1])
else:
    scrap(link)
