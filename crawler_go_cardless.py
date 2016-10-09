import signal
import sys
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib import parse
import re

robots_exclusion = ''

# represents Links Repository
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

links_db = LinksDatabase()

# reprents a page
class Page():

    def __init__(self, url):
        self.links = []
        self.baseURL = url

    def getAssets(self):
        return ['asset']

    def getBaseUrl(self):
        return self.baseURL

    def getLinks(self):
        try:
            # get the source text of the page
            resp = requests.get(self.baseURL)
            page = resp.text

            if resp.status_code != 200:
                print('Something went wrong. Check the URL')
            else:
                # parse all the links on the page
                links = BeautifulSoup(page, "html.parser", parse_only=SoupStrainer('a'))
                # assets = BeautifulSoup(page, "html.parser", parse_only=SoupStrainer(['img', 'script']))

                # for asset in assets:
                #     if asset.has_attr('src'):
                #         print(asset['src'])
                # hanlding relative and absolute URLs
                for link in links:
                    if link.has_attr('href'):
                        self.links.append(parse.urljoin(self.baseURL, link['href']))

        except requests.exceptions.MissingSchema as error:
            print(error)

        return self.links

def handle(signal, frame):
    print('\nCrawling has been stopped!')
    links_db.print_repository()
    sys.exit(0)

def registerSignal():
    signal.signal(signal.SIGINT, handle)

def startSpider(startUrl):
    pagesToVisit = [startUrl]

    while len(pagesToVisit) > 0:
        url = pagesToVisit.pop()
        # print('Popped : ', url)
        if not links_db.is_visited(url):
            links_db.add_link(url)
            # print('Visiting : ', url)
            page = Page(url)
            linksOnThePage = page.getLinks()
            assetsOnThePage = page.getAssets()
            print(page.getBaseUrl())
            for asset in assetsOnThePage:
                print('      |_' + asset)
            # print(linksOnThePage)
            for link in linksOnThePage:
                # print('Added : ', link)
                if re.match(startUrl + '*', link) and (re.match(robots_exclusion, link) == None):
                    pagesToVisit.append(link)

def readRobotsTxt(url):
    print(url)
    global robots_exclusion
    try:
        resp = requests.get(url)
        robots = resp.text
        robots = robots.split('\n')
        # print(robots)
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

    # print('Exclusion : ' + robots_exclusion)

# main function
if __name__=='__main__':
    startUrl = input('Enter start URL (Default - https://gocardless.com) : ').strip()

    if startUrl == '':
        startUrl = 'https://gocardless.com'

    # if not (startUrl[:10] != 'http://www' and startUrl[:11] != 'https://www'):
    #     startUrl = 'https://www.' + startUrl

    if startUrl[-1] != '/':
        startUrl += '/'

    # register the handler to handle CTRL+C event
    registerSignal()

    # Read robots.txt and build regex to skips pages later
    readRobotsTxt(startUrl + 'robots.txt')

    # start the spider here
    startSpider(startUrl)
    
