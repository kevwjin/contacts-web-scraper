import gspread
from oauth2client.service_account import ServiceAccountCredentials
from WebContactScraper import WebsiteContacts
from GoogleSearchWebScraper import GoogleSearch
import csv
import sys
import os
from sortedcontainers import SortedSet

class WebContactSheet:
    """
    The WebContactSheetManager manages the contact gathered from the WebContactScraper module. In a
    Google Sheets file, the contacts are formatted by url, emails, Facebooks, Instagrams, Twitters, and
    LinkedIns.
    """
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    # note that in the online gspread docs, 'gc' is used instead of 'client'
    client = gspread.authorize(creds)
    # parameter for open is name of sheet
    # sheet1 specifies the sheet number sheet on the sheet to get access
    
    # test file_name is 'Contacts'
    def __init__(self, file_name):
        """Sets up the Google Sheet file.
        
        Pre:
            file_name: name of the file to access
        Post:
            Sheet1 and Sheet2 are linked to the WebContactSheet class. While Sheet1 provides the 
            extracted contact info, Sheet2 takes the keywords for a Google Search to find relevant
            websites to extract contact info from.

            - If no header is added to Sheet1 and/or Sheet2, then the respective header(s) will be added.
            - If contact info and search keywords are already on the respectie sheets, the initialization
              will update the row to insert the next contact info or search keywords.
        Return:
            None
        """
        
        self._file_names_sheet = self.client.open('ExistingFileNames').get_worksheet(0)
        
        # check whether the file_name is unique
        not_unique = True
        name = file_name
        while not_unique:
            unique_file_names = self._file_names_sheet.col_values(1)
            for unique_file_name in unique_file_names:
                if name == unique_file_name:
                    while True:
                        confirm = input('That file name already exists. Would you like to proceed? (Y/N): ').upper()
                        if confirm == 'Y':
                            not_unique = False
                            break
                        elif confirm == 'N':
                            sys.exit(0)
                not_unique = False
        
        four_sheets_warning = input('The file must contain 4 sheets for the program to work. Hit <ENTER> to proceed.')
            
        while True:
            try:
                # define sheets
                self._sheet1 = self.client.open(file_name).get_worksheet(0)
                self._sheet2 = self.client.open(file_name).get_worksheet(1)
                self._sheet3 = self.client.open(file_name).get_worksheet(2)
                self._sheet4 = self.client.open(file_name).get_worksheet(3)
                
                # insert header for sheet1 if not already added
                header1 = self._sheet1.row_values(1)
                if len(header1) == 0:
                    # inserting header row
                    header_row = ['url', 'emails', 'facebooks', 'instagrams', 'twitters', 'linkedins']
                    self._sheet1.insert_row(header_row, 1)
                
                # insert header for sheet2 if not already added
                header2 = self._sheet2.row_values(1)
                if len(header2) == 0:
                    # inserting header row
                    header_row = ['keyphrase', 'status']
                    self._sheet2.insert_row(header_row, 1)
                    
                # insert header for sheet2 if not already added
                header3 = self._sheet3.row_values(1)
                if len(header3) == 0:
                    # inserting header row
                    header_row = ['keyphrase', 'status']
                    self._sheet3.insert_row(header_row, 1)
                    
                # insert header for sheet2 if not already added
                header4 = self._sheet4.row_values(1)
                if len(header4) == 0:
                    # inserting header row
                    header_row = ['website', 'status']
                    self._sheet4.insert_row(header_row, 1)
                
                # define the number of urls
                self._num_urls = 0
                idx = 2
                url = self._sheet1.cell(idx, 1).value
                while url != '':
                    idx += 1
                    url = self._sheet1.cell(idx, 1).value
                self._num_urls = idx-2
                
                # list of new keyphrases written in Sheet2
                self._sheet2_keyphrases = []
                # define the number of searches, append searches to _sheet2_search_keyphrases
                self._sheet2_num_keyphrases = 0
                idx = 2
                search = self._sheet2.cell(idx, 1).value
                while search != '':
                    self._sheet2_keyphrases.append(search)
                    self._sheet2.update_cell(idx, 2, 'to scrape')
                    idx += 1
                    search = self._sheet2.cell(idx, 1).value
                self._sheet2_num_keyphrases = idx-2
                
                # list of new keyphrases written in Sheet3
                self._sheet3_keyphrases = []
                # define the number of searches, append searches to _sheet3_search_keyphrases
                self._sheet3_num_keyphrases = 0
                idx = 2
                search = self._sheet3.cell(idx, 1).value
                while search != '':
                    self._sheet3_keyphrases.append(search)
                    self._sheet3.update_cell(idx, 2, 'to scrape')
                    idx += 1
                    search = self._sheet3.cell(idx, 1).value
                self._sheet3_num_keyphrases = idx-2
                
                # list of new websites written in Sheet4
                self._sheet4_websites = []
                # define the number of searches, append searches to _sheet2_search_keyphrases
                self._sheet4_num_websites = 0
                idx = 2
                search = self._sheet4.cell(idx, 1).value
                while search != '':
                    self._sheet4_websites.append(search)
                    self._sheet4.update_cell(idx, 2, 'to scrape')
                    idx += 1
                    search = self._sheet4.cell(idx, 1).value
                self._sheet4_num_websites = idx-2
            
                break
            except:
                pause = input('The file does not contain 4 sheets. Once the file contains 4 sheets, hit <ENTER> to proceed.')
                    
    
    def append_row(self, url):
        """Scrapes the website of the given url, then appends a row with the scraped contacts to the sheets.
        
        Pre:
            url: the url of the website to have added information
        Post:
            row added to Google Sheets
        Return:
            None
        """
        
        tmp_website_contacts = WebsiteContacts(url)
        row = [tmp_website_contacts.url, tmp_website_contacts.emails, tmp_website_contacts.facebooks, tmp_website_contacts.instagrams, tmp_website_contacts.twitters, tmp_website_contacts.linkedins]
        self._sheet1.insert_row(row, self._num_urls + 2)
        
        # update number of urls
        self._num_urls += 1
    
    def append_rows(self, urls):
        """Scrapes the website of the given urls, then appends a row with the scraped contacts to the sheets.
        
        Pre:
            urls: the urls of the websites to have added information
        Post:
            rows added to Google Sheets
        Return:
            None
        """
        
        for url in urls:
            tmp_website_contacts = WebsiteContacts(url)
            row = [tmp_website_contacts.url, tmp_website_contacts.emails, tmp_website_contacts.facebooks, tmp_website_contacts.instagrams, tmp_website_contacts.twitters, tmp_website_contacts.linkedins]
            self._sheet1.insert_row(row, self._num_urls + 2)
            self._num_urls += 1
        
    def web_of_web_search_scrape(self):
        """Performs contact scraping of websites from websites from the Google Search page of the keyphrase(s)
        from second sheet of the Google Sheets file.
        
        Pre:
            None
        Post:
            rows of website contact information added to Sheet1
        Return:
            None
        """
    
        for i in range(self._sheet2_num_keyphrases):
            if (self._sheet2.cell(i+1, 2).value == 'to scrape'):
                self._sheet2_keyphrases.append(self._sheet2.cell(i+1, 1).value)
        
        website_list = SortedSet()
        for keyphrase in self._sheet2_keyphrases:
            search = GoogleSearch(keyphrase)
            for website in search.website_list:
                website_list.add(website)
        
        print()
        print('Websites to scrape:')
        print('-------------------')
        for website in website_list:
            print(website)
        
        print()
        print('Websites scraped:')
        print('-----------------')
        for website in website_list:
            # prevents duplicates from being scraped
            if website in self._sheet1.col_values(1):
                continue
            print(website)
            self.append_row(website)
        
        for i in range(self._sheet2_num_keyphrases):
            if (self._sheet2.cell(i+1, 2).value == 'to scrape'):
                self._sheet2.cell(i+1, 2).update_cell('scraped')
    
    def web_search_scrape(self):
        """Performs contact scraping of websites from the Google Search page of the keyphrase(s) from third
        sheet of the Google Sheets file.
        
        Pre:
            None
        Post:
            rows of website contact information added to Sheet1
        Return:
            None
        """
        
        for i in range(self._sheet3_num_keyphrases):
            if (self._sheet3.cell(i+1, 2).value == 'to scrape'):
                self._sheet3_keyphrases.append(self._sheet3.cell(i+1, 1).value)
        
        url_list = SortedSet()
        for keyphrase in self._sheet3_keyphrases:
            search = GoogleSearch(keyphrase)
            for url in search.url_list:
                url_list.add(url)
        
        print()
        print('Websites to scrape:')
        print('-------------------')
        for url in url_list:
            print(url)
            
        print()
        print('Websites scraped:')
        print('-----------------')
        for website in url_list:
            # prevents duplicates from being scraped
            if website in self._sheet1.col_values(1):
                continue
            print(website)
            self.append_row(website)
        
        for i in range(self._sheet2_num_keyphrases):
            if (self._sheet2.cell(i+1, 2).value == 'to scrape'):
                self._sheet2.cell(i+1, 2).update_cell('scraped')
        
    def web_scrape(self):
        """Performs contact scraping of specified website(s) from fourth sheet of the Google Sheets file.
        
        Pre:
            None
        Post:
            rows of website contact information added to Sheet1
        Return:
            None
        """
        
        for i in range(self._sheet4_num_websites):
            if (self._sheet4.cell(i+1, 2).value == 'to scrape'):
                self._sheet4_websites.append(self._sheet4.cell(i+1, 1).value)
                self._sheet2.cell(i+1, 2).update_cell('scraped')
                
        print()
        print('Website(s) to scrape:')
        print('---------------------')
        for website in self._sheet4_websites:
            print(website)
                
        print()
        print('Website(s) scraped:')
        print('-------------------')
        for website in self._sheet4_websites:
            self.append_row(website)
            print(website)
        
