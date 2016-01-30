from bs4 import BeautifulSoup
import http
import json
import requests

def extract_routes():
    index_page = requests.get('http://millercenter.org/president/speeches')
    soup = BeautifulSoup(index_page.content)
    routes = [sub['href'] for sub in soup.findAll(attrs={'class': 'transcript'})]
    return routes

def fetch_speech(route):
    host = 'http://millercenter.org/'
    res = requests.get(host + route)
    if res.status_code != 200:
        raise http.client.HTTPException
    return res


class Speech(object):
    """hold and store data about a presidential speech
    """
    def __init__(self, content):
        """initialize with a page's content"""
        self.soup = BeautifulSoup(content)
        self.name = self._extract_name()
        self.title, self.date = self._parse_speech_title()
        self.transcript = self._extract_transcript()

    def _extract_name(self):
        name = self.soup.find(attrs=({'id': 'innercontent'})).find('h2').next_element
        return name

    def _parse_speech_title(self):
        header = self.soup.find(attrs=({'id': 'amprestitle'})).text
        title, date = extract_date(header)
        return title, date

    def _extract_transcript(self):
        transcript = self.soup.find(attrs=({'id': 'transcript'})).getText()
        return transcript

    def write(self, file_name=None):
        metadata = {}
        metadata['date'] = self.date
        metadata['name'] = self.name
        metadata['title'] = self.title
        metadata['transcript'] = self.transcript
        if not file_name:
            initials = [part[0] for part in self.name.split(' ')]
            file_name = ''.join(initials)
            file_name += self.title.replace(' ', '')
            file_name = file_name.replace('/', '')
            file_name += self.date.replace(' ', '').replace(',', '')
        with open(file_name + '.json', 'w') as f:
            f.write(json.dumps(metadata))


def extract_date(header):
    """extract date from the amprestitle object

    Structure looks like: 'Title Words (Month DD, YYYY)'
    """
    date_opener = header.rfind('(')
    title = header[0:date_opener]
    date = header[date_opener:]
    return title, date

def store_everything():
    routes = extract_routes()
    for i, route in enumerate(routes[819:]):
        page = fetch_speech(route)
        speech = Speech(page.content)
        speech.write()
        print(':: wrote the %s-th speech\n', i)
