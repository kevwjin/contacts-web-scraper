#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 12:59:24 2020

@author: kevinjin
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from datetime import datetime, timedelta
from sortedcontainers import SortedSet

class GoogleSearch:
    """
    The GoogleSearch class visits sites from a GoogleSearch to extract relevant sites for the WebContactScraper
    module to scrape contact information.
    """
    
    def __init__(self, query):
        """Sets up the Google Search.
        
        Pre:
            query: keywords to be searched
        Post:
            The Google Search URL is built from the query, replacing whitespace with '+'. The member
            variable _url_list is assigned values from the __extract_urls() function.
        Return:
            None
        """
        self._query = query
        append_query = self._query.replace(' ', '+')
        self._search_url = "https://google.com/search?q=" + append_query
        self._url_list = self.__extract_search_urls()
        self._website_list = self.__extract_websites()
        #for url in self._url_list:
            #print(url)
        #for website in self._website_list:
            #print(website)

    @property
    def website_list(self):
        return self._website_list
    
    @property
    def url_list(self):
        return self._url_list

    def __file_search_limit(self):
        """Limits the program to one search every 10 minutes to prevent overloading of Google's servers.
        
        Pre:
            None
        Post:
            The last time read is written to the PrevSearchTime.txt file.
        Return:
            10: indicates that the last search was at least 10 minutes ago
            diff_time: amount of time since the last time searched
        
        """
        
        curr_time = datetime.now()
        #print(curr_time)
        
        with open('PrevSearchTime.txt', 'r') as reader:
            prev_time_str = reader.read()
            if prev_time_str == '':
                with open('PrevSearchTime.txt', 'w') as writer:
                    writer.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                return 10
            prev_time = datetime.strptime(prev_time_str, '%d/%m/%Y %H:%M:%S')
            diff_time = curr_time - prev_time
            if diff_time > timedelta(minutes = 10):
                with open('PrevSearchTime.txt', 'w') as writer:
                    writer.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                return 10
            else:
                return diff_time

    def __extract_search_urls(self):
        """Extracts all URLs on the first page of the Google Search.
        
        Pre:
            None
        Post:
            If the file search limit is not met, the program will print the number of minutes until it
            will begin scraping again. The program will set a timer so that it will continue to run 10
            minutes after the last search.
        Return:
            urls: a list of urls extracted from the Google Search page

        """
        
        # find the time remaining and put a timer to that amount of time
        file_search_limit = self.__file_search_limit()
        if file_search_limit != 10:
            remaining_secs = (10 * 60) - int(file_search_limit.total_seconds())
            print('The program will automatically scrape in {} minutes. Please wait.'.format(round(remaining_secs/60)))
            #time.sleep(remaining_secs)
        
        html = requests.get(self._search_url).text        
        soup = BeautifulSoup(html, 'lxml')
        
        # TODO: find way to traverse pages in Google Search
        urls = SortedSet()
        #pages = []
        for a in soup.find_all('a', href=True):
            if '/url?q=' in a['href'] and 'google.com' not in a['href']:
                url_end = a['href'].find('&sa=U')
                urls.add(a['href'][7:url_end])
        #for a in soup.find_all('a', aria-label=True, href=True):
            #if '/search?q=' in a['href']:
                #pages.add(a['href'])
        
        return urls
    
    def __extract_domain(self, url):
        # find domain end given URL
        domain_name_end = 0
        for i in range(len(url)-1, 0, -1):
            if url[i] == '.':
                domain_name_end = i
                break
        # find domain start given URL
        domain_name_start = 0
        for i in range(domain_name_end-1, 0, -1):
            if url[i] == "/" or url[i] == ".":
                domain_name_start = i+1
                break
        return url[domain_name_start : domain_name_end]
    
    def __extract_websites(self):
        """Extracts all websites listed on the website from the _url_list.
        
        Pre:
            None
        Post:
            None
        Return:
            
        """
        
        url_websites = SortedSet()
        
        for url in self._url_list:
            
            domain = self.__extract_domain(url)
            
            try:
                html = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}).text
                soup = BeautifulSoup(html, 'lxml')
            except:
                print('The HTML from', url, 'could not be extracted.')
                # if HTML was not extracted, continue to next iteration
                continue
            
            # appends all urls from the website
            for link in soup.find_all('a', attrs={'href': re.compile("https?://")}):
                if domain in link['href'] or 'http' not in link['href'] or len(re.findall('(facebook|twitter|instagram|linkedin|youtube|pinterest|tumblr|itunes)', link['href'])) != 0:
                    continue
                parsed_link = urlparse(link['href'])
                root_link = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_link)
                
                url_websites.add(str(root_link))
                
        return url_websites
    
if __name__ == '__main__':
    google = GoogleSearch('top 100 fitness blogs')