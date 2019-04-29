#!/usr/bin/env python
# coding: utf-8

# # Mars Web Scraping Project (using Selenium, MongoDB and Flask)

# Dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
import pandas as pd
import time

#Selenium
executable_path = {'executable_path':'C:/ChromeDriver/chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless=True)

#PyMongo
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.marsscrape_db
collection = db.items

def scrape ():
    # # Latest Mars News from Nasa

    #Use this url as the scraping target
    nasa_news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    #Use url client
    nasaresponse = requests.get(nasa_news_url)
    #Make some Nasa news soup
    nasa_news_soup = bs(nasaresponse.text, 'html.parser')
    #Getting the list element closest to the p value and storing in a variable
    news_p = nasa_news_soup.find("div", class_="rollover_description_inner").text.strip()
    #Getting the list element closes to the tile and storing in a variable
    news_title = nasa_news_soup.find("div", class_="content_title").text.strip()
    print(news_p)
    print(news_title)
    # #  JPL Featured Mars Image

    #Use this url as the scraping target
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars#submit"
    browser.visit(jpl_url)
    html = browser.html
    jpl_soup = bs(html, 'html.parser')
    #click 'FULL IMAGE' and then 'more info'
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(10)
    browser.click_link_by_partial_text("more info")
    #Feed HTMl and Parse
    html = browser.html
    jpl_feature_soup = bs(html, 'html.parser')
    jpl_feature_image_links = jpl_feature_soup.find_all('div', class_='download_tiff')
    #Empty list to store output of for loop
    link_list = []
    #Getting all links
    for item in jpl_feature_image_links:
        link = item.find('a')['href']
        link_list.append(link)
    #Getting the second item and appending to the first part of the url
    jpgend = link_list[1]
    featured_image_url = ('https:' + jpgend)
    print(featured_image_url)
    # # Latest Mars Weather Report - Twitter

    #Acquiring scrape target
    mars_twitter = 'https://twitter.com/marswxreport?lang=en'
    #Use url client
    twitterresponse = requests.get(mars_twitter)
    #Make some twitter weather soup
    mars_weather_parsed = bs(twitterresponse.text, 'html.parser')
    #selecting the top tweet and stripping text
    mars_weather = mars_weather_parsed.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text.strip()
    print(mars_weather)
    # # Mars Facts from Space-Facts.com

    #Acquiring scraping target
    mars_facts_url = 'https://space-facts.com/mars/'
    factstable = pd.read_html(mars_facts_url)
    #reference first item in list
    factstable_ = factstable[0]
    #df to html
    mars_facts = factstable_.to_html(index=False, header=False).strip()
    factstable_.to_html('mars_facts.html', index=False, header=False)
    print(mars_facts)
    # # Mars Hemisphere Images from USGS.gov

    #ACQUIRING TARGET URL
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemisphere_url)
    html = browser.html
    hemisphere_soup = bs(html, 'html.parser')
    hemisphere_results = hemisphere_soup.find_all("div", class_="description")
    #Holding titles and the links to be used to gather the full image url
    title = []
    link_list = []
    for result in hemisphere_results:
        title_text = result.find('h3').text.strip()
        link = result.a['href']
        title.append(title_text)
        link_list.append(link)
    img_url = []
    #Getting the full res image links
    i = 0
    j = 0
    while i < 4:
        page = 'https://astrogeology.usgs.gov' + link_list[j]
        browser.visit(page)
        html = browser.html
        hemisphere_page_soup = bs(html, 'html.parser')
        hemisphere_downloads = hemisphere_page_soup.find("div", class_='downloads')
        hemisphere_url = hemisphere_downloads.ul.a['href']
        img_url.append(hemisphere_url)
        i+=1
        j+=1
    img_url
    #Create a list of dictionaries based on title_list and img_url
    dict0 = dict({ "title" : title[0], "img_url": img_url[0]})
    dict1 = dict({ "title" : title[1], "img_url": img_url[1]})
    dict2 = dict({ "title" : title[2], "img_url": img_url[2]})
    dict3 = dict({ "title" : title[3], "img_url": img_url[3]})
    #Final list of dictionaries
    hemisphere_image_urls = [dict0,dict1,dict2,dict3]
    print(hemisphere_image_urls)

    #dictionary to store info in MongoDB
    scraped_data = {
        "news_title": news_title, 
        "news_p": news_p, 
        "featured_image_url": featured_image_url, 
        "mars_weather": mars_weather, 
        "mars_facts": mars_facts, 
        "hemisphere_image_urls":hemisphere_image_urls
        }
    
    return scraped_data 

    #Put it in MongoDB
    collection.insert_one(scraped_data)

#scrape()
# # make sure Scraped Data is in MongoDB

#listings = db.items.find()

#for listing in listings:
    #print(listing)
