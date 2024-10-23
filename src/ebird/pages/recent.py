import datetime as dt

import requests

from bs4 import BeautifulSoup


def get_recent_checklists(region):
    url = _get_url(region)
    content = _get_page(url)
    root = _get_tree(content)
    return _get_checklists(root)

def _get_url(region):
    return "https://ebird.org/region/%s/recent-checklists" % region


def _get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def _get_tree(content):
    return BeautifulSoup(content, "lxml")


def _get_checklists(root):
    checklists = []
    node = root.find('ul', {'class': 'RecentChecklists-list'})
    nodes = node.find_all('li', {'class': 'Chk'})
    for node in nodes:
        checklists.append({
            "identifier": _get_identifier(node),
            "species": _get_species(node),
            "date": _get_date(node),
            "location": _get_location(node),
            "subnational1": _get_subnational1(node),
            "subnational2": _get_subnational2(node),
            "observer": _get_observer(node),
        }

        )
    return checklists


def _get_identifier(node):
    node = node.find('div', {'class': 'Chk-species'})
    url = node.find('a')["href"]
    return url.split('/')[-1]


def _get_species(node):
    node = node.find('div', {'class': 'Chk-species'})
    node = node.find('span')
    return int(node.text.strip())


def _get_date(node):
    node = node.find('div', {'class': 'Chk-date'})
    value = node.find('time')['datetime']
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M")


def _get_location(node):
    node = node.find('div', {'class': 'Chk-location'})
    node = node.find(class_="u-loc-name")
    return node.text.strip()


def _get_subnational1(node):
    node = node.find('div', {'class': 'Chk-location'})
    node = node.find('span', {"class": "u-loc-ancestors"})
    node = node.find_all('span')[1]
    return node.text.strip()


def _get_subnational2(node):
    node = node.find('div', {'class': 'Chk-location'})
    node = node.find('span', {"class": "u-loc-ancestors"})
    node = node.find_all('span')[0]
    return node.text.strip()


def _get_observer(node):
    node = node.find('div', {'class': 'Chk-observer'})
    node = node.find_all('span')[1]
    return node.text.strip()
