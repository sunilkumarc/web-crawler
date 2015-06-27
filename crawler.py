import signal
import sys
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib import parse

# Represents Links Repository
class LinksDatabase():

    def __init__(self):
        self.links = []

    def get_len(self):
        return len(self.links)

    def add_link(self, link):
        self.links.append(link)

    def print_repository(self):
        for i in range(1, self.get_len()+1):
            print(i, self.links[i-1])

        print('No of links fetched :', self.get_len())

# Create a links database instance
links_db = LinksDatabase()

# reprents a page
class Page():

    def __init__(self, url):
        self.links = []
        self.baseURL = url

    def getLinks(self):
        try:
            # get the source text of the page
            page = requests.get(self.baseURL).text

            # parse all the links on the page
            links = BeautifulSoup(page, parse_only=SoupStrainer('a'))

            # hanlding relative and absolute URLs
            for link in links:
                if link.has_attr('href'):
                    l = parse.urljoin(self.baseURL, link['href'])
                    self.links.append(l)
        except requests.exceptions.MissingSchema as error:
            print(error)

        return self.links

def handle(signal, frame):
    print('\nCrawling has been stopped!')

    # print the links fetched
    links_db.print_repository()

    # stop crawling
    sys.exit(0)

def registerSignal():
    # registering a handler for SIGINT event
    signal.signal(signal.SIGINT, handle)

# spider which crawls
def startSpider(startUrl, maxLinksToFetch, links_db):
    pagesToVisit = [startUrl]
    numberFetched = 0

    # crawl until maximum links allowed are fetched and there are still pages to visit
    while (numberFetched < maxLinksToFetch) and (len(pagesToVisit) > 0):
        url = pagesToVisit[0]
        print('Visiting : ' + url)
        pagesToVisit = pagesToVisit[1:]

        # create an instance of a page which is identified by an URL
        page = Page(url)

        # get all the links on the page
        linksOnThePage = page.getLinks()

        # add links one by one to the links repository until maximum limit is reached
        for link in linksOnThePage:
            numberFetched += 1
            if numberFetched > maxLinksToFetch:
                break
            else:
                pagesToVisit.append(link)
                links_db.add_link(link)

# main function
if __name__=='__main__':
    startUrl = input()
    maxLinksToFetch = int(input())

    # register the handler to handle CTRL+C event
    registerSignal()

    # start the spider here
    startSpider(startUrl, maxLinksToFetch, links_db)

    # print all the links that have been fetched
    links_db.print_repository()
