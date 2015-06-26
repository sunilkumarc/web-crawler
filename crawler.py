import signal
import sys
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib import parse

# Links fetched by crawling the internet.
links_repository = []

def print_repository():
    for i in range(1, len(links_repository)+1):
        print(i, links_repository[i-1])

    print('No of links fetched :', len(links_repository))

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

    # print the links repository when the crawling has been stopped
    print_repository()

    # stop crawling
    sys.exit(0)

def registerSignal():
    # registering a handler for SIGINT event
    signal.signal(signal.SIGINT, handle)

# spider which crawls
def startSpider(startUrl, maxLinksToFetch, links_repository):
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
                links_repository.append(link)

# main function
if __name__=='__main__':
    startUrl = input()
    maxLinksToFetch = int(input())

    # register the handler to handle CTRL+C event
    registerSignal()

    # start the spider here
    startSpider(startUrl, maxLinksToFetch, links_repository)

    # print all the links that have been fetched
    print_repository()
