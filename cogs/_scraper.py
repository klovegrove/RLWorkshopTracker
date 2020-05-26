from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import _json

## What I want this to do:
#### 1. Get data from steam
#### 2. Put the data into objects
#### 3. Write the data to a json file
#### 4. Return the data to the bot right away as well,
####    instead of making the bot read the json
# -- I'll probably have this only run once, or maybe monthly? And then do a compare and add any new maps in 

class WorkshopMap:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.nicknames = []
        self.author = ''
        self.description = ''
        self.imgLink = ''
        self.mapLink = ''
        self.trackingData = ''

def getDescription(script):
    pattern = '(?<=\"description\"\:\").*(?=\"\,\"user_subscribed\")'
    found = ''

    script = str(script)

    try:
        found = re.search(pattern, script).group(0)    
    except AttributeError as err:
        found = ''

    # Parse the description to make it more readable
    remove = ['<br \\/>', '\\n', '\\r', '\\']
    result = found

    for i in remove:
        new = ''

        if (i == '\\n'):
            new = '\n'

        found = found.replace(i, new)

    return found

def getSteamURL(link):
    start = link.find('id=') + 3
    result = link[start : start + 10 ]
    return result

def getWorkshopMaps(maps = []):
    #driver = webdriver.Chrome()
    with webdriver.Chrome() as driver:
        driver.get('https://steamcommunity.com/workshop/browse/?appid=252950&browsesort=trend&section=readytouseitems&actualsort=trend&p=1&days=-1')

        workshopMaps = []
        idList = [x.id for x in maps]
        changedIds = []

        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        for a in soup.findAll('div', attrs={'class':'workshopItem'}):
            map = WorkshopMap()
            map.id = a.find('a', attrs = {'class': 'ugc'})['data-publishedfileid']
            map.name = a.find('div', attrs={'class':'workshopItemTitle'}).text
            map.nicknames = [map.name.lower()]
            map.author = a.find('div', attrs={'class':'workshopItemAuthorName'}).find('a').text 
            map.imgLink = a.find('a', attrs = {'class': 'ugc'}).find('div', attrs = {'class': 'workshopItemPreviewHolder'}).find('img', attrs = {'class': 'workshopItemPreviewImage'})['src']
            map.mapLink = a.find('a', attrs = {'class': 'ugc'})['href']
            
            script = a.next_sibling.next_sibling

            map.description = getDescription(script)

            # if the id is in the list, add the existing trackingData
            if (map.id in idList):
                map.trackingData = [ x for x in maps if x.id == map.id ][0].trackingData
                map.nicknames = [ x.nicknames for x in maps if x.id == map.id]

            workshopMaps.append(map)
            changedIds.append(map.id)        

    #driver.quit()

    unchangedMaps = [x for x in maps if x.id not in changedIds]

    unchangedMaps.extend(workshopMaps)

    workshopMaps = unchangedMaps

    return workshopMaps

# x = getWorkshopMaps()

# for map in x:
#     print(map.name)