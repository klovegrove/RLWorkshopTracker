from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re

class WorkshopMap:
    def __init__(self):
        self.name = ''
        self.author = ''
        self.description = ''
        self.imgLink = ''
        self.mapLink = ''        

def getDescription(script):
    pattern = '(?<=\"description\"\:).*(?=\,\"user_subscribed\")'
    found = ''

    script = str(script)
    # print(script)

    try:
        found = re.search(pattern, script).group(0)    
    except AttributeError as err:
        found = ''

    return found

def getWorkshopMaps():
    driver = webdriver.Chrome()
    driver.get('https://steamcommunity.com/workshop/browse/?appid=252950&browsesort=trend&section=readytouseitems&actualsort=trend&p=1&days=-1')

    workshopMaps = list()
    
    content = driver.page_source
    soup = BeautifulSoup(content)
    for a in soup.findAll('div', attrs={'class':'workshopItem'}):
        map = WorkshopMap()
        map.name = a.find('div', attrs={'class':'workshopItemTitle'}).text
        map.author = a.find('div', attrs={'class':'workshopItemAuthorName'}).find('a').text 
        map.imgLink = a.find('a', attrs = {'class': 'ugc'}).find('div', attrs = {'class': 'workshopItemPreviewHolder'}).find('img', attrs = {'class': 'workshopItemPreviewImage'})['src']
        map.mapLink = a.find('a', attrs = {'class': 'ugc'})['href']
        
        script = a.next_sibling.next_sibling

        map.description = getDescription(script)

        workshopMaps.append(map)
        
        # print(f'Map Name: {map.name}')
        # print(f'Map Author: {map.author}')
        # print(f'Tumbnail Link: {map.imgLink}')
        # print(f'Map Link: {map.mapLink}')
        # print('---------------------------------\n')

    driver.quit()

    return workshopMaps

# x = getWorkshopMaps()

# for map in x:
#     print(map.name)