if __name__ == '__main__':

    print('NOTICE: For the program to work properly, follow the instructions carefully.')
    print('Before proceeding, share the file with the following service account email:')
    print('webcontactscraper-951@inbound-ship-281503.iam.gserviceaccount.com')
    
    confirm = 'N'
    file_name = 'Untitled'
    while confirm == 'N':
        file_name = input('Enter the name of the Google Sheets file: ')
        confirm = input('Confirm the file name? (Y/N): ').upper()
        if confirm == 'Y':
            break
        
    wcs_manager = WebContactSheet(file_name)
    
    choice = '0'
    while choice != '4':
        print()
        print('Web Contact Scraper')
        print('-------------------')
        print('1. Scrape websites found from websites of a Google Search')
        print('2. Scrape websites of a Google Search')
        print('3. Scrape selected website(s)')
        print('4. Quit')
        
        while True:
            choice = input('Enter a number for the operation (1-4): ')
            if choice == '1' or choice == '2' or choice == '3' or choice == '4':
                break
                
        print()
        if choice == '1':
            print('Before proceeding, enter the keywords for the search in the first column the second sheet of the Google Sheet file.')
            print('NOTICE: Only run this operation once every 10 minutes if different search phrases are used. Otherwise, Google may ban your IP.')
            print('NOTICE: If the program is re-run with the same search phrase, your IP is safe.')
            confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            print(confirm)
            while confirm != 'Y' and confirm != 'N':
                confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            if confirm == 'Y':
                wcs_manager.web_of_web_search_scrape()
        if choice == '2':
            print('Before proceeding, enter the keywords for the search in the first column the third sheet of the Google Sheet file.')
            print('NOTICE: Only run this operation once every 10 minutes if different search phrases are used. Otherwise, Google may ban your IP.')
            print('NOTICE: If the program is re-run with the same search phrase, your IP is safe.')
            confirm = input('EWould you like to proceed directly to scraping? (Y/N): ').upper()
            while confirm != 'Y' and confirm != 'N':
                confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            if confirm == 'Y':
                wcs_manager.web_search_scrape()
            elif confirm == 'N':
                choice = '0'
        if choice == '3':
            print('Before proceeding, enter the root URL of the website(s) in the first column of the fourth sheet of the Google Sheet file.')
            confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            while confirm != 'Y' and confirm != 'N':
                confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            if confirm == 'Y':
                wcs_manager.web_scrape()
        if choice == '4':
            confirm = input('Are you sure you want to quit? (Y/N): ').upper()
            while confirm != 'Y' and confirm != 'N':
                confirm = input('Would you like to proceed directly to scraping? (Y/N): ').upper()
            if confirm == 'N':
                choice == '0'