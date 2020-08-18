# Demo file for Spyder Tutorial
# Hans Fangohr, University of Southampton, UK

import requests
from bs4 import BeautifulSoup
import re
from sortedcontainers import SortedSet

class WebsiteContacts:
    """
    The WebsiteContacts module is used to extract contact information from a website given a url.
    Given a url, the module will extract the emails, facebooks, instragrams, twitters, and linkedins
    on all pages of a website containing 'about' or 'contact' in the relative url.
    """
    
    def __init__(self, url="", emails=None, facebooks=None, instagrams=None, twitters=None, linkedins=None):
        self._url = url
        emptyCnt = 0
        if emails == None:
            emails = SortedSet()
            emptyCnt += 1
        if facebooks == None:
            facebooks = SortedSet()
            emptyCnt += 1
        if instagrams == None:
            instagrams = SortedSet()
            emptyCnt += 1
        if twitters == None:
            twitters = SortedSet()
            emptyCnt += 1
        if linkedins == None:
            linkedins = SortedSet()
            emptyCnt += 1
          
        self._emails = emails
        self._facebooks = facebooks
        self._instagrams = instagrams
        self._twitters = twitters
        self._linkedins = linkedins
        
        # only find contacts if all fields other than url are empty
        if url != "" and emptyCnt == 5:
            self.__find_contacts()
    
    def __sorted_set_to_string(self, convert_set):
        """Converts the sorted set to a string with values separated by commas.
        
        Pre:
            self: WebsiteContacts object
            convert_set: the set to be converted
        Post:
            None
        Return:
            returnStr: the formatted string from the convert_set
        """
        returnStr = ''
        for i in range(len(convert_set)):
            returnStr += convert_set[i] + ', '
        returnStr = returnStr[:len(returnStr)-2]
        return returnStr
    
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, url):
        self._url = url
    
    @property
    def emails(self):
        return self.__sorted_set_to_string(self._emails)
    
    @emails.setter
    def emails(self, emails):
        self._emails = emails
    
    @property
    def facebooks(self):
        return self.__sorted_set_to_string(self._facebooks)
    
    @facebooks.setter
    def facebooks(self, facebooks):
        self._facebooks = facebooks
    
    @property
    def instagrams(self):
        return self.__sorted_set_to_string(self._instagrams)
    
    @instagrams.setter
    def instagrams(self, instagrams):
        self._instagrams = instagrams
    
    @property
    def twitters(self):
        return self.__sorted_set_to_string(self._twitters)
    
    @twitters.setter
    def twitters(self, twitters):
        self._twitters = twitters
        
    @property
    def linkedins(self):
        return self.__sorted_set_to_string(self._linkedins)
    
    @linkedins.setter
    def linkedins(self, linkedins):
        self._linkedins = linkedins
    
    
    def __extract_urls(self, html, root):
        """Extracts all URLs with shared roots from a given webpage.
        
        Pre:
            self: WebsiteContacts object
            html: html of webpage
            root: root of URL
        Post:
            None
        Return:
            URLs: set of URLs associated with the given root
        """
        
        #print("Root is:", root)
        #print()
        soup = BeautifulSoup(html, 'lxml')
        
        urls = set()
        for a in soup.find_all('a', href=True):
            if (a['href'].find(root) == 0):
                urls.add(a['href'])
                #print("Found URL:", a['href'])
            # else if only relative URL
            elif (len(a['href']) > 0 and a['href'][0] == '/'):
                urls.add(root + a['href'])
                #print("Found URL:", root + a['href'])
                
        #print(urls)
        return urls
    
    def __decode_email(self, email):
        """Decodes encoded email.
        
        Pre:
            self: WebsiteContacts object
            email: encoded email
        Post:
            None
        Return:
            decoded: decoded email
        """
        
        decoded = ''
        key = int(email[:2], 16)
    
        for i in range(2, len(email)-1, 2):
            decoded += chr(int(email[i:i+2], 16)^key)   # ^ stands for XOR
    
        return decoded
    
    def __find_contacts(self):
        """Finds emails of a blog given the root URL.
        
        Pre: 
            self - WebsiteContacts object
        Post:
            self.emails: updated set of emails
            self.facebooks: updated set of facebooks
            self.instagrams: updated set of instagrams
            self.twitters: updated set of twitters
            self.twitters: updated set of linkedins
        Return:
            None
        """
        
        # find domain start given root URL
        domain_start = 0
        for i in range(len(self._url)-1, 0, -1):
            if self._url[i] == ".":
                domain_start = i
                break
        # find domain end given root URL
        domain_end = 0
        for i in range(len(self._url)-1, domain_start, -1):
            if self._url[i] == '/':
                domain_end = i
                break
        if domain_end == 0:
            domain_end = len(self._url)-1
        
        domain = self._url[domain_start : domain_end]
                
        # setup for while loop conditions
        visited = set()
        urls = [self._url]
        i = 0
        
        while i < min(200, len(urls)):
            url = urls[i]
            i += 1
            
            # if URL in visited then skip to the next iteration
            if url in visited:
                continue
            # otherwise add the URL to set of visited URLs
            visited.add(url)
            
            # print URL to be tried
            #print("Trying:", url);
            
            try:
                html = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}).text
            except:
                print ("HTML from", url, "was not extracted.")
                # if HTML was not extracted, continue to next iteration
                continue
            
            if len(re.findall('(contact|about|our team|board of)', url)) != 0:
                # list of emails found on URL
                url_emails = re.findall('[a-z0-9-_]+@[a-z0-9-_]+.com', html, re.IGNORECASE)
                encoded_url_emails = re.findall("data-cfemail=\"[a-z0-9]{38}\"", html)
                    
                # list of SNS contact found on URL
                url_facebooks = re.findall('facebook.com/[@a-z0-9-_]+/?\"', html, re.IGNORECASE)
                url_instagrams = re.findall('instagram.com/[@a-z0-9-_]+/?\"', html, re.IGNORECASE)
                url_twitters = re.findall('twitter.com/[@a-z0-9-_]+/?\"', html, re.IGNORECASE)
                url_linkedins = re.findall('linkedin.com/[@a-z0-9-_]+/?\"', html, re.IGNORECASE)
                
                # find email contacts
                for email in url_emails:
                    self._emails.add(email.lower())
                for email in encoded_url_emails:
                    self._emails.add(self.__decode_email(email[-39:-1]).lower())
                
                # find SNS contacts
                for facebook in url_facebooks:
                    if (facebook[-2 : -1] == '/'):
                        self._facebooks.add(facebook.lower()[:-2])
                    else:
                        self._facebooks.add(facebook.lower()[:-1])
                for instagram in url_instagrams:
                    if (instagram[-2 : -1] == '/'):
                        self._instagrams.add(instagram.lower()[:-2])
                    else:
                        self._instagrams.add(instagram.lower()[:-1])
                for twitter in url_twitters:
                    if (twitter[-2 : -1] == '/'):
                        self._twitters.add(twitter.lower()[:-2])
                    else:
                        self._twitters.add(twitter.lower()[:-1])
                for linkedins in url_linkedins:
                    if (linkedins[-2 : -1] == '/'):
                        self._linkedins.add(linkedins.lower()[:-2])
                    else:
                        self._linkedins.add(linkedins.lower()[:-1])
            
            # look for additional URLs only if its the first iteration
            if i == 1:
                for next_urls in self.__extract_urls(html, url[:url.find(domain)+4]):
                    urls.append(next_urls);
    
    def __repr__(self):
        """Convert to formal string, for repr().
        
        Pre:
            self: WebsiteContacts object
        Post:
            None
        Return:
            string representing WebsiteContact constructor with corresponding contents

        """
        
        return "WebsiteContacts({}, {}, {}, {}, {}, {})".format(self._url, self._emails, self._facebooks, self._instagrams, self._twitters, self._linkedins)
                
    def return_contacts(self, contacts):
        """The contacts of the contact type are printed.
        
        Pre:
            self: WebsiteContacts object
            contacts: set or sorted set of contacts
        Post:
            None
        Return:
            items in contacts returned
        """
        
        returnStr = ""
        if len(contacts) == 0:
            returnStr = 'None\n'
        else:
            for contact in contacts:
                returnStr += contact + '\n'
        return returnStr
    
    def __str__(self):
        """All contacts in the object are formatted to a string.
        
        Pre:
            self: WebsiteContacts object
        Post:
            all contacts printed
        Return:
            None
        """
        
        returnStr = 'URL: ' + self.url + '\n'
        returnStr += 'Email(s):\n' + self.return_contacts(self._emails) + '\n'
        returnStr += 'Facebook(s):\n' + self.return_contacts(self._facebooks) + '\n'
        returnStr += 'Instagram(s):\n' + self.return_contacts(self._instagrams) + '\n'
        returnStr += 'Twitter(s):\n' + self.return_contacts(self._twitters) + '\n'
        returnStr += 'LinkedIn(s):\n' + self.return_contacts(self._linkedins)
        return returnStr


if __name__ == '__main__':
    contact = WebsiteContacts('http://fitlittlecookie.wordpress.com/')
    print(str(contact))