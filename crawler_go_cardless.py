import signal
import sys
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib import parse
import re

# Represents Links Repository
class LinksDatabase():
    def __init__(self):
        self.links = set()

    def get_len(self):
        return len(self.links)

    def add_link(self, link):
        self.links.add(link)

    def is_visited(self, link):
        if link in self.links:
            return True
        return False

# Reprents a page
class Page():
    def __init__(self, url):
        self.links = []
        self.assets = []
        self.baseURL = url
        self.resp = requests.get(self.baseURL)
        self.page = self.resp.text

    def getAssets(self):
        try:
            if self.resp.status_code != 200:
                print('Something went wrong. Check the URL')
            else:
                # parse all the links on the page
                assets = BeautifulSoup(self.page, 'html.parser', parse_only=SoupStrainer(['script', 'link', 'img']))

                for asset in assets:
                    if asset.has_attr('src'):
                        self.assets.append(asset['src'])

                results = assets.findAll('link', {'rel': ['icon', 'stylesheet', 'image/png', 'image/jpg', 'apple-touch-icon-precomposed']});
                for link in results:
                    self.assets.append(link['href'])

        except requests.exceptions.MissingSchema as error:
            print(error)

        return self.assets

    def getBaseUrl(self):
        return self.baseURL

    def getLinks(self):
        try:
            if self.resp.status_code != 200:
                print('Something went wrong. Check the URL')
            else:
                # parse all the links on the page
                links = BeautifulSoup(self.page, "html.parser", parse_only=SoupStrainer('a'))
                for link in links:
                    if link.has_attr('href'):
                        self.links.append(parse.urljoin(self.baseURL, link['href']))

        except requests.exceptions.MissingSchema as error:
            print(error)

        return self.links

# Represents a Crawler
class Crawler():
    def __init__(self, startUrl):
        self.startUrl = startUrl

    def startSpider(self):
        pagesToVisit = [self.startUrl]

        while len(pagesToVisit) > 0:
            url = pagesToVisit.pop()

            if not links_db.is_visited(url):
                links_db.add_link(url)
                print('\nVisiting : ' + url)
                page = Page(url)
                linksOnThePage = page.getLinks()
                assetsOnThePage = page.getAssets()

                for asset in assetsOnThePage:
                    print('      |___  ' + asset)

                for link in linksOnThePage:
                    if re.match(startUrl + '*', link) and (re.match(robots_exclusion, link) == None):
                        pagesToVisit.append(link)

# Handler to handle CTRL+C signal
def handle(signal, frame):
    print('\nCrawling has been stopped!')
    sys.exit(0)

def registerSignal():
    signal.signal(signal.SIGINT, handle)

# Function to read robots.txt and prepare regex to skip Disallowed resources
def readRobotsTxt(url):
    global robots_exclusion
    try:
        resp = requests.get(url)
        robots = resp.text
        robots = robots.split('\n')

        line = 0
        for line in range(0, len(robots)):
            if 'User-agent: *' in robots[line]:
                line += 1
                break

        while line < len(robots):
            if 'User-agent' in robots[line]:
                break
            else:
                if 'Disallow' in robots[line]:
                    d,disallow = robots[line].strip().split(' ')
                    robots_exclusion += '.*' + disallow + '.*|'
            line += 1

        robots_exclusion = robots_exclusion[:-1]
    except Exception as e:
        print(e)
        robots_exclusion = '.*'

# regex to consider robots.txt
robots_exclusion = ''

# Local db to store already visited links
links_db = LinksDatabase()

# main function
if __name__=='__main__':
    startUrl = input('Enter start URL (Default - https://gocardless.com) : ').strip() or 'https://gocardless.com'

    if startUrl[-1] != '/':
        startUrl += '/'

    # register the handler to handle CTRL+C event
    registerSignal()

    # Read robots.txt and build regex to skips resources mentioned in the file.
    readRobotsTxt(startUrl + 'robots.txt')

    # Start the crawler here
    print('Starting crawler. Press CTRL+C to stop crawling.')
    crawler = Crawler(startUrl)
    crawler.startSpider()